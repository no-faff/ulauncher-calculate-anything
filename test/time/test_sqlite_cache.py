import pytest
from calculate_anything.time.sqlite_cache import TimezoneSqliteCache


test_spec = [
    {
        'input': (('Athen',), {}),
        'expected': [
            {
                'name': 'Athens',
                'cc': 'GR',
                'country': 'Greece',
                'timezone': 'Europe/Athens',
                'state': 'ESYE31',
            },
            {
                'name': 'Athens',
                'cc': 'US',
                'country': 'United States',
                'timezone': 'America/New_York',
                'state': 'GA',
            },
            {
                'name': 'Athens',
                'cc': 'US',
                'country': 'United States',
                'timezone': 'America/New_York',
                'state': 'OH',
            },
            {
                'name': 'Athens',
                'cc': 'US',
                'country': 'United States',
                'timezone': 'America/Chicago',
                'state': 'AL',
            },
        ],
    },
    {
        'input': (('Tehran',), {}),
        'expected': [
            {
                'name': 'Tehran',
                'cc': 'IR',
                'country': 'Iran',
                'timezone': 'Asia/Tehran',
                'state': '26',
            },
        ],
    },
    {
        'input': (('Ath',), {'exact': True}),
        'expected': [
            {
                'name': 'Ath',
                'cc': 'BE',
                'country': 'Belgium',
                'timezone': 'Europe/Brussels',
                'state': 'WAL',
            },
        ],
    },
    {'input': (('Somecitythatdoesnotexist',), {}), 'expected': []},
    {
        'input': (('Ath', 'GR'), {}),
        'expected': [
            {
                'name': 'Athens',
                'cc': 'GR',
                'country': 'Greece',
                'timezone': 'Europe/Athens',
                'state': 'ESYE31',
            },
        ],
    },
    {'input': (('Madrid', 'SomeCountry'), {}), 'expected': []},
    {
        'input': (('Pragu', 'Czechia'), {}),
        'expected': [
            {
                'name': 'Prague',
                'cc': 'CZ',
                'country': 'Czechia',
                'state': '52',
                'timezone': 'Europe/Prague',
            },
        ],
    },
    {'input': (('Pragu', 'Czechia'), {'exact': True}), 'expected': []},
    {
        # State-code disambiguation. The sqlite state join was broken, so this
        # returned nothing instead of the Athens in Alabama.
        'input': (('Athens', 'AL'), {}),
        'expected': [
            {
                'name': 'Athens',
                'cc': 'US',
                'country': 'United States',
                'timezone': 'America/Chicago',
                'state': 'AL',
            },
        ],
    },
]


@pytest.mark.parametrize('test_spec', test_spec)
def test(test_spec):
    cache = TimezoneSqliteCache()
    cache.load()

    args, kwargs = test_spec['input']
    cities = cache.get(*args, **kwargs)
    cities = [{k: v for k, v in city.items() if k != 'id'} for city in cities]
    expected = test_spec['expected']

    assert cities == expected

    cache.close_db()


def test_sqlite_loader_rejects_corrupt_file(tmp_path):
    # connect() is lazy, so a corrupt file used to load "successfully" and crash
    # on the first query. The loader must reject it up front so the caller can
    # fall back to the default database.
    from calculate_anything.utils.loaders import SqliteLoader

    corrupt = tmp_path / 'corrupt.sqlite3'
    corrupt.write_text('this is not a database')

    loader = SqliteLoader(str(corrupt))
    assert loader.load() is False
    assert loader.db is None
