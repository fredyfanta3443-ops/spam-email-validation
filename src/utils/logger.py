import logging
from pathlib import Path
from datetime import datetime

# Shared across all get_logger() calls so every module in a single run
# writes to the same log file instead of each creating its own.
_LOG_FILE = None


def get_logger(name: str) -> logging.Logger:
    global _LOG_FILE

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    if _LOG_FILE is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir = Path("logs") / datetime.now().strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)
        _LOG_FILE = log_dir / f"{timestamp}.log"

    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s]: %(filename)s - Line %(lineno)d: %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    logger.addHandler(handler)
    logger.propagate = False
    return logger
