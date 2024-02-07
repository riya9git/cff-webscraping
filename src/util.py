#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By

from pathlib import Path

root_dir = Path(__file__).parents[1]


def init_driver(headless=True):
    """
    Initialize driver for web-scraping.
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(root_dir / "export"),
            "download.directory_upgrade": True,
            "download.prompt_for_download": False,
        },
    )
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    return driver


def is_on_page(driver, text):
    """
    Return if text shows up on a webpage. Useful for checking for fail conditions.
    """

    element = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
    return bool(element)


def export_file(df, file_dir):
    """
    Export roster file.
    """
    export_dir = root_dir / f"export/{file_dir}"
    df.to_csv(export_dir, index=False)
