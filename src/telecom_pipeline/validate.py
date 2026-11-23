"""Validation: checks on the cleaned data. Returns a result instead of raising."""
from dataclasses import dataclass, field
import pandas as pd
from .clean import RANGES

REQUIRED = ["device_id", "timestamp", "region", "latency_ms", "packet_loss_pct", "throughput_mbps", "status"]
VALID_STATUS = {"up", "down"}


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


def validate(df: pd.DataFrame, max_null_ratio: float = 0.05) -> ValidationResult:
    r = ValidationResult()
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        r.errors.append(f"missing columns: {missing}")
        return r
    if df.empty:
        r.errors.append("dataframe is empty")
        return r

    if df[["device_id", "timestamp"]].isna().any().any():
        r.errors.append("null values in key columns")
    if df.duplicated(subset=["device_id", "timestamp"]).any():
        r.errors.append("duplicate (device_id, timestamp) rows")
    if not set(df["status"].dropna().unique()) <= VALID_STATUS:
        r.errors.append("unexpected status values")

    for col, (lo, hi) in RANGES.items():
        vals = df[col].dropna()
        if not vals.between(lo, hi).all():
            r.errors.append(f"{col} outside [{lo}, {hi}]")
        ratio = df[col].isna().mean()
        if ratio > max_null_ratio:
            r.warnings.append(f"{col}: {ratio:.1%} null (threshold {max_null_ratio:.0%})")
    return r
