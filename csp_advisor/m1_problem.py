"""
MODULE 1 — PHÁT BIỂU BÀI TOÁN & ĐỊNH NGHĨA TRẠNG THÁI (Thành viên 1)

Bài toán: Một gia đình cần mua căn hộ ở quận Hai Bà Trưng cho NHIỀU người
(con gái, con trai, bố mẹ, ông bà). Mỗi người có yêu cầu riêng (ngân sách, diện tích,
số phòng ngủ, loại căn hộ), và giữa các người có ràng buộc chung (một số người muốn ở
CÙNG PHỐ để tiện qua lại, tổng tiền không vượt ngân sách gia đình, không ai mua trùng căn).

Phát biểu dưới dạng CSP (Constraint Satisfaction Problem) gồm 3 thành phần:
    X (Variables)   : mỗi người cần nhà là 1 biến            -> "Con gái", "Con trai", "Bố mẹ", "Ông bà"
    D (Domains)     : miền giá trị của mỗi biến = các căn hộ -> id của các căn trong dataset
    C (Constraints) : các ràng buộc (xem chi tiết ở Module 2)
"""

import csv
import random
from pathlib import Path

# Đường dẫn tới dataset của nhóm (1.678 căn hộ ở quận Hai Bà Trưng, tin đăng năm 2025)
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "apartments.csv"

# ---------------------------------------------------------------------------
# 1. YÊU CẦU CỦA TỪNG NGƯỜI (đầu vào của người dùng) — có thể sửa tuỳ ý
#    types   = loại căn hộ chấp nhận ("Căn hộ chung cư", "Nhà tập thể"); None = loại nào cũng được
#    streets = các phố mong muốn; None = phố nào cũng được
# ---------------------------------------------------------------------------
# Thứ tự khai báo ở đây = thứ tự gán biến khi KHÔNG dùng MRV.
REQUIREMENTS = {
    "Con gái":  {"max_price": 5.0, "min_area": 40, "min_bedrooms": 2,
                 "types": None, "streets": None},
    "Con trai": {"max_price": 7.0, "min_area": 60, "min_bedrooms": 2,
                 "types": ["Căn hộ chung cư"], "streets": None},
    "Bố mẹ":    {"max_price": 9.0, "min_area": 70, "min_bedrooms": 3,
                 "types": None, "streets": None},
    "Ông bà":   {"max_price": 5.0, "min_area": 50, "min_bedrooms": 2,
                 "types": ["Nhà tập thể"], "streets": None},
}

# Các cặp người phải ở CÙNG PHỐ (ràng buộc nhị phân - binary constraint)
SAME_STREET_PAIRS = [
    ("Bố mẹ", "Ông bà"),
    ("Bố mẹ", "Con gái"),
]

# Tổng ngân sách cả gia đình (tỷ VND) - ràng buộc toàn cục (global constraint)
# 11 tỷ: có lời giải nhưng khó tìm. Thử 8.0: KHÔNG có lời giải.
TOTAL_BUDGET = 11.0


# ---------------------------------------------------------------------------
# 2. ĐỌC DỮ LIỆU
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
            houses[i] = {                              # id của căn hộ = số thứ tự dòng
                "id": i,
                "type": row["property_type"],
                "street": row["street"],
                "project": row["project"],
                "price": float(row["price_billion_vnd"]),   # đổi chuỗi -> số thực
                "area": float(row["area_m2"]),
                "bedrooms": int(row["bedrooms"]),            # đổi chuỗi -> số nguyên
            }
    return houses


def make_synthetic_houses(n=300, seed=42):
    """Sinh dữ liệu giả để code vẫn chạy được khi thiếu file CSV."""
    rng = random.Random(seed)
    streets = ["Minh Khai", "Lò Đúc", "Bạch Mai", "Thanh Nhàn", "Kim Ngưu"]
    houses = {}
    for i in range(n):
        area = rng.randint(30, 130)
        kind = rng.choice(["Căn hộ chung cư", "Nhà tập thể"])
        houses[i] = {"id": i, "type": kind, "street": rng.choice(streets), "project": "",
                     "price": round(area * rng.uniform(0.04, 0.12), 2),  # 40–120 triệu/m²
                     "area": float(area), "bedrooms": rng.randint(1, 4)}
    return houses


# ---------------------------------------------------------------------------
# 3. CẤU TRÚC CSP
# ---------------------------------------------------------------------------
class CSP:
    def __init__(self, houses, requirements, same_street_pairs, total_budget):
        self.houses = houses                       # tra cứu thông tin căn hộ theo id
        self.requirements = requirements           # ràng buộc đơn (unary) của từng biến
        self.same_street_pairs = same_street_pairs # ràng buộc nhị phân "cùng phố"
        self.total_budget = total_budget           # ràng buộc toàn cục về tiền

        # X: danh sách biến
        self.variables = list(requirements)

        # D: ban đầu MỖI biến có thể nhận BẤT KỲ căn hộ nào (sẽ được lọc ở Module 2)
        self.domains = {var: list(houses) for var in self.variables}

        # Đồ thị ràng buộc (constraint graph): nối 2 biến nếu có ràng buộc "cùng phố"
        self.neighbors = {var: set() for var in self.variables}
        for a, b in same_street_pairs:
            self.neighbors[a].add(b)
            self.neighbors[b].add(a)


def build_csp(total_budget=TOTAL_BUDGET):
    """Tạo một bài toán CSP mới (domain đầy đủ, chưa lọc)."""
    return CSP(load_houses(), REQUIREMENTS, SAME_STREET_PAIRS, total_budget)
