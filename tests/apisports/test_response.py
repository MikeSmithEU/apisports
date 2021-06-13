from apisports.response import AbstractResponse, ErrorResponse, HttpErrorResponse
from apisports.data import NoneData
from helpers import MockResponse
import pytest


def assert_is_error(response):
    assert not response.ok
    assert response.errors
    assert response.data is NoneData


def test_invalidjson():
    response = AbstractResponse.create(None, MockResponse("-"))

    assert_is_error(response)
    assert type(response) is ErrorResponse


def test_httperror():
    response = AbstractResponse.create(None, MockResponse('[]', 404))

    assert_is_error(response)
    assert type(response) is HttpErrorResponse


def test_reportederror():
    response = AbstractResponse.create(None, MockResponse('{"errors": {"random": "error"}}', 200))

    assert_is_error(response)
    assert type(response) is ErrorResponse
    assert response.errors == {"random": "error"}
