from datetime import datetime

import apm
import rec1
import sheets
from util import init_driver


def webscrape(city, timestamp):
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
        else:
            match city["provider"]:
                case "apm":
                    driver = init_driver()
                    apm.download_rosters(driver, city, timestamp)
                    driver.close()
                case "rec1":
                    driver = init_driver()
                    rec1.download_rosters(driver, city, timestamp)
                    driver.close()
                case _:
                    print("Unconfigured domain")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    city_links = sheets.get_city_links()

    for city in city_links:
        webscrape(city, timestamp)
