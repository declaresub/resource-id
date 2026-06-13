# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for development.

**Setup:**
```
uv sync --all-extras --dev
```

**Run tests with coverage:**
```
uv run pytest --cov=src --cov-report term-missing tests
```

**Run a single test:**
```
uv run pytest tests/test_resource_id.py::test_name
```

**Lint:**
```
uv run ruff check src tests
```

**Build distribution:**
```
uv build
```

## Architecture

This is a single-class Python library. All logic lives in [src/resource_id/resource_id.py](src/resource_id/resource_id.py); the package `__init__.py` re-exports `ResourceId`.

**`ResourceId`** stores its value internally as a plain `int`, constrained to the UUID range (`0 <= value < 2**128`) at construction. It accepts a `str` (base62, or a UUID string in dashed or dashless-hex form), an `int`, a `uuid.UUID`, or another `ResourceId` — the `ResourceIdValue` union. A string longer than 22 chars (the max base62 length for an in-range id) is parsed as a UUID rather than base62. Non-integer numeric inputs such as `float` are rejected at construction to avoid silent truncation. `__repr__` returns the base62 string representation.

**Pydantic integration** is handled via `__get_pydantic_core_schema__` and `__get_pydantic_json_schema__` classmethods — no separate adapter or plugin needed. Pydantic validates by calling `ResourceId(value)` and serializes by calling `str(resource_id)` (which uses `__repr__`).

**Base62 alphabet:** `0–9` then `a–z` then `A–Z` (digits first, lowercase before uppercase). This is not the same as standard base64 ordering.

**Version** is managed by `setuptools_scm` from git tags — there is no hardcoded version string in source.
