#!/usr/bin/env python3
"""Reproducible TB data pipeline (sample): WHO GHO + World Bank -> harmonised Parquet + QA report.

Official data only. Missing values stay missing (no interpolation, no imputation).
Usage: python3 tb_pipeline.py [--country KAZ] [--start 2000] [--end 2025] [--out out]
"""
import argparse, hashlib, json, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

WHO_BASE = "https://ghoapi.azureedge.net/api"
WB_BASE = "https://api.worldbank.org/v2"

WHO_INDICATORS = {
    "MDG_0000000020": "tb_incidence_per_100k",
    "TB_e_inc_num": "tb_incident_cases",
    "MDG_0000000017": "tb_mortality_hivneg_per_100k",
    "TB_e_mort_exc_tbhiv_num": "tb_deaths_hivneg",
    "TB_c_newinc": "tb_notified_new_relapse",
    "TB_1": "tb_treatment_coverage_pct",
    "TB_c_new_tsr": "tb_treatment_success_new_pct",
    "TB_e_inc_rr_num": "rr_tb_incident_cases",
}
WB_INDICATORS = {
    "SH.TBS.INCD": "tb_incidence_per_100k",
    "SH.TBS.DTEC.ZS": "tb_case_detection_pct",
    "SH.TBS.CURE.ZS": "tb_treatment_success_pct",
    "SP.POP.TOTL": "population_total",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "SH.XPD.CHEX.GD.ZS": "health_expenditure_pct_gdp",
}
COLUMNS = ["country_iso3", "year", "variable", "value", "value_low", "value_high",
           "unit_note", "source", "source_indicator", "source_url", "retrieved_utc"]


