"""Core Logging Configuration"""

import logging
import logging.handlers
from pathlib import Path
from khops.core.config import settings

# Create logs directory if it doesn't exist
Path(settings.LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)


def setup_logging():
    """Configure logging for the application"""

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # File handler
    if settings.LOG_TO_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE_PATH,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)

    return root_logger


# Setup on import
logger = setup_logging()
