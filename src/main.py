from datetime import datetime

import apm
import rec1
import sheets


def webscrape(city, timestamp):
    """
    Kick off webscraping for a city. Automatically dispatch to the right
    package based on city domain. Expects a well-formatted row from the
    the "City Links" Google Sheet.
    """
    city_name = city["full_name"]
    print(f"#### {city_name} ####")
    try:
        if city["skip"] == "Y":
            print("Skipped due to config file")
        else:
            match city["provider"]:
                case "apm":
                    apm.download_rosters(city, timestamp)
                case "rec1":
                    rec1.download_rosters(city, timestamp)
                case _:
                    print("Unconfigured domain")
            if city["provider"] in ["apm", "rec1"]:
                print("Success!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    city_links = sheets.get_city_links()

    for city in city_links:
        webscrape(city, timestamp)
