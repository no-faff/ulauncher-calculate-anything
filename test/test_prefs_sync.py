import json
from pathlib import Path
from calculate_anything.units import UnitsService
from calculate_anything.lang import LanguageService
from calculate_anything.currency import CurrencyService
from calculate_anything.time import TimezoneService
from calculate_anything.preferences import Preferences
from calculate_anything.prefs_sync import PreferencesSync
from test.tutils import reset_instance, temp_filepath, osremove
from test.test_preferences import mock_providers


def _write(path, prefs):
    Path(path).write_text(json.dumps({'preferences': prefs}))


def _pint_litres():
    ureg = UnitsService().unit_registry
    return round(ureg.Quantity(1, 'pint').to('liter').magnitude, 4)


def test_change_saved_before_first_query_is_applied(
    in_memory_cache, mock_currency_provider
):
    # Regression: the baseline is captured at startup, so a change saved
    # before any query (restart -> set Imperial -> query) is still applied.
    fpath = temp_filepath('prefs_sync_change.json')
    try:
        with reset_instance(
            Preferences,
            LanguageService,
            TimezoneService,
            UnitsService,
            CurrencyService,
        ), in_memory_cache(), mock_providers(mock_currency_provider):
            LanguageService().set('en_US')

            # Startup: services configured with the US system, baseline taken.
            _write(fpath, {'unit_system': 'us'})
            Preferences().units.set_unit_system('us')
            Preferences().commit()
            sync = PreferencesSync(fpath)
            sync.capture_baseline()
            assert UnitsService().unit_system == 'us'
            assert _pint_litres() == 0.4732

            # User switches to imperial and saves before running any query.
            _write(fpath, {'unit_system': 'imperial'})

            # The first query triggers a refresh: the change must apply.
            sync.apply_changes(lambda key: None)
            assert UnitsService().unit_system == 'imperial'
            assert _pint_litres() == 0.5683

            CurrencyService().stop()
    finally:
        osremove(fpath)


def test_unchanged_prefs_apply_nothing(in_memory_cache, mock_currency_provider):
    fpath = temp_filepath('prefs_sync_noop.json')
    try:
        with reset_instance(
            Preferences,
            LanguageService,
            TimezoneService,
            UnitsService,
            CurrencyService,
        ), in_memory_cache(), mock_providers(mock_currency_provider):
            LanguageService().set('en_US')
            _write(fpath, {'unit_system': 'imperial'})
            Preferences().units.set_unit_system('imperial')
            Preferences().commit()
            sync = PreferencesSync(fpath)
            sync.capture_baseline()
            assert UnitsService().unit_system == 'imperial'

            # Same values on disk: nothing changes, stays imperial.
            sync.apply_changes(lambda key: None)
            assert UnitsService().unit_system == 'imperial'

            CurrencyService().stop()
    finally:
        osremove(fpath)
