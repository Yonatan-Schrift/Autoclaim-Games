"""
@file:   setup.py
@brief:  Includes functions for setting up the browser agent.
@author: Yonatan-Schrift
"""
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright
from core.anti_bot import random_sleep


def setup_and_open(url=None, isEpic=False):
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

    # sets up specific cookies for epic-games
    if(isEpic):
        value = (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z"
        browser.add_cookies([
            {
                "name": "OptanonAlertBoxClosed",
                "value": value,
                "domain": ".epicgames.com",
                "path": "/"
            },
            {
                "name": "HasAcceptedAgeGates",
                "value": "USK:9007199254740991,general:18,EPIC SUGGESTED RATING:18",
                "domain": "store.epicgames.com",
                "path": "/"
            }
        ])

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
