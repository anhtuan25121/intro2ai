---
tags: [intro2ai, exam, practice]
---

# 📝 Đề thi tham khảo — Adversarial Search

> Bộ bài tập luyện tập cho phần thi giữa kì ([[Lecture 5 - Adversarial Search]]). Mỗi bài đều có **lời giải chi tiết** ngay bên dưới — hãy tự làm trước khi xem đáp án.

## Về nguồn tham khảo

Mình không tìm được đề thi giữa kì cũ **công khai đầy đủ** của chính khóa HCMUS (các tài liệu tìm thấy trên Scribd/Studocu đều bị khoá xem trước). Vì slide bài giảng của khóa này dựa theo giáo trình chuẩn quốc tế **AIMA (Artificial Intelligence: A Modern Approach — Russell & Norvig)**, các bài tập bên dưới được:
1. **Tự soạn mới, tự kiểm chứng từng bước** (đảm bảo đúng 100%, bám sát đúng công thức trong [[Lecture 5 - Adversarial Search]])
2. **Phỏng theo phong cách** đề thi thật của các khóa AI cùng giáo trình AIMA trên thế giới (đã kiểm tra hợp lệ), để bạn làm quen dạng câu hỏi thường gặp:
   - [AIMA Official Exercises — Chapter 5 Adversarial Search](https://github.com/aimacode/aima-exercises/tree/master/markdown/5-Adversarial-Search) (bộ bài tập chính thức đi kèm giáo trình)
   - [UC Berkeley CS188 — Practice Midterms (Minimax/Alpha-Beta/Expectimax)](https://inst.eecs.berkeley.edu/~cs188/sp23/assets/exam/cs188-sp23-practice-midterm.pdf)
   - [MIT 6.034 — Minimax & Alpha-Beta Recitation Solutions](https://web.mit.edu/6.034/wwwbob/recitation5-solns.pdf)
   - [Wisconsin CS 540 — Minimax & Alpha-Beta Homework Solutions](https://pages.cs.wisc.edu/~dyer/cs540/hw/hw2/HW2_written_sol.pdf)
   - [Yale CPSC 474 — Alpha-Beta Practice Exam Solutions](https://zoo.cs.yale.edu/classes/cs474/f2021/Examples/x2_practice_solutions.html)

Nếu muốn luyện thêm, các link trên có nhiều bài tập khác cùng dạng (có đáp án chính thức).

---

## Bài 1 — Minimax cơ bản (vẽ cây & tính giá trị)

Cho cây trò chơi sau (branching factor = 2, sâu 3 tầng). Tầng gốc là **MAX**, tầng kế là **MIN**, tầng lá là giá trị UTILITY:

```
                    A (MAX)
                 /        \
              B (MIN)     C (MIN)
             /    \        /    \
           D(MAX) E(MAX) F(MAX) G(MAX)
           /  \    /  \   /  \   /  \
          3    5  2    9  7   1  4   6
```

**Yêu cầu:**
a) Tính giá trị Minimax tại D, E, F, G, B, C, A.
b) MAX nên chọn nhánh nào (trái hay phải) tại root?

### Lời giải Bài 1

- D = max(3,5) = **5**
- E = max(2,9) = **9**
- F = max(7,1) = **7**
- G = max(4,6) = **6**
- B = min(D,E) = min(5,9) = **5**
- C = min(F,G) = min(7,6) = **6**
- A = max(B,C) = max(5,6) = **6**

→ MAX nên chọn nhánh **phải** (qua C), giá trị minimax của root = **6**.

---

## Bài 2 — Minimax + Alpha-Beta pruning đầy đủ

*(Bài tập này phỏng theo MIT 6.034, đã được tự kiểm chứng lại từng bước)*

Cho cây trò chơi (giá trị dưới mỗi lá là UTILITY):

```
A (MAX)
├── B (MIN)
│     ├── E (leaf) = 2
│     └── F (MAX)
│           ├── K (leaf) = 3
│           └── L (leaf) = 0
├── C (MIN)
│     ├── G (MAX)
│     │     ├── M (MIN)
│     │     │     ├── Q (leaf) = 1
│     │     │     └── R (leaf) = 10
│     │     └── N (leaf) = 7
│     └── H (leaf) = 6
└── D (MIN)
      ├── I (leaf) = 1
      └── J (MAX)
            ├── O (leaf) = 2
            └── P (leaf) = 20
```

**Yêu cầu:**
a) Dùng Minimax (không cắt tỉa), tính giá trị tại mọi node và cho biết MAX nên đi nhánh nào tại A.
b) Dùng Alpha-Beta pruning (duyệt trái → phải), liệt kê **các node bị cắt tỉa (pruned)** và giá trị α, β tại các node quan trọng.
c) Giải thích: giá trị root ở câu (b) có khác câu (a) không? Vì sao?

