#!/usr/bin/env python

import os
import time
import warnings

import pandas as pd
from selenium.webdriver.common.by import By

from util import init_driver, is_on_page

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def get_rosters(city):
    """
    Get all rosters from city and download.
    """
    city_name = city["abbreviation"]
    login_url = city["full_url"]
    username = city["user"]
    password = city["password"]
    rosters_url = f"{login_url}/roster"
    download_dir = f"export/{city_name}"
    download_fn = f"{download_dir}/active_report.xlsx"

    # Create temp download directory
    os.mkdir(download_dir)

    # Open window
    driver = init_driver(download_dir=download_dir)

    # Open login screen
    driver.get(login_url)
    time.sleep(1)

    # Login to portal
    login(driver, city_name, username, password)

    # Check if failed to log in
    if is_on_page(driver, "incorrect") or is_on_page(driver, "locked"):
        exit_code = 2

    else:
        # Open rosters page
        driver.get(rosters_url)
        time.sleep(1)

        # Check if failed to find rosters page
        if is_on_page(driver, "Page not found"):
            exit_code = 2

        else:
            download_rosters(driver, city_name)
            time.sleep(30)

            # Check if nothing downloaded
            if is_on_page(driver, "No records found"):
                exit_code = 3

            else:
                # Upload file and remove local copy
                df = pd.read_excel(download_fn)
                city["rosters"] = df
                os.remove(download_fn)
                exit_code = 0

    # Remove temp download directory
    os.rmdir(download_dir)

    # Close driver
    driver.close()

    city["exit_code"] = exit_code

    return city


def login(driver, city_name, username, password):
    """
    Log into roster portal for a city.
    """
    # Enter username
    if city_name in ["SJ"]:
        username_aria = "[aria-label='Login name Required']"
    else:
        username_aria = "[aria-label='Email address Required']"
    username_field = driver.find_element(By.CSS_SELECTOR, username_aria)
    username_field.send_keys(username)

    # Enter password
    password_field = driver.find_element(
        By.CSS_SELECTOR, "[aria-label='Password Required']"
    )
    password_field.send_keys(password)

    # Click login button
    login_button = driver.find_element(By.CLASS_NAME, "btn-super")
    login_button.click()
    time.sleep(1)


def download_rosters(driver, city_name):
    """
    Download roster as xlsx for city.
    """
    # Click "Add activities" button
    add_activities = driver.find_element(By.CLASS_NAME, "button-add--wrapper")
    add_activities.click()
    time.sleep(2)

    # Click select all checkbox (using aria-label)
    all_activities_button = driver.find_element(
        By.CSS_SELECTOR, "[aria-label='All Activities']"
    )
    all_activities_button.click()

    # Click save button
    save_button = driver.find_element(
        By.CSS_SELECTOR, "div.modal-footer__right button.btn.btn-strong"
    )
    save_button.click()
    time.sleep(1)

    # Change output to Excel
    output_type = driver.find_element(
        By.XPATH, '//span[contains(text(), "Adobe Acrobat Reader")]'
    )
    driver.execute_script("arguments[0].scrollIntoView();", output_type)
    output_type.click()
    ms_excel_option = driver.find_element(
        By.XPATH,
        '//div[text()="Microsoft Excel (accessible)"]',
    )
    ms_excel_option.click()

    # Get email
    if city_name in ["ML", "SCa", "SJ"]:
        email_field_xpath = '//span[contains(text(), "Home phone")]'
    else:
        email_field_xpath = '//span[contains(text(), "Primary phone")]'
    email_field = driver.find_element(By.XPATH, email_field_xpath)
    driver.execute_script("arguments[0].scrollIntoView();", email_field)
    email_field.click()
    customer_email_option = driver.find_element(
        By.XPATH, '//div[text()="Customer email"]'
    )
    customer_email_option.click()

    # Get head of household
    hoh_option = driver.find_element(
        By.XPATH, "//span[text()='Use head of household contact information?']"
    )
    driver.execute_script("arguments[0].click();", hoh_option)
    time.sleep(1)

    # Download
    download_button = driver.find_element(
        By.CSS_SELECTOR, "button[type='submit'].btn.btn-strong"
    )
    driver.execute_script("arguments[0].click();", download_button)
