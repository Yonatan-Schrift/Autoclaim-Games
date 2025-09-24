import random
import time
from typing import Final
from playwright.sync_api import Page, Locator

DEFAULT_ERROR_RATE: Final[float] = 0.06
DEFAULT_THINK_PAUSE: Final[float] = 0.08
_TYPOS_ALPHABET: Final[str] = "abcdefghijklmnopqrstuvwxyz0123456789"


def random_sleep(min_sec: float = 0.2, max_sec: float = 1.5) -> float:
    """
    Sleep for a random duration between min_sec and max_sec seconds.

    Args:
        min_sec: Minimum duration in seconds.
        max_sec: Maximum duration in seconds.

    Returns:
        The actual sleep duration in seconds.
    """
    # Swaps min and max if max is smaller
    if max_sec < min_sec:
        min_sec, max_sec = max_sec, min_sec

    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

    return delay


def user_click(locator: Locator, timeout_ms: int = 15_000):
    """
    Human-like click: wait -> hover -> small pause -> click.

    Args:
        locator: Target locator.
        timeout_ms: Max wait for visibility before interacting.
    """
    locator.wait_for(state="visible", timeout=timeout_ms)
    locator.hover()
    random_sleep()
    locator.click()


def human_type(page: Page, locator: Locator, text: str,
               min_delay=0.03, max_delay=0.24,
               error_rate=DEFAULT_ERROR_RATE, timeout_ms=15_000):
    """
    Type `text` into element represented by `locator` simulating human typing.

    Args:
        page: Playwright page.
        locator: Target locator (focusable/typeable element).
        text: Text to type.
        min_delay: Min per-character delay (seconds).
        max_delay: Max per-character delay (seconds).
        error_rate: Probability of a typo that gets corrected (0..1).
        timeout_ms: Max wait for visibility before typing.
    """
    if not text:
        return  # nothing to type

    # Focus on the element
    locator.wait_for(state="visible", timeout=timeout_ms)
    locator.scroll_into_view_if_needed()
    locator.click()

    # Swaps min and max if max is smaller
    if max_delay < min_delay:
        min_delay, max_delay = max_delay, min_delay

    def _ms() -> int:
        return int(random.uniform(min_delay, max_delay) * 1000)

    for ch in text:
        # simulate occasional typo
        if random.random() < error_rate:
            wrong_char = random.choice(_TYPOS_ALPHABET)
            page.keyboard.type(wrong_char, delay=_ms())
            random_sleep(0.05, 0.25)
            page.keyboard.press("Backspace")
            random_sleep(0.02, 0.1)

        # type the intended char
        page.keyboard.type(ch, delay=_ms())

        # small random pause occasionally (simulate thinking)
        if random.random() < DEFAULT_THINK_PAUSE:
            random_sleep(0.05, 0.4)
