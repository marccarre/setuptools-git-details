import subprocess
from typing import Dict, List, Union


def get_all_details() -> Dict[str, Union[str, bool]]:
    return {
        "name": get_repository_name(),
        "revision": get_commit_hash(),
        "branch": get_branch(),
        "tag": get_tag(),
        "url": get_repository_url(as_https_url=True),
        "git": get_repository_url(as_https_url=False),
        "is_dirty": has_uncommitted_changes(),
    }


def is_in_git_project() -> bool:
    cmd = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        universal_newlines=True,
        capture_output=True,
    )
    return cmd.returncode == 0 and cmd.stdout.strip() == "true"


def get_repository_name() -> str:
    """Get the name of the current Git repository, according to its origin.

    Returns:
        Name of the current Git repository.
    """
    url = get_repository_url()
    name = url.split("/")[-1]
    return _remove_suffix(name, ".git")


def get_repository_url(as_https_url: bool = False) -> str:
    """Get the URL of the current Git repository.

    Args:
        as_https_url: if true, returns a "https://" URL, if false (default), returns a "git@" URL.

    Returns:
        URL of the current Git repository.
    """
    url = _run(["git", "config", "--get", "remote.origin.url"])
    return _as_https_url(url) if as_https_url else url


def _as_https_url(git_url: str) -> str:
    git_url = git_url.replace(":", "/").replace("git@", "https://")
    return _remove_suffix(git_url, ".git")


def _remove_suffix(text: str, suffix: str) -> str:
    return text[: -len(suffix)] if len(suffix) != 0 and text.endswith(suffix) else text


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes, i.e., whether the current branch
    is "dirty".

    Returns:
        True if "dirty". False otherwise.
    """
    cmd = subprocess.run(["git", "diff", "--exit-code", "--quiet", "HEAD"])
    return cmd.returncode != 0


def get_commit_hash() -> str:
    """Get the hash (a.k.a. SHA) of the most recent Git commit.

    If there are uncommitted changes, "-dirty" is appended to the hash of the
    Git commit.

    Returns:
        Hash of the most recent Git commit.
    """
    hash = _run(["git", "rev-parse", "HEAD"])
    return f"{hash}-dirty" if has_uncommitted_changes() else hash


def get_branch() -> str:
    """Get the active branch of the current Git repository.

    If there are uncommitted changes, "-dirty" is appended to the branch name.

    Returns:
        Branch of the current Git repository.
    """
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return f"{branch}-dirty" if has_uncommitted_changes() else branch


def get_tag() -> str:
    """Get the tag of the most recent Git commit, if any.

    If no tag exists, an empty string is returned.
    If there are uncommitted changes, "-dirty" is appended to the tag.

    Returns:
        Tag of the most recent Git commit, if any."""
    cmd = subprocess.run(
        ["git", "describe", "--exact-match", "HEAD"],
        capture_output=True,
        universal_newlines=True,
    )
    if cmd.returncode != 0:
        return ""  # No tag. Return an empty string.
    tag = cmd.stdout.strip()
    return f"{tag}-dirty" if tag and has_uncommitted_changes() else tag


def _run(cmd: List[str], stderr: int = subprocess.STDOUT) -> str:
    return subprocess.check_output(cmd, universal_newlines=True, stderr=stderr).strip()
