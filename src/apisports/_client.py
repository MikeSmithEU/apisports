import requests
import requests.structures
import os
import yaml
from m2r import convert
from .response import AbstractResponse
from keyword import kwlist


class ClientInitError(ImportError):
    pass


class Client:
    """

    :param host: Host to call the api on, should contain "{endpoint}" which will be replaced by the proper url for
    each different endpoint

    :type host: Union[str, None] Will use ``default_host`` if `None`

    :param api_key: The API key to use for requests.
    :type api_key: str

    :param session: The `requests` session to use, if None given, a new session will be used.
    :type session: :class:`Session <requests.Session>` object
    """

    default_host = ''
    """
    Default host to call the api on.

    :type: str
    """

    def __init__(self, host=None, api_key=None, session=None):
        if host is None:
            host = self.default_host
        if session is None:
            session = requests.session()

        self._url = host.rstrip('/') + '/{endpoint}'
        self._session = session
        self._headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': host,
        }

    def status(self):
        """
        This call allows you to:

        * To follow your consumption in real time
        * Manage your subscription and change it if necessary
        * Check the status of our servers
        * Test all endpoints without writing a line of code.

        .. note::
            This call does not count against the daily quota.

        :return: :class:`AbstractResponse <apisports.response.AbstractResponse>` object
        :rtype: apisports.response.AbstractResponse
        """

        return self.get('status')

    def get(self, endpoint, params=None):
        """
        :return: :class:`AbstractResponse <apisports.response.AbstractResponse>` object
        :rtype: apisports.response.AbstractResponse
        """

        return AbstractResponse.create(
            self,
            self._session.get(
                self._url.format(endpoint=endpoint),
                params=params,
                headers=self._headers
            )
        )


class ClientMeta:
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def get(cls, kind, version=None):
        if version is None:
            version = 1
        filename = os.path.join(cls.data_dir, f'{kind}-v{version}.yaml')
        try:
            with open(filename, encoding='UTF-8') as stream:
                config = yaml.safe_load(stream)

            return {
                "default_host": config['servers'][0]['url'],
                **{
                    cls.operation_id_to_method_name(p['get']['operationId']): cls._get_method(
                        class_name=kind,
                        name=cls.operation_id_to_method_name(p['get']['operationId']),
                        description=p['get']['description'] if 'description' in p['get'] else '',
                        endpoint=k.lstrip('/'),
                        params=[
                            param
                            for param in p['get']['parameters']
                            if param['in'] == 'query'
                        ]
                        if 'parameters' in p['get'] else [],
                    ) for k, p in config['paths'].items()
                }
            }
        except (KeyError, OSError, TypeError, yaml.YAMLError) as exc:
            raise ClientInitError(f"Could not load API config for {kind} from {filename}") from exc

    @staticmethod
    def _get_method(class_name, name, description, endpoint, params):
        def _(self, **kwargs):
            return self.get(endpoint, kwargs)

        _.__name__ = name
        _.__module__ = f'apisports.{class_name}'

        _.__doc__ = convert(description) + '\n\n'

        for p in params:
            _.__doc__ += ":param {name}: {description}{pattern}\n".format(**{
                "description": '',
                "pattern": (' (' + p['schema']['pattern'] + ')' if 'pattern' in p['schema'] else ''),
                **p
            })
            if 'type' in p['schema']:
                _.__doc__ += ":type {name}: {type}\n".format(
                    name=p['name'] + '_' if p['name'] in kwlist else p['name'],
                    type=p['schema']['type'],
                )

        _.__doc__ += '\n:return: :class:`AbstractResponse <apisports.response.AbstractResponse>` object'
        _.__doc__ += '\n:rtype: apisports.response.AbstractResponse'
        return _

    @staticmethod
    def operation_id_to_method_name(operation_id):
        name = operation_id[4:].replace('-', '_')

        # avoid using python keywords for parameters
        if name in kwlist:
            name = name + '_'

        return name
