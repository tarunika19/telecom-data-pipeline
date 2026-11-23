"""KPI calculation per device and hour."""
import pandas as pd

SLA_P95_LATENCY_MS = 80
SLA_AVG_LOSS_PCT = 1.0


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    g = df.assign(hour=df["timestamp"].dt.floor("h")).groupby(["device_id", "region", "hour"])
    kpi = g.agg(
        samples=("timestamp", "size"),
        avg_latency_ms=("latency_ms", "mean"),
        p95_latency_ms=("latency_ms", lambda s: s.quantile(0.95)),
        avg_packet_loss_pct=("packet_loss_pct", "mean"),
        avg_throughput_mbps=("throughput_mbps", "mean"),
        availability_pct=("status", lambda s: (s == "up").mean() * 100),
    ).reset_index()
    kpi["sla_breach"] = (
        (kpi["p95_latency_ms"] > SLA_P95_LATENCY_MS) | (kpi["avg_packet_loss_pct"] > SLA_AVG_LOSS_PCT)
    ).astype(int)
    num = kpi.select_dtypes("number").columns
    kpi[num] = kpi[num].round(2)
    return kpi
