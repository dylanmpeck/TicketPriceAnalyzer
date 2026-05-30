from datetime import datetime, timedelta
import db


def _parse_dt(s):
    # Strip trailing Z so fromisoformat works on Python <3.11 and returns naive UTC
    return datetime.fromisoformat(s.rstrip("Z").split("+")[0])


def analyze(event_id):
    """
    Returns a dict with trend metrics for the given event.
    Returns None if there isn't enough data to analyze.
    """
    all_rows = db.get_snapshots(event_id)
    if not all_rows:
        return None

    now = datetime.utcnow()
    cutoff_30d = (now - timedelta(days=30)).isoformat()
    rows_30d = [r for r in all_rows if r["fetched_at"] >= cutoff_30d]

    # Data age: difference between first and last snapshot
    first_fetch = _parse_dt(all_rows[0]["fetched_at"])
    data_age_days = (now - first_fetch).days

    valid_lowest = [r["lowest"] for r in all_rows if r["lowest"] is not None]
    valid_30d_lowest = [r["lowest"] for r in rows_30d if r["lowest"] is not None]

    if not valid_lowest:
        return None

    current_lowest = valid_lowest[-1]
    avg_30d_lowest = sum(valid_30d_lowest) / len(valid_30d_lowest) if valid_30d_lowest else None

    # Price velocity: compare last N consecutive lowest prices
    recent = valid_lowest[-5:] if len(valid_lowest) >= 5 else valid_lowest
    consecutive_drops = 0
    for i in range(len(recent) - 1, 0, -1):
        if recent[i] < recent[i - 1]:
            consecutive_drops += 1
        else:
            break

    return {
        "event_id": event_id,
        "data_age_days": data_age_days,
        "snapshot_count": len(all_rows),
        "current_lowest": current_lowest,
        "avg_30d_lowest": avg_30d_lowest,
        "consecutive_drops": consecutive_drops,
        "pct_of_30d_avg": (current_lowest / avg_30d_lowest) if avg_30d_lowest else None,
    }
