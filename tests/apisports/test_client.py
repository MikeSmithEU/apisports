from contextlib import contextmanager
import os
from apisports._client import ClientMeta, ClientInitError
from apisports import _client_class
from apisports.data import SingleData, SimpleData, PagedData
import pytest
import requests_mock
import requests


@contextmanager
def clientmeta_test_path():
    """
    Get ClientMeta which loads from tests YAML location
    """

    prev_dir = ClientMeta.data_dir

    try:
        ClientMeta.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        yield ClientMeta
    finally:
        ClientMeta.data_dir = prev_dir


def expect_client_init_error(name, version=None):
    if version is None:
        version = 1

    expected_message = "Could not load API config for {name} from {path}"

    with clientmeta_test_path():
        with pytest.raises(ClientInitError) as excinfo:
            _client_class(name, version)

        assert str(excinfo.value) == expected_message.format(
            name=name.lower(),
            path=os.path.join(ClientMeta.data_dir, f'{name.lower()}-v{version}.yaml')
        )


def clientmeta_test_class(name, version=None):
    with clientmeta_test_path():
        cls = _client_class(name, version)

        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock://', adapter)
    return cls


@pytest.fixture
def test_v3():
    return clientmeta_test_class('test', 3)


@pytest.fixture
def session(adapter):
    session = requests.Session()
    session.mount('mock://', adapter)
    return session


@pytest.fixture
def adapter():
    return requests_mock.Adapter()


def register_mock_uri(session, *args, **kwargs):
    adapter = session.get_adapter('mock://')

    def _(func):
        def wrapped_func(request, context):
            context.status_code = 200
            context.headers['Content-Type'] = 'application/json'
            return func(request, context)

        adapter.register_uri('GET', *args, **kwargs, json=wrapped_func)
        pass
    return _


def assert_response_ok(response):
    assert response.ok
    assert response.errors() == []
    assert response.error_description() == "Success"


def mock_paginated_count(request, context):
    per_page = 3

    try:
        start = int(request.params["from"])
        stop = int(request.params["to"])
        page = int(requests.params['page']) if 'page' in request.params else 1
    except ValueError as exc:
        return {
            "errors": [
                {
                    "message": str(exc)
                }
            ]
        }

    start = start + (page - 1) * per_page
    if start > stop:
        return {
            "errors": [
                {
                    "page": "value too high"
                }
            ]
        }

    result = list(range(start, min(stop + 1, start + per_page + 1)))

    return {
        "paging": {
            "current": page,
            "total": stop - start,
        },
        "results": len(result),
        "response": result
    }


def test_client_init_error():
    expect_client_init_error('FileDoesNotExist')
    expect_client_init_error('InvalidYAML')


def test_clientmeta(test_v3, session):
    assert test_v3.default_host == 'mock://api-test1.server.local'

    assert callable(test_v3.status)
    assert callable(test_v3.ping)
    assert callable(test_v3.null)
    assert callable(test_v3.paginated_count)


def test_status(test_v3, session):
    @register_mock_uri(session, 'mock://api-test1.server.local/status')
    def mock_status(request, context):
        return {"response": {"status": "ok"}}

    test = test_v3(session=session)
    response = test.status()

    assert_response_ok(response)
    expected = dict(status="ok")
    data = response.data()
    assert type(data) is SingleData
    assert len(response) == 1
    assert data.item() == expected
    assert next(iter(response)) == expected
    assert next(iter(data)) == expected


def test_paginated_count(test_v3, session):
    register_mock_uri(session, 'mock://api-test1.server.local/paginated_count')(mock_paginated_count)
    # todo
    assert True
