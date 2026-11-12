"""
MODULE 3 — CÁC HÀM HEURISTIC (Thành viên 3)

Backtracking cần trả lời 2 câu hỏi ở mỗi bước:
  (1) Gán biến NÀO tiếp theo?         -> MRV, tie-break bằng Degree heuristic
  (2) Thử giá trị NÀO trước?           -> LCV (Least Constraining Value)

Nguyên tắc ghi nhớ:
  - Chọn BIẾN: "fail-first"   -> chọn biến khó nhất để phát hiện ngõ cụt sớm.
  - Chọn GIÁ TRỊ: "fail-last" -> chọn giá trị dễ chịu nhất để giữ nhiều lựa chọn cho biến khác.
"""

from m2_constraints import satisfies_binary


def select_unassigned_variable(csp, assignment, use_mrv=True):
    """Chọn biến chưa gán tiếp theo."""
    unassigned = [v for v in csp.variables if v not in assignment]

    if not use_mrv:
        return unassigned[0]               # không dùng heuristic: lấy theo thứ tự cố định

    def degree(var):
        # Degree = số biến CHƯA GÁN mà var có ràng buộc (cạnh trong constraint graph)
        return sum(1 for n in csp.neighbors[var] if n not in assignment)

    # MRV: domain nhỏ nhất trước. Nếu hoà -> biến có degree LỚN nhất (dấu trừ).
    return min(unassigned, key=lambda v: (len(csp.domains[v]), -degree(v)))


def order_domain_values(csp, var, assignment, use_lcv=True):
    """Sắp xếp các giá trị trong domain của var theo thứ tự nên thử."""
    if not use_lcv:
        return list(csp.domains[var])

    assigned_cost = sum(csp.houses[h]["price"] for h in assignment.values())
    others = [v for v in csp.variables if v not in assignment and v != var]

    def ruled_out(house_id):
        # Đếm xem nếu chọn house_id thì bao nhiêu giá trị của các biến khác bị loại
        remaining = csp.total_budget - assigned_cost - csp.houses[house_id]["price"]
        count = 0
        for other in others:
            for h in csp.domains[other]:
                if (not satisfies_binary(csp, var, house_id, other, h)
                        or csp.houses[h]["price"] > remaining):
                    count += 1
        return count

    # Ít loại nhất lên trước; nếu hoà thì căn rẻ hơn lên trước
    return sorted(csp.domains[var], key=lambda h: (ruled_out(h), csp.houses[h]["price"]))
