__all__ = [
    "__version__",
    "version",
    "__version_tuple__",
    "version_tuple",
]

try:
    from ._version import __version__, __version_tuple__, version, version_tuple
except ImportError:
    __version__ = version = "unknown"
    __version_tuple__ = version_tuple = (0, 1, "unknown")
