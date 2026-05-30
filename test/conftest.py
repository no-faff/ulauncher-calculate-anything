import pytest
from calculate_anything.time import TimezoneService
from test.fixtures import (
    log_filepath,
    httpserver_listen_address,
    httpserver_ssl_context,
    mock_currency_provider,
    in_memory_cache,
    mock_currency_service,
    ecb_data,
    coinbase_data,
    fixerio_data,
    mycurrencynet_data,
)


__all__ = [
    'log_filepath',
    'httpserver_listen_address',
    'httpserver_ssl_context',
    'mock_currency_provider',
    'in_memory_cache',
    'mock_currency_service',
    'ecb_data',
    'coinbase_data',
    'fixerio_data',
    'mycurrencynet_data',
]


@pytest.fixture(autouse=True, scope='session')
def _close_services():
    # Close long-lived resources (the timezone sqlite connection) at the
    # end of the session so they are not finalised by the garbage
    # collector. Python 3.13+ turns that ResourceWarning into an error.
    yield
    TimezoneService().stop()
