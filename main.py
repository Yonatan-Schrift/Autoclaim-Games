"""
@file:   main.py
@brief:  A program that automatically claims free video games from select web-stores.
@author: Yonatan-Schrift
"""
import os

from playwright.sync_api import sync_playwright, TimeoutError
from time import sleep

from selenium.common import TimeoutException

from anti_bot_actions import *
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
        except TimeoutError:
            print("No 2FA prompt found")

    # website changed or already signed in
    except TimeoutError:
        print("Login step not required (already signed in or site changed)")

    sleep(1544)


def gog():
    pass


def prime_gaming():
    pass


def setup_and_open(url=None):
    p = sync_playwright().start()

    user_data_dir = "pw_user_data"
    browser = p.firefox.launch_persistent_context(
        user_data_dir,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) "
            "Gecko/20100101 Firefox/128.0"
        ),
        headless=False,
        args=["--start-maximized"]
    )

    page = browser.pages[0]
    page.set_viewport_size({"width": 1920, "height": 1080})

    # hide navigator.webdriver
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    random_sleep()
    if url:
        page.goto(url)

    return p, browser, page


def main():
    load_dotenv(override=True, dotenv_path="./user.env")

    epic_games()

    return 0


if __name__ == '__main__':
    main()
