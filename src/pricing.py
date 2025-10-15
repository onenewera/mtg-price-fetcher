from functools import lru_cache
import os
import logging

from .scraper import get_card_price

logger = logging.getLogger(__name__)

DEFAULT_SOURCE = os.getenv("DEFAULT_PRICE_SOURCE", "scryfall")


def fetch_price(card: str, set_: str | None = None, source: str | None = None) -> dict:
    """
    Returns: {"card": str, "set": str|None, "price": float|str|None,
              "currency": "USD", "source": str, "status": "ok"|"not_found"|"error", "error": str|None}
    """
    source = source or DEFAULT_SOURCE
    try:
        # Use existing scraper which returns a dict with price strings; adapt as needed
        res = get_card_price(card, set_)
        # Expecting something like { 'prices': {'avg': '1.23'}, ... }
        price_value = None
        if isinstance(res, dict):
            prices = res.get("prices") or {}
            price_value = prices.get("avg") or prices.get("low") or prices.get("high")
        if price_value in (None, ""):
            return {"card": card, "set": set_, "price": None, "currency": "USD", "source": source, "status": "not_found", "error": None}
        return {"card": card, "set": set_, "price": _coerce_number(price_value), "currency": "USD", "source": source, "status": "ok", "error": None}
    except Exception as e:
        logger.exception("fetch_price failed")
        return {"card": card, "set": set_, "price": None, "currency": "USD", "source": source, "status": "error", "error": str(e)}


def _coerce_number(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return value


@lru_cache(maxsize=5000)
def fetch_price_cached(card: str, set_: str | None, source: str | None):
    return fetch_price(card, set_, source)


