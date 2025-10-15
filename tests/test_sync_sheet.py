from application import application as app
from unittest.mock import patch, MagicMock


def _fake_ws_with_headers_and_rows(rows):
    ws = MagicMock()
    ws.get_all_values.return_value = rows
    ws.spreadsheet.values_batch_update = MagicMock()
    return ws


@patch("src.app.get_worksheet")
@patch("src.app.fetch_price_cached")
def test_sync_sheet_dry_run(mock_fetch, mock_ws):
    headers = ["Card","Set","Source","LastPrice","Currency","LastChecked","Status","Notes"]
    data = [headers, ["Island","LEA","scryfall","","","","",""]]
    mock_ws.return_value = _fake_ws_with_headers_and_rows(data)
    mock_fetch.return_value = {"card":"Island","set":"LEA","price":0.12,"currency":"USD","source":"scryfall","status":"ok","error":None}

    c = app.test_client()
    rv = c.post("/api/sync-sheet", json={"dry_run": True})
    assert rv.status_code == 200
    assert rv.get_json()["dry_run"] is True
    assert rv.get_json()["updated"] == 1


