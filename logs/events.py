"""
@file:   logs/events.py
@module: logs.events
@brief:  This file contains functions for logging specific events (like persistent logs).
@author: Yonatan-Schrift
"""

import logging
from os import getenv

from core.utils import env_to_bool
from logs.notifications import send_discord_notification

PERSISTENT = 60  # Custom log level for persistent logs
logging.addLevelName(PERSISTENT, 'PERSISTENT')


def persistent(self, message, *args, **kws) -> None:
    if self.isEnabledFor(PERSISTENT):
        self._log(PERSISTENT, message, args, **kws)


logging.Logger.PERSISTENT = persistent


def log_persistent(logger: logging.Logger, message: str) -> None:
    """
    Logs a message at the PERSISTENT level.
    also optionally sends a notification via multiple services.
    Args:
        logger: the logger to use
        message: the message to log

    """
    logger.log(PERSISTENT, message)

    # send notifications
    if env_to_bool("NOTIFY_ON_DISCORD") and getenv("DISCORD_WEBHOOK_URL"):
        try:
            notify_everyone = env_to_bool("DISCORD_NOTIFY_EVERYONE")

            mention = " @everyone" if notify_everyone else ""
            success = send_discord_notification(
                getenv("DISCORD_WEBHOOK_URL"),
                f"{message}\n\n*This is an automated message.*{mention}"
            )
            if not success:
                logger.warning(f"Discord notification failed for: {message}")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            logger.warning(f"Event not notified to Discord: {message}")
