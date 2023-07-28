# Changelog

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
