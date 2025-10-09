"""
@file:   sites/prime_gaming.py
@module: sites.prime_gaming
@brief:  This file contains functions specific to claiming games from the prime gaming website.
@author: Yonatan-Schrift
"""

from core.anti_bot import random_sleep, scroll_down, user_click
from core.setup import setup_and_open
from core.utils import click_locator, safe_find, safe_fill
from core.exceptions import *
from logs.events import log_persistent
from logs.logger import get_logger, stop_logger

from playwright.sync_api import Page

from sites.website import Website


class PrimeGaming(Website):
    logger = get_logger(__name__)
    BASE_URL = "https://gaming.amazon.com/"

    @staticmethod
    def run(pg_mail: str, pg_pass: str, headless: bool = False) -> int:
        """
        Main function to claim free games from Prime Gaming Store.

        Args:
            pg_mail (str): prime-gaming account email
            pg_pass (str): prime-gaming account password
            headless (bool): config to run browser in headless mode

        Returns:
            1 on failure, 0 on success
        """
        PrimeGaming.logger.info("Running prime_gaming...")
        # Constants
        status = 0  # default return value to success

        if not pg_mail or not pg_pass:
            PrimeGaming.logger.critical("-!- ERROR: Prime Gaming credentials not provided -!-")
            return 1

        # setup playwright
        p, browser, page = setup_and_open(PrimeGaming.BASE_URL, headless=headless)

        try:
            PrimeGaming.logger.info("Checking if already signed in...")
            locator = safe_find(page, "[title='Sign in']", timeout_ms=1000)
            if locator:
                try:
                    PrimeGaming.sign_in(pg_mail, pg_pass, page)  # sign in
                except (ProjectError, Exception) as e:
                    PrimeGaming.logger.critical(f"-!- ERROR: {e} -!-")  # log error
                    status = 1  # set return value to error (code can maybe continue?)

            username = safe_find(page, "[data-a-target='user-dropdown-first-name-text']",
                                 timeout_ms=1000).get_attribute(
                "title")
            PrimeGaming.logger.info(f"Signed in as {username}")

            PrimeGaming.scroll_until_end(page)

            # move games to dict to remove duplicates
            unclaimed_games = PrimeGaming.get_unique_game_locators(page,
                                                                   ".offer-list__content__grid [data-a-target='FGWPOffer']",
                                                                   "aria-label")

            for i, (name, selector) in enumerate(unclaimed_games.items(), start=1):
                print(f"[{i}]: Claiming {name}")

                try:
                    PrimeGaming.claim_game(page, selector, name)
                except ProjectError as e:
                    PrimeGaming.logger.error(f"-!- ERROR: {e} -!-")  # log error
                    status = 1  # set return value to error, continue to the next game

                except Exception as e:
                    PrimeGaming.logger.critical(f"-!- ERROR: {e} -!-")  # log error
                    return 1  # return error, unknown exception

                random_sleep()
                page.goto(PrimeGaming.BASE_URL, wait_until="load", timeout=15000)
                PrimeGaming.scroll_until_end(page)

            PrimeGaming.logger.info(f"Claimed {len(unclaimed_games)} games")


        finally:
            PrimeGaming.logger.debug("Closing browser and Playwright...")
            try:
                browser.close()
            finally:
                p.stop()
                PrimeGaming.logger.debug("Browser and Playwright closed.")

            # stops the logger
            stop_logger(PrimeGaming.logger)

        return status

    @staticmethod
    def sign_in(pg_mail: str, pg_pass: str, page: Page):
        PrimeGaming.logger.info("Signing in...")

        PrimeGaming.logger.debug("Clicking sign in button...")
        if not click_locator(page, "[title='Sign in']"):
            raise LocatorNotFoundError("Sign in button missing, please check for updates to the script")

        # Checks once again for account, since sometimes the account is already signed in
        locator = safe_find(page, "[aria-label='User dropdown and more options']", timeout_ms=3000)
        if locator:
            PrimeGaming.logger.info("Already signed in!")
            return

        PrimeGaming.logger.debug("Entering Credentials...")

        safe_fill(page, "#ap_email", pg_mail, "#continue-announce")
        safe_fill(page, "#ap_password", pg_pass, "#signInSubmit")

        # I have no clue if 2fa is even used here, leaving this commented out for now

        # logger.debug("Checking for 2FA...")
        # locator = safe_find(page, "text=6-digit", timeout_ms=3000)
        # if locator:
        #     logger.info("2FA found, waiting for user to enter code...")
        #     wait_for_user_input("-?- Enter the 6-digit code into the browser, press continue, then press Enter here...")
        #     click_locator(page, "#yes")

        # --- Verifying sign in was successful ---
        locator = safe_find(page, "[data-a-target='user-dropdown-first-name-text']", timeout_ms=3000)
        if not locator:
            raise InvalidCredentialsError("Could not sign in, please check your credentials and/or 2FA code")

    @staticmethod
    def claim_game(page: Page, selector: str, game_name: str) -> bool:
        PrimeGaming.logger.info("Claiming game...")

        loc = safe_find(page, selector, is_hidden=True)
        if not loc:
            raise LocatorNotFoundError(f"Could not find game locator for {game_name}")
        user_click(loc)

        page.wait_for_load_state("networkidle")

        if page.url == PrimeGaming.BASE_URL:
            # claimed an amazon game, no extra steps needed
            PrimeGaming.logger.info("Game claimed successfully!")
            log_persistent(PrimeGaming.logger, f"Successfully claimed {game_name}")
            return True

        random_sleep()

        locator = safe_find(page, "text=Get game")
        user_click(locator)

        random_sleep()

        # gog games manual claim (requires captcha)
        locator = safe_find(page, "[title='Claim Code']", timeout_ms=3000)
        if locator:
            with page.context.expect_page() as new_page_info:
                user_click(locator)

            new_page = new_page_info.value
            new_page.wait_for_load_state("networkidle")

            PrimeGaming.logger.info("Found claim code... must claim manually")

            log_persistent(PrimeGaming.logger, f"Claim{game_name} from {new_page.url}")

            PrimeGaming.logger.info("Game claimed successfully!")

            new_page.close()
            return True

        # Legacy games (Personally I don't care for that storefront, so no automation)
        locator = safe_find(page, "input[data-a-target='copy-code-input']", timeout_ms=3000, is_hidden=True)
        if locator:
            PrimeGaming.logger.info("Legacy-Games game... must claim manually")

            log_persistent(PrimeGaming.logger,
                           f"Claim{game_name} from legacy games with code: {locator.get_attribute('value')}")

            PrimeGaming.logger.info("Game claimed successfully!")
            return True

        # Epic games (currently none available so can't create)
        #
        #

        PrimeGaming.logger.info("Game claimed successfully!")
        log_persistent(PrimeGaming.logger, f"Successfully claimed {game_name}")

        random_sleep(1, 2)

        return True

    @staticmethod
    def scroll_until_end(page: Page, max_scrolls: int = 50, stable_retries: int = 3):
        """
        Scrolls down repeatedly using scroll_down() until the page height stops changing
        for `stable_retries` consecutive checks.

        Args:
            page (Page): Playwright page instance.
            max_scrolls (int): Maximum scroll iterations before giving up.
            stable_retries (int): How many times height must remain unchanged before stopping.
        """
        stable_count = 0

        for i in range(max_scrolls):
            previous_height = page.evaluate("document.documentElement.scrollHeight")

            # Scroll down one viewport at a time
            try:
                scroll_down(page, amount=page.evaluate("window.innerHeight"))
            except Exception as e:
                PrimeGaming.logger.error(f"[ERROR] scroll_down() failed on iteration {i}: {e}")
                break

            random_sleep(1, 2)

            current_height = page.evaluate("document.documentElement.scrollHeight")
            PrimeGaming.logger.debug(
                f"[DEBUG] Scroll #{i}: prev={previous_height}, curr={current_height}, stable={stable_count}")

            # If height hasn't changed, increment stability counter
            if current_height == previous_height:
                stable_count += 1
                if stable_count >= stable_retries:
                    PrimeGaming.logger.debug(
                        f"[INFO] -!- Page height stable for {stable_retries} checks — finished after {i + 1} scrolls.")
                    return True
            else:
                stable_count = 0  # reset if height changes

        PrimeGaming.logger.warning("[WARN] -!- Reached max scrolls without full stabilization.")
        return False

    @staticmethod
    def get_unique_game_locators(
            page: Page,
            game_selector: str,
            unique_by: str
    ) -> dict[str, str]:
        """
        Collects all locators matching `game_selector` and deduplicates them
        by a given attribute (e.g., aria-label, id, name).

        Args:
            page (Page): Playwright page instance or scoped locator.
            game_selector (str): CSS or XPath selector for the elements.
            unique_by (str): Attribute name to deduplicate by.

        Returns:
            dict[str, str]: Mapping from unique attribute value → href.
        """
        locators = page.locator(game_selector).all()
        unique_dict = {}

        for loc in locators:
            try:
                game_name = loc.get_attribute(unique_by).removeprefix("Claim ")
                if not game_name:
                    continue  # skip elements without this attribute
                if game_name not in unique_dict:
                    unique_dict[game_name] = f'a[data-a-target="FGWPOffer"][href="{loc.get_attribute("href")}"]'
            except Exception as e:
                print(f"[WARN] Failed to process locator: {e}")

        return unique_dict
