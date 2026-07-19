---
layout: default
title: INTRO2AI — Ghi chú ôn tập
---

<div class="hero">
  <h1 class="hero-title"><span class="hero-emoji">🧠</span> <span class="hero-grad">INTRO2AI</span></h1>
  <p class="hero-sub">Hệ thống hoá kiến thức môn <strong>Nhập môn Trí tuệ Nhân tạo</strong> — từ agent, search đến adversarial search, kèm bài lab thực chiến.</p>
  <div class="hero-actions">
    <a class="btn btn-primary" href="{{ '/lecture-5-adversarial-search.html' | relative_url }}">⭐ Ôn thi giữa kì</a>
    <a class="btn" href="{{ '/lo-trinh-hoc.html' | relative_url }}">🗺️ Lộ trình học</a>
  </div>
</div>

> **Thi giữa kì — closed-book**, nội dung **chỉ** nằm trong **Lecture 5 · Adversarial Search**. Học Lecture 5 → ôn nhanh bằng Cheat Sheet → làm Đề thi tham khảo → đọc Hướng dẫn trình bày.

## ⭐ Trọng tâm thi giữa kì

<div class="card-grid">
  <a class="card card-star" href="{{ '/lecture-5-adversarial-search.html' | relative_url }}">
    <span class="card-icon">♟️</span>
    <span class="card-title">Lecture 5 — Adversarial Search</span>
    <span class="card-desc">Minimax, Alpha-beta pruning, Expectiminimax — lý thuyết đầy đủ, nội dung duy nhất của đề thi.</span>
  </a>
  <a class="card card-star" href="{{ '/cheat-sheet-adversarial-search.html' | relative_url }}">
    <span class="card-icon">⚡</span>
    <span class="card-title">Cheat Sheet</span>
    <span class="card-desc">Tóm tắt siêu nhanh toàn bộ Lecture 5 — lướt lại trong 10 phút trước giờ thi.</span>
  </a>
  <a class="card card-star" href="{{ '/de-thi-tham-khao.html' | relative_url }}">
    <span class="card-icon">📝</span>
    <span class="card-title">Đề thi tham khảo</span>
    <span class="card-desc">Bài tập luyện tập đủ dạng, có lời giải chi tiết từng bước.</span>
  </a>
  <a class="card card-star" href="{{ '/huong-dan-lam-bai.html' | relative_url }}">
    <span class="card-icon">🎯</span>
    <span class="card-title">Hướng dẫn làm bài</span>
    <span class="card-desc">Cách trình bày từng dạng câu hỏi để ăn trọn điểm — vẽ cây, đánh dấu cắt tỉa, giải thích.</span>
  </a>
</div>

## 📚 Kiến thức nền tảng

<div class="card-grid">
  <a class="card" href="{{ '/lecture-1-introduction-to-ai.html' | relative_url }}">
    <span class="card-icon">🌱</span>
    <span class="card-title">L1 — Introduction to AI</span>
    <span class="card-desc">AI là gì, lịch sử, các hướng tiếp cận và ứng dụng.</span>
  </a>
  <a class="card" href="{{ '/lecture-2-intelligent-agents.html' | relative_url }}">
    <span class="card-icon">🤖</span>
    <span class="card-title">L2 — Intelligent Agents</span>
    <span class="card-desc">Agent, rationality, PEAS, phân loại môi trường và agent.</span>
  </a>
  <a class="card" href="{{ '/lecture-3-1-problem-solving-by-searching.html' | relative_url }}">
    <span class="card-icon">🧩</span>
    <span class="card-title">L3.1 — Problem Solving by Searching</span>
    <span class="card-desc">State space, 5 thành phần của bài toán tìm kiếm.</span>
  </a>
  <a class="card" href="{{ '/lecture-3-2-uninformed-search.html' | relative_url }}">
    <span class="card-icon">🔦</span>
    <span class="card-title">L3.2 — Uninformed Search</span>
    <span class="card-desc">BFS, UCS, DFS, DLS, IDS, Bidirectional — so sánh đầy đủ.</span>
  </a>
  <a class="card" href="{{ '/lecture-3-3-informed-search.html' | relative_url }}">
    <span class="card-icon">🧭</span>
    <span class="card-title">L3.3 — Informed Search</span>
    <span class="card-desc">Greedy Best-First, A*, thiết kế heuristic admissible/consistent.</span>
  </a>
  <a class="card" href="{{ '/lecture-4-local-search-algorithms.html' | relative_url }}">
    <span class="card-icon">🏔️</span>
    <span class="card-title">L4 — Local Search</span>
    <span class="card-desc">Hill-climbing, Simulated annealing, Beam search, Genetic Algorithm.</span>
  </a>
</div>

## 🕹️ Lý thuyết vào thực chiến

<div class="card-grid">
  <a class="card" href="{{ '/lab-1-hide-and-seek.html' | relative_url }}">
    <span class="card-icon">👻</span>
    <span class="card-title">Lab 1 — Hide and Seek Arena</span>
    <span class="card-desc">A* + Minimax chạy thật, đấu thật với 15 nhóm: bug thật đã gặp, bài học benchmark, và giới hạn toán học của pursuit-evasion.</span>
  </a>
  <a class="card" href="{{ '/lo-trinh-hoc.html' | relative_url }}">
    <span class="card-icon">🗺️</span>
    <span class="card-title">Lộ trình học &amp; Liên kết kiến thức</span>
    <span class="card-desc">Đọc theo thứ tự nào, lecture nào nối với lecture nào — bức tranh toàn cảnh môn học.</span>
  </a>
</div>

## Mạch kiến thức

<div class="flow">
  <div class="flow-step"><strong>L1</strong> AI là gì</div>
  <div class="flow-step"><strong>L2</strong> Agents</div>
  <div class="flow-step"><strong>L3</strong> Search: BFS → A*</div>
  <div class="flow-step"><strong>L4</strong> Local search</div>
  <div class="flow-step flow-star"><strong>L5</strong> Adversarial ⭐</div>
  <div class="flow-step"><strong>Lab 1</strong> Thực chiến</div>
</div>
