import code


def debugger(**kwargs):
    code.interact(
        banner='Ctrl+D to continue. Available vars: %s' % (', '.join(kwargs.keys())),
        local=kwargs
    )


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        self.reason = f"HTTP {status_code}"


class MockClient:
    def __init__(self, response):
        self._response = response

    def get(self, *args, **kwargs):
        return self._response
