"""
@file:   sites/epic_games.py
@module: sites.epic_games
@brief:  This file contains functions specific to claiming games from the epic-games website.
@author: Yonatan-Schrift
"""
import os # for os.getlogin()

from core.anti_bot import random_sleep, user_click, scroll_down
from core.setup import setup_and_open
from core.utils import click_locator, safe_find, wait_for_user_input, safe_fill, DEFAULT_TIMEOUT_MS
from core.exceptions import *
from logs.events import log_persistent
from logs.logger import get_logger, stop_logger

from playwright.sync_api import Page, TimeoutError as PWTimeoutError

from sites.website import Website


# Setup logger

class EpicGames(Website):
    BASE_URL = 'https://store.epicgames.com/en-US/free-games'
    logger = get_logger(__name__)

    @staticmethod
    def run(eg_mail: str, eg_pass: str, headless: bool = False) -> int:
        """
        Main function to claim free games from Epic Games Store.

        Args:
            eg_mail (str): epic-games account email
            eg_pass (str): epic-games account password
            headless (bool): config to run browser in headless mode

        Returns:
            1 on failure, 0 on success
        """
        EpicGames.logger.info("Running epic_games...")
        # Constants
        url_claim = 'https://store.epicgames.com/en-US/free-games'
        status = 0  # default return value to success

        if not eg_mail or not eg_pass:
            EpicGames.logger.critical("-!- ERROR: Epic Games credentials not provided -!-")
            return 1

        # setup playwright
        p, browser, page = setup_and_open(url_claim, is_epic=True, headless=headless)
        try:
            # Checks if the user is already signed in
            EpicGames.logger.info("Checking if already signed in...")
            locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=5000)
            if not locator:
                try:
                    EpicGames.sign_in(eg_mail, eg_pass, page)  # sign in
                except ProjectError as e:
                    EpicGames.logger.critical(f"-!- ERROR: {e} -!-")  # log error
                    status = 1  # set return value to error

            username = safe_find(page, "[aria-label='Account menu']", timeout_ms=3000).get_attribute("title")
            EpicGames.logger.info(f"Signed in as {username}")

            # Locate all free games on the page
            free_games = page.locator("[aria-label*='Free Games'][aria-label*='Free Now'], "
                                      "[data-component='VaultOfferCard']").all() # a fix for Christmas 2025
            if not free_games:
                log_persistent(EpicGames.logger,
                    "No free games found, unusual behavior, please check for updates to the script or any "
                    "geo-restrictions."
                )
                return status

            # Claim each free game
            for i, item in enumerate(free_games, start=1):
                item.scroll_into_view_if_needed()
                random_sleep()

                try:
                    game_name = EpicGames.clean_text(item.inner_text())
                    href = item.get_attribute('href')

                    # A fix for when href is not directly on the item
                    if not href:
                        anchor = item.locator("a")
                        if not anchor:
                            raise EpicGamesGameNotFoundError("Could not find game link")
                        href = anchor.get_attribute('href')
                    if(href == "/en-US/free-games"):
                        # skip empty free games cards (Especially during holiday events)
                        EpicGames.logger.warning(f"-!- Skipping empty free game card -!-")
                        continue
                    link = f"https://store.epicgames.com{href}"
                except Exception as e:
                    EpicGames.logger.warning(f"-!- Skipping a game due to unexpected error: {e}")
                    status = 1
                    continue

                EpicGames.logger.info(f"[{i}] Trying to claim {game_name} from {link}...")
                try:
                    EpicGames.claim_game(page, link, game_name)
                except PWTimeoutError as e:
                    EpicGames.logger.error(f"-!- Failed to claim {game_name} due to timeout: {e} -!-")
                    status = 1
                except Exception as e:
                    EpicGames.logger.error(f"-!- Failed to claim {game_name} due to unexpected error: {e}-!-")
                    status = 1  # set return value to error if any game fails to be claimed

                random_sleep()
                page.goto(url_claim, wait_until="load", timeout=15000)

        finally:
            EpicGames.logger.debug("Closing browser and Playwright...")
            try:
                browser.close()
            finally:
                p.stop()
                EpicGames.logger.debug("Browser and Playwright closed.")

            # stops the logger
            stop_logger(EpicGames.logger)

        return status

    @staticmethod
    def sign_in(eg_mail: str, eg_pass: str, page: Page):
        EpicGames.logger.info("Signing in...")

        EpicGames.logger.debug("Clicking sign in button...")
        if not click_locator(page, "[aria-label='Sign in']"):
            raise LocatorNotFoundError("Sign in button missing, please check for updates to the script")

        # Checks once again for account, since sometimes the account is already signed in
        locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=DEFAULT_TIMEOUT_MS)
        if locator:
            EpicGames.logger.info("Already signed in!")
            return

        EpicGames.logger.debug("Entering Credentials...")
        safe_fill(page, "#email", eg_mail, "#continue")
        safe_fill(page, "#password", eg_pass, "#sign-in")

        EpicGames.logger.debug("Checking for 2FA...")
        locator = safe_find(page, "text=6-digit")
        if locator:
            EpicGames.logger.info("2FA found, waiting for user to enter code...")
            wait_for_user_input("-?- Enter the 6-digit code into the browser, press continue, then press Enter here...")
            click_locator(page, "#yes")

        # --- Verifying sign in was successful ---
        locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=3000)
        if not locator:
            raise InvalidCredentialsError("Could not sign in, please check your credentials and/or 2FA code")

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Extracts the game name from the Epic Games locator text.

        Expected format:
            FREE NOW
            <Game Name>
            Free Now - <date>

        Args:
            text (str): Raw locator text

        Returns:
            str: Extracted game name

        Raises:
            GameNameNotFoundError: If a game name cannot be extracted
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if len(lines) >= 2:
            return lines[1]  # game name is always the second non-empty line

        EpicGames.logger.error(
            "Game name could not be extracted\n"
            f"Could not find game name in \"{text}\". If the issue persists, please contact me via GitHub"
        )

        raise EpicGamesGameNotFoundError(
            f"Could not find game name in \"{text}\". If the issue persists, please contact me via GitHub"
        )

    @staticmethod
    def claim_game(page: Page, link: str, game_name: str):
        EpicGames.logger.info(f"Claiming game from {link}...")
        page.goto(link)
        # scroll smoothly down a little bit
        scroll_down(page, 200)

        # Check if game is already owned
        if safe_find(page, "text='In Library'", timeout_ms=2000):
            EpicGames.logger.info("Game already in library, skipping...")
            # print(f"--- Game already claimed ---")
            return

        # Accept EULA if it appears (only on first claim)
        if safe_find(page, "text='end user license agreement'", timeout_ms=2000):
            EpicGames.logger.warning("End User License Agreement detected, should be accepted automatically...")
            page.locator("button").filter(has_text="Accept").click()

        EpicGames.logger.debug("Clicking purchase button...")
        click_locator(page, "[data-testid*='purchase']")

        # Wait until the checkout iframe exists
        page.wait_for_selector("#webPurchaseContainer iframe", timeout=DEFAULT_TIMEOUT_MS)

        # Attach to the checkout iframe
        iframe = page.frame_locator("#webPurchaseContainer iframe")

        # Locate the Place Order button (only when not loading)
        button = iframe.locator(
            'button:has-text("Place Order"):not(:has(.payment-loading--loading))'
        )

        # Wait until button is visible and click
        EpicGames.logger.debug("Clicking Place Order button...")
        button.wait_for(state="visible", timeout=20_000)
        user_click(button)

        # captcha = page.frame_locator("#h_captcha_challenge_checkout_free_prod iframe")
        # if captcha:
        #     print(f"-!- CAPTCHA -!-")
        #     input("press Enter in the console to continue...")

        # Wait until the "Thanks for your order!" text appears
        if safe_find(page, "text=Thanks for your order!",timeout_ms=15_000):
            EpicGames.logger.info("Game successfully claimed!")
            log_persistent(EpicGames.logger, f"User {os.getlogin()} Successfully claimed {game_name} from {link}")
            return
