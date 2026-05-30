import importlib.util

import pytest


# Babel is a core dependency, so on a normal install the babel-aware
# formatting path is the one that runs. Babel and pint format units and
# currencies differently (plurals, localised names), so the unit tests come
# in two mirrored copies: babel/test_units.py for when babel is present and
# test_units.py for the plain fallback when babel could not be imported.
#
# Select the right copy automatically so the suite passes either way: with
# babel installed, run the babel copy and skip the plain one; without it, do
# the reverse.
_HAS_BABEL = importlib.util.find_spec('babel') is not None

if _HAS_BABEL:
    collect_ignore = ['test_units.py']
else:
    collect_ignore = ['babel']


@pytest.fixture(autouse=True)
def _reset_conversion_mode():
    # test_units_mode_crazy switches the singleton UnitsService into CRAZY
    # mode and resets it at the end, but a failing assertion aborts before
    # that reset and leaks CRAZY into later tests, changing how many results
    # a query returns. Reset after every test so the suite stays order
    # independent.
    yield
    from calculate_anything.units import UnitsService

    UnitsService().set_conversion_mode(UnitsService.ConversionMode.NORMAL)
