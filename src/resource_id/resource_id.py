"""ResourceId implements base62-encoded identifiers, suitable for URLs and URIs."""

from typing import Any, Dict, Protocol, Union, runtime_checkable
from uuid import UUID

try:
    from typing import TypeAlias
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAlias


__all__ = ["ResourceId"]

ALPHABET = tuple("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
DECODE_MAP = {x: idx for idx, x in enumerate(ALPHABET)}


@runtime_checkable
class Base62Encodable(Protocol):
    def __int__(self) -> int:  # pragma: no cover
        ...


ResourceIdValue: TypeAlias = Union[str, Base62Encodable]


def b62encode(value: Base62Encodable):
    """Encode anything that can be converted to a non-negative int.  This includes uuid.UUID objects."""
    value = int(value)
    if 0 > value:
        raise ValueError("value must convert to a non-negative integer.")
    x = value
    b62_repr: str = ""
    while x:
        x, b62_repr = (
            x // 62,
            ALPHABET[x % 62] + b62_repr,
        )
    return b62_repr if b62_repr else "0"


def b62decode(value: str):
    """Decode a base62-encoded str.  Returns int.  Raises ValueError if value is invalid."""

    sgn, value = (-1, value[1:]) if value[0] == "-" else (1, value)
    x = 0
    for digit in value:
        try:
            x = x * 62 + DECODE_MAP[digit]
        except KeyError as exc:
            raise ValueError(f"Invalid base62 value '{value}'.") from exc
    return sgn * x


class ResourceId:
    __slots__ = ["value"]

    def __init__(self, value: ResourceIdValue):
        self.value = self._to_int(value)

    @property
    def uuid(self) -> UUID:
        return UUID(int=self.value)

    def __repr__(self) -> str:
        return b62encode(self.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.value)

    def __int__(self):
        return self.value

    @staticmethod
    def _to_int(value: ResourceIdValue):
        # to be replaced with a match statement someday.
        if isinstance(value, str):
            return b62decode(value)
        elif isinstance(value, Base62Encodable):  # type: ignore
            int_value = int(value)
            if int_value < 0:
                raise ValueError("value must be non-negative.")
            return int_value
        else:
            raise TypeError("value must be str or Base62Encodable.")

    # validation methods for use by Pydantic 1
    @classmethod
    def _json_schema(cls):
        return {
            "title": cls.__name__,
            "description": "An opaque resource id.",
            "type": "string",
        }

    @classmethod
    def __get_validators__(cls):
        # for pydantic 1
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        # __get_pydantic_json_schema__ replaces __modify_schema__ in pydantic 2.
        field_schema.update(cls._json_schema())

    @classmethod
    def validate(cls, value: ResourceIdValue):
        return cls(value)


try:
    # these pydantic object exist only in pydantic 2.
    from pydantic import PlainSerializer, PlainValidator, WithJsonSchema

    try:  # pragma: no cover
        from typing import Annotated
    except ImportError:  # pragma: no cover
        from typing_extensions import Annotated

    ResourceId = Annotated[ResourceId, PlainValidator(ResourceId), PlainSerializer(lambda x: str(x), return_type=str), WithJsonSchema(ResourceId._json_schema(), mode=None)]  # type: ignore
except ImportError:  # pragma: no cover
    pass
