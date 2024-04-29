#!/usr/bin/env python

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import pandas as pd

import apm
import rec1
import sheets

LOG_HEADER = [
    "abbreviation",
    "full_name",
    "exit_code",
    "provider",
    "full_url",
]

exit_code_desc = [
    "Success",
    "Uncaught exception",
    "Caught exception",
    "No records found",
    "Skipped",
    "Not configured",
]

BLANK = ""
SUMMARY_HEADERS = [
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "Activity",
    "Date From",
    "Date To",
    "Weekdays",
    "Time From",
    "Time To",
    "BLANK",
    "Enrollee Name",
    "BLANK",
    "BLANK",
    "Age",
    "Date of Birth",
    "Gndr",
    "1st Contact Name",
    "HOH Email",
    "1st Contact Phone",
    "Alt Contact Phone",
    "BLANK",
    "BLANK",
    "BLANK",
    "abbreviation",
    "Date",
    "BLANK",
    "BLANK",
    "BLANK",
    "Total Paid",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "Site",
    "Location",
    "run_datetime",
    "provider",
]


def get_rosters(config):
    """
    Kick off webscraping for a city. Automatically dispatch to the right
    package based on city domain. Expects a well-formatted row from the
    the "City Links" Google Sheet.
    """
    print(config["full_name"])

    if config["skip"] == "Y":
        config["exit_code"] = 4
        return config

    try:
        match config["provider"]:
            case "apm":
                config = apm.get_rosters(config)
            case "rec1":
                config = rec1.get_rosters(config)
            case _:
                config["exit_code"] = 5

    except Exception as e:
        print(config["full_name"], e)
        config["exit_code"] = 1

    return config


def format_log_data(rosters):
    df = pd.DataFrame(
        map(lambda x: dict(filter(lambda y: y[0] in LOG_HEADER, x.items())), rosters)
    )
    df["exit_code"] = df["exit_code"].map(lambda x: exit_code_desc[x])

    return df


def transform_apm(roster):
    return pd.DataFrame(
        map(
            lambda x: [
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                x["Activity"],
                x["Date From"],
                x["Date To"],
                x["Weekdays"],
                x["Time From"],
                x["Time To"],
                BLANK,
                x["Enrollee Name"],
                BLANK,
                BLANK,
                x["Age"],
                BLANK,
                x["Gndr"],
                x["1st Contact Name"],
                x["HOH Email"],
                x["1st Contact Phone"],
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                roster["abbreviation"],
                x["Date"],
                BLANK,
                BLANK,
                BLANK,
                x["Total Paid"],
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                x["Site"],
                x["Location"],
                run_datetime,
                roster["provider"],
            ],
            map(
                lambda x: defaultdict(lambda: "", x),
                filter(
                    lambda x: x["Activity Status"] == "Open",
                    roster["rosters"].to_dict("records"),
                ),
            ),
        ),
    )


def transform_rec1(roster):
    return pd.DataFrame(
        map(
            lambda x: [
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                x["Class"],
                x["Time"].split(" | ")[1].split("-")[0],
                x["Time"].split(" | ")[1].split("-")[1],
                BLANK,
                x["Time"].split(" | ")[2].split("-")[0],
                x["Time"].split(" | ")[2].split("-")[1],
                BLANK,
                x["Participant"],
                BLANK,
                BLANK,
                x["Age"],
                x["Dob"],
                x["Gender"],
                x["Parent"],
                x["Email"],
                x["Phone"],
                x["Mobile"],
                BLANK,
                BLANK,
                BLANK,
                roster["abbreviation"],
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                BLANK,
                x["Time"].split(" | ")[0],
                run_datetime,
                roster["provider"],
            ],
            map(
                lambda x: defaultdict(lambda: "", x),
                filter(
                    lambda x: x["Participant"] is not None,
                    roster["rosters"].to_dict("records"),
                ),
            ),
        ),
    )


if __name__ == "__main__":
    run_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"Datetime of run: {run_datetime}")

    config = sheets.get_config_file()

    with ThreadPoolExecutor() as executor:
        rosters = list(executor.map(get_rosters, config))

    log_data = format_log_data(rosters)
    sheet_id = sheets.create_new_roster_file(run_datetime, log_data)

    for roster in filter(lambda x: x["exit_code"] == 0, rosters):
        sheets.upload_roster(roster["rosters"], sheet_id, roster["abbreviation"])

    summary = pd.concat(
        map(
            lambda x: transform_apm(x) if x["provider"] == "apm" else transform_rec1(x),
            filter(lambda x: x["exit_code"] == 0, rosters),
        ),
    ).reset_index(drop=True)
    summary.columns = SUMMARY_HEADERS

    sheets.upload_roster(summary, sheet_id, "Summary")
