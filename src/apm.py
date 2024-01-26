import os
import time
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from util import init_driver, get_login

cities = [
    ["dublin", "dublinrecguide"],
    ["fremont", "fremont"],
    ["hayward", "haywardrec"],
    ["milpitas", "milpitasrec"],
    ["mountain_view", "mountainviewrecreation"],
    ["pacifica", "pacifica"],
    ["redwood_city", "rwcpark"],
    ["san_carlos", "sancarlos"],
    ["san_jose", "sanjoseparksandrec"],
]


def download_rosters(city, timestamp, domain):
    """
    Get all rosters from city and download.
    """

    city_name, city_url = city
    driver = init_driver()
    login(driver, city_url)
    time.sleep(1)
    get_rosters(driver, city_url)
    os.rename(
        "export/active_report.xlsx",
        f"export/{city_name}_{timestamp}_{domain}.xlsx",
    )


def login(driver, city_url):
    """
    Log into roster portal for a city.
    """
    USERNAME, PASSWORD = get_login()
    URL = f"https://anc.apm.activecommunities.com/{city_url}/myaccount"
    driver.get(URL)
    time.sleep(1)
    try:
        driver.find_element(
            By.CSS_SELECTOR, "[aria-label='Email address Required']"
        ).send_keys(USERNAME)
    except NoSuchElementException:
        driver.find_element(
            By.CSS_SELECTOR, "[aria-label='Login name Required']"
        ).send_keys(USERNAME)
    driver.find_element(By.CSS_SELECTOR, "[aria-label='Password Required']").send_keys(
        PASSWORD
    )
    driver.find_element(By.CLASS_NAME, "btn-super").click()


def get_rosters(driver, city_url):
    """
    Download roster as xlsx for city.
    """

    driver.get(f"https://anc.apm.activecommunities.com/{city_url}/myaccount/roster")
    time.sleep(1)

    if "pagenotfound" not in driver.current_url:
        # Filter by term
        driver.find_element(By.CLASS_NAME, "button-add--wrapper").click()
        time.sleep(2)
        season_filter = driver.find_element(
            By.CSS_SELECTOR, "[aria-description='All seasons']"
        )
        season_filter.click()
        season_filter.send_keys(Keys.UP)
        season_filter.send_keys(Keys.ENTER)
        driver.find_element(
            By.CSS_SELECTOR,
            "button.btn.btn-strong.report-search-list-header__apply-btn",
        ).click()
        driver.find_element(By.CSS_SELECTOR, "[aria-label='All Activities']").click()
        driver.find_element(
            By.CSS_SELECTOR, "div.modal-footer__right button.btn.btn-strong"
        ).click()
        time.sleep(1)

        # Change output to Excel
        output_type = driver.find_element(
            By.XPATH, '//span[contains(text(), "Adobe Acrobat Reader")]'
        )
        driver.execute_script("arguments[0].scrollIntoView();", output_type)
        output_type.click()
        driver.find_element(
            By.XPATH,
            '//div[text()="Microsoft Excel (accessible)"]',
        ).click()

        # Get email
        try:
            output_type = driver.find_element(
                By.XPATH, '//span[contains(text(), "Primary phone")]'
            )
        except NoSuchElementException:
            output_type = driver.find_element(
                By.XPATH, '//span[contains(text(), "Home phone")]'
            )
        driver.execute_script("arguments[0].scrollIntoView();", output_type)
        output_type.click()
        driver.find_element(
            By.XPATH,
            '//div[text()="Customer email"]',
        ).click()

        # Get head of household
        driver.execute_script(
            "arguments[0].click();",
            driver.find_element(
                By.XPATH, "//span[text()='Use head of household contact information?']"
            ),
        )
        time.sleep(1)

        # Download
        download_button = driver.find_element(
            By.CSS_SELECTOR, "button[type='submit'].btn.btn-strong"
        )
        driver.execute_script("arguments[0].click();", download_button)
        time.sleep(8)
        driver.close()
