"""
MODULE 2 — BỘ KIỂM TRA RÀNG BUỘC (Thành viên 2)

Có 3 loại ràng buộc trong bài toán:
  1. Unary  (đơn)     : chỉ liên quan 1 biến.   VD: nhà của "Bố mẹ" phải >= 3 phòng ngủ.
  2. Binary (nhị phân): liên quan 2 biến.       VD: nhà "Bố mẹ" phải gần nhà "Con trai".
  3. Global (toàn cục): liên quan nhiều biến.   VD: tổng tiền các căn <= ngân sách gia đình;
                                                    các người không được mua trùng 1 căn (AllDiff).
"""

from m1_problem import are_near


# ---------------------------------------------------------------------------
# 1. RÀNG BUỘC ĐƠN (UNARY)
# ---------------------------------------------------------------------------
def satisfies_unary(csp, var, house_id):
    """Căn nhà house_id có thoả yêu cầu riêng của người var không?"""
    house = csp.houses[house_id]
    req = csp.requirements[var]
    if house["price"] > req["max_price"]:              # vượt ngân sách cá nhân
        return False
    if house["area"] < req["min_area"]:                # quá nhỏ
        return False
    if house["bedrooms"] < req["min_bedrooms"]:        # thiếu phòng ngủ
        return False
    if req["districts"] is not None and house["district"] not in req["districts"]:
        return False                                   # không đúng quận mong muốn
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
    pair_is_near = (var_a, var_b) in csp.near_pairs or (var_b, var_a) in csp.near_pairs
    if pair_is_near:                           # nếu 2 người này phải ở gần nhau
        d_a = csp.houses[house_a]["district"]
        d_b = csp.houses[house_b]["district"]
        if not are_near(d_a, d_b):
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
