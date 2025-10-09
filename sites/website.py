"""
@file       sites/website.py
@module     sites.website
@brief      Interface module for adding more websites in the future.
@author     Yonatan-Schrift
"""

from abc import ABC, abstractmethod
from playwright.sync_api import Page
import logging


class Website(ABC):
    """
    Abstract base class for all website automation implementations.
    Defines the interface every website must implement.
    """

    BASE_URL: str
    logger: logging.Logger

    # ─────────────────────────────────────────────
    # Abstract methods (must be implemented)
    # ─────────────────────────────────────────────

    @staticmethod
    @abstractmethod
    def sign_in(email: str, password: str, page: Page):
        """
        Perform sign-in flow for the website.
        """
        pass

    @staticmethod
    @abstractmethod
    def claim_game(page: Page, selector: str, game_name: str):
        """
        Claim a single available game or offer.
        """
        pass

    @staticmethod
    @abstractmethod
    def run(email: str, password: str, headless: bool = False) -> int:
        """
        Run the full automation flow for the site.
        Returns an exit code (0 = success, non-zero = error).
        """
        pass
