"""A setuptools plugin to write git details to the designated .py file."""

from setuptools_git_details.main import (
    Generate,
    finalize_distribution_options,
    validate_write_to,
)

# Public API:
__all__ = [
    "Generate",
    "finalize_distribution_options",
    "validate_write_to",
]
