from selenium import webdriver

from pathlib import Path

root_dir = Path(__file__).parents[1]


def init_driver():
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
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    return driver


def get_login():
    """
    Return username and password for login.
    """
    login_dir = root_dir / "data/login.txt"
    return open(login_dir, "r").read().split()


def export_file(df, file_dir):
    """
    Export roster file.
    """
    export_dir = root_dir / f"export/{file_dir}"
    df.to_csv(export_dir, index=False)


def process_city(city, pkg, timestamp):
    print(f"Getting roster for {city[0]}")
    try:
        pkg.download_rosters(city, timestamp, pkg.__name__)
    except Exception as e:
        print(e)
