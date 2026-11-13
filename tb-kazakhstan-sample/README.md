# TB data pipeline sample: Kazakhstan, 2000–2025

A small working sample of a reproducible pipeline for tuberculosis statistics from official sources.

- **Sources:** WHO Global Health Observatory (OData API) and World Bank WDI (API v2). No keys needed.
- **Run:** `pip install pandas pyarrow && python3 tb_pipeline.py --country KAZ --start 2000 --end 2025`
- **Rule:** official values only. Missing years stay missing; nothing is interpolated or filled.

## Output (`out/`)

| File | What it is |
|---|---|
| `tb_long.parquet` / `tb_long.csv` | One row per country, year, source and indicator, with the value, its low/high bounds, source URL and retrieval time |
| `tb_wide.parquet` | One row per year, one column per variable and source |
| `QUALITY_REPORT.md` | Coverage per series, missing years, duplicate and range checks, WHO vs World Bank comparison, request log |
| `request_log.json` | Every request with UTC time, HTTP status, size and SHA-256 of the response |

## What the sample run found

- 13 series, 26 years each; 9 of them complete for 2000–2025.
- WHO and World Bank TB incidence agree in 24 of 25 overlapping years; 2024 differs by 1 per 100k (46 vs 45).
- Rifampicin-resistant TB incidence exists only from 2015.

Not in this sample: national sources of Kazakhstan and tables from PDF/DOCX files.
