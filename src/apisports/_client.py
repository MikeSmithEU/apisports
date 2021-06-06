import requests
import requests.structures
import os
import yaml
from m2r import convert
from .response import Response


class ClientInitError(ImportError):
    pass


class Client:
    default_host = ''

    def __init__(self, host=None, api_key=None):
        if host is None:
            host = self.default_host
        self._url = host.rstrip('/') + '/{endpoint}'
        self._host = host
        self._api_key = api_key

    def status(self):
        return self._get('status')

    def _get(self, endpoint, payload=None):
        """
        :return: :class:`Response <apisports.response.Response>` object
        :rtype: Response
        """
        headers = {
            'x-rapidapi-key': self._api_key,
            'x-rapidapi-host': self._host
        }

        return Response(
            requests.request("GET", self._url.format(endpoint=endpoint), headers=headers, data=payload)
        )


class ClientMeta:
    @staticmethod
    def yaml_file(kind, version=None):
        if version is None:
            version = '1'
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            'resources', '{kind}-v{version}.yaml'.format(kind=kind, version=version))

    @classmethod
    def get_endpoints(mcs, kind, version=None):
        with open(mcs.yaml_file(kind, version=version), 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except (KeyError, yaml.YAMLError) as exc:
                raise ClientInitError(exc)

        return {
            "default_host": config['servers'][0]['url'],
            **{
                p['get']['operationId'][4:].replace('-', '_'): mcs._get_method(
                    description=p['get']['description'],
                    endpoint=k.lstrip('/'),
                    params=[param for param in p['get']['parameters'] if param['in'] == 'query'],
                    response=p['get']['responses']['200']['content']['application/json']['schema'],
                ) for k, p in config['paths'].items()
            }
        }

    @staticmethod
    def _get_method(description, endpoint, params, response):
        def _(self, **kwargs):
            return self._get(endpoint, kwargs)

        _.__doc__ = convert(description) + '\n\n\n'

        for p in params:
            try:
                _.__doc__ += ":param {name}: {description}{pattern}\n".format(**{
                    "description": '',
                    "pattern": (' (' + p['schema']['pattern'] + ')' if 'pattern' in p['schema'] else ''),
                    **p
                })
                if 'type' in p['schema']:
                    _.__doc__ += ":type {name}: {type}\n".format(
                        name=p['name'],
                        type=p['schema']['type'],
                    )
            except KeyError as e:
                raise e

        _.__doc__ += '\n\n:return: :class:`Response <apisports._client.Response>` object'
        _.__doc__ += '\n:rtype: Response'
        return _

