from contextlib import contextmanager
import os
from apisports._client import ClientMeta, ClientInitError
from apisports import _client_class
from apisports.data import SingleData, NoneData, SimpleData, PagedData
import pytest
import requests_mock
import requests
from math import ceil


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

        # adapter = requests_mock.Adapter()
    return cls


@pytest.fixture
def test_v3():
    return clientmeta_test_class('test', 3)


@pytest.fixture
def mock(session):
    with requests_mock.mock() as mock:
        return mock


@pytest.fixture
def session(adapter):
    session = requests.Session()
    session.mount('http+mock://', adapter)
    return session


@pytest.fixture
def adapter():
    return requests_mock.Adapter()


def register_mock_uri(session, *args, **kwargs):
    # adapter = session.get_adapter('mock://')

    def _(func):
        def wrapped_func(request, context):
            context.status_code = 200
            context.headers['Content-Type'] = 'application/json'
            return func(request, context)

        session.register_uri(
            'GET',
            *args,
            **kwargs,
            json=wrapped_func
        )

    return _


def assert_response_ok(response):
    assert response.ok
    assert response.errors() == []
    assert response.error_description() == "Success"


def test_client_init_error():
    expect_client_init_error('FileDoesNotExist')
    expect_client_init_error('InvalidYAML')


def test_clientmeta(test_v3, session):
    assert test_v3.default_host == 'http+mock://api-test1.server.local'

    assert callable(test_v3.status)
    assert callable(test_v3.ping)
    assert callable(test_v3.null)
    assert callable(test_v3.paginated_count)
    assert callable(test_v3.import_)


def test_session(test_v3, session):
    t = test_v3(session=session)
    t2 = test_v3()

    # assert type(t._session) is requests.Session
    assert t._session is session

    assert type(t2._session) is requests.Session
    assert t2._session is not session


def test_status(test_v3, session, mock, adapter):
    @register_mock_uri(adapter, 'http+mock://api-test1.server.local/status')
    def mock_status(request, context):
        return {"response": {"status": "ok"}}

    test = test_v3(session=session)
    response = test.status()

    assert_response_ok(response)
    expected = dict(status="ok")
    data = response.data()
    assert type(data) is SingleData
    assert len(response) == 1
    assert list(iter(data)) == [expected]
    assert next(iter(response)) == expected
    assert next(iter(data)) == expected
    assert data.item() == expected


def test_null(test_v3, session, mock, adapter):
    @register_mock_uri(adapter, 'http+mock://api-test1.server.local/null')
    def mock_null(request, context):
        return {"response": None}

    test = test_v3(session=session)
    response = test.null()

    assert_response_ok(response)
    assert response.data() is NoneData


def test_python_keyword_import(test_v3, session, mock, adapter):
    @register_mock_uri(adapter, 'http+mock://api-test1.server.local/import')
    def mock_null(request, context):
        return {"response": None}

    test = test_v3(session=session)
    response = test.import_()

    assert_response_ok(response)
    assert response.data() is NoneData


def test_paginated_count(test_v3, session, mock, adapter):
    @register_mock_uri(adapter, 'http+mock://api-test1.server.local/paginated-count')
    def mock_paginated_count(request, context):
        per_page = 3
        params = {k: v[0] for k, v in request.qs.items()}

        try:
            start = int(params["from"]) if 'from' in params else 1
            stop = int(params["to"]) + 1 if 'to' in params else 14
            page = int(params['page']) if 'page' in params else 1
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

        result = list(range(start, min(stop, start + per_page)))

        return {
            "get": "paginated-count",
            "parameters": params,
            "paging": {
                "current": page,
                "total": ceil((stop - start) / per_page),
            },
            "results": len(result),
            "response": result
        }

    test = test_v3(session=session)
    test.paginated_count()

    response = test.paginated_count(**{"from": 1, "to": 10})
    expected = list(range(1, 11))

    assert type(response.data()) is PagedData
    assert list(iter(response.data())) == expected
    assert list(iter(response)) == expected

    # test support for keyword safe parameter alias
    response = test.paginated_count(from_=1, to=10)
    expected = list(range(1, 11))

    assert type(response.data()) is PagedData
    assert list(iter(response.data())) == expected
    assert list(iter(response)) == expected

    response = test.paginated_count(from_=1, to=2)
    expected = [1, 2]

    assert type(response.data()) is SimpleData
    assert list(iter(response.data())) == expected
    assert list(iter(response)) == expected

    response = test.paginated_count(from_=1, to=1)
    expected = [1]

    assert type(response.data()) is SingleData
    assert list(iter(response.data())) == expected
    assert list(iter(response)) == expected
    assert response.data().item() == 1
