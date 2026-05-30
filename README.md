# TicketPriceAnalyzer

Monitors resale ticket prices for Bruno Mars at Levi's Stadium (Oct 10 & 11, 2026) via the SeatGeek API. Stores price snapshots in a local SQLite database, analyzes trends over time, and alerts when conditions suggest a good time to buy.

## How it works

A cron job runs `main.py` every 6 hours. Each run:
1. Fetches current price stats (lowest, average, median, highest, listing count) for both show dates from SeatGeek
2. Stores a snapshot in `prices.db`
3. Analyzes the last 30 days of snapshots for trend signals
4. Fires an alert if all conditions are met

The alert is intentionally conservative — it requires at least 30 days of collected data before it will trigger, so the baseline is meaningful before any buy signal is issued.

## Alert conditions

All three must be true simultaneously:

| Condition | Default threshold |
|---|---|
| Minimum data collected | 30 days |
| Current lowest price | ≤ 80% of 30-day average lowest |
| Consecutive price drops | 3 or more fetches in a row |

Thresholds are defined in `config.py` and can be tuned once a month or more of data has been collected.

## Setup

**1. Clone and configure credentials**

```bash
git clone git@github.com:dylanmpeck/TicketPriceAnalyzer.git
cd TicketPriceAnalyzer
cp .env.example .env
# Edit .env and fill in your SeatGeek client_id and client_secret
# Get credentials at: https://seatgeek.com/account/develop
```

**2. Install dependencies**

Only `requests` and `rich` are required — both are available in most Python 3 environments.

```bash
pip install requests rich
```

**3. Run manually to verify**

```bash
python3 main.py
```

**4. Set up the cron job**

```bash
crontab -e
```

Add this line (adjust path as needed):

```
0 */6 * * * /usr/bin/python3 /path/to/TicketPriceAnalyzer/main.py >> /path/to/TicketPriceAnalyzer/run.log 2>&1
```

## Viewing collected data

```bash
python3 view.py
```

Displays a per-event summary with current price, 30-day average, a sparkline trend chart, and a table of recent snapshots.

## File overview

| File | Purpose |
|---|---|
| `main.py` | Entry point — fetch, store, analyze, alert |
| `fetcher.py` | SeatGeek API calls |
| `db.py` | SQLite schema and read/write helpers |
| `analyzer.py` | Trend metrics (moving average, consecutive drops) |
| `alerter.py` | Alert condition checks and notification output |
| `config.py` | Credentials, target show details, alert thresholds |
| `view.py` | CLI dashboard for manual data inspection |

## Notes

- `prices.db`, `run.log`, `alerts.log`, and `.env` are gitignored and never committed
- SeatGeek's resale marketplace for this event may not have listings until closer to the show date (~2–3 months out). The cron job will collect `null` snapshots until then, and the analysis will begin automatically once prices populate.
- Alerts are logged to `alerts.log` in addition to stdout. To add email or push notifications, extend the `notify()` function in `alerter.py`.
