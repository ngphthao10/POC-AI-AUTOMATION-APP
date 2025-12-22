"""Enhanced logging utility with file and console output"""
import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str,
    level=logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs",
    console_format: str = '%(levelname)s - %(message)s',
    file_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
):
    """
    Setup an enhanced logger with both console and file output.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
        console_format: Format for console output
        file_format: Format for file output

    Returns:
        Configured logger instance

    Usage:
        logger = setup_logger(__name__, level=logging.DEBUG)
        logger.info("This goes to console and file")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if enabled)
    if log_to_file:
        try:
            # Create logs directory if it doesn't exist
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)

            # Create log filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d')
            log_filename = f"{name.replace('.', '_')}_{timestamp}.log"
            log_file = log_path / log_filename

            # File handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            logger.debug(f"Logging to file: {log_file}")

        except Exception as e:
            logger.warning(f"Failed to setup file logging: {e}")

    return logger


def setup_automation_logger(
    automation_name: str,
    execution_id: str = None,
    level=logging.DEBUG
):
    """
    Setup logger specifically for automation runs with execution tracking.

    Args:
        automation_name: Name of the automation (e.g., 'csp_admin')
        execution_id: Unique execution ID
        level: Logging level

    Returns:
        Configured logger with execution-specific log file

    Usage:
        logger = setup_automation_logger('csp_admin', execution_id='run_123')
    """
    if not execution_id:
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    log_dir = f"logs/{automation_name}"
    logger_name = f"{automation_name}.{execution_id}"

    logger = setup_logger(
        name=logger_name,
        level=level,
        log_to_file=True,
        log_dir=log_dir,
        console_format='%(asctime)s - %(levelname)s - %(message)s',
        file_format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    logger.info(f"=" * 60)
    logger.info(f"Starting automation: {automation_name}")
    logger.info(f"Execution ID: {execution_id}")
    logger.info(f"Log file: logs/{automation_name}/{logger_name}_*.log")
    logger.info(f"=" * 60)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a default one.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        return setup_logger(name)

    return logger
