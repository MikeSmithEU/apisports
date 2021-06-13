class PagedDataError(Exception):
    """Raised when :class:`PagedData` encounters an error when fetching the next page"""

    def __init__(self, message, error_description=''):
        super().__init__(': '.join((message, error_description)))


class AbstractData:
    @staticmethod
    def create(client, data):
        """
        Factory method that creates the appropriate :class:`AbstractData` object for the given data

        :return: :class:`AbstractData` object
        :rtype: AbstractData
        """

        if data is None:
            return NoneData

        if 'response' not in data or data['response'] is None:
            return NoneData

        response = data['response']

        if 'paging' in data and \
                data['paging']['total'] > 1 and \
                data['paging']['current'] == 1:
            return PagedData(client, data)

        if type(response) is not list:
            return SingleData(response)

        length = len(response)
        if length == 0:
            return NoneData
        if length == 1:
            return SingleData(response[0])
        return SimpleData(response)

    def __iter__(self):
        raise NotImplementedError('__iter__ needs to be implemented in subclass')

    def __len__(self):
        raise NotImplementedError('__len__ needs to be implemented in subclass')


class NoneData(AbstractData):
    """
    Singleton Null AbstractData implementation. To represent no data available.
    """

    def __iter__(self):
        yield from ()

    def __len__(self):
        return 0

    def __call__(self, *args, **kwargs):
        """
        Be gracious to incidental attempts to using the singleton object as class, just return self.
        """
        return self


# singleton
NoneData = NoneData()


class SimpleData(AbstractData):
    """
    Provides a simple iterator for non-paged data.
    """

    def __init__(self, data):
        self._data = data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return '{cls}({data})'.format(
            cls=str(self.__class__.__name__),
            data=repr(self._data)
        )


class SingleData(AbstractData):
    """
    Adds an extra method to easily access data that only contains a single item.
    """

    def __init__(self, data):
        self._data = data

    def __iter__(self):
        return iter([self._data])

    def __len__(self):
        return 1

    def item(self):
        return self._data

    def __repr__(self):
        return '{cls}({data})'.format(
            cls=str(self.__class__.__name__),
            data=repr(self._data)
        )


class PagedData(AbstractData):
    """
    Automagically fetches next page for multi-page data.
    """

    def __init__(self, client, data):
        """
        :param client: :class:`Client <apisports._client.Client>` object
        :type client: apisports._client.Client

        :param data: The response data
        :type data: dict
        """
        self._client = client
        self._current_page = data['paging']['current']
        self._total_pages = data['paging']['total']

        # estimate of the amount of elements (maximum)
        self._length = data['results'] * (self._total_pages - self._current_page + 1)

        self._data = data['response']
        self._get = data['get'] if 'get' in data else None
        self._parameters = data['parameters'] if 'parameters' in data else {}

    def __len__(self):
        """
        This is just an estimate (maximum) until after all data has been fetched
        """

        return self._length

    def _fetch_next_page(self):
        if self._get is None:
            raise PagedDataError("Don't know how to fetch next page", "no request-uri known")

        if self._client is None:
            raise PagedDataError("Don't know how to fetch next page", "no client class known")

        result = self._client.get(
            self._get,
            {
                **self._parameters,
                "page": self._current_page + 1
            })
        if not result.ok:
            raise PagedDataError("Could not fetch next page", result.error_description)
        self._data += list(iter(result.data))
        self._current_page += 1

    def __iter__(self):
        for row in self._data:
            yield row

        if self._current_page >= self._total_pages:
            return

        length = len(self._data)
        while self._current_page < self._total_pages:
            self._fetch_next_page()
            for i in range(len(self._data) - length):
                yield self._data[i + length]
            length = len(self._data)

        # update length to precise length
        self._length = length
