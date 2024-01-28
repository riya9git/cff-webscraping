import re
import time

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from util import init_driver, get_login
from sheets import upload_roster


def download_rosters(city, timestamp):
    """
    Get all rosters from city and download.
    """
    city_name, city_url = city["abbreviation"], city["full_url"]
    domain = city["provider"]
    driver = init_driver()
    login(driver, city_url)
    time.sleep(2)
    classes, rosters = get_all_rosters(driver)

    export = []
    for i, roster in enumerate(rosters):
        extra_headers = ["City", "Timestamp", "Class", "Time"]
        extra_columns = [city_name, timestamp, *classes[i]]
        header = extra_headers + roster[0]
        blank = extra_columns + [None] * len(roster[0])
        data = [[*extra_columns, *row] for row in roster[1:]]
        export.append(pd.DataFrame([header, blank] + data))

    try:
        df = pd.concat(export)
        df = df.rename(columns=df.iloc[0]).drop(df.index[0]).reset_index(drop=True)

        upload_roster(df, f"{city_name}_{timestamp}_{domain}")

    except ValueError:
        print("No classes found!")


def login(driver, city_url):
    """
    Log into roster portal for a city.
    """
    USERNAME, PASSWORD = get_login()
    URL = city_url
    driver.get(URL)
    time.sleep(1)
    driver.find_element(By.PARTIAL_LINK_TEXT, "Log In").click()
    toggle_button = driver.find_elements(By.CLASS_NAME, "rec1-login-toggle-button")
    if toggle_button:
        toggle_button[0].click()
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "btn-primary").click()


def read_page(driver):
    """
    Read page and return class information, enrollment, and link to roster.
    """
    table = driver.find_element(By.CLASS_NAME, "ui-table-fixed")
    table_rows = table.text.split("\n")
    _, table_rows = table_rows[0], table_rows[1:]
    class_names = []
    class_times = []
    class_enrollments = []
    for i in range(len(table_rows) // 3):
        class_names.append(re.sub(r"^[\d]+\. (.*)", r"\1", table_rows[i * 3]))
        class_times.append(table_rows[i * 3 + 1])
        class_enrollments.append(
            int(re.sub(r"View \((\d*)\).*", r"\1", table_rows[i * 3 + 2]))
        )
    class_links = table.find_elements(By.CLASS_NAME, "is-dashboardRoster")

    return class_names, class_times, class_enrollments, class_links


def get_roster(driver):
    """
    Return list of roster entries.
    """
    roster_rows = []
    row_elements = (
        driver.find_element(By.CLASS_NAME, "dashboard-table")
        .find_element(By.TAG_NAME, "tbody")
        .find_elements(By.TAG_NAME, "tr")
    )
    for row_element in row_elements:
        if row_element.get_attribute("data-id"):
            row = []
            for td in row_element.find_elements(By.TAG_NAME, "td"):
                row.append(td.text)
            roster_rows.append(row)

    return roster_rows


def get_headers(driver):
    """
    Return header rows of roster.
    """
    header_elements = (
        driver.find_element(By.CLASS_NAME, "dashboard-table")
        .find_element(By.TAG_NAME, "thead")
        .find_elements(By.TAG_NAME, "th")
    )
    header = []
    for th in header_elements:
        header.append(th.text)

    return header


def go_to_next_page(driver, scope):
    """
    Go to next page of scope. Return True if exists, otherwise return False.
    """
    container_class = ""
    button_class = ""
    match scope:
        case "catalog":
            container_class = "text-center"
            button_class = "rec1-instructor-portal-page"
        case "roster":
            container_class = "instructor-activity-roster-container"
            button_class = "rec1-dashboard-roster-page"

    try:
        next_button = (
            driver.find_element(By.CLASS_NAME, container_class)
            .find_element(By.CLASS_NAME, "pagination")
            .find_elements(By.TAG_NAME, "li")[-1]
        )
    except NoSuchElementException:
        return False
    if next_button.get_attribute("class") == "disabled":
        return False
    else:
        driver.execute_script(
            "$(arguments[0]).click();",
            next_button.find_element(By.CLASS_NAME, button_class),
        )  # Click on unreachable button
        return True


def close_roster_page(driver):
    """
    Exit from roster page.
    """
    driver.find_elements(By.CLASS_NAME, "close")[-1].click()


def get_all_rosters(driver):
    """
    Get all non-empty rosters from every page of website catalog.
    """
    classes = []
    rosters = []
    try_next_page_catalog = True
    while try_next_page_catalog:
        time.sleep(0.5)
        class_names, class_times, class_enrollments, class_links = read_page(driver)
        for i, enrollment in enumerate(class_enrollments):
            time.sleep(0.5)
            class_links[i].click()
            time.sleep(0.5)
            roster = [get_headers(driver)]
            if enrollment > 0:
                try_next_page_roster = True
                while try_next_page_roster:
                    time.sleep(0.5)
                    roster.extend(get_roster(driver))
                    try_next_page_roster = go_to_next_page(driver, "roster")
            close_roster_page(driver)
            classes.append([class_names[i], class_times[i]])
            rosters.append(roster)
        try_next_page_catalog = go_to_next_page(driver, "catalog")

    return classes, rosters
