# ResourceId

The resource-id package provides a ResourceId class implementing base62-encoded identifiers, suitable
for URLs, URIs, and perhaps something else.

ResourceId is written to work with [Pydantic](https://pydantic-docs.helpmanual.io).
In particular, it can be used with [FastAPI](https://fastapi.tiangolo.com) as a path parameter.

![tox](https://github.com/declaresub/resource-id/actions/workflows/tox.yml/badge.svg)


## Requirements

Resource-id requires Python >= 3.10.
As of version 1.4.0, resource-id requires pydantic 2.


## Installation

    pip install resource-id

## Usage

There is one class, ResourceId.

    from resource_id import ResourceId

Create a ResourceId:

    id = ResourceId(43)
    id1 = ResourceId('deadbeef')
    id2 = ResourceId(UUID(int=101))

A ResourceId can be created from a str (a base62 string, or a UUID in dashed or
dashless-hex form), an int, a uuid.UUID, or another ResourceId. The value must
be non-negative and fit in a UUID (< 2**128).


Create a URL path using a ResourceId:

    path = f"/api/foo/{ResourceId('deadbeef')}"

Define a FastAPI request handler with a ResourceId:

    @app.get('/api/foo/{foo_id}')
    async def get_foo(foo_id: ResourceId):
        ...

Here, FastAPI will validate the value of the path variable foo_id with Pydantic.  If validation fails, 
FastAPI returns 422 Unprocessable Entity.

### Litestar

FastAPI builds its OpenAPI schema from Pydantic, so ResourceId works there out
of the box.  Litestar uses its own schema system and has no public API for
custom path-parameter types ([litestar#4205][litestar-4205]), so resource-id
ships the integration as an optional extra:

    pip install resource-id[litestar]

Importing `resource_id.litestar` registers ResourceId as the `resourceid`
path-parameter type; add `ResourceIdSchemaPlugin` to your app so ResourceId
fields render correctly in the OpenAPI document:

```python
import resource_id.litestar  # registers the {...:resourceid} path-param type
from resource_id.litestar import ResourceIdPathParameter, ResourceIdSchemaPlugin
from litestar import Litestar, get


@get("/api/foo/{foo_id:resourceid}")
async def get_foo(foo_id: ResourceIdPathParameter) -> str:
    ...


app = Litestar([get_foo], plugins=[ResourceIdSchemaPlugin()])
```

The path parameter is parsed into a ResourceId (an invalid value yields a 400),
and the plugin renders ResourceId fields as `{"type": "string", "format":
"resource-id"}` instead of the empty schema litestar would otherwise emit.

[litestar-4205]: https://github.com/litestar-org/litestar/issues/4205

Convert a ResourceId to a UUID:

    res_id = ResourceId(43)
    id = res_id.uuid

### More

I have some projects that use PostgreSQL and asyncpg.  It is quite simple to add conversion between PostgreSQL UUID datatype and ResourceId.

```
def get_uuid(value: ResourceId) -> str:
    assert isinstance(value, ResourceId)
    return str(value.uuid)


def get_resource_id(value: str) -> ResourceId:
    assert isinstance(value, str)
    return ResourceId(UUID(value))


async def init_connection(conn: asyncpg.Connection):
    await conn.set_type_codec(
        "uuid", encoder=get_uuid, decoder=get_resource_id, schema="pg_catalog"
    )
```


## Testing

This project uses [uv](https://docs.astral.sh/uv/) for development.  To set up and run tests:

    uv sync --all-extras --dev
    uv run pytest tests


## Package Verification

As of version 1.4.0, releases use trusted publishing.
As of version 1.5.0, commits are now signed using gitsign.
