setup:
    bin/setup

lint:
    pre-commit run --all-files

test:
    uv run pytest \
        --cov-report xml:.coverage.xml \
        --cov-report html:.coverage_html \
        --cov setuptools_git_details

install:
    uv run pip uninstall -y setuptools_git_details ; uv run pip install -e $(pwd)

setup-release:
    python3 -m pip install --upgrade build
    python3 -m build
    python3 -m pip install --upgrade twine

test-release: setup-release
    python3 -m twine upload --repository testpypi dist/*

release: setup-release
    python3 -m twine upload dist/*

clean:
    rm -fr \
        .coverage* \
        .mypy_cache \
        .pytest_cache \
        .venv \
        *.egg-info \
        *.log \
        dist \
        logs
    find . -type f -name _git.py -exec rm {} \+
    find . -type d -name __pycache__ -exec rm -r {} \+
