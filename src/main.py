#!/usr/bin/env python

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

import apm
import rec1
import sheets


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
                    exit_code = apm.download_rosters(city, timestamp)
                case "rec1":
                    exit_code = rec1.download_rosters(city, timestamp)
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

    print("Done")


if __name__ == "__main__":
    # Set parallel to true for faster download
    parallel = True

    print("Starting webscraper")

    # Get timestamp of run
    curr_date = datetime.now().strftime("%Y-%m-%d")
    curr_time = datetime.now().strftime("%H-%M-%S")
    print(f"Datetime of run: {curr_date}{curr_time}")

    # Get config files
    print("Getting config file")
    city_links = sheets.get_city_links()
    print(f"Got records for {len(city_links)} cities")

    if parallel:
        # Run webscraping in parallel
        print("Running webscraper in parallel")
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(webscrape, city, curr_date, curr_time)
                for city in city_links
            }

    else:
        # Run sequentially
        print("Running webscraper sequentially")
        for city in city_links:
            webscrape(city, curr_date, curr_time)

    print("All done!")
