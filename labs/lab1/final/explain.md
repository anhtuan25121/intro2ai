# Giải thích `final/agent.py` — từng đoạn, và vì sao khác `init/agent.py`

> Mục đích file này: để tự đọc lại và **tự giải thích được bằng lời của mình** khi bị hỏi trực tiếp — không phải để học thuộc. Đọc kèm `overview.md` và `plan.md` (đặc biệt mục 9, 11, 13) để có đầy đủ bối cảnh thực nghiệm đứng sau mỗi quyết định.
>
> Quy ước: mỗi mục nêu **(1) đoạn code nói gì**, **(2) khác `init` chỗ nào**, **(3) vì sao khác — có bằng chứng gì** (nếu có).

---

## 0. Bức tranh tổng: cái gì giữ nguyên, cái gì mới

| Phần | `init/agent.py` | `final/agent.py` | Đổi hay giữ |
|---|---|---|---|
| Helper (`is_valid`, `get_neighbors`, `manhattan`, `bfs_distances`) | Có, module-level, dùng chung 2 class | Y hệt logic, chỉ bỏ bớt comment 1-dòng/hàm | **Giữ** |
| `astar` | Có | Y hệt | **Giữ** |
| `PacmanAgent` | A* thuần, không try/except | A* y hệt + bọc try/except | **Gần như giữ**, chỉ thêm lớp an toàn |
| `GhostAgent` | Greedy 0-ply: `BFS distance × 10 + mobility` | Minimax + alpha-beta + iterative deepening, greedy cũ lùi thành fallback | **Viết lại hoàn toàn** |
| Tổng độ dài | 148 dòng | 308 dòng | +160 dòng, gần hết nằm ở Ghost mới |

**Một câu tóm tắt để trả lời khi bị hỏi "khác nhau ở đâu":** *Pacman gần như không đổi vì đã tối ưu gần trần (15/15 thắng); toàn bộ công sức dồn vào việc thay Ghost từ "chạy xa Pacman 1 bước, không nhìn trước" sang "mô phỏng trước vài lượt đối đáp qua lại giữa 2 bên bằng minimax, nhưng vẫn giữ logic cũ làm phương án dự phòng khi lỗi".*

---

## 1. Constants và exception phụ trợ

```python
MOVES = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
CAPTURE_DIST = 2
ASSUMED_PACMAN_SPEED = 2
TIME_BUDGET = 0.65
MAX_DEPTH = 10

class _SearchTimeout(Exception):
    pass
```

- `CAPTURE_DIST = 2`: khớp đúng luật đề bài — "bắt được khi Manhattan distance < 2" (PDF trang 3). Không phải số tự chọn.
- `ASSUMED_PACMAN_SPEED = 2`: khớp đúng luật đề bài — "Seek Agent moves at a speed of 2 cells per step" (PDF trang 3, mục "About the speed"). **Đây từng bị nghi ngờ là bug trong lúc thảo luận** (tưởng default là 1 theo `arena.py`), nhưng đọc lại PDF xác nhận tốc độ 2 là **bắt buộc theo luật thật**, không phải giả định tuỳ ý — nên giữ nguyên.
- `TIME_BUDGET = 0.65`: đề bài giới hạn 1s/bước (PDF mục Notices). Chọn 0.65s để chừa biên an toàn ~0.35s phòng máy chấm (Colab CPU-only) chậm hơn máy dev — đã đo thực tế bước chậm nhất của Ghost chỉ tốn đúng 0.65s (`plan.md` mục 11, bảng kiểm chứng thực nghiệm).
- `MAX_DEPTH = 10`: trần trên lý thuyết, thực tế hầu như không bao giờ chạm tới vì hết `TIME_BUDGET` trước — chỉ là chốt chặn an toàn tránh đệ quy vô hạn nếu thời gian đo sai lệch bất thường.
- `_SearchTimeout`: exception tự định nghĩa, dùng để "ngắt" đệ quy `_minimax` giữa chừng khi hết giờ (xem mục 4).

