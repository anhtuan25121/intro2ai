---
layout: default
title: Lecture 3.3 - Informed Search
---

# Lecture 3.3 — Informed (Heuristic) Search Strategies

> Không thuộc phạm vi thi giữa kì (chỉ Lecture 5). Xem nền tảng ở [Lecture 3.1 - Problem Solving by Searching](lecture-3-1-problem-solving-by-searching.md) và [Lecture 3.2 - Uninformed Search](lecture-3-2-uninformed-search.md).

## Heuristic là gì?

- Tri thức đặc thù bài toán (problem-specific knowledge) thêm vào ngoài định nghĩa chuẩn
- **h(n)**: heuristic function — ước lượng **chi phí rẻ nhất từ node n đến goal**
- Điều kiện: h(n) ≥ 0, và **h(goal) = 0**

## Best-First Search (khung tổng quát)

- Chọn node để expand dựa trên **evaluation function f(n)**
- Cách chọn f(n) khác nhau → ra các thuật toán khác nhau (Greedy, A*,...)

## 1. Greedy Best-First Search

- `f(n) = h(n)` — chỉ dùng heuristic, bỏ qua cost đã đi (g)
- Expand node **có vẻ gần goal nhất**
- Ví dụ kinh điển: **Straight-line distance heuristic (h_SLD)** trong bản đồ Romania
- Complete: Yes nếu graph-search & state space hữu hạn
- Time/Space: O(b^m) — nhưng thực tế giảm nhiều nhờ heuristic tốt
- **Optimal: NO** — có thể đi lệch hướng vì chỉ nhìn "vẻ ngoài" gần goal

## 2. A* Search ⭐ (thuật toán informed search quan trọng nhất)

- `f(n) = g(n) + h(n)`
  - g(n) = cost thực tế đã đi từ start đến n
  - h(n) = ước lượng cost từ n đến goal
  - f(n) = ước lượng tổng cost của giải pháp tốt nhất đi qua n
- Complete: Yes (nếu mọi step cost > ε và b hữu hạn)
- **Optimal: Yes — với điều kiện heuristic phù hợp** (xem bên dưới)
- Time & Space: **exponential** trong trường hợp xấu nhất — A* thường **hết memory trước khi hết time**

### Điều kiện để A* tối ưu

**Admissible heuristic** (điều kiện cho TREE-SEARCH):

- h(n) **không bao giờ overestimate** (đánh giá cao hơn) chi phí thật để đến goal
- `h(n) ≤ h*(n)` với mọi n (h* = cost thật)
- Ví dụ: straight-line distance luôn admissible (đường thẳng luôn ngắn nhất)

**Consistent heuristic** (điều kiện cho GRAPH-SEARCH — mạnh hơn admissible):

- Với mọi n và successor n' qua action a: `h(n) ≤ c(n,a,n') + h(n')` (triangle inequality)
- Mọi heuristic consistent đều admissible (ngược lại không đúng)
- Nếu h consistent → f(n) **không giảm (non-decreasing)** dọc theo bất kỳ path nào

> **Ghi nhớ**:
> - h admissible → A* + TREE-SEARCH tối ưu
> - h consistent → A* + GRAPH-SEARCH tối ưu

### Contours của A*

- A* mở rộng mọi node có f(n) < C* (cost lời giải tối ưu) trước khi tìm ra goal
- Contour của UCS: hình tròn quanh start (không có thông tin hướng)
- Contour của A*: kéo dài về phía goal (nhờ heuristic) → hiệu quả hơn nhiều

### Ưu & nhược điểm A*

- **Ưu điểm**: optimally efficient — không thuật toán tối ưu nào expand ít node hơn với cùng 1 heuristic consistent
- **Nhược điểm**: vẫn phải giữ toàn bộ node trong memory → không thực tế cho bài toán lớn

## 3. Memory-Bounded Heuristic Search (khắc phục nhược điểm A*)

### Iterative-Deepening A* (IDA*)

- Giống IDS nhưng cutoff theo **f-value (g+h)** thay vì độ sâu
- Mỗi vòng lặp: cutoff mới = f-value nhỏ nhất từng vượt ngưỡng ở vòng trước
- Tốt với unit step costs, khó với real-valued costs

### Recursive Best-First Search (RBFS)

- Giống DFS nhưng nhớ **f-value tốt nhất của nhánh thay thế (alternative)** từ tổ tiên
- Backtrack khi current node vượt quá f_limit; khi backtrack, cập nhật f-value node cha = best f-value của con
- Space: **O(bd)** — tuyến tính (như DFS)
- Nhược điểm: có thể "switch" qua lại tốn thời gian nếu best path đổi liên tục

### (Simplified) Memory-bounded A* — SMA*

- Giống A* nhưng khi hết memory → xoá node tệ nhất (f lớn nhất), backup giá trị lên node cha
- Tìm được lời giải tối ưu **trong giới hạn memory cho phép**

## 4. Heuristic Functions — cách xây dựng heuristic tốt

### Ví dụ kinh điển: 8-puzzle

- **h1 = số ô sai vị trí (misplaced tiles / Hamming distance)**
- **h2 = tổng khoảng cách Manhattan** của từng ô đến vị trí đích — thường tốt hơn h1

### Effective Branching Factor (b*)

`N + 1 = 1 + b* + (b*)² + ... + (b*)^d`

- N = tổng số node A* sinh ra, d = độ sâu lời giải
- Heuristic tốt → b* gần 1 → giải được bài toán lớn với chi phí hợp lý

### Heuristic Dominance

- Nếu h2(n) ≥ h1(n) với mọi n (cả 2 admissible) → **h2 dominates h1**
- A* dùng h2 sẽ **không bao giờ expand nhiều node hơn** A* dùng h1
- Nên chọn heuristic có giá trị cao hơn (miễn vẫn consistent & tính nhanh)

### Relaxed Problems (cách sinh heuristic admissible)

- Bỏ bớt ràng buộc của bài toán gốc → bài toán "nới lỏng" dễ giải hơn
- Cost lời giải tối ưu của relaxed problem = heuristic admissible cho bài toán gốc
- Ví dụ 8-puzzle: bỏ điều kiện "ô đích phải trống" → sinh ra Manhattan distance; bỏ cả điều kiện kề nhau → sinh ra misplaced tiles
- Kết hợp nhiều heuristic admissible: `h(n) = max{h1(n),...,hm(n)}` — vẫn consistent, dominate tất cả thành phần

### Pattern Database Heuristics

- Lưu trước cost lời giải tối ưu cho **subproblem** (ví dụ chỉ định vị 1 số quân cụ thể)
- Cost của subproblem là **lower bound** cho cost bài toán đầy đủ
- Ví dụ: 7-tile pattern database cho 15-puzzle có 519 triệu entries

### Learning heuristics from experience

- Học h(n) từ nhiều lời giải tối ưu đã biết (dùng neural net, decision tree,...)

## Xem thêm

- [Lộ trình học & Liên kết kiến thức](lo-trinh-hoc.md) — bảng đối chiếu khái niệm Lecture 3 ↔ Lecture 5
- [Lecture 5 - Adversarial Search](lecture-5-adversarial-search.md) — Evaluation function EVAL(s) (H-Minimax) là "họ hàng" của heuristic h(n) ở trên: cùng mục đích ước lượng để tránh duyệt hết cây, nhưng EVAL đo "lợi thế" còn h(n) đo "chi phí còn lại" (nội dung thi)
