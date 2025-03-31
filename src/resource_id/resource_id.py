"""ResourceId implements base62-encoded identifiers, suitable for URLs and URIs."""

from typing import Any, Protocol, Union, runtime_checkable
from uuid import UUID

try:
    from typing import TypeAlias
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAlias


from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


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

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value != other.value
        else:
            return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value < other.value
        else:
            return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value <= other.value
        else:
            return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value > other.value
        else:
            return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value >= other.value
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
            # I presume that the standard input is a base-62 encoded integer.
            # Thus we try this case first to take advantage of zero-cost exception
            # handling in python 3.11+.  Only that fails do we attempt to parse value
            # as a UUID string.
            # The presumption means that a hex string of length 32 will be parsed as a base-62
            # encoded int, not a UUID.  This preserves the earlier behavior of _to_int.
            try:
                return b62decode(value)
            except ValueError as exc:
                try:
                    return UUID(value).int
                except ValueError:
                    raise exc

        elif isinstance(value, Base62Encodable):  # type: ignore
            int_value = int(value)
            if int_value < 0:
                raise ValueError("value must be non-negative.")
            return int_value
        else:
            raise TypeError("value must be str or Base62Encodable.")

    @classmethod
    def _json_schema(cls):
        return {
            "title": cls.__name__,
            "description": "An opaque identifier.",
            "type": "string",
            "format": "resource-id",
        }

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:  # type: ignore
        return core_schema.no_info_plain_validator_function(
            cls,
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, return_schema=core_schema.str_schema()
            ),
        )  # type: ignore

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return cls._json_schema()
