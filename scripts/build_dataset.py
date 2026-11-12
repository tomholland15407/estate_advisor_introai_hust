"""Clean the raw Hanoi housing listings and sample 1,500 houses.

Input:  data/raw/HN_housing_price_raw.csv
Output: data/hanoi_houses.csv  (district, price_billion_vnd, area_m2, bedrooms)
"""
import csv
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "HN_housing_price_raw.csv"
OUT = ROOT / "data" / "hanoi_houses.csv"
SAMPLE_SIZE = 1500
SEED = 42


def vn_number(s):
    """Parse Vietnamese-formatted numbers: '93,27' -> 93.27, '1.250.000' -> 1250000."""
    s = s.strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    return float(s)


def price_per_m2_billion(s):
    m = re.match(r"\s*([\d.,]+)\s*(triệu|tỷ|đ)/m²", s)
    if not m:
        return None
    value, unit = vn_number(m.group(1)), m.group(2)
    return value * {"tỷ": 1, "triệu": 1e-3, "đ": 1e-9}[unit]


def clean(row):
    district = re.sub(r"^(Quận|Huyện|Thị xã)\s+", "", row["Quận"].strip())
    bed = re.match(r"\s*(\d+)\s*phòng", row["Số phòng ngủ"])
    area = re.match(r"\s*([\d.,]+)\s*m²", row["Diện tích"])
    ppm2 = price_per_m2_billion(row["Giá/m2"])
    if not (district and bed and area and ppm2):
        return None
    area = vn_number(area.group(1))
    bedrooms = int(bed.group(1))
    price = round(area * ppm2, 2)
    # Drop implausible listings / typos.
    if not (15 <= area <= 500 and 1 <= bedrooms <= 10 and 0.5 <= price <= 100):
        return None
    return {"district": district, "price_billion_vnd": price,
            "area_m2": area, "bedrooms": bedrooms}


def main():
    with open(RAW, encoding="utf-8-sig") as f:
        rows = [c for c in map(clean, csv.DictReader(f)) if c]
    unique = list({tuple(r.values()): r for r in rows}.values())
    random.Random(SEED).shuffle(unique)
    sample = sorted(unique[:SAMPLE_SIZE], key=lambda r: (r["district"], r["price_billion_vnd"]))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sample[0]))
        w.writeheader()
        w.writerows(sample)
    print(f"{len(rows)} clean rows, {len(unique)} unique -> wrote {len(sample)} to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
