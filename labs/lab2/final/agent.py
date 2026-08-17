# - GROUP INFORMATION
#   + NO.: 0
#   + NAME: A-Star
#   + MEMBER: 2
#       - STUDENT ID #1: 19127616
#       - STUDENT ID #2: 19127615
#
# Lab 2 - Blind Adversary
# Strategy:
#   Seek: belief tracking + adversarial interception when Ghost is visible.
#   Hide: belief tracking of speed-2 Pacman + risk-aware evasion.
# The map is tiny (21x21), so a static graph model is precomputed once.

import sys
import time
import heapq
from collections import deque
from pathlib import Path

import numpy as np

_here = Path(__file__).resolve()
_candidate_src_paths = [
    _here.parent.parent.parent / "src",  # normal submissions/<group>/agent.py layout
    _here.parents[2] / "lab1" / "HideSeek" / "pacman" / "src",  # repo lab2/final
]
for _src in _candidate_src_paths:
    if _src.exists():
        sys.path.insert(0, str(_src))
        break

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move
from belief import EnemyTracker


MOVES = (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT)
PACMAN_SPEED_FOR_GHOST_MODEL = 2
CAPTURE_DISTANCE = 2  # Arena captures when Manhattan distance < 2.
INF = 30000

# Keep large safety margins below the 1 second arena limit.
PACMAN_SEARCH_BUDGET = 0.20
GHOST_SEARCH_BUDGET = 0.28
PACMAN_MAX_DEPTH = 5
GHOST_MAX_DEPTH = 4


class _SearchTimeout(Exception):
    pass


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def is_valid(pos, map_state):
    r, c = pos
    h, w = map_state.shape
    return 0 <= r < h and 0 <= c < w and map_state[r, c] != 1


def get_neighbors(pos, map_state):
    result = []
    for move in MOVES:
        dr, dc = move.value
        nxt = (pos[0] + dr, pos[1] + dc)
        if is_valid(nxt, map_state):
            result.append((nxt, move))
    return result


def astar(map_state, start, goal):
    """Shortest micro-step path on the known maze structure."""
    if start == goal:
        return []
    if not is_valid(start, map_state) or not is_valid(goal, map_state):
        return []

    heap = [(manhattan(start, goal), 0, 0, start)]
    parent = {start: (None, None)}
    best_g = {start: 0}
    counter = 0

    while heap:
        _, g, _, pos = heapq.heappop(heap)
        if g != best_g.get(pos):
            continue
        if pos == goal:
            path = []
            cur = pos
            while parent[cur][0] is not None:
                prev, move = parent[cur]
                path.append(move)
                cur = prev
            path.reverse()
            return path

        for nxt, move in get_neighbors(pos, map_state):
            ng = g + 1
            if ng < best_g.get(nxt, INF):
                best_g[nxt] = ng
                parent[nxt] = (pos, move)
                counter += 1
                heapq.heappush(
                    heap,
                    (ng + manhattan(nxt, goal), ng, counter, nxt),
                )
    return []


def follow_path(path, speed):
    if not path:
        return Move.STAY, 1
    first = path[0]
    steps = 1
    for i in range(1, min(int(speed), len(path))):
        if path[i] != first:
            break
        steps += 1
    return first, steps


def ghost_actions(pos, map_state):
    actions = [(pos, Move.STAY)]
    actions.extend(get_neighbors(pos, map_state))
    return actions


def pacman_actions(pos, map_state, speed):
    """Legal Pacman endpoints with the actual (move, steps) action."""
    actions = [(pos, Move.STAY, 1)]
    speed = max(1, int(speed))
    for move in MOVES:
        dr, dc = move.value
        cur = pos
        for steps in range(1, speed + 1):
            nxt = (cur[0] + dr, cur[1] + dc)
            if not is_valid(nxt, map_state):
                break
            actions.append((nxt, move, steps))
            cur = nxt
    return actions


