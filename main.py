# -*- coding: utf-8 -*-
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
from calculate_anything.prefs_sync import PreferencesSync
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


# Keeps the running services in sync with the saved preferences file so a Save
# takes effect without a restart. The baseline is captured at startup in
# PreferencesEventListener.
_sync = PreferencesSync(_PREFS_FILE)


def _refresh_preferences(extension):
    prefs = _sync.apply_changes(lambda key: extension.preferences.get(key))
    extension.preferences.update(prefs)


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
        # Record what startup applied, so a change saved before the first
        # query is still detected and applied by _refresh_preferences.
        _sync.capture_baseline()


class PreferencesUpdateEventListener(EventListener):
    @safe_operation('Update preferences')
    def on_event(self, event, extension):
        super().on_event(event, extension)

        preferences = Preferences()
        PreferencesSync._apply_one(
            preferences,
            lambda key: extension.preferences.get(key),
            event.id,
            event.new_value,
            event.old_value,
        )
        preferences.commit()


class SystemExitEventListener(EventListener):
    def on_event(self, event, extension):
        TimezoneService().stop()
        CurrencyService().stop()
        return super().on_event(event, extension)


if __name__ == '__main__':
    CalculateAnythingExtension().run()
