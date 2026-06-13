"""ResourceId implements base62-encoded identifiers, suitable for URLs and URIs."""

from typing import Any, TypeAlias, Union
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


__all__ = ["ResourceId"]

ALPHABET = tuple("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
DECODE_MAP = {x: idx for idx, x in enumerate(ALPHABET)}
UUID_BITS = 128


ResourceIdValue: TypeAlias = Union[str, int, UUID, "ResourceId"]


def b62encode(value: Union[int, UUID]):
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


# The base62 encoding of any in-range id (value < 2**UUID_BITS) is at most this
# many characters; a longer string can only be a UUID, not a base62 id.
_MAX_BASE62_ID_LEN = len(b62encode((1 << UUID_BITS) - 1))


def b62decode(value: str):
    """Decode a base62-encoded str.  Returns int.  Raises ValueError if value is invalid."""

    if value == "":
        raise ValueError("invalid literal for b62decode: ''")

    x = 0
    for digit in value:
        try:
            x = x * 62 + DECODE_MAP[digit]
        except KeyError as exc:
            raise ValueError(f"Invalid base62 value '{value}'.") from exc
    return x


class ResourceId:
    __slots__ = ["value"]
    uuid_gen = staticmethod(uuid4)

    def __init__(self, value: ResourceIdValue | None = None):
        if value is None:
            value = self.uuid_gen()
        int_value = self._to_int(value)
        # A ResourceId must fit in a UUID, so .uuid is always valid: reject
        # out-of-range values at construction rather than deferring the failure.
        if int_value < 0:
            raise ValueError("value must be non-negative.")
        if int_value >> UUID_BITS:
            raise ValueError(f"value must fit in a UUID (< 2**{UUID_BITS}).")
        self.value = int_value

    @property
    def uuid(self) -> UUID:
        return UUID(int=self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({b62encode(self.value)})"

    def __str__(self) -> str:
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
    def _to_int(value: object):
        # value is typed `object`, not ResourceIdValue: __init__ enforces the
        # accepted types at type-check time, but this validator must also defend
        # against untyped callers (pydantic, dynamic code) at runtime.
        match value:
            case str():
                # Base62 is the canonical form, but our encoding of any in-range
                # id is at most _MAX_BASE62_ID_LEN chars; a longer string can
                # only be a UUID (36-char dashed or 32-char dashless hex).
                # Parse those as a UUID first so e.g. uuid.hex round-trips
                # instead of silently mis-decoding as a base62 value.  No string
                # this short is ever a valid UUID, so shorter input takes the
                # base62 path directly.
                if len(value) > _MAX_BASE62_ID_LEN:
                    try:
                        return UUID(value).int
                    except ValueError:
                        pass
                return b62decode(value)
            case ResourceId():
                # idempotent/copy construction; pydantic re-validates by calling
                # ResourceId(value) even when value is already a ResourceId.
                return value.value
            case UUID():
                return value.int
            case int():
                # bool is a subclass of int, so it lands here and converts
                # losslessly.  float/Decimal/Fraction are deliberately excluded:
                # their __int__ truncates the fractional part, the silent error
                # class behind the Ariane 5 failure.  ResourceIdValue rejects
                # them at type-check time; this rejects them at runtime via the
                # default case.  __init__ enforces the value range.
                return value
            case _:
                raise TypeError("value must be a str, int, or UUID.")

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
