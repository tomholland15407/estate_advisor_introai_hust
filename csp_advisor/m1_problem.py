"""
MODULE 1 — PHÁT BIỂU BÀI TOÁN & ĐỊNH NGHĨA TRẠNG THÁI (Thành viên 1)

Bài toán: Một gia đình ở Hà Nội cần mua nhà cho NHIỀU người (con gái, con trai, bố mẹ, ông bà).
Mỗi người có yêu cầu riêng (ngân sách, diện tích, số phòng ngủ, quận mong muốn),
và giữa các người có ràng buộc chung (bố mẹ muốn ở GẦN các con, tổng tiền không vượt
ngân sách gia đình, không ai mua trùng một căn).

Phát biểu dưới dạng CSP (Constraint Satisfaction Problem) gồm 3 thành phần:
    X (Variables)   : mỗi người cần nhà là 1 biến            -> "Con gái", "Con trai", "Bố mẹ", "Ông bà"
    D (Domains)     : miền giá trị của mỗi biến = các căn nhà -> id của các căn trong dataset
    C (Constraints) : các ràng buộc (xem chi tiết ở Module 2)
"""

import csv
import random
from pathlib import Path

# Đường dẫn tới dataset thật (1.500 căn nhà ở 12 quận nội thành Hà Nội)
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "hanoi_houses.csv"

# ---------------------------------------------------------------------------
# 1. BẢN ĐỒ QUẬN GIÁP RANH (dùng cho ràng buộc "ở gần nhau")
#    Hai quận được coi là "gần" nếu là cùng một quận hoặc giáp ranh nhau.
#    Đây là bản đồ đơn giản hoá (theo địa giới cũ, có tính các cầu qua sông Hồng).
# ---------------------------------------------------------------------------
ADJACENT_DISTRICTS = {
    "Ba Đình":      {"Hoàn Kiếm", "Tây Hồ", "Cầu Giấy", "Đống Đa"},
    "Hoàn Kiếm":    {"Ba Đình", "Đống Đa", "Hai Bà Trưng", "Long Biên"},
    "Tây Hồ":       {"Ba Đình", "Cầu Giấy", "Bắc Từ Liêm"},
    "Long Biên":    {"Hoàn Kiếm", "Hai Bà Trưng", "Hoàng Mai"},
    "Cầu Giấy":     {"Ba Đình", "Tây Hồ", "Đống Đa", "Thanh Xuân", "Nam Từ Liêm", "Bắc Từ Liêm"},
    "Đống Đa":      {"Ba Đình", "Hoàn Kiếm", "Hai Bà Trưng", "Thanh Xuân", "Cầu Giấy"},
    "Hai Bà Trưng": {"Hoàn Kiếm", "Đống Đa", "Hoàng Mai", "Long Biên"},
    "Hoàng Mai":    {"Hai Bà Trưng", "Thanh Xuân", "Long Biên"},
    "Thanh Xuân":   {"Đống Đa", "Cầu Giấy", "Nam Từ Liêm", "Hà Đông", "Hoàng Mai"},
    "Nam Từ Liêm":  {"Cầu Giấy", "Bắc Từ Liêm", "Thanh Xuân", "Hà Đông"},
    "Bắc Từ Liêm":  {"Tây Hồ", "Cầu Giấy", "Nam Từ Liêm"},
    "Hà Đông":      {"Thanh Xuân", "Nam Từ Liêm"},
}


def are_near(district_a, district_b):
    """Trả về True nếu 2 quận trùng nhau hoặc giáp ranh."""
    return district_a == district_b or district_b in ADJACENT_DISTRICTS.get(district_a, set())


