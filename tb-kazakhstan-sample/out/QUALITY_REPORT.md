# Data quality report: KAZ, 2000-2025

Generated 2026-11-13T19:52:36+00:00 by tb_pipeline.py. Official values only; nothing interpolated or filled.

## Coverage by series

| source | indicator | variable | years with value | first | last | missing years |
|---|---|---|---|---|---|---|
| WHO GHO | MDG_0000000017 | tb_mortality_hivneg_per_100k | 26/26 | 2000 | 2025 | none |
| WHO GHO | MDG_0000000020 | tb_incidence_per_100k | 26/26 | 2000 | 2025 | none |
| WHO GHO | TB_1 | tb_treatment_coverage_pct | 26/26 | 2000 | 2025 | none |
| WHO GHO | TB_c_newinc | tb_notified_new_relapse | 26/26 | 2000 | 2025 | none |
| WHO GHO | TB_e_inc_num | tb_incident_cases | 26/26 | 2000 | 2025 | none |
| WHO GHO | TB_e_inc_rr_num | rr_tb_incident_cases | 11/26 | 2015 | 2025 | 15 years (2000..2014) |
| WHO GHO | TB_e_mort_exc_tbhiv_num | tb_deaths_hivneg | 26/26 | 2000 | 2025 | none |
| World Bank WDI | NY.GDP.PCAP.CD | gdp_per_capita_usd | 26/26 | 2000 | 2025 | none |
| World Bank WDI | SH.TBS.CURE.ZS | tb_treatment_success_pct | 24/26 | 2000 | 2023 | 2024, 2025 |
| World Bank WDI | SH.TBS.DTEC.ZS | tb_case_detection_pct | 25/26 | 2000 | 2024 | 2025 |
| World Bank WDI | SH.TBS.INCD | tb_incidence_per_100k | 25/26 | 2000 | 2024 | 2025 |
| World Bank WDI | SH.XPD.CHEX.GD.ZS | health_expenditure_pct_gdp | 24/26 | 2000 | 2023 | 2024, 2025 |
| World Bank WDI | SP.POP.TOTL | population_total | 26/26 | 2000 | 2025 | none |

## Integrity checks

- Duplicate (country, year, source, indicator) keys: 0
- Negative values: 0
- Rows where value is outside its own [low, high] interval: 0

## Cross-source check: TB incidence per 100k (WHO GHO vs World Bank)

- Overlapping years: 25; identical: 24; max absolute difference: 1

| year | WHO | World Bank | abs diff |
|---|---|---|---|
| 2024 | 46 | 45 | 1 |

## Request log

| UTC time | status | bytes | sha256 (first 16) | URL |
|---|---|---|---|---|
| 2026-11-13T19:47:35+00:00 | 200 | 15250 | af1960e8ac922bf5 | https://ghoapi.azureedge.net/api/MDG_0000000020?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:36+00:00 | 200 | 15636 | 25494fb1dd4acf25 | https://ghoapi.azureedge.net/api/TB_e_inc_num?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:37+00:00 | 200 | 15166 | a2d407aa997de38d | https://ghoapi.azureedge.net/api/MDG_0000000017?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:38+00:00 | 200 | 15651 | bc88f51b291140a6 | https://ghoapi.azureedge.net/api/TB_e_mort_exc_tbhiv_num?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:39+00:00 | 200 | 14630 | 8c4953a49ff6bd1a | https://ghoapi.azureedge.net/api/TB_c_newinc?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:40+00:00 | 200 | 14944 | e390f9baa70fb140 | https://ghoapi.azureedge.net/api/TB_1?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:41+00:00 | 200 | 87 | e611df4e6b8346df | https://ghoapi.azureedge.net/api/TB_c_new_tsr?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:47:42+00:00 | 200 | 6612 | 11db98aef849b2cb | https://ghoapi.azureedge.net/api/TB_e_inc_rr_num?$filter=SpatialDim%20eq%20%27KAZ%27%20and%20TimeDim%20ge%202000%20and%20TimeDim%20le%202025 |
| 2026-11-13T19:48:37+00:00 | 200 | 5880 | 504ef0df2bac0976 | https://api.worldbank.org/v2/country/KAZ/indicator/SH.TBS.INCD?format=json&date=2000:2025&per_page=200 |
| 2026-11-13T19:49:34+00:00 | 200 | 5970 | 9db985b8ea4253a6 | https://api.worldbank.org/v2/country/KAZ/indicator/SH.TBS.DTEC.ZS?format=json&date=2000:2025&per_page=200 |
| 2026-11-13T19:50:33+00:00 | 200 | 6102 | e39576737a3308f9 | https://api.worldbank.org/v2/country/KAZ/indicator/SH.TBS.CURE.ZS?format=json&date=2000:2025&per_page=200 |
| 2026-11-13T19:51:10+00:00 | 200 | 5266 | cfb4d3b47bc11746 | https://api.worldbank.org/v2/country/KAZ/indicator/SP.POP.TOTL?format=json&date=2000:2025&per_page=200 |
| 2026-11-13T19:51:49+00:00 | 200 | 5836 | 89caad54bcf089d7 | https://api.worldbank.org/v2/country/KAZ/indicator/NY.GDP.PCAP.CD?format=json&date=2000:2025&per_page=200 |
| 2026-11-13T19:52:36+00:00 | 200 | 5980 | a2c928efa2f84c90 | https://api.worldbank.org/v2/country/KAZ/indicator/SH.XPD.CHEX.GD.ZS?format=json&date=2000:2025&per_page=200 |
