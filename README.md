# Telecom Data Engineering Pipeline

Python, Pandas, SQL, SQLite, pytest.

Synthetic router measurements (latency, packet loss, throughput, status) with deliberately
injected data-quality problems are cleaned, validated, aggregated into hourly per-device KPIs,
stored in SQLite and summarised in a Markdown report.

```
generate -> clean -> validate -> metrics -> SQLite -> report
```

## Run
```bash
pip install -r requirements.txt
python -m telecom_pipeline            # writes output/network.db and output/report.md
pytest
```
Use `PYTHONPATH=src python -m telecom_pipeline` if running from the repo root without installing.

## Modules
| Module | Responsibility |
|---|---|
| `generate.py` | synthetic data, optional dirty rows (duplicates, nulls, impossible values, casing) |
| `clean.py` | normalisation, range checks (invalid -> NaN), de-duplication, cleaning stats |
| `validate.py` | schema, key, range, status and null-ratio checks; errors vs. warnings |
| `metrics.py` | hourly avg/p95 latency, loss, throughput, availability, SLA breach flag |
| `storage.py` | SQLite tables + SQL queries |
| `report.py` | Markdown report from SQL |

## Ideas for next steps
- Config file for SLA thresholds and ranges
- Anomaly detection (rolling z-score) on latency
- Incremental loads instead of table replace
- GitHub Actions running pytest, logging instead of print
