from typing import Union
from uuid import UUID

import pydantic
import pytest

from resource_id.resource_id import Base62Encodable, ResourceId, b62decode, b62encode

pydantic_major_version = int(pydantic.VERSION.split(".")[0])


@pytest.mark.parametrize("src, expected", [(1, "1"), (62, "10")])
def test_b62encode(src: Base62Encodable, expected: str):
    assert b62encode(src) == expected


def test_b62encode_fail():
    with pytest.raises(ValueError):
        b62encode(-1)


@pytest.mark.parametrize("src, expected", [("1", 1), ("11", 63)])
def test_b62decode(src: str, expected: int):
    assert b62decode(src) == expected


def test_b62decode_fail():
    with pytest.raises(ValueError):
        b62decode("*")


@pytest.mark.parametrize("arg, value", [(1, 1), ("11", 63), (UUID(int=1728), 1728)])
def test_init(arg: Union[str, Base62Encodable], value: int):
    assert ResourceId(arg).value == value


def test_init_bad_arg_value():
    with pytest.raises(ValueError):
        ResourceId(-1)


def test_init_bad_arg_type():
    with pytest.raises(TypeError):
        ResourceId({})  # type: ignore


def test_uuid():
    value = UUID(int=123)
    assert ResourceId(value).uuid == value


def test_repr():
    arg = 1
    assert repr(ResourceId(arg)) == "1"


def test_eq():
    assert ResourceId(1) == ResourceId(1)


def test_not_eq():
    assert ResourceId(1) != 1


def test_hash():
    assert hash(ResourceId(1)) == hash(1)


def test_int():
    value = 2
    assert int(ResourceId(value)) == value


def test___get_validators__():
    # for pydantic 2, ResourceId is wrapped with Annotated, and special methot lookup bypasses __getattr__.  Thus we must
    # get the actual ResourceId class from the Annootated object.
    __get_validators__ = ResourceId.__origin__.__get_validators__ if hasattr(ResourceId, "__origin__") else ResourceId.__get_validators__  # type: ignore
    assert next(__get_validators__()) == ResourceId.validate  # type: ignore


def test_validate():
    assert ResourceId.validate("test") == ResourceId("test")


def test_modify_schema():
    __modify_schema__ = ResourceId.__origin__.__modify_schema__ if hasattr(ResourceId, "__origin__") else ResourceId.__modify_schema__  # type: ignore
    schema = {}
    __modify_schema__(schema)
    assert schema == ResourceId._json_schema()  # type: ignore


def test__json_schema():
    assert isinstance(ResourceId._json_schema(), dict)  # type: ignore


@pytest.mark.skipif(
    not hasattr(pydantic, "TypeAdapter"),
    reason="Serialization is only implemented for pydantic 2.",
)
def test_serialization_pydantic2():
    V = pydantic.TypeAdapter(ResourceId)
    id = ResourceId("test")
    assert V.dump_json(id) == b'"test"'
