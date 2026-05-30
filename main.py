#!/usr/bin/env python3
import pathlib, os
_env = pathlib.Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
"""
Fetch SeatGeek prices for Bruno Mars at Levi's Stadium, store snapshots,
analyze trends, and alert if conditions are met.

Run via cron every few hours:
  0 */6 * * * cd /home/dylanmpeck/Projects/scalper && python main.py >> run.log 2>&1
"""
import sys
from datetime import datetime, timezone

import db
import fetcher
import analyzer
import alerter


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def run():
    db.init()
    now = utcnow()
    print(f"[{now}] Starting fetch...")

    try:
        events = fetcher.find_events()
    except Exception as e:
        print(f"ERROR fetching event list: {e}", file=sys.stderr)
        sys.exit(1)

    if not events:
        print("No matching events found on SeatGeek. Check performer slug / venue city.", file=sys.stderr)
        sys.exit(1)

    for event in events:
        event_id = event["id"]
        event_date = event.get("datetime_local", "")[:10]
        event_title = event.get("title", "Bruno Mars")
        stats = event.get("stats", {})

        # Prefer a fresh per-event fetch if listing came from the search endpoint
        # (search results sometimes have stale stats)
        try:
            fresh_stats = fetcher.fetch_event_stats(event_id)
            if fresh_stats:
                stats = fresh_stats
        except Exception as e:
            print(f"  WARN: could not refresh stats for event {event_id}: {e}")

        db.insert_snapshot(event_id, event_date, event_title, now, stats)

        lowest = stats.get("lowest_price")
        avg = stats.get("average_price")
        count = stats.get("listing_count")
        print(f"  [{event_date}] lowest=${lowest}  avg=${avg}  listings={count}")

        metrics = analyzer.analyze(event_id)
        if metrics:
            print(
                f"  trend → data_age={metrics['data_age_days']}d  "
                f"snapshots={metrics['snapshot_count']}  "
                f"consecutive_drops={metrics['consecutive_drops']}  "
                f"pct_of_30d_avg={metrics['pct_of_30d_avg']:.2%}"
                if metrics.get("pct_of_30d_avg") else
                f"  trend → data_age={metrics['data_age_days']}d  "
                f"snapshots={metrics['snapshot_count']}  (building baseline)"
            )

        should_alert, reason = alerter.check(metrics, event_title, event_date)
        if should_alert:
            alerter.notify(reason)
        else:
            print(f"  no alert: {reason}")

    print(f"[{utcnow()}] Done.")


if __name__ == "__main__":
    run()
