import pandas as pd
from telecom_pipeline.metrics import compute_kpis


def _frame(latencies, loss, status):
    n = len(latencies)
    return pd.DataFrame({
        "device_id": ["RTR-000"] * n, "region": ["Mainz"] * n,
        "timestamp": pd.date_range("2026-01-01 10:00", periods=n, freq="5min"),
        "latency_ms": latencies, "packet_loss_pct": loss,
        "throughput_mbps": [500.0] * n, "status": status,
    })


def test_hourly_aggregation():
    k = compute_kpis(_frame([10, 20, 30, 40], [0, 0, 0, 0], ["up"] * 4))
    assert len(k) == 1
    assert k.loc[0, "avg_latency_ms"] == 25.0
    assert k.loc[0, "availability_pct"] == 100.0
    assert k.loc[0, "sla_breach"] == 0


def test_availability_counts_down_samples():
    k = compute_kpis(_frame([10, 10, 10, 10], [0] * 4, ["up", "up", "up", "down"]))
    assert k.loc[0, "availability_pct"] == 75.0


def test_sla_breach_on_latency_and_loss():
    assert compute_kpis(_frame([200] * 4, [0] * 4, ["up"] * 4)).loc[0, "sla_breach"] == 1
    assert compute_kpis(_frame([10] * 4, [5] * 4, ["up"] * 4)).loc[0, "sla_breach"] == 1


def test_nan_values_ignored():
    k = compute_kpis(_frame([10, None, 30, None], [0] * 4, ["up"] * 4))
    assert k.loc[0, "avg_latency_ms"] == 20.0
