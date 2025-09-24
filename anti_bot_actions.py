import random
import time
from playwright.sync_api import Page, TimeoutError


def random_sleep(min_sec=0.2, max_sec=1.5):
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def user_click(locator):
    locator.hover()
    random_sleep()
    locator.click()


def human_type(page: Page, loc, text: str,
               min_delay=0.03, max_delay=0.24,
               error_rate=0.06):
    """
    Type `text` into element represented by `locator` simulating human typing.

    - locator: Playwright locator
    - min_delay/max_delay: per-character delay range in seconds
    - error_rate: fraction of chars that will be typed wrong and corrected (0-1)
    """

    # ensure element is visible and focused with a real click
    loc.scroll_into_view_if_needed()
    loc.click()  # click to focus; triggers focus/input events like a human

    for ch in text:
        # decide whether to make a mistake
        if random.random() < error_rate:
            # type a wrong char
            wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
            page.keyboard.type(wrong_char, delay=int(random.uniform(min_delay, max_delay) * 1000))
            # short pause then backspace
            time.sleep(random.uniform(0.05, 0.25))
            page.keyboard.press("Backspace")
            # small pause before continuing
            time.sleep(random.uniform(0.02, 0.1))

        # type the intended char
        page.keyboard.type(ch, delay=int(random.uniform(min_delay, max_delay) * 1000))

        # small random pause occasionally (simulate thinking)
        if random.random() < 0.08:
            time.sleep(random.uniform(0.05, 0.4))


def find_locator_and_click(page: Page, text: str):
    try:
        locator = page.locator(text)
        locator.wait_for(state="visible", timeout=15000)
        random_sleep()

        user_click(locator)

    except TimeoutError:
        pass


def find_and_fill(page: Page, to_locate: str, to_fill: str, to_continue: str):
    try:
        locator = page.locator(to_locate)
        locator.wait_for(state="visible", timeout=15000)
        random_sleep(2, 4)

        if to_fill:
            human_type(page=page, loc=locator, text=to_fill)
            random_sleep()
        else:
            print(f"-!- No value provided for {to_locate}")

        find_locator_and_click(page, to_continue)

    except TimeoutError:
        print(f"-!- Could not find element: {to_locate}")
