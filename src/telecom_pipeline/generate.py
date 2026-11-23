"""Synthetic network measurement data (with optional, realistic data-quality issues)."""
import numpy as np
import pandas as pd

REGIONS = ["Frankfurt", "Darmstadt", "Mainz", "Wiesbaden"]


def generate(n_devices: int = 20, hours: int = 48, seed: int = 42, dirty: bool = True) -> pd.DataFrame:
    """One measurement per device every 5 minutes."""
    rng = np.random.default_rng(seed)
    ts = pd.date_range("2026-01-01", periods=hours * 12, freq="5min")
    devices = [f"RTR-{i:03d}" for i in range(n_devices)]
    region_of = {d: REGIONS[i % len(REGIONS)] for i, d in enumerate(devices)}

    idx = pd.MultiIndex.from_product([devices, ts], names=["device_id", "timestamp"])
    df = idx.to_frame(index=False)
    n = len(df)
    df["region"] = df["device_id"].map(region_of)
    # daily load pattern: busier in the evening -> higher latency and loss
    load = 0.5 + 0.5 * np.sin((df["timestamp"].dt.hour - 14) / 24 * 2 * np.pi)
    df["latency_ms"] = rng.normal(25 + 30 * load, 6).clip(1)
    df["packet_loss_pct"] = rng.gamma(1.2, 0.15 + 0.4 * load).clip(0, 100)
    df["throughput_mbps"] = rng.normal(900 - 300 * load, 60).clip(10)
    df["status"] = np.where(rng.random(n) < 0.995, "up", "down")
    df.loc[df["status"] == "down", ["latency_ms", "throughput_mbps"]] = np.nan

    if dirty:
        k = max(1, n // 100)
        pick = lambda: rng.choice(n, k, replace=False)
        df.loc[pick(), "latency_ms"] = -1                      # impossible value
        df.loc[pick(), "packet_loss_pct"] = 150                # out of range
        df.loc[pick(), "throughput_mbps"] = np.nan             # missing
        i = pick()
        df.loc[i, "region"] = " " + df.loc[i, "region"].str.lower() + " "  # formatting
        df.loc[pick(), "status"] = "UP"                        # casing
        df.loc[pick(), "device_id"] = None                     # missing key
        df = pd.concat([df, df.sample(k, random_state=seed)], ignore_index=True)  # duplicates
        df["timestamp"] = df["timestamp"].astype(str)
    return df
