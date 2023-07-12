from typing import Union
from uuid import UUID

import pydantic
import pytest

from resource_id import ResourceId
from resource_id.resource_id import Base62Encodable

pydantic_major_version = int(pydantic.VERSION.split(".")[0])


@pytest.mark.parametrize("arg", [1, "test", UUID(int=1728)])
def test_init(arg: Union[str, Base62Encodable]):
    assert ResourceId(arg)


def test_init_bad_value():
    with pytest.raises(ValueError):
        ResourceId(-1)


def test_init_bad_type():
    with pytest.raises(TypeError):
        ResourceId(None)  # type: ignore


def test_bad_value_after_init():
    res_id = ResourceId(1)
    res_id.value = -1
    with pytest.raises(ValueError):
        repr(res_id)


def test_repr():
    arg = 1
    assert repr(ResourceId(arg)) == "1"


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


@pytest.mark.parametrize("arg", [1, "test", UUID(int=1728)])
def test_validate(arg: Union[str, Base62Encodable]):
    assert ResourceId.validate(arg)


def test___modify_schema__():
    field_schema = {}
    ResourceId.__modify_schema__(field_schema)
    assert field_schema["title"] == ResourceId.__name__


class Foo(pydantic.BaseModel):
    id: ResourceId


def test_foo_init():
    foo = Foo(id=ResourceId("test"))
    assert foo.id == ResourceId("test")


def test_pydantic_json_schema():
    # it is not so easy to test __get_pydantic_json_schema__ directly without digging around in the innards of pydantic 2.
    # so we just check the schema generated for Foo to see that its id item has the expected JSON schema for ResourceId.
    foo = Foo(id=ResourceId("test"))
    schema = foo.schema() if pydantic_major_version < 2 else foo.model_json_schema()  # type: ignore
    assert "properties" in schema
    assert schema["properties"]["id"] == {
        "description": ResourceId.schema_description,
        "title": ResourceId.__name__,
        "type": "string",
    }
