# - GROUP INFORMATION
#   + NO.: 0
#   + NAME: A-Star
#   + MEMBER: 2
#       - STUDENT ID #1: 19127616
#       - STUDENT ID #2: 19127615
# Optimized submission - bản final

import sys
import time
from pathlib import Path
from collections import deque
import heapq

src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move

MOVES = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
CAPTURE_DIST = 2  # bắt được khi Manhattan distance < 2
ASSUMED_PACMAN_SPEED = 2  # Pacman luôn được đi tối đa 2 ô thẳng hàng mỗi lượt
TIME_BUDGET = 0.65  # giây - <= 1s theo đề
MAX_DEPTH = 10  # trần trên số lượt minimax, tránh quá sâu gây timeout


class _SearchTimeout(Exception):
    # ngắt ngang minimax khi hết giờ, xem _search_best_move
    pass


# ô có đi được không (check ô không phải tường, ô nằm trong chứ không ra ngoài bản đồ)
def is_valid(pos, map_state):
    r, c = pos
    h, w = map_state.shape
    if r < 0 or r >= h or c < 0 or c >= w:
        return False
    return map_state[r, c] == 0


# các ô kề đi được từ 1 vị trí, kèm nước đi tương ứng
def get_neighbors(pos, map_state):
    neighbors = []
    for move in MOVES:
        dr, dc = move.value
        npos = (pos[0] + dr, pos[1] + dc)
        if is_valid(npos, map_state):
            neighbors.append((npos, move))
    return neighbors


# khoảng cách Manhattan giữa 2 ô
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# A* tìm đường ngắn nhất, trả về danh sách nước đi (rỗng nếu đã ở goal hoặc không tới được)
def astar(map_state, start, goal):
    if start == goal:
        return []

    counter = 0
    heap = [(manhattan(start, goal), 0, counter, start, [])]
    visited = set()

    while heap:
        _, g, _, pos, path = heapq.heappop(heap)
        if pos in visited:
            continue
        visited.add(pos)
        if pos == goal:
            return path
        for npos, move in get_neighbors(pos, map_state):
            if npos not in visited:
                ng = g + 1
                counter += 1
                f_score = ng + manhattan(npos, goal)
                heapq.heappush(heap, (f_score, ng, counter, npos, path + [move]))

    return []  # Không tìm được đường


# BFS từ 1 điểm, trả về khoảng cách THẬT (có tính tường) tới mọi ô đi được
def bfs_distances(map_state, start):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        pos = queue.popleft()
        for npos, _ in get_neighbors(pos, map_state):
            if npos not in dist:
                dist[npos] = dist[pos] + 1
                queue.append(npos)
    return dist


# BFS từ start, trả về khoảng cách thực tế đến mọi ô trong map
def pacman_step_positions(pos, move, map_state, speed=ASSUMED_PACMAN_SPEED):
    dr, dc = move.value
    positions = []
    cur = pos
    for _ in range(speed):
        nxt = (cur[0] + dr, cur[1] + dc)
        if not is_valid(nxt, map_state):
            break
        positions.append(nxt)
        cur = nxt
    return positions


# toàn bộ vị trí Pacman có thể tới trong 1 lượt: đứng yên, hoặc đi 1-2 ô theo 1 trong 4 hướng
def pacman_actions(pos, map_state):
    actions = [pos]
    for move in MOVES:
        actions.extend(pacman_step_positions(pos, move, map_state))
    seen = set()
    unique = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            unique.append(a)
    return unique


# Pacman: vai trò Seeker, dùng A* để đuổi Ghost, thêm try/except cho an toàn
class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))

    def step(self, map_state, my_position, enemy_position, step_number):
        try:
            if enemy_position is None:
                return (Move.STAY, 1)

            my_pos = tuple(my_position)
            target = tuple(enemy_position)

            # Tìm đường ngắn nhất đến Ghost
            path = astar(map_state, my_pos, target)
            if not path:
                return (Move.STAY, 1)

            # đi thẳng luôn nếu vài bước kế tiếp trong path cùng hướng với bước đầu
            first_move = path[0]
            steps = 1
            for i in range(1, min(self.pacman_speed, len(path))):
                if path[i] == first_move:
                    steps += 1
                else:
                    break

            return (first_move, steps)
        except Exception:
            return (Move.STAY, 1)


