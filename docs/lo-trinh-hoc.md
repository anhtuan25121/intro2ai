---
layout: default
title: Lộ trình học & Liên kết kiến thức
---

# 🗺️ Lộ trình học & Liên kết kiến thức

> Trang này dành cho người **mới bắt đầu đọc site**: đọc theo thứ tự dưới đây, hiểu được **mạch liên kết giữa các lecture**, thì sẽ nắm trọn kiến thức môn học và làm được bài giữa kì (chỉ Lecture 5) lẫn hiểu sâu hơn về bản chất thuật toán.

## 1. Câu chuyện xuyên suốt môn học

Toàn bộ môn học trả lời 1 câu hỏi lớn: **"Làm sao thiết kế một agent hành xử hợp lý (rational)?"** Mỗi lecture giải quyết một mảnh của câu hỏi đó:

```text
Lecture 2: Agent
   agent phải HÀNH ĐỘNG hợp lý trong 1 môi trường (PEAS, task environment)
        │
        ▼
Lecture 3.1: Problem Solving
   để chọn hành động, agent cần TÌM (search) 1 chuỗi action dẫn tới goal
   → định nghĩa problem bằng 5 thành phần, biểu diễn bằng SEARCH TREE
        │
        ▼
   ┌─────────────────────┬──────────────────────┐
   ▼                                             ▼
Lecture 3.2: Uninformed              Lecture 3.3: Informed
   tìm mà KHÔNG biết gì thêm            tìm CÓ heuristic h(n) dẫn đường
   (BFS, UCS, DFS, IDS...)              (Greedy, A*...)
        │                                             │
        └──────────────────┬──────────────────────────┘
                            ▼
                Lecture 4: Local Search
        khi CHỈ CẦN trạng thái đích (không cần đường đi) → Hill-climbing, GA...
                            │
                            ▼
                Lecture 5: Adversarial Search  ⭐ THI GIỮA KÌ
        khi có THÊM 1 agent khác (đối thủ) cùng hành động trong môi trường
        → search tree giờ có 2 loại node (MAX/MIN) thay vì 1 loại
        → Minimax, Alpha-Beta, Expectiminimax
```

**Điểm mấu chốt**: Lecture 5 (Adversarial Search) **không phải kiến thức tách rời** — nó là **phần mở rộng trực tiếp** của Lecture 3.1-3.3 khi thêm một giả định mới: *"có một agent khác đang cố phá hoại mục tiêu của bạn."* Nếu bạn hiểu rõ khái niệm search tree/node/DFS ở Lecture 3, bạn sẽ thấy Minimax và Alpha-Beta chỉ là DFS có "gắn thêm luật chơi 2 phe".

## 2. Bảng đối chiếu khái niệm — "phiên bản Lecture 3 vs phiên bản Lecture 5"

Đây là bảng **quan trọng nhất** của trang này — giúp bạn thấy Lecture 5 dùng lại ý tưởng gì từ các lecture trước, chỉ đổi tên/đổi ngữ cảnh:

| Khái niệm ở Lecture 3.x | Khái niệm tương ứng ở Lecture 5 | Điểm khác biệt |
|---|---|---|
| **Problem**: Initial state, Actions(s), Result(s,a), Goal test, Path cost ([Lecture 3.1](lecture-3-1-problem-solving-by-searching.md)) | **Game**: S0, PLAYER(s), ACTIONS(s), RESULT(s,a), TERMINAL-TEST(s), UTILITY(s,p) | Game có thêm PLAYER(s) vì có **nhiều agent luân phiên**; UTILITY thay Goal test vì có thể có nhiều mức "thắng/thua/hoà" chứ không chỉ đạt/không đạt goal |
| **Search tree**, **node**, **frontier** ([Lecture 3.1](lecture-3-1-problem-solving-by-searching.md)) | **Game tree** — mỗi tầng đổi chủ (MAX rồi MIN rồi MAX...) | Cây minimax về bản chất vẫn là search tree, chỉ khác: node ở tầng chẵn/lẻ có "quyền ưu tiên" khác nhau (max vs min) |
| **DFS** — traversal trái sang phải, xuống tận lá rồi quay lui ([Lecture 3.2](lecture-3-2-uninformed-search.md)) | **Minimax / Alpha-Beta traversal** | Alpha-Beta **chính là DFS** + thêm 2 biến α, β để cắt tỉa nhánh không cần duyệt |
| **Heuristic function h(n)**: ước lượng cost còn lại đến goal ([Lecture 3.3](lecture-3-3-informed-search.md)) | **Evaluation function EVAL(s)**: ước lượng "độ tốt" của 1 trạng thái chưa kết thúc | h(n) ước lượng **chi phí** (càng nhỏ càng tốt); EVAL(s) ước lượng **lợi thế** (càng lớn càng tốt cho MAX) — hướng ngược nhau về ý nghĩa nhưng cùng mục đích: "đỡ phải duyệt tới tận cùng" |
| **Admissible/Consistent heuristic** đảm bảo A* tối ưu ([Lecture 3.3](lecture-3-3-informed-search.md)) | Không có yêu cầu tương tự cho EVAL(s) — chỉ cần giữ đúng thứ tự win>draw>loss | H-Minimax **không đảm bảo tối ưu tuyệt đối** như A*, chỉ là xấp xỉ tốt nhất có thể trong thời gian cho phép |
| **Uniform-cost/A\*** dùng priority queue chọn node "tốt nhất" tiếp theo ([Lecture 3.2](lecture-3-2-uninformed-search.md), [Lecture 3.3](lecture-3-3-informed-search.md)) | Minimax **không** dùng priority queue — nó duyệt **toàn bộ** cây (hoặc tới cutoff) rồi lan giá trị ngược lên | Vì đối thủ MIN cũng "thông minh", ta không thể chỉ nhìn nhánh có vẻ tốt nhất — phải xét mọi khả năng đối thủ phản công |
| **Local search** (Hill-climbing...) chỉ quan tâm **trạng thái cuối**, không quan tâm đường đi ([Lecture 4](lecture-4-local-search-algorithms.md)) | Minimax quan tâm **toàn bộ chuỗi nước đi cho tới hết game** | Adversarial search **không thể** dùng local search vì phải dự đoán phản ứng của đối thủ ở từng bước, không chỉ tối ưu 1 bước |

