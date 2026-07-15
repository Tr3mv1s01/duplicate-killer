import logging
import os
from logging.handlers import RotatingFileHandler

from src.utils.constants import LOG_FILE


_LOG_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~/.config"))
    if os.name == "nt"
    else os.path.expanduser("~/.config"),
    "DuplicateKiller",
    "logs",
)


def setup_logger(name: str = "duplicate_killer") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    os.makedirs(_LOG_DIR, exist_ok=True)
    log_path = os.path.join(_LOG_DIR, LOG_FILE)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
