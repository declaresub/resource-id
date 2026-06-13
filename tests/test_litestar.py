from typing import Any

import pytest

pytest.importorskip("litestar")

from litestar import Litestar, get  # noqa: E402
from litestar.testing import TestClient  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from resource_id import ResourceId  # noqa: E402
from resource_id.litestar import ResourceIdPathParameter, ResourceIdSchemaPlugin  # noqa: E402


def test_path_param_routing():
    @get("/r/{rid:resourceid}")
    async def handler(rid: ResourceIdPathParameter) -> str:
        # The matched segment is parsed into a ResourceId instance.
        assert isinstance(rid, ResourceId)
        return str(rid)

    app = Litestar([handler])
    with TestClient(app) as client:
        assert client.get("/r/1").text == "1"
        # base62 round-trip: ResourceId(255) -> "47" -> ResourceId(255)
        assert client.get(f"/r/{ResourceId(255)}").text == str(ResourceId(255))


def test_invalid_path_param_is_rejected():
    @get("/r/{rid:resourceid}")
    async def handler(rid: ResourceIdPathParameter) -> str:
        return str(rid)

    app = Litestar([handler])
    with TestClient(app) as client:
        # "!" is not a valid base62 character, so ResourceId() raises and the
        # request is rejected rather than reaching the handler.
        assert client.get("/r/oops!").status_code >= 400


def _only_model_properties(app: Litestar) -> dict[str, Any]:
    # The app defines exactly one model; fetch its properties without depending
    # on litestar's component name (which differs for function-local classes).
    schemas = app.openapi_schema.to_schema()["components"]["schemas"]
    (model,) = schemas.values()
    return model["properties"]


def test_response_field_gets_a_string_schema():
    class Out(BaseModel):
        rid: ResourceId

    @get("/x")
    async def handler() -> Out:
        return Out(rid=ResourceId(1))

    app = Litestar([handler], plugins=[ResourceIdSchemaPlugin()])
    prop = _only_model_properties(app)["rid"]
    assert prop["type"] == "string"
    assert prop["format"] == "resource-id"


def test_response_field_without_plugin_is_untyped():
    # Documents why the plugin is needed: litestar emits {} for a bare
    # ResourceId field without it.
    class Out(BaseModel):
        rid: ResourceId

    @get("/x")
    async def handler() -> Out:
        return Out(rid=ResourceId(1))

    app = Litestar([handler])
    assert _only_model_properties(app)["rid"] == {}


def test_schema_plugin_supports_subclasses():
    class Sub(ResourceId): ...

    assert ResourceIdSchemaPlugin.is_plugin_supported_type(ResourceId)
    assert ResourceIdSchemaPlugin.is_plugin_supported_type(Sub)
    assert not ResourceIdSchemaPlugin.is_plugin_supported_type(int)
    assert not ResourceIdSchemaPlugin.is_plugin_supported_type("not a type")
