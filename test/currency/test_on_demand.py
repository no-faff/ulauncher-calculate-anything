import time
from queue import Queue

import pytest

from calculate_anything.currency import CurrencyService
from calculate_anything.currency.cache import CurrencyCache


class FakeProvider:
    '''Minimal provider so on-demand fetches stay deterministic and offline.'''

    def __init__(self, rates, had_error=False):
        self._rates = rates
        self.had_error = had_error
        self.calls = 0

    def request_currencies(self, *currencies, force=False):
        self.calls += 1
        return {} if self.had_error else self._rates


def _rates():
    return {'USD': {'rate': 1.1, 'timestamp_refresh': 1000.0}}


def _wait_until(predicate, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return False


@pytest.fixture
def service():
    svc = CurrencyService()
    attrs = (
        '_provider',
        '_cache',
        '_is_running',
        '_on_demand_fetching',
        '_on_demand_last_fetch',
    )
    saved = {attr: getattr(svc, attr) for attr in attrs}
    # A fresh cache with update_frequency 0 is disabled, i.e. "None" mode.
    svc._cache = CurrencyCache()
    svc._is_running = False
    svc._on_demand_fetching = False
    svc._on_demand_last_fetch = 0.0
    yield svc
    for attr, value in saved.items():
        setattr(svc, attr, value)


def test_fetch_on_demand_applies_rates(service):
    service._provider = FakeProvider(_rates())
    queue = Queue()

    def callback(data, had_error):
        queue.put((data, had_error))

    service.add_update_callback(callback)
    try:
        service.fetch_on_demand()
        data, had_error = queue.get(timeout=5)
        assert _wait_until(lambda: not service.is_fetching)
    finally:
        service.remove_update_callback(callback)

    assert data == _rates()
    assert had_error is False
    assert service._provider.calls == 1
    assert service._on_demand_last_fetch > 0


def test_fetch_on_demand_skips_when_cache_enabled(service):
    service._cache.enable(86400)
    service._provider = FakeProvider(_rates())
    service.fetch_on_demand()
    assert service._provider.calls == 0
    assert service.is_fetching is False


def test_fetch_on_demand_skips_while_thread_running(service):
    service._is_running = True
    service._provider = FakeProvider(_rates())
    service.fetch_on_demand()
    assert service._provider.calls == 0


def test_fetch_on_demand_skips_within_ttl(service):
    service._provider = FakeProvider(_rates())
    service._on_demand_last_fetch = time.time()
    service.fetch_on_demand()
    assert service._provider.calls == 0


def test_fetch_on_demand_single_in_flight(service):
    service._provider = FakeProvider(_rates())
    service._on_demand_fetching = True
    service.fetch_on_demand()
    assert service._provider.calls == 0
