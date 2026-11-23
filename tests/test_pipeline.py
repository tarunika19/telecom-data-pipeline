import sqlite3
from telecom_pipeline.cli import run


def test_end_to_end(tmp_path):
    db, rep = tmp_path / "n.db", tmp_path / "r.md"
    assert run(str(db), str(rep), n_devices=5, hours=12, seed=3) == 0
    with sqlite3.connect(db) as c:
        tables = {r[0] for r in c.execute("select name from sqlite_master where type='table'")}
        assert {"measurements", "device_kpis"} <= tables
        n = c.execute("select count(*) from device_kpis").fetchone()[0]
        assert n == 5 * 12
    text = rep.read_text()
    assert "Regional summary" in text and "Top 5 devices" in text


def test_deterministic_with_seed(tmp_path):
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    run(str(tmp_path / "a.db"), str(a), 4, 6, 9)
    run(str(tmp_path / "b.db"), str(b), 4, 6, 9)
    assert a.read_text() == b.read_text()
