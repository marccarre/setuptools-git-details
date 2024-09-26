setup:
    bin/setup

lint:
    pre-commit run --all-files

install:
    uv run pip uninstall -y setuptools_git_details ; uv run pip install -e $(pwd)

clean:
    rm -fr \
        .coverage* \
        .mypy_cache \
        .pytest_cache \
        .venv \
        *.egg-info
    find . -type d -name __pycache__ -exec rm -r {} \+
