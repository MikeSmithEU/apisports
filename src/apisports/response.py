import json
from json import JSONDecodeError
from .data import NoneData, AbstractData


class AbstractResponse:
    """
    Generic response object.

    :param client: :class:`Client <apisports._client.Client>` object
    :type client: apisports._client.Client

    :param response: :class:`Response <requests.Response>` object
    :type response: requests.Response

    :param data: The data object returned by the API call
    :type data: Union[None, dict]
    """

    def __init__(self, client, response, data=None):
        self._client = client
        self._response = response
        self._data_object = None
        self._data = dict() if data is None else data

    @staticmethod
    def create(client, response):
        """
        AbstractResponse factory method.

        :param response: :class:`Response <requests.Response>` object
        :type response: requests.Response

        :return: :class:`AbstractResponse <apisports.response.AbstractResponse>` object
        :rtype: AbstractResponse
        """

        try:
            data = json.loads(response.text)
        except (JSONDecodeError, KeyError) as exc:
            data = dict(errors=str(exc))

        response_class = SuccessResponse

        if response.status_code == 200:
            if (data is None) or ('errors' in data and data['errors']):
                response_class = ErrorResponse
        else:
            response_class = HttpErrorResponse

        return response_class(client, response, data)

    @property
    def data(self):
        """
        Get the :class:`AbstractData <apisports.data.AbstractData>` object.

        :return: :class:`AbstractData <apisports.data.AbstractData>` object
        :rtype: AbstractData
        """

        return NoneData

    @property
    def ok(self):
        """
        Whether the request has completed without errors.

        :type: bool
        """
        return False

    @property
    def errors(self):
        """
        Get the errors.

        :return: Dict of errors
        :rtype: dict
        """

        if 'errors' not in self._data:
            return {}

        errors = self._data['errors']

        if not errors:
            return {}

        if type(errors) is dict:
            return errors

        if type(errors) is list:
            return dict(errors=errors)

        return dict(error=errors)

    @property
    def error_description(self):
        """
        Get a string representation of the errors, or "Success" on success...

        :return: Error string
        :rtype: str
        """

        return "Success" if self.ok else '\n'.join([f"{k}: {v}" for k, v in self.errors.items()])

    @property
    def headers(self):
        """
        Get response headers

        :return: :class:`Headers` object
        :rtype: Headers
        """
        return Headers(self._response.headers)

    @property
    def raw(self):
        """
        Get raw Response object.

        :return: :class:`Response <requests.Response>` object.
        :rtype: `requests.Response`
        """
        return self._response

    @property
    def text(self):
        """
        Get raw response text.

        :return: response body as string
        :rtype: str
        """
        return self._response.text

    def __iter__(self):
        """
        Delegates iteration to the :class:`AbstractData <apisports.data.AbstractData>` class.
        """

        return iter(self.data)

    def __len__(self):
        """
        Delegates ``len()`` to the :class:`AbstractData <apisports.data.AbstractData>` class.
        """

        return len(self.data)


class ErrorResponse(AbstractResponse):
    pass


class HttpErrorResponse(ErrorResponse):
    @property
    def errors(self):
        return dict(
            http_status_code=self._response.status_code,
            http_status_text=self._response.reason,
            details=super().errors
        )

    @property
    def error_description(self):
        return "HTTP {http_status_code}: {http_status_text}\n{content_details}".format(
            **self.errors,
            content_details=super().error_description
        )


class SuccessResponse(AbstractResponse):
    @property
    def ok(self):
        return True

    @property
    def data(self):
        if self._data_object is None:
            self._data_object = AbstractData.create(self._client, self._data)
        return self._data_object


class Headers:
    """
    Response Headers details class.

    :param headers: :class:`CaseInsensitiveDict <requests.structures.CaseInsensitiveDict>` object
    :type headers: requests.structures.CaseInsensitiveDict
    """
    def __init__(self, headers):
        self._headers = headers

    def __getitem__(self, item):
        try:
            return self._headers[item]
        except KeyError:
            return None

    @property
    def server(self):
        """
        Get the current version of the API proxy used by APISports/RapidAPI.

        :rtype: str
        """
        return self['server']

    @property
    def requests_limit(self):
        """
        The number of requests allocated per day according to your subscription

        :rtype: str
        """
        return self['x-ratelimit-requests-limit']

    @property
    def requests_remaining(self):
        """
        The number of remaining requests per day according to your subscription.

        :rtype: str
        """
        return self['x-ratelimit-requests-remaining']

    @property
    def rate_limit(self):
        """
        Maximum number of API calls per minute.

        :rtype: str
        """
        return self['X-RateLimit-Limit']

    @property
    def rate_limit_remaining(self):
        """
        Number of API calls remaining before reaching the limit per minute.

        :rtype: str
        """
        return self['X-RateLimit-Remaining']

    @property
    def raw(self):
        """
        Get raw headers.

        :return: :class:`CaseInsensitiveDict <requests.structures.CaseInsensitiveDict>` object
        :rtype: CaseInsensitiveDict
        """
        return self._headers
