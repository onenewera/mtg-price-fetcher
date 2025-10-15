import os
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials

_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]


def get_gspread_client():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not set")
    info = json.loads(raw)
    creds = Credentials.from_service_account_info(info, scopes=_SCOPE)
    return gspread.authorize(creds)


def get_worksheet():
    sheet_id = os.getenv("SHEET_ID")
    tab = os.getenv("SHEET_TAB_NAME", "Cards")
    if not sheet_id:
        raise RuntimeError("SHEET_ID not set")
    gc = get_gspread_client()
    sh = gc.open_by_key(sheet_id)
    return sh.worksheet(tab)


def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