**Khác `init`:** `init` không có khối constants này (không cần, vì không có search có depth/time budget). Đây là phần mới hoàn toàn cho Ghost.

---

## 2. Helper dùng chung

```python
def is_valid(pos, map_state): ...
def get_neighbors(pos, map_state): ...
def manhattan(a, b): ...
def astar(map_state, start, goal): ...
def bfs_distances(map_state, start): ...
```

Logic **y hệt `init`** — kiểm tra ô hợp lệ, liệt kê ô kề, khoảng cách Manhattan, A* tìm đường, BFS tính khoảng cách thật tới mọi ô. Vẫn là hàm module-level dùng chung cho cả `PacmanAgent` và `GhostAgent`, không viết riêng cho từng class (đây là điểm sạch — tránh trùng lặp code, một lỗi khá phổ biến ở nhiều bài khác trong lớp).

**Khác `init`:** duy nhất là **mất các comment 1-dòng** mà `init` có phía trên mỗi hàm (ví dụ `init` có "# Kiểm tra ô có đi được không" trên `is_valid`). Không phải lỗi kỹ thuật, chỉ là đánh đổi phong cách — các hàm này đủ ngắn/rõ để tự giải thích qua tên hàm, nhưng nếu người đọc hoàn toàn mới thì `init` định hướng nhanh hơn một chút.

```python
def pacman_step_positions(pos, move, map_state, speed=ASSUMED_PACMAN_SPEED): ...
def pacman_actions(pos, map_state): ...
```

**Hoàn toàn mới, không có trong `init`.** Hai hàm này mô phỏng: "nếu Pacman đi thẳng theo hướng `move`, nó có thể dừng lại ở tối đa bao nhiêu ô khác nhau (tối đa `speed` ô, dừng sớm nếu đụng tường)" và "toàn bộ vị trí Pacman có thể đến được trong 1 lượt (đứng yên, hoặc đi 1/2 ô theo 4 hướng)". Cần thiết vì **minimax phải mô phỏng đúng luật tốc độ x2 của Pacman** khi tính lượt "MIN" trong cây tìm kiếm — nếu chỉ cho Pacman đi 1 ô/lượt trong mô phỏng, Ghost sẽ đánh giá thấp tầm với thật của đối thủ (đúng lỗi mà nhóm 10 mắc phải, ghi trong `class_overview_review.md` mục 3).

---

## 3. `PacmanAgent`

```python
class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))

    def step(self, map_state, my_position, enemy_position, step_number):
        try:
            ...
            path = astar(map_state, my_pos, target)
            ...
        except Exception:
            return (Move.STAY, 1)
```

Logic A* **y hệt `init`** — tìm đường ngắn nhất tới Ghost bằng A*, rồi đi thẳng tối đa `pacman_speed` ô nếu các bước kế tiếp cùng hướng.

**Khác `init` duy nhất:** toàn bộ thân hàm được bọc trong `try/except Exception: return (Move.STAY, 1)`.

**Vì sao thêm mà không đổi thuật toán:** đã tự thử nghiệm thêm tính năng "dự đoán hướng đi của Ghost" (nội suy tuyến tính từ 2-3 vị trí quan sát gần nhất) để chặn đầu thay vì đuổi theo vị trí hiện tại. Kết quả benchmark ban đầu (30 trận) cho thấy có 1 trận tệ hơn — nhưng khi kiểm tra lại kỹ, phát hiện 2 đối thủ trong bộ test dùng `random.choice()` không seed, nên chênh lệch đó là nhiễu ngẫu nhiên từ đối thủ, không phải do tính năng dự đoán. Sau khi seed `random.seed(42)` và chạy lại, kết quả **giống hệt nhau tuyệt đối** giữa có/không có dự đoán (`plan.md` mục 10). Quyết định cuối: **bỏ tính năng dự đoán** — không phải vì nó có hại, mà vì nó không mang lại lợi ích đo được trong khi làm code phức tạp hơn không cần thiết. Giữ nguyên A* thuần, chỉ thêm `try/except` cho an toàn.

