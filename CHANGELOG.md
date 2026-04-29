# Changelog

## 1.5.0
* Drop support for Python 3.9; require Python >= 3.10.
* `ResourceId()` with no arguments now generates a new identifier via `uuid4`.
* Add class attribute `uuid_gen` to allow overriding the UUID generator.
* `__repr__` now returns `ResourceId(...)` instead of the bare base62 string. **This is a breaking change** for code that relied on `repr()` for serialization.
* Add `__str__` method that returns the base62 string (preserves `str()` and f-string behavior).
* `b62decode` now raises `ValueError` on empty string input (previously raised `IndexError`).
* `b62decode` no longer accepts negative values.
* Commits are now signed using gitsign (sigstore).

## 1.4.0
* resource-id now requires pydantic 2; pydantic 1 support has been dropped.
* ResourceId objects are now comparable.
* Packages are now published to pypi using trusted publishing.
* Drop support for python 3.8; add python 3.13.

## 1.3.0
* ResourceId now parses string inputs as follows: first it attempts to parse input
as a base62-encoded int; if that fails, it attempts to parse as a UUID formatted string.
This turns out to be quite useful when retrieving data as JSON from a database.

## 1.2.3
* ResourceId json schema type is now correctly set to 'string'.

## 1.2.2
* Rewrite pydantic 2 methods in ResourceId in response to changes in Pydantic 2.0.3 that broke
JSON schema generation by ResourceId. This caused problems for FastAPI openapi documentation generation.

## 1.2,1
* Replace Pydantic annotation with implementation of Pydantic class methods in ResourceId class.
FastAPI does not appear to be able to handle Pydantic-annotated types.

## 1.2.0
* ResourceId.__eq__ now returns NotImplemented in response to a class mismatch.
* Pydantic 2 support is now implemented via annotation of the ResourceId type.
* tox test matric tests Pydantic 1 and 2 with each supported python version.

## 1.1.0
* Drop support for python 3.7; add 3.11 to tox environment list.
* Update ResourceId to support Pydantic 2.  This requires adding Pydantic
    as a dependency.  Support for Pydantic 1 remains.

## 1.0.0

* Initial release.
