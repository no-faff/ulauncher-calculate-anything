# -*- coding: utf-8 -*-
import json
from pathlib import Path

from calculate_anything.utils.misc import images_dir
from calculate_anything import logging
from ulauncher.api.shared.action.CopyToClipboardAction import (
    CopyToClipboardAction,
)
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import (
    RenderResultListAction,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    PreferencesEvent,
    PreferencesUpdateEvent,
    SystemExitEvent,
)
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from calculate_anything.utils import safe_operation
from calculate_anything.preferences import Preferences
from calculate_anything.query.handlers import (
    PercentagesQueryHandler,
    UnitsQueryHandler,
    CalculatorQueryHandler,
    TimeQueryHandler,
    Base10QueryHandler,
    Base16QueryHandler,
    Base2QueryHandler,
    Base8QueryHandler,
)
from calculate_anything.query.handlers import MultiHandler
from calculate_anything.time import TimezoneService
from calculate_anything.lang import LanguageService
from calculate_anything.currency import CurrencyService


# See what I did for Ulauncher.
# You won't let use my own formatter, due to duplicate logs
logging.disable_stdout_handler()


class CalculateAnythingExtension(Extension):
    def __init__(self):
        super(CalculateAnythingExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(SystemExitEvent, SystemExitEventListener())


# Workaround for Ulauncher 6 beta: PreferencesUpdateEvent doesn't fire in
# API v2 compat mode. Reading from disk ensures saved preferences are used.
# The extension id (and so the prefs filename) is the install directory
# name, so this works regardless of the installed extension id.
# Can likely be removed once Ulauncher 6 is finalised.
_EXT_ID = Path(__file__).parent.name
_PREFS_FILE = (
    Path.home()
    / ".config"
    / "ulauncher"
    / "ext_preferences"
    / "{}.json".format(_EXT_ID)
)


# Snapshot of the preference values last applied to the services, used to
# apply saved changes on the next query without needing a restart.
_applied_preferences = {}


def _apply_preference(preferences, extension, key, new_value, old_value):
    """Apply a single changed preference to its service."""
    if key == 'cache':
        preferences.currency.set_cache_update_frequency(new_value)
    elif key == 'default_currencies':
        preferences.currency.set_default_currencies(new_value)
    elif key == 'api_key':
        currency_provider = extension.preferences['currency_provider']
        preferences.currency.add_provider(currency_provider, new_value)
    elif key == 'currency_provider':
        if old_value:
            preferences.currency.remove_provider(old_value)
        api_key = extension.preferences['api_key']
        preferences.currency.add_provider(new_value, api_key)
    elif key == 'currency_provider_protocol':
        preferences.currency.set_currency_provider_protocol(new_value)
    elif key == 'default_cities':
        preferences.time.set_default_cities(new_value)
    elif key == 'units_conversion_mode':
        preferences.units.set_conversion_mode(new_value)
    elif key == 'unit_system':
        preferences.units.set_unit_system(new_value)
    elif key == 'trig_mode':
        preferences.calculator.set_trig_mode(new_value)


def _refresh_preferences(extension):
    """Read saved preferences from disk and apply any that changed.

    Ulauncher 6 in API v2 compat mode does not reliably fire
    PreferencesUpdateEvent, so a Save would otherwise need a restart to take
    effect. Reading on each query and applying the diff keeps the running
    services in sync with what the user saved.
    """
    global _applied_preferences
    try:
        data = json.loads(_PREFS_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return
    prefs = data.get("preferences", {})
    extension.preferences.update(prefs)

    if not _applied_preferences:
        # First read after startup: PreferencesEvent already applied these,
        # so just record the baseline.
        _applied_preferences = dict(prefs)
        return

    changed = [
        (key, value, _applied_preferences.get(key))
        for key, value in prefs.items()
        if _applied_preferences.get(key) != value
    ]
    if not changed:
        return

    preferences = Preferences()
    for key, new_value, old_value in changed:
        with safe_operation('Apply preference {}'.format(key)):
            _apply_preference(preferences, extension, key, new_value, old_value)
    preferences.commit()
    _applied_preferences = dict(prefs)


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        _refresh_preferences(extension)
        query_nokw = event.get_argument() or ''
        query = query_nokw
        mode = 'calculator'
        if event.get_keyword() == extension.preferences['time_kw']:
            query = TimeQueryHandler().keyword + query
            handlers = [TimeQueryHandler]
            mode = 'time'
        elif event.get_keyword() == extension.preferences['dec_kw']:
            query = Base10QueryHandler().keyword + query
            handlers = [Base10QueryHandler]
            mode = 'dec'
        elif event.get_keyword() == extension.preferences['hex_kw']:
            query = Base16QueryHandler().keyword + query
            handlers = [Base16QueryHandler]
            mode = 'hex'
        elif event.get_keyword() == extension.preferences['oct_kw']:
            query = Base8QueryHandler().keyword + query
            handlers = [Base8QueryHandler]
            mode = 'oct'
        elif event.get_keyword() == extension.preferences['bin_kw']:
            query = Base2QueryHandler().keyword + query
            handlers = [Base2QueryHandler]
            mode = 'bin'
        else:
            query = CalculatorQueryHandler().keyword + query
            handlers = [
                UnitsQueryHandler,
                CalculatorQueryHandler,
                PercentagesQueryHandler,
            ]

        items = []
        results = MultiHandler().handle(query, *handlers)
        for result in results:
            if result.clipboard is not None:
                on_enter = CopyToClipboardAction(result.clipboard)
            else:
                on_enter = HideWindowAction()

            items.append(
                ExtensionResultItem(
                    icon=result.icon or images_dir('icon.svg'),
                    name=result.name,
                    description=result.description,
                    highlightable=False,
                    on_enter=on_enter,
                )
            )

        should_show_placeholder = (
            query_nokw.strip() == '' and len(items) == 0
        ) or (
            len(items) == 0
            and extension.preferences['show_empty_placeholder'] == 'y'
        )

        if should_show_placeholder:
            items.append(
                ExtensionResultItem(
                    icon=images_dir('icon.svg'),
                    name=LanguageService().translate('no-result', 'misc'),
                    description=LanguageService().translate(
                        'no-result-{}-description'.format(mode), 'misc'
                    ),
                    highlightable=False,
                    on_enter=HideWindowAction(),
                )
            )

        return RenderResultListAction(items)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        super().on_event(event, extension)

        preferences = Preferences()

        with safe_operation('Set language'):
            preferences.language.set('en_US')

        with safe_operation('Set default cities'):
            default_cities = event.preferences['default_cities']
            preferences.time.set_default_cities(default_cities)

        with safe_operation('Set units conversion mode'):
            mode = event.preferences['units_conversion_mode']
            preferences.units.set_conversion_mode(mode)

        with safe_operation('Set unit system'):
            unit_system = event.preferences.get('unit_system', 'us')
            preferences.units.set_unit_system(unit_system)

        with safe_operation('Set currency provider protocol'):
            protocol = event.preferences['currency_provider_protocol']
            preferences.currency.set_currency_provider_protocol(protocol)

        with safe_operation('Set currency providers'):
            provider = event.preferences['currency_provider']
            api_key = event.preferences['api_key']
            preferences.currency.add_provider(provider, api_key)

        with safe_operation('Set cache interval'):
            frequency = event.preferences['cache']
            preferences.currency.set_cache_update_frequency(frequency)

        with safe_operation('Set default currencies'):
            default_currencies = event.preferences['default_currencies']
            preferences.currency.set_default_currencies(default_currencies)

        with safe_operation('Set trigonometry mode'):
            trig_mode = event.preferences['trig_mode']
            preferences.calculator.set_trig_mode(trig_mode)

        preferences.commit()


class PreferencesUpdateEventListener(EventListener):
    @safe_operation('Update preferences')
    def on_event(self, event, extension):
        super().on_event(event, extension)

        preferences = Preferences()
        _apply_preference(
            preferences, extension, event.id, event.new_value, event.old_value
        )
        preferences.commit()


class SystemExitEventListener(EventListener):
    def on_event(self, event, extension):
        TimezoneService().stop()
        CurrencyService().stop()
        return super().on_event(event, extension)


if __name__ == '__main__':
    CalculateAnythingExtension().run()
