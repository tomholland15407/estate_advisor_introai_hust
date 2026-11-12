"""
MODULE 5 — BỘ GIẢI BACKTRACKING & CHƯƠNG TRÌNH CHÍNH (Thành viên 5)

Chạy:  python3 csp_advisor/m5_solver.py          (ngân sách mặc định 11 tỷ) 
       python3 csp_advisor/m5_solver.py 8.0      (thử ngân sách khác)

Backtracking search = tìm kiếm theo chiều sâu (DFS), mỗi tầng gán thêm 1 biến.
Nếu không còn giá trị hợp lệ cho một biến -> quay lui (backtrack) về biến trước.
"""

import sys
import time

from m1_problem import build_csp, TOTAL_BUDGET
from m2_constraints import apply_node_consistency, is_consistent
from m3_heuristics import select_unassigned_variable, order_domain_values
from m4_inference import forward_check, restore


def backtracking_search(csp, use_mrv=True, use_lcv=True, use_fc=True):
    """Hàm bao: khởi tạo thống kê rồi gọi hàm đệ quy."""
    stats = {"nodes": 0, "backtracks": 0, "pruned": 0}
    options = {"mrv": use_mrv, "lcv": use_lcv, "fc": use_fc}
    result = backtrack({}, csp, options, stats)
    return result, stats


def backtrack(assignment, csp, options, stats):
    # 1. ĐIỀU KIỆN DỪNG: mọi biến đã được gán -> tìm được lời giải
    if len(assignment) == len(csp.variables):
        return dict(assignment)

    # 2. Chọn biến tiếp theo (Module 3)
    var = select_unassigned_variable(csp, assignment, options["mrv"])

    # 3. Thử lần lượt từng giá trị theo thứ tự (Module 3)
    for value in order_domain_values(csp, var, assignment, options["lcv"]):
        stats["nodes"] += 1                               # mỗi lần thử = 1 node

        # 4. Kiểm tra ràng buộc (Module 2)
        if not is_consistent(csp, assignment, var, value):
            continue

        assignment[var] = value                          # gán thử
        removed, ok = [], True
        if options["fc"]:                                # 5. Suy diễn (Module 4)
            removed, ok = forward_check(csp, assignment, var)
            stats["pruned"] += len(removed)

        if ok:                                           # 6. Đệ quy sang biến tiếp theo
            result = backtrack(assignment, csp, options, stats)
            if result is not None:
                return result

        restore(csp, removed)                            # 7. Hoàn tác khi thất bại
        del assignment[var]

    stats["backtracks"] += 1                             # hết giá trị -> quay lui
    return None


# ---------------------------------------------------------------------------
# CHƯƠNG TRÌNH CHÍNH
# ---------------------------------------------------------------------------
def print_solution(csp, solution):
    total = 0
    for var in csp.variables:
        h = csp.houses[solution[var]]
        total += h["price"]
        print(f"  {var:<9}-> căn #{h['id']:<4} {h['type']:<16} phố {h['street']:<14} "
              f"{h['price']:>5.2f} tỷ  {h['area']:>5.1f} m²  {h['bedrooms']} PN")
    print(f"  Tổng: {total:.2f} / {csp.total_budget} tỷ")


def main():
    # Đọc ngân sách từ dòng lệnh nếu có, ví dụ: python3 m5_solver.py 8.0
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else TOTAL_BUDGET

    # So sánh 4 cấu hình: từ backtracking "trần" đến đầy đủ heuristic
    configs = [
        ("Backtracking thuần",       dict(use_mrv=False, use_lcv=False, use_fc=False)),
        ("+ Forward Checking",       dict(use_mrv=False, use_lcv=False, use_fc=True)),
        ("+ FC + MRV/Degree",        dict(use_mrv=True,  use_lcv=False, use_fc=True)),
        ("+ FC + MRV/Degree + LCV",  dict(use_mrv=True,  use_lcv=True,  use_fc=True)),
    ]

    csp = build_csp(budget)
    print(f"Ngân sách gia đình: {budget} tỷ")
    print(f"Số căn hộ trong dữ liệu: {len(csp.houses)}")
    apply_node_consistency(csp)
    print("Domain sau khi lọc ràng buộc đơn (node consistency):")
    for var in csp.variables:
        print(f"  {var:<9}: {len(csp.domains[var])} căn")

    print(f"\n{'Cấu hình':<26}{'Nodes':>8}{'Quay lui':>10}{'Cắt tỉa':>9}{'Thời gian':>11}")
    best = None
    for name, opts in configs:
        csp = build_csp(budget)           # tạo CSP mới cho mỗi lần chạy (domain sạch)
        apply_node_consistency(csp)
        start = time.perf_counter()
        solution, stats = backtracking_search(csp, **opts)
        ms = (time.perf_counter() - start) * 1000
        print(f"{name:<26}{stats['nodes']:>8}{stats['backtracks']:>10}"
              f"{stats['pruned']:>9}{ms:>9.1f}ms")
        best = (csp, solution)

    csp, solution = best
    print("\nGợi ý căn hộ cho gia đình (cấu hình đầy đủ):")
    if solution is None:
        print("  Không có lời giải — thuật toán đã CHỨNG MINH không tồn tại cách chọn nào.")
        print("  Hãy tăng ngân sách hoặc nới lỏng yêu cầu trong m1_problem.py")
    else:
        print_solution(csp, solution)


if __name__ == "__main__":
    main()
