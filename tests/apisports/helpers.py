import code

from apisports.data import NoneData


def debugger(**kwargs):
    code.interact(
        banner='Ctrl+D to continue. Available vars: %s' % (', '.join(kwargs.keys())),
        local=kwargs
    )


def assert_response_ok(response):
    assert response.ok
    assert not response.errors
    assert response.errors == {}
    assert response.error_description == "Success"


def assert_response_error(response):
    assert not response.ok
    assert response.errors
    assert response.data is NoneData
    assert response.error_description != "Success"


class MockResponse:
    def __init__(self, text, status_code=200, headers={}):
        self.text = text
        self.status_code = status_code
        self.reason = f"HTTP {status_code}"
        self.headers = headers


class MockClient:
    def __init__(self, response):
        self._response = response

    def get(self, *args, **kwargs):
        return self._response
