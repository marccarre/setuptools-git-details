import logging
import os
from typing import Mapping, Optional


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addHandler(get_console_handler())
    if os.environ.get("SETUPTOOLS_GIT_DETAILS_LOG_TO_FILE"):
        logger.addHandler(get_file_handler())
    logger.setLevel(get_log_level())
    return logger


def get_log_level(env: Mapping[str, str] = os.environ) -> int:
    value: Optional[str] = env.get("SETUPTOOLS_GIT_DETAILS_DEBUG")
    return logging.INFO if value is None else logging.DEBUG


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
