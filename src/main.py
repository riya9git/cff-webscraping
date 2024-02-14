#!/usr/bin/env python

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

import apm
import rec1
import sheets


LOG_HEADER = [
    "abbreviation",
    "full_name",
    "date",
    "time",
    "exit_code",
    # "skip",
    "provider",
    # "domain",
    "full_url",
]


def webscrape(city, sheet_id):
    """
    Kick off webscraping for a city. Automatically dispatch to the right
    package based on city domain. Expects a well-formatted row from the
    the "City Links" Google Sheet.
    """
    city_name = city["full_name"]
    print(f"\n> {city_name}")

    try:
        if city["skip"] == "Y":
            print("Skipped due to config file")
            exit_code = 4

        else:
            match city["provider"]:
                case "apm":
                    exit_code = apm.download_rosters(city, sheet_id)
                case "rec1":
                    exit_code = rec1.download_rosters(city, sheet_id)
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
    df = df[LOG_HEADER]
    sheets.upload_log(df, sheet_id, header=False)

    print("Done")


if __name__ == "__main__":
    # Set parallel to true for faster download
    parallel = True

    print("Starting webscraper")

    # Get timestamp of run
    curr_date = datetime.now().strftime("%Y-%m-%d")
    curr_time = datetime.now().strftime("%H-%M-%S")
    datetime = curr_date + "_" + curr_time
    print(f"Datetime of run: {datetime}")

    # Get config files
    print("Getting config file")
    city_links = sheets.get_city_links()
    print(f"Got records for {len(city_links)} cities")

    # Create new sheet
    print("Creating new sheet")
    log_header = pd.DataFrame(LOG_HEADER + ["roster_count", "course_count"]).T
    sheet_id = sheets.create_new_roster_file(datetime, log_header)
    print(f"id: {sheet_id}")

    if parallel:
        # Run webscraping in parallel
        print("Running webscraper in parallel")
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(webscrape, city, sheet_id) for city in city_links
            }

    else:
        # Run sequentially
        print("Running webscraper sequentially")
        for city in city_links:
            webscrape(city, sheet_id)

    print("All done!")
