"""
@file:   sites/prime_gaming.py
@module: sites.prime_gaming
@brief:  This file contains functions specific to claiming games from the prime gaming website.
@author: Yonatan-Schrift
"""

from core.anti_bot import random_sleep, user_click, scroll_down
from core.setup import setup_and_open
from core.utils import click_locator, safe_find, wait_for_user_input, safe_fill
from core.exceptions import *
from logs.events import log_persistent
from logs.logger import get_logger, stop_logger

from playwright.sync_api import Page, TimeoutError as PWTimeoutError

# init logger
logger = get_logger(__name__)

def prime_gaming(pg_mail: str, pg_pass: str, headless: bool = False) -> int:
    """
    Main function to claim free games from Prime Gaming Store.

    Args:
        pg_mail (str): prime-gaming account email
        pg_pass (str): prime-gaming account password
        headless (bool): config to run browser in headless mode

    Returns:
        1 on failure, 0 on success
    """
    logger.info("Running prime_gaming...")
    # Constants
    url_claim = 'https://gaming.amazon.com/home'
    status = 0  # default return value to success

    if not pg_mail or not pg_pass:
        logger.critical("-!- ERROR: Prime Gaming credentials not provided -!-")
        return 1

    # setup playwright
    p, browser, page = setup_and_open(url_claim, headless=headless)

    try:
        logger.info("Checking if already signed in...")
        locator = safe_find(page, "[title='Sign in']", timeout_ms=3000)
        if locator:
            try:
                sign_in(pg_mail, pg_pass, page)  # sign in
            except (ProjectError, Exception) as e:
                logger.critical(f"-!- ERROR: {e} -!-")  # log error
                status = 1  # set return value to error

    finally:
        logger.debug("Closing browser and Playwright...")
        try:
            browser.close()
        finally:
            p.stop()
            logger.debug("Browser and Playwright closed.")

        # stops the logger
        logger.info("Finished all tasks\n")
        stop_logger(logger)

    return status

# WIP:
def sign_in(pg_mail: str, pg_pass: str, page: Page):
    logger.info("Signing in...")

    logger.debug("Clicking sign in button...")
    if not click_locator(page, "[title='Sign in']"):
        raise LocatorNotFoundError("Sign in button missing, please check for updates to the script")

    # Checks once again for account, since sometimes the account is already signed in
    locator = safe_find(page, "[aria-label='User dropdown and more options']", timeout_ms=3000)
    if locator:
        logger.info("Already signed in!")
        return

    logger.debug("Entering Credentials...")

    safe_fill(page, "#ap_email", pg_mail, "#continue-announce")
    safe_fill(page, "#ap_password", pg_pass, "#sign-in")

    logger.debug("Checking for 2FA...")
    locator = safe_find(page, "text=6-digit")
    if locator:
        logger.info("2FA found, waiting for user to enter code...")
        wait_for_user_input("-?- Enter the 6-digit code into the browser, press continue, then press Enter here...")
        click_locator(page, "#yes")

    # --- Verifying sign in was successful ---
    locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=3000)
    if not locator:
        raise InvalidCredentialsError("Could not sign in, please check your credentials and/or 2FA code")
