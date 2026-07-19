# INTRO2AI — Nhập môn Trí tuệ Nhân tạo

Kho học tập cá nhân môn **Introduction to AI**: ghi chú bài giảng đã hệ thống hoá, tài liệu ôn thi giữa kì, và bài lab Hide & Seek Arena.

**📖 Trang ôn tập (GitHub Pages):** https://liltommy142.github.io/intro2ai/

## Cấu trúc repo

```
docs/            Ghi chú bài giảng + tài liệu ôn thi (nguồn của GitHub Pages)
slides/          Slide PDF gốc của môn học (Lecture 1–5)
Obsidian Vault/  Bản vault Obsidian của cùng bộ ghi chú (học offline, có graph view)
labs/lab1/       Lab 1 — Hide and Seek Arena (pursuit-evasion trên maze)
project/         Đồ án môn học
```

## Nội dung ôn tập (`docs/`)

| Chủ đề | Nội dung |
|---|---|
| Lecture 1 | AI là gì, lịch sử, ứng dụng |
| Lecture 2 | Intelligent Agents — rationality, PEAS, các loại agent |
| Lecture 3.1–3.3 | Search: state space, BFS/UCS/DFS/IDS, Greedy/A*, heuristics |
| Lecture 4 | Local search — Hill-climbing, Simulated annealing, GA |
| Lecture 5 ⭐ | **Adversarial search — Minimax, Alpha-beta, Expectiminimax** (trọng tâm thi giữa kì) |
| Ôn thi | Cheat sheet, đề thi tham khảo có lời giải, hướng dẫn trình bày bài |

## Lab 1 — Hide and Seek Arena (`labs/lab1/`)

Mỗi nhóm viết 2 agent đấu đồng thời trên maze: **Pacman** (đuổi bắt, tốc độ ×2 theo đường thẳng) và **Ghost** (sống sót đủ 200 bước). Ràng buộc ≤1s/bước, ≤128MB.

- `final/agent.py` — bản nộp final: Pacman dùng A*, Ghost dùng minimax + alpha-beta + iterative deepening + time budget, 2 lớp fallback an toàn. Đây là bài áp dụng thực tế trực tiếp của Lecture 3.3 (A*) và Lecture 5 (minimax/alpha-beta).
- `final/overview.md`, `final/plan.md` — phân tích giải đấu, chiến lược, và toàn bộ nhật ký benchmark/bài học (kiểm soát seed khi A/B test, vì sao iterative deepening là bắt buộc...).
- `final/tests/`, `final/scripts/` — 42 unit test + script tự tổ chức giải đấu bằng đúng harness chấm điểm.
- `HideSeek/` — framework arena gốc; `24C05/` — code 16 nhóm trong lớp + kết quả 240 trận vòng initial (tư liệu phân tích đối thủ).

Chạy lại benchmark:

```bash
source labs/lab1/.venv/bin/activate   # numpy + openpyxl
python labs/lab1/final/scripts/sync_bench.py
python labs/lab1/final/scripts/run_tournament.py
```

## GitHub Pages

Site build bằng Jekyll từ thư mục `docs/` trên nhánh `main` (layout + CSS tự viết, không dùng theme ngoài, hỗ trợ dark mode).
