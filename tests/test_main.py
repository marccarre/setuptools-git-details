import re
from pathlib import Path
from unittest.mock import Mock

import pytest
from setuptools.dist import Distribution

from setuptools_git_details.main import (
    Configuration,
    finalize_distribution_options,
)


def test_config() -> None:
    project_toml_path = Path(__file__).parent / "sample_pyproject.toml"
    config = Configuration.from_pyproject_toml(project_toml_path)
    assert config == Configuration(write_to=Path("tests/_git.py"))


def test_invalid_config_no_tool_section() -> None:
    project_toml_path = Path(__file__).parent / "invalid_pyproject_no_tool_section.toml"
    with pytest.raises(ValueError, match="Invalid pyproject.toml: no tool section"):
        Configuration.from_pyproject_toml(project_toml_path)


def test_invalid_config_no_tool_sgd_section() -> None:
    project_toml_path = (
        Path(__file__).parent / "invalid_pyproject_no_tool_sgd_section.toml"
    )
    with pytest.raises(
        ValueError,
        match="Invalid pyproject.toml: no tool.setuptools-git-details section",
    ):
        Configuration.from_pyproject_toml(project_toml_path)


def test_invalid_config_no_write_to_field() -> None:
    project_toml_path = (
        Path(__file__).parent / "invalid_pyproject_no_write_to_field.toml"
    )
    with pytest.raises(
        ValueError,
        match="Invalid tool.setuptools-git-details section: write_to key-value pair is missing",
    ):
        Configuration.from_pyproject_toml(project_toml_path)


def test_finalize_distribution_options() -> None:
    # Clean-up before the test:
    generated_file = Path("tests/_git.py")
    generated_file.unlink(missing_ok=True)
    mock_dist = _create_mock_distribution()
    # Given:
    project_toml_path = Path(__file__).parent / "sample_pyproject.toml"
    # When:
    finalize_distribution_options(mock_dist, project_toml_path)
    # Then:
    lines = generated_file.read_text().splitlines()
    assert len(lines) == 16
    assert lines[0] == "# This file was generated by setuptools-git-details."
    assert lines[1] == "# Do NOT change. Do NOT track in version control."
    assert re.match(
        r"^# Generated at: \d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}\+00:00$",
        lines[2],
    )
    assert lines[3] == ""
    assert lines[4] == "from typing import Dict, Union"
    assert lines[5] == ""
    assert lines[6] == "git: Dict[str, Union[str, bool]] = {"
    assert lines[7] == '    "name": "setuptools-git-details",'
    assert re.match(r'^    "revision": "[a-fA-F0-9]{40}(?:-dirty)?",$', lines[8])
    assert re.match(r'^    "branch": "(?:.*?)",$', lines[9])
    assert re.match(r'^    "tag": "(?:.*?)",$', lines[10])
    assert (
        lines[11] == '    "url": "https://github.com/marccarre/setuptools-git-details",'
    )
    assert (
        lines[12] == '    "git": "git@github.com:marccarre/setuptools-git-details.git",'
    )
    assert re.match(r'^    "is_dirty": (?:True|False),$', lines[13])
    assert lines[14] == "}"
    assert lines[15] == "__git__ = git"


def test_finalize_distribution_options_disabled() -> None:
    # Clean-up before the test:
    generated_file = Path("tests/_git.py")
    generated_file.unlink(missing_ok=True)
    mock_dist = _create_mock_distribution()
    # Given a pyproject.toml file with enabled=false:
    project_toml_path = Path(__file__).parent / "sample_pyproject_disabled.toml"
    # When:
    finalize_distribution_options(mock_dist, project_toml_path)
    # Then no file is generated:
    assert not generated_file.exists()


def _create_mock_distribution(name: str = "test") -> Distribution:
    mock_dist = Mock(Distribution)
    mock_dist.setuptools_git_details = None
    mock_dist.metadata = Mock()
    mock_dist.metadata.name = name
    return mock_dist
