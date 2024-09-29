from __future__ import annotations

import logging
import os
import shutil
import sys
from dataclasses import dataclass
from distutils.errors import DistutilsOptionError, DistutilsSetupError
from pathlib import Path
from string import Template
from typing import Any, Dict, Mapping

from setuptools.dist import Distribution
from setuptools.errors import PlatformError, SetupError

import setuptools_git_details.git as git

if sys.version_info < (3, 11):
    from tomli import loads as load_toml
else:
    from tomllib import loads as load_toml


logger = logging.getLogger(__name__)


def get_log_level(env: Mapping[str, str] = os.environ) -> int:
    value: str | None = env.get("SETUPTOOLS_GIT_DETAILS_DEBUG")
    return logging.WARNING if value is None else logging.DEBUG


def get_formatter() -> logging.Formatter:
    return logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
    )


def get_console_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(get_formatter())
    return handler


def get_file_handler(env: Mapping[str, str] = os.environ) -> logging.Handler:
    handler = logging.FileHandler(
        env.get("SETUPTOOLS_GIT_DETAILS_LOG_FILE", "setuptools_git_details.log")
    )
    handler.setFormatter(get_formatter())
    return handler


logger.addHandler(get_console_handler())
logger.addHandler(get_file_handler())
logger.setLevel(get_log_level())


PYPROJECT_TOML = "pyproject.toml"
TOOL = "tool"
SETUPTOOLS_GIT_DETAILS = "setuptools-git-details"
SETUPTOOLS_GIT_DETAILS_SNAKE_CASED = "setuptools_git_details"
ENABLED = "enabled"
WRITE_TO = "write_to"


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


def _read_pyproject_toml(name: str | os.PathLike[str]) -> Dict[str, Any]:
    path = Path(name)
    data = path.read_text(encoding="utf-8")
    return load_toml(data)


@dataclass(frozen=True)
class Configuration:
    """setuptools-git-details configuration"""

    write_to: Path
    enabled: bool = True

    @classmethod
    def from_pyproject_toml(
        cls,
        name: str | os.PathLike[str] = PYPROJECT_TOML,
    ) -> Configuration:
        """
        Read Configuration from pyproject.toml.
        """
        pyproject_data = _read_pyproject_toml(name)
        config = cls._validate_pyproject_toml(pyproject_data)
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> Configuration:
        if WRITE_TO not in config:
            raise ValueError(
                f"Invalid tool.{SETUPTOOLS_GIT_DETAILS} section: {WRITE_TO} key-value pair is missing"
            )
        cls.validate_filepath(config[WRITE_TO])
        config[WRITE_TO] = Path(config[WRITE_TO])
        return cls(**config)

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
        return config

    @classmethod
    def validate_filepath(cls, value: Any | str | os.PathLike[str]) -> None:
        filepath = Path(value)
        if filepath.exists():
            logger.warning("%s will be overridden.", filepath.as_posix())
        dir = filepath.parent
        if not dir.exists():
            raise SetupError(
                f"{SETUPTOOLS_GIT_DETAILS}: {dir.as_posix()} does NOT exist."
            )
        if not dir.is_dir():
            raise SetupError(
                f"{SETUPTOOLS_GIT_DETAILS}: {dir.as_posix()} is NOT a directory."
            )


def setup_keywords(
    dist: Distribution,
    attr: str,
    value: Any,
    pyproject_toml: str | os.PathLike[str] = PYPROJECT_TOML,
) -> None:
    logger.debug("▶️ Start: %s=%s ; %r", attr, value, vars(dist.metadata))
    config = _load_configuration(dist, pyproject_toml)
    if config:
        logger.debug(f"👍 {SETUPTOOLS_GIT_DETAILS} has a valid configuration.")
    else:
        logger.debug(f"⏹️ {SETUPTOOLS_GIT_DETAILS} not configured.")


def finalize_distribution_options(
    dist: Distribution, pyproject_toml: str | os.PathLike[str] = PYPROJECT_TOML
) -> None:
    logger.debug(
        "▶️ Start: %s/%s/%s: %r",
        dist.metadata.name,
        id(dist),
        id(dist.metadata),
        vars(dist.metadata),
    )
    config = _load_configuration(dist, pyproject_toml)
    if not config:
        logger.debug(
            f"⏹️ {SETUPTOOLS_GIT_DETAILS} not configured. Nothing to do. Bye! 👋😊"
        )
        return
    if not config.enabled:
        logger.debug(f"⏩ {SETUPTOOLS_GIT_DETAILS} disabled. Nothing to do. Bye! 👋😊")
        return
    # Extract git details:
    if not shutil.which("git"):
        raise PlatformError(
            f"{SETUPTOOLS_GIT_DETAILS}: git is either not installed or not in PATH."
        )
    if not git.is_in_git_project():
        logger.debug(
            "⏹️ Not in a git project and no git details in distribution metadata. Nothing to do. Bye! 👋😊"
        )
        return
    git_details = git.get_all_details()
    # Write git details to file:
    logger.debug(f"Write git details to file: {config.write_to.as_posix()}")
    content = TEMPLATE.substitute(**git_details)
    config.write_to.write_text(content)
    logger.debug(
        "✅ Finished: %s/%s/%s: %r",
        dist.metadata.name,
        id(dist),
        id(dist.metadata),
        vars(dist.metadata),
    )


def _load_configuration(
    dist: Distribution, pyproject_toml: str | os.PathLike[str]
) -> Configuration:
    """Load configuration from either setup.py or pyproject.toml."""
    dist_config = getattr(dist, SETUPTOOLS_GIT_DETAILS_SNAKE_CASED, None)
    toml_config = _read_pyproject_toml(pyproject_toml)
    if dist_config is None and toml_config is None:
        return None
    if dist_config is not None and toml_config is not None:
        raise DistutilsSetupError(
            f"Both setup.py and pyproject.toml configure {SETUPTOOLS_GIT_DETAILS}. Please remove one of them."
        )
    if dist_config is None:
        logger.debug(f"Loading configuration from {PYPROJECT_TOML}")
        return Configuration.from_pyproject_toml(pyproject_toml)
    if not isinstance(dist_config, dict):
        raise DistutilsOptionError(
            f"Incorrect config format. Expected a dictionary, got: {dist_config}"
        )
    logger.debug("Loading configuration from setup.py arguments")
    return Configuration.from_dict(dist_config)


def main() -> None:
    try:
        from setuptools_git_details._git import __git__
    except ImportError:
        __git__ = {}
    print(SETUPTOOLS_GIT_DETAILS)
    for k, v in __git__.items():
        print(f"- {k}: {v or "N/A"}")


if __name__ == "__main__":
    main()
