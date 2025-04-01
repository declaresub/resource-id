# ResourceId

The resource-id package provides a ResourceId class implementing base62-encoded identifiers, suitable
for URLs, URIs, and perhaps something else.

ResourceId is written to work with [Pydantic](https://pydantic-docs.helpmanual.io).
In particular, it can be used with [FastAPI](https://fastapi.tiangolo.com) as a path parameter.

![tox](https://github.com/declaresub/resource-id/actions/workflows/tox.yml/badge.svg)


## Requirements

Resource-id requires Python >= 3.9. For python == 3.9, typing_extensions is required.
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

In fact a ResourceId can be created from any object that implements __int__,


Create a URL path using a ResourceId:

    path = f"/api/foo/{ResourceId('deadbeef')}"

Define a FastAPI request handler with a ResourceId:

    @app.get('/api/foo/{foo_id}')
    async def get_foo(foo_id: ResourceId):
        ...

Here, FastAPI will validate the value of the path variable foo_id with Pydantic.  If validation fails, 
FastAPI returns 422 Unprocessable Entity.

    
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

The requirements.txt file is for development and testing. If you have any interest in either,
create a virtual environment and install this package.  The following may work.

    python -m venv /path/to/virtual-environment
    cd /path/to/virtual-environment
    source bin/activate
    pushd /path/to/repository
    pip install -r requirements.txt


Run unit tests:

    pytest --cov=src --cov-report term-missing tests

Or

    tox


## Package Verification

As of version 1.4.0, releases use trusted publishing.
