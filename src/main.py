#!/usr/bin/env python

from datetime import datetime

import pandas as pd

import apm
import rec1
import sheets
from util import init_driver


def webscrape(city, curr_date, curr_time):
    """
    Kick off webscraping for a city. Automatically dispatch to the right
    package based on city domain. Expects a well-formatted row from the
    the "City Links" Google Sheet.
    """
    timestamp = curr_date + curr_time
    city_name = city["full_name"]
    print(f"\n> {city_name}")

    try:
        if city["skip"] == "Y":
            print("Skipped due to config file")
            exit_code = 4

        else:
            match city["provider"]:
                case "apm":
                    driver = init_driver()
                    exit_code = apm.download_rosters(driver, city, timestamp)
                    driver.close()

                case "rec1":
                    driver = init_driver()
                    exit_code = rec1.download_rosters(driver, city, timestamp)
                    driver.close()

                case _:
                    print("Unconfigured domain")
                    exit_code = 5

    except Exception as e:
        print(e)
        exit_code = 1

    city["date"] = curr_date
    city["time"] = curr_time
    city["exit_code"] = exit_code

    # Upload log
    print("Uploading log")
    df = pd.DataFrame([city])
    df = df[
        [
            "abbreviation",
            "full_name",
            "date",
            "time",
            "exit_code",
            "skip",
            "provider",
            "domain",
            "full_url",
        ]
    ]
    sheets.upload_log(df, header=False)

    print("All done!")


if __name__ == "__main__":
    print("Starting webscraper")

    # Get timestamp of run
    curr_date = datetime.now().strftime("%Y-%m-%d")
    curr_time = datetime.now().strftime("%H-%M-%S")
    print(f"Datetime of run: {curr_date}{curr_time}")

    # Get config files
    print("Getting config file")
    city_links = sheets.get_city_links()
    print(f"Done! Got records for {len(city_links)} cities.")

    # Run webscraping
    print("Running webscraper")
    for city in city_links:
        webscrape(city, curr_date, curr_time)

    print("All done!")
