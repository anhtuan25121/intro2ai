---
tags: [intro2ai]
---

# Lecture 3.1 — Problem Solving by Searching

> Không thuộc phạm vi thi giữa kì (chỉ Lecture 5). Nền tảng quan trọng cho [[Lecture 3.2 - Uninformed Search]] và [[Lecture 3.3 - Informed Search]].

## Goal-based agent & Problem formulation
- **Goal**: tập các trạng thái thế giới thoả mãn mục tiêu
- **Problem formulation**: quyết định state & action nào cần xét, dựa trên goal
- **Search**: quá trình tìm sequence of actions đạt goal
- **Execution phase**: thực hiện các action sau khi tìm được solution

```
function SIMPLE-PROBLEM-SOLVING-AGENT(percept) returns an action
  state ← UPDATE-STATE(state, percept)
  if seq is empty:
      goal ← FORMULATE-GOAL(state)
      problem ← FORMULATE-PROBLEM(state, goal)
      seq ← SEARCH(problem)
  action ← FIRST(seq); seq ← REST(seq)
  return action
```

## 5 thành phần định nghĩa Problem (well-defined problem)
| Thành phần | Ý nghĩa | Ví dụ (Romania) |
|---|---|---|
| **Initial state** | Trạng thái bắt đầu | In(Arad) |
| **Actions(s)** | Hành động khả dụng tại s | {Go(Sibiu), Go(Timisoara), Go(Zerind)} |
| **Transition model / Result(s,a)** | Kết quả khi thực hiện a tại s | Result(In(Arad),Go(Zerind)) = In(Zerind) |
| **Goal test** | Kiểm tra state có phải goal | In(Bucharest) |
| **Path cost** | Hàm chi phí (số, không âm) | c(In(Arad),Go(Zerind),In(Zerind)) = 75 |

- **State space**: đồ thị có hướng — node = state, edge = action; sinh ra từ initial state + actions + transition model
- **Optimal solution**: solution có path cost thấp nhất

## Formulating problems by Abstraction
- Loại bỏ chi tiết không cần thiết khỏi representation
- Abstraction tốt: loại bỏ tối đa chi tiết nhưng vẫn giữ **validity** và đảm bảo action trừu tượng **dễ thực hiện**

## Toy problems vs Real-world problems
| | Toy problems | Real-world problems |
|---|---|---|
| Mục đích | Luyện thuật toán, so sánh hiệu năng | Giải quyết vấn đề thực tế |
| Đặc điểm | Mô tả ngắn gọn, chính xác | Không có mô tả chuẩn duy nhất |
| Ví dụ | 8-puzzle, 8-queens, vacuum world, missionaries & cannibals | Route finding, TSP, VLSI layout, robot navigation |

### Ví dụ toy problems tiêu biểu
- **Vacuum world**: state = vị trí + tình trạng bẩn của các ô; 2×2ⁿ states
- **8-puzzle**: NP-complete, 9!/2 = 181,440 trạng thái khả dĩ; 15-puzzle: 1.3 nghìn tỷ trạng thái
- **8-queens**: Incremental formulation (thêm từng quân) vs Complete-state formulation (đặt hết rồi di chuyển)
- **Knuth's 4 problem**: minh họa không gian trạng thái vô hạn (factorial, sqrt, floor)

### Real-world problems tiêu biểu
- **Route-finding problem**: state = (location, time)
- **Touring problem**: state phải bao gồm cả **tập thành phố đã thăm** (visited set)
- **TSP (Traveling Salesperson Problem)**: NP-hard, mỗi thành phố thăm đúng 1 lần, tour ngắn nhất

## Search Tree & Infrastructure
- **Search tree**: cây các sequence hành động khả dĩ từ initial state (root)
- **Frontier**: tập các leaf node sẵn sàng để expand
- **Node structure**: STATE, PARENT, ACTION, PATH-COST (g(n))

### TREE-SEARCH vs GRAPH-SEARCH
- **TREE-SEARCH**: không nhớ visited states → có thể lặp vô hạn (redundant paths)
- **GRAPH-SEARCH**: thêm **explored set**, không mở rộng lại state đã explore/đang ở frontier
- **Separation property**: frontier chia state space thành 2 vùng — explored & unexplored; mọi path từ initial state đến unexplored phải đi qua frontier

## Đánh giá thuật toán tìm kiếm (4 tiêu chí — nền tảng cho các bài sau)
| Tiêu chí | Câu hỏi |
|---|---|
| **Completeness** | Luôn tìm được solution nếu tồn tại? |
| **Time complexity** | Bao lâu để tìm ra? |
| **Space complexity** | Cần bao nhiêu memory? |
| **Optimality** | Luôn tìm được solution chi phí thấp nhất? |

Đo bằng: **b** (branching factor), **d** (độ sâu của lời giải rẻ nhất), **m** (độ sâu tối đa của state space, có thể = ∞)

## Xem thêm
- [[Lộ trình học & Liên kết kiến thức]] — bảng đối chiếu khái niệm Lecture 3 ↔ Lecture 5
- [[Lecture 2 - Intelligent Agents]] — Goal-based agent, nguồn gốc của Problem formulation
- [[Lecture 5 - Adversarial Search]] — Game cũng được định nghĩa bằng 5-6 thành phần tương tự (S0, PLAYER, ACTIONS, RESULT, TERMINAL-TEST, UTILITY), search tree ở đây chính là nền tảng của Game tree (nội dung thi)
