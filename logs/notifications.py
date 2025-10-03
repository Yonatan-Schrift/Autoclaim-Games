"""
@file       logs/notifications.py
@module     logs.notifications
@brief      this file contains functions for sending notifications via various services (e.g., Discord, email, Telegram).
@author     Yonatan-Schrift
"""

import discord_webhook
# import smtplib


def send_discord_notification(webhook_url: str, message: str) -> bool:
    """
    Sends a notification message to a Discord channel via webhook.

    Args:
        webhook_url (str): The Discord webhook URL.
        message (str): The message to send.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """

    webhook = discord_webhook.DiscordWebhook(url=webhook_url, content=message)
    response = webhook.execute()
    return response.status_code == 200
