from apisports import Football


def test_basic():
    assert(type(Football.players).__name__ == 'function')
