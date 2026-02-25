# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Setup** (create and activate a virtual environment first):
```
pip install -r requirements.txt
```

**Run tests with coverage:**
```
pytest --cov=src --cov-report term-missing tests
```

**Run a single test:**
```
pytest tests/test_resource_id.py::test_name
```

**Run tests across all supported Python versions:**
```
tox
```

**Lint:**
```
ruff check src tests
```

**Build distribution:**
```
python -m build
```

## Architecture

This is a single-class Python library. All logic lives in [src/resource_id/resource_id.py](src/resource_id/resource_id.py); the package `__init__.py` re-exports `ResourceId`.

**`ResourceId`** stores its value internally as a plain `int`. It accepts `str` (base62 or UUID string) or any object implementing `__int__` (the `Base62Encodable` protocol). `__repr__` returns the base62 string representation.

**Pydantic integration** is handled via `__get_pydantic_core_schema__` and `__get_pydantic_json_schema__` classmethods — no separate adapter or plugin needed. Pydantic validates by calling `ResourceId(value)` and serializes by calling `str(resource_id)` (which uses `__repr__`).

**Base62 alphabet:** `0–9` then `a–z` then `A–Z` (digits first, lowercase before uppercase). This is not the same as standard base64 ordering.

**Version** is managed by `setuptools_scm` from git tags — there is no hardcoded version string in source.
