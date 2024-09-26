from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any, Dict

from setuptools_git_details.git import get_all_details

if sys.version_info >= (3, 11):
    from tomllib import loads as load_toml
else:
    from tomli import loads as load_toml


TOOL = "tool"
SETUPTOOLS_GIT_DETAILS = "setuptools_git_details"


TEMPLATE = Template("""\
# This file was generated by setuptools-git-details.
# Do NOT change. Do NOT track in version control.

from typing import Dict

git: Dict[str, str | bool] = {
    "name": "${name}",
    "revision": "${revision}",
    "branch": "${branch}",
    "tag": "${tag}",
    "url": "${url}",
    "git": "${git}",
    "is_dirty": ${is_dirty},
}
__git__ = git
""")


@dataclass
class Configuration:
    """setuptools-git-details configuration"""

    file: Path

    @classmethod
    def from_file(
        cls,
        name: str | os.PathLike[str] = "pyproject.toml",
    ) -> Configuration:
        """
        Read Configuration from pyproject.toml.
        """
        path = Path(name)
        data = path.read_text(encoding="utf-8")
        pyproject_data = load_toml(data)
        config = cls._validate_pyproject_toml(pyproject_data)
        return Configuration(file=Path(config["file"]))

    @classmethod
    def _validate_pyproject_toml(cls, pyproject_data: Dict[str, Any]) -> Dict[str, Any]:
        if TOOL not in pyproject_data:
            raise ValueError("Invalid pyproject.toml: no tool section")
        tool_section = pyproject_data[TOOL]
        if SETUPTOOLS_GIT_DETAILS not in tool_section:
            raise ValueError(
                f"Invalid pyproject.toml: no tool.{SETUPTOOLS_GIT_DETAILS} section"
            )
        config = tool_section[SETUPTOOLS_GIT_DETAILS]
        if "file" not in config:
            raise ValueError(
                f"Invalid tool.{SETUPTOOLS_GIT_DETAILS} section: file key-value pair is missing"
            )
        return config


def main(filepath: str | os.PathLike[str] = "pyproject.toml") -> None:
    config = Configuration.from_file(filepath)
    git_details = get_all_details()
    content = TEMPLATE.substitute(**git_details)
    config.file.write_text(content)
