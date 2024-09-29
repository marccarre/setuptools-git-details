"""A setuptools plugin to write git details to the designated .py file."""

from setuptools_git_details.main import (
    finalize_distribution_options,
    main,
    setup_keywords,
)

# Public API:
__all__ = [
    "finalize_distribution_options",
    "setup_keywords",
    "main",
]
