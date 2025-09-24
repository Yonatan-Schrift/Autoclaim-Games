import random
import time
from typing import Final
from playwright.sync_api import Page, Locator

DEFAULT_ERROR_RATE: Final[float] = 0.06
DEFAULT_THINK_PAUSE: Final[float] = 0.08
DEFAULT_MIN_DELAY : Final[float] = 0.03
DEFAULT_MAX_DELAY: Final[float] = 0.03
DEFAULT_MAX_ALLOWED_DELAY: Final[int] = 300 # 5 minutes
_TYPOS_ALPHABET: Final[str] = "abcdefghijklmnopqrstuvwxyz0123456789"


def random_sleep(min_sec: float = 0.2, max_sec: float = 1.5) -> float:
    """
    Sleep for a random duration between min_sec and max_sec seconds.

    Args:
        min_sec: Minimum duration in seconds.
        max_sec: Maximum duration in seconds.

    Returns:
        The sleep duration in seconds.
    """
    # Swaps min and max if max is smaller
    if max_sec < min_sec:
        min_sec, max_sec = max_sec, min_sec
    if max_sec < 0 or min_sec < 0 or max_sec > DEFAULT_MAX_ALLOWED_DELAY:
        return 0

    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

    return delay


def user_click(locator: Locator):
    """
    Human-like click:  hover -> small pause -> click.

    Args:
        locator (Locator | None): Target locator.
    """
    if Locator is None: return  # in case of empty locator

    locator.scroll_into_view_if_needed()
    locator.hover()
    random_sleep(0.1, 0.3)
    locator.click()


def human_type(
        page: Page,
        locator: Locator,
        text: str,
        min_delay: float = DEFAULT_MIN_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        error_rate: float = DEFAULT_ERROR_RATE,
) -> None:
    """
    Type `text` into element represented by `locator` simulating human typing.

    Args:
        page (Page): Playwright page.
        locator (Locator): Target locator (focusable/typeable element).
        text (str): Text to type.
        min_delay (float): Min per-character delay (seconds).
        max_delay (float): Max per-character delay (seconds).
        error_rate (float): Probability of a typo that gets corrected (0..1).

    Returns:
        None
    """
    if not text:
        return  # nothing to type

    # Focus on the element
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

def scroll_down(page: Page, amount: int) -> None:
    total = 0

    while total < amount:
        pick = random.randint(1, amount - total)
        total += pick
        page.mouse.wheel(100, pick)
