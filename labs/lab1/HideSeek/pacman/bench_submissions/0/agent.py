# - GROUP INFORMATION
#   + NO.: 0
#   + NAME: A-Star
#   + MEMBER: 1
#       - STUDENT ID: 19127616
# Optimized submission - ban final

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
CAPTURE_DIST = 2  # de bai: bat duoc khi Manhattan distance < 2
ASSUMED_PACMAN_SPEED = 2  # ban final Pacman duoc di toi da 2 o thang hang moi luot
TIME_BUDGET = 0.65  # giay - chua bien an toan duoi muc gioi han 1s cua de bai
MAX_DEPTH = 10  # tran tren, thuc te thuong khong toi vi het TIME_BUDGET truoc


class _SearchTimeout(Exception):
    pass


# ---------------- Helper dung chung cho ca 2 agent ----------------

def is_valid(pos, map_state):
    r, c = pos
    h, w = map_state.shape
    if r < 0 or r >= h or c < 0 or c >= w:
        return False
    return map_state[r, c] == 0


def get_neighbors(pos, map_state):
    neighbors = []
    for move in MOVES:
        dr, dc = move.value
        npos = (pos[0] + dr, pos[1] + dc)
        if is_valid(npos, map_state):
            neighbors.append((npos, move))
    return neighbors


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


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
                heapq.heappush(heap, (ng + manhattan(npos, goal), ng, counter, npos, path + [move]))

    return []


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


def pacman_step_positions(pos, move, map_state, speed=ASSUMED_PACMAN_SPEED):
    """Cac vi tri Pacman co the dung lai neu di thang theo `move` toi da `speed` o (dung stop som khi dung tuong,
    giong cach environment.py thuc su di chuyen)."""
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


def pacman_actions(pos, map_state):
    """Toan bo vi tri Pacman co the den duoc trong 1 luot: dung yen, hoac di 1/2 o theo 1 trong 4 huong."""
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


# ---------------- Pacman: A* duoi thang, giu nguyen logic ban initial ----------------
#
# Da thu them 1 lop du doan huong di cua Ghost (noi suy tuyen tinh tu 2 vi tri gan nhat)
# nhung test thuc te qua 15 doi thu (script run_tournament.py) cho thay: 14/15 tran
# ket qua y het ban khong du doan, 1/15 tran (truoc Ghost nhom 8) lai CHAM HON 1 buoc -
# du doan tuyen tinh don gian bi lech khi doi thu di khong theo duong thang (vi du doi
# thu dung minimax). Loi ich = 0, rui ro > 0 nen bo tinh nang nay, chi giu lai A* truc
# tiep (da toi uu san, 15/15 tran o ban initial) cong them try/except cho an toan.

class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))

    def step(self, map_state, my_position, enemy_position, step_number):
        # Boc CA HAM trong try/except (khong chi doan astar) - neu tuple(...) hay bat ky
        # buoc nao khac loi thi van co 1 nuoc an toan de tra ve thay vi crash ca tran.
        try:
            if enemy_position is None:
                return (Move.STAY, 1)

            my_pos = tuple(my_position)
            target = tuple(enemy_position)

            path = astar(map_state, my_pos, target)
            if not path:
                return (Move.STAY, 1)

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


# ---------------- Ghost: minimax + alpha-beta + iterative deepening ----------------
#
# Y tuong: thay vi chi chon nuoc di xa Pacman nhat o buoc hien tai (greedy 1 buoc),
# mo phong truoc vai luot doi dap qua lai giua 2 ben (Ghost toi da hoa khoang cach,
# gia dinh Pacman toi thieu hoa no va co the di toi 2 o/luot). Neu minimax loi hoac
# khong kip chay het 1 vong nao, rot ve lai logic greedy ban dau cho an toan.

class GhostAgent(BaseGhostAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._map_ready = False
        self._degree = {}
        self._prev_pos = None

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
        # Dung khoang cach Manhattan THAT SU voi vi tri Pacman mo phong tai chinh node nay
        # (khong dung lai ban do khoang cach tinh san tu dau luot, vi Pacman mo phong co the
        # da di rat xa vi tri that sau vai nuoc trong cay - dung ban do cu se danh gia sai).
        dist = manhattan(ghost_pos, pac_pos)
        degree = self._degree.get(ghost_pos, 0)

        score = dist * 10 + degree * 3
        if degree <= 1:
            score -= 20  # dung o ngo cut / hanh lang cut la rui ro cao
        if ghost_pos == self._prev_pos:
            score -= 2  # phat nhe viec dung yen/quay lai cho cu de tranh bi doan bai

        return score

    def _minimax(self, ghost_pos, pac_pos, depth, alpha, beta, maximizing, map_state, pac_dist_map, deadline):
        if time.perf_counter() > deadline:
            raise _SearchTimeout

        if manhattan(ghost_pos, pac_pos) < CAPTURE_DIST:
            return -100000 - depth  # bi bat cang som (con nhieu depth con lai) cang te

        if depth == 0:
            return self._evaluate(ghost_pos, pac_pos)

        if maximizing:
            best = float("-inf")
            candidates = get_neighbors(ghost_pos, map_state) + [(ghost_pos, Move.STAY)]
            candidates.sort(key=lambda x: pac_dist_map.get(x[0], 0), reverse=True)
            for npos, _ in candidates:
                val = self._minimax(npos, pac_pos, depth - 1, alpha, beta, False, map_state, pac_dist_map, deadline)
                if val > best:
                    best = val
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return best
        else:
            best = float("inf")
            candidates = pacman_actions(pac_pos, map_state)
            candidates.sort(key=lambda p: manhattan(p, ghost_pos))
            for npos in candidates:
                val = self._minimax(ghost_pos, npos, depth - 1, alpha, beta, True, map_state, pac_dist_map, deadline)
                if val < best:
                    best = val
                beta = min(beta, best)
                if alpha >= beta:
                    break
            return best

    def _greedy_fallback(self, my_pos, pac_pos, map_state, dist_map=None):
        # logic cua ban initial submission - dung khi minimax loi hoac het gio ngay vong dau.
        # dist_map co the duoc truyen san (tu _search_best_move, da tinh roi) de khoi tinh lai BFS 2 lan/buoc.
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
        best_move = self._greedy_fallback(my_pos, pac_pos, map_state, dist_map=pac_dist_map)

        candidates_root = get_neighbors(my_pos, map_state) + [(my_pos, Move.STAY)]
        candidates_root.sort(key=lambda x: pac_dist_map.get(x[0], 0), reverse=True)

        depth = 1
        while depth <= MAX_DEPTH and time.perf_counter() < deadline:
            try:
                local_best_score = float("-inf")
                local_best_move = None
                for npos, move in candidates_root:
                    score = self._minimax(npos, pac_pos, depth, float("-inf"), float("inf"),
                                           False, map_state, pac_dist_map, deadline)
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
        # 2 lop an toan: (1) thu minimax day du; (2) neu loi (ke ca loi ngay o tuple(...))
        # thi rot ve greedy don gian; (3) neu ca greedy cung loi (vd map_state la rac) thi
        # tra ve STAY - khong bao gio de step() nem exception ra ngoai.
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
                move = self._greedy_fallback(tuple(my_position), tuple(enemy_position), map_state)
                self._prev_pos = tuple(my_position)
                return move
            except Exception:
                return Move.STAY
