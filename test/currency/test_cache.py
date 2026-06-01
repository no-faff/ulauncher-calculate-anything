import json
import glob
from unittest.mock import patch
import calculate_anything.currency.cache as cache_mod
from calculate_anything.currency.cache import CurrencyCache


def test_save_is_atomic(tmp_path):
    # The cache is written to a temp file and swapped in with os.replace, so a
    # reader never sees a half-written file and no temp file is left behind.
    # CurrencyCache is a plain class, so a fresh instance is fully isolated.
    target = str(tmp_path / 'currency_data.json')
    with patch.object(cache_mod, 'CURRENCY_DATA_FILE', target):
        cache = CurrencyCache()
        cache.enable(86400)
        cache.save({'currency_USD': {'rate': 1.1}}, 'someprovider')

    on_disk = json.load(open(target))
    assert on_disk['provider'] == 'someprovider'
    assert on_disk['exchange_rates']['currency_USD']['rate'] == 1.1
    assert glob.glob(str(tmp_path / '*.tmp')) == []
