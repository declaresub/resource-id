# Changelog


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
