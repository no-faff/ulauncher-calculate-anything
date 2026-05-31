import pytest
from calculate_anything.lang import LanguageService
from calculate_anything.units import UnitsService

LanguageService().set('en_US')


def _litres(unit):
    ureg = UnitsService().unit_registry
    return round(ureg.Quantity(1, unit).to('liter').magnitude, 4)


@pytest.fixture
def units_us():
    # Default (US) system, restored after the test so the shared singleton
    # never leaks an imperial registry into other test modules.
    UnitsService().set_unit_system('us')
    UnitsService().start(force=True)
    yield
    UnitsService().set_unit_system('us')
    UnitsService().start(force=True)


def test_explicit_aliases_resolve(units_us):
    assert _litres('us_pint') == 0.4732
    assert _litres('uk_pint') == 0.5683
    assert _litres('imp_pint') == 0.5683
    assert _litres('imperial_pint') == 0.5683
    assert _litres('us_gallon') == 3.7854
    assert _litres('uk_gallon') == 4.5461


def test_aliases_are_case_insensitive(units_us):
    assert _litres('US_PINT') == 0.4732
    assert _litres('Imp_Pint') == 0.5683
    assert _litres('UK_PINT') == 0.5683


def test_us_is_the_default_for_bare_units(units_us):
    assert _litres('pint') == 0.4732
    assert _litres('gallon') == 3.7854


def test_imperial_system_changes_bare_units():
    try:
        UnitsService().set_unit_system('imperial')
        UnitsService().start(force=True)

        # Bare names now resolve to imperial.
        assert _litres('pint') == 0.5683
        assert _litres('gallon') == 4.5461
        ureg = UnitsService().unit_registry
        assert (
            round(ureg.Quantity(26, 'pint').to('liter').magnitude, 2) == 14.77
        )

        # Explicit forms still pin the system regardless.
        assert _litres('us_pint') == 0.4732
        assert _litres('uk_pint') == 0.5683
    finally:
        UnitsService().set_unit_system('us')
        UnitsService().start(force=True)
