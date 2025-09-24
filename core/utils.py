"""
@file:   utils.py
@brief:  Includes various utilities, especially for locating elements in a page
@author: Yonatan-Schrift
"""

from core.anti_bot import random_sleep, user_click, human_type
from playwright.sync_api import Page, Locator
from playwright.sync_api import TimeoutError as PWTimeoutError
from typing import Optional, Final
from warnings import warn

DEFAULT_TIMEOUT_MS : Final[int] = 15000

def click_locator(page: Page, text: str) -> bool:
    """
    Locate an element and click it, mimicking human behavior.

    Args:
        page (Page): the Playwright Page to search
        text (str): the locator string for the element to be clicked

    Returns:
        bool: True if the locator was found and clicked, False otherwise
    """
    locator = safe_find(page, text)
    user_click(locator)

    return True if locator else False


def fill_field(page: Page, to_locate: str, to_fill: str, to_continue: str) -> bool:
    """
    Locate an element and fill it with the given value.

    Args:
        page (Page): The Playwright Page to search.
        to_locate (str): The selector string of the element to locate.
        to_fill (str): The text to fill inside the located element.
        to_continue (str): The selector string of the "continue" element to click after filling.

    Returns:
        bool: True if the element was found and filled, False otherwise.
    """
    locator = safe_find(page, to_locate)
    if to_fill:
        human_type(page=page, locator=locator, text=to_fill)
        random_sleep()
    else:
        warn(f"-!- No value provided for {to_locate}")
        return False

    click_locator(page, to_continue)

    return True


def safe_find(page: Page, to_locate: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> Optional[Locator]:
    """
    Locate an element and wait until it becomes visible, returning None on failure.

    Args:
        page (Page): the page to search
        to_locate (str): the string to find
        timeout_ms (int): the time to wait before catching the error

    Returns:
        None - if to_locate wasn't found
        Playwright locate object if found.

    Raises:
        RuntimeError: if the timeout is exceeded
    """
    if not to_locate:
        warn(f"-!- No value provided for {to_locate}")
        return None

    try:
        locator = page.locator(to_locate)
        locator.wait_for(state="visible", timeout=timeout_ms)
        random_sleep(1, 3.5)
        return locator
    except PWTimeoutError:
        return None
