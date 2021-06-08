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
        response = data['response']
        if 'paging' in data and \
                data['paging']['total'] > 1 and \
                data['paging']['current'] == 1:
            return PagedData(client, data)
        length = len(response)
        if length == 0:
            return NoneData
        if length == 1:
            return SingleData(response)
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


class SingleData(SimpleData):
    """
    Adds an extra method to easily access data that only contains a single item.
    """

    def item(self):
        return next(iter(self))


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
        self._get = data['get']
        self._parameters = data['parameters']

    def __len__(self):
        """
        This is just an estimate (maximum) until after all data has been fetched
        """

        return self._length

    def _fetch_next_page(self):
        result = self._client.get(
            self._get,
            {
                **self._parameters,
                "page": self._current_page + 1
            })
        if not result.ok:
            raise PagedDataError("Could not fetch next page", result.error_description())
        self._data += list(iter(result.data()))
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
