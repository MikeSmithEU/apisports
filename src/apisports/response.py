class Response:
    """
    Generic response object.

    :param response: :class:`Response <requests.Response>` object
    :type response: requests.Response
    """

    def __init__(self, response):
        self._response = response

    def ok(self):
        """
        :return: If request was ok
        :rtype: bool
        """
        return self._response.status_code == 200

    def headers(self):
        """
        :return: :class:`Headers` object
        :rtype: Headers
        """
        return Headers(self._response.headers)

    def response_raw(self):
        return self._response

    def text(self):
        return self._response.text


class Headers:
    """
    :param headers: :class:`CaseInsensitiveDict <requests.structures.CaseInsensitiveDict>` object
    :type headers: requests.structures.CaseInsensitiveDict
    """
    def __init__(self, headers):

        self._headers = headers

    def _get(self, key):
        try:
            return self._headers[key]
        except KeyError:
            return ''

    def server(self):
        """
        Get the current version of the API proxy used by APISports/RapidAPI.

        :rtype: str
        """
        return self._get('server')

    def requests_limit(self):
        """
        The number of requests allocated per day according to your subscription

        :rtype: str
        """
        return self._get('x-ratelimit-requests-limit')

    def requests_remaining(self):
        """
        The number of remaining requests per day according to your subscription.

        :rtype: str
        """
        return self._get('x-ratelimit-requests-remaining')

    def rate_limit(self):
        """
        Maximum number of API calls per minute.

        :rtype: str
        """
        return self._get('X-RateLimit-Limit')

    def rate_limit_remaining(self):
        """
        Number of API calls remaining before reaching the limit per minute.

        :rtype: str
        """
        return self._get('X-RateLimit-Remaining')

    def all(self):
        """
        Get all headers.

        :return: :class:`CaseInsensitiveDict <requests.structures.CaseInsensitiveDict>` object
        :rtype: CaseInsensitiveDict
        """
        return self._headers
