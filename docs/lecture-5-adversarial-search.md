---
layout: default
title: Lecture 5 - Adversarial Search
---

# Lecture 5 — Adversarial Search

> **TRỌNG TÂM THI GIỮA KÌ** — Đây là **nội dung duy nhất** trong đề thi closed-book. Học kỹ toàn bộ trang này.
> Xem thêm [Cheat Sheet - Adversarial Search](cheat-sheet-adversarial-search.md) để ôn nhanh trước giờ thi.

## 1. Game theory trong AI — phân loại game

Bảng phân loại game theo 2 trục: **tính ngẫu nhiên** và **mức độ quan sát**:

| | Perfect information | Imperfect information |
|---|---|---|
| **Deterministic** | Chess, Checkers, Go, Othello | — |
| **Chance** | Backgammon, Monopoly | Bridge, Poker, Scrabble |

- **Deterministic**: không có yếu tố ngẫu nhiên (xúc xắc, bốc bài...)
- **Perfect information**: mọi người chơi thấy toàn bộ trạng thái (không có quân úp/bài úp)

### Giả định cơ bản của "classic" adversarial search
1. **Two players** — MAX và MIN, chơi luân phiên
2. **Complete knowledge** — biết đầy đủ trạng thái trò chơi
3. **No chance** — không có yếu tố ngẫu nhiên
4. **Zero-sum** — tổng lợi ích 2 bên = 0 (bên này thắng thì bên kia thua tương ứng)
5. **Rational players** — cả 2 đều chơi tối ưu để tối đa hoá lợi ích của mình

## 2. Định nghĩa hình thức của Game

Một game được định nghĩa bởi:

| Thành phần | Ý nghĩa |
|---|---|
| **S₀** | INITIAL STATE — trạng thái khởi đầu |
| **PLAYER(s)** | Xác định người chơi nào đến lượt ở trạng thái s |
| **ACTIONS(s)** | Tập các nước đi hợp lệ tại s |
| **RESULT(s,a)** | Mô hình chuyển trạng thái — hàm kết quả |
| **TERMINAL-TEST(s)** | Kiểm tra s có phải trạng thái kết thúc game không |
| **UTILITY(s,p)** | Giá trị lợi ích số học của trạng thái kết thúc s đối với player p (ví dụ: thắng=+1, thua=-1, hoà=0 trong cờ vua) |

- **Search tree**: S0 là root, các nhánh là ACTIONS, các node là các trạng thái kết quả của RESULT
- **Ply**: một nước đi (move) của một người chơi (nửa lượt)

## 3. Các mốc lịch sử quan trọng (dễ ra thi dạng số liệu)

### Chess (Cờ vua)
- Branching factor **b ≈ 35**, độ sâu trung bình **d ≈ 100** ply
- Không gian tìm kiếm ≈ **10¹⁵⁴** node (search tree), trong khi chỉ có ~10⁴⁰ trạng thái hợp lệ khác nhau
- **Deep Blue** (IBM) đánh bại Garry **Kasparov** năm **1997** (6 ván)
  - 30 bộ xử lý IBM RS/6000
  - Tính được **30 tỷ vị trí mỗi nước đi**
  - Tìm kiếm sâu **14 đến 40 ply** (trung bình dùng iterative deepening)
  - Hàm đánh giá (evaluation function) dùng **~8000 đặc trưng (features)**

### Checkers (Cờ đam)
- **Chinook** (1989–2007) giải quyết hoàn toàn được checkers
- Duyệt khoảng **10¹⁸** node
- Dùng alpha-beta pruning + **cơ sở dữ liệu tàn cuộc (endgame database)** chứa **39 nghìn tỷ (39 trillion)** vị trí

### Go (Cờ vây)
- Branching factor **b ≈ 361** (bàn 19×19), không gian trạng thái ≈ **10¹⁷⁴**
- **AlphaGo** (Google DeepMind) đánh bại **Lee Sedol 4–1** vào **03/2016**
- Kết hợp **policy network + value network + Monte Carlo Tree Search (MCTS)**

## 4. Minimax Algorithm

