"""
@file:   epic_games.py
@brief:  This file contains functions specific to claiming games from the epic-games website.
@author: Yonatan-Schrift
"""

from core.anti_bot import random_sleep, user_click, scroll_down
from core.setup import setup_and_open
from core.utils import fill_field, click_locator, safe_find
from core.exceptions import *
from logs.logger import get_logger

from playwright.sync_api import Page, TimeoutError as PWTimeoutError

# Setup logger
logger = get_logger(__name__)


def epic_games(eg_mail: str, eg_pass: str, ):
    # Constants
    url_claim = 'https://store.epicgames.com/en-US/free-games'
    claimed = 0

    # setup playwright
    p, browser, page = setup_and_open(url_claim, is_epic=True)

    # Checks if the user is already signed in
    logger.info("Checking if already signed in...")
    locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=3000)
    if not locator:
        try:
            sign_in(eg_mail, eg_pass, page) # sign in
        except ProjectError as e:
            logger.error(f"-!- ERROR: {e} -!-") # log error
            return 1

    # Locate all free games on the page
    free_games = page.locator("[aria-label*='Free Games'][aria-label*='Free Now']").all()

    # Claim each free game
    for i, item in enumerate(free_games, start=1):
        item.scroll_into_view_if_needed()
        random_sleep()

        game_name = clean_text(item.inner_text())
        link = f"https://store.epicgames.com{item.get_attribute('href')}"

        logger.info(f"Trying to claim {game_name} from {link} ...")
        try:
            claim_game(page, link)
            claimed += 1
        except PWTimeoutError:
            logger.error(f"-!- Failed to claim {game_name} -!-")

        random_sleep()
        page.goto(url_claim, wait_until="load")
    print(f"Successfully claimed {claimed} games")

    # closes browser and Playwright
    logger.info("Closing browser and Playwright...")
    try:
        browser.close()
    finally:
        p.stop()


def sign_in(eg_mail: str, eg_pass: str, page: Page):
    logger.info("Signing in...")

    # --- Sign in button ---
    logger.debug("Clicking sign in button...")
    if not click_locator(page, "[aria-label='Sign in']"):
        raise LocatorNotFoundError("Sign in button missing, please check for updates to the script")

    # --- Enters email ---
    logger.debug("Entering Email...")
    if not fill_field(page, "#email", eg_mail, "#continue"):
        raise InvalidCredentialsError(INVALID_CREDS_MSG)  # I'm pretty sure this never raises only sends out a warning

    # --- Enters password  ---
    logger.debug("Entering password...")
    if not fill_field(page, "#password", eg_pass, "#sign-in"):
        raise InvalidCredentialsError(INVALID_CREDS_MSG)  # I'm pretty sure this never raises only sends out a warning

    # --- 2FA step --- (User step)
    logger.debug("Checking for 2FA...")
    locator = safe_find(page, "text=6-digit")
    if locator:
        logger.info("2FA found, waiting for user to enter code...")
        input("-?- Enter the 6-digit code into the browser, press continue, then press Enter here...")
        click_locator(page, "#yes")

    # --- Verifying sign in was successful ---
    locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=3000)
    if not locator:
        logger.error("Sign in failed: invalid credentials, 2FA code or unexpected issue")
        raise InvalidCredentialsError("Could not sign in, please check your credentials and/or 2FA code")


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

    logger.error(
        "Game name could not be extracted\n"
        "Could not find game name in \"{text}\". If the issue persists, please contact me via GitHub"
    )

    raise EpicGamesGameNotFoundError(
        f"Could not find game name in \"{text}\". If the issue persists, please contact me via GitHub"
    )


def claim_game(page: Page, link: str):
    logger.info(f"Claiming game from {link} ...")
    page.goto(link)
    # scroll smoothly down a little bit
    scroll_down(page, 200)

    # Check if game is already owned
    if safe_find(page, "text='In Library'", timeout_ms=2000):
        logger.info("Game already in library, skipping...")
        # print(f"--- Game already claimed ---")
        return

    # Accept EULA if it appears (only on first claim)
    if safe_find(page, "text='end user license agreement'", timeout_ms=2000):
        logger.warning("End User License Agreement detected, should be accepted automatically...")
        # print(f"-?- Accepts End User License Agreement (only needed once) -?-")
        page.locator("button").filter(has_text="Accept").click()

    logger.debug("Clicking purchase button...")
    click_locator(page, "[data-testid*='purchase']")

    # Wait until the checkout iframe exists
    page.wait_for_selector("#webPurchaseContainer iframe", timeout=20_000)

    # Attach to the checkout iframe
    iframe = page.frame_locator("#webPurchaseContainer iframe")

    # Locate the Place Order button (only when not loading)
    button = iframe.locator(
        'button:has-text("Place Order"):not(:has(.payment-loading--loading))'
    )

    # Wait until button is visible and click
    logger.debug("Clicking Place Order button...")
    button.wait_for(state="visible", timeout=20_000)
    user_click(button)


    # TODO: handle captcha if it appears
    # captcha = page.frame_locator("#h_captcha_challenge_checkout_free_prod iframe")
    # if captcha:
    #     print(f"-!- CAPTCHA -!-")
    #     input("press Enter in the console to continue...")

    # Wait until the "Thanks for your order!" text appears
    if safe_find(page, "text=Thanks for your order!"):
        logger.info("Game successfully claimed!")
        return
