# Lab 2 — Blind Adversary (CSC14003)

Tài liệu làm việc chung của nhóm. Đọc hết mục 1-3 trước khi code.

---

## 1. Đề bài tóm tắt

Giống hệt Lab 1 (Hide and Seek Arena), **chỉ thêm partial observability**:

- Map 21×21. Ta viết 2 agent: **Pacman = Seek** (đuổi bắt) và **Ghost = Hide** (chạy trốn).
- Pacman thắng nếu chạm Ghost (Manhattan distance < 2). Ghost thắng nếu sống đủ 200 bước.
- Pacman đi 2 ô/bước theo đường thẳng (không được rẽ hình L ngay trong bước đó). Ghost đi 1 ô/bước.
- Hai bên đi **đồng thời**, không thấy nước đi của nhau trước.
- Giới hạn: **1 giây/bước**, **128MB** (Google Colab CPU-only, Python 3.11).
- Thư viện được phép: numpy, pandas, scipy, gurobi, pytorch, scikit-learn.

**Điểm mới của Lab 2 — tầm nhìn giới hạn:**

Mỗi agent chỉ nhìn thấy theo hình chữ thập: ô hiện tại + tối đa 5 ô theo 4 hướng (Up/Down/Left/Right), tia nhìn **bị chặn hoàn toàn khi gặp tường**.

Interface không đổi so với Lab 1:

```python
def step(self, map_state, my_position, enemy_position, step_number):
    # Pacman: return Move hoặc (Move, steps)
    # Ghost:  return Move (UP/DOWN/LEFT/RIGHT/STAY)
```

Khác biệt nằm ở dữ liệu truyền vào:

| | Lab 1 | Lab 2 |
|---|---|---|
| `map_state` | chỉ có `0` (trống) và `1` (tường) | thêm `-1` = ô ngoài tầm nhìn |
| `enemy_position` | luôn có giá trị | **`None` khi đối phương ngoài tầm nhìn** |

---

## 2. Sự thật kỹ thuật quan trọng nhất — đọc kỹ, đây là chỗ dễ sai nhất

Đọc source thật của framework (`labs/lab1/HideSeek/pacman/src/environment.py`, hàm `get_observation`) thì cơ chế fog hoạt động như sau:

```python
obs = self.map.copy()          # bắt đầu từ BẢN ĐỒ ĐẦY ĐỦ
for r, c in toàn bộ map:
    if (r, c) không nhìn thấy and obs[r, c] == 0:
        obs[r, c] = -1          # CHỈ ô trống mới bị che
```

Ba hệ quả:

1. **Toàn bộ tường (`1`) được cấp đầy đủ ngay từ bước 1**, không bị che. File `agent_interface.py` ghi rõ: `1 = wall (always visible)`. Nghĩa là ta biết trước cấu trúc mê cung.
2. Vì tường không bao giờ bị đổi thành `-1`, nên **`-1` = ô trống chắc chắn đi được, chỉ là hiện không nhìn thấy**.
3. → Điều kiện "ô này đi được" phải viết là **`map_state[r, c] != 1`**, KHÔNG phải `== 0`.

> ⚠️ **Nếu dùng `== 0` thì agent sẽ tê liệt.** Mỗi bước chỉ có ~20-30 ô là `0`, phần còn lại là `-1`, nên BFS/A\* không tìm được đường tới bất cứ đâu xa hơn tầm nhìn. Agent sẽ đứng im hoặc quẩn quanh tại chỗ.

Cả 3 bài mẫu top của khoá trước (`labs/lab1/HideSeek/Blind/{A,B,C}/agent.py`) đều dùng `!= 1`:

- `Blind/B/agent.py:54` → `return 0 <= r < h and 0 <= c < w and km[r, c] != 1`
- `Blind/A/agent.py:607` → `return self._is_in_bounds(pos) and self.global_map[pos] != 1`
- `Blind/C/agent.py:227` → `if 0 <= nr < h and 0 <= nc < w and map_state[nr, nc] != 1`

**Lưu ý phụ:** không hardcode con số bán kính tầm nhìn. `STUDENT_GUIDE.md:358` có ví dụ bất đối xứng (`--pacman-obs-radius 5 --ghost-obs-radius 3`) trong khi PDF nói 5 ô. Muốn biết đang nhìn thấy ô nào thì kiểm tra `map_state != -1`, đừng giả định con số.

