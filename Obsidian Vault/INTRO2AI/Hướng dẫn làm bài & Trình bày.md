---
tags: [intro2ai, exam, guide]
---

# ✍️ Hướng dẫn làm bài & Trình bày — Adversarial Search

> Mục tiêu trang này: biết **chính xác cách trình bày** từng dạng câu hỏi để **ăn trọn điểm**, tránh mất điểm oan vì thiếu bước trình bày dù hiểu đúng bản chất.

## Nguyên tắc chung khi làm bài thuật toán (áp dụng mọi dạng)

1. **Luôn ghi rõ loại node** (MAX hay MIN hay CHANCE) tại mỗi tầng trước khi tính — giám khảo chấm theo bước, không chỉ theo đáp số cuối.
2. **Ghi công thức trước khi thay số**: ví dụ viết `B = min(D, E)` rồi mới thay `= min(5,9) = 5`, đừng nhảy thẳng vào số.
3. **Không làm tắt/nhẩm trong đầu** — với alpha-beta và expectiminimax, phần lớn điểm nằm ở **bước trung gian** (giá trị α/β tại từng node, phép nhân xác suất), không chỉ đáp số cuối.
4. **Khoanh tròn/ghi chú rõ đáp số cuối** (giá trị root, nước đi được chọn) để giám khảo dễ tìm thấy.

---

## Dạng 1: Vẽ cây Minimax và tính giá trị

**Đề thường hỏi:** "Cho cây trò chơi sau, tính giá trị Minimax tại mỗi node và cho biết MAX/MIN nên chọn nhánh nào."

**Cách trình bày chuẩn:**
1. Ghi rõ **loại node từng tầng** (MAX/MIN) ngay cạnh cây — đừng để giám khảo phải tự suy ra.
2. Tính **từ lá lên gốc (bottom-up)** — không tính tắt từ gốc xuống.
3. Với mỗi node trung gian, viết:
   ```
   Tên_node (MAX/MIN) = max/min(giá trị con 1, giá trị con 2, ...) = <kết quả>
   ```
4. Ở node gốc, sau khi có giá trị, **ghi rõ nhánh nào được chọn** (không chỉ ghi con số) — vì đề thường hỏi "nước đi nào", không chỉ "giá trị bao nhiêu".

**Lỗi hay mất điểm:**
- Quên ghi loại node (MAX/MIN) → giám khảo không biết bạn có hiểu ai đang chọn ở tầng đó không.
- Tính giá trị đúng nhưng quên trả lời "chọn nhánh nào" khi đề hỏi.
- Nhầm lẫn thứ tự max/min giữa các tầng (đặc biệt khi cây có >3 tầng, dễ đếm nhầm tầng chẵn/lẻ).

→ Xem ví dụ mẫu ở [[Đề thi tham khảo - Adversarial Search]] Bài 1, Bài 2 (phần a).

---

## Dạng 2: Áp dụng Alpha-Beta Pruning

**Đề thường hỏi:** "Áp dụng Alpha-Beta pruning (duyệt trái→phải), cho biết node nào bị cắt tỉa, và giá trị α/β tại các node."

**Cách trình bày chuẩn (đây là dạng bài hay bị trừ điểm nhiều nhất nếu trình bày thiếu):**

1. **Luôn duyệt theo DFS, trái sang phải**, trừ khi đề nói khác.
2. Tại **mỗi node**, ghi rõ cặp `(α, β)` **khi bước vào node đó** (kế thừa từ node cha) — đây là bước hay bị bỏ qua nhất.
3. Khi xét xong mỗi node con, **cập nhật lại v, rồi kiểm tra điều kiện cắt tỉa**:
   - Ở node MAX: sau khi có `v`, kiểm tra `v ≥ β` → nếu đúng, dừng ngay, ghi chú **"cắt (prune) các con còn lại"**; nếu không, cập nhật `α = max(α, v)`.
   - Ở node MIN: kiểm tra `v ≤ α` → nếu đúng, **cắt các con còn lại**; nếu không, cập nhật `β = min(β, v)`.
