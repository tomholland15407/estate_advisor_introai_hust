# Hanoi Real Estate Advisor

Project for the **Introduction to AI** class at HUST (Hanoi University of Science and Technology).

## Dataset

`data/hanoi_houses.csv` contains **1,500 houses** sold in Hanoi's 12 urban districts (listings from 2020–2021).

| Column | Type | Description |
|---|---|---|
| `district` | string | District name, e.g. `Cầu Giấy`, `Đống Đa` |
| `price_billion_vnd` | float | Total price in billion VND (area × listed price per m²) |
| `area_m2` | float | Land area in m² |
| `bedrooms` | int | Number of bedrooms (1–10) |

Median price is ~3.75 billion VND and median area ~40 m².

### How it was built

`python3 scripts/build_dataset.py` reads the raw listings in `data/raw/`, then:
1. strips the `Quận` prefix from district names,
2. converts the price per m² (triệu / tỷ / đ) to billion VND and multiplies by area,
3. drops listings with missing fields, "more than 10 bedrooms", area outside 15–500 m² or price outside 0.5–100 billion VND,
4. removes duplicates and takes a random sample of 1,500 (seed 42).

### Source & license

Raw data: [Vietnam Housing Dataset (Hanoi)](https://www.kaggle.com/datasets/ladcva/vietnam-housing-dataset-hanoi) by Le Anh Duc,
licensed [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The raw file in this repo is a subset (10,980 rows) taken from the
[NCT-NEU mirror](https://github.com/NCT-NEU/Sach_Khoa_hoc_du_lieu_python/tree/main/datasets). The derived dataset here is shared under the same license, for non-commercial use.
