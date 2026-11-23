"""SQLite persistence and SQL queries used for reporting."""
import sqlite3
import pandas as pd


def save(conn: sqlite3.Connection, clean_df: pd.DataFrame, kpis: pd.DataFrame) -> None:
    clean_df.assign(timestamp=clean_df["timestamp"].astype(str)).to_sql(
        "measurements", conn, if_exists="replace", index=False)
    kpis.assign(hour=kpis["hour"].astype(str)).to_sql("device_kpis", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kpi_device ON device_kpis(device_id)")
    conn.commit()


WORST_DEVICES_SQL = """
SELECT device_id, region,
       ROUND(AVG(p95_latency_ms), 1)      AS avg_p95_latency_ms,
       ROUND(AVG(avg_packet_loss_pct), 2) AS avg_loss_pct,
       ROUND(AVG(availability_pct), 2)    AS availability_pct,
       SUM(sla_breach)                    AS sla_breach_hours
FROM device_kpis
GROUP BY device_id, region
ORDER BY sla_breach_hours DESC, avg_p95_latency_ms DESC
LIMIT ?
"""

REGION_SUMMARY_SQL = """
SELECT region,
       ROUND(AVG(avg_latency_ms), 1)      AS avg_latency_ms,
       ROUND(AVG(avg_packet_loss_pct), 2) AS avg_loss_pct,
       ROUND(AVG(avg_throughput_mbps), 0) AS avg_throughput_mbps,
       ROUND(AVG(availability_pct), 2)    AS availability_pct,
       ROUND(100.0 * SUM(sla_breach) / COUNT(*), 1) AS sla_breach_hour_pct
FROM device_kpis
GROUP BY region
ORDER BY sla_breach_hour_pct DESC
"""

PEAK_HOURS_SQL = """
SELECT CAST(strftime('%H', hour) AS INTEGER) AS hour_of_day,
       ROUND(AVG(avg_latency_ms), 1) AS avg_latency_ms,
       ROUND(AVG(avg_packet_loss_pct), 2) AS avg_loss_pct
FROM device_kpis
GROUP BY hour_of_day
ORDER BY avg_latency_ms DESC
LIMIT 5
"""


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)
