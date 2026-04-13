"""
@file:   logs/logger.py
@module: logs.logger
@brief:  This file contains functions for setting up and managing a logger.
@author: Yonatan-Schrift
"""

import logging
import os
import json
import fcntl

from logging.handlers import RotatingFileHandler
from logs.events import PERSISTENT

# Ensure logs directory exists (currently always exists as this file is in /logs)
LOG_DIR = os.path.join("logs")
os.makedirs(LOG_DIR, exist_ok=True)


def _update_counter(counter_file: str) -> int:
    """
    Atomically update the counter file using file locking.
    
    Args:
        counter_file: Path to the counter JSON file.
        
    Returns:
        The new count value after incrementing.
    """
    # Create file if it doesn't exist
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            json.dump({"count": 1}, f)
        return 1
    
    with open(counter_file, 'a+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.seek(0)
            content = f.read()
            count = json.loads(content).get("count", 0) if content else 0
            count += 1
            if count >= 7:
                f.seek(0)
                f.truncate()
                count = 0
            else:
                f.seek(0)
                f.truncate()
                json.dump({"count": count}, f)
            return count
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes to both console and a log file.
    Clears the log file every couple of runs (the number is stored in the config) to avoid excessive size.

    Args:
        name (str): Name of the logger (usually __name__ of the module)

    Returns:
        logging.Logger: Configured logger instance
    """
    log_name = name.removeprefix("sites.")
    log_file = os.path.join(LOG_DIR, f"{log_name}.log")
    persistent_log_file = os.path.join(LOG_DIR, f"{log_name}_claimed.log")
    counter_file = os.path.join(LOG_DIR, f"{log_name}_counter.json")

    clear_log_day = os.getenv("KEEP_LOG_FOR")  # days after which to clear the log file

    # --- Atomically update the counter file ---
    count = _update_counter(counter_file)

    if count == 0:
        # Clear the main log file (not the persistent one) when counter resets
        open(log_file, "w").close()

    # --- Create logger ---
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    # --- Console handler ---
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # --- Main file handler ---
    file_handler = logging.FileHandler(log_file, mode='a', encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # --- Persistent file handler ---
    persistent_handler = logging.FileHandler(persistent_log_file, encoding="utf-8")
    persistent_handler.setLevel(PERSISTENT)  # only log persistent level logs
    persistent_handler.setFormatter(logging.Formatter(
        "%(asctime)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    ))

    # --- Add handlers ---
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(persistent_handler)

    logger.debug(f"Logger '{log_name}' initialized, logging to console and '{log_file}'")
    return logger


def stop_logger(logger: logging.Logger):
    """
    Cleanly stop a logger by closing and removing all its handlers.

    Args:
        logger (logging.Logger): The logger instance to stop.
    """
    # Copy handlers so we can modify the logger safely

    logger.info(f"Stopping logger\n")
    for handler in logger.handlers[:]:
        try:
            handler.flush()  # make sure buffered logs are written
            handler.close()  # close file/stream
        except Exception as e:
            # Optional: fallback in case a handler misbehaves
            print(f"Warning: failed to close handler {handler}: {e}")
        finally:
            logger.removeHandler(handler)
