import numpy as np
from telecom_pipeline.validate import validate


def test_cleaned_data_passes(cleaned):
    assert validate(cleaned[0]).passed


def test_raw_dirty_data_fails(raw):
    import pandas as pd
    df = raw.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    assert not validate(df).passed


def test_missing_column_detected(cleaned):
    r = validate(cleaned[0].drop(columns=["latency_ms"]))
    assert not r.passed and "missing columns" in r.errors[0]


def test_out_of_range_detected(cleaned):
    df = cleaned[0].copy()
    df.loc[df.index[0], "packet_loss_pct"] = 101
    assert any("packet_loss_pct" in e for e in validate(df).errors)


def test_high_null_ratio_warns(cleaned):
    df = cleaned[0].copy()
    df.loc[df.index[: len(df) // 2], "throughput_mbps"] = np.nan
    r = validate(df)
    assert r.passed and any("throughput_mbps" in w for w in r.warnings)


def test_empty_frame_fails(cleaned):
    assert not validate(cleaned[0].iloc[0:0]).passed
