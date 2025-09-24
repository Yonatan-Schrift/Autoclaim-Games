"""
@file:   epic_games.py
@brief:  This file contains functions specific to claiming games from the epic-games website.
@author: Yonatan-Schrift
"""
from core.setup import setup_and_open
from core.utils import fill_field, click_locator, safe_find
from core.exceptions import *

from playwright.sync_api import Page

from time import sleep


def epic_games(eg_mail: str, eg_pass: str):
    url_claim = 'https://store.epicgames.com/en-US/free-games'

    p, browser, page = setup_and_open(url_claim)

    # Checks if the user is already signed in
    locator = safe_find(page, "[aria-label='Account menu']")
    if not locator:
        try:
            sign_in(eg_mail, eg_pass, page)
        except ProjectError as e:
            print(f"-!- ERROR: {e}")
            return 1


    locator = safe_find(page, "[aria-label='free']")

    sleep(1544)


def sign_in(eg_mail: str, eg_pass: str, page: Page):
    # --- Sign in button ---
    if not click_locator(page, "[aria-label='Sign in']"):
        raise LocatorNotFoundError("Sign in button missing, please check for updates to the script")

    # --- Enters email ---
    if not fill_field(page, "#email", eg_mail, "#continue"):
        raise InvalidCredentialsError(INVALID_CREDS_MSG)

    # --- Enters password  ---
    if not fill_field(page, "#password", eg_pass, "#sign-in"):
        raise InvalidCredentialsError(INVALID_CREDS_MSG)

    # --- 2FA step --- (User step)
    locator = safe_find(page, "text=6-digit")
    if locator:
        input("-?- Enter the 6-digit code into the browser, then press Enter here...")
        click_locator(page, "#yes")
