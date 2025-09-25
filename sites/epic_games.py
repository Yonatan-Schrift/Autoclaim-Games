"""
@file:   epic_games.py
@brief:  This file contains functions specific to claiming games from the epic-games website.
@author: Yonatan-Schrift
"""
from core.anti_bot import random_sleep, user_click, scroll_down
from core.setup import setup_and_open
from core.utils import fill_field, click_locator, safe_find
from core.exceptions import *

from playwright.sync_api import Page, TimeoutError as PWTimeoutError
import re


def epic_games(eg_mail: str, eg_pass: str):
    url_claim = 'https://store.epicgames.com/en-US/free-games'

    p, browser, page = setup_and_open(url_claim, isEpic=True)
    claimed = 0

    # Checks if the user is already signed in
    locator = safe_find(page, "[aria-label='Account menu']", timeout_ms=3000)
    if not locator:
        try:
            sign_in(eg_mail, eg_pass, page)
        except ProjectError as e:
            print(f"-!- ERROR: {e}")
            return 1

    free_games = page.locator("[aria-label*='Free Games'][aria-label*='Free Now']").all()
    for i, item in enumerate(free_games, start=1):
        item.scroll_into_view_if_needed()
        random_sleep()
        game_name = clean_text(item.inner_text())
        link = f"https://store.epicgames.com{item.get_attribute('href')}"
        print(f"Item {i}: {game_name}, link: {link}")
        try:
            claim_game(page, link)
            claimed += 1
        except PWTimeoutError:
            print(f"-!- Failed to claim {game_name} -!-")

        random_sleep()
        page.goto(url_claim, wait_until="load")
    print(f"--- Successfully claimed {claimed} games ---")


def sign_in(eg_mail: str, eg_pass: str, page: Page):
    # --- Sign in button ---
    if not click_locator(page, "[aria-label='Sign in']"):
        raise LocatorNotFoundError("Sign in button missing, please check for updates to the script")

    # --- Enters email ---
    if not fill_field(page, "#email", eg_mail, "#continue"):
        raise InvalidCredentialsError(INVALID_CREDS_MSG)  # I'm pretty sure this never raises only sends out a warning

    # --- Enters password  ---
    if not fill_field(page, "#password", eg_pass, "#sign-in"):
        raise InvalidCredentialsError(INVALID_CREDS_MSG)  # I'm pretty sure this never raises only sends out a warning

    # --- 2FA step --- (User step)
    locator = safe_find(page, "text=6-digit")
    if locator:
        input("-?- Enter the 6-digit code into the browser, then press Enter here...")
        click_locator(page, "#yes")

    locator = safe_find(page, "[text='Sign in']")


def clean_text(text: str) -> str:
    pattern = re.compile(r"\n(.*)\n")
    match = pattern.search(text)
    if match: return match.group(1)


def claim_game(page: Page, link: str):
    page.goto(link)
    # scroll smoothly down a little bit
    scroll_down(page, 200)

    if safe_find(page, "text='In Library'", timeout_ms=2000):
        print(f"--- Game already claimed ---")
        return
    if safe_find(page, "text='end user license agreement'", timeout_ms=2000):
        print(f"-?- Accept End User License Agreement (only needed once) -?-")
        page.locator("button").filter(has_text="Accept").click()

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
    button.wait_for(state="visible", timeout=20_000)
    user_click(button)

    # captcha = page.frame_locator("#h_captcha_challenge_checkout_free_prod iframe")
    # if captcha:
    #     print(f"-!- CAPTCHA -!-")
    #     input("press Enter in the console to continue...")

    if safe_find(page, "text=Thanks for your order!"):
        print(f"--- CLAIMED ---")
        return
