import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Factory logger aman (tidak duplicate handler)
    stdout: INFO
    stderr: WARNING+
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    )
    stdout_handler.addFilter(lambda r: r.levelno <= logging.INFO)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    )

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    logger.propagate = False
    return logger