---

## 4. `GhostAgent` — phần viết lại hoàn toàn

### 4a. Vì sao viết lại thay vì giữ greedy cũ

`init` chọn nước đi bằng cách nhìn **đúng 1 bước** (0-ply): với mỗi ô kề, tính `BFS-distance-tới-Pacman × 10 + số ô kề đi được`, chọn ô điểm cao nhất. Đây là greedy thuần, không mô phỏng trước các lượt đối đáp qua lại. Trong 16 bài của lớp, 14/15 nhóm khác đều có ít nhất một dạng nhìn trước (minimax, flood-fill, Voronoi) — nhóm 0 (mình) là Ghost yếu nhất lớp về mặt thiết kế thuật toán (`class_overview_review.md` mục 3). Đây là lý do trực tiếp khiến việc viết lại Ghost trở thành ưu tiên cao nhất cho bản final.

### 4b. `_prepare_map`

Tính trước "độ" (số ô kề đi được) của **mọi** ô trên bản đồ, chỉ chạy 1 lần (`self._map_ready` chặn chạy lại). Dùng làm thành phần `open_degree` trong hàm đánh giá — tránh phải tính lại số ô kề cho từng node trong cây minimax.

### 4c. `_evaluate` — hàm đánh giá heuristic

```python
dist = manhattan(ghost_pos, pac_pos)
degree = self._degree.get(ghost_pos, 0)
score = dist * 10 + degree * 3
if degree <= 1:
    score -= 20
if ghost_pos == self._prev_pos:
    score -= 2
```

**Đây là chỗ quan trọng nhất để hiểu, vì có lịch sử debug thật đứng sau nó.**

Bản nháp đầu tiên không dùng `manhattan` ở đây — dùng một **bản đồ khoảng cách BFS tính 1 lần từ vị trí Pacman thật ở đầu lượt** (`pac_dist_map`), tra cứu lại cho mọi node trong cây minimax. Nghe hợp lý hơn (BFS chính xác hơn Manhattan vì có tính tường) nhưng **gây bug nghiêm trọng**: vị trí Pacman *mô phỏng* trong cây có thể trôi xa vị trí thật sau vài nước giả lập, nên tra cứu vào bản đồ cũ (tính từ vị trí ban đầu) cho ra khoảng cách sai — Ghost tưởng đang an toàn dựa trên thông tin cũ trong khi Pacman mô phỏng đã áp sát. Hậu quả đo được: Ghost bị bắt trong **9 bước** thay vì 200 bước như bản greedy cũ, trước cùng một đối thủ `example_student` (`plan.md` mục 9).

→ Sửa bằng cách dùng `manhattan(ghost_pos, pac_pos)` — khoảng cách **sống**, tính lại tại đúng node đang xét, giữa 2 vị trí *mô phỏng* thật sự ở node đó (không tra bản đồ tĩnh). Đổi lại chấp nhận Manhattan kém chính xác hơn BFS (bỏ qua tường) — nhưng đúng còn hơn nhanh mà sai.

**Câu hỏi phỏng vấn dễ gặp nhất:** *"Tại sao không dùng BFS cho chính xác mà lại dùng Manhattan?"* → Trả lời: đã thử BFS-tĩnh trước, gây bug thực tế (9 bước vs 200 bước), lý do là vị trí mô phỏng trôi khỏi vị trí tính bản đồ ban đầu. Manhattan tính lại tại từng node tuy kém chính xác về mặt hình học (không biết tường) nhưng luôn phản ánh đúng 2 vị trí đang xét ngay lúc đó — ưu tiên đúng hơn ưu tiên chính xác tuyệt đối.

Phần cộng thêm (`degree * 3`, phạt `-20` khi vào ngõ cụt, phạt nhẹ `-2` khi quay lại vị trí cũ): các trọng số này **là số viết tay, chưa tách thành hằng số có tên** — đây là điểm còn có thể cải thiện (đã tự nhận ở phần review clean-code trước).

