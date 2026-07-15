---
layout: default
title: Lecture 2 - Intelligent Agents
---

# Lecture 2 — Intelligent Agents

> Không thuộc phạm vi thi giữa kì (chỉ Lecture 5). Trang này để tham khảo/hệ thống hóa.

## Agent là gì?

- **Agent**: nhận thức môi trường qua **sensors**, tác động qua **actuators**
- **Percept**: input tại 1 thời điểm · **Percept sequence**: lịch sử toàn bộ percept
- **Agent function**: f: P* → A (ánh xạ percept sequence → action) — khái niệm toán học
- **Agent program**: cài đặt thực tế của agent function (chỉ nhận percept hiện tại)
- `agent = architecture + program`

## Rationality (Tính hợp lý)

- **Rational agent**: chọn hành động **tối đa hoá performance measure kỳ vọng**, dựa trên percept sequence + tri thức sẵn có
- Phụ thuộc 4 yếu tố: **Performance measure, Prior knowledge, Percept sequence, Actions**
- **Rationality ≠ Perfection** (omniscience là bất khả thi trong thực tế)
- **Rational agent cần**:
  - **Information gathering**: hành động để thu thập thêm thông tin (exploration)
  - **Learning**: học từ percept để cải thiện
  - **Autonomy**: không chỉ dựa vào tri thức có sẵn của designer, mà tự học bù đắp tri thức thiếu/sai

## PEAS Framework

Đặc tả task environment gồm 4 thành phần: **P**erformance measure, **E**nvironment, **A**ctuators, **S**ensors

Ví dụ: Automated taxi driver

| PEAS | Nội dung |
|---|---|
| Performance | Safe, fast, legal, comfortable, maximize profit |
| Environment | Roads, traffic, pedestrians, customers |
| Actuators | Steering, accelerator, brake, signal, display |
| Sensors | Cameras, GPS, speedometer, sonar,... |

## Tính chất của Task Environment (7 cặp thuộc tính — RẤT HAY HỎI)

| Thuộc tính | Ý nghĩa |
|---|---|
| Fully vs Partially observable | Sensor thấy đủ toàn bộ state hay không |
| Single agent vs Multiagent | 1 agent hay nhiều agent (competitive/cooperative) |
| Deterministic vs Stochastic | Next state có xác định 100% bởi state+action không |
| Episodic vs Sequential | Quyết định hiện tại có ảnh hưởng quyết định tương lai không |
| Static vs Dynamic | Môi trường có tự thay đổi trong lúc agent suy nghĩ không |
| Discrete vs Continuous | Trạng thái/percept/action rời rạc hay liên tục |
| Known vs Unknown | Agent có biết luật/outcome của actions không |

- Môi trường đơn giản nhất: fully observable + deterministic + episodic + static + discrete + single-agent
- Hầu hết thực tế: partially observable + stochastic + sequential + dynamic + continuous + multi-agent

## Cấu trúc Agent (Agent Programs) — 5 loại, tăng dần độ phức tạp

1. **Simple reflex agent**
   - Chọn action chỉ dựa trên percept hiện tại, dùng condition-action rule: `IF percept THEN action`
   - Hạn chế: chỉ hoạt động tốt khi môi trường **fully observable**

2. **Model-based reflex agent**
   - Duy trì **internal state** để theo dõi phần môi trường không quan sát được (partial observability)
   - Cần model: "world evolves" + "how actions affect world"

3. **Goal-based agent**
   - Có thêm thông tin **goal** (mục tiêu) để lựa chọn action phù hợp mục tiêu
   - Linh hoạt hơn nhưng kém hiệu quả hơn reflex agent

4. **Utility-based agent**
   - Dùng **utility function** (nội tại hoá performance measure) để đánh giá "mức độ tốt" (degree of success), không chỉ đạt goal hay không
   - Cần khi có **nhiều goal xung đột** hoặc **goal không chắc chắn đạt được** — chọn action tối đa hoá **expected utility**

5. **Learning agent**
   - Gồm 4 thành phần: **Performance element** (chọn action) · **Critic** (đánh giá phản hồi so với performance standard) · **Learning element** (cải thiện) · **Problem generator** (đề xuất hành động khám phá)

## Ví dụ PEAS khác

Medical diagnosis · Satellite image analysis · Part-picking robot · Refinery controller · Interactive English tutor (xem bảng SGK)
