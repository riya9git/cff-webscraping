#!/usr/bin/env python

import os
import time
import warnings

import pandas as pd
from selenium.webdriver.common.by import By

from sheets import upload_roster
from util import init_driver, is_on_page

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def download_rosters(city, sheet_id):
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
    print("Logging into portal")
    login(driver, city_name, username, password)

    # Check if failed to log in
    if is_on_page(driver, "incorrect") or is_on_page(driver, "locked"):
        print("Caught failure: could not log in")
        exit_code = 2

    else:
        # Open rosters page
        print("Opening rosters page")
        driver.get(rosters_url)
        time.sleep(1)

        # Check if failed to find rosters page
        if is_on_page(driver, "Page not found"):
            print("Caught failure: could not find rosters page")
            exit_code = 2

        else:
            print("Downloading rosters")
            get_rosters(driver, city_name)
            time.sleep(30)

            # Check if nothing downloaded
            if is_on_page(driver, "No records found"):
                print("Outcome: No records found")
                exit_code = 3

            else:
                # Upload file and remove local copy
                print("Uploading data")
                df = pd.read_excel(download_fn)
                upload_roster(df, sheet_id, city_name)
                os.remove(download_fn)
                print("Outcome: Success")
                exit_code = 0

    # Remove temp download directory
    os.rmdir(download_dir)

    # Close driver
    driver.close()

    return exit_code


def login(driver, city_name, username, password):
    """
    Log into roster portal for a city.
    """
    # Enter username
    print("Entering username")
    if city_name in ["SJ"]:
        print("(Using alternative element)")
        username_aria = "[aria-label='Login name Required']"
    else:
        username_aria = "[aria-label='Email address Required']"
    username_field = driver.find_element(By.CSS_SELECTOR, username_aria)
    username_field.send_keys(username)

    # Enter password
    print("Entering password")
    password_field = driver.find_element(
        By.CSS_SELECTOR, "[aria-label='Password Required']"
    )
    password_field.send_keys(password)

    print("Logging in")
    # Click login button
    login_button = driver.find_element(By.CLASS_NAME, "btn-super")
    login_button.click()
    time.sleep(1)


def get_rosters(driver, city_name):
    """
    Download roster as xlsx for city.
    """
    # Click "Add activities" button
    print("Opening add activites")
    add_activities = driver.find_element(By.CLASS_NAME, "button-add--wrapper")
    add_activities.click()
    time.sleep(2)

    # Click select all checkbox (using aria-label)
    print("Selecting all activities")
    all_activities_button = driver.find_element(
        By.CSS_SELECTOR, "[aria-label='All Activities']"
    )
    all_activities_button.click()

    # Click save button
    print("Clicking save")
    save_button = driver.find_element(
        By.CSS_SELECTOR, "div.modal-footer__right button.btn.btn-strong"
    )
    save_button.click()
    time.sleep(1)

    # Change output to Excel
    print("Changing output type to Excel (accessible)")
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
    print("Adding email to output")
    if city_name in ["ML", "SCa", "SJ"]:
        print("(Using alternative xpath)")
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
    print("Adding head of household information to output")
    hoh_option = driver.find_element(
        By.XPATH, "//span[text()='Use head of household contact information?']"
    )
    driver.execute_script("arguments[0].click();", hoh_option)
    time.sleep(1)

    # Download
    print("Requesting download")
    download_button = driver.find_element(
        By.CSS_SELECTOR, "button[type='submit'].btn.btn-strong"
    )
    driver.execute_script("arguments[0].click();", download_button)
