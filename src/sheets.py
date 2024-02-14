#!/usr/bin/env python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# https://developers.google.com/identity/protocols/oauth2/scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

CREDS_PATH = "auth/credentials.json"
TOKEN_PATH = "auth/token.json"

CITY_PORTALS_SHEET_ID = "1jM7ful2aOJ-eO5suBD19KIXH-4jY74GIiihCRtFyxTE"
CITY_PORTALS_SHEET_NAME = "City Portals"

FOLDER_ID = "1-JoIuYv-Qh2NTjvVcg8ohGWpT30XiFW4"


# General methods
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
    with build("sheets", "v4", credentials=creds) as service:
        values = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=sheet_range)
            .execute()
            .get("values", [])
        )

    return values


def create_sheet(sheet_name, folder_id, creds):
    """
    Creates a new Google sheet in a given folder.
    """
    with build("drive", "v3", credentials=creds) as service:
        file_metadata = {
            "name": sheet_name,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [folder_id],
        }
        response = (
            service.files()
            .create(
                body=file_metadata,
            )
            .execute()
        )
    return response


def upload_to_sheet(df, creds, sheet_id, title):
    df = df.fillna("N/A")
    values = [df.columns.tolist()] + df.values.tolist()

    with build("sheets", "v4", credentials=creds) as service:
        # Add sheet
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
        ).execute()

        # Upload values
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{title}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": values},
        ).execute()


def append_to_sheet(df, creds, sheet_id, title, header=False):
    """
    Append data to sheet. Has optional `header` parameter to also
    upload DataFrame column names.
    """
    df = df.fillna("N/A")
    if header:
        values = [df.columns.tolist()] + df.values.tolist()
    else:
        values = df.values.tolist()

    with build("sheets", "v4", credentials=creds) as service:
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{title}!A1",
            valueInputOption="RAW",
            body={"values": values},
        ).execute()


# Webscraper methods
def create_new_roster_file(timestamp, log_header):
    """
    Create new roster file, and name the first sheet Log.
    """
    creds = get_creds()
    
    # Create new sheet
    sheet_id = create_sheet(timestamp, FOLDER_ID, creds)["id"]

    # Rename Sheet1 to Log
    with build("sheets", "v4", credentials=creds) as service:
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {"sheetId": 0, "title": "Log"},
                            "fields": "title",
                        }
                    }
                ]
            },
        ).execute()

    # Add header to log
    append_to_sheet(log_header, creds, sheet_id, "Log")

    return sheet_id


def get_city_links():
    """
    Return config information for the webscraper
    from "City Links" sheet in "DataManagement Scripts".

    Columns: abbreviation full_name skip user password provider domain full_url
    """
    creds = get_creds()
    values = get_values(creds, CITY_PORTALS_SHEET_ID, CITY_PORTALS_SHEET_NAME)

    # Reformat into list of dicts
    header, data = values[0], values[1:]
    city_links = []
    for datum in data:
        city_links.append({header[i]: datum[i] for i in range(len(datum))})

    return city_links


def upload_roster(df, sheet_id, sheet_name):
    """
    Upload roster to Google sheet.
    """
    creds = get_creds()
    upload_to_sheet(df, creds, sheet_id, sheet_name)


def upload_log(df, sheet_id, header=False):
    """
    Upload webscraping results to Google sheet.
    """
    creds = get_creds()
    append_to_sheet(df, creds, sheet_id, "Log", header=header)