### Lời giải Bài 2

**a) Minimax thuần:**

| Node | Loại | Giá trị | Cách tính |
|---|---|---|---|
| M | MIN | 1 | min(Q=1, R=10) |
| G | MAX | 7 | max(M=1, N=7) |
| C | MIN | 6 | min(G=7, H=6) |
| F | MAX | 3 | max(K=3, L=0) |
| B | MIN | 2 | min(E=2, F=3) |
| J | MAX | 20 | max(O=2, P=20) |
| D | MIN | 1 | min(I=1, J=20) |
| **A** | **MAX** | **6** | max(B=2, **C=6**, D=1) |

→ MAX chọn nhánh **C**, giá trị root = **6**.

**b) Alpha-Beta (duyệt trái → phải), trace từng bước:**

```
MAX-VALUE(A, α=−∞, β=+∞)
 └─ B: MIN-VALUE(B, α=−∞, β=+∞)
      ├─ E=2 → v=2, β=2
      └─ F: MAX-VALUE(F, α=−∞, β=2)
            ├─ K=3 → v=3 ≥ β(2) → PRUNE L, return 3
      v=min(2,3)=2 → B trả về 2
 A: v=max(−∞,2)=2, α=2

 └─ C: MIN-VALUE(C, α=2, β=+∞)
      ├─ G: MAX-VALUE(G, α=2, β=+∞)
            ├─ M: MIN-VALUE(M, α=2, β=+∞)
                  ├─ Q=1 → v=1 ≤ α(2) → PRUNE R, return 1
            v=max(−∞,1)=1, α=max(2,1)=2
            ├─ N=7 → v=max(1,7)=7, α=7
            G trả về 7
      v=min(+∞,7)=7, β=7
      ├─ H=6 → v=min(7,6)=6, β=6
      C trả về 6
 A: v=max(2,6)=6, α=6

 └─ D: MIN-VALUE(D, α=6, β=+∞)
      ├─ I=1 → v=1 ≤ α(6) → PRUNE toàn bộ nhánh J (gồm O, P), return 1
 A: v=max(6,1)=6 (không đổi)

A trả về 6
```

**Các node bị cắt tỉa (không cần evaluate):** L, R, và toàn bộ nhánh J (O, P) — tổng cộng **4 node lá** được cắt trong số 10 lá (E,K,L,Q,R,N,H,I,O,P).

**c)** Giá trị root **giống hệt** câu (a): đều bằng **6**, chọn nhánh **C**. Alpha-Beta **không bao giờ thay đổi giá trị/quyết định ở root** — nó chỉ **bỏ qua sớm** các nhánh chắc chắn không ảnh hưởng đến kết quả cuối cùng.

---

## Bài 3 — Ảnh hưởng của thứ tự duyệt (move ordering) đến Alpha-Beta

Cho cây: root MAX có 2 con MIN là **L** và **R**; L có 2 lá {a=3, b=5}; R có 2 lá {c=2, d=9}.

**Yêu cầu:** So sánh số node bị cắt tỉa khi duyệt R theo thứ tự **(c, d)** so với thứ tự **(d, c)**.

### Lời giải Bài 3

Sau khi duyệt xong L: L = min(3,5) = 3 → tại root, α = 3 khi bắt đầu duyệt R với (α=3, β=+∞).

**Thứ tự (c, d)** — c=2 trước:
- v=2 (từ c) → kiểm tra v ≤ α (2 ≤ 3) → **đúng → cắt d luôn**, R trả về 2.
- **1 node bị cắt (d)**.

