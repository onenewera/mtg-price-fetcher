from application import application as app


def test_health():
    c = app.test_client()
    rv = c.get("/healthz")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "ok"


