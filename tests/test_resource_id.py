from typing import Any, Union
from uuid import UUID

import jsonschema
import pydantic
import pytest

from resource_id.resource_id import Base62Encodable, ResourceId, b62decode, b62encode


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


def test_uuid_str():
    value = UUID(int=666)
    assert ResourceId(str(value)).uuid == value


def test_bad_str():
    with pytest.raises(ValueError):
        ResourceId("oops!")


def test_repr():
    arg = 1
    assert repr(ResourceId(arg)) == "1"


def test_eq():
    assert ResourceId(1) == ResourceId(1)


def test_ne():
    assert ResourceId(1) != ResourceId(2)


def test_lt():
    assert ResourceId(1) < ResourceId(2)


def test_le():
    assert ResourceId(2) <= ResourceId(2)


def test_gt():
    assert ResourceId(2) > ResourceId(1)


def test_ge():
    assert ResourceId(2) >= ResourceId(2)


@pytest.mark.parametrize(
    "result",
    [
        ResourceId(1).__eq__(1),
        ResourceId(1).__ne__(1),
        ResourceId(1).__lt__(1),
        ResourceId(1).__le__(1),
        ResourceId(1).__gt__(1),
        ResourceId(1).__ge__(1),
    ],
)
def test_cmp_not_implemented(result: Any):
    assert result is NotImplemented


def test_hash():
    assert hash(ResourceId(1)) == hash(1)


def test_int():
    value = 2
    assert int(ResourceId(value)) == value


def test_validate():
    t = pydantic.TypeAdapter(ResourceId)
    assert t.validate_json('"test"') == ResourceId("test")


def test_serialization():
    V = pydantic.TypeAdapter(ResourceId)
    id = ResourceId("test")
    assert V.dump_json(id) == b'"test"'


def test_model_json_schema():
    class Model(pydantic.BaseModel):
        id: ResourceId

    m = Model(id=ResourceId("test"))
    assert m.model_json_schema(mode="serialization")


def test_json_schema():
    assert jsonschema.validate("test", ResourceId._json_schema()) is None  # pyright: ignore[reportPrivateUsage]
