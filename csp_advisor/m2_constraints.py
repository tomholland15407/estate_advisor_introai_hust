"""
MODULE 2 — BỘ KIỂM TRA RÀNG BUỘC (Thành viên 2)

Có 3 loại ràng buộc trong bài toán:
  1. Unary  (đơn)     : chỉ liên quan 1 biến.   VD: căn của "Bố mẹ" phải >= 3 phòng ngủ.
  2. Binary (nhị phân): liên quan 2 biến.       VD: căn "Bố mẹ" phải cùng phố với căn "Ông bà".
  3. Global (toàn cục): liên quan nhiều biến.   VD: tổng tiền các căn <= ngân sách gia đình;
                                                    các người không được mua trùng 1 căn (AllDiff).
"""

# ---------------------------------------------------------------------------
# 1. RÀNG BUỘC ĐƠN (UNARY)
# ---------------------------------------------------------------------------
def satisfies_unary(csp, var, house_id):
    """Căn hộ house_id có thoả yêu cầu riêng của người var không?"""
    house = csp.houses[house_id]
    req = csp.requirements[var]
    if house["price"] > req["max_price"]:              # vượt ngân sách cá nhân
        return False
    if house["area"] < req["min_area"]:                # quá nhỏ
        return False
    if house["bedrooms"] < req["min_bedrooms"]:        # thiếu phòng ngủ
        return False
    if req["types"] is not None and house["type"] not in req["types"]:
        return False                                   # không đúng loại căn hộ
    if req["streets"] is not None and house["street"] not in req["streets"]:
        return False                                   # không đúng phố mong muốn
    return True


def apply_node_consistency(csp):
    """
    Node consistency: loại khỏi domain mọi giá trị vi phạm ràng buộc đơn.
    Làm 1 lần TRƯỚC khi tìm kiếm -> domain nhỏ đi rất nhiều -> tìm kiếm nhanh hơn.
    """
    for var in csp.variables:
        csp.domains[var] = [h for h in csp.domains[var] if satisfies_unary(csp, var, h)]


# ---------------------------------------------------------------------------
# 2. RÀNG BUỘC NHỊ PHÂN (BINARY)
# ---------------------------------------------------------------------------
def satisfies_binary(csp, var_a, house_a, var_b, house_b):
    """Hai lựa chọn (var_a = house_a) và (var_b = house_b) có hợp nhau không?"""
    if house_a == house_b:                     # AllDiff: 2 người không mua cùng 1 căn
        return False
    pairs = csp.same_street_pairs
    if (var_a, var_b) in pairs or (var_b, var_a) in pairs:   # 2 người này phải ở cùng phố
        if csp.houses[house_a]["street"] != csp.houses[house_b]["street"]:
            return False
    return True


# ---------------------------------------------------------------------------
# 3. RÀNG BUỘC TOÀN CỤC: TỔNG NGÂN SÁCH
# ---------------------------------------------------------------------------
def within_total_budget(csp, assignment, var, house_id):
    """Tổng giá các căn đã chọn (kể cả căn mới) có <= ngân sách gia đình không?"""
    total = csp.houses[house_id]["price"]
    for other_var, other_house in assignment.items():
        if other_var != var:
            total += csp.houses[other_house]["price"]
    return total <= csp.total_budget


# ---------------------------------------------------------------------------
# 4. HÀM TỔNG HỢP
# ---------------------------------------------------------------------------
def is_consistent(csp, assignment, var, house_id):
    """
    Gán var = house_id có hợp lệ với các biến ĐÃ GÁN trong assignment không?
    assignment là dict, ví dụ {"Bố mẹ": 12, "Con trai": 305}
    """
    if not satisfies_unary(csp, var, house_id):
        return False
    for other_var, other_house in assignment.items():      # so với từng biến đã gán
        if other_var == var:
            continue
        if not satisfies_binary(csp, var, house_id, other_var, other_house):
            return False
    return within_total_budget(csp, assignment, var, house_id)
