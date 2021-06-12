from apisports.response import AbstractResponse, ErrorResponse, HttpErrorResponse
from apisports.data import NoneData
import pytest


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


def test_invalidjson():
    response = AbstractResponse.create(None, MockResponse("-"))

    assert not response.ok
    assert type(response) is ErrorResponse
    assert response.data() is NoneData


def test_httperror():
    response = AbstractResponse.create(None, MockResponse('[]', 404))

    assert not response.ok
    assert type(response) is HttpErrorResponse
    assert response.data() is NoneData