4. Với mỗi nhánh bị cắt, **gạch chéo (✗) hoặc ghi rõ "pruned"** ngay trên hình vẽ — đừng chỉ bỏ qua không nhắc tới, giám khảo cần thấy bạn *biết* nhánh đó bị cắt chứ không phải *quên* làm.
5. Cuối cùng, đối chiếu: **giá trị root phải giống hệt Minimax thường** — nếu khác, chắc chắn bạn đã tính sai ở đâu đó.

**Khuôn mẫu trình bày từng node (khuyến khích viết theo mẫu này):**
```
Node X (MAX), nhận (α=.., β=..) từ node cha
  → xét con 1: v = ...   [so β? / so α?]   → (prune? / không prune, cập nhật α hoặc β)
  → xét con 2: v = ...   ...
  → trả về v = ...
```

**Lỗi hay mất điểm:**
- Cắt tỉa đúng nhánh nhưng **không giải thích lý do** (thiếu câu "vì v ≥ β" hay "vì v ≤ α").
- Quên cập nhật α/β sau mỗi bước — dẫn đến cắt sai hoặc không cắt được nhánh đáng lẽ phải cắt.
- Nhầm chiều bất đẳng thức giữa node MAX và MIN (lỗi phổ biến nhất — xem lại [[Cheat Sheet - Adversarial Search]] mục "Bẫy thường gặp").
- Duyệt sai thứ tự (phải-trái thay vì trái-phải) khi đề không yêu cầu khác.

→ Xem ví dụ mẫu có trace từng bước ở [[Đề thi tham khảo - Adversarial Search]] Bài 2 (phần b), Bài 3.

---

## Dạng 3: Câu hỏi lý thuyết ngắn / Đúng-Sai / So sánh

**Đề thường hỏi:** "Định nghĩa X là gì?", "So sánh A và B", "Đúng hay Sai: ...".

**Cách trình bày chuẩn:**
1. Với câu **định nghĩa**: nêu định nghĩa chính xác trước (1-2 câu), sau đó **cho ví dụ minh hoạ ngắn** — đừng chỉ nêu ví dụ mà bỏ qua định nghĩa gốc.
2. Với câu **so sánh** (VD: "So sánh Minimax và Alpha-Beta"): trình bày dạng bảng hoặc gạch đầu dòng theo từng tiêu chí (độ phức tạp, kết quả, độ chính xác) — tránh viết văn xuôi dài dòng khó chấm điểm.
3. Với câu **Đúng/Sai**: luôn **giải thích vì sao**, kể cả khi đề không yêu cầu — vì phần điểm chính thường nằm ở phần giải thích, không phải chỉ ở việc chọn Đúng/Sai đúng.

**Lỗi hay mất điểm:**
- Trả lời đúng/sai nhưng không giải thích → chỉ được 1 phần nhỏ số điểm câu đó.
- Nêu ví dụ nhưng thiếu định nghĩa tổng quát phía sau (giám khảo cần thấy bạn hiểu khái niệm, không chỉ thuộc ví dụ).

→ Xem bộ câu hỏi mẫu ở [[Đề thi tham khảo - Adversarial Search]] Bài 5, Bài 6 và phần "Câu hỏi tự kiểm tra nhanh" cuối [[Lecture 5 - Adversarial Search]].

---

## Dạng 4: Bài tập Expectiminimax (có node CHANCE)

**Đề thường hỏi:** "Tính EXPECTIMINIMAX tại root, cho biết MAX nên chọn action nào."

**Cách trình bày chuẩn:**
1. Tính giá trị các node MAX/MIN như bình thường trước (bottom-up).
2. Tại node CHANCE, **viết rõ từng số hạng** của tổng kỳ vọng, không rút gọn:
   ```
   CHANCE = P(kết_quả_1) × giá_trị_1 + P(kết_quả_2) × giá_trị_2 + ...
          = (0.5 × 2) + (0.5 × 4)
          = 1 + 2 = 3
   ```