class MazeModel:
    """Static graph features derived from walls, which are always visible."""

    def __init__(self, map_state, pacman_speed=2):
        self.map = np.asarray(map_state)
        self.h, self.w = self.map.shape
        self.walkable = self.map != 1
        self.cells = [tuple(x) for x in np.argwhere(self.walkable)]
        self.n = len(self.cells)
        self.index = {p: i for i, p in enumerate(self.cells)}
        self.pacman_speed = max(1, int(pacman_speed))

        self.neighbor_indices = [[] for _ in range(self.n)]
        self.degree = np.zeros(self.n, dtype=np.int16)
        for i, (r, c) in enumerate(self.cells):
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                q = (r + dr, c + dc)
                j = self.index.get(q)
                if j is not None:
                    self.neighbor_indices[i].append(j)
            self.degree[i] = len(self.neighbor_indices[i])

        self.dist = self._all_pairs_micro_distances()
        self.turn_dist = self._all_pairs_pacman_turns()
        self.capture_turn = self._capture_turn_matrix()

        # Escape-space heuristic: number of cells reachable within six micro-steps.
        self.local_space = np.sum(self.dist <= 6, axis=1).astype(np.int16)
        self.axis_clear = self._build_axis_clear_matrix()

    def _all_pairs_micro_distances(self):
        dmat = np.full((self.n, self.n), INF, dtype=np.int16)
        for source in range(self.n):
            dmat[source, source] = 0
            q = deque([source])
            while q:
                u = q.popleft()
                nd = int(dmat[source, u]) + 1
                for v in self.neighbor_indices[u]:
                    if dmat[source, v] == INF:
                        dmat[source, v] = nd
                        q.append(v)
        return dmat

    def _macro_neighbors(self, source_idx):
        r, c = self.cells[source_idx]
        result = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            cr, cc = r, c
            for _ in range(self.pacman_speed):
                q = (cr + dr, cc + dc)
                j = self.index.get(q)
                if j is None:
                    break
                result.append(j)
                cr, cc = q
        return result

    def _all_pairs_pacman_turns(self):
        macro = [self._macro_neighbors(i) for i in range(self.n)]
        dmat = np.full((self.n, self.n), INF, dtype=np.int16)
        for source in range(self.n):
            dmat[source, source] = 0
            q = deque([source])
            while q:
                u = q.popleft()
                nd = int(dmat[source, u]) + 1
                for v in macro[u]:
                    if dmat[source, v] == INF:
                        dmat[source, v] = nd
                        q.append(v)
        return dmat

    def _capture_turn_matrix(self):
        # Column g contains the turns needed for Pacman to end at g or an
        # adjacent walkable cell, which is sufficient for distance < 2.
        cap = np.empty_like(self.turn_dist)
        for g in range(self.n):
            targets = [g] + self.neighbor_indices[g]
            cap[:, g] = np.min(self.turn_dist[:, targets], axis=1)
        return cap

    def _build_axis_clear_matrix(self):
        visible = np.zeros((self.n, self.n), dtype=bool)
        for i, (r1, c1) in enumerate(self.cells):
            visible[i, i] = True
            for j in range(i + 1, self.n):
                r2, c2 = self.cells[j]
                clear = False
                if r1 == r2:
                    lo, hi = sorted((c1, c2))
                    clear = not np.any(self.map[r1, lo + 1:hi] == 1)
                elif c1 == c2:
                    lo, hi = sorted((r1, r2))
                    clear = not np.any(self.map[lo + 1:hi, c1] == 1)
                if clear:
                    visible[i, j] = True
                    visible[j, i] = True
        return visible

    def idx(self, pos):
        return self.index.get(tuple(pos))

    def micro_distance(self, a, b):
        ia, ib = self.idx(a), self.idx(b)
        if ia is None or ib is None:
            return manhattan(a, b)
        return int(self.dist[ia, ib])

    def capture_turns(self, pac, ghost):
        ip, ig = self.idx(pac), self.idx(ghost)
        if ip is None or ig is None:
            d = manhattan(pac, ghost)
            return max(0, (max(0, d - 1) + self.pacman_speed - 1) // self.pacman_speed)
        return int(self.capture_turn[ip, ig])

    def is_axis_clear(self, a, b):
        ia, ib = self.idx(a), self.idx(b)
        if ia is None or ib is None:
            return False
        return bool(self.axis_clear[ia, ib])

    def prob_vector(self, belief):
        if belief is None:
            return None
        try:
            probs = np.asarray([belief[p] for p in self.cells], dtype=np.float64)
            probs = np.nan_to_num(probs, nan=0.0, posinf=0.0, neginf=0.0)
            probs[probs < 0] = 0.0
            total = float(probs.sum())
            if total <= 1e-15:
                return None
            return probs / total
        except Exception:
            return None


class PacmanAgent(BasePacmanAgent):
    """Seeker: adversarial interception when visible, belief pursuit otherwise."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))
        self.tracker = EnemyTracker()  # Ghost moves at speed 1.
        self.model = None
        self._hidden_goal = None
        self._explore_goal = None
        self._visits = None
        self._seen_ever = None

    def _ensure_model(self, map_state):
        if self.model is None or self.model.map.shape != map_state.shape:
            self.model = MazeModel(map_state, pacman_speed=self.pacman_speed)
            self._visits = np.zeros(map_state.shape, dtype=np.int16)
            self._seen_ever = np.zeros(map_state.shape, dtype=bool)

    def _eval_visible(self, pac, ghost):
        if manhattan(pac, ghost) < CAPTURE_DISTANCE:
            return 100000.0
        ig = self.model.idx(ghost)
        turns = self.model.capture_turns(pac, ghost)
        maze = self.model.micro_distance(pac, ghost)
        degree = int(self.model.degree[ig]) if ig is not None else 4
        space = int(self.model.local_space[ig]) if ig is not None else 0
        los_bonus = 4.0 if self.model.is_axis_clear(pac, ghost) else 0.0

        # Pacman wants fewer turns to capture and prefers herding the Ghost into
        # low-mobility / low-space regions.
        return (
            -95.0 * turns
            - 3.0 * maze
            + 9.0 * (4 - degree)
            - 0.10 * space
            + los_bonus
        )

    def _visible_value(self, pac, ghost, depth, deadline, cache):
        if time.perf_counter() >= deadline:
            raise _SearchTimeout
        if manhattan(pac, ghost) < CAPTURE_DISTANCE:
            return 100000.0 + depth
        if depth <= 0:
            return self._eval_visible(pac, ghost)

        key = (pac, ghost, depth)
        if key in cache:
            return cache[key]

        p_actions = pacman_actions(pac, self.model.map, self.pacman_speed)
        p_actions.sort(
            key=lambda a: self.model.capture_turns(a[0], ghost)
        )
        best = float("-inf")

        for p2, _, _ in p_actions:
            worst = float("inf")
            g_actions = ghost_actions(ghost, self.model.map)
            # Ghost is assumed to choose the safest response.
            g_actions.sort(
                key=lambda a: self.model.capture_turns(p2, a[0]),
                reverse=True,
            )
            for g2, _ in g_actions:
                if manhattan(p2, g2) < CAPTURE_DISTANCE:
                    val = 100000.0 + depth
                else:
                    val = self._visible_value(p2, g2, depth - 1, deadline, cache)
                if val < worst:
                    worst = val
                # The Ghost has already found a response no better than an
                # existing Pacman alternative, so this Pacman action cannot win.
                if worst <= best:
                    break
            if worst > best:
                best = worst

        cache[key] = best
        return best

    def _search_visible_action(self, my_pos, ghost_pos):
        deadline = time.perf_counter() + PACMAN_SEARCH_BUDGET
        fallback_path = astar(self.model.map, my_pos, ghost_pos)
        if fallback_path:
            best_action = follow_path(fallback_path, self.pacman_speed)
        else:
            best_action = (Move.STAY, 1)

        root_actions = pacman_actions(my_pos, self.model.map, self.pacman_speed)
        root_actions.sort(
            key=lambda a: (
                self.model.capture_turns(a[0], ghost_pos),
                -a[2],
            )
        )

        for depth in range(1, PACMAN_MAX_DEPTH + 1):
            if time.perf_counter() >= deadline:
                break
            try:
                cache = {}
                local_best = None
                local_score = float("-inf")

                for p2, move, steps in root_actions:
                    worst = float("inf")
                    responses = ghost_actions(ghost_pos, self.model.map)
                    responses.sort(
                        key=lambda a: self.model.capture_turns(p2, a[0]),
                        reverse=True,
                    )
                    for g2, _ in responses:
                        if manhattan(p2, g2) < CAPTURE_DISTANCE:
                            val = 100000.0 + depth
                        else:
                            val = self._visible_value(
                                p2, g2, depth - 1, deadline, cache
                            )
                        worst = min(worst, val)
                        if worst <= local_score:
                            break

                    # Prefer a real move and then a longer straight stride on ties.
                    tie = (move != Move.STAY, steps)
                    best_tie = (
                        local_best is not None and local_best[0] != Move.STAY,
                        local_best[1] if local_best is not None else 0,
                    )
                    if worst > local_score or (
                        abs(worst - local_score) < 1e-9 and tie > best_tie
                    ):
                        local_score = worst
                        local_best = (move, steps)

                if local_best is not None:
                    best_action = local_best
            except _SearchTimeout:
                break

        return best_action


    def _select_initial_explore_goal(self, my_pos):
        """Systematically sweep cells that have never entered our field of view."""
        if self._seen_ever is None:
            return None
        my_idx = self.model.idx(my_pos)
        if my_idx is None:
            return None

        if self._explore_goal is not None:
            old_idx = self.model.idx(self._explore_goal)
            if (
                old_idx is not None
                and not self._seen_ever[self._explore_goal]
                and self.model.turn_dist[my_idx, old_idx] < INF
            ):
                return self._explore_goal

        candidates = []
        for i, pos in enumerate(self.model.cells):
            if self._seen_ever[pos]:
                continue
            d = int(self.model.turn_dist[my_idx, i])
            if d >= INF or d <= 0:
                continue
            # Prefer the nearest unrevealed cell.  On ties, prefer cells with
            # more surrounding space because one visit tends to reveal more rays.
            candidates.append((d, -int(self.model.local_space[i]), pos))

        if not candidates:
            self._explore_goal = None
            return None
        candidates.sort()
        self._explore_goal = candidates[0][2]
        return self._explore_goal

    def _select_hidden_goal(self, my_pos):
        probs = self.model.prob_vector(self.tracker.belief)
        if probs is None:
            return self.tracker.get_target(my_pos)

        my_idx = self.model.idx(my_pos)
        if my_idx is None:
            return self.tracker.get_target(my_pos)

        # A target is attractive when a sizeable amount of belief lies within
        # two maze steps of it, but it should also be reachable quickly.
        cluster_mass = (self.model.dist <= 2).dot(probs)
        travel_turns = self.model.turn_dist[my_idx].astype(np.float64)
        score = cluster_mass / (1.0 + 0.28 * travel_turns)

        if self._visits is not None:
            visit_vec = np.asarray([self._visits[p] for p in self.model.cells])
            score -= 0.0008 * visit_vec
        score[my_idx] -= 1.0  # do not deliberately target the current cell

        best_idx = int(np.argmax(score))
        candidate = self.model.cells[best_idx]

        # Commitment prevents a flat belief distribution from making the target
        # flip every step.  Keep the old goal while it remains competitive.
        old_idx = self.model.idx(self._hidden_goal) if self._hidden_goal is not None else None
        if old_idx is not None and self.model.turn_dist[my_idx, old_idx] < INF:
            if score[old_idx] >= 0.80 * score[best_idx]:
                return self._hidden_goal

        self._hidden_goal = candidate
        return candidate

    def step(self, map_state, my_position, enemy_position, step_number):
        try:
            my_pos = tuple(my_position)
            self._ensure_model(map_state)
            if self._visits is not None and is_valid(my_pos, map_state):
                self._visits[my_pos] = min(30000, int(self._visits[my_pos]) + 1)
            if self._seen_ever is not None:
                self._seen_ever |= (np.asarray(map_state) == 0)

            self.tracker.update(map_state, my_pos, enemy_position, step_number)

            if enemy_position is not None:
                self._hidden_goal = None
                self._explore_goal = None
                return self._search_visible_action(my_pos, tuple(enemy_position))

            if self.tracker.last_seen is None:
                goal = self._select_initial_explore_goal(my_pos)
            else:
                goal = self._select_hidden_goal(my_pos)
            if goal is not None:
                path = astar(map_state, my_pos, tuple(goal))
                if path:
                    return follow_path(path, self.pacman_speed)
                self._hidden_goal = None

            # Robust exploration fallback: walk toward the least-visited reachable
            # neighbor, preferring higher mobility to avoid oscillating in pockets.
            options = get_neighbors(my_pos, map_state)
            if options:
                def key(item):
                    pos, _ = item
                    visits = int(self._visits[pos]) if self._visits is not None else 0
                    degree = len(get_neighbors(pos, map_state))
                    return (visits, -degree, pos)
                _, move = min(options, key=key)
                return move, 1
            return Move.STAY, 1
        except Exception:
            return Move.STAY, 1


class GhostAgent(BaseGhostAgent):
    """Hider: conservative adversarial evasion + full belief-risk scoring."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tracker = EnemyTracker()
        # Pacman may move 1 or 2 cells straight in one arena step.
        self.tracker.max_enemy_speed = PACMAN_SPEED_FOR_GHOST_MODEL
        self.model = None
        self.history = deque(maxlen=8)
        self._patrol_target = None

    def _ensure_model(self, map_state):
        if self.model is None or self.model.map.shape != map_state.shape:
            self.model = MazeModel(
                map_state,
                pacman_speed=PACMAN_SPEED_FOR_GHOST_MODEL,
            )

    def _eval_visible(self, ghost, pac):
        if manhattan(ghost, pac) < CAPTURE_DISTANCE:
            return -100000.0

        ig = self.model.idx(ghost)
        turns = self.model.capture_turns(pac, ghost)
        maze = self.model.micro_distance(pac, ghost)
        degree = int(self.model.degree[ig]) if ig is not None else 0
        space = int(self.model.local_space[ig]) if ig is not None else 0

        # Leaving the shared row/column (or hiding behind a wall) guarantees that
        # a cross-shaped sensor cannot see this state, independent of radius.
        hidden_bonus = 32.0 if not self.model.is_axis_clear(ghost, pac) else -6.0

        score = (
            105.0 * turns
            + 3.5 * maze
            + 11.0 * degree
            + 0.12 * space
            + hidden_bonus
        )
        if degree <= 1:
            score -= 80.0
        if ghost in self.history:
            score -= 5.0
        return score

    def _visible_value(self, ghost, pac, depth, deadline, cache):
        if time.perf_counter() >= deadline:
            raise _SearchTimeout
        if manhattan(ghost, pac) < CAPTURE_DISTANCE:
            return -100000.0 - depth
        if depth <= 0:
            return self._eval_visible(ghost, pac)

        key = (ghost, pac, depth)
        if key in cache:
            return cache[key]

        best = float("-inf")
        g_actions = ghost_actions(ghost, self.model.map)
        g_actions.sort(
            key=lambda a: self.model.capture_turns(pac, a[0]),
            reverse=True,
        )

        for g2, _ in g_actions:
            worst = float("inf")
            p_actions = pacman_actions(
                pac,
                self.model.map,
                PACMAN_SPEED_FOR_GHOST_MODEL,
            )
            p_actions.sort(key=lambda a: self.model.capture_turns(a[0], g2))
            for p2, _, _ in p_actions:
                if manhattan(g2, p2) < CAPTURE_DISTANCE:
                    val = -100000.0 - depth
                else:
                    val = self._visible_value(g2, p2, depth - 1, deadline, cache)
                worst = min(worst, val)
                if worst <= best:
                    break
            best = max(best, worst)

        cache[key] = best
        return best

    def _search_visible_move(self, my_pos, pac_pos):
        deadline = time.perf_counter() + GHOST_SEARCH_BUDGET
        best_move = self._belief_risk_move(my_pos)

        roots = ghost_actions(my_pos, self.model.map)
        roots.sort(
            key=lambda a: self.model.capture_turns(pac_pos, a[0]),
            reverse=True,
        )

        for depth in range(1, GHOST_MAX_DEPTH + 1):
            if time.perf_counter() >= deadline:
                break
            try:
                cache = {}
                local_move = None
                local_score = float("-inf")

                for g2, move in roots:
                    worst = float("inf")
                    p_actions = pacman_actions(
                        pac_pos,
                        self.model.map,
                        PACMAN_SPEED_FOR_GHOST_MODEL,
                    )
                    p_actions.sort(key=lambda a: self.model.capture_turns(a[0], g2))
                    for p2, _, _ in p_actions:
                        if manhattan(g2, p2) < CAPTURE_DISTANCE:
                            val = -100000.0 - depth
                        else:
                            val = self._visible_value(
                                g2, p2, depth - 1, deadline, cache
                            )
                        worst = min(worst, val)
                        if worst <= local_score:
                            break

                    # On equal safety, moving is preferable to freezing in sight.
                    tie = (move != Move.STAY, self.model.micro_distance(pac_pos, g2))
                    best_tie = (
                        local_move is not None and local_move != Move.STAY,
                        -1,
                    )
                    if worst > local_score or (
                        abs(worst - local_score) < 1e-9 and tie > best_tie
                    ):
                        local_score = worst
                        local_move = move

                if local_move is not None:
                    best_move = local_move
            except _SearchTimeout:
                break

        return best_move


    def _hidden_position_score(self, pos, probs):
        g = self.model.idx(pos)
        if g is None:
            return float("-inf")
        degree = int(self.model.degree[g])
        space = int(self.model.local_space[g])
        if probs is None:
            score = 10.0 * degree + 0.10 * space
        else:
            cap_turns = self.model.capture_turn[:, g].astype(np.float64)
            expected_turns = float(np.dot(probs, cap_turns))
            risk_one = float(probs[cap_turns <= 1].sum())
            risk_two = float(probs[cap_turns <= 2].sum())
            los_mass = float(probs[self.model.axis_clear[:, g]].sum())
            score = (
                22.0 * expected_turns
                - 260.0 * risk_one
                - 75.0 * risk_two
                - 18.0 * los_mass
                + 10.0 * degree
                + 0.10 * space
            )
        if degree <= 1:
            score -= 70.0
        return score

    def _patrol_move(self, my_pos):
        """Move between junctions while Pacman is hidden.

        A stable junction target prevents one-step belief noise from making the
        Ghost oscillate inside a corridor.  If currently in a corridor, escape
        to the nearest junction first; afterwards choose a safe reachable one.
        """
        probs = self.model.prob_vector(self.tracker.belief)
        my_idx = self.model.idx(my_pos)
        if my_idx is None:
            return self._belief_risk_move(my_pos)

        target_idx = self.model.idx(self._patrol_target) if self._patrol_target is not None else None
        if target_idx is None or self._patrol_target == my_pos:
            junctions = [
                i for i in range(self.model.n)
                if int(self.model.degree[i]) >= 3 and self.model.cells[i] != my_pos
            ]
            if not junctions:
                self._patrol_target = None
                return self._belief_risk_move(my_pos)

            current_degree = int(self.model.degree[my_idx])
            if current_degree < 3:
                nearest = min(int(self.model.dist[my_idx, i]) for i in junctions)
                pool = [i for i in junctions if int(self.model.dist[my_idx, i]) == nearest]
                target_idx = max(
                    pool,
                    key=lambda i: self._hidden_position_score(self.model.cells[i], probs),
                )
            else:
                recent = set(self.history)
                def target_score(i):
                    pos = self.model.cells[i]
                    travel = int(self.model.dist[my_idx, i])
                    repeat_penalty = 25.0 if pos in recent else 0.0
                    return self._hidden_position_score(pos, probs) - 1.8 * travel - repeat_penalty
                target_idx = max(junctions, key=target_score)
            self._patrol_target = self.model.cells[target_idx]

        path = astar(self.model.map, my_pos, self._patrol_target)
        if path:
            return path[0]
        self._patrol_target = None
        return self._belief_risk_move(my_pos)

    def _belief_risk_move(self, my_pos):
        """Choose the safest one-step Ghost action using the whole Pacman belief."""
        actions = get_neighbors(my_pos, self.model.map)
        if not actions:
            actions = [(my_pos, Move.STAY)]
        probs = self.model.prob_vector(self.tracker.belief)

        if probs is None:
            # No usable enemy information: stay in a roomy junction rather than
            # drifting into a dead end.
            best = None
            best_score = float("-inf")
            for pos, move in actions:
                i = self.model.idx(pos)
                degree = int(self.model.degree[i]) if i is not None else 0
                space = int(self.model.local_space[i]) if i is not None else 0
                score = 12.0 * degree + 0.20 * space
                if pos in self.history:
                    score -= 3.0
                if move == Move.STAY:
                    score -= 0.5
                if score > best_score:
                    best_score = score
                    best = move
            return best if best is not None else Move.STAY

        best_move = Move.STAY
        best_score = float("-inf")
        for pos, move in actions:
            g = self.model.idx(pos)
            if g is None:
                continue

            cap_turns = self.model.capture_turn[:, g].astype(np.float64)
            expected_turns = float(np.dot(probs, cap_turns))
            risk_one = float(probs[cap_turns <= 1].sum())
            risk_two = float(probs[cap_turns <= 2].sum())
            los_mass = float(probs[self.model.axis_clear[:, g]].sum())

            degree = int(self.model.degree[g])
            space = int(self.model.local_space[g])
            history_penalty = 4.0 if pos in self.history else 0.0
            stay_penalty = 0.8 if move == Move.STAY else 0.0

            score = (
                22.0 * expected_turns
                - 260.0 * risk_one
                - 75.0 * risk_two
                - 18.0 * los_mass
                + 10.0 * degree
                + 0.10 * space
                - history_penalty
                - stay_penalty
            )
            if degree <= 1:
                score -= 70.0

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def step(self, map_state, my_position, enemy_position, step_number):
        try:
            my_pos = tuple(my_position)
            self._ensure_model(map_state)
            self.tracker.update(map_state, my_pos, enemy_position, step_number)

            if enemy_position is not None:
                self._patrol_target = None
                move = self._search_visible_move(my_pos, tuple(enemy_position))
            else:
                move = self._patrol_move(my_pos)

            self.history.append(my_pos)
            return move
        except Exception:
            try:
                my_pos = tuple(my_position)
                options = get_neighbors(my_pos, map_state)
                if options:
                    return max(options, key=lambda x: len(get_neighbors(x[0], map_state)))[1]
            except Exception:
                pass
            return Move.STAY
