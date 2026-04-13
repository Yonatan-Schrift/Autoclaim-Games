"""
@file:   core/setup.py
@module: core.setup
@brief:  Includes functions for setting up the browser agent.
@author: Yonatan-Schrift
"""
import os
import time

from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as PlaywrightError
from core.anti_bot import random_sleep
from logs.logger import get_logger

# Setup logger
logger = get_logger(__name__)


def setup_and_open(url: str = None, is_epic: bool = False, headless: bool = False):
    """
    Sets up the browser and opens the given URL.
    Includes retry logic for DNS/network failures.

    Args:
        url (str): The URL to open.
        is_epic (bool): Unused parameter kept for backwards compatibility.
        headless (bool): Whether to set up browser headless.

    Returns:
        Tuple: A tuple containing the Playwright instance, browser context, and page object.
    """
    p = sync_playwright().start()
    browser = None
    try:
        # Use persistent context to maintain login sessions across runs
        user_data_dir = "pw_user_data"
        os.makedirs(user_data_dir, exist_ok=True)
        
        browser = p.firefox.launch_persistent_context(
            user_data_dir,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) "
                "Gecko/20100101 Firefox/128.0"
            ),
            headless=headless,
            viewport={"width": 1920, "height": 1080}
        )

        page = browser.pages[0]

        # hide navigator.webdriver
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        random_sleep()
        
        # Retry logic for DNS/network failures
        if url:
            max_retries = 3
            retry_delay = 10  # seconds
            for attempt in range(max_retries):
                try:
                    page.goto(url, wait_until="load", timeout=30000)
                    break
                except PlaywrightError as e:
                    error_str = str(e)
                    if "NS_ERROR_UNKNOWN_HOST" in error_str or "net::ERR_NAME_NOT_RESOLVED" in error_str:
                        if attempt < max_retries - 1:
                            logger.warning(f"DNS resolution failed for {url}, retrying in {retry_delay}s ({attempt + 1}/{max_retries})...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"DNS resolution failed after {max_retries} attempts")
                            raise
                    else:
                        raise

        return p, browser, page
    except Exception:
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        p.stop()
        raise
