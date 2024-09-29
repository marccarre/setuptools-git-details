import re
import subprocess
import uuid

import pytest

from setuptools_git_details.git import (
    get_all_details,
    get_tag,
    has_uncommitted_changes,
    is_in_git_project,
)


def test_get_all_details() -> None:
    git_details = get_all_details()
    assert len(git_details) == 7
    assert git_details["name"] == "setuptools-git-details"
    assert git_details["url"] == "https///github.com/marccarre/setuptools-git-details"
    assert git_details["git"] == "git@github.com:marccarre/setuptools-git-details.git"
    assert "branch" in git_details
    assert "tag" in git_details
    assert re.match(r"^[a-fA-F0-9]{40}(-dirty)?$", str(git_details["revision"]))
    assert git_details["is_dirty"] in (True, False)


def test_get_tag_without_a_tag_should_return_empty_string() -> None:
    if _has_tag():
        pytest.skip("Do NOT run if there is already a git tag.")
        return
    assert get_tag() == ""


def test_get_tag_with_a_tag() -> None:
    if _has_tag():
        pytest.skip("Do NOT run if there is already a git tag.")
        return
    # Create a temporary tag and extract it using get_tag:
    expected_tag = f"test_get_tag_{uuid.uuid1()}"
    try:
        # Given:
        cmd = subprocess.run(["git", "tag", "-a", expected_tag, "-m", expected_tag])
        assert cmd.returncode == 0
        # When:
        tag = get_tag()
        # Then:
        if has_uncommitted_changes():
            assert tag == f"{expected_tag}-dirty"
        else:
            assert tag == expected_tag
    finally:
        cmd = subprocess.run(["git", "tag", "-d", expected_tag])
        assert cmd.returncode == 0


def _has_tag() -> bool:
    return subprocess.run(["git", "describe", "--exact-match", "HEAD"]).returncode == 0


def test_is_in_git_project() -> None:
    assert is_in_git_project()
