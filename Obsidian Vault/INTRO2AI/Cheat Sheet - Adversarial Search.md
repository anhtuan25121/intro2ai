---
tags: [intro2ai, exam, cheat-sheet]
---

# 🧠 Cheat Sheet — Adversarial Search (ôn nhanh trước giờ thi)

> Chi tiết đầy đủ: [[Lecture 5 - Adversarial Search]] · Luyện tập: [[Đề thi tham khảo - Adversarial Search]] · Cách trình bày: [[Hướng dẫn làm bài & Trình bày]]

## 1. Định nghĩa game (5 thành phần)
`S0, PLAYER(s), ACTIONS(s), RESULT(s,a), TERMINAL-TEST(s), UTILITY(s,p)`

## 2. Giả định cổ điển
Two-player · Zero-sum · Deterministic · Perfect information · Rational

## 3. Minimax
```
MAX-VALUE:  v = −∞; v = max(v, MIN-VALUE(child))
MIN-VALUE:  v = +∞; v = min(v, MAX-VALUE(child))
```
- Complete: có (nếu tree hữu hạn) · Optimal: có (vs optimal opponent)
- Time: **O(b^m)** · Space: **O(bm)**

## 4. Alpha-Beta Pruning
- **α** = best (max) choice tìm được cho MAX trên đường đi
- **β** = best (min) choice tìm được cho MIN trên đường đi
- Cắt tại MAX-VALUE khi `v ≥ β` (prune) — cập nhật `α = max(α,v)`
- Cắt tại MIN-VALUE khi `v ≤ α` (prune) — cập nhật `β = min(β,v)`
- Không đổi kết quả so với Minimax
- Best ordering → **O(b^(m/2))** → effective branching factor = **√b**
  - Chess: b≈35 → √35 ≈ **6**

## 5. Heuristic Minimax (H-MINIMAX)
- Thay TERMINAL-TEST → CUTOFF-TEST; thay UTILITY → EVAL(s)
- EVAL phải: (1) giữ thứ tự win>draw>loss, (2) tính nhanh, (3) tương quan với thắng thực tế
- Eval tuyến tính (chess material): `Eval = 9q + 5r + 3b + 3n + p`
- **Quiescence search**: mở rộng thêm ở vị trí "non-quiescent" (đang có capture) tránh horizon effect
- b^m=10⁶, b=35 → m=4 (novice) · m=8 (master) · m=12 (Deep Blue)

## 6. Expectiminimax (stochastic games)
Thêm node **CHANCE**: `value = Σ_r P(r) · EXPECTIMINIMAX(RESULT(s,r))`
(giá trị = kỳ vọng có trọng số xác suất, không phải max/min)
Ví dụ: Backgammon (dice)

## 7. Số liệu lịch sử — HỌC THUỘC

| Game | b | Không gian trạng thái | Sự kiện |
|---|---|---|---|
| **Chess** | ~35 | ~10¹⁵⁴ (tree) | **Deep Blue** thắng **Kasparov** 1997 (6 ván) — 30 CPU IBM RS/6000, 30 tỷ vị trí/nước, sâu 14–40 ply, eval ~8000 features |
| **Checkers** | — | ~10¹⁸ node | **Chinook** (1989–2007) giải hoàn toàn — alpha-beta + endgame DB 39 nghìn tỷ vị trí |
| **Go** | ~361 | ~10¹⁷⁴ | **AlphaGo** thắng **Lee Sedol** 4–1, 03/2016 — policy net + value net + MCTS |

## 8. Bảng phân loại game
| | Perfect info | Imperfect info |
|---|---|---|
| Deterministic | Chess, Checkers, Go, Othello | — |
| Chance | Backgammon, Monopoly | Bridge, Poker, Scrabble |

## 9. Multiplayer (>2 người)
Utility scalar → **utility vector**; mỗi player maximize thành phần của chính mình; có thể có alliance hình thành/tan rã.

---
## ⚡ Bẫy thường gặp
- Nhầm α/β: α gắn với **MAX** (lower bound), β gắn với **MIN** (upper bound)
- Nhầm điều kiện cắt: MAX cắt khi `v ≥ β`; MIN cắt khi `v ≤ α` (không phải ngược lại)
- Alpha-beta **không** cải thiện kết quả, chỉ cải thiện **tốc độ**
- O(b^(m/2)) chỉ đạt được với **thứ tự duyệt tối ưu** (best-case), không phải luôn luôn
- Expectiminimax node CHANCE dùng **kỳ vọng (expectation)**, không phải max hay min
