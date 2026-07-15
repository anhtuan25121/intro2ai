---
layout: default
title: Lecture 3.2 - Uninformed Search
---

# Lecture 3.2 — Uninformed Search Strategies

> Không thuộc phạm vi thi giữa kì (chỉ Lecture 5). Xem nền tảng ở [Lecture 3.1 - Problem Solving by Searching](lecture-3-1-problem-solving-by-searching.md).

## Uninformed (Blind) Search

Không dùng thông tin nào ngoài định nghĩa bài toán — chỉ sinh successor & phân biệt goal/non-goal.

## Bảng tổng hợp so sánh (QUAN TRỌNG NHẤT — bảng SGK Figure 3.21)

| Tiêu chí | BFS | UCS | DFS | DLS | IDS | Bidirectional |
|---|---|---|---|---|---|---|
| Complete? | Yes* | Yes* | No | No | Yes* | Yes* |
| Time | O(b^d) | O(b^(1+⌊C*/ε⌋)) | O(b^m) | O(b^ℓ) | O(b^d) | O(b^(d/2)) |
| Space | O(b^d) | O(b^(1+⌊C*/ε⌋)) | O(bm) | O(bℓ) | O(bd) | O(b^(d/2)) |
| Optimal? | Yes** | Yes | No | No | Yes** | Yes**† |

\*complete nếu b hữu hạn (UCS thêm điều kiện step cost ≥ ε>0); \*\*optimal nếu step costs đều bằng nhau; †nếu cả 2 chiều dùng BFS

## 1. Breadth-First Search (BFS)

- Expand node **nông nhất (shallowest)** trước
- Cài đặt: frontier = **FIFO queue**
- Goal test áp dụng **khi sinh ra node** (không phải khi chọn expand) → tìm goal sớm hơn
- Complete: **Yes** · Optimal: chỉ khi step cost đều bằng nhau
- Time & Space: **O(b^d)** — vấn đề lớn nhất là **memory** (space) chứ không phải time

## 2. Uniform-Cost Search (UCS)

- Expand node có **path cost g(n) thấp nhất** (không phải nông nhất)
- Cài đặt: frontier = **priority queue** theo g
- Tương đương BFS nếu step cost đều bằng nhau; tương đương **Dijkstra's algorithm** nói chung
- Goal test áp dụng **khi node được chọn để expand** (pop ra khỏi PQ), KHÔNG phải khi sinh ra
- ⚠️ Chỉ dừng khi **goal bị POP ra khỏi PQ**, không dừng ngay khi goal được sinh ra (khác BFS!)
- Complete: Yes (nếu cost tốt nhất hữu hạn & mọi step cost ≥ ε>0) · **Optimal: Yes**
- Time/Space: O(b^(1+⌊C*/ε⌋)) — C* = cost lời giải tối ưu

## 3. Depth-First Search (DFS)

- Expand node **sâu nhất (deepest)** trước
- Cài đặt: frontier = **LIFO stack**
- Space: chỉ **O(bm)** — tuyến tính, rất tiết kiệm bộ nhớ
- Complete: **No** (tree-search có thể lặp vô hạn); **Yes nếu graph-search & state space hữu hạn**
- Optimal: **No** — trả về lời giải "leftmost" bất kể cost
- Time: O(b^m)

## 4. Depth-Limited Search (DLS)

- DFS với **giới hạn độ sâu ℓ** định trước → tránh vô hạn
- Trả về **cutoff** (khác failure) nếu bị cắt do đạt giới hạn ℓ mà chưa tìm ra goal
- Complete: **No nếu ℓ < d** · Optimal: **No nếu ℓ > d**
- DFS = trường hợp đặc biệt của DLS khi ℓ = ∞

## 5. Iterative Deepening Search (IDS)

- Chạy DLS lặp lại với **ℓ tăng dần**: 0, 1, 2, ... cho đến khi tìm ra solution
- Kết hợp ưu điểm: **space của DFS** (O(bd)) + **completeness/optimality của BFS**
- Complete: **Yes** (nếu b hữu hạn) · Optimal: **Yes nếu step cost = 1**
- Time: O(b^d) — dù duyệt lặp lại nhiều lần các tầng trên nhưng tổng chi phí vẫn là O(b^d) vì số node tầng sâu nhất áp đảo
- Thường được ưu tiên khi search space lớn và **không biết độ sâu lời giải**

## 6. Bidirectional Search

- Chạy đồng thời 2 search: 1 từ initial state tiến lên, 1 từ goal state lùi lại — hy vọng 2 bên gặp nhau ở giữa
- Time/Space: **O(b^(d/2))** — cải thiện đáng kể
- Goal test: kiểm tra frontier 2 bên có giao nhau không
- Optimal: Yes nếu cả 2 chiều dùng BFS
- **Nhược điểm**: cần lưu frontier ít nhất 1 bên trong memory; khó search backwards (cần biết predecessors); khó nếu có nhiều goal hoặc goal trừu tượng

## Ghi chú thêm

- **Redundant paths**: nhiều cách để đến cùng 1 state → graph-search dùng explored set để tránh lặp lại
- Bài toán exponential-complexity thường **không giải được bằng uninformed methods** ngoại trừ instance nhỏ (bảng complexity BFS: depth 16 → 350 năm, 10 exabytes memory!)

## Xem thêm

- [Lộ trình học & Liên kết kiến thức](lo-trinh-hoc.md) — bảng đối chiếu khái niệm Lecture 3 ↔ Lecture 5
- [Lecture 5 - Adversarial Search](lecture-5-adversarial-search.md) — thuật toán **Alpha-Beta pruning chính là DFS** (mục 3 ở trên) có thêm 2 biến α, β để cắt tỉa (nội dung thi)
