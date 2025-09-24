"""
@file:   main.py
@brief:  A program that automatically claims free video games from select web-stores.
@author: Yonatan-Schrift
"""
import os

from time import sleep

from core.setup import setup_and_open
from core.utils import find_and_fill, find_locator_and_click
from playwright.sync_api import TimeoutError as PWTimeoutError
from dotenv import load_dotenv


def epic_games():
    url_claim = 'https://store.epicgames.com/en-US/free-games'

    # Get credentials
    eg_mail = os.getenv("EG_EMAIL")
    eg_pass = os.getenv("EG_PASSWORD")

    p, browser, page = setup_and_open(url_claim)

    try:
        # --- Sign in button ---
        find_locator_and_click(page, "[aria-label='Sign in']")

        # --- Enters email ---
        find_and_fill(page, "#email", eg_mail, "#continue")

        # --- Enters password  ---
        find_and_fill(page, "#password", eg_pass, "#sign-in")

        # --- 2FA step --- (User step)
        try:
            locator = page.locator("text=6-digit")
            locator.wait_for(state="visible", timeout=15000)

            input("-?- Enter the 6-digit code into the browser, then press Enter here...")

            find_locator_and_click(page, "#yes")
        except PWTimeoutError:
            print("No 2FA prompt found")

    # website changed or already signed in
    except PWTimeoutError:
        print("Login step not required (already signed in or site changed)")

    sleep(1544)


def gog():
    pass


def prime_gaming():
    pass

def main():
    load_dotenv(override=True, dotenv_path="./user.env")

    epic_games()

    return 0


if __name__ == '__main__':
    main()