**Thứ tự (d, c)** — d=9 trước:
- v=9 (từ d) → kiểm tra v ≤ α (9 ≤ 3)? sai → không cắt, tiếp tục.
- v=min(9,2)=2 (từ c) → hết con, không còn gì để cắt.
- **0 node bị cắt** — phải duyệt cả 2 lá.

**Kết luận:** Giá trị cuối cùng của root **giống hệt nhau** (root = max(3,2) = 3) ở cả 2 thứ tự — nhưng thứ tự **(c, d)** (đưa giá trị "nguy hiểm" — dễ gây cắt tỉa — lên trước) **hiệu quả hơn**. Đây chính là lý do vì sao move ordering (ví dụ ưu tiên xét nước ăn quân trước trong cờ vua) giúp Alpha-Beta đạt gần độ phức tạp O(b^(m/2)).

---

## Bài 4 — Expectiminimax (game có yếu tố ngẫu nhiên)

Cho cây: root là **MAX**, có 2 action **Trái** và **Phải**, mỗi action dẫn tới 1 node **CHANCE**, dưới mỗi outcome của CHANCE là 1 node **MIN** với 2 lá.

```
Root (MAX)
├── Trái → C1 (CHANCE)
│     ├── p=0.5 → M1 (MIN): lá {5, 2}
│     └── p=0.5 → M2 (MIN): lá {8, 4}
└── Phải → C2 (CHANCE)
      ├── p=0.3 → M3 (MIN): lá {6, 9}
      └── p=0.7 → M4 (MIN): lá {1, 10}
```

**Yêu cầu:** Tính EXPECTIMINIMAX(root) và cho biết MAX nên chọn action nào.

### Lời giải Bài 4

- M1 = min(5,2) = **2**
- M2 = min(8,4) = **4**
- C1 = 0.5×M1 + 0.5×M2 = 0.5×2 + 0.5×4 = 1 + 2 = **3**

- M3 = min(6,9) = **6**
- M4 = min(1,10) = **1**
- C2 = 0.3×M3 + 0.7×M4 = 0.3×6 + 0.7×1 = 1.8 + 0.7 = **2.5**

- Root = max(C1=3, C2=2.5) = **3** → MAX chọn action **Trái**.

> **Lưu ý cách trình bày:** luôn viết rõ phép nhân xác suất × giá trị cho **từng outcome** trước khi cộng lại — không rút gọn tắt, giám khảo cần thấy từng bước.

---

## Bài 5 — Trắc nghiệm Đúng/Sai (lý thuyết)

Xác định Đúng/Sai và giải thích ngắn gọn:

1. Alpha-beta pruning có thể trả về giá trị root khác với Minimax đầy đủ.
2. Thứ tự duyệt node ảnh hưởng đến **số lượng node bị cắt tỉa**, nhưng không ảnh hưởng đến **giá trị cuối cùng** của root.
3. Tại node MIN, ta cắt tỉa khi `v ≥ β`.
4. Effective branching factor sau alpha-beta với thứ tự **ngẫu nhiên** luôn bằng đúng √b.
5. Trong trường hợp xấu nhất (thứ tự duyệt tệ nhất), Alpha-Beta có độ phức tạp thời gian **giống hệt** Minimax không cắt tỉa: O(b^m).
6. EVAL(s) bắt buộc phải là hàm tuyến tính theo các đặc trưng (features) của trạng thái.
7. Quiescence search giúp tránh horizon effect bằng cách mở rộng thêm tìm kiếm tại các vị trí "chưa ổn định" (non-quiescent).
8. Trong multiplayer game (>2 người chơi), utility vẫn có thể biểu diễn bằng 1 số vô hướng (scalar) duy nhất như 2 người chơi.
9. Node CHANCE trong Expectiminimax chọn giá trị **lớn nhất** trong các outcome, giống node MAX.
10. Alpha-beta pruning giúp AI đưa ra **nước đi tốt hơn** so với Minimax thuần.

### Đáp án Bài 5