---

## 3. Kiến trúc & phân chia module

Code chia làm 2 file, ghép qua một interface cố định:

```
lab2/init/
├── agent.py      # PacmanAgent + GhostAgent (search, minimax, pathfinding)
└── belief.py     # EnemyTracker — suy luận vị trí đối phương khi mất dấu
```

| File | Người phụ trách | Nội dung |
|---|---|---|
| `agent.py` | **Tommy - 19127616** | Kế thừa từ `labs/lab1/final/agent.py`: A\*, BFS, minimax + alpha-beta + iterative deepening, time budget, safety net. Sửa để chạy với map 3 giá trị và xử lý nhánh `enemy_position is None`. |
| `belief.py` | **19127615** | Theo dõi và ước lượng vị trí đối phương qua thời gian. Chi tiết ở mục 4. |

**Interface giữa 2 file — đã chốt, không đổi** (vì `agent.py` gọi theo đúng chữ ký này):

```python
class EnemyTracker:
    def __init__(self):
        ...

    def update(self, map_state, my_pos, enemy_pos, step):
        """Gọi mỗi bước. enemy_pos là None nếu không nhìn thấy. Không trả về gì."""
        ...

    def get_target(self, my_pos):
        """Trả về (row, col) — vị trí phỏng đoán của đối phương.
        Trả None nếu chưa đủ thông tin để đoán."""
        ...
```

Nếu thấy interface này thiếu gì thì **báo trước khi code**, đừng tự đổi giữa chừng — đổi là hỏng phần ghép.

---

## 4. Đặc tả `belief.py` — phần việc chi tiết

### Bài toán

Khi `enemy_position is None`, agent vẫn phải quyết định đi đâu. Cần một cơ chế trả lời: *"đối phương nhiều khả năng đang ở đâu?"*

Trong repo hiện có sẵn một bản tối giản chỉ nhớ vị trí thấy lần cuối. Việc cần làm là **nâng nó lên belief distribution** — mảng xác suất 21×21 cập nhật theo thời gian.

### Thuật toán — mỗi lần `update()` chạy đúng 2 pha

**Pha 1: Predict (dự đoán khuếch tán).**
Đối phương vừa đi 1 bước, nên xác suất phải lan sang các ô kề. Với mỗi ô có xác suất > 0, chia đều xác suất đó cho các ô kề **đi được** (`!= 1`) — và cả chính nó nếu đối phương được đứng yên (Ghost có `Move.STAY`).

**Pha 2: Update (cập nhật theo quan sát).**

- Nếu `enemy_pos` **có giá trị** → biết chính xác: gán toàn bộ xác suất về 0, riêng ô đó = 1.0. Xong.
- Nếu `enemy_pos is None` → mọi ô ta **đang nhìn thấy** (`map_state != -1`) chắc chắn không có đối phương → gán xác suất các ô đó = 0. Sau đó chuẩn hoá lại cho tổng = 1.

> Pha 2 nhánh `None` là phần hay nhất của thuật toán: "không nhìn thấy nó ở đây" cũng là một thông tin, và nó thu hẹp dần vùng nghi ngờ theo thời gian.

**Trường hợp biên bắt buộc xử lý:**

- Tổng xác suất về 0 (mâu thuẫn, thường do lỗi làm tròn) → reset về phân phối đều trên toàn bộ ô chưa nhìn thấy.
- Chưa từng thấy đối phương lần nào → khởi tạo phân phối đều trên mọi ô đi được.

**`get_target()`** trả về ô có xác suất cao nhất. Nếu hoà nhiều ô, chọn ô gần `my_pos` nhất (tie-break đơn giản, tránh mỗi bước nhảy target lung tung).

### Khung code để bắt đầu

```python
import numpy as np

class EnemyTracker:
    def __init__(self):
        self.belief = None          # np.ndarray (21, 21), float

    def _init_belief(self, map_state):
        walkable = (map_state != 1)
        self.belief = walkable.astype(float)
        self.belief /= self.belief.sum()

    def update(self, map_state, my_pos, enemy_pos, step):
        if self.belief is None:
            self._init_belief(map_state)
        # TODO pha 1: predict
        # TODO pha 2: update theo quan sát

    def get_target(self, my_pos):
        if self.belief is None:
            return None
        # TODO: trả ô có xác suất cao nhất
```

