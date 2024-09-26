import re

from setuptools_git_details.git import get_all_details


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
