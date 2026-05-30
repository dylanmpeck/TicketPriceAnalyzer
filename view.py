#!/usr/bin/env python3
"""
Usage: python3 view.py
Shows a price history table and trend sparkline for each tracked event.
"""
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich import box
import db
import analyzer

console = Console()

SPARK_CHARS = "▁▂▃▄▅▆▇█"

def sparkline(values):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    return "".join(SPARK_CHARS[round((v - lo) / span * (len(SPARK_CHARS) - 1))] for v in values)


def format_price(v):
    return f"${v:.0f}" if v is not None else "[dim]—[/dim]"


def render_event(event):
    rows = db.get_snapshots(event["event_id"])
    metrics = analyzer.analyze(event["event_id"])

    console.rule(f"[bold]{event['event_title']}[/bold]  ·  {event['event_date']}")

    # Summary line
    if metrics:
        age = metrics["data_age_days"]
        snap = metrics["snapshot_count"]
        current = format_price(metrics["current_lowest"])
        avg30 = format_price(metrics["avg_30d_lowest"])
        drops = metrics["consecutive_drops"]
        pct = f"{metrics['pct_of_30d_avg']*100:.1f}% of 30d avg" if metrics["pct_of_30d_avg"] else "—"
        console.print(
            f"  Data age: [cyan]{age}d[/cyan]  |  "
            f"Snapshots: [cyan]{snap}[/cyan]  |  "
            f"Current low: [green]{current}[/green]  |  "
            f"30d avg low: [yellow]{avg30}[/yellow]  |  "
            f"Pct of avg: [magenta]{pct}[/magenta]  |  "
            f"Consec drops: [red]{drops}[/red]"
        )
    else:
        console.print("  [dim]No data yet.[/dim]")

    # Sparkline of lowest prices
    prices = [r["lowest"] for r in rows if r["lowest"] is not None]
    if prices:
        spark = sparkline(prices)
        lo, hi = min(prices), max(prices)
        console.print(f"\n  Price trend (low ${lo:.0f} → high ${hi:.0f}):")
        console.print(f"  [cyan]{spark}[/cyan]  ({len(prices)} data points)\n")
    else:
        console.print()

    # Snapshot table — last 20 rows
    table = Table(box=box.SIMPLE_HEAD, show_footer=False)
    table.add_column("Fetched (UTC)", style="dim", min_width=22)
    table.add_column("Lowest",  justify="right", style="green")
    table.add_column("Average", justify="right", style="yellow")
    table.add_column("Median",  justify="right")
    table.add_column("Highest", justify="right", style="dim")
    table.add_column("Listings", justify="right", style="dim")

    display_rows = rows[-20:]
    if len(rows) > 20:
        table.add_row(f"[dim]… {len(rows)-20} earlier rows omitted …[/dim]", "", "", "", "", "")

    for r in display_rows:
        table.add_row(
            r["fetched_at"],
            format_price(r["lowest"]),
            format_price(r["average"]),
            format_price(r["median"]),
            format_price(r["highest"]),
            str(r["listing_count"]) if r["listing_count"] is not None else "[dim]—[/dim]",
        )

    console.print(table)


def main():
    events = db.get_known_events()
    if not events:
        console.print("[yellow]No data in database yet. Run main.py first.[/yellow]")
        return

    console.print()
    for event in events:
        render_event(event)
        console.print()


if __name__ == "__main__":
    main()