1. **Sai.** Alpha-beta luôn cho giá trị root giống hệt Minimax đầy đủ — nó chỉ tăng tốc, không đổi kết quả.
2. **Đúng.** Đây là bản chất của pruning: bỏ qua nhánh chắc chắn không tốt hơn, không ảnh hưởng quyết định cuối.
3. **Sai.** Điều kiện `v ≥ β` là cắt tỉa tại node **MAX**. Ở node MIN, điều kiện đúng là `v ≤ α`.
4. **Sai.** √b chỉ đạt được với thứ tự duyệt **tốt nhất (best-case)**. Với thứ tự ngẫu nhiên, độ phức tạp gần O(b^(3m/4)).
5. **Đúng.** Worst-case của Alpha-Beta (thứ tự tệ nhất, không cắt được gì) bằng đúng Minimax thuần O(b^m); chỉ có best-case mới đạt O(b^(m/2)).
6. **Sai.** Tuyến tính chỉ là 1 lựa chọn phổ biến/dễ tính; EVAL(s) không bắt buộc tuyến tính, miễn thỏa 3 điều kiện (giữ thứ tự win>draw>loss, tính nhanh, tương quan thắng thực tế).
7. **Đúng.**
8. **Sai.** Multiplayer cần **vector lợi ích** (mỗi phần tử ứng với 1 player), không dùng scalar như 2 người chơi.
9. **Sai.** Node CHANCE tính **giá trị kỳ vọng** (Σ xác suất × giá trị), không phải max.
10. **Sai.** Alpha-beta chỉ giúp **nhanh hơn** (duyệt được sâu hơn trong cùng thời gian), bản thân nó không "giỏi hơn" Minimax về chất lượng nước đi khi so cùng độ sâu.

---

## Bài 6 — Câu hỏi tự luận ứng dụng

1. Với cờ carô (tic-tac-toe) 3×3, hãy đề xuất UTILITY(s, X) hợp lý cho 3 trường hợp: X thắng, O thắng, hoà.
2. Một agent chơi cờ vua chỉ có 1 giây suy nghĩ mỗi nước. Nên ưu tiên cải thiện **move ordering** hay tăng **độ sâu cutoff**? Giải thích bằng công thức độ phức tạp.
3. Một bạn sinh viên nói: "Alpha-beta pruning giúp AI chơi cờ **giỏi hơn** vì nó tìm ra nước đi **tốt hơn** Minimax." Nhận định này đúng hay sai? Vì sao?
4. Nếu 1 trò chơi có **3 người chơi** (multiplayer) thay vì 2, Minimax cần thay đổi gì về cách biểu diễn utility?
5. Vì sao Adversarial Search không thể áp dụng thuật toán **Hill-Climbing** (Lecture 4) để chọn nước đi?

### Gợi ý đáp án Bài 6

1. UTILITY(s,X) = +1 nếu X thắng, −1 nếu O thắng, 0 nếu hoà (theo đúng định nghĩa UTILITY(s,p) — giá trị lợi ích cho player p tại trạng thái kết thúc s).
2. Nên ưu tiên **move ordering tốt** trước: vì với ordering tốt, Alpha-Beta đạt O(b^(m/2)) — tương đương *tăng gấp đôi* độ sâu tìm được trong cùng thời gian so với ordering ngẫu nhiên O(b^(3m/4)). Cải thiện ordering thường "lời" hơn nhiều so với chỉ tăng cutoff depth mà giữ nguyên ordering kém.
3. **Sai.** Alpha-beta cho kết quả **giống hệt** Minimax nếu duyệt cùng độ sâu — nó không "giỏi hơn" về chất lượng quyết định, chỉ **nhanh hơn** (nhờ đó, gián tiếp, có thể tận dụng thời gian dư để tăng độ sâu tìm kiếm → lúc đó mới thực sự chơi tốt hơn).
4. Cần thay UTILITY (số vô hướng) bằng **utility vector** — mỗi phần tử là lợi ích của 1 người chơi cụ thể; mỗi node chọn hành động tối đa hoá thành phần tương ứng với player đang đến lượt.
5. Vì Hill-Climbing chỉ quan tâm **trạng thái hiện tại tốt tới đâu**, không dự đoán được **phản ứng của đối thủ** ở các nước tiếp theo — trong khi Adversarial Search bắt buộc phải "nhìn trước" cả chuỗi nước đi luân phiên giữa 2 bên (dùng search tree/Minimax) mới đưa ra quyết định đúng đắn.
