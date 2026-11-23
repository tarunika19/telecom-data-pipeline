import numpy as np
from telecom_pipeline.clean import clean


def test_no_duplicates_or_null_keys(cleaned):
    df, _ = cleaned
    assert not df.duplicated(["device_id", "timestamp"]).any()
    assert df[["device_id", "timestamp"]].notna().all().all()


def test_values_normalised(cleaned):
    df, _ = cleaned
    assert set(df["status"].unique()) <= {"up", "down"}
    assert all(r == r.strip().title() for r in df["region"].unique())
    assert df["device_id"].str.fullmatch(r"RTR-\d{3}").all()


def test_invalid_values_become_nan(cleaned):
    df, stats = cleaned
    assert stats["invalid_latency_ms"] > 0
    assert (df["latency_ms"].dropna() >= 0).all()
    assert (df["packet_loss_pct"].dropna() <= 100).all()


def test_stats_add_up(cleaned):
    _, s = cleaned
    assert s["rows_in"] - s["dropped_missing_key"] - s["dropped_duplicates"] == s["rows_out"]


def test_clean_does_not_mutate_input(raw):
    snapshot = raw.copy()
    clean(raw)
    assert raw.equals(snapshot)