3. Đảm bảo **tổng các xác suất trên các nhánh con của 1 node CHANCE bằng 1** — nếu đề cho xác suất mà tổng không phải 1, có thể bạn đọc nhầm đề.
4. Sau khi có giá trị tất cả CHANCE node, node MAX phía trên chọn **giá trị CHANCE lớn nhất** (không phải tính trung bình lần nữa).

**Lỗi hay mất điểm:**
- Nhầm CHANCE node với MAX/MIN node (lấy max/min thay vì tính kỳ vọng).
- Quên nhân xác suất, chỉ cộng giá trị thô.
- Sai số học khi cộng dồn nhiều số thập phân — nên viết từng bước rõ ràng để giám khảo (và chính bạn) dễ kiểm tra lại.

→ Xem ví dụ mẫu ở [[Đề thi tham khảo - Adversarial Search]] Bài 4.

---

## Dạng 5: Câu hỏi về cột mốc lịch sử (Deep Blue, Chinook, AlphaGo)

**Đề thường hỏi:** "Nêu số liệu về Deep Blue/Chinook/AlphaGo", hoặc lồng trong câu hỏi khác làm ví dụ minh hoạ.

**Cách trình bày chuẩn:**
- Nêu **đúng số liệu**, không cần nêu thừa nếu đề không hỏi (nêu sai số liệu bị trừ điểm nặng hơn là không nêu).
- Nếu không nhớ chính xác con số, ưu tiên nêu đúng **thứ tự lớn (order of magnitude)** và **tên/năm sự kiện** — đây là phần chắc chắn được chấm điểm dù thiếu chi tiết nhỏ.

→ Bảng số liệu đầy đủ ở [[Cheat Sheet - Adversarial Search]] mục 7.

---

## Quản lý thời gian trong phòng thi

Gợi ý phân bổ nếu đề có nhiều câu (điều chỉnh theo thời lượng thực tế của đề bạn):
1. **Đọc lướt toàn bộ đề trước** (2-3 phút) — xác định câu nào là "vẽ cây tính tay" (tốn thời gian nhất) và câu nào là lý thuyết (làm nhanh).
2. Làm **câu lý thuyết/Đúng-Sai trước** — chắc điểm, tốn ít thời gian.
3. Làm **câu Minimax thuần** trước **Alpha-Beta** — vì Alpha-Beta thường yêu cầu bạn đã hiểu đúng giá trị Minimax để đối chiếu.
4. Dành thời gian còn lại cho **Alpha-Beta / Expectiminimax** — đây là câu tốn thời gian và dễ sai sót nhỏ nhất, cần trình bày từng bước cẩn thận theo Dạng 2/4 ở trên.
5. **Luôn để lại 5 phút cuối** để kiểm tra lại: giá trị root Alpha-Beta có khớp Minimax không, tổng xác suất CHANCE node có bằng 1 không.

## Checklist trước khi nộp bài

- [ ] Mọi node trong cây đã ghi rõ loại (MAX/MIN/CHANCE)?
- [ ] Mọi phép tính trung gian đều hiển thị công thức, không chỉ đáp số?
- [ ] Nhánh bị cắt tỉa (nếu có) đã đánh dấu rõ + ghi lý do (v≥β hay v≤α)?
- [ ] Đáp số cuối (giá trị root, nước đi/action được chọn) đã được khoanh/nêu rõ ràng?
- [ ] Với câu Đúng/Sai, đã giải thích lý do chưa (không chỉ khoanh Đ/S)?
- [ ] Số liệu lịch sử (nếu có) nêu đúng, không bịa thêm nếu không chắc?

---

## Xem thêm
- [[Lecture 5 - Adversarial Search]] — lý thuyết đầy đủ
- [[Cheat Sheet - Adversarial Search]] — tóm tắt nhanh + bẫy thường gặp
- [[Đề thi tham khảo - Adversarial Search]] — bài tập luyện tập kèm lời giải mẫu đúng format
- [[Lộ trình học & Liên kết kiến thức]] — hiểu bối cảnh tổng thể môn học