def fetch(url, log, retries=2):
    """GET a JSON document; record URL, UTC time, HTTP Date header and SHA-256 of the body."""
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                body = r.read()
                log.append({"url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "http_status": r.status, "http_date": r.headers.get("Date"),
                            "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
                return json.loads(body)
        except Exception as exc:  # noqa: BLE001
            if attempt == retries:
                log.append({"url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "error": repr(exc)})
                return None
            time.sleep(2 * (attempt + 1))


def who_rows(country, start, end, log):
    rows = []
    for code, var in WHO_INDICATORS.items():
        flt = f"SpatialDim eq '{country}' and TimeDim ge {start} and TimeDim le {end}"
        url = f"{WHO_BASE}/{code}?$filter={urllib.parse.quote(flt)}"
        data = fetch(url, log)
        if data is None:
            continue
        stamp = log[-1]["retrieved_utc"]
        for rec in data.get("value", []):
            # keep only all-population rows; disaggregated rows are out of scope for this sample
            if rec.get("Dim1") not in (None, "", "SEX_BTSX") and rec.get("Dim1Type") not in (None, ""):
                continue
            rows.append({"country_iso3": rec["SpatialDim"], "year": rec["TimeDim"], "variable": var,
                         "value": rec.get("NumericValue"), "value_low": rec.get("Low"), "value_high": rec.get("High"),
                         "unit_note": rec.get("Value"), "source": "WHO GHO", "source_indicator": code,
                         "source_url": url, "retrieved_utc": stamp})
    return rows


def wb_rows(country, start, end, log):
    rows = []
    for code, var in WB_INDICATORS.items():
        url = f"{WB_BASE}/country/{country}/indicator/{code}?format=json&date={start}:{end}&per_page=200"
        data = fetch(url, log)
        if not data or len(data) < 2 or data[1] is None:
            continue
        stamp = log[-1]["retrieved_utc"]
        for rec in data[1]:
            rows.append({"country_iso3": rec["countryiso3code"], "year": int(rec["date"]), "variable": var,
                         "value": rec["value"], "value_low": None, "value_high": None,
                         "unit_note": rec["indicator"]["value"], "source": "World Bank WDI",
                         "source_indicator": code, "source_url": url, "retrieved_utc": stamp})
    return rows


def quality_report(df, start, end, log, country):
    years = list(range(start, end + 1))
    lines = [f"# Data quality report: {country}, {start}-{end}", "",
             f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by tb_pipeline.py. "
             "Official values only; nothing interpolated or filled.", "",
             "## Coverage by series", "",
             "| source | indicator | variable | years with value | first | last | missing years |",
             "|---|---|---|---|---|---|---|"]
    for (src, code, var), g in df.groupby(["source", "source_indicator", "variable"], sort=True):
        have = sorted(int(y) for y in g.loc[g["value"].notna(), "year"])
        miss = [y for y in years if y not in have]
        miss_s = ", ".join(map(str, miss)) if len(miss) <= 8 else f"{len(miss)} years ({miss[0]}..{miss[-1]})"
        lines.append(f"| {src} | {code} | {var} | {len(have)}/{len(years)} | {have[0] if have else 'n/a'} | "
                     f"{have[-1] if have else 'n/a'} | {miss_s or 'none'} |")
    dup = int(df.duplicated(["country_iso3", "year", "source", "source_indicator"]).sum())
    neg = int((df["value"] < 0).sum())
    lines += ["", "## Integrity checks", "",
              f"- Duplicate (country, year, source, indicator) keys: {dup}",
              f"- Negative values: {neg}",
              f"- Rows where value is outside its own [low, high] interval: "
              f"{int(((df['value'] < df['value_low']) | (df['value'] > df['value_high'])).sum())}"]
    # cross-source consistency: WHO vs World Bank incidence rate
    a = df[(df.source == "WHO GHO") & (df.variable == "tb_incidence_per_100k")].set_index("year")["value"]
    b = df[(df.source == "World Bank WDI") & (df.variable == "tb_incidence_per_100k")].set_index("year")["value"]
    both = pd.concat([a.rename("who"), b.rename("wb")], axis=1).dropna()
    lines += ["", "## Cross-source check: TB incidence per 100k (WHO GHO vs World Bank)", ""]
    if both.empty:
        lines.append("No overlapping years.")
    else:
        both["abs_diff"] = (both["who"] - both["wb"]).abs()
        lines.append(f"- Overlapping years: {len(both)}; identical: {int((both.abs_diff == 0).sum())}; "
                     f"max absolute difference: {both.abs_diff.max():g}")
        bad = both[both.abs_diff > 0]
        if not bad.empty:
            lines += ["", "| year | WHO | World Bank | abs diff |", "|---|---|---|---|"]
            lines += [f"| {y} | {r.who:g} | {r.wb:g} | {r.abs_diff:g} |" for y, r in bad.iterrows()]
    lines += ["", "## Request log", "", "| UTC time | status | bytes | sha256 (first 16) | URL |", "|---|---|---|---|---|"]
    for e in log:
        lines.append(f"| {e['retrieved_utc']} | {e.get('http_status', 'ERROR')} | {e.get('bytes', '')} | "
                     f"{e.get('sha256', e.get('error', ''))[:16]} | {e['url']} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="KAZ")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2025)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    log = []
    rows = who_rows(a.country, a.start, a.end, log) + wb_rows(a.country, a.start, a.end, log)
    if not rows:
        sys.exit("no data fetched; see request log")
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["year"] = df["year"].astype("int16")
    for c in ("value", "value_low", "value_high"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.sort_values(["source", "source_indicator", "year"]).reset_index(drop=True)
    df.to_parquet(out / "tb_long.parquet", index=False)
    df.to_csv(out / "tb_long.csv", index=False)
    wide = (df.assign(col=df["variable"] + "__" + df["source"].str.split().str[0].str.lower())
              .pivot_table(index=["country_iso3", "year"], columns="col", values="value", aggfunc="first")
              .reset_index())
    wide.columns.name = None
    wide.to_parquet(out / "tb_wide.parquet", index=False)
    (out / "request_log.json").write_text(json.dumps(log, indent=1))
    (out / "QUALITY_REPORT.md").write_text(quality_report(df, a.start, a.end, log, a.country))
    print(f"rows={len(df)} series={df.groupby(['source','source_indicator']).ngroups} "
          f"requests={len(log)} errors={sum('error' in e for e in log)}")


if __name__ == "__main__":
    main()
