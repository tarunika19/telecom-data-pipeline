"""Markdown network performance report built from SQL queries."""
import sqlite3
from .storage import query, WORST_DEVICES_SQL, REGION_SUMMARY_SQL, PEAK_HOURS_SQL


def build_report(conn: sqlite3.Connection, clean_stats: dict, warnings: list[str]) -> str:
    lines = ["# Network Performance Report", "", "## Data quality", ""]
    lines += [f"- {k.replace('_', ' ')}: {v}" for k, v in clean_stats.items()]
    lines += [f"- WARNING: {w}" for w in warnings]
    sections = [
        ("Regional summary", query(conn, REGION_SUMMARY_SQL)),
        ("Top 5 devices by SLA breach hours", query(conn, WORST_DEVICES_SQL, (5,))),
        ("Busiest hours of day (latency)", query(conn, PEAK_HOURS_SQL)),
    ]
    for title, df in sections:
        lines += ["", f"## {title}", "", df.to_markdown(index=False) if _has_tabulate() else df.to_string(index=False)]
    return "\n".join(lines) + "\n"


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False
