"""Shared Naukri login helpers including OTP verification."""

import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

OTP_INPUT_XPATHS = [
    "//input[@id='otpField' or @name='otp' or @id='otp']",
    "//input[contains(@placeholder,'OTP') or contains(@placeholder,'otp')]",
    "//input[contains(@class,'otp')]",
    "//input[@type='tel' and (@maxlength='6' or @maxlength='4' or @maxlength='1')]",
    "//input[@inputmode='numeric']",
]

OTP_VERIFY_XPATHS = [
    "//button[contains(.,'Verify')]",
    "//button[contains(.,'Submit')]",
    "//button[contains(.,'Continue')]",
    "//*[@type='submit' and (contains(.,'Verify') or contains(.,'Login'))]",
]

SKIP_LOCATOR = "//*[text() = 'SKIP AND CONTINUE']"
CLOSE_LOCATOR = "//*[contains(@class, 'cross-icon') or @alt='cross-icon']"

LOGIN_CHECKPOINTS = [
    (By.ID, "ff-inventory"),
    (By.XPATH, "//*[contains(@class, 'view-profile')]//a"),
    (By.XPATH, "//a[contains(@href, '/mnjuser/profile')]"),
]


def _find_elements(driver, xpaths):
    for xpath in xpaths:
        elements = driver.find_elements(By.XPATH, xpath)
        visible = [el for el in elements if el.is_displayed()]
        if visible:
            return visible
    return []


def is_logged_in(driver):
    url = driver.current_url.lower()
    if "mnjuser" in url:
        return True

    for by, value in LOGIN_CHECKPOINTS:
        try:
            if driver.find_element(by, value).is_displayed():
                return True
        except Exception:
            pass
    return False


def is_otp_required(driver):
    if is_logged_in(driver):
        return False
    return bool(_find_elements(driver, OTP_INPUT_XPATHS))


def get_otp_from_user(log_msg):
    otp = os.environ.get("NAUKRI_OTP", "").strip()
    if otp:
        log_msg("Using OTP from NAUKRI_OTP environment variable.")
        return otp

    log_msg("OTP verification required. Check your phone or email.")
    return input("Enter the OTP sent to your phone/email: ").strip()


def fill_otp(driver, otp):
    inputs = _find_elements(driver, OTP_INPUT_XPATHS)
    if not inputs:
        return False

    if len(inputs) == 1:
        inputs[0].clear()
        inputs[0].send_keys(otp)
        return True

    for index, digit in enumerate(otp[: len(inputs)]):
        inputs[index].send_keys(digit)
    return True


def submit_otp(driver):
    buttons = _find_elements(driver, OTP_VERIFY_XPATHS)
    if buttons:
        buttons[0].click()
        return True

    inputs = _find_elements(driver, OTP_INPUT_XPATHS)
    if inputs:
        inputs[-1].send_keys(Keys.ENTER)
        return True
    return False


def dismiss_post_login_popups(driver, wait_for_element, get_element):
    if wait_for_element(driver, CLOSE_LOCATOR, "XPATH", 10):
        get_element(driver, CLOSE_LOCATOR, "XPATH").click()
    if wait_for_element(driver, SKIP_LOCATOR, "XPATH", 5):
        get_element(driver, SKIP_LOCATOR, "XPATH").click()


def handle_otp_if_required(driver, log_msg):
    for _ in range(8):
        if is_logged_in(driver):
            return True
        if is_otp_required(driver):
            break
        time.sleep(1)

    if not is_otp_required(driver):
        return is_logged_in(driver)

    otp = get_otp_from_user(log_msg)
    if not otp:
        log_msg("No OTP entered.")
        return False

    if not fill_otp(driver, otp):
        log_msg("Could not find OTP input field.")
        return False

    time.sleep(1)
    if not submit_otp(driver):
        log_msg("Could not find OTP submit button.")
        return False

    time.sleep(3)
    return True


def wait_for_login(driver, log_msg, timeout=60):
    for _ in range(timeout):
        if is_logged_in(driver):
            return True
        time.sleep(1)

    log_msg("Login failed. Current URL: %s" % driver.current_url)
    return False
