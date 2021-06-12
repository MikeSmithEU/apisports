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
