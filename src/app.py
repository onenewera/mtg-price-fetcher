from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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

