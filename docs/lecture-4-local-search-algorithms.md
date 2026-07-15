---
layout: default
title: Lecture 4 - Local Search Algorithms
---

# Lecture 4 — Local Search Algorithms and Optimization Problems

> Không thuộc phạm vi thi giữa kì (chỉ Lecture 5). Trang này để tham khảo/hệ thống hóa.

## Optimization Problems & Local Search

- **Optimization problem**: tìm **best state** theo 1 objective function — không quan tâm đường đi (path), chỉ quan tâm **cấu hình cuối cùng**
- Ví dụ: 8-queens (cấu hình cuối), TSP, scheduling, VLSI design
- **Local search**: chỉ giữ **1 (hoặc vài) current node**, di chuyển đến neighbor — KHÔNG lưu path, dùng memory O(1) hằng số
- Phù hợp cho state space lớn/vô hạn (kể cả continuous)

### State-space Landscape

- "Location" = state, "Elevation" = giá trị objective function / heuristic cost
- **Global maximum/minimum**: đỉnh/đáy toàn cục — mục tiêu tìm kiếm
- **Complete algorithm**: luôn tìm ra goal nếu tồn tại
- **Optimal algorithm**: luôn tìm ra global extremum

## 1. Hill-Climbing Search

- Vòng lặp: di chuyển liên tục theo hướng **tăng giá trị (increasing value)**, dừng khi đạt "peak" (không neighbor nào tốt hơn)
- Không nhìn trước (no lookahead), không giữ search tree — chỉ nhớ state hiện tại
- Gọi là **"greedy local search"**

### Ví dụ: 8-queens với Hill-climbing

- Complete-state formulation: 8 quân trên bàn, mỗi cột 1 quân
- Successor: di chuyển 1 quân trong cùng cột (8×7 = 56 successors)
- h(n) = số cặp quân **đang tấn công nhau** (trực tiếp/gián tiếp) → global minimum h=0
- 8-queens (~17 triệu state): trung bình 4 bước nếu thành công, 3 bước nếu bị kẹt

### Vấn đề của Hill-Climbing (RẤT HAY HỎI)

| Vấn đề | Mô tả |
|---|---|
| **Local maxima** | Đỉnh cục bộ nhưng không phải đỉnh toàn cục — bị kẹt |
| **Ridges** | Dãy các đỉnh cục bộ liên tiếp không kết nối trực tiếp |
| **Plateau/Shoulder** | Vùng phẳng — không biết hướng nào để cải thiện |

- 8-queens: steepest-ascent hill-climbing chỉ giải được **14%** instance (kẹt 86%)

### Các biến thể khắc phục

- **Sideways moves**: cho phép di chuyển ngang (giá trị bằng nhau) khi bị kẹt ở plateau, giới hạn số bước để tránh vòng lặp vô hạn → nâng tỉ lệ giải 8-queens từ 14% lên **94%** (nhưng tốn thêm bước: ~21 bước/thành công, ~64 bước/thất bại)
- **Stochastic hill climbing**: chọn ngẫu nhiên trong các uphill move, xác suất tỉ lệ với độ dốc
- **First-choice hill climbing**: sinh ngẫu nhiên successor đến khi gặp cái tốt hơn hiện tại — tốt khi có nhiều successor
- **Random-restart hill climbing**: chạy nhiều lần từ random initial state; nếu xác suất thành công mỗi lần là p → kỳ vọng cần 1/p lần restart. Rất hiệu quả cho 8-queens.

## 2. Simulated Annealing

- Kết hợp hill-climbing với **random walk** để vừa hiệu quả vừa complete
- Ý tưởng: "lắc mạnh" (nhiệt độ cao) ban đầu, giảm dần cường độ (nhiệt độ) theo thời gian — mô phỏng quá trình luyện kim (annealing)
- Cho phép **đôi khi di chuyển đến state tệ hơn** với xác suất `e^(ΔE/T)` (ΔE < 0), giúp thoát local maxima
- T (temperature) giảm dần theo schedule; khi T=0 → trả về current state
- Nếu T giảm đủ chậm → thuật toán sẽ tìm được **global optimum với xác suất tiến đến 1**

## 3. Local Beam Search

- Giữ **k states** thay vì 1 (khác với chạy k lần random-restart độc lập!)
- Bắt đầu với k random state; mỗi bước sinh tất cả successor của k state, chọn lại k successor tốt nhất
- **Thông tin được chia sẻ** giữa các thread song song (khác random-restart)
- Nhược điểm: có thể mất đa dạng (diversity), cả k state hội tụ vào 1 vùng nhỏ → giống hill-climbing tốn kém
- **Stochastic beam search**: chọn k successor ngẫu nhiên có trọng số theo value (thay vì luôn chọn tốt nhất) → tăng đa dạng

## 4. Genetic Algorithms (GA)

- Biến thể của stochastic beam search: successor sinh ra bằng cách **kết hợp 2 parent state** (sexual reproduction) thay vì chỉnh sửa 1 state

### Quy trình GA

1. **Population**: tập k state ngẫu nhiên ban đầu
2. **Fitness function**: đánh giá độ tốt mỗi state (giá trị cao hơn = tốt hơn) — VD 8-queens: số cặp quân KHÔNG tấn công nhau (max = 28)
3. **Selection**: chọn cặp cha mẹ ngẫu nhiên, xác suất được chọn tỉ lệ thuận với fitness (roulette wheel)
4. **Crossover**: chọn 1 điểm cắt ngẫu nhiên, ghép nửa đầu của cha + nửa sau của mẹ → con mới
5. **Mutation**: đột biến ngẫu nhiên với xác suất nhỏ tại từng vị trí trên chuỗi

### Representation

- Mỗi state (individual) biểu diễn dưới dạng **chuỗi ký tự hữu hạn** (thường là 0/1, hoặc chuỗi số)
- VD 8-queens: 8 × log₂8 = 24 bit, hoặc 8 chữ số (1-8)

```text
function GENETIC-ALGORITHM(population, FITNESS-FN) returns an individual
  repeat
    new_population ← {}
    for i = 1 to SIZE(population):
        x ← RANDOM-SELECTION(population, FITNESS-FN)
        y ← RANDOM-SELECTION(population, FITNESS-FN)
        child ← REPRODUCE(x, y)
        if (small probability): child ← MUTATE(child)
        add child to new_population
    population ← new_population
  until đủ tốt hoặc hết thời gian
  return best individual
```

### Nhận xét về GA

- **Ưu điểm**: crossover giúp "nhảy" đến vùng search space hoàn toàn khác (random exploration mạnh); ít cần domain knowledge; liên hệ hấp dẫn đến tiến hóa sinh học
- **Nhược điểm**: nhiều tham số cần tinh chỉnh (khó tái lập trên bài toán khác); thiếu bằng chứng thực nghiệm chắc chắn rằng GA tốt hơn hill-climbing + random-restart; cần thiết kế representation cẩn thận
- Ứng dụng: **Genetic Programming**
