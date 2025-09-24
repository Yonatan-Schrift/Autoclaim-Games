"""
@file:   main.py
@brief:  A program that automatically claims free video games from select web-stores.
@author: Yonatan-Schrift
"""
import os

from playwright.sync_api import sync_playwright
from time import sleep
from anti_bot_actions import *
from dotenv import load_dotenv

def epic_games():
    url_claim = 'https://store.epicgames.com/en-US/free-games'
    url_login = 'https://www.epicgames.com/id/login?lang=en-US&noHostRedirect=true&redirectUrl=' + url_claim

    p, browser, page = setup_and_open(url_claim)

    locator = page.locator("text='Sign in'")
    locator.wait_for(state="visible", timeout=15000)

    if locator:
        print('found login')
        user_click(locator) # clicking on the sign in

        random_sleep(1,4)

        locator = page.locator("#email")
        locator.wait_for(state="visible", timeout=15000)

        if locator:
            print('found email')
            # get email and passwords from user file
            eg_mail = os.getenv("EG_MAIL")
            eg_pass = os.getenv("EG_PASSWORD")

            print(eg_mail, eg_pass)
            sleep(1500)
            human_type(page=page, loc=locator, text=eg_mail)




    else:
        print('no login')


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
    load_dotenv(override=True)
    eg_mail = os.getenv("EG_MAIL")
    eg_pass = os.getenv("EG_PASSWORD")

    print(eg_mail, eg_pass)
    sleep(15000)
    epic_games()

    return 0


if __name__ == '__main__':
    main()
