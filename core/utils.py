"""
@file:   utils.py
@brief:  Includes various utilities, especially for locating elements in a page
@author: Yonatan-Schrift
"""


from core.anti_bot import random_sleep, user_click, human_type
from playwright.sync_api import Page, Locator
from playwright.sync_api import TimeoutError as PWTimeoutError
from typing import Optional

def find_locator_and_click(page: Page, text: str):
    try:
        locator = page.locator(text)
        locator.wait_for(state="visible", timeout=15000)
        random_sleep()

        user_click(locator)

    except PWTimeoutError:
        pass


def find_and_fill(page: Page, to_locate: str, to_fill: str, to_continue: str):
    try:
        locator = page.locator(to_locate)
        locator.wait_for(state="visible", timeout=15000)
        random_sleep(2, 4)

        if to_fill:
            human_type(page=page, locator=locator, text=to_fill)
            random_sleep()
        else:
            print(f"-!- No value provided for {to_locate}")

        find_locator_and_click(page, to_continue)

    except PWTimeoutError:
        print(f"-!- Could not find element: {to_locate}")


def safe_find(page: Page, to_locate: str, timeout_ms: int = 15_000) -> Optional[Locator]:
    """
    This function tries to create a locator and handles it not being found

    Args:
        page (Page): the page to search
        to_locate (str): the string to find
        timeout_ms (int): the time to wait before catching the error

    Returns:
        None - if to_locate is empty or wasn't found
        Playwright locate object if found.
    """
    if to_locate is None:
        print("-!- No value provided for to_locate")
        return None

    try:
        locator = page.locator(to_locate)
        locator.wait_for(state="visible", timeout=timeout_ms)
        return locator
    except PWTimeoutError:
        return None