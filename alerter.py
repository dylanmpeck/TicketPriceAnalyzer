import config


def check(metrics, event_title, event_date):
    """
    Evaluate alert conditions against current metrics.
    Returns (should_alert: bool, reason: str).
    """
    if metrics is None:
        return False, "no data yet"

    if metrics["data_age_days"] < config.MIN_DATA_DAYS:
        remaining = config.MIN_DATA_DAYS - metrics["data_age_days"]
        return False, f"still collecting baseline data ({remaining} days remaining)"

    if metrics["current_lowest"] is None or metrics["current_lowest"] < config.ABSOLUTE_FLOOR:
        return False, "current lowest price missing or below sanity floor"

    if metrics["pct_of_30d_avg"] is None:
        return False, "insufficient 30-day average data"

    if metrics["pct_of_30d_avg"] > config.PRICE_DROP_PCT:
        return False, (
            f"price ({metrics['current_lowest']:.0f}) is {metrics['pct_of_30d_avg']*100:.1f}% "
            f"of 30d avg — threshold is {config.PRICE_DROP_PCT*100:.0f}%"
        )

    if metrics["consecutive_drops"] < config.CONSECUTIVE_DROPS:
        return False, (
            f"only {metrics['consecutive_drops']} consecutive price drops "
            f"(need {config.CONSECUTIVE_DROPS})"
        )

    reason = (
        f"ALERT: {event_title} on {event_date}\n"
        f"  Current lowest:  ${metrics['current_lowest']:.0f}\n"
        f"  30-day avg low:  ${metrics['avg_30d_lowest']:.0f}\n"
        f"  Drop:            {(1 - metrics['pct_of_30d_avg'])*100:.1f}% below avg\n"
        f"  Consecutive drops: {metrics['consecutive_drops']}"
    )
    return True, reason


def notify(message):
    """Emit an alert. Extend this to send email/SMS/push as needed."""
    print(f"\n{'='*60}")
    print(message)
    print('='*60)

    with open("alerts.log", "a") as f:
        from datetime import datetime
        f.write(f"[{datetime.utcnow().isoformat()}] {message}\n\n")
