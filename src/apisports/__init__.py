from ._client import ClientMeta, Client


def _client_class(kind, version=None):
    """
    :return: :class:`type`
    :rtype: type
    """

    return type(kind, (Client,), ClientMeta.get(kind.lower(), version=version))


Football = _client_class('Football', 3)
Rugby = _client_class('Rugby')
Baseball = _client_class('Baseball')
Formula1 = _client_class('Formula1')
Basketball = _client_class('Basketball')
Hockey = _client_class('Hockey')