# ---------------------------------------------------------------------------
# 2. YÊU CẦU CỦA TỪNG NGƯỜI (đầu vào của người dùng) — có thể sửa tuỳ ý
#    districts = None nghĩa là "quận nào cũng được"
# ---------------------------------------------------------------------------
# Thứ tự khai báo ở đây = thứ tự gán biến khi KHÔNG dùng MRV.
REQUIREMENTS = {
    "Con gái":  {"max_price": 4.0, "min_area": 30, "min_bedrooms": 2,
                 "districts": None},
    "Con trai": {"max_price": 4.5, "min_area": 35, "min_bedrooms": 2,
                 "districts": ["Cầu Giấy", "Thanh Xuân", "Nam Từ Liêm"]},
    "Bố mẹ":    {"max_price": 7.0, "min_area": 50, "min_bedrooms": 3,
                 "districts": ["Đống Đa", "Ba Đình", "Hai Bà Trưng"]},
    "Ông bà":   {"max_price": 6.0, "min_area": 40, "min_bedrooms": 2,
                 "districts": ["Hoàn Kiếm", "Ba Đình", "Tây Hồ"]},
}

# Các cặp người phải ở GẦN nhau (ràng buộc nhị phân - binary constraint)
NEAR_PAIRS = [
    ("Bố mẹ", "Con trai"),
    ("Bố mẹ", "Con gái"),
    ("Bố mẹ", "Ông bà"),
    ("Con gái", "Ông bà"),     # con gái muốn tiện qua chăm ông bà
]

# Tổng ngân sách cả gia đình (tỷ VND) - ràng buộc toàn cục (global constraint)
# 8.5 tỷ: có lời giải nhưng khó tìm. Thử 8.0: KHÔNG có lời giải.
TOTAL_BUDGET = 8.5


# ---------------------------------------------------------------------------
# 3. ĐỌC DỮ LIỆU
# ---------------------------------------------------------------------------
def load_houses(path=None):
    """Đọc file CSV, trả về dict {id: căn_nhà}. Mỗi căn nhà là 1 dict."""
    path = path or DATA_FILE
    if not Path(path).exists():
        print(f"[!] Không tìm thấy {path}, dùng dữ liệu giả lập.")
        return make_synthetic_houses()

    houses = {}
    with open(path, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):   # mỗi dòng CSV -> 1 dict
            houses[i] = {                              # id của căn nhà = số thứ tự dòng
                "id": i,
                "district": row["district"],
                "price": float(row["price_billion_vnd"]),   # đổi chuỗi -> số thực
                "area": float(row["area_m2"]),
                "bedrooms": int(row["bedrooms"]),            # đổi chuỗi -> số nguyên
            }
    return houses


def make_synthetic_houses(n=300, seed=42):
    """Sinh dữ liệu giả để code vẫn chạy được khi thiếu file CSV."""
    rng = random.Random(seed)
    districts = list(ADJACENT_DISTRICTS)
    houses = {}
    for i in range(n):
        area = rng.randint(20, 120)
        houses[i] = {"id": i, "district": rng.choice(districts),
                     "price": round(area * rng.uniform(0.06, 0.15), 2),  # 60–150 triệu/m²
                     "area": float(area), "bedrooms": rng.randint(1, 6)}
    return houses


# ---------------------------------------------------------------------------
# 4. CẤU TRÚC CSP
# ---------------------------------------------------------------------------
class CSP:
    def __init__(self, houses, requirements, near_pairs, total_budget):
        self.houses = houses                       # tra cứu thông tin căn nhà theo id
        self.requirements = requirements           # ràng buộc đơn (unary) của từng biến
        self.near_pairs = near_pairs               # ràng buộc nhị phân "ở gần"
        self.total_budget = total_budget           # ràng buộc toàn cục về tiền

        # X: danh sách biến
        self.variables = list(requirements)

        # D: ban đầu MỖI biến có thể nhận BẤT KỲ căn nhà nào (sẽ được lọc ở Module 2)
        self.domains = {var: list(houses) for var in self.variables}

        # Đồ thị ràng buộc (constraint graph): nối 2 biến nếu có ràng buộc "ở gần"
        self.neighbors = {var: set() for var in self.variables}
        for a, b in near_pairs:
            self.neighbors[a].add(b)
            self.neighbors[b].add(a)


def build_csp(total_budget=TOTAL_BUDGET):
    """Tạo một bài toán CSP mới (domain đầy đủ, chưa lọc)."""
    return CSP(load_houses(), REQUIREMENTS, NEAR_PAIRS, total_budget)
