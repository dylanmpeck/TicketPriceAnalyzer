import os

def _load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass

_load_dotenv()

def _require(key):
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}. Copy .env.example to .env and fill it in.")
    return val

CLIENT_ID = os.environ.get("SEATGEEK_CLIENT_ID") or _require("SEATGEEK_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SEATGEEK_CLIENT_SECRET") or _require("SEATGEEK_CLIENT_SECRET")

DB_PATH = os.path.join(os.path.dirname(__file__), "prices.db")

# Target show
PERFORMER_SLUG = "bruno-mars"
TARGET_DATES = ["2026-10-10", "2026-10-11"]
VENUE_CITY = "santa clara"

# Alert thresholds — conservative; tune after 30+ days of data
MIN_DATA_DAYS = 30
PRICE_DROP_PCT = 0.80       # alert if current lowest ≤ 80% of 30-day avg lowest
CONSECUTIVE_DROPS = 3       # price must have fallen N fetches in a row
ABSOLUTE_FLOOR = 50         # never alert below this (sanity check)
