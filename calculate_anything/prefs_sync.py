'''Keeps the running services in sync with the saved preferences file.

Ulauncher 6 in API v2 compat mode does not reliably fire
PreferencesUpdateEvent, so a Save would otherwise need a restart to take
effect. This reads the preferences file and re-applies any value that differs
from the last applied one.

The baseline of already-applied values is captured at startup (once the
PreferencesEvent has configured the services), so a change saved before the
first query is still picked up. Capturing it lazily on the first query instead
would record the already-changed value and silently skip applying it.

This lives in ``calculate_anything`` rather than ``main.py`` so it carries no
Ulauncher dependency and can be tested directly.
'''

import json
from pathlib import Path
from typing import Callable, Dict
from calculate_anything.preferences import Preferences
from calculate_anything.utils import safe_operation


__all__ = ['PreferencesSync']


class PreferencesSync:
    def __init__(self, prefs_file) -> None:
        self._prefs_file = Path(prefs_file)
        self._applied: Dict[str, object] = {}

    def read(self) -> Dict[str, object]:
        try:
            data = json.loads(self._prefs_file.read_text())
        except (OSError, json.JSONDecodeError):
            return {}
        return data.get('preferences', {})

    def capture_baseline(self) -> None:
        '''Record the currently saved values as already applied. Call once the
        startup PreferencesEvent has configured the services.'''
        self._applied = dict(self.read())

    def apply_changes(
        self, get_pref: Callable[[str], object]
    ) -> Dict[str, object]:
        '''Apply any saved value that differs from the last applied one and
        return the saved preferences so the caller can refresh its own copy.

        ``get_pref`` returns the current value of another preference, needed
        when applying an api key or currency provider.'''
        prefs = self.read()
        if not prefs:
            return prefs

        changed = [
            (key, value, self._applied.get(key))
            for key, value in prefs.items()
            if self._applied.get(key) != value
        ]
        if not changed:
            return prefs

        preferences = Preferences()
        for key, new_value, old_value in changed:
            with safe_operation('Apply preference {}'.format(key)):
                self._apply_one(
                    preferences, get_pref, key, new_value, old_value
                )
        preferences.commit()
        self._applied = dict(prefs)
        return prefs

    @staticmethod
    def _apply_one(preferences, get_pref, key, new_value, old_value) -> None:
        '''Apply a single changed preference to its service.'''
        if key == 'cache':
            preferences.currency.set_cache_update_frequency(new_value)
        elif key == 'default_currencies':
            preferences.currency.set_default_currencies(new_value)
        elif key == 'api_key':
            preferences.currency.add_provider(
                get_pref('currency_provider'), new_value
            )
        elif key == 'currency_provider':
            if old_value:
                preferences.currency.remove_provider(old_value)
            preferences.currency.add_provider(new_value, get_pref('api_key'))
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
