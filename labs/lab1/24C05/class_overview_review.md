# Đánh giá tổng quan mặt bằng chung — Hide and Seek Arena (24C05)

> Tổng hợp từ: review code nhóm 0, phân tích `results.csv` (240 trận), QA file `[FAI] QA Labs + Project.xlsx`, và đọc code 15 nhóm còn lại (2–16).

## 1. Vị trí của nhóm 0 trong lớp

| Vai trò | Kết quả thực tế (results.csv) | Thuật toán | Đánh giá |
|---|---|---|---|
| Pacman (Seek) | **15/15 thắng**, trung bình ~9.7 bước bắt được | A* thuần (heap, Manhattan heuristic) | Mạnh, gần trần, ngang tier với nhóm 6 |
| Ghost (Hide) | **2/15 thắng** (1 trận là do đối thủ timeout, thắng thật chỉ 1/15) | Greedy: `BFS distance × 10 + mobility`, 0-ply | **Yếu nhất trong toàn bộ 16 nhóm được khảo sát** |

**Kết luận cốt lõi:** Ghost là nút thắt cổ chai duy nhất. Pacman đã tối ưu gần trần, cải thiện thêm có lợi ích biên rất nhỏ. Toàn bộ nỗ lực cho bản final nên dồn vào việc viết lại Ghost.

## 2. Bảng phân loại trình độ toàn lớp (Pacman / Ghost)

| Nhóm | Pacman | Ghost | Ghi chú nổi bật |
|---|---|---|---|
| **0 (mình)** | Search-based (A*) | **Reactive/greedy 0-ply** | Ghost yếu nhất cả lớp — không có lookahead |
| 2 | Search-based (BFS) | Adversarial (minimax d4 + alpha-beta) | Không time budget, branching dễ nổ |
| 3 | Search-based+ (all-pairs BFS + 1-ply minimax) | Heuristic-aware (safety margin, haven cells, không lookahead thật) | Bảng lookup O(1)/bước |
| 4 | Hybrid (A* + minimax d3) | **Adversarial, mạnh** (dự đoán 3 lượt, dead-end map) | Có bug crash khi chưa từng thấy Pacman |
| 5 | Adversarial (minimax d4 + AB) | Heuristic-aware (feature-weighted, không lookahead) | Không try/except |
| 6 | Search-based (A* — giống nhóm 0) | **Adversarial, mạnh** (minimax d4 + topology bonus/penalty ±20/-100) | Không try/except, không time budget |
| 7 | Hybrid (BFS ↔ minimax d6, chuyển theo khoảng cách) | Sophisticated planning (BFS mục tiêu chiến lược + dead-end precompute + line-break) | Không try/except |
| 8 | Search-based (BFS) | **Adversarial, best-in-class** (iterative deepening d1-19, budget 0.85s, flood-fill safe-area) | Có safety net đầy đủ |
| 9 | Adversarial (minimax d3, tick-based BFS) | Adversarial (minimax d3 + dead-end penalty) | Kiến trúc sạch, không time budget |
| 10 | Search-based (BFS + anti-oscillation) | Shallow minimax d2, Manhattan-only, **bỏ qua pacman_speed** | Ghost yếu thứ nhì cả lớp |
| 11 | Search-based+ (A* + dự đoán vận tốc Ghost để chặn đầu) | Adversarial (minimax d3, eval giàu: Voronoi, tunnel-horizon) | Không try/except, dễ crash |
| 12 | Search-based (BFS) — **bug crash khi enemy=None** | Adversarial nhưng depth=10, không time budget | Rủi ro nhất nhóm 11-13 |
| 13 | Adversarial (iterative deepening minimax d1-6) | Adversarial (dùng chung engine với Pacman) | **Robust nhất lớp**: time budget cứng 0.6s + try/except fallback về greedy |
| 14 | Hybrid (A* + minimax d3) | Adversarial (minimax 4-ply, territory-control: flood-fill + dead-end) | Không time budget/try-except |
| 15 | Adversarial (minimax d4, symmetric 2 bên) | Adversarial (minimax d4, symmetric) | Thiết kế nguyên bản nhất, nhưng zero safety net |
| 16 | Hybrid (A* + minimax d2-3, time budget 0.82s, try/except) | Heuristic race/Voronoi "spare time" (không minimax) | Ghost có bug crash khi mất tầm nhìn; nhiều code thừa không dùng cho Ghost |

