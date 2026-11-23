"""Cleaning: normalise formats, drop unusable rows, null out impossible values."""
import numpy as np
import pandas as pd

RANGES = {
    "latency_ms": (0, 5000),
    "packet_loss_pct": (0, 100),
    "throughput_mbps": (0, 100_000),
}


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (clean_df, stats). Input is not modified."""
    out = df.copy()
    stats = {"rows_in": len(out)}

    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out = out.dropna(subset=["device_id", "timestamp"])
    stats["dropped_missing_key"] = stats["rows_in"] - len(out)

    out["device_id"] = out["device_id"].str.strip().str.upper()
    out["region"] = out["region"].str.strip().str.title()
    out["status"] = out["status"].str.strip().str.lower()

    for col, (lo, hi) in RANGES.items():
        out[col] = pd.to_numeric(out[col], errors="coerce")
        bad = out[col].notna() & ~out[col].between(lo, hi)
        stats[f"invalid_{col}"] = int(bad.sum())
        out.loc[bad, col] = np.nan

    before = len(out)
    out = out.drop_duplicates(subset=["device_id", "timestamp"], keep="first")
    stats["dropped_duplicates"] = before - len(out)

    out = out.sort_values(["device_id", "timestamp"]).reset_index(drop=True)
    stats["rows_out"] = len(out)
    return out, stats
