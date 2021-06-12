from apisports.data import *
import pytest


def test_abstractdata():
    with pytest.raises(NotImplementedError):
        iter(AbstractData())

    with pytest.raises(NotImplementedError):
        len(AbstractData())


def test_nonedata_general():
    assert len(NoneData) == 0
    assert list(iter(NoneData)) == []
    assert NoneData() == NoneData


@pytest.mark.parametrize("data", [
    None,
    {"response": None},
    {"response": []},
    {}
])
def test_nonedata(data):
    data_obj = AbstractData.create(client=None, data=data)

    assert data_obj == NoneData
    assert len(data_obj) == 0
    assert list(iter(data_obj)) == []


@pytest.mark.parametrize("data", [
    1, 0, "test", True, False, None, 4, -5, -1.2
])
def test_singledata(data):
    data_obj = AbstractData.create(
        client=None, data={"response": [data]}
    )
    assert type(data_obj) is SingleData
    assert len(data_obj) == 1
    assert data_obj.item() == data
    assert next(iter(data_obj)) == data
    assert list(iter(data_obj)) == [data]

    # None will (correctly) result in NoneData
    if data is None:
        return

    data_obj = AbstractData.create(
        client=None, data={"response": data}
    )
    assert type(data_obj) is SingleData
    assert len(data_obj) == 1
    assert data_obj.item() == data
    assert next(iter(data_obj)) == data

    assert str(data_obj) == 'SingleData(%r)' % (data,)
    assert str(data_obj) == repr(data_obj)


def test_simple_data():
    data = list(range(5))
    data_obj = AbstractData.create(
        client=None, data={"response": data}
    )

    assert str(data_obj) == 'SimpleData(%r)' % (data,)
    assert str(data_obj) == repr(data_obj)
    assert len(data_obj) == 5
    assert list(iter(data_obj)) == data

    iterator = iter(data_obj)
    assert next(iterator) == 0
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert next(iterator) == 3
    assert next(iterator) == 4


def test_paged_data():
    data_obj = AbstractData.create(
        client=None, data={
            "response": list(range(3)),
            "paging": {
                "current": 1,
                "total": 3,
            },
            "results": 3,
            "get": "/null",
        }
    )

    assert len(data_obj) == 9
    iterator = iter(data_obj)
    assert next(iterator) == 0
    assert next(iterator) == 1
    assert next(iterator) == 2

    with pytest.raises(PagedDataError) as exc:
        next(iterator)

    assert "no client class known" in str(exc)

    data_obj = AbstractData.create(
        client=None, data={
            "response": list(range(3)),
            "paging": {
                "current": 1,
                "total": 3,
            },
            "results": 3,
        }
    )

    with pytest.raises(PagedDataError) as exc:
        list(iter(data_obj))

    assert "no request-uri known" in str(exc)