## 3. Nhận xét theo từng khía cạnh

### Pacman
Đa số các nhóm dùng search-based (BFS/A*) hoặc hybrid (BFS/A* + minimax khi ở gần). Nhóm 0 nằm ở tier trung bình, kết quả thực tế đã rất tốt (15/15, ~9.7 bước). Ý tưởng đáng học nếu muốn tối ưu thêm: **nhóm 11** ước lượng vận tốc/hướng của Ghost từ các lần quan sát liên tiếp để chặn đầu (intercept) thay vì đuổi theo vị trí hiện tại — một dạng dự đoán đơn giản, không cần adversarial search.

### Ghost — nút thắt cổ chai
**14/15 nhóm còn lại đều có ít nhất một dạng lookahead hoặc heuristic địa hình** (dead-end awareness, flood-fill safe-area, Voronoi race, minimax) — không nhóm nào chỉ dùng "khoảng cách × trọng số" thuần túy như nhóm 0. Đây là nguyên nhân trực tiếp khiến Ghost nhóm 0 bị bắt trong ~11 bước ở 13/15 trận: gần như mọi Pacman trong lớp đều đủ mạnh để bắt một Ghost không biết dự đoán/né vùng nguy hiểm.

### Bẫy kỹ thuật phổ biến quan sát được ở các nhóm khác (cần tránh khi viết lại)
- **Không có time budget / iterative deepening**: nhóm 2, 5, 6, 7, 9, 11, 12, 14, 15 — rủi ro timeout nếu map lớn hơn hoặc máy chấm chậm hơn máy dev.
- **Không có `try/except` bọc search**: phần lớn các nhóm trên — vì mỗi trận chỉ chạy **1 lần duy nhất** (theo QA), một lỗi runtime là mất trắng cả trận.
- **Bỏ qua `pacman_speed` khi mô hình hóa đối thủ trong minimax** (nhóm 10, phần nào nhóm 12) — khiến Ghost đánh giá thấp tầm với thật của Pacman.
- **Cache không giới hạn** (nhóm 9, 13) — rủi ro memory nếu trận kéo dài.
- Một vài bug cụ thể: nhóm 4 (crash khi `threat is None`), nhóm 12 (crash khi `enemy_position is None` do IndexError trên list rỗng), nhóm 16 (Ghost crash khi mất tầm nhìn kẻ địch).

## 4. Thông tin quan trọng từ QA (`[FAI] QA Labs + Project.xlsx`, sheet `HideSeek`)

- Agent Pacman/Ghost cùng nhóm **không** bị đấu với nhau khi chấm điểm chính thức, nhưng **được phép self-play để test** (`arena.py --seek 0 --hide 0`).
- **Tie-break khi win-rate bằng nhau**: dựa vào `avg_pacman_step − avg_ghost_step` — Pacman cần bắt **nhanh**, Ghost cần sống **lâu** (càng gần 200 bước càng tốt).
- Vị trí khởi tạo **cố định**, mỗi cặp đấu **chỉ chạy đúng 1 lần** (không lặp lại nhiều trận lấy trung bình) → chiến lược ngẫu nhiên hóa không có lợi ích thực sự ở đây, ưu tiên deterministic nhưng mạnh và **an toàn** (không crash) hơn là né đoán bài.
- **Final submission lab1 vẫn là HideSeek bình thường**, không phải bản Blind/fog-of-war (đã được thầy đính chính) → không cần đầu tư xử lý fog cho bản final.
- Optimized submission được phép dùng checkpoint result (ranking + source code các nhóm khác) để tối ưu tiếp — chính là cơ sở của bảng phân tích ở mục 2.

## 5. Blueprint đề xuất cho Ghost bản final (theo thứ tự ưu tiên)

