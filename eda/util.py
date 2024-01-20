from urllib.parse import urlparse

import pandas as pd


def get_df() -> pd.DataFrame:
    df = pd.read_excel("City_Links_MISC.xlsx", sheet_name="webscraping")
    df["netloc"] = df["url"].map(lambda d: urlparse(d).netloc)
    return df
