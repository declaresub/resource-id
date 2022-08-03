# ResourceId

The resource-id package provides a ResourceId class implementing base62-encoded identifiers, suitable
for URLs, URIs, and perhaps something else.

ResourceId is written to work with [Pydantic](https://pydantic-docs.helpmanual.io), but does not depend on Pydantic.
In particular, it can be used with [FastAPI](https://fastapi.tiangolo.com) as a path parameter.

![tox](https://github.com/declaresub/resource-id/actions/workflows/tox.yml/badge.svg)


## Requirements

Resource-id requires Python >= 3.7. For python <= 3.9, typing_extensions is required. For Python 3.7, 
importlib-metadata is required.

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
FastAPI (unfortunately) returns 422 Unprocessable Entity.

    
Convert a ResourceId to a UUID:

    res_id = ResourceId(43)
    id = res_id.uuid



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

I sign resource-id releases on pypi with my GPG key (3A27290FD243BD83BC3F5BC886C057F96A41A77B), which you can retrieve from https://keys.openpgp.org.  
You can verify a package by downloading it and its GPG signature file from pypi, then running gpg --verify.
