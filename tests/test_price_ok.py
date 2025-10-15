from application import application as app
from unittest.mock import patch


@patch("src.pricing.fetch_price", return_value={"card":"Island","set":"LEA","price":0.12,"currency":"USD","source":"scryfall","status":"ok","error":None})
def test_price_endpoint(mock_fetch):
    c = app.test_client()
    rv = c.get("/api/price?card=Island&set=LEA")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "ok"
    assert data["price"] == 0.12


