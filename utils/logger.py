"""
utils/logger.py
---------------
Structured logging for AutoGen course projects.

Uses Python's built-in logging with optional rich formatting.
Writes to both console and a log file.

Usage:
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Starting agent pipeline")
    logger.error("API call failed: %s", error)
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Try to import rich for pretty console output; fall back to plain logging
try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def get_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Returns a configured logger for a module.

    Args:
        name: Logger name (use __name__ for module-level loggers)
        level: Log level string ("DEBUG", "INFO", "WARNING", "ERROR")
               Defaults to LOG_LEVEL env var or "INFO"
        log_file: Path to log file. Defaults to LOG_FILE env var or None.

    Example:
        logger = get_logger(__name__)
        logger.info("Agent pipeline started")
        logger.debug("Config: %s", llm_config)
    """
    # Determine log level
    level_str = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, level_str.upper(), logging.INFO)

    logger = logging.getLogger(name)

    # Don't add handlers if already configured
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # --- Console Handler ---
    if RICH_AVAILABLE:
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            markup=True,
        )
        console_handler.setLevel(log_level)
        fmt = "%(message)s"
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    console_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console_handler)

    # --- File Handler (optional) ---
    log_filepath = log_file or os.getenv("LOG_FILE")
    if log_filepath:
        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # File captures everything
        file_fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        file_handler.setFormatter(logging.Formatter(file_fmt))
        logger.addHandler(file_handler)

    return logger


# Module-level convenience logger for quick use
course_logger = get_logger("autogen_course")


def log_agent_message(agent_name: str, content: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Logs an agent message in a structured format.
    Useful for debugging multi-agent conversations.
    """
    log = logger or course_logger
    separator = "-" * 40
    log.debug("\n%s\n[%s]\n%s\n%s", separator, agent_name, separator, content[:500])