1. **Minimax + alpha-beta với iterative deepening + time budget cứng** (mẫu chuẩn: nhóm 13 — depth 1→6, budget ~0.6s, fallback về best move ở độ sâu hoàn chỉnh gần nhất nếu hết giờ). Đây là điểm nhiều nhóm khác thiếu — làm đúng chỗ này là đã hơn quá nửa lớp về độ an toàn.
2. **`try/except` bọc toàn bộ search, fallback về greedy đơn giản khi lỗi** (nhóm 13, 16) — vì mỗi trận chỉ chạy 1 lần, một lần crash là mất trắng.
3. **Eval dùng khoảng cách BFS thật (maze-aware) thay vì Manhattan**, cộng thêm bonus/penalty theo `open_degree`/dead-end (nhóm 6, 8, 13, 14).
4. **Mô hình hóa đúng luật tốc độ x2 của Pacman trong cây tìm kiếm** — sinh action multi-step (1 hoặc 2 ô) cho lượt Pacman thay vì chỉ 1 ô/lượt (nhóm 4, 8, 13), tránh lỗi của nhóm 10.
5. Phương án thay thế nếu muốn giảm rủi ro cài đặt minimax: **BFS-race/Voronoi "spare time" heuristic** (nhóm 16) — so sánh ai tới ô nào trước giữa Ghost và Pacman (có tính tốc độ Pacman), ưu tiên ô Pacman không thể chiếm trước. Đơn giản hơn minimax, ít bug hơn, vẫn vượt xa greedy thuần.

## 6. Việc cần làm tiếp theo
- [ ] Viết lại `GhostAgent` theo blueprint mục 5.
- [ ] Self-play test bằng `arena.py --seek 0 --hide 0 --delay 0.3` để xem trực quan điểm chết hiện tại.
- [ ] Benchmark Ghost mới với Pacman của các nhóm 8, 13 (baseline mạnh) trong `24C05/source_code/`.
- [ ] Pacman: cân nhắc thêm dự đoán vận tốc Ghost (kiểu nhóm 11) nếu còn thời gian — ưu tiên thấp hơn Ghost.

## 7. Xếp hạng chính thức thật sự — và vì sao nhóm 0 đang Rank 1 dù Ghost yếu nhất lớp

Đã tra `Checkpoint Result.xlsx` (kết quả chính thức, có cột `Rank`) để đối chiếu.

### Bảng xếp hạng (sheet `summary`, top các nhóm liên quan)

| Team | Win Pacman | Avg Pacman Steps | Win Ghost | Avg Ghost Steps | **Total Win** | Pacman−Ghost | **Rank** |
|---|---|---|---|---|---|---|---|
| **0** | 15 | 9.667 | 2 | 23.933 | **17** | −14.267 | **1** |
| 13 | 15 | 9.8 | 2 | 23.933 | **17** | −14.133 | **2** |
| 16 | 15 | 9.533 | 1 | 24.667 | 16 | −15.13 | 3 |
| 12 | 15 | 9.867 | 1 | 11.667 | 16 | −1.8 | 4 |
| 8 | 15 | 9.867 | 1 | 11.4 | 16 | −1.53 | 5 |

Công thức xếp hạng thực tế: sắp theo **Total Win = Win Pacman + Win Ghost** trước; nếu hoà mới xét tie-break `avg_pacman_steps − avg_ghost_steps` (càng thấp/âm càng tốt).

### Sự thật đằng sau con số

Tra toàn bộ 240 trận đấu, **cả giải chỉ có đúng 8 trận Ghost thắng**, và tất cả đều thuộc 2 dạng:

