# Dataset

`apartments.csv` contains **1,678 apartment listings** in Hai Bà Trưng district, Hanoi (asking prices, listings from June–December 2025):
1,198 regular apartments (`Căn hộ chung cư`) and 480 collective apartments (`Nhà tập thể`) on 59 streets.

| Column | Type | Description |
|---|---|---|
| `id` | int | Row number, used as the apartment's id in the CSP |
| `property_type` | string | `Căn hộ chung cư` or `Nhà tập thể` |
| `street` | string | Street name, e.g. `Minh Khai`, `Lò Đúc` |
| `project` | string | Building / project name (empty for ~40% of rows) |
| `price_billion_vnd` | float | Asking price in billion VND |
| `area_m2` | float | Area in m² as listed (some rooftop/penthouse listings include terrace area) |
| `bedrooms` | int | Number of bedrooms |
| `bathrooms` | int or empty | Number of bathrooms |
| `title` | string | Original listing title |

Median price is ~7.0 billion VND (regular apartments ~8.8, collective apartments ~3.85) and median area 80 m².

## How it was built

A team member compiled `raw/hai_ba_trung_apartments_final.csv` (2,040 rows, semicolon-separated, Vietnamese number format).
`python3 scripts/build_dataset.py` (from the repo root) turns it into `apartments.csv`:
1. converts prices like `8.900.000.000` to billion VND,
2. fixes street names that Excel turned into dates (`08-Thg3` → `8 Tháng 3`),
3. drops rows with no street or no bedroom count (the CSP needs both),
4. drops typos: price per m² outside 20–300 million VND or area outside 15–400 m²,
5. removes listings posted twice (same title, price and area).

`ward_name` is not used because it is empty in about half of the raw rows; every row is in Hai Bà Trưng, so `district_name` is not used either.

## Source & license

The raw listings come from [Vietnam Real Estates](https://www.kaggle.com/datasets/yashdev01/vietnam-real-estates) on Kaggle by Yash,
licensed [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The files here are shared under the same license, for non-commercial use.
