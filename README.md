# Hai Bà Trưng Apartment Advisor — Tư vấn mua căn hộ bằng CSP

> Bài tập lớn môn **Nhập môn Trí tuệ Nhân tạo** — Đại học Bách khoa Hà Nội (HUST).
> Repo này là **sổ tay hướng dẫn nội bộ** cho 5 thành viên trong nhóm. Repo nộp cho thầy/cô sẽ làm riêng.

---

## Mục lục

1. [Chạy thử trong 2 phút](#1-chạy-thử-trong-2-phút)
2. [Bài toán là gì?](#2-bài-toán-là-gì)
3. [Cấu trúc thư mục](#3-cấu-trúc-thư-mục)
4. [Bức tranh tổng thể: các module nối với nhau thế nào](#4-bức-tranh-tổng-thể)
5. [Kết quả thực nghiệm (con số để trình bày với thầy/cô)](#5-kết-quả-thực-nghiệm)
6. Hướng dẫn bảo vệ cho từng thành viên
   - [Thành viên 1 — Phát biểu bài toán](#thành-viên-1--module-1-phát-biểu-bài-toán--định-nghĩa-trạng-thái)
   - [Thành viên 2 — Kiểm tra ràng buộc](#thành-viên-2--module-2-bộ-kiểm-tra-ràng-buộc)
   - [Thành viên 3 — Heuristic](#thành-viên-3--module-3-các-hàm-heuristic)
   - [Thành viên 4 — Forward Checking](#thành-viên-4--module-4-cắt-tỉa-miền-giá-trị--forward-checking)
   - [Thành viên 5 — Backtracking & pipeline](#thành-viên-5--module-5-bộ-giải-backtracking--chương-trình-chính)
7. [Câu hỏi chung cả nhóm nên chuẩn bị](#7-câu-hỏi-chung-cả-nhóm-nên-chuẩn-bị)
8. [Mẹo khi thuyết trình](#8-mẹo-khi-thuyết-trình)

---

## 1. Chạy thử trong 2 phút

Chỉ cần **Python 3** (không cần cài thư viện nào).

```bash
git clone -b hai_ba_trung https://github.com/tomholland15407/estate_advisor_introai_hust.git
cd estate_advisor_introai_hust
python3 csp_advisor/m5_solver.py         # ngân sách mặc định 11 tỷ -> có lời giải
python3 csp_advisor/m5_solver.py 8.0     # ngân sách 8.0 tỷ -> chứng minh KHÔNG có lời giải
```

Kết quả mẫu (ngân sách 11 tỷ):

```
Domain sau khi lọc ràng buộc đơn (node consistency):
  Con gái  : 504 căn
  Con trai : 270 căn
  Bố mẹ    : 366 căn
  Ông bà   : 375 căn

Cấu hình                     Nodes  Quay lui  Cắt tỉa  Thời gian
Backtracking thuần          312093       844        0    101.4ms
+ Forward Checking             848        59   105473     62.1ms
+ FC + MRV/Degree              274        13    78889     33.9ms
+ FC + MRV/Degree + LCV          4         0      838     62.9ms

Gợi ý căn hộ cho gia đình (cấu hình đầy đủ):
  Con gái  -> căn #1186 Căn hộ chung cư  phố Lò Đúc          2.25 tỷ  100.0 m²  2 PN
  Con trai -> căn #794  Căn hộ chung cư  phố Thọ Lão         2.00 tỷ  100.0 m²  2 PN
  Bố mẹ    -> căn #1435 Nhà tập thể      phố Lò Đúc          3.78 tỷ   75.0 m²  3 PN
  Ông bà   -> căn #818  Nhà tập thể      phố Lò Đúc          2.40 tỷ   50.0 m²  3 PN
  Tổng: 10.43 / 11.0 tỷ
```

(Thời gian chạy trên máy mỗi người sẽ khác, nhưng số **Nodes**, **Quay lui**, **Cắt tỉa** thì luôn giống nhau.)


### Chuyển giữa 2 phiên bản (branch)

Repo có 2 branch, mỗi branch là một phiên bản đầy đủ (code + dữ liệu + hướng dẫn):

| Branch | Dữ liệu |
|---|---|
| `hanoi` | 1.500 căn nhà ở 12 quận nội thành Hà Nội (2020–2021) |
| `hai_ba_trung` | 1.678 căn hộ ở quận Hai Bà Trưng (2025), do nhóm tổng hợp |

```bash
git branch                 # xem đang ở branch nào (có dấu *)
git switch hai_ba_trung    # chuyển sang phiên bản Hai Bà Trưng
git switch hanoi           # chuyển sang phiên bản Hà Nội
```

Sau khi chuyển, các file trong thư mục tự thay đổi theo branch. Nếu Git báo lỗi vì bạn đã sửa file, chạy `git stash` trước rồi chuyển lại.

---

## 2. Bài toán là gì?

Một gia đình muốn mua **4 căn hộ ở quận Hai Bà Trưng** cho 4 nhóm người: **Con gái, Con trai, Bố mẹ, Ông bà**.

**Yêu cầu riêng của từng người** (ràng buộc đơn — *unary*):

| Người | Giá tối đa | Diện tích tối thiểu | Phòng ngủ tối thiểu | Loại căn hộ |
|---|---|---|---|---|
| Con gái | 5.0 tỷ | 40 m² | 2 | Loại nào cũng được |
| Con trai | 7.0 tỷ | 60 m² | 2 | Chỉ căn hộ chung cư |
| Bố mẹ | 9.0 tỷ | 70 m² | 3 | Loại nào cũng được |
| Ông bà | 5.0 tỷ | 50 m² | 2 | Chỉ nhà tập thể |

(Trong `m1_problem.py` mỗi người còn có mục `streets` để chọn phố mong muốn; mặc định là "phố nào cũng được".)

**Yêu cầu giữa các người** (ràng buộc nhị phân — *binary*): các cặp sau phải ở **cùng một phố**:
Bố mẹ – Ông bà (để tiện chăm sóc), Bố mẹ – Con gái.

**Yêu cầu chung cả nhà** (ràng buộc toàn cục — *global*):
- Tổng tiền 4 căn ≤ **11 tỷ**.
- Không ai mua trùng một căn (*AllDiff*).

**Dữ liệu:** 1.678 tin rao bán căn hộ thật ở Hai Bà Trưng (tháng 6–12/2025), do nhóm tổng hợp, xem [`data/README.md`](data/README.md).

> **Vì sao không chỉ tìm 1 căn hộ?** Tìm 1 căn thoả điều kiện chỉ là *lọc dữ liệu* (một vòng `for` là xong),
> không cần AI. Khi có **nhiều người** và **ràng buộc giữa họ**, lựa chọn của người này ảnh hưởng người kia →
> số tổ hợp bùng nổ (504 × 270 × 366 × 375 ≈ **18,7 tỷ** tổ hợp) → lúc đó mới cần thuật toán tìm kiếm thông minh.

---

## 3. Cấu trúc thư mục

```
estate_advisor_introai_hust/
├── README.md                  ← file bạn đang đọc
├── csp_advisor/
│   ├── m1_problem.py          ← Thành viên 1: biến, miền, dữ liệu, yêu cầu của từng người
│   ├── m2_constraints.py      ← Thành viên 2: kiểm tra ràng buộc
│   ├── m3_heuristics.py       ← Thành viên 3: MRV, Degree, LCV
│   ├── m4_inference.py        ← Thành viên 4: Forward Checking + khôi phục
│   └── m5_solver.py           ← Thành viên 5: Backtracking + chạy chương trình  ◄ CHẠY FILE NÀY
├── data/
│   ├── apartments.csv         ← 1.678 căn hộ đã làm sạch
│   ├── raw/                   ← file gốc của nhóm
│   └── README.md              ← nguồn, cách làm sạch & giấy phép dữ liệu
└── scripts/build_dataset.py   ← script làm sạch dữ liệu
```

---

## 4. Bức tranh tổng thể

```
               m1_problem.py  (Thành viên 1)
         Đọc CSV → tạo biến X, miền D, đồ thị ràng buộc
                          │
                          ▼
               m2_constraints.py  (Thành viên 2)
         apply_node_consistency(): lọc D bằng ràng buộc đơn
                          │
                          ▼
   ┌───────────── m5_solver.py: backtrack()  (Thành viên 5) ─────────────┐
   │  Lặp lại cho tới khi gán đủ 4 biến:                                   │
   │   ① Chọn biến       → select_unassigned_variable()   (Thành viên 3)   │
   │   ② Xếp thứ tự giá trị → order_domain_values()       (Thành viên 3)   │
   │   ③ Kiểm tra hợp lệ → is_consistent()                (Thành viên 2)   │
   │   ④ Cắt tỉa miền    → forward_check()                (Thành viên 4)   │
   │   ⑤ Đệ quy; nếu thất bại → restore() rồi thử giá trị khác (TV 4, 5)  │
   └───────────────────────────────────────────────────────────────────────┘
```

Câu nói tóm tắt cho cả nhóm:
> *"Module 1 mô hình hoá bài toán thành CSP, Module 2 định nghĩa thế nào là hợp lệ, Module 3 quyết định thử cái gì trước,
> Module 4 nhìn trước để loại bỏ lựa chọn vô vọng, và Module 5 là vòng lặp tìm kiếm ghép tất cả lại."*

---

## 5. Kết quả thực nghiệm

| Cấu hình | Nodes (11 tỷ) | Thời gian (11 tỷ) | Nodes (8.0 tỷ — vô nghiệm) | Thời gian (8.0 tỷ) |
|---|---:|---:|---:|---:|
| Backtracking thuần | 312.093 | 101 ms | 8.917.149 | 2.280 ms |
| + Forward Checking | 848 | 62 ms | 17.990 | 335 ms |
| + FC + MRV/Degree | 274 | 34 ms | 5.808 | 947 ms |
| + FC + MRV/Degree + LCV | **4** | 63 ms | 5.808 | 1.273 ms |

(Thời gian đo trên một máy Mac; máy khác sẽ khác, nhưng xu hướng giống nhau.)

Bốn điều rút ra (nên nói khi thuyết trình):
1. **Forward Checking** giảm số node khoảng **370 lần** (312.093 → 848): phát hiện ngõ cụt sớm thay vì đi sâu rồi mới biết.
2. **MRV** giảm thêm khoảng **3 lần**: chọn biến "khó" trước nên thất bại xảy ra ở tầng nông của cây.
3. **LCV** đưa xuống còn **4 node** = gán thẳng 4 biến, không quay lui lần nào. Khi bài toán **vô nghiệm** (8.0 tỷ), LCV **không giảm node nào** —
   vì phải duyệt hết mọi khả năng thì thứ tự thử giá trị không quan trọng.
4. **Ít node hơn không có nghĩa là nhanh hơn.** LCV chỉ cần 4 node nhưng mỗi node phải đếm hàng trăm nghìn phép kiểm tra, nên tổng thời gian
   (63 ms) còn chậm hơn không dùng LCV (34 ms). Ở ngân sách 8.0 tỷ, MRV giảm node 3 lần nhưng lại chậm hơn, vì Forward Checking cắt tỉa
   nhiều hơn hẳn ở mỗi node (2,27 triệu so với 566 nghìn giá trị). Đây là điểm hiểu sâu: **chi phí mỗi node** cũng quan trọng như **số node**.

---

## Thành viên 1 — Module 1: Phát biểu bài toán & Định nghĩa trạng thái

📄 File: `csp_advisor/m1_problem.py`

### 1. Lĩnh vực phụ trách
Biến bài toán đời thực ("gia đình muốn mua căn hộ") thành mô hình toán học **CSP** mà máy tính giải được.
Đọc dữ liệu CSV, định nghĩa biến, miền giá trị, yêu cầu của từng người và đồ thị ràng buộc.

### 2. Kiến thức lý thuyết cần nắm
- **CSP** là bộ ba **(X, D, C)**:
  - **X** — tập biến: `{Con gái, Con trai, Bố mẹ, Ông bà}`.
  - **D** — miền giá trị của mỗi biến: tập id các căn hộ (0 → 1677).
  - **C** — tập ràng buộc: quy định tổ hợp giá trị nào được phép.
- **Trạng thái (state)** trong CSP = một **phép gán (assignment)**, ví dụ `{"Ông bà": 818, "Bố mẹ": 1435}`.
  - **Gán đầy đủ (complete)**: mọi biến đều có giá trị.
  - **Gán nhất quán (consistent)**: không vi phạm ràng buộc nào.
  - **Lời giải (solution)** = phép gán vừa đầy đủ vừa nhất quán.
- **Đồ thị ràng buộc (constraint graph)**: mỗi biến là 1 đỉnh, mỗi ràng buộc nhị phân là 1 cạnh.
  Đồ thị của nhóm: `Bố mẹ – Ông bà`, `Bố mẹ – Con gái`. `Con trai` không có cạnh nào (chỉ bị ràng buộc qua ngân sách và AllDiff).
- **Vì sao CSP tốt hơn tìm kiếm thông thường?** Tìm kiếm thường coi trạng thái là "hộp đen";
  CSP biết **cấu trúc bên trong** (biến, ràng buộc) nên có thể dùng heuristic và cắt tỉa tổng quát,
  không phụ thuộc bài toán cụ thể.

### 3. Giải thích code
| Thành phần | Ý nghĩa |
|---|---|
| `REQUIREMENTS` | Yêu cầu của từng người → chính là **ràng buộc đơn**. `types`/`streets` bằng `None` nghĩa là "loại nào/phố nào cũng được". Thứ tự khai báo = thứ tự gán khi không dùng MRV. |
| `SAME_STREET_PAIRS` | Danh sách cặp người phải ở cùng phố → **ràng buộc nhị phân**, cũng là **cạnh** của đồ thị ràng buộc. |
| `TOTAL_BUDGET` | Ngân sách cả nhà → **ràng buộc toàn cục**. |
| `load_houses()` | Đọc CSV bằng `csv.DictReader`; mỗi dòng thành 1 dict; đổi chuỗi sang `float`/`int`. Dùng **số thứ tự dòng làm id**. Nếu thiếu file thì gọi `make_synthetic_houses()` sinh dữ liệu giả. |
| `class CSP.__init__` | `self.variables` = X; `self.domains` = D (ban đầu mỗi biến nhận **mọi** căn); `self.neighbors` = danh sách kề của đồ thị ràng buộc, xây từ `same_street_pairs`. |
| `build_csp(budget)` | Tạo một CSP mới tinh. Module 5 gọi hàm này **mỗi lần chạy** để các lần chạy không ảnh hưởng nhau. |

### 4. Câu hỏi thầy/cô có thể hỏi
**❓ Tại sao chọn biến là "người", giá trị là "căn hộ"? Đảo ngược lại được không?**
> Được, nhưng kém hơn. Nếu biến là căn hộ (1.678 biến) và giá trị là "ai mua" (5 giá trị: 4 người + không ai), thì có 1.678 biến
> và hầu hết phải gán "không ai" — không gian tìm kiếm khổng lồ (5^1678). Chọn người làm biến cho **4 biến** với miền vài trăm
> giá trị, và các ràng buộc (cùng phố, ngân sách) phát biểu tự nhiên giữa các biến.

**❓ Không gian trạng thái của bài toán lớn cỡ nào?**
> Sau khi lọc ràng buộc đơn: 504 × 270 × 366 × 375 ≈ **18,7 tỷ** phép gán đầy đủ. Tính cả phép gán dở dang
> (các node trong cây tìm kiếm) còn nhiều hơn. Duyệt hết là không khả thi, nên cần backtracking + cắt tỉa.

**❓ Vì sao ràng buộc vị trí là "cùng phố" mà không phải "cùng phường" hay "gần nhau"?**
> Toàn bộ dữ liệu nằm trong một quận (Hai Bà Trưng), nên quận không phân biệt được gì. Cột phường bị trống ở khoảng một nửa số dòng,
> còn cột phố có ở hơn 90% dòng. "Cùng phố" là thông tin **có thật trong dữ liệu**, không phải tự đoán. Muốn dùng "gần nhau" theo khoảng cách
> thật thì cần toạ độ GPS; khi đó chỉ cần sửa hàm `satisfies_binary` ở Module 2 mà **không phải sửa thuật toán** — đó là ưu điểm của việc
> tách mô hình (Module 1–2) khỏi thuật toán (Module 3–5).

---

## Thành viên 2 — Module 2: Bộ kiểm tra ràng buộc

📄 File: `csp_advisor/m2_constraints.py`

### 1. Lĩnh vực phụ trách
Định nghĩa **"thế nào là hợp lệ"**. Mọi module khác đều hỏi Module 2 trước khi quyết định.

### 2. Kiến thức lý thuyết cần nắm
- **Phân loại ràng buộc theo số biến (arity)**:
  - **Unary** (1 biến): `price(Bố mẹ) ≤ 9.0`, `type(Ông bà) = Nhà tập thể`.
  - **Binary** (2 biến): `street(Bố mẹ) = street(Ông bà)`.
  - **Global / higher-order** (nhiều biến): `AllDiff(...)`, `Σ price ≤ 11`.
- **Node consistency**: một biến là *node-consistent* nếu **mọi** giá trị trong miền thoả ràng buộc đơn của nó.
  Ta đạt được điều này bằng cách lọc miền **một lần trước khi tìm kiếm** → miền giảm từ 1.678 xuống còn 270–504.
- **Kiểm tra nhất quán**: một giá trị mới chỉ cần được kiểm tra với **các biến đã gán**; các biến chưa gán chưa có gì để mâu thuẫn.

### 3. Giải thích code
| Hàm | Ý nghĩa |
|---|---|
| `satisfies_unary(csp, var, house_id)` | Lấy căn hộ và yêu cầu của người `var`; kiểm tra lần lượt giá, diện tích, phòng ngủ, loại căn hộ, phố. Sai ở đâu `return False` ngay (thoát sớm). |
| `apply_node_consistency(csp)` | Với mỗi biến, giữ lại các căn thoả `satisfies_unary`. Dùng *list comprehension*. |
| `satisfies_binary(csp, a, ha, b, hb)` | (1) **AllDiff**: hai người không trùng căn. (2) Nếu `(a, b)` nằm trong `same_street_pairs` (xét cả 2 chiều) → hai căn phải cùng phố. |
| `within_total_budget(csp, assignment, var, house_id)` | Cộng giá căn mới + giá các căn **đã gán** của người khác; so với ngân sách. |
| `is_consistent(csp, assignment, var, house_id)` | **Hàm tổng hợp**: unary → binary với từng biến đã gán → ngân sách. Đây là hàm Module 4 và 5 gọi. |

### 4. Câu hỏi thầy/cô có thể hỏi
**❓ AllDiff là ràng buộc toàn cục, sao em lại kiểm tra nó trong hàm nhị phân?**
> Vì AllDiff trên n biến **tương đương** với n(n−1)/2 ràng buộc nhị phân "≠" từng cặp. Tách ra như vậy thì đúng về logic
> nhưng **yếu hơn** khi suy diễn: ví dụ 3 biến cùng miền chỉ có 2 giá trị thì từng cặp vẫn thoả nhưng AllDiff thì vô nghiệm.
> Trong bài này miền rất lớn so với 4 biến nên cách tách cặp là đủ.

**❓ Ràng buộc ngân sách có đưa về nhị phân được không?**
> Không trực tiếp được, vì nó phụ thuộc cùng lúc **cả 4 biến**. Về lý thuyết, mọi ràng buộc bậc cao đều có thể đổi sang
> nhị phân bằng cách thêm **biến phụ** (ví dụ biến "tổng tiền đến người thứ k"), nhưng làm vậy phức tạp. Nhóm em kiểm tra trực tiếp
> trên các biến đã gán, và Forward Checking (Module 4) cũng tận dụng nó để loại các căn đắt hơn số tiền còn lại.

**❓ Tại sao phải lọc ràng buộc đơn trước, không để tìm kiếm tự lọc?**
> Nếu không lọc trước, mỗi lần thử một giá trị ta phải kiểm tra lại cùng điều kiện, và MRV sẽ thấy mọi miền đều có 1.678 giá trị
> (không phân biệt được biến nào khó). Lọc trước làm **một lần duy nhất** với chi phí O(n·d) và giúp MRV có thông tin chính xác ngay từ đầu.

---

## Thành viên 3 — Module 3: Các hàm Heuristic

📄 File: `csp_advisor/m3_heuristics.py`

### 1. Lĩnh vực phụ trách
Quyết định **thứ tự**: gán biến nào trước, thử giá trị nào trước. Không làm thay đổi kết quả đúng/sai,
chỉ ảnh hưởng **tốc độ** (274 node → 4 node).

### 2. Kiến thức lý thuyết cần nắm
- **MRV — Minimum Remaining Values** (còn gọi *most constrained variable*, *fail-first*):
  chọn biến có **ít giá trị hợp lệ nhất** còn lại. Lý do: biến khó nhất nếu thất bại thì nên thất bại **càng sớm càng tốt**,
  ở tầng nông của cây, để cắt bỏ cả nhánh lớn.
- **Degree heuristic**: dùng để **phá hoà** khi MRV bằng nhau — chọn biến tham gia **nhiều ràng buộc nhất với các biến chưa gán**
  (bậc lớn nhất trong đồ thị ràng buộc). Gán nó trước sẽ giảm nhánh của nhiều biến khác.
- **LCV — Least Constraining Value** (*fail-last*): với biến đã chọn, thử giá trị **loại bỏ ít lựa chọn nhất** của các biến
  khác trước. Lý do: ta chỉ cần **một** lời giải, nên chọn giá trị "dễ chịu" nhất để giữ đường đi tới lời giải.
- **Ghi nhớ**: biến → *fail-first*; giá trị → *fail-last*. Vì **mọi biến cuối cùng đều phải gán** (nên đụng cái khó trước),
  nhưng **chỉ cần một giá trị** thành công (nên thử cái dễ trước).

### 3. Giải thích code
**`select_unassigned_variable(csp, assignment, use_mrv)`**
- Lấy danh sách biến chưa gán.
- Nếu tắt MRV → trả về biến đầu tiên (thứ tự cố định).
- Hàm con `degree(var)`: đếm láng giềng **chưa gán** của `var` trong `csp.neighbors`.
- `min(..., key=lambda v: (len(domain), -degree))`: so sánh theo **tuple** — ưu tiên miền nhỏ nhất; nếu bằng nhau
  thì ưu tiên degree lớn nhất (dấu `-` vì dùng `min`).
- Ví dụ: ban đầu miền `Con trai` = 270 nhỏ nhất → MRV chọn **Con trai** trước tiên.

**`order_domain_values(csp, var, assignment, use_lcv)`**
- Tính số tiền đã tiêu `assigned_cost` cho các biến đã gán.
- Hàm con `ruled_out(house_id)`: giả sử chọn căn này, đếm xem bao nhiêu giá trị trong miền của các biến **chưa gán khác**
  bị loại (vi phạm ràng buộc nhị phân, hoặc đắt hơn số tiền còn lại).
- `sorted(..., key=(ruled_out, price))`: ít loại nhất lên trước; hoà thì căn rẻ hơn trước.

### 4. Câu hỏi thầy/cô có thể hỏi
**❓ LCV giảm từ 274 xuống 4 node, sao thời gian lại tăng (34 ms → 63 ms)?**
> Vì với mỗi biến, LCV phải tính `ruled_out` cho **mọi** giá trị trong miền, mỗi lần duyệt miền của các biến còn lại — chi phí
> khoảng O(d × n × d) phép kiểm tra (d = kích thước miền, ở đây vài trăm). Số node giảm nhưng **chi phí mỗi node** tăng mạnh hơn.
> LCV có lợi khi việc đi sai nhánh rất đắt (bài toán lớn hơn, nhiều biến hơn). Khi bài toán **vô nghiệm** (8.0 tỷ), LCV không giảm
> node nào mà vẫn tốn chi phí — vì phải duyệt hết thì thứ tự giá trị không còn ý nghĩa. Tương tự nếu ta muốn tìm **tất cả** lời giải.

**❓ Vì sao MRV gần như vô dụng nếu không có Forward Checking?**
> Không có FC thì miền **không bao giờ bị thu nhỏ** trong lúc tìm kiếm — MRV chỉ thấy kích thước miền ban đầu, nên luôn chọn
> theo cùng một thứ tự tĩnh. Chính FC cập nhật miền sau mỗi bước, MRV mới phản ánh được biến nào "đang khó nhất". Vì vậy
> nhóm em bật MRV **cùng với** FC trong bảng so sánh.

**❓ MRV chọn `Con trai` đầu tiên dù `Con trai` không có cạnh nào trong đồ thị ràng buộc. Có hợp lý không?**
> MRV chỉ nhìn **kích thước miền**, không nhìn đồ thị: `Con trai` có ít lựa chọn nhất (270). Degree heuristic chỉ dùng khi **hoà** về MRV;
> nếu hai biến cùng số giá trị, Degree sẽ chọn `Bố mẹ` (bậc 2: nối với `Ông bà` và `Con gái`). Chọn `Con trai` trước vẫn có ích vì
> sau đó Forward Checking dùng ràng buộc ngân sách để loại các căn quá đắt của 3 người còn lại.

---

## Thành viên 4 — Module 4: Cắt tỉa miền giá trị & Forward Checking

📄 File: `csp_advisor/m4_inference.py`

### 1. Lĩnh vực phụ trách
**Suy diễn (inference)**: sau mỗi lần gán, loại ngay các giá trị không còn khả thi khỏi miền của biến chưa gán,
và **khôi phục** chính xác khi quay lui.

### 2. Kiến thức lý thuyết cần nắm
- **Forward Checking**: khi gán `X = v`, với mỗi biến **chưa gán** `Y` có ràng buộc với `X`, xoá khỏi `D(Y)` mọi giá trị
  không nhất quán với `X = v`. Nếu một miền **rỗng** → ngõ cụt → quay lui ngay.
- **Pruning (cắt tỉa)**: loại bỏ những nhánh chắc chắn không chứa lời giải, **không làm mất lời giải** (thuật toán vẫn đầy đủ — *complete*).
- **Arc consistency (AC-3)**: mạnh hơn FC. FC chỉ kiểm tra cung giữa **biến vừa gán** và các biến chưa gán. AC-3 kiểm tra
  **mọi cặp** biến, và khi một miền thay đổi thì lan truyền tiếp. **MAC** (*Maintaining Arc Consistency*) = chạy AC-3 sau mỗi lần gán.
- **Quan hệ giữa FC và AC**: FC = làm cho mọi cung `(Y → X)` với `X` vừa gán trở nên arc-consistent; nó không xét cung giữa
  hai biến **đều chưa gán**.

### 3. Giải thích code
**`forward_check(csp, assignment, var)`** — gọi **sau khi** `assignment[var]` đã được gán:
- `removed = []`: nhật ký các giá trị bị xoá, dạng `(biến, id_căn)`.
- Duyệt mọi biến **chưa gán** `other` (bao gồm cả biến không có cạnh, vì ràng buộc ngân sách và AllDiff là toàn cục).
- Duyệt trên **bản sao** `list(csp.domains[other])` vì ta xoá phần tử trong lúc lặp — xoá trên chính list đang duyệt sẽ bỏ sót phần tử.
- Nếu `is_consistent(...)` sai → xoá khỏi miền và ghi vào `removed`.
- Nếu miền rỗng → trả `(removed, False)` để Module 5 quay lui ngay.

**`restore(csp, removed)`**:
- Thêm lại từng giá trị đã xoá, rồi sắp xếp lại miền theo id để giữ **đúng thứ tự ban đầu**
  (để kết quả tìm kiếm có thể lặp lại).

### 4. Câu hỏi thầy/cô có thể hỏi
**❓ Tại sao phải `restore`? Không khôi phục thì sao?**
> Các giá trị bị xoá chỉ sai **trong nhánh hiện tại** (vì nó mâu thuẫn với lựa chọn hiện tại). Khi quay lui và thử lựa chọn khác,
> những giá trị đó có thể lại hợp lệ. Nếu không khôi phục, ta sẽ **mất lời giải** — thuật toán không còn đầy đủ (incomplete).

**❓ FC khác AC-3 thế nào? Sao nhóm không dùng AC-3?**
> FC chỉ kiểm tra giữa biến vừa gán và các biến chưa gán; AC-3 kiểm tra mọi cặp và lan truyền. Ví dụ: sau khi gán `Ông bà` ở phố Lò Đúc,
> FC giữ lại trong miền `Bố mẹ` chỉ các căn ở Lò Đúc, nhưng **không** kiểm tra tiếp `Con gái` (vì `Con gái` không có ràng buộc trực tiếp
> với `Ông bà`). AC-3 thì sẽ thấy: `Con gái` phải cùng phố với `Bố mẹ`, mà `Bố mẹ` giờ chỉ còn ở Lò Đúc → `Con gái` cũng chỉ còn căn ở Lò Đúc.
> AC-3 cắt tỉa mạnh hơn nhưng tốn chi phí O(c·d³) mỗi lần chạy. Với bài 4 biến, FC + MRV đã giảm số node xuống rất thấp nên FC là lựa chọn
> cân bằng. Nâng cấp lên MAC là hướng phát triển.

**❓ FC phát hiện ngõ cụt sớm hơn backtracking thường ở chỗ nào? Cho ví dụ.**
> Backtracking thường chỉ biết ngõ cụt khi đến lượt gán một biến và **mọi** giá trị đều sai. FC biết ngay khi miền một biến
> **tương lai** rỗng. Ví dụ: chọn cho `Bố mẹ` một căn 9 tỷ → chỉ còn 2 tỷ cho 3 người → FC lập tức xoá mọi căn đắt hơn 2 tỷ khỏi miền
> của họ; nếu một người không còn căn nào thì bỏ căn 9 tỷ ngay, thay vì gán thử hàng trăm tổ hợp. Thực nghiệm: số node giảm từ
> 312.093 xuống 848.

---

## Thành viên 5 — Module 5: Bộ giải Backtracking & Chương trình chính

📄 File: `csp_advisor/m5_solver.py`

### 1. Lĩnh vực phụ trách
Thuật toán **Backtracking Search** đệ quy ghép tất cả module lại; chạy thực nghiệm so sánh 4 cấu hình và in kết quả.

### 2. Kiến thức lý thuyết cần nắm
- **Backtracking search** = **tìm kiếm theo chiều sâu (DFS)** trên cây phép gán, mỗi tầng gán thêm **đúng 1 biến**,
  và **dừng nhánh ngay** khi phép gán dở dang vi phạm ràng buộc.
- **Tính giao hoán (commutativity)** của CSP: thứ tự gán không ảnh hưởng kết quả → mỗi tầng chỉ cần xét **một** biến,
  cây chỉ có dⁿ lá thay vì n!·dⁿ.
- **Độ phức tạp**: xấu nhất O(dⁿ) (n biến, d giá trị/miền). Heuristic và FC không đổi độ phức tạp xấu nhất nhưng giảm mạnh
  trong thực tế.
- **Tính đầy đủ (completeness)**: nếu có lời giải, backtracking chắc chắn tìm thấy; nếu trả về `None` nghĩa là
  **đã chứng minh vô nghiệm** (ví dụ ngân sách 8.0 tỷ).
- **Các chỉ số đo**: *nodes* = số lần thử một giá trị; *backtracks* = số lần một biến hết giá trị phải quay lui;
  *pruned* = số giá trị FC đã cắt.

### 3. Giải thích code
**`backtracking_search(csp, use_mrv, use_lcv, use_fc)`**: tạo dict `stats`, gói các tuỳ chọn vào `options`, gọi `backtrack({}, ...)`.

**`backtrack(assignment, csp, options, stats)`** — 7 bước (đã đánh số trong code):
1. **Điều kiện dừng**: gán đủ biến → trả về bản sao lời giải.
2. Chọn biến (Module 3).
3. Duyệt giá trị theo thứ tự của LCV (Module 3); mỗi lần thử tăng `nodes`.
4. `is_consistent` (Module 2) sai → bỏ qua giá trị.
5. Gán thử, rồi `forward_check` (Module 4) nếu bật.
6. Nếu FC không báo ngõ cụt → **đệ quy**. Có lời giải → trả lên ngay.
7. Thất bại → `restore` miền, xoá phép gán, thử giá trị tiếp theo. Hết giá trị → `backtracks += 1`, trả `None`.

**`main()`**: đọc ngân sách từ dòng lệnh; in kích thước miền sau node consistency; chạy 4 cấu hình, **mỗi cấu hình dùng CSP mới**
(vì FC sửa miền); in bảng số liệu và lời giải.

### 4. Câu hỏi thầy/cô có thể hỏi
**❓ Backtracking khác DFS thông thường ở đâu?**
> Hai điểm: (1) mỗi tầng chỉ gán **một biến** (nhờ tính giao hoán) chứ không sinh mọi hành động có thể; (2) kiểm tra ràng buộc
> **ngay trên phép gán dở dang** và bỏ nhánh sớm, thay vì đi đến lá rồi mới kiểm tra (*generate-and-test*). Ngoài ra trạng thái
> được sửa tại chỗ rồi hoàn tác (`del assignment[var]`, `restore`), không sao chép toàn bộ trạng thái ở mỗi node.

**❓ Kết quả trả về có phải là phương án *tốt nhất* (rẻ nhất) không?**
> Không. CSP tìm phương án **thoả mãn** (*satisfaction*), không phải **tối ưu** (*optimization*). Kết quả ví dụ tốn 10,43 / 11 tỷ:
> hợp lệ nhưng không nhất thiết rẻ nhất. Muốn tối ưu có thể dùng **Branch and Bound**: tìm được lời giải chi phí C thì đặt ngân sách
> mới < C và tìm tiếp, cho tới khi vô nghiệm — lời giải cuối cùng là tối ưu.

**❓ Vì sao "nodes" ở dòng cuối là 4 mà "cắt tỉa" vẫn là 838?**
> 4 node nghĩa là gán 4 biến, mỗi biến thử **đúng 1 giá trị** đầu tiên của LCV là thành công — không quay lui lần nào. 838 là
> số giá trị FC loại khỏi miền các biến khác trong 4 lần gán đó. Chính việc cắt tỉa này giữ cho các lựa chọn tiếp theo
> luôn hợp lệ.

---

## 7. Câu hỏi chung cả nhóm nên chuẩn bị

**❓ Tại sao dùng CSP mà không dùng A\* hay tìm kiếm cục bộ (hill climbing)?**
> A\* cần **hàm chi phí đường đi** và mục tiêu là đường đi tối ưu; ở đây không có "đường đi", chỉ có điều kiện cần thoả. Tìm kiếm cục bộ
> (min-conflicts) có thể nhanh với bài toán lớn nhưng **không đầy đủ**: không thể chứng minh "vô nghiệm" như ta làm với 8.0 tỷ.

**❓ Bài toán có lời giải nào khác không? Làm sao tìm hết?**
> Có, rất nhiều. Muốn tìm tất cả, sửa bước 6: thay vì `return result` thì lưu vào danh sách và tiếp tục duyệt.

**❓ Dữ liệu lấy từ đâu, có đáng tin không?**
> Nhóm tổng hợp 2.040 tin rao bán căn hộ ở Hai Bà Trưng (tháng 6–12/2025) từ bộ dữ liệu công khai *Vietnam Real Estates* trên Kaggle
> (giấy phép CC BY-NC-SA 4.0). Sau khi làm sạch (bỏ dòng thiếu phố hoặc số phòng ngủ, bỏ giá/m² vô lý, bỏ tin đăng trùng) còn 1.678 căn.
> Giá là **giá rao bán**, không phải giá giao dịch thật. Chi tiết trong `data/README.md`.

---

## 8. Mẹo khi thuyết trình

- **Chạy demo trực tiếp** cả 2 lệnh (11 và 8.0 tỷ). Bảng số liệu là bằng chứng mạnh nhất cho thấy nhóm hiểu thuật toán.
- Mỗi người mở **đúng file của mình** và chỉ vào từng dòng khi giải thích; các bước trong code đã được đánh số.
- **Thử sửa `REQUIREMENTS`** trong `m1_problem.py` (ví dụ cho Ông bà chỉ chọn phố `Minh Khai`) rồi chạy lại để luyện giải thích tại sao số node thay đổi.
- Nói được **1 câu kết nối** module mình với module trước và sau (xem [mục 4](#4-bức-tranh-tổng-thể)).
- Tài liệu tham khảo chính: Russell & Norvig, *Artificial Intelligence: A Modern Approach*, Chương 6 — *Constraint Satisfaction Problems*.
