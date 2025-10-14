"""
@file:   core/utils.py
@module: core.utils
@brief:  Includes various utilities, especially for locating elements in a page
@author: Yonatan-Schrift
"""
import os

from core.anti_bot import random_sleep, user_click, human_type
from core.exceptions import *

from playwright.sync_api import Page, Locator
from playwright.sync_api import TimeoutError as PWTimeoutError

from typing import Optional, Final
import threading
import queue

DEFAULT_TIMEOUT_MS: Final[int] = 15000


def env_to_bool(env_var_name: Optional[str], default: bool = False) -> bool:
    """
    Convert an environment variable string to a boolean.

    Args:
        env_var_name (Optional[str]): The name of the environment variable to convert.
        default (bool): The default boolean value to return if the environment variable is not set.

    Returns:
        bool: The converted boolean value.
    """
    env_value = os.getenv(env_var_name)

    if env_value is None:
        return default

    return env_value.lower() in ("1", "true", "yes", "on")


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
    if not locator: return False

    user_click(locator)

    return True


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

    Raises:
        LocatorNotFoundError: If the element to locate is not found.
        MissingValueError: If the value to fill is not provided.
    """
    locator = safe_find(page, to_locate)
    if not locator:
        # Either already signed in or locator changed
        raise LocatorNotFoundError(f"-!- Couldn't locate element {to_locate}")
    if to_fill:
        human_type(page=page, locator=locator, text=to_fill)
        random_sleep()
    else:
        raise MissingValueError(f"-!- No value provided for \'to_locate\'")

    click_locator(page, to_continue)

    return True


def safe_find(page: Page, to_locate: str, timeout_ms: int = DEFAULT_TIMEOUT_MS, is_hidden: bool = False) -> Optional[Locator]:
    """
        Locate an element and wait until it becomes visible, returning None on failure (e.g., timeout or not found).

    Args:
        page (Page): the page to search
        timeout_ms (int): the time to wait before catching the error
        to_locate (str): the string to find
        is_hidden (bool) : whether to wait for the element to be visible

    Returns:
        None - if to_locate wasn't found
        Playwright locate object if found.

    Raises:
        MissingValueError: if to_locate is not provided

    Notes:
        On multiple matches, returns the first one.
    """
    if not to_locate:
        raise MissingValueError(f"-!- No value provided for \'to_locate\'")

    try:
        locator = page.locator(to_locate).first
        if not is_hidden: locator.wait_for(state="visible", timeout=timeout_ms)

        random_sleep(1, 3.5)
        return locator
    except PWTimeoutError:
        return None



def safe_fill(page: Page, to_locate: str, to_fill: str, to_continue: str):
    try:
        fill_field(page, to_locate, to_fill, to_continue)
    except ProjectError as e:
        raise e


def wait_for_user_input(prompt: str, timeout: int = 300) -> str | None:
    """
    Wait for user input with a timeout.

    Args:
        prompt: The prompt to show to the user.
        timeout: Max seconds to wait.

    Returns:
        The user input as string, or None if EOF (Ctrl+D/Z).

    Raises:
        TimeoutError: If no input was given within `timeout`.
    """
    q = queue.Queue()

    def reader():
        try:
            q.put(input(prompt))
        except EOFError:
            q.put(None)

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    t.join(timeout)

    if t.is_alive():
        raise TimeoutError("2FA entry timed out")

    return q.get()
