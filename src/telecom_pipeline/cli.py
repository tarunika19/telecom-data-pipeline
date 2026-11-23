"""Run the whole pipeline: generate -> clean -> validate -> KPIs -> SQLite -> report."""
import argparse
import sqlite3
import sys
from pathlib import Path

from .generate import generate
from .clean import clean
from .validate import validate
from .metrics import compute_kpis
from .storage import save
from .report import build_report


def run(db_path: str = "output/network.db", report_path: str = "output/report.md",
        n_devices: int = 20, hours: int = 48, seed: int = 42) -> int:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    raw = generate(n_devices, hours, seed)
    clean_df, stats = clean(raw)
    result = validate(clean_df)
    if not result.passed:
        print("Validation failed:", *result.errors, sep="\n  - ")
        return 1
    kpis = compute_kpis(clean_df)
    with sqlite3.connect(db_path) as conn:
        save(conn, clean_df, kpis)
        report = build_report(conn, stats, result.warnings)
    Path(report_path).write_text(report, encoding="utf-8")
    print(f"OK: {stats['rows_out']} rows, {len(kpis)} KPI rows -> {db_path}, {report_path}")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default="output/network.db")
    p.add_argument("--report", default="output/report.md")
    p.add_argument("--devices", type=int, default=20)
    p.add_argument("--hours", type=int, default=48)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    sys.exit(run(a.db, a.report, a.devices, a.hours, a.seed))


if __name__ == "__main__":
    main()
