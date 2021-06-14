import json
import pytest

from apisports.response import AbstractResponse, ErrorResponse, HttpErrorResponse, Headers
from helpers import MockResponse, assert_response_ok, assert_response_error


def test_invalidjson():
    response = AbstractResponse.create(None, MockResponse("-"))

    assert_response_error(response)
    assert type(response) is ErrorResponse


def test_httperror():
    response = AbstractResponse.create(None, MockResponse('[]', 404))

    assert_response_error(response)
    assert type(response) is HttpErrorResponse


def test_reportederror():
    response = AbstractResponse.create(None, MockResponse('{"errors": {"random": "error"}}', 200))

    assert_response_error(response)
    assert type(response) is ErrorResponse
    assert response.errors == {"random": "error"}


def test_error():
    response = AbstractResponse.create(None, MockResponse('{"errors": ["error"]}', 200))

    assert_response_error(response)

    assert type(response) is ErrorResponse
    assert response.errors == {"errors": ["error"]}


@pytest.mark.parametrize("data", [
    False,
    None,
])
def test_error_simple_types(data):
    response = AbstractResponse.create(
        None,
        MockResponse('{"errors": %s}' % (json.dumps(data),))
    )

    assert_response_ok(response)
    assert response.errors == {}


def test_response_properties():
    text = '{"response": "Test"}'
    mock_response = MockResponse(text)
    response = AbstractResponse.create(None, mock_response)

    assert_response_ok(response)
    assert response.text == text
    assert response.raw is mock_response
    assert type(response.headers) is Headers


@pytest.mark.parametrize("text", [
    "",
    '{"response": "ok"}'
])
def test_response_headers(text):
    headers = {
        "X-RateLimit-Limit": "RateLimit",
        "X-RateLimit-Remaining": "RateRemaining",
        "x-ratelimit-requests-limit": "RequestsLimit",
        "x-ratelimit-requests-remaining": "RequestsRemaining",
        "server": "Server",
    }
    mock_response = MockResponse("", headers=headers)
    response = AbstractResponse.create(text, mock_response)

    assert type(response.headers) is Headers
    assert response.headers.rate_limit == "RateLimit"
    assert response.headers.rate_limit_remaining == "RateRemaining"
    assert response.headers.requests_limit == "RequestsLimit"
    assert response.headers.requests_remaining == "RequestsRemaining"
    assert response.headers.server == "Server"

    assert response.headers.raw is headers

    for key, value in headers.items():
        assert key in response.headers
        assert response.headers[key] == value

    assert "X-Unknown-Header" not in response.headers

    assert response.headers["X-Unknown-Header"] is None