### Ràng buộc

- Chỉ được import `numpy` và thư viện chuẩn Python.
- **Không sửa `agent.py`.** Nếu cần agent.py đổi gì thì nhắn, đừng tự sửa.
- Cả `update()` phải chạy dưới ~50ms (agent còn phải chạy minimax trong cùng 1 giây). Mảng 21×21 thì thoải mái, chỉ cần tránh vòng lặp Python lồng nhau 4 tầng — dùng numpy vectorized nếu được.
- Bọc logic trong `try/except` hoặc kiểm tra `None` cẩn thận: agent **không được phép ném exception ra ngoài** trong bất kỳ trường hợp nào, mỗi trận chỉ chạy đúng 1 lần, crash là mất trắng trận đó.

### Tài liệu tham khảo

Đọc để hiểu nguyên lý rồi **tự cài lại theo cách hiểu của mình** — đừng copy nguyên khối, đề bài cho phép dùng AI/tham khảo nhưng giảng viên có quyền phỏng vấn miệng:

- `labs/lab1/HideSeek/Blind/B/agent.py` — hàm `_update_belief`, dòng ~187-210. Bản gọn nhất, dễ đọc nhất, nên đọc đầu tiên.
- `labs/lab1/HideSeek/Blind/C/agent.py` — hàm `_init_belief` / `_update_belief`, dòng ~198-233. Có comment tiếng Việt.
- `labs/lab1/HideSeek/Blind/A/agent.py` — đầy đủ nhất (883 dòng), có thêm dự đoán hướng và ambush. Đọc nếu còn thời gian.

### Cách test độc lập (không cần chờ `agent.py`)

Viết một script nhỏ tự tạo `map_state` giả rồi gọi `update()` liên tục, in ra ô xác suất cao nhất mỗi bước, kiểm tra 3 điều:

1. Khi thấy đối phương → `get_target()` trả đúng vị trí đó.
2. Sau khi mất dấu vài bước → vùng xác suất lan rộng dần một cách hợp lý.
3. Tổng xác suất luôn ≈ 1.0, không bao giờ NaN.

---

## 5. Chạy thử với framework

Framework của Lab 1 dùng lại được cho Lab 2, chỉ cần bật 2 cờ observation radius:

```bash
cd labs/lab1/HideSeek/pacman
python src/arena.py --seek <id> --hide example_student \
    --pacman-obs-radius 5 --ghost-obs-radius 5 \
    --pacman-speed 2 --capture-distance 2
```

Thêm `--no-viz` để chạy nhanh không hiển thị, `--delay 0.3` để xem chậm lại khi debug.

---

## 6. Checklist trước khi nộp

- [ ] Không còn chỗ nào dùng `== 0` để kiểm tra ô đi được (grep lại toàn bộ code).
- [ ] Chạy thử ở chế độ blind thật, agent di chuyển bình thường chứ không đứng im/kẹt góc.
- [ ] `enemy_position is None` không dẫn tới `STAY` vô điều kiện ở cả 2 agent.
- [ ] Không hardcode con số bán kính tầm nhìn ở bất kỳ đâu.
- [ ] Giữ nguyên `try/except` + time budget kế thừa từ Lab 1.
- [ ] Test đủ: chưa từng thấy đối phương suốt trận / thấy rồi mất dấu / xuất hiện lại sau khi mất dấu lâu.
- [ ] Đúng format nộp: `group_id.zip` chứa `group_id/agent.py` + `belief.py` cùng thư mục.

---

## 7. Ghi chú — chỗ PDF và framework nói khác nhau

Đề `Blind-2526-3.pdf` (trang 4) viết: *"students must ensure their agents treat all −1 cells as completely unknown and never blindly assume they are safe to traverse."*

Nhưng framework tham chiếu luôn giữ nguyên toàn bộ tường và chỉ che ô trống (mục 2), nên trên thực tế `-1` **luôn là ô đi được**. Hai nguồn mâu thuẫn nhau.

Hướng xử lý của nhóm: **code theo framework** (`!= 1`), vì đó là thứ thật sự chấm điểm, và vì cả 3 bài mẫu top khoá trước đều làm vậy — làm đúng theo chữ trong PDF thì agent không đi đâu được.

