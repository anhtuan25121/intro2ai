# Overview — Hide and Seek Arena, chuẩn bị bản Final (Nhóm 0)

> Tài liệu tổng hợp bức tranh toàn cảnh trước khi lên kế hoạch chi tiết (`plan.md`). Nguồn: đề bài PDF, `STUDENT_GUIDE.md`, QA chính thức, `results.csv`/`Checkpoint Result.xlsx` (240 trận), và review code 16 nhóm trong `24C05/`. Chi tiết đầy đủ nằm ở `24C05/class_overview_review.md`.

## 1. Đề bài tóm tắt

- Mỗi nhóm viết 2 agent: **Pacman/Seek** (bắt Ghost càng nhanh càng tốt) và **Ghost/Hide** (sống đủ 200 bước).
- Cả hai di chuyển **đồng thời**, không thấy nước đi của nhau trước.
- Pacman có tốc độ **x2** theo đường thẳng (bù lại vì cùng tốc độ thì Pacman không bao giờ bắt được). Bắt được khi Manhattan distance < 2.
- Vị trí khởi tạo **cố định**, mỗi cặp đấu chỉ chạy **đúng 1 lần** (không lấy trung bình nhiều trận).
- Xếp hạng: sắp theo **Total Win** (Win Pacman + Win Ghost) trước; hoà thì tie-break bằng `avg_pacman_steps − avg_ghost_steps` (càng thấp/âm càng tốt — Pacman cần nhanh, Ghost cần sống lâu).
- Bản final này **vẫn là HideSeek bình thường**, không phải bản Blind/fog-of-war.
- Ràng buộc: ≤1s/bước, ≤128MB (Colab CPU-only). Được dùng AI tools, nhưng "students should use them wisely" và giảng viên **có quyền phỏng vấn miệng** để kiểm tra hiểu bài.
- Agent của chính mình (Pacman/Ghost cùng nhóm) không bị đấu với nhau khi chấm, nhưng được phép self-play để test.

## 2. Vị trí hiện tại: Rank 1, nhưng mong manh

| Chỉ số | Giá trị |
|---|---|
| Win as Pacman | 15/15, avg 9.667 bước |
| Win as Ghost | 2/15 (thực chất chỉ 1 trận là "thắng thật") |
| Total Win | 17 (cao nhất giải, hoà với nhóm 13) |
| Rank | **1** (hơn nhóm 13 đúng 0.133 bước ở tie-break) |

**Sự thật quan trọng:** cả giải (240 trận) chỉ có **8 trận Ghost thắng**, và toàn bộ đều đến từ (a) Pacman #11 bị lỗi/chậm (avg 62.8 bước) hoặc (b) đối thủ bị **AGENT_TIMEOUT**. Không có trận nào một Ghost thật sự né được một Pacman đang hoạt động tốt — kể cả các Ghost dùng minimax tinh vi nhất lớp. Rank 1 hiện tại đến từ việc **khai thác đúng lỗi của 3 nhóm khác (#3, #11, #15)**, không phải từ Ghost giỏi.

## 3. Bức tranh toàn lớp (16 nhóm)

| Khía cạnh | Nhận định |
|---|---|
| Pacman | Đa số search-based (BFS/A*) hoặc hybrid (+minimax khi gần). Nhóm 0 ở tier trung bình nhưng kết quả thực tế gần như tối ưu. |
| Ghost | **14/15 nhóm khác đều có lookahead hoặc heuristic địa hình** (dead-end, flood-fill, Voronoi, minimax) — chỉ nhóm 0 dùng greedy 0-ply thuần. Nhóm 0 là thiết kế Ghost yếu nhất lớp về mặt kỹ thuật. |
| Robustness | Phần lớn các nhóm (kể cả có minimax) **thiếu `try/except` và time budget** — rủi ro crash/timeout rất phổ biến trong lớp, kể cả nhóm 15 đã từng timeout thật 2 trận. |
| Nhóm mạnh nhất kỹ thuật | **Nhóm 13**: minimax iterative-deepening + time budget cứng (0.6s) + eval maze-aware + try/except fallback. Đây cũng là đối thủ cạnh tranh Rank 1 trực tiếp. **Nhóm 8**: Ghost tốt nhất lớp (ID minimax d1-19, flood-fill safe-area). **Nhóm 16**: Pacman robust nhất (time budget + try/except toàn cục). |

## 4. Rủi ro chính cho bản final

1. **Rủi ro xói mòn:** Pacman #11 (chậm) và Pacman #3 (timeout) — nguồn gốc 2 trận thắng Ghost hiện tại — nhiều khả năng được đối thủ tự vá ở bản optimized (dự đoán: gần như mọi nhóm ưu tiên thêm safety net). Nếu vậy, Total Win nhóm 0 tụt 17 → 15, rớt khỏi top.
2. **Rủi ro cạnh tranh trực tiếp:** Nhóm 13 hoà điểm sát nút (0.13 bước), có nền tảng kỹ thuật tốt nhất lớp để tinh chỉnh chính xác khoảng cách đó — nếu nhóm 0 đứng yên, rất dễ bị soán ngôi.
3. **Rủi ro nội tại:** Ghost hiện tại chưa từng thắng thật trước một Pacman khoẻ mạnh — nếu bản final gặp đúng dạng Pacman "chuẩn" (đa số các nhóm), tỉ lệ thắng Ghost gần như bằng 0.

## 5. Định hướng tổng thể

Rank 1 hiện tại là **may mắn có điều kiện**, không phải năng lực thật. Mục tiêu bản final: biến lợi thế may mắn này thành lợi thế thật — Ghost phải đủ mạnh để **tự tạo ra chiến thắng**, không phụ thuộc lỗi đối thủ; đồng thời giữ Pacman đủ nhanh để không bị nhóm 13 vượt ở tie-break. Kế hoạch chi tiết: xem `plan.md` trong cùng thư mục.

## 6. Trạng thái hiện tại (đã code + tự test)

- `final/agent.py` đã viết xong: Pacman A* (giữ nguyên logic initial, đã thử thêm dự đoán hướng đi nhưng test cho thấy không có lợi ích thật nên bỏ — xem `plan.md` mục 10), Ghost minimax + alpha-beta + iterative deepening + time budget + fallback an toàn.
- Hạ tầng tự test: `.venv` tại `labs/lab1/.venv`, script `final/scripts/sync_bench.py` + `final/scripts/run_tournament.py` mô phỏng đúng cách chấm của thầy (dùng thẳng `Arena`/`AgentLoader`/`Environment` gốc, đúng cấu hình đề bài). Kết quả mới nhất lưu tại `final/test_results/`.
- Kết quả tự test (nhóm 0 bản final vs bản **initial** của 15 nhóm khác, 30 trận): Win Pacman 15/15 (avg 9.733 bước), Win Ghost 1/15 (avg 24.067 bước) — chi tiết và bài học rút ra ở `plan.md` mục 9-10.
- Việc còn lại: đóng gói `0.zip` trước khi nộp thật.
