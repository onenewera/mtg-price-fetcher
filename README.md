# MTG Price Fetcher

## Overview

A small Flask service that fetches MTG card prices and can sync results into a Google Sheet. Deployed on Railway.

## Environment

- `SHEET_ID`: Google Sheet ID
- `SHEET_TAB_NAME`: Tab name (default `Cards`)
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Entire service account JSON string
- `ALLOWED_ORIGINS`: Comma-separated CORS origins (default `*`)
- `HTTP_USER_AGENT`: HTTP UA for outbound requests (default `mtg-price-fetcher/1.0`)
- `REQUEST_TIMEOUT`: Request timeout seconds (default `20`)
- `REDIS_URL` (optional): Redis URL for shared cache
- `DEFAULT_PRICE_SOURCE`: Default provider (default `scryfall`)

Create a Google Cloud service account with Sheets API enabled and share the sheet with the service account email as Editor.

## Endpoints

- `GET /healthz`
- `GET /api/price?card=<name>&set=<set>&source=<opt>`
- `POST /api/prices` body: `{ "items": [{"card":"...","set":"...","source":"..."}] }`
- `POST /api/sync-sheet` body: `{ "dry_run": true|false, "rows": "all" }`

Legacy endpoint retained for compatibility:
- `GET /cards?name=<name>&set=<set>`

## Running locally

```
pip install -r requirements.txt
export FLASK_ENV=development
export SHEET_ID=...
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
python -m gunicorn application:application --workers 2 --threads 4 --timeout 60 --bind 0.0.0.0:8080
```

## Tests & CI

Run tests: `pytest -q`
CI runs on GitHub Actions with Python 3.13.

## Release Notes

- Added stable API: `/api/price`, `/api/prices`, `/api/sync-sheet`, `/healthz`
- Google Sheets integration via service account
- LRU cache plus optional Redis TTL cache
- Rate limiting and CORS via env
- Basic tests and CI workflow

## Future Work

- Historical prices and PostgreSQL persistence
- Nightly batch scheduler calling `/api/sync-sheet`
- Alerts on high error rate
- `/metrics` for Prometheus
- Source plugin architecture
- Auth (bearer token) for write endpoints