Nhưng cần **hiểu và giải thích được lý do** nếu bị hỏi: PDF cảnh báo về mặt nguyên tắc (đừng giả định vùng chưa quan sát là an toàn), còn bản cài đặt cụ thể của Arena thì không che tường nên rủi ro đó không tồn tại. Dẫn chứng là dòng `obs = self.map.copy()` trong `get_observation()`.

**✅ ĐÃ CHỐT (QA BlindArena Q4 — file `[FAI] QA Labs + Project.xlsx`):** giảng viên xác nhận trực tiếp:
- Đổi `obs_radius` từ 0 sang >0 là framework tự chuyển sang fog-of-war, tự quyết `enemy_position = None` và tự che vùng ngoài tầm nhìn → **framework này chính là thứ chấm điểm, không có bản riêng.**
- `map_state` mà agent nhận **chỉ chứa quan sát** (không phải map thật của environment), và cách đọc `visible = map_state != -1; global_map[visible] = map_state[visible]` được giảng viên nói rõ **"không vi phạm luật"**.
- "the agent should have no way to break the rules to get the position of opponent if it is outside of your visibility" → cứ tin `enemy_position`/`map_state` framework đưa.

→ Hướng `!= 1` là đúng và an toàn để trả lời vấn đáp. Lưu ý nhỏ: QA không nhắc lại nguyên văn câu "tường luôn hiện", nên dẫn chứng cho riêng ý đó vẫn là dòng `obs = self.map.copy()` trong `get_observation()` — mà QA đã xác nhận file đó là framework chấm thật.

---

## 8. Tài nguyên có sẵn trong repo

- `labs/lab1/HideSeek/Blind/{A,B,C}/agent.py` — 3 bài top khoá trước, **đúng chế độ Blind**, 657-883 dòng. Nguồn tham khảo giá trị nhất.
- `labs/lab1/HideSeek/pacman/src/` — framework đầy đủ, dùng lại được ngay qua cờ obs-radius.
- `labs/lab1/final/scripts/{sync_bench.py,run_tournament.py}` — hạ tầng benchmark tự động của Lab 1, thêm 2 cờ obs-radius là chạy được cho Lab 2.
- `labs/lab1/final/tests/test_agent.py` — 42 unit test, tái dùng khung để test agent Lab 2.
- `labs/lab1/final/explain.md` — giải thích chi tiết từng phần của `agent.py` Lab 1 (minimax, alpha-beta, iterative deepening, safety net). Đọc nếu muốn hiểu phần `agent.py` đang kế thừa.

---

## 9. QA đã chốt (từ `[FAI] QA Labs + Project.xlsx`)

Những điều giảng viên đã trả lời, ảnh hưởng trực tiếp tới cách làm — đọc trước khi tối ưu:

1. **Cách chấm: mỗi cặp match chạy ĐÚNG 1 lần, vị trí start CỐ ĐỊNH** (HideSeek Q5, BlindArena Q3). Không có trung bình nhiều seed như lúc mình benchmark — một trận xui là mất luôn. → Ưu tiên **độ ổn định/không crash** hơn là tối ưu ăn may. Không được để timeout hay STAY chết kẹt.
2. **Tie-break = average completion step** (HideSeek Q4). Khi hoà win-rate thì xét `(avg Pacman step − avg Ghost step)`. → **Pacman phải bắt NHANH** (ít bước — A* đường ngắn nhất đang đúng hướng), **Ghost phải sống LÂU** (kéo đủ 200 bước càng tốt). Không chỉ thắng, mà thắng cho gọn.
3. **Agent của mình KHÔNG đấu với chính mình khi chấm** (HideSeek Q3): Pacman của mình đấu Ghost nhóm khác và ngược lại. → Phải bền với đối thủ lạ, đừng chỉ test với `example_student`. Được phép self-play để quan sát.
4. **128MB là RAM, tính CẢ arena + mọi thư viện import** (BlindArena Q2). → Giữ `belief.py` chỉ `numpy`. Ý tưởng ML (pytorch/sklearn) ở mục để-dành phải cân nhắc kỹ RAM, dễ vượt hạn.
5. **Framework hiện tại chính là bản chấm** (BlindArena Q4) — xem §7, vấn đề PDF-vs-framework coi như đã xử lý.
6. Có **reference grading sheet** (link trong sheet `HideSeek` ô E1 — "this is NOT YOURS", chỉ để tham khảo tiêu chí).
