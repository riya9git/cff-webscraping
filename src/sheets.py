#!/usr/bin/env python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CREDS_PATH = "auth/credentials.json"
TOKEN_PATH = "auth/token.json"

CITY_PORTALS_SHEET_ID = "1jM7ful2aOJ-eO5suBD19KIXH-4jY74GIiihCRtFyxTE"
CITY_PORTALS_SHEET_NAME = "City Portals"

UPLOAD_SHEET_ID = "1j10jNGR8fPmv4xS86QFqU_ZpCQthVyFLdBoij44P7tQ"
UPLOAD_LOG_SHEET_NAME = "Log"


def get_creds(oauth_loc=CREDS_PATH, scope=SCOPES):
    """
    Gets credentials to access Google Drive. Requires OAuth token.
    """
    creds = None
    # Check for saved token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(oauth_loc, scope)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


def get_values(creds, sheet_id, sheet_range):
    """
    Access values of a Gsheet using sheet_id and range.
    https://developers.google.com/sheets/api/guides/concepts
    """
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    values = result.get("values", [])

    return values


def upload_to_sheet(df, creds, sheet_id, title):
    df = df.fillna("N/A")
    values = [df.columns.tolist()] + df.values.tolist()

    service = build("sheets", "v4", credentials=creds)

    # Adding sheet
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()

    # Uploading values
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{title}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()


def append_to_sheet(df, creds, sheet_id, title, header=False):
    df = df.fillna("N/A")
    if header:
        values = [df.columns.tolist()] + df.values.tolist()
    else:
        values = df.values.tolist()

    service = build("sheets", "v4", credentials=creds)

    # Uploading values
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=f"{title}!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()


def get_city_links():
    """
    Return config information for the webscraper
    from "City Links" sheet in "DataManagement Scripts".

    Columns: abbreviation full_name skip user password provider domain full_url
    """
    creds = get_creds()
    values = get_values(creds, CITY_PORTALS_SHEET_ID, CITY_PORTALS_SHEET_NAME)

    header, data = values[0], values[1:]
    city_links = []
    for datum in data:
        city_links.append({header[i]: datum[i] for i in range(len(datum))})

    return city_links


def upload_roster(df, sheet_name):
    """
    Upload roster to Google sheet.
    """
    creds = get_creds()
    upload_to_sheet(df, creds, UPLOAD_SHEET_ID, sheet_name)


def upload_log(df, header=False):
    """
    Upload webscraping results to Google sheet.
    """
    creds = get_creds()
    append_to_sheet(df, creds, UPLOAD_SHEET_ID, UPLOAD_LOG_SHEET_NAME, header=header)