### Ý tưởng
- MAX cố gắng **tối đa hoá** utility, MIN cố gắng **tối thiểu hoá** utility
- Từ giá trị của mỗi node lá (leaf/terminal), tính ngược lên gốc bằng cách:
  - Ở node MAX: chọn giá trị **lớn nhất** trong các con
  - Ở node MIN: chọn giá trị **nhỏ nhất** trong các con

### Công thức đệ quy

```
MINIMAX(s) =
  UTILITY(s)                                   nếu TERMINAL-TEST(s)
  max_{a ∈ Actions(s)} MINIMAX(RESULT(s,a))     nếu PLAYER(s) = MAX
  min_{a ∈ Actions(s)} MINIMAX(RESULT(s,a))     nếu PLAYER(s) = MIN
```

### Pseudocode (SGK)

```
function MINIMAX-DECISION(state) returns an action
    return arg max_{a ∈ ACTIONS(s)} MIN-VALUE(RESULT(state,a))

function MAX-VALUE(state) returns a utility value
    if TERMINAL-TEST(state) then return UTILITY(state)
    v ← −∞
    for each a in ACTIONS(state) do
        v ← MAX(v, MIN-VALUE(RESULT(state,a)))
    return v

function MIN-VALUE(state) returns a utility value
    if TERMINAL-TEST(state) then return UTILITY(state)
    v ← +∞
    for each a in ACTIONS(state) do
        v ← MIN(v, MAX-VALUE(RESULT(state,a)))
    return v
```

> **Ghi nhớ khi thi**: MAX-VALUE khởi tạo v = −∞ rồi lấy MAX; MIN-VALUE khởi tạo v = +∞ rồi lấy MIN. Rất dễ bị hỏi vẽ tay 1 cây minimax nhỏ (3-4 tầng) và tính giá trị từng node.

### Tính chất của Minimax
| Tiêu chí | Kết quả |
|---|---|
| **Complete** | Có, nếu cây hữu hạn (finite tree) |
| **Optimal** | Có, nếu đối thủ chơi tối ưu (optimal opponent) |
| **Time complexity** | O(b^m) |
| **Space complexity** | O(bm) — DFS-like, tuyến tính |

trong đó **b** = branching factor, **m** = độ sâu tối đa của cây

### Multiplayer games (>2 người chơi)
- Thay utility **vô hướng (scalar)** bằng **vector lợi ích** (mỗi phần tử là utility của 1 player)
- Mỗi node chọn hành động tối đa hoá utility của chính player đang đến lượt (thành phần tương ứng trong vector)
- Có thể xảy ra hiện tượng **liên minh (alliance)** hình thành và tan rã tuỳ theo tình huống

## 5. Alpha-Beta Pruning

### Mục đích
Cắt tỉa các nhánh **không cần thiết phải duyệt** vì chúng không thể ảnh hưởng đến quyết định cuối cùng — nhưng **không làm thay đổi kết quả** so với Minimax đầy đủ.

### Định nghĩa α, β
- **α** = giá trị của lựa chọn tốt nhất (cao nhất) mà **MAX** tìm được cho đến hiện tại trên đường đi từ gốc (dọc theo path) — "worst case tốt nhất cho MAX"
- **β** = giá trị của lựa chọn tốt nhất (thấp nhất) mà **MIN** tìm được cho đến hiện tại trên đường đi từ gốc — "worst case tốt nhất cho MIN"
- Alpha-beta **cập nhật α, β khi duyệt** và **cắt tỉa (prune)** khi phát hiện một nhánh không thể tốt hơn giá trị đã biết

### Công thức rút gọn Minimax (dùng để chứng minh cắt tỉa hợp lệ)
Giá trị minimax của root có thể tính được mà không cần xét toàn bộ cây — nếu biết một nhánh chắc chắn tệ hơn phương án đã có, ta bỏ qua nó (prune) mà **không ảnh hưởng đến quyết định ở gốc**.

### Pseudocode