1. Ghost sống đủ 200 bước khi gặp **Pacman #11** — bản thân Pacman #11 bị lỗi/chậm bất thường (chỉ 11/15 thắng, avg 62.8 bước, so với chuẩn ~9-12 bước của cả lớp).
2. Ghost thắng "ăn không" vì đối thủ Pacman bị **AGENT_TIMEOUT** (Pacman #15 timeout 2 lần, Pacman #3 timeout 2 lần).

**Không có trận nào trong cả 240 trận mà một Ghost thật sự né được một Pacman đang hoạt động bình thường** — kể cả các Ghost dùng minimax/alpha-beta/iterative-deepening tinh vi nhất lớp (nhóm 13, nhóm 8) cũng không thắng thêm được trận nào ngoài đúng những "freebie" nói trên.

**Nhóm 0 và nhóm 13 là hai nhóm DUY NHẤT ăn trọn cả 2 loại freebie này**, nên cùng đạt Total Win = 17 (cao nhất giải). Giữa hai nhóm hoà nhau, nhóm 0 vượt lên Rank 1 chỉ nhờ Pacman nhanh hơn **0.133 bước trung bình** (9.667 vs 9.8) — một khoảng cách cực kỳ mong manh.

→ Kết luận: "Ghost yếu nhất lớp" đúng về **thiết kế thuật toán** (0-ply greedy so với minimax của các nhóm khác), nhưng trong pool đối thủ hiện tại điều đó **không ảnh hưởng kết quả** vì luật chơi (Pacman speed×2 + full visibility + fixed start) thiên vị Seeker quá mạnh — không Ghost nào trong lớp (kể cả loại xịn nhất) né được một Pacman tử tế.

### ⚠️ Rủi ro cho bản optimized submission

Rank 1 hiện tại **không đến từ việc Ghost giỏi**, mà từ việc khai thác đúng lỗi của 3 nhóm khác (#3, #11, #15). Ở vòng optimized, các nhóm đó nhiều khả năng sẽ tự sửa lỗi Pacman — khi đó các "freebie" này có thể biến mất, kéo Total Win của nhóm 0 từ 17 xuống lại 15 (rớt xuống ngang cụm rank 5-13 hiện tại). Viết lại Ghost theo blueprint ở mục 5 **không phải để "làm đẹp"** mà là bảo hiểm bắt buộc để giữ hạng, vì lợi thế Rank 1 hiện tại vốn rất mong manh và có thể mất bất cứ lúc nào khi đối thủ tự vá lỗi.

## 8. Văn phong code, dấu vết AI, và dự đoán bước đi bản final của từng nhóm

> Đọc lại toàn bộ code 16 nhóm lần 2, lần này soi theo góc độ: (A) phong cách viết code, (B) suy đoán tỉ lệ code do AI hỗ trợ (heuristic, KHÔNG phải bằng chứng xác thực, chỉ để tham khảo), (C) dự đoán ưu tiên sửa đổi ở bản optimized submission.

### Nhóm 0 (mình) — tự phân tích

- **Style:** Comment 100% tiếng Việt, đúng 1 dòng/hàm, đặt ngay trên `def`, cực kỳ đều tay trên cả 6 hàm. Tên biến/hàm tiếng Anh snake_case có nghĩa. Pha trộn functional (helper module-level) + class-based (2 Agent class). Không type hints, không docstring `"""..."""`, **không có `try/except`**. File 149 dòng sạch tuyệt đối — không TODO sót, không code chết, không debug print.
- **AI% ước tính ~40-55%:** Nghiêng AI vì comment 1-dòng/hàm cực nhất quán và code sạch không tì vết. Nghiêng người tự viết vì thuật toán bám sát gần như nguyên văn phần gợi ý thuật toán của `STUDENT_GUIDE.md`, và **thiếu hoàn toàn lớp phòng thủ** (`try/except`, time budget) dù đề bài cảnh báo rõ — nếu AI tự do triển khai thường sẽ tự thêm các phần an toàn này.

### Bảng tổng hợp 15 nhóm còn lại

| Nhóm | Style nổi bật | AI% ước tính | Dự đoán bước đi bản final |
|---|---|---|---|
| 2 | Anh, docstring "giáo trình", có đoạn trailing-whitespace kiểu paste từ chat AI | 55-65% | Thêm time budget + try/except, giữ nguyên tier |
| 3 | Anh, section-header gọn, còn sót TODO của template | 35-45% | Nâng Ghost lên có lookahead thật, dọn TODO |
| 4 | Mix Anh/Việt, tên tếu ("HomeLander"), debug log thật + TODO gây crash | 15-30% (thấp) | Ưu tiên 1: fix bug `threat is None` gây crash |
| 5 | Anh, comment giải thích rationale rất mực thước, docstring Google-style | 60-65% | Thêm try/except, dọn dead code, time budget |
| 6 | Mix style 2 class, comment đời thường ("i don't know if..."), debug print sót | 15-25% | Thêm bộ nhớ last-seen cho Ghost, time budget |
| 7 | Việt, giọng ghi chú cá nhân, tên hàm không nhất quán PEP8, không docstring nào | 10-20% (thấp nhất) | Thêm try/except + time budget cho minimax d6 |
| 8 | Mix Anh/Việt, bug dấu phẩy thừa, import chết | ~45% | Ghost đã tốt → dồn lực nâng cấp Pacman (đang yếu nhất đội) |
| 9 | Anh hoàn toàn, giáo trình đều tay, duplicate code 2 class nhưng style nhất quán | 55-60% | Thêm time budget, giới hạn cache, gộp code trùng |
| 10 | Tối thiểu, tên riêng cá nhân ("nhom 10/Phong/Vinh"), nhiều code chết | 15-25% | Vá lỗ hổng lớn nhất: đưa `pacman_speed` vào eval Ghost |
| 11 | Anh, comment Việt bị lỗi encoding (mojibake), tên "Hybrid Phantom v2" | 35-45% | Thêm try/except+time budget, tăng depth |
| 12 | Giữ nguyên docstring template gốc, 2 class style khác hẳn nhau | 20-30% | Ưu tiên 1: vá crash `enemy_position=None`, thêm time budget |
| 13 | Cực nhất quán, kiến trúc 3-file rõ ràng, comment Việt giải thích kỹ thuật sâu | 55-70% (cao nhất) | Tinh chỉnh trọng số eval, tăng depth, nới time budget — đối thủ trực tiếp rank 1 |
| 14 | Anh, tên có nghĩa, import bị lặp 2 lần ở đầu file | 35-45% | Thêm safety net trước khi tối ưu thuật toán |
| 15 | Anh, bám sát pseudocode AIMA, kể chuyện debug cụ thể | 25-30% | Ưu tiên 1 gần chắc chắn: thêm time budget+try/except (từng timeout thật 2 trận) |
| 16 | Phân hoá rõ: Pacman hệ thống/đủ docstring, Ghost còn TODO+joke cá nhân | Pacman 55-60%, Ghost 15-20% | Sửa Ghost: xử lý `None`, dọn code chết |

*Tất cả % chỉ là suy đoán heuristic dựa trên dấu hiệu văn phong, không phải bằng chứng xác thực.

### Xu hướng chung & rủi ro 2 mặt trận cho nhóm 0

Gần như toàn bộ 15 nhóm còn lại được dự đoán ưu tiên số 1 là thêm `try/except` + time budget ở bản final. Điều này tạo ra **hai rủi ro trực tiếp cho Rank 1 hiện tại**:

1. **Rủi ro xói mòn:** 2 trận thắng miễn phí (nhờ Pacman #11 chậm, Pacman #3 timeout) rất có thể bị đối thủ vá ở bản final → Total Win tụt từ 17 xuống 15.
2. **Rủi ro cạnh tranh trực tiếp:** Nhóm 13 (hoà điểm, chỉ thua 0.13 bước) được dự đoán sẽ tinh chỉnh chính xác khoảng cách đó — nếu nhóm 0 đứng yên, rất dễ bị soán ngôi dù không có gì thay đổi ở phía mình.

**Hệ quả:** viết lại Ghost thật sự mạnh không còn là "nice to have" mà là bảo hiểm sống còn, vì chưa từng có nhóm nào trong lớp thắng Ghost thật trước một Pacman khoẻ mạnh — nếu làm được, đây sẽ là lợi thế mà không đối thủ nào có.
