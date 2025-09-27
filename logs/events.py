"""
@file:   logs/events.py
@module: logs.events
@brief:  This file contains functions for logging specific events (like persistent logs).
@author: Yonatan-Schrift
"""

import logging

PERSISTENT = 60 # Custom log level for persistent logs
logging.addLevelName(PERSISTENT, 'PERSISTENT')

def persistent(self, message, *args, **kws) -> None:
    if self.isEnabledFor(PERSISTENT):
        self._log(PERSISTENT, message, args, **kws)

logging.Logger.PERSISTENT = persistent

def log_persistent(logger: logging.Logger, message: str) -> None:
    """
    Logs a message at the PERSISTENT level.
    Args:
        logger: the logger to use
        message: the message to log

    """
    logger.log(PERSISTENT, message)