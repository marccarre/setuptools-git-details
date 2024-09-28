# setuptools-git-details

A setuptools package to add details from git to your project.

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

- Add API tokens to `~/.pypirc`.
- Update the version in `pyproject.toml`.
- Create a tag with the same version:

  ```console
  export VERSION="vX.Y.Z"
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

[testpypi]: https://test.pypi.org/
