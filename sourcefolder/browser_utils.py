"""Shared Chrome setup to reduce bot-detection blocks on Naukri."""

import re
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

try:
    import undetected_chromedriver as uc

    HAS_UC = True
except ImportError:
    HAS_UC = False

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

_STEALTH_ARGS = [
    "--disable-notifications",
    "--disable-popups",
    "--disable-blink-features=AutomationControlled",
    f"--user-agent={USER_AGENT}",
]


def _get_chrome_major_version():
    try:
        result = subprocess.run(
            [
                "reg",
                "query",
                r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon",
                "/v",
                "version",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        match = re.search(r"(\d+)\.", result.stdout)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def _apply_stealth(driver):
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": (
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
        },
    )


def _build_selenium_options(headless):
    options = webdriver.ChromeOptions()
    for arg in _STEALTH_ARGS:
        options.add_argument(arg)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")

    return options


def _build_uc_options(headless):
    options = uc.ChromeOptions()
    for arg in _STEALTH_ARGS:
        options.add_argument(arg)
    if headless:
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
    return options


def _create_uc_driver(headless):
    chrome_version = _get_chrome_major_version()
    kwargs = {
        "options": _build_uc_options(headless),
        "headless": headless,
        "use_subprocess": True,
    }
    if chrome_version:
        kwargs["version_main"] = chrome_version
    return uc.Chrome(**kwargs)


def create_chrome_driver(headless):
    """Launch Chrome with settings that are less likely to be blocked."""
    if headless and HAS_UC:
        try:
            return _create_uc_driver(headless)
        except Exception:
            pass

    options = _build_selenium_options(headless)
    driver = webdriver.Chrome(options=options, service=ChromeService())
    _apply_stealth(driver)
    return driver
