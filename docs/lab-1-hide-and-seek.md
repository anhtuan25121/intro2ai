---
layout: default
title: Lab 1 — Hide and Seek Arena (áp dụng thực tế)
---

# Lab 1 — Hide and Seek Arena

> **Vì sao trang này nằm trong bộ ôn tập?** Lab 1 là nơi lý thuyết của [Lecture 3.3 (A*)](lecture-3-3-informed-search.md) và [Lecture 5 (Minimax/Alpha-beta)](lecture-5-adversarial-search.md) được đem ra chạy thật, đấu thật với 15 nhóm khác. Những bài học dưới đây là thứ slide không dạy — và cũng là câu trả lời sẵn nếu bị phỏng vấn miệng về bài nộp.

## 1. Bài toán

Trò chơi pursuit-evasion trên maze 21×21, hai agent di chuyển **đồng thời** (không thấy nước đi của nhau trước):

| | Pacman (Seeker) | Ghost (Hider) |
|---|---|---|
| Mục tiêu | Bắt Ghost càng nhanh càng tốt | Sống sót đủ 200 bước |
| Lợi thế | Tốc độ ×2 theo đường thẳng | Biết trước Pacman sẽ đuổi mình |
| Điều kiện bắt | Manhattan distance < 2 | — |

Ràng buộc kỹ thuật: **≤1s/bước, ≤128MB**, mỗi cặp đấu chỉ chạy đúng 1 trận (không lấy trung bình) — nghĩa là 1 lần crash/timeout là mất trắng trận đó.

## 2. Ánh xạ lý thuyết → cài đặt

| Thuật toán trong bài giảng | Dùng ở đâu trong `final/agent.py` | Ghi chú thực tế |
|---|---|---|
| A* ([L3.3](lecture-3-3-informed-search.md)) | Pacman tìm đường ngắn nhất tới Ghost | Heuristic = Manhattan (admissible trên grid 4 hướng) |
| BFS ([L3.2](lecture-3-2-uninformed-search.md)) | Bản đồ khoảng cách thật (có tính tường) từ vị trí Pacman | Nền cho eval của Ghost và greedy fallback |
| Minimax + Alpha-beta ([L5](lecture-5-adversarial-search.md)) | Ghost lookahead: Ghost = MAX, Pacman = MIN | Phải mô hình hoá đúng tốc độ ×2 của Pacman trong nhánh MIN |
| Iterative deepening ([L3.2](lecture-3-2-uninformed-search.md)) | Tăng depth dần 1→10, có deadline 0.65s | Lý do ở mục 4 — đây không phải "trang trí" |
| Evaluation function ([L5](lecture-5-adversarial-search.md)) | `dist×10 + degree×3`, phạt ngõ cụt | Giống eval cắt tỉa ở depth giới hạn trong slide |

## 3. Những bug thật đã gặp (và bài học)

**Bug 1 — Eval dùng bản đồ khoảng cách "chết".** Bản nháp đầu tính BFS distance map từ vị trí Pacman *lúc đầu lượt* rồi dùng cho **mọi node** trong cây minimax. Nhưng vị trí Pacman mô phỏng trong cây đã trôi xa vị trí thật — eval báo "an toàn" trong khi Pacman mô phỏng đã áp sát. Hậu quả: Ghost minimax mới bị bắt **nhanh hơn cả Ghost greedy cũ** (9 bước vs 200 bước trước cùng đối thủ). Fix: dùng khoảng cách tính tại đúng node đang xét.
→ *Bài học: eval function phải đánh giá đúng trạng thái của node, không phải trạng thái gốc.*

**Bug 2 — A/B test bị nhiễu bởi random của… đối thủ.** So sánh 2 phiên bản Pacman thấy lệch 1 bước, suýt kết luận sai "tính năng mới phản tác dụng". Thực ra 2 nhóm đối thủ dùng `random.choice()` không seed — kết quả không tái lập được. Sau khi cố định `random.seed(42)` trước mỗi trận: 2 phiên bản **giống hệt nhau trên cả 30 trận**.
→ *Bài học: khi benchmark phải kiểm soát mọi nguồn ngẫu nhiên, kể cả trong code đối thủ.*

**Bug 3 — `try/except` không bọc trọn `step()`.** Dòng `tuple(my_position)` nằm ngoài khối `try`; nếu input dị dạng thì fallback trong `except` cũng crash theo (dùng biến chưa tồn tại — double fault). Fix: bọc toàn bộ thân hàm, 2 lớp fallback (minimax lỗi → greedy → `Move.STAY`).

## 4. Vì sao iterative deepening + time budget là bắt buộc?

Đã thử đơn giản hoá thành minimax depth cố định để "dễ giải thích hơn" — và đo được cái giá thật:

| Depth cố định | Kết quả | Thời gian/bước tệ nhất |
|---|---|---|
| 3–7 | Mất trận thắng 200 bước trước Pacman yếu (Total Win 17→15) | ≤0.115s |
| 8 | Vẫn mất | 0.768s — sát ngưỡng 1s |
| 15 | — | **Treo >2 phút, phải kill** |

Không tồn tại một depth cố định vừa đủ sâu để hữu ích vừa đủ nông để an toàn cho mọi tình huống. Iterative deepening + deadline là cách **duy nhất** tự tìm depth tối đa an toàn theo từng tình huống — đúng tinh thần "anytime algorithm" của [Lecture 5](lecture-5-adversarial-search.md).

## 5. Phát hiện lớn nhất: giới hạn toán học của bài toán

Qua 240 trận vòng initial của cả lớp + benchmark riêng: **không một Ghost nào** (kể cả minimax tinh vi nhất lớp) né được một Pacman hoạt động tốt quá ~11-13 bước. Với vị trí xuất phát cố định, khoảng cách ban đầu ngắn, Pacman tốc độ ×2 và full visibility — bị bắt sớm gần như là **định mệnh toán học** của cấu hình pursuit-evasion này, bất kể thuật toán.

Hệ quả chiến lược: mọi trận Ghost "thắng" trong giải đều đến từ lỗi đối thủ (Pacman chậm/crash/timeout). Giá trị thật của bản final vì thế không nằm ở thắng thêm, mà ở **không tự thua**: try/except đầy đủ, time budget có biên an toàn, đã stress-test input dị dạng, memory 0.07MB/128MB.

## 6. Checklist tư duy rút ra (dùng lại cho mọi bài AI thi đấu)

1. Đọc kỹ **luật chấm điểm** trước khi tối ưu thuật toán — tie-break quyết định thứ hạng nhiều hơn thuật toán "xịn".
2. Mô hình hoá **đúng luật chuyển động** của đối thủ trong cây tìm kiếm (tốc độ ×2 hay bị bỏ quên).
3. Search có độ sâu → bắt buộc iterative deepening + deadline; không đoán mò depth.
4. Fallback nhiều lớp, không bao giờ để `step()` ném exception.
5. Benchmark phải tái lập được (seed mọi nguồn random) và **đủ toàn bộ đối thủ** (tập con 10/15 đã từng che mất matchup thua nặng nhất).
6. Hiểu từng dòng code mình nộp — chuẩn bị trả lời "khác biệt giữa greedy và minimax của bạn là gì, tại sao?"

---

*Chi tiết đầy đủ (số liệu benchmark, nhật ký từng vòng test/sửa): xem `labs/lab1/final/overview.md` và `labs/lab1/final/plan.md` trong repo.*
