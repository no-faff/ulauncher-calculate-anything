import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
from typing import Dict


__all__ = ['CurrencyRate', 'CurrencyData']


class CurrencyRate(TypedDict):
    rate: float
    # The per-rate field is timestamp_refresh; last_update_timestamp is the
    # separate top-level cache key, not part of an individual rate.
    timestamp_refresh: float


CurrencyData = Dict[str, CurrencyRate]
