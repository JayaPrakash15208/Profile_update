"""Shared Chrome setup to reduce bot-detection blocks on Naukri."""

import os
import re
import subprocess
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

try:
    import undetected_chromedriver as uc

    HAS_UC = True
except ImportError:
    HAS_UC = False

IS_LINUX = sys.platform.startswith("linux")

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

_LINUX_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
]

_CHROME_BINARIES = [
    "/usr/bin/google-chrome-stable",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]

_CHROME_VERSION_COMMANDS = [
    "google-chrome-stable",
    "google-chrome",
    "chromium-browser",
    "chromium",
]


def _get_chrome_binary():
    for path in _CHROME_BINARIES:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def _get_chrome_major_version():
    if sys.platform == "win32":
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

    chrome_binary = _get_chrome_binary()
    commands = [chrome_binary] if chrome_binary else []
    commands.extend(_CHROME_VERSION_COMMANDS)

    for cmd in commands:
        if not cmd:
            continue
        try:
            result = subprocess.run(
                [cmd, "--version"],
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


def _apply_platform_args(options):
    for arg in _STEALTH_ARGS:
        options.add_argument(arg)

    if IS_LINUX:
        for arg in _LINUX_ARGS:
            options.add_argument(arg)

    chrome_binary = _get_chrome_binary()
    if chrome_binary:
        options.binary_location = chrome_binary


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
    _apply_platform_args(options)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")

    return options


def _build_uc_options(headless):
    options = uc.ChromeOptions()
    _apply_platform_args(options)

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
        except Exception as exc:
            print(f"undetected-chromedriver failed, falling back to selenium: {exc}")

    options = _build_selenium_options(headless)
    driver = webdriver.Chrome(options=options, service=ChromeService())
    _apply_stealth(driver)
    return driver
