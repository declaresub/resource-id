"""Litestar integration for :class:`ResourceId`.

Importing this module registers ``ResourceId`` as a litestar path-parameter
type, so routes may be declared with ``{id:resourceid}`` and receive a parsed
``ResourceId`` instance::

    import resource_id.litestar  # registers the path-param type (side effect)
    from resource_id.litestar import ResourceIdPathParameter

    @get("/widgets/{widget_id:resourceid}")
    async def get_widget(widget_id: ResourceIdPathParameter) -> ...:
        ...

Litestar has no public API for custom path-parameter types
(litestar-org/litestar#4205, closed "not planned"), so registration uses the
same internal maps litestar's own built-in types (``int``, ``uuid``, ...) use.

This module also exposes :class:`ResourceIdSchemaPlugin`, which teaches
litestar's OpenAPI generator to render ``ResourceId`` fields as strings, and
:data:`ResourceIdPathParameter`, a convenience annotated path-parameter type.

Requires the ``litestar`` extra: ``pip install resource-id[litestar]``.
"""

from typing import Annotated, Any

import litestar.routes.base as litestar_base
from litestar.openapi.spec import OpenAPIType, Schema
from litestar.params import PathParameter
from litestar.plugins import OpenAPISchemaPlugin

from .resource_id import ResourceId

__all__ = ["ResourceIdPathParameter", "ResourceIdSchemaPlugin"]


# Register ResourceId as the "resourceid" path-parameter type. litestar parses a
# matched segment by calling the mapped type, i.e. ResourceId(segment).
litestar_base.param_type_map["resourceid"] = ResourceId  # pyright: ignore[reportUnknownMemberType]
litestar_base.parsers_map[ResourceId] = ResourceId


class ResourceIdSchemaPlugin(OpenAPISchemaPlugin):
    """Render ``ResourceId`` fields as strings in litestar's OpenAPI output.

    Litestar builds OpenAPI schemas with its own plugin system rather than
    pydantic's ``__get_pydantic_json_schema__``. ``ResourceId`` is a plain class
    (not a ``BaseModel``, not a stdlib type), so without this plugin a response
    field typed ``ResourceId`` serializes to the empty schema ``{}`` ("any")
    instead of a string. Add it to the app:
    ``Litestar(..., plugins=[ResourceIdSchemaPlugin()])``.
    """

    @staticmethod
    def is_plugin_supported_type(value: Any) -> bool:
        return isinstance(value, type) and issubclass(value, ResourceId)

    def to_openapi_schema(self, field_definition: Any, schema_creator: Any) -> Schema:
        # Mirrors ResourceId._json_schema(); built field-wise so the static
        # types check (litestar types `format` as a standard-formats enum, which
        # has no "resource-id" member, but OpenAPI `format` is an open string).
        return Schema(
            type=OpenAPIType.STRING,
            format="resource-id",  # pyright: ignore[reportArgumentType]
            title="ResourceId",
            description="An opaque identifier.",
        )


#: ``ResourceId`` annotated as a litestar path parameter. ``PathParameter`` pins
#: the parameter type so a dependency like ``id: ResourceIdPathParameter`` resolves
#: to the route's ``{id:resourceid}`` path param without query/path ambiguity.
ResourceIdPathParameter = Annotated[ResourceId, PathParameter()]