# Ghost: vai trò Hider, dùng minimax + alpha-beta + iterative deepening
class GhostAgent(BaseGhostAgent):
    # chỉ khởi tạo state rỗng ở đây - _degree được đổ dữ liệu thật ở _prepare_map bên dưới
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._map_ready = False
        self._degree = {}
        self._prev_pos = None

    # tính trước số ô kề đi được của mọi ô trên bản đồ, chỉ chạy 1 lần cho cả trận
    def _prepare_map(self, map_state):
        if self._map_ready:
            return
        h, w = map_state.shape
        for r in range(h):
            for c in range(w):
                if map_state[r, c] == 0:
                    pos = (r, c)
                    self._degree[pos] = len(get_neighbors(pos, map_state))
        self._map_ready = True

    def _evaluate(self, ghost_pos, pac_pos):
        # dùng Manhattan sống tại node này, không dùng lại bản đồ BFS tính sẵn từ đầu
        dist = manhattan(ghost_pos, pac_pos)
        degree = self._degree.get(ghost_pos, 0)

        score = dist * 10 + degree * 3
        if degree <= 1:
            score -= 20  # ngõ cụt / hành lang cụt, rủi ro cao
        if ghost_pos == self._prev_pos:
            score -= 2  # đứng yên/quay lại chỗ cũ hơi dễ đoán bài, phạt nhẹ

        return score

    # minimax với alpha-beta pruning, trả về score của node (không trả move)
    def _minimax(
        self,
        ghost_pos,
        pac_pos,
        depth,
        alpha,
        beta,
        maximizing,
        map_state,
        pac_dist_map,
        deadline,
    ):
        # hết giờ giữa chừng thì raise để _search_best_move bắt, dừng vòng iterative deepening
        # ở đây và giữ lại kết quả của độ sâu trước đó, không dùng kết quả tính dở
        if time.perf_counter() > deadline:
            raise _SearchTimeout

        if manhattan(ghost_pos, pac_pos) < CAPTURE_DIST:
            return -100000 - depth  # bị bắt càng sớm (depth còn lại càng nhiều) càng tệ

        if depth == 0:
            return self._evaluate(ghost_pos, pac_pos)

        if maximizing:
            # lượt Ghost: chọn nước giúp có max điểm. Sắp theo pac_dist_map trước (xa Pacman lúc đầu lượt nhất) chỉ để alpha-beta cắt sớm hơn, không ảnh hưởng kết quả cuối cùng.
            best = float("-inf")
            candidates = get_neighbors(ghost_pos, map_state) + [(ghost_pos, Move.STAY)]
            candidates.sort(key=lambda x: pac_dist_map.get(x[0], 0), reverse=True)

            for npos, _ in candidates:
                val = self._minimax(
                    npos,
                    pac_pos,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    map_state,
                    pac_dist_map,
                    deadline,
                )
                if val > best:
                    best = val
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return best
        else:
            # lượt Pacman: giả định nó chơi tối ưu, chọn nước làm Ghost tệ nhất
            best = float("inf")
            candidates = pacman_actions(pac_pos, map_state)
            candidates.sort(key=lambda p: manhattan(p, ghost_pos))

            for npos in candidates:
                val = self._minimax(
                    ghost_pos,
                    npos,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    map_state,
                    pac_dist_map,
                    deadline,
                )
                if val < best:
                    best = val
                beta = min(beta, best)
                if alpha >= beta:
                    break
            return best

    def _greedy_fallback(self, my_pos, pac_pos, map_state, dist_map=None):
        # logic của bản initial, dùng khi minimax lỗi hoặc chưa kịp xong vòng đầu.
        # dist_map cho phép truyền sẵn (từ _search_best_move) để đỡ tính BFS 2 lần/bước
        if dist_map is None:
            dist_map = bfs_distances(map_state, pac_pos)
        best_move = Move.STAY
        best_score = -1

        for npos, move in get_neighbors(my_pos, map_state) + [(my_pos, Move.STAY)]:
            dist = dist_map.get(npos, -1)

            if dist == -1:
                continue
            mobility = len(get_neighbors(npos, map_state))
            score = dist * 10 + mobility

            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def _search_best_move(self, my_pos, pac_pos, map_state, deadline):
        pac_dist_map = bfs_distances(map_state, pac_pos)
        best_move = self._greedy_fallback(
            my_pos, pac_pos, map_state, dist_map=pac_dist_map
        )

        candidates_root = get_neighbors(my_pos, map_state) + [(my_pos, Move.STAY)]
        candidates_root.sort(key=lambda x: pac_dist_map.get(x[0], 0), reverse=True)

        # iterative deepening: tăng dần độ sâu, mỗi độ sâu chạy xong hẳn mới cập nhật best_move - nếu hết giờ giữa chừng thì giữ kết quả của độ sâu trước đó
        depth = 1
        while depth <= MAX_DEPTH and time.perf_counter() < deadline:
            try:
                local_best_score = float("-inf")
                local_best_move = None

                for npos, move in candidates_root:
                    score = self._minimax(
                        npos,
                        pac_pos,
                        depth,
                        float("-inf"),
                        float("inf"),
                        False,
                        map_state,
                        pac_dist_map,
                        deadline,
                    )
                    if score > local_best_score:
                        local_best_score = score
                        local_best_move = move
                if local_best_move is not None:
                    best_move = local_best_move
            except _SearchTimeout:
                break
            depth += 1

        return best_move

    def step(self, map_state, my_position, enemy_position, step_number):
        # 2 lớp an toàn: minimax lỗi -> rớt về greedy; greedy cũng lỗi -> đứng yên. Không bao giờ để step() văng exception ra ngoài.
        try:
            if enemy_position is None:
                return Move.STAY

            my_pos = tuple(my_position)
            pac_pos = tuple(enemy_position)

            self._prepare_map(map_state)
            deadline = time.perf_counter() + TIME_BUDGET
            move = self._search_best_move(my_pos, pac_pos, map_state, deadline)
            self._prev_pos = my_pos

            return move

        except Exception:
            try:
                move = self._greedy_fallback(
                    tuple(my_position), tuple(enemy_position), map_state
                )
                self._prev_pos = tuple(my_position)

                return move
            except Exception:
                return Move.STAY
