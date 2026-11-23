"""OPERA-X shared application services."""

from .version import get_version

# Expose the conventional package attribute without maintaining a second
# hardcoded version. VERSION is the release's single source of truth.
__version__ = get_version()

__all__ = ["__version__", "get_version"]
