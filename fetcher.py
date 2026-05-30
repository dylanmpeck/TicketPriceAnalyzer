import requests
import config

BASE_URL = "https://api.seatgeek.com/2"


def _auth():
    return {"client_id": config.CLIENT_ID, "client_secret": config.CLIENT_SECRET}


def find_events():
    """Search SeatGeek for Bruno Mars events at Levi's Stadium on the target dates."""
    found = []
    for date in config.TARGET_DATES:
        params = {
            **_auth(),
            "performers.slug": config.PERFORMER_SLUG,
            "venue.city": config.VENUE_CITY,
            "datetime_local.gte": f"{date}T00:00:00",
            "datetime_local.lte": f"{date}T23:59:59",
            "per_page": 10,
        }
        resp = requests.get(f"{BASE_URL}/events", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for event in data.get("events", []):
            found.append(event)
    return found


def fetch_event_stats(event_id):
    """Fetch current stats for a single event by ID."""
    params = {**_auth()}
    resp = requests.get(f"{BASE_URL}/events/{event_id}", params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("stats", {})
