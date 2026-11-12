"""Clean the team's Hai Bà Trưng apartment listings.

Input:  data/raw/hai_ba_trung_apartments_final.csv  (semicolon-separated, Vietnamese number format)
Output: data/apartments.csv
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hai_ba_trung_apartments_final.csv"
OUT = ROOT / "data" / "apartments.csv"

# Excel turned some street names into dates when the file was edited.
STREET_FIXES = {"08-Thg3": "8 Tháng 3"}


def vn_number(s):
    """'8.900.000.000' -> 8900000000.0 ; '107.228.915,66' -> 107228915.66"""
    return float(s.replace(".", "").replace(",", "."))


def clean(row):
    street = STREET_FIXES.get(row["street_name"].strip(), row["street_name"].strip())
    if not street or not row["bedroom_count"]:
        return None                                   # needed by the CSP
    price = vn_number(row["price_vnd"]) / 1e9          # billion VND
    area = vn_number(row["area_m2"])
    price_per_m2 = price * 1000 / area                 # million VND / m²
    # Drop typos: e.g. 4.5 million or 4,800 billion VND for one apartment.
    if not (20 <= price_per_m2 <= 300 and 15 <= area <= 400):
        return None
    return {
        "property_type": row["property_type_name"].strip(),
        "street": street,
        "project": row["project_name"].strip(),
        "price_billion_vnd": round(price, 3),
        "area_m2": area,
        "bedrooms": int(row["bedroom_count"]),
        "bathrooms": row["bathroom_count"].strip(),
        "title": row["name"].strip(),
    }


def main():
    with open(RAW, encoding="utf-8-sig", newline="") as f:
        raw = list(csv.DictReader(f, delimiter=";"))
    rows = [c for c in map(clean, raw) if c]
    # Same title + price + area = the same listing posted twice.
    unique = list({(r["title"], r["price_billion_vnd"], r["area_m2"]): r for r in rows}.values())
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", *unique[0]])
        w.writeheader()
        for i, r in enumerate(unique):
            w.writerow({"id": i, **r})
    print(f"{len(raw)} raw -> {len(rows)} clean -> {len(unique)} unique rows in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