```
function ALPHA-BETA-SEARCH(state) returns an action
    v ← MAX-VALUE(state, −∞, +∞)
    return the action in ACTIONS(state) with value v

function MAX-VALUE(state, α, β) returns a utility value
    if TERMINAL-TEST(state) then return UTILITY(state)
    v ← −∞
    for each a in ACTIONS(state) do
        v ← MAX(v, MIN-VALUE(RESULT(state,a), α, β))
        if v ≥ β then return v     // prune
        α ← MAX(α, v)
    return v

function MIN-VALUE(state, α, β) returns a utility value
    if TERMINAL-TEST(state) then return UTILITY(state)
    v ← +∞
    for each a in ACTIONS(state) do
        v ← MIN(v, MAX-VALUE(RESULT(state,a), α, β))
        if v ≤ α then return v     // prune
        β ← MIN(β, v)
    return v
```

> **Điều kiện cắt tỉa — rất hay thi**
> - Trong **MAX-VALUE**: nếu `v ≥ β` → **prune** (cắt), vì MIN (ở tầng trên) sẽ không bao giờ chọn nhánh này (đã có lựa chọn tốt hơn ≤ β cho MIN rồi)
> - Trong **MIN-VALUE**: nếu `v ≤ α` → **prune**, vì MAX (ở tầng trên) sẽ không bao giờ chọn nhánh này

### Ví dụ minh hoạ kinh điển (SGK — 6 node lá)
Cây có 2 nhánh con của root (2 node MIN ở tầng 2), mỗi nhánh có 2 node lá MAX ở tầng 3, mỗi node đó có các lá giá trị:
- Nhánh trái: lá = 3, 12, 8
- Nhánh phải: lá = 2, 14, 5, 2

Kết quả cuối: **giá trị root = 3**, với nhiều nhánh được cắt bỏ (không cần duyệt hết tất cả lá) mà kết quả vẫn giống hệt Minimax đầy đủ.

> **Cách vẽ tay khi thi**: Vẽ cây từ trái sang phải, duyệt DFS. Ghi giá trị α, β hiện tại tại mỗi node khi đi vào. Khi thấy điều kiện `v ≥ β` (tại MAX) hoặc `v ≤ α` (tại MIN) thì gạch chéo (cắt) các nhánh con còn lại chưa duyệt của node đó.

### Tính chất của Alpha-Beta
- **Không ảnh hưởng đến kết quả cuối cùng** (giống hệt Minimax)
- Với **thứ tự duyệt tốt nhất (good/perfect move ordering)**: độ phức tạp thời gian giảm còn **O(b^(m/2))**
  - Tương đương với việc tăng gấp đôi độ sâu tìm kiếm được trong cùng thời gian!
- **Effective branching factor** giảm còn **√b**
  - Ví dụ: cờ vua b ≈ 35 → effective branching factor còn khoảng **~6** thay vì 35
- Với thứ tự ngẫu nhiên: độ phức tạp ≈ O(b^(3m/4))
- Thứ tự duyệt tốt: nên xét các nước đi có khả năng tốt nhất trước (ví dụ: ăn quân trước, dùng heuristic ordering)

## 6. Heuristic (Cutoff) Minimax — H-MINIMAX

Vì không thể duyệt hết cây đến tận cùng (do quá sâu như cờ vua), ta:
1. Thay **TERMINAL-TEST** bằng **CUTOFF-TEST** (dừng sớm khi đạt giới hạn độ sâu, hoặc "quiescent" — xem mục Quiescence)
2. Thay **UTILITY(s)** bằng **EVAL(s)** — hàm đánh giá heuristic ước lượng độ tốt của trạng thái **không kết thúc**

```
H-MINIMAX(s, d) =
  EVAL(s)                                              nếu CUTOFF-TEST(s,d)
  max_{a} H-MINIMAX(RESULT(s,a), d+1)                  nếu PLAYER(s) = MAX
  min_{a} H-MINIMAX(RESULT(s,a), d+1)                  nếu PLAYER(s) = MIN
```

### Yêu cầu của Evaluation function EVAL(s)
1. Phải giữ đúng **thứ tự thắng > hoà > thua** (win > draw > loss ordering) của UTILITY thật
2. Việc tính toán **không được quá tốn thời gian** (phải nhanh)
3. Đối với các trạng thái không kết thúc, EVAL phải **tương quan chặt chẽ với khả năng thắng thực tế**

