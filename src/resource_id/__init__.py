try:
    from importlib.metadata import PackageNotFoundError, metadata  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, metadata  # type: ignore


from .resource_id import ResourceId


__all__ = ['ResourceId']


try:
    __version__: str = metadata(__name__)["version"]
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = ""
