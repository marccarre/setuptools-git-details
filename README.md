# setuptools-git-details

A `setuptools` package to add details from git to your project.

## Features

- Generates a file containing:
  - the name of the project,
  - the current revision,
  - the current branch,
  - the current tag, if any,
  - the `https://` URL to this project,
  - the `git@` URL to this project,
  - whether the current revision/branch/tag is "dirty".
  This file can then be used at will.
- Can be installed & configured through both `setup.py` and [PEP 518][pep518]'s
  `pyproject.toml`.
- Does not require to change source code of the project.

## Usage

### 1. Configure `pyproject.toml`

```toml
[tool.setuptools-git-details]
write_to = "myproject/_git.py"
enabled = true  # Optional. Default: true.
```

### 2. Let `setuptools-git-details` generate the git details Python file

The next time you run `setuptools` (e.g., via `pip install -e $(pwd)`),
`setuptools-git-details` will then generate a file like the following at the
location defined via `write_to` (e.g., in this case `myproject/_git.py`):

```python
# This file was generated by setuptools-git-details.
# Do NOT change. Do NOT track in version control.
# Generated at: 2024-09-29T05:18:09.101566+00:00

from typing import Dict, Union

git: Dict[str, Union[str, bool]] = {
    "name": "myproject",
    "revision": "738484d4c18cb04c7f9095c2ec834fea4872f184",
    "branch": "main",
    "tag": "",
    "url": "https://github.com/myorg/myproject",
    "git": "git@github.com:myorg/myproject.git",
    "is_dirty": False,
}
__git__ = git
```

### 3. Use the generated file in your Python code

```python
try:
    from myproject._git import git
except ImportError:
    git = {}

print(git.get("revision", "N/A"))
```

Examples:

- In a CLI, print these details as part of `--help` or `--version`.
- In an ETL, use these details as metadata for your data lineage.
- etc.

## Development

### Setup

Install [`just`](https://github.com/casey/just?tab=readme-ov-file#installation)
and then run the below command:

```console
just setup
```

### Lint

```console
just lint
```

### Install

```console
just install
```

### Clean

```console
just clean
```

## Release

### Test-release to [test.pypi.org][testpypi]

- Add [test.pypi.org][testpypi]'s API token to `~/.pypirc`.
- Update the version in `pyproject.toml`.
- Create a tag with the same version:

  ```console
  export VERSION="X.Y.Z"  # N.B.: no "v" prefix!
  git tag -a "${VERSION}" -m "${VERSION}"
  git push origin tag "${VERSION}"
  ```

- Run:

  ```console
  just test-release
  ```

- Test the release:

  ```console
  python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps setuptools-git-details
  ```

N.B.: in case of release failure, and a re-release, the tag can be deleted this
way (warning: bad practice to delete tags):

```console
git tag -d "${VERSION}"
git push origin --delete "${VERSION}"
```

### Release to [pypi.org][pypi]

- Add [pypi.org][pypi]'s API token to `~/.pypirc`.
- Run:

  ```console
  just release
  ```

- Test the release:

  ```console
  python3 -m pip install setuptools-git-details
  ```

[pep518]: https://www.python.org/dev/peps/pep-0518
[pypi]: https://pypi.org/
[testpypi]: https://test.pypi.org/