### Ví dụ: Eval tuyến tính cho cờ vua (material counting)
```
Eval(s) = 9·(số hậu chênh lệch) + 5·(số xe) + 3·(số tượng) + 3·(số mã) + 1·(số tốt)
        = 9q + 5r + 3b + 3n + p
```
- Đây là **hàm tổng trọng số tuyến tính (weighted linear sum of features)**
- **Hạn chế**: không nắm bắt được tương tác phi tuyến giữa các quân
  - Ví dụ: 2 tượng (bishop) mạnh hơn hẳn khi vào tàn cuộc (endgame) so với trung cuộc — hàm tuyến tính không phản ánh được điều này

### Giới hạn độ sâu tìm kiếm thực tế (Cutting off search)
Với b^m = 10⁶ khả năng tính được trong thời gian cho phép, và b = 35 (cờ vua) → **m ≈ 4**
- **4-ply**: trình độ người mới chơi (novice)
- **8-ply**: trình độ PC thông thường / kiện tướng (master)
- **12-ply**: trình độ Deep Blue khi đấu với Kasparov

### Quiescence search
- Vấn đề: dừng đánh giá ở 1 vị trí "không ổn định" (non-quiescent) — ví dụ vị trí đang có nước ăn quân (capture) sắp xảy ra — sẽ cho kết quả sai lệch (horizon effect)
- Giải pháp: **mở rộng tìm kiếm thêm** tại các vị trí non-quiescent (như đang có capture) cho đến khi đạt vị trí **"quiescent" (ổn định)** rồi mới áp dụng EVAL

## 7. Stochastic Games (Game có yếu tố ngẫu nhiên)

- Khi có yếu tố ngẫu nhiên (xúc xắc, đối thủ không thể đoán trước, hành động có thể thất bại), ta thêm **CHANCE node** vào cây trò chơi
- Ví dụ: **Backgammon** — có node CHANCE đại diện cho các kết quả tung xúc xắc, mỗi nhánh gắn xác suất tương ứng (ví dụ P = 1/36 cho một cặp xúc xắc cụ thể, 1/18 cho cặp khác do đối xứng)

### Công thức Expectiminimax

```
EXPECTIMINIMAX(s) =
  UTILITY(s)                                                nếu TERMINAL-TEST(s)
  max_a EXPECTIMINIMAX(RESULT(s,a))                          nếu PLAYER(s) = MAX
  min_a EXPECTIMINIMAX(RESULT(s,a))                          nếu PLAYER(s) = MIN
  Σ_r P(r)·EXPECTIMINIMAX(RESULT(s,r))                       nếu PLAYER(s) = CHANCE
```

- Node CHANCE: giá trị = **kỳ vọng (expected value)** = tổng của xác suất P(r) nhân với giá trị minimax của kết quả r, lấy tổng qua mọi kết quả ngẫu nhiên r có thể xảy ra
- Đây chính là điểm khác biệt cốt lõi so với Minimax thường: **có thêm 1 loại node thứ 3 (CHANCE)** ngoài MAX và MIN, và giá trị của nó là **trung bình có trọng số theo xác suất**, không phải max/min

> **Lưu ý khi thi**: Nếu đề cho một cây có node CHANCE với xác suất từng nhánh, chỉ cần: (1) tính utility/minimax value của các node lá dưới CHANCE trước, (2) nhân từng giá trị với xác suất tương ứng rồi cộng lại ra giá trị node CHANCE, (3) tiếp tục lan truyền lên trên bình thường theo MAX/MIN.

---

## Câu hỏi tự kiểm tra nhanh
1. Nêu 5 thành phần định nghĩa hình thức 1 game.
2. Viết công thức MINIMAX và độ phức tạp thời gian/không gian.
3. Alpha là gì? Beta là gì? Điều kiện cắt tỉa ở node MAX và node MIN?
4. Vì sao alpha-beta với thứ tự duyệt tốt cho complexity O(b^(m/2))? Ý nghĩa thực tế của con số này với cờ vua?
5. EVAL(s) cần thỏa mãn điều kiện gì? Cho ví dụ 1 hàm eval tuyến tính.
6. Quiescence search giải quyết vấn đề gì?
7. Expectiminimax khác Minimax ở điểm nào? Viết công thức cho node CHANCE.
8. Kể tên & năm của 3 cột mốc: Deep Blue, Chinook, AlphaGo — đối thủ là ai, thắng/thua thế nào.
