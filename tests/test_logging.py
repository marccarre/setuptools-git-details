import logging

from setuptools_git_details.logging import get_log_level


def test_get_log_level() -> None:
    assert get_log_level({}) == logging.INFO
    assert get_log_level({"SETUPTOOLS_GIT_DETAILS_DEBUG": ""}) == logging.DEBUG
    assert get_log_level({"SETUPTOOLS_GIT_DETAILS_DEBUG": "1"}) == logging.DEBUG
    assert get_log_level({"SETUPTOOLS_GIT_DETAILS_DEBUG": "INFO"}) == logging.DEBUG
