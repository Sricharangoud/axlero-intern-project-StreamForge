import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Configures production-grade logging for StreamForge.
    Ensures log formatters print timestamps, log levels, logger names, and messages.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Define a clean log message format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure stdout stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Root logger setup
    root_logger = logging.getLogger("streamforge")
    root_logger.setLevel(log_level)
    
    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(stream_handler)

    return root_logger


# Create default application logger instance
logger = setup_logging()
