import os
import time
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*").split(",")}})
limiter = Limiter(get_remote_address, app=app, default_limits=["100/minute"])

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

# Import routes AFTER app is created if they register blueprints or use `app`
@app.get('/cards')
def fetch_card_price():
    # Imported inside to avoid any accidental import-time side effects
    from .scraper import get_card_price

    cardname = request.args.get('name')
    setname = request.args.get('set')
    result = get_card_price(cardname, setname)
    return jsonify(result)


# New API: stable endpoints
from .pricing import fetch_price_cached
from .sheets_client import get_worksheet, now_iso


@app.before_request
def _t0():
    g._t = time.time()


@app.after_request
def _t1(resp):
    try:
        ms = int((time.time() - g._t) * 1000)
        app.logger.info("path=%s status=%s ms=%s", request.path, resp.status_code, ms)
    except Exception:
        pass
    return resp


@app.get("/api/price")
@limiter.limit("30/minute")
def api_price():
    card = (request.args.get("card") or "").strip()
    if not card:
        return jsonify({"error": "missing required query param: card"}), 400
    set_ = (request.args.get("set") or "").strip() or None
    source = (request.args.get("source") or "").strip() or None
    res = fetch_price_cached(card, set_, source)
    return jsonify(res), 200


@app.post("/api/prices")
@limiter.limit("30/minute")
def api_prices():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []
    if not isinstance(items, list):
        return jsonify({"error": "body.items must be a list"}), 400
    out = []
    for it in items:
        card = (it.get("card") or "").strip()
        if not card:
            out.append({"status": "error", "error": "missing card"})
            continue
        set_ = (it.get("set") or "").strip() or None
        source = (it.get("source") or "").strip() or None
        out.append(fetch_price_cached(card, set_, source))
    return jsonify({"results": out}), 200


@app.post("/api/sync-sheet")
@limiter.limit("10/minute")
def sync_sheet():
    payload = request.get_json(silent=True) or {}
    dry_run = bool(payload.get("dry_run", False))

    ws = get_worksheet()
    data = ws.get_all_values()  # list[list[str]]
    if not data:
        return jsonify({"updated": 0, "message": "empty sheet"}), 200

    headers = data[0]
    try:
        idx_card = headers.index("Card")
        idx_set = headers.index("Set")
        idx_src = headers.index("Source")
        idx_price = headers.index("LastPrice")
        idx_curr = headers.index("Currency")
        idx_checked = headers.index("LastChecked")
        idx_status = headers.index("Status")
    except ValueError as e:
        return jsonify({"error": f"missing expected header: {e}"}), 400

    updates = []
    updated_count = 0
    for r, row in enumerate(data[1:], start=2):
        if len(row) <= idx_card or not row[idx_card].strip():
            continue
        card = row[idx_card].strip()
        set_ = (row[idx_set].strip() if len(row) > idx_set else "") or None
        src = (row[idx_src].strip() if len(row) > idx_src else "") or None

        res = fetch_price_cached(card, set_, src)
        values = ["", "", "", ""]
        values[0] = str(res.get("price") if res.get("price") is not None else "")
        values[1] = res.get("currency") or "USD"
        values[2] = now_iso()
        values[3] = res.get("status", "error")
        rng = f"{chr(ord('A')+idx_price)}{r}:{chr(ord('A')+idx_status)}{r}"
        updates.append((rng, [values]))
        updated_count += 1

    if dry_run or not updates:
        return jsonify({"updated": updated_count, "dry_run": True}), 200

    body = {"valueInputOption": "USER_ENTERED", "data": [
        {"range": rng, "values": vals} for rng, vals in updates
    ]}
    # Using underlying gspread Spreadsheet method
    ws.spreadsheet.values_batch_update(body)
    return jsonify({"updated": updated_count, "dry_run": False}), 200