### 4d. `_minimax` — minimax + alpha-beta

```python
if manhattan(ghost_pos, pac_pos) < CAPTURE_DIST:
    return -100000 - depth
if depth == 0:
    return self._evaluate(ghost_pos, pac_pos)
if maximizing:   # lượt Ghost — muốn score cao
    ...
else:            # lượt Pacman — giả định muốn score thấp (dồn Ghost vào bí)
    candidates = pacman_actions(pac_pos, map_state)  # có cả bước 2 ô
    ...
```

- Ghost là người **maximize** (muốn điểm cao = càng xa/càng an toàn càng tốt).
- Pacman được mô phỏng là người **minimize** (giả định đối thủ chơi tối ưu, luôn chọn nước dồn Ghost vào thế tệ nhất) — đúng giả định cổ điển của minimax (xem `lecture-5-adversarial-search.md` mục 1: "Rational players").
- Bị bắt (`< CAPTURE_DIST`) trả về điểm cực thấp, **trừ thêm theo `depth`** — nghĩa là bị bắt càng sớm (còn nhiều depth chưa dùng) càng bị phạt nặng hơn bị bắt muộn. Đây là cách khuyến khích Ghost "trì hoãn cái chết" ngay cả khi không tránh được, khớp với tiêu chí chấm điểm thật (avg-Ghost-steps càng cao càng tốt, kể cả khi vẫn thua — xem QA #4).
- Alpha-beta cắt tỉa (`if alpha >= beta: break`) — **không đổi kết quả so với minimax đầy đủ, chỉ giúp chạy nhanh hơn để có thời gian tìm sâu hơn trong cùng ngân sách thời gian** (đúng tính chất đã học ở `cheat-sheet-adversarial-search.md`: "Alpha-beta không cải thiện kết quả, chỉ cải thiện tốc độ").
- Ở lượt Pacman, dùng `pacman_actions` (không phải chỉ 4 hướng 1 ô) — mô phỏng đúng luật tốc độ x2, tránh lỗi đánh giá thấp tầm với của Pacman.

**Khác `init`:** toàn bộ hàm này không tồn tại trong `init` — `init` không có bất kỳ dạng nhìn trước nào.

### 4e. `_greedy_fallback`

**Chính là logic Ghost của `init`, copy gần như nguyên văn** (`BFS distance × 10 + mobility`), chỉ thêm tham số `dist_map=None` để có thể tái dùng bản đồ BFS đã tính sẵn ở nơi gọi thay vì tính lại (tối ưu nhỏ, không đổi logic — đã re-test xác nhận kết quả giống hệt trước/sau khi thêm tham số này, `plan.md` mục 11).

**Vai trò:** dùng làm **phương án dự phòng** khi minimax lỗi hoặc hết giờ ngay từ vòng đầu tiên (chưa có kết quả depth nào hoàn chỉnh).

### 4f. `_search_best_move` — iterative deepening

```python
best_move = self._greedy_fallback(...)   # khởi tạo bằng nước đi an toàn
depth = 1
while depth <= MAX_DEPTH and time.perf_counter() < deadline:
    try:
        ... tính điểm cho từng nước đi ở depth hiện tại ...
        if local_best_move is not None:
            best_move = local_best_move   # chỉ ghi đè khi depth này chạy xong trọn vẹn
    except _SearchTimeout:
        break
    depth += 1
return best_move
```

Tăng dần độ sâu tìm kiếm 1, 2, 3... Mỗi độ sâu chạy xong trọn vẹn mới cập nhật `best_move` — nếu hết giờ giữa chừng ở một độ sâu, `_SearchTimeout` được bắt và dừng vòng lặp, **giữ nguyên kết quả của độ sâu hoàn chỉnh gần nhất** (không bao giờ dùng kết quả nửa vời). Đây chính là kỹ thuật "H-MINIMAX" đã học — thay `TERMINAL-TEST` bằng `CUTOFF-TEST` (giới hạn thời gian) và không có `UTILITY(s)` thật (vì game chưa kết thúc) nên dùng `EVAL(s)` xấp xỉ (xem `lecture-5-adversarial-search.md` mục 6).

**Khác `init`:** hoàn toàn mới — `init` không có khái niệm độ sâu hay deadline.

### 4g. `step` — 2 lớp an toàn

```python
try:
    ...
    move = self._search_best_move(...)
    return move
except Exception:
    try:
        move = self._greedy_fallback(...)
        return move
    except Exception:
        return Move.STAY
```

3 tầng: (1) thử minimax đầy đủ; (2) nếu lỗi bất kỳ đâu (kể cả lỗi ở bước đầu `tuple(my_position)`) → lùi về greedy đơn giản; (3) nếu cả greedy cũng lỗi (bản đồ dị dạng...) → trả `Move.STAY`, không bao giờ để exception thoát ra ngoài.

**Vì sao cần kỹ đến vậy:** theo luật đề bài, mỗi cặp đấu **chỉ chạy đúng 1 lần** (QA #5) — một lỗi runtime là mất trắng cả trận, không có cơ hội chạy lại. `init` không có lớp bảo vệ nào — đây là rủi ro thật, không phải lý thuyết (đã xảy ra thật với timeout của 2 nhóm khác trong 240 trận chính thức, theo `class_overview_review.md` mục 3).

Một chi tiết đã cân nhắc kỹ và **chủ động giữ nguyên, không sửa**: `except Exception` ở đây vô tình bắt luôn cả lỗi timeout do framework bắn ra qua cơ chế báo hiệu hệ thống khi hết 1 giây — nghĩa là nếu đúng lúc đó agent đang chạy, lỗi sẽ bị nuốt và agent tự trả về một nước đi hợp lệ thay vì thua thẳng. Đã đo thực tế: bước chậm nhất của Ghost chỉ tốn 0.65s (đúng bằng `TIME_BUDGET`), còn cách xa mốc 1s, nên tình huống này gần như không xảy ra được trong thực tế với biên an toàn hiện tại (`plan.md` mục 11, phát hiện #1).

---

## 5. Bảng tổng hợp lý do — dùng để trả lời nhanh khi bị hỏi

| Câu hỏi có thể gặp | Trả lời ngắn |
|---|---|
| Vì sao Pacman gần như không đổi? | Đã tối ưu gần trần (15/15 thắng, ~9.7 bước), lợi ích thêm rất nhỏ so với rủi ro thêm bug |
| Vì sao Ghost đổi hoàn toàn? | Là Ghost yếu nhất lớp (0-ply), nút thắt cổ chai duy nhất theo review 16 nhóm |
| Vì sao eval dùng Manhattan sống, không dùng BFS tĩnh? | Đã thử BFS tĩnh trước, gây bug thật (bắt trong 9 bước thay vì 200) vì vị trí mô phỏng trôi khỏi bản đồ tính sẵn |
| Vì sao bỏ tính năng dự đoán hướng Ghost cho Pacman? | Test lại có kiểm soát random-seed cho thấy không có lợi ích thật, chênh lệch ban đầu là do đối thủ dùng random không seed |
| Vì sao Ghost có try/except 2 lớp mà Pacman chỉ 1 lớp? | Ghost có search phức tạp hơn (nhiều điểm có thể lỗi: minimax, timeout) nên cần lớp giữa (greedy fallback) trước khi lùi về STAY; Pacman logic đơn giản hơn, 1 lớp đã đủ |
| Vì sao dùng alpha-beta? | Không đổi kết quả so với minimax thường, chỉ giúp chạy nhanh hơn để tìm được độ sâu lớn hơn trong cùng ngân sách thời gian |
| Vì sao `ASSUMED_PACMAN_SPEED = 2`, không phải 1? | Khớp đúng luật đề bài (PDF): Pacman luôn được đi tốc độ x2 để đảm bảo có thể bắt được Ghost |
| Bản final có thắng Ghost nhiều hơn init không? | **Không** — test kiểm soát chặt trên đủ cả 15 đối thủ (không chỉ tập con) cho Total Win **hoà tuyệt đối 16-16**, và final còn hơi kém hơn ở tie-break (xem mục 9). Giá trị thật nằm ở an toàn (try/except) và giá trị kỹ thuật/học thuật, không phải điểm số |
| Vì sao không dùng depth cố định cho đơn giản, đỡ phải giải thích iterative deepening? | Đã thử thật (xem mục 8) — depth cố định 3-8 đều mất trận thắng thật duy nhất (Ghost sống 200 bước trước Pacman #11 yếu, tụt xuống chỉ còn 11 bước); tăng depth lên 15 để cứu lại thì bị treo hơn 2 phút. Không có depth cố định nào vừa đủ sâu vừa an toàn cho mọi tình huống - đó là lý do bắt buộc phải dùng iterative deepening + time budget |

---

## 6. Giới hạn còn lại, tự nhận thẳng (không né tránh)

- Trọng số trong `_evaluate` (`×10`, `×3`, `-20`, `-2`) là số viết tay, chưa tách hằng số có tên/giải thích — nếu bị hỏi "sao chọn đúng mấy số này", câu trả lời thật là: thử vài giá trị qua self-play quan sát trực quan, chưa có quy trình tuning bài bản (grid search/tối ưu hoá tham số).
- Ghost mới, xét trên toàn bộ 15 đối thủ (không phải tập con đã chọn lọc), **hoà tuyệt đối** với Ghost cũ (`init`) về Total Win, và **kém hơn một chút** ở tie-break — chi tiết và con số cụ thể ở mục 9. Giá trị thực sự của việc viết lại nằm ở an toàn (try/except) và giá trị kỹ thuật khi trình bày, không phải ở việc "Ghost mới mạnh hơn".
- Có đúng 1 đối thủ (kiểu Pacman dùng BFS + cache đường đi, chỉ replan khi Ghost dịch ≥2 ô) khiến minimax của final chọn nước **tệ hơn hẳn** greedy đơn giản (kém 10 bước) — chưa root-cause được chính xác vì sao, chỉ biết là có thật (mục 9). Nếu bị hỏi "Ghost mới có nhược điểm gì không", đây là câu trả lời trung thực nhất.

## 7. Unit test tự động (`final/tests/test_agent.py`)

Đã bù lỗ hổng "không có unit test" — viết `unittest` thuần, 42 test, import trực tiếp `final/agent.py`. Chạy:
```bash
source labs/lab1/.venv/bin/activate
python labs/lab1/final/tests/test_agent.py
```
Bao phủ helper thuần, logic nội bộ Ghost (`_evaluate`, `_minimax`, `_greedy_fallback`), và hành vi tổng thể `step()` của cả 2 agent (kể cả khi input dị dạng, khi `TIME_BUDGET` bị ép hết ngay từ đầu). Có 1 test hồi quy: so `_greedy_fallback` với đúng công thức gốc của bản `init` để phát hiện sớm nếu refactor sau này vô tình đổi logic fallback.

## 8. Đã thử đơn giản hoá Ghost để dễ giải thích hơn — đo được cái giá thật, quyết định giữ nguyên

Lo ngại bộ máy Ghost (minimax + alpha-beta + iterative deepening + time budget) quá phức tạp so với trình độ "vừa học AI", đã thử thay bằng minimax thuần depth cố định (bỏ hẳn alpha-beta/iterative deepening/time budget), với giả thuyết ban đầu: lợi ích của bộ máy phức tạp này không đáng kể.

**Benchmark thật (30 trận) cho thấy giả thuyết sai** — Total Win giảm 17 → 15, vì mất đúng 1 trận: Ghost từng sống 200 bước trước Pacman #11 (yếu/chậm) nay chỉ sống 11 bước như bình thường. Thử tăng depth cố định lên 4-8 vẫn không cứu được trận đó (depth=8 đã tốn 0.768s/bước — sát ngưỡng 1s); thử depth=15 (kèm alpha-beta) thì bị **treo hơn 2 phút**.

**Kết luận:** không có depth cố định nào vừa đủ sâu để hữu ích vừa đủ nông để an toàn cho mọi tình huống. Iterative deepening + time budget là cách DUY NHẤT tự động tìm đúng độ sâu tối đa an toàn theo từng tình huống — một lý do kỹ thuật chính đáng, không phải chỉ để "cho có vẻ kỹ thuật". Đã khôi phục lại bộ máy đầy đủ; số liệu benchmark sau khi khôi phục **giống hệt** trước khi thử đơn giản hoá (xem `plan.md` mục 13 để có bảng số liệu chi tiết của cả 2 lần thử).

**Đây gần như chắc chắn là câu hỏi phỏng vấn tốt để chuẩn bị**: "sao không dùng depth cố định cho đơn giản?" — giờ có câu trả lời bằng số liệu thật tự đo, không phải chỉ lý thuyết suông.

## 9. Kiểm chứng nghiêm ngặt nhất: cho `init` và `final` chạy qua ĐÚNG cùng 1 harness, cùng 15 đối thủ

Các benchmark trước đó (mục 8, và các lần test trước) so sánh `final` với số liệu "chính thức" của `init` (2 nguồn dữ liệu khác nhau), hoặc chỉ test trên 1 tập con 10/15 đối thủ. Để chắc chắn, đã cho cả `init/agent.py` và `final/agent.py` cùng chạy qua đúng 1 script, cùng seed, cùng đủ 15 đối thủ:

| | INIT | FINAL |
|---|---|---|
| Win Ghost | 1/15 | 1/15 |
| Avg Ghost steps | 24.600 | 24.067 |
| **Total Win** | **16** | **16** |
| **Tie-break** (`avg_pacman − avg_ghost`, thấp hơn = tốt hơn) | **−14.867** | **−14.333** |

**Total Win hoà tuyệt đối. Tie-break nhỉnh về phía INIT** — nếu áp đúng công thức xếp hạng thật, INIT xếp hạng cao hơn FINAL một chút, không phải ngược lại.

Soi từng trận: phía Pacman **giống hệt 100%** trên cả 15 đối thủ (đúng kỳ vọng, logic không đổi). Phía Ghost, 13/15 trận giống hệt, lệch đúng 2 trận:
- **Đối thủ dạng nhóm 2** (Pacman dùng BFS + cache đường đi, chỉ replan khi Ghost dịch ≥2 ô): INIT sống 22 bước, FINAL chỉ sống **12 bước** — **minimax tệ hơn hẳn greedy** ở matchup này.
- Đối thủ dạng nhóm 5: INIT 11 bước, FINAL 13 bước — minimax tốt hơn +2.

**Vì sao trận thua (nhóm 2) chưa từng bị phát hiện trước đây:** benchmark 10-đối-thủ dùng ở mục 8 chỉ chọn 4,5,6,7,9,11,13,14,15,16 — **bỏ sót đúng đối thủ gây ra khoản lỗ lớn nhất**. Bài học: benchmark trên tập con dễ bỏ sót matchup xấu, phải test đủ toàn bộ đối thủ mới kết luận chắc được.

**Nếu bị hỏi thẳng "vậy final có tốt hơn init không"**: câu trả lời trung thực là *"không đo được lợi ích rõ ràng nào cả — hoà Total Win, còn hơi kém ở tie-break. Lý do giữ bản final không phải vì nó thắng nhiều hơn, mà vì an toàn hơn (không crash/timeout) và thể hiện đúng thuật toán trọng tâm của môn học (minimax + alpha-beta)."*
