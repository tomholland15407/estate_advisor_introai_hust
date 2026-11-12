"""
MODULE 4 — CẮT TỈA MIỀN GIÁ TRỊ & SUY DIỄN (Thành viên 4)

Forward Checking (FC): ngay sau khi gán var = value, nhìn "về phía trước" sang các biến
chưa gán và XOÁ khỏi domain của chúng những giá trị không còn hợp lệ.
  - Nếu domain của một biến bị xoá sạch -> chắc chắn ngõ cụt -> quay lui NGAY,
    không cần đi sâu thêm (tiết kiệm rất nhiều node).
  - Mọi giá trị bị xoá đều được GHI LẠI để khôi phục khi quay lui (restore).
"""

from m2_constraints import is_consistent


def forward_check(csp, assignment, var):
    """
    Gọi SAU khi đã gán assignment[var].
    Trả về (removed, ok):
      removed : danh sách (biến, giá_trị) đã bị xoá — để khôi phục sau
      ok      : False nếu có biến bị rỗng domain (ngõ cụt)
    """
    removed = []
    for other in csp.variables:
        if other in assignment:                       # chỉ xét biến CHƯA gán
            continue
        for house_id in list(csp.domains[other]):     # list(...) = duyệt trên bản sao
            if not is_consistent(csp, assignment, other, house_id):
                csp.domains[other].remove(house_id)   # cắt tỉa
                removed.append((other, house_id))     # ghi lại để khôi phục
        if not csp.domains[other]:                    # domain rỗng -> thất bại sớm
            return removed, False
    return removed, True


def restore(csp, removed):
    """Trả lại các giá trị đã bị forward_check xoá (dùng khi quay lui)."""
    touched = set()
    for var, house_id in removed:
        csp.domains[var].append(house_id)
        touched.add(var)
    for var in touched:
        csp.domains[var].sort()      # đưa domain về đúng thứ tự ban đầu (theo id)
