from typing import Union

import pytest
from uuid import UUID

from resource_id import ResourceId
from resource_id.resource_id import Base62Encodable


@pytest.mark.parametrize('arg', [1, 'test', UUID(int=1728)])
def test_init(arg: Union[str, Base62Encodable]):
    assert ResourceId(arg)


def test_init_bad_value():
    with pytest.raises(ValueError):
        ResourceId(-1)

def test_init_bad_type():
    with pytest.raises(TypeError):
        ResourceId(None) # type: ignore

def test_bad_value_after_init():
    res_id = ResourceId(1)
    res_id.value = -1
    with pytest.raises(ValueError):
        repr(res_id)

def test_repr():
    arg = 1
    assert repr(ResourceId(arg)) == '1'


def test_invalid_base62():
    with pytest.raises(ValueError):
        ResourceId("bad-value")

def test_uuid():
    value = UUID(int=123)
    assert ResourceId(value).uuid == value

def test_eq():
    assert ResourceId(1) == ResourceId(1)

def test_eq_class_mismatch():
    with pytest.raises(TypeError):
        ResourceId(1) != 1  # type: ignore

def test_hash():
    assert hash(ResourceId(1))

def test_int():
    value = 2
    assert int(ResourceId(value)) == value


def test___get_validators__():
    assert next(ResourceId.__get_validators__()) == ResourceId.validate

@pytest.mark.parametrize('arg', [1, 'test', UUID(int=1728)])
def test_validate(arg: Union[str, Base62Encodable]):
    assert ResourceId.validate(arg)

def test___modify_schema__():
    field_schema = {}
    ResourceId.__modify_schema__(field_schema)
    assert field_schema['title'] == ResourceId.__name__