## 3. Vì sao hiểu bảng trên giúp bạn thi tốt hơn?

- Khi đề bài yêu cầu "vẽ cây và tính giá trị Minimax", bạn đang làm đúng thao tác DFS đã học ở Lecture 3.2 — chỉ khác là mỗi tầng đổi vai trò max/min.
- Khi đề bài hỏi "vì sao Alpha-Beta không đổi kết quả", câu trả lời gốc rễ giống hệt lý do GRAPH-SEARCH không đổi kết quả so với TREE-SEARCH ở Lecture 3.1: **ta chỉ bỏ qua các nhánh chắc chắn không tối ưu**, không bỏ qua nhánh có khả năng tối ưu.
- Khi đề bài hỏi về EVAL(s) và cutoff test, hãy liên hệ ngay tới khái niệm heuristic h(n) và "vì sao không thể duyệt hết cây" ở Lecture 3.3 — lý do giống hệt: **cây quá lớn (b^m), phải cắt bớt bằng ước lượng**.

## 4. Lộ trình đọc đề xuất

### Nếu bạn còn nhiều thời gian trước khi thi (>1 ngày)

1. Đọc [Lecture 1](lecture-1-introduction-to-ai.md) và [Lecture 2](lecture-2-intelligent-agents.md) để có bối cảnh (agent, rationality, PEAS) — 20-30 phút
2. Đọc [Lecture 3.1](lecture-3-1-problem-solving-by-searching.md) kỹ — đây là **nền tảng khái niệm** (state, search tree, node) mà Lecture 5 dùng lại — 20 phút
3. Đọc lướt [Lecture 3.2](lecture-3-2-uninformed-search.md) (đặc biệt DFS) và [Lecture 3.3](lecture-3-3-informed-search.md) (đặc biệt khái niệm heuristic) — 20 phút
4. Đọc lướt [Lecture 4](lecture-4-local-search-algorithms.md) để hiểu vì sao adversarial search **không thể** dùng cách tiếp cận local search — 10 phút
5. Đọc kỹ toàn bộ [Lecture 5](lecture-5-adversarial-search.md) — đây là nội dung thi — 45-60 phút
6. Làm [Đề thi tham khảo](de-thi-tham-khao.md) để tự kiểm tra
7. Đọc [Hướng dẫn làm bài & Trình bày](huong-dan-lam-bai.md) để biết cách trình bày ăn trọn điểm

### Nếu bạn chỉ còn vài giờ (như "thi vào ngày mai")

1. Đọc kỹ [Lecture 5](lecture-5-adversarial-search.md) (nội dung thi, tự đủ, không cần đọc lại Lecture 1-4)
2. Học thuộc [Cheat Sheet](cheat-sheet-adversarial-search.md)
3. Làm nhanh phần bài tập minimax + alpha-beta ở [Đề thi tham khảo](de-thi-tham-khao.md) để luyện tay vẽ cây
4. Đọc [Hướng dẫn làm bài & Trình bày](huong-dan-lam-bai.md) mục "Dạng 1" và "Dạng 2" (2 dạng bài chiếm điểm nhiều nhất: vẽ cây minimax + áp dụng alpha-beta)

## 5. Xem thêm

- [Trang chủ](index.md) — mục lục toàn bộ site
- [Lecture 5 - Adversarial Search](lecture-5-adversarial-search.md) — nội dung thi chính
- [Cheat Sheet](cheat-sheet-adversarial-search.md) — tóm tắt 1 trang
- [Đề thi tham khảo](de-thi-tham-khao.md) — bài tập luyện tập có lời giải
- [Hướng dẫn làm bài & Trình bày](huong-dan-lam-bai.md) — kỹ thuật trình bày bài thi
