from __future__ import annotations

import logging
from typing import Final


class _MinimalPrettyFormatter(logging.Formatter):
    _RESET: Final[str] = "\x1b[0m"
    _GREY: Final[str] = "\x1b[90m"
    _BLUE: Final[str] = "\x1b[94m"
    _GREEN: Final[str] = "\x1b[92m"
    _YELLOW: Final[str] = "\x1b[93m"
    _RED: Final[str] = "\x1b[91m"
    _BOLD_RED: Final[str] = "\x1b[1;91m"

    _LEVEL_STYLES: Final[dict[int, tuple[str, str]]] = {
        logging.DEBUG: ("DBG", _BLUE),
        logging.INFO: ("INF", _GREEN),
        logging.WARNING: ("WRN", _YELLOW),
        logging.ERROR: ("ERR", _RED),
        logging.CRITICAL: ("CRT", _BOLD_RED),
    }

    def format(self, record: logging.LogRecord) -> str:
        level_short, level_color = self._LEVEL_STYLES.get(
            record.levelno, ("LOG", self._GREY)
        )
        timestamp = self.formatTime(record, datefmt="%H:%M:%S")
        message = record.getMessage()
        return (
            f"{self._GREY}[{timestamp}]{self._RESET} "
            f"{level_color}{level_short}{self._RESET} "
            f"{message}"
        )


def get_logger(name: str = "anticloudflarewaf", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_MinimalPrettyFormatter())
        logger.addHandler(handler)

    return logger

