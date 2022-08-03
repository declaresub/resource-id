# ResourceId

The resource-id package provides a ResourceId class implementing base62-encoded identifiers, suitable
for URLs, URIs, and probably something else.

ResourceId is written to work with [Pydantic](https://pydantic-docs.helpmanual.io), but does not depend on Pydantic.
In particular, it can be used with [FastAPI](https://fastapi.tiangolo.com) as a path parameter.




## Requirements

Resource-id requires Python >= 3.7. For python <= 3.9, typing_extensions is required.

## Installation

    pip install resource-id

## Usage

There is one class, ResourceId.

    from resource_id import ResourceId

Create a ResourceId:

    id = ResourceId(43)
    id1 = ResourceId('deadbeef')
    id2 = ResourceId(UUID(int=101))


Create a URL path using a ResourceId:

    path = f"/api/foo/{ResourceId('deadbeef')}"

Define a FastAPI request handler with a ResourceId:

    @app.get('/api/foo/{foo_id}')
    async def get_foo(foo_id: ResourceId):
        ...

Here, FastAPI will validate the value of the path variable foo_id with Pydantic.  If validation fails, 
FastApi (unfortunately) returns 422 Unprocessable Entity.

    
Convert a ResourceId to a UUID:

    res_id = ResourceId(43)
    id = res_id.uuid






## Testing

Run unit tests:

    pytest --cov=src --cov-report term-missing tests


