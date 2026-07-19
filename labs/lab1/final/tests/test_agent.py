"""
Unit test cho final/agent.py — bù lại lỗ hổng đã tự nhận ở explain.md mục 6:
"không có test case tự động (unit test) cho từng hàm riêng lẻ".

Chạy trực tiếp:
    source labs/lab1/.venv/bin/activate
    python labs/lab1/final/tests/test_agent.py

Hoặc qua unittest discovery:
    python -m unittest discover -s labs/lab1/final/tests -v

File này KHÔNG dùng sync_bench.py / bench_submissions - nó import thẳng
final/agent.py (nguồn "thật", nơi mình sửa trực tiếp) bằng importlib, tự chèn
đúng sys.path tới HideSeek/pacman/src trước khi load, để không phụ thuộc vào
bước đồng bộ thủ công sang submissions/0 hay bench_submissions/0.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

LAB1_DIR = Path(__file__).resolve().parent.parent.parent
AGENT_PATH = LAB1_DIR / "final" / "agent.py"
SRC_DIR = LAB1_DIR / "HideSeek" / "pacman" / "src"

# Chèn trước để "from agent_interface import ..." trong agent.py tìm thấy đúng
# module, dù agent.py tự tính sai src_path khi chạy từ vị trí final/ (nó giả
# định mình nằm trong submissions/<id>/agent.py, không phải final/agent.py).
sys.path.insert(0, str(SRC_DIR))

_spec = importlib.util.spec_from_file_location("final_agent_under_test", AGENT_PATH)
agent_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(agent_module)

from environment import Move  # noqa: E402  (phải sau khi đã chèn sys.path)

is_valid = agent_module.is_valid
get_neighbors = agent_module.get_neighbors
manhattan = agent_module.manhattan
astar = agent_module.astar
bfs_distances = agent_module.bfs_distances
pacman_step_positions = agent_module.pacman_step_positions
pacman_actions = agent_module.pacman_actions
PacmanAgent = agent_module.PacmanAgent
GhostAgent = agent_module.GhostAgent
CAPTURE_DIST = agent_module.CAPTURE_DIST
TIME_BUDGET = agent_module.TIME_BUDGET
_SearchTimeout = agent_module._SearchTimeout


def open_map(h, w):
    """Bản đồ trống toàn bộ, không tường, chỉ viền ngoài nếu cần tự vẽ."""
    return np.zeros((h, w), dtype=int)


def map_from_ascii(rows):
    """
    Dùng ký hiệu giống PDF đề bài: '#' = tường (1), '.' = đường đi (0).
    Mỗi phần tử list là 1 hàng, cùng độ dài.
    """
    return np.array([[1 if ch == "#" else 0 for ch in row] for row in rows], dtype=int)


# ---------------------------------------------------------------------------
# Helper functions dùng chung cho 2 agent
# ---------------------------------------------------------------------------

class TestIsValid(unittest.TestCase):
    def test_out_of_bounds(self):
        m = open_map(5, 5)
        self.assertFalse(is_valid((-1, 0), m))
        self.assertFalse(is_valid((0, -1), m))
        self.assertFalse(is_valid((5, 0), m))
        self.assertFalse(is_valid((0, 5), m))

    def test_wall_blocks(self):
        m = open_map(3, 3)
        m[1, 1] = 1
        self.assertFalse(is_valid((1, 1), m))

    def test_open_cell_ok(self):
        m = open_map(3, 3)
        self.assertTrue(is_valid((1, 1), m))


class TestGetNeighbors(unittest.TestCase):
    def test_open_map_center_has_4_neighbors(self):
        m = open_map(5, 5)
        neighbors = get_neighbors((2, 2), m)
        self.assertEqual(len(neighbors), 4)
        moves = {mv for _, mv in neighbors}
        self.assertEqual(moves, {Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT})

    def test_corner_has_2_neighbors(self):
        m = open_map(5, 5)
        neighbors = get_neighbors((0, 0), m)
        self.assertEqual(len(neighbors), 2)

    def test_walls_reduce_neighbors(self):
        m = map_from_ascii([
            "###",
            "#.#",
            "###",
        ])
        # ô (1,1) bị vây kín 4 phía -> không có láng giềng nào
        self.assertEqual(get_neighbors((1, 1), m), [])


class TestManhattan(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(manhattan((0, 0), (3, 4)), 7)
        self.assertEqual(manhattan((2, 2), (2, 2)), 0)


class TestAstar(unittest.TestCase):
    def test_same_start_goal_returns_empty(self):
        m = open_map(5, 5)
        self.assertEqual(astar(m, (2, 2), (2, 2)), [])

    def test_finds_straight_path(self):
        m = open_map(5, 5)
        path = astar(m, (0, 0), (0, 3))
        self.assertEqual(len(path), 3)
        self.assertTrue(all(mv == Move.RIGHT for mv in path))

    def test_no_path_when_goal_unreachable(self):
        # goal bị tách khỏi phòng start bằng tường kín, không có đường tới
        m = map_from_ascii([
            "#####",
            "#...#",
            "#####",
            "#...#",
            "#####",
        ])
        self.assertEqual(astar(m, (1, 1), (3, 1)), [])

    def test_path_respects_walls(self):
        m = map_from_ascii([
            "#####",
            "#...#",
            "#.#.#",
            "#...#",
            "#####",
        ])
        path = astar(m, (1, 1), (3, 3))
        self.assertGreater(len(path), 0)
        # thực thi từng bước, phải luôn đứng ở ô hợp lệ và đến đúng goal
        pos = (1, 1)
        for mv in path:
            dr, dc = mv.value
            pos = (pos[0] + dr, pos[1] + dc)
            self.assertTrue(is_valid(pos, m), f"bước đi qua tường tại {pos}")
        self.assertEqual(pos, (3, 3))


class TestBfsDistances(unittest.TestCase):
    def test_distance_zero_at_start(self):
        m = open_map(5, 5)
        dist = bfs_distances(m, (2, 2))
        self.assertEqual(dist[(2, 2)], 0)

    def test_open_map_matches_manhattan(self):
        m = open_map(5, 5)
        dist = bfs_distances(m, (0, 0))
        # bản đồ trống hoàn toàn: BFS distance phải = Manhattan distance
        for r in range(5):
            for c in range(5):
                self.assertEqual(dist[(r, c)], manhattan((0, 0), (r, c)))

    def test_wall_forces_longer_route(self):
        m = map_from_ascii([
            "#####",
            "#.#.#",
            "#.#.#",
            "#...#",
            "#####",
        ])
        dist = bfs_distances(m, (1, 1))
        # Manhattan tới (1,3) là 2, nhưng có tường chắn giữa nên phải đi vòng
        self.assertEqual(manhattan((1, 1), (1, 3)), 2)
        self.assertGreater(dist[(1, 3)], 2)

    def test_unreachable_cell_absent(self):
        m = map_from_ascii([
            "#####",
            "#...#",
            "#####",
            "#...#",
            "#####",
        ])
        dist = bfs_distances(m, (1, 1))
        self.assertNotIn((3, 1), dist)


class TestPacmanStepPositions(unittest.TestCase):
    def test_stops_at_wall(self):
        m = map_from_ascii([
            "####",
            "#..#",
            "#.##",
            "####",
        ])
        # từ (1,1) đi RIGHT tối đa speed=2, nhưng (1,3) là tường -> chỉ được 1 ô
        positions = pacman_step_positions((1, 1), Move.RIGHT, m, speed=2)
        self.assertEqual(positions, [(1, 2)])

    def test_full_speed_on_open_corridor(self):
        m = open_map(5, 5)
        positions = pacman_step_positions((2, 0), Move.RIGHT, m, speed=2)
        self.assertEqual(positions, [(2, 1), (2, 2)])

    def test_zero_positions_when_immediately_blocked(self):
        m = map_from_ascii([
            "###",
            "#.#",
            "###",
        ])
        positions = pacman_step_positions((1, 1), Move.RIGHT, m, speed=2)
        self.assertEqual(positions, [])


class TestPacmanActions(unittest.TestCase):
    def test_includes_stay_and_no_duplicates(self):
        m = open_map(5, 5)
        actions = pacman_actions((2, 2), m)
        self.assertIn((2, 2), actions)
        self.assertEqual(len(actions), len(set(actions)))

    def test_reaches_up_to_speed_2_away(self):
        m = open_map(5, 5)
        actions = pacman_actions((2, 2), m)
        self.assertIn((2, 4), actions)  # RIGHT x2
        self.assertIn((0, 2), actions)  # UP x2


# ---------------------------------------------------------------------------
# PacmanAgent
# ---------------------------------------------------------------------------

class TestPacmanAgent(unittest.TestCase):
    def setUp(self):
        self.agent = PacmanAgent(pacman_speed=2)

    def test_enemy_none_returns_stay(self):
        m = open_map(5, 5)
        move = self.agent.step(m, (0, 0), None, 1)
        self.assertEqual(move, (Move.STAY, 1))

    def test_chases_along_shortest_path(self):
        m = open_map(5, 5)
        move, steps = self.agent.step(m, (0, 0), (0, 3), 1)
        self.assertEqual(move, Move.RIGHT)
        self.assertGreaterEqual(steps, 1)
        self.assertLessEqual(steps, 2)  # pacman_speed=2

    def test_speed_multiplier_used_on_straight_corridor(self):
        m = open_map(5, 5)
        # kẻ thù ở thẳng hàng, cách xa hơn 2 ô -> phải đi tối đa speed=2
        move, steps = self.agent.step(m, (2, 0), (2, 4), 1)
        self.assertEqual(move, Move.RIGHT)
        self.assertEqual(steps, 2)

    def test_returns_stay_when_no_path_exists(self):
        m = map_from_ascii([
            "#####",
            "#...#",
            "#####",
            "#...#",
            "#####",
        ])
        move = self.agent.step(m, (1, 1), (3, 1), 1)
        self.assertEqual(move, (Move.STAY, 1))

    def test_never_raises_on_malformed_input(self):
        m = open_map(5, 5)
        # my_position=None làm tuple(my_position) ném TypeError - try/except
        # phải bắt và trả về nước an toàn thay vì cho crash lan ra ngoài.
        move = self.agent.step(m, None, (1, 1), 1)
        self.assertEqual(move, (Move.STAY, 1))


# ---------------------------------------------------------------------------
# GhostAgent - các hàm nội bộ
# ---------------------------------------------------------------------------

class TestGhostAgentEvaluate(unittest.TestCase):
    def setUp(self):
        self.agent = GhostAgent()
        self.map = open_map(9, 9)
        self.agent._prepare_map(self.map)

    def test_farther_from_pacman_scores_higher(self):
        near = self.agent._evaluate((4, 5), (4, 4))
        far = self.agent._evaluate((0, 0), (4, 4))
        self.assertGreater(far, near)

    def test_dead_end_penalized(self):
        m = map_from_ascii([
            "#####",
            "#...#",
            "#.#.#",
            "#...#",
            "#####",
        ])
        agent = GhostAgent()
        agent._prepare_map(m)
        # (1,1) có 2 láng giềng (degree=2), (1,2) cũng mở - so sánh 1 ô thật sự
        # là ngõ cụt (degree<=1) với 1 ô thoáng để kiểm tra phạt -20 có áp dụng
        dead_end_map = map_from_ascii([
            "#####",
            "#...#",
            "###.#",
            "#...#",
            "#####",
        ])
        agent2 = GhostAgent()
        agent2._prepare_map(dead_end_map)
        pac_pos = (1, 1)
        dead_end_score = agent2._evaluate((3, 1), pac_pos)  # ô (3,1): degree=1 thật sự
        self.assertEqual(agent2._degree[(3, 1)], 1)
        open_score = agent2._evaluate((3, 3), pac_pos)  # ô thoáng hơn, cùng tầm khoảng cách
        # cả 2 có thể khác khoảng cách, nhưng điểm phạt -20 phải thể hiện rõ trong
        # so sánh với 1 ô degree>=2 có CÙNG khoảng cách tới pacman
        same_dist_open = [
            p for p in agent2._degree
            if manhattan(p, pac_pos) == manhattan((3, 1), pac_pos) and agent2._degree[p] >= 2
        ]
        if same_dist_open:
            other = same_dist_open[0]
            self.assertLess(dead_end_score, agent2._evaluate(other, pac_pos))

    def test_prev_pos_penalized(self):
        agent = GhostAgent()
        agent._prepare_map(self.map)
        agent._prev_pos = (2, 2)
        score_same = agent._evaluate((2, 2), (5, 5))
        agent._prev_pos = (9, 9)  # giả lập khác vị trí trước đó
        score_diff = agent._evaluate((2, 2), (5, 5))
        self.assertLess(score_same, score_diff)


class TestGhostAgentMinimax(unittest.TestCase):
    """
    Minimax + alpha-beta + deadline (iterative deepening quản lý ở _search_best_move,
    đây là đơn vị nhỏ nhất: 1 lần gọi _minimax với depth/deadline cụ thể).
    """

    def setUp(self):
        self.agent = GhostAgent()
        self.map = open_map(9, 9)
        self.agent._prepare_map(self.map)
        self.dist_map = bfs_distances(self.map, (4, 4))
        self.far_future_deadline = agent_module.time.perf_counter() + 5

    def test_capture_distance_is_catastrophic(self):
        val = self.agent._minimax(
            (4, 4), (4, 4), depth=2, alpha=float("-inf"), beta=float("inf"),
            maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=self.far_future_deadline,
        )
        self.assertLess(val, -50000)

    def test_depth_zero_matches_evaluate(self):
        val = self.agent._minimax(
            (0, 0), (4, 4), depth=0, alpha=float("-inf"), beta=float("inf"),
            maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=self.far_future_deadline,
        )
        self.assertEqual(val, self.agent._evaluate((0, 0), (4, 4)))

    def test_deeper_capture_penalized_less_than_immediate(self):
        # bị bắt ngay (depth còn lại lớn) phải tệ hơn bị bắt ở một node xa hơn
        # trong cây (depth còn lại nhỏ) - đúng định nghĩa "-100000 - depth".
        immediate = self.agent._minimax(
            (4, 4), (4, 4), depth=3, alpha=float("-inf"), beta=float("inf"),
            maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=self.far_future_deadline,
        )
        later = self.agent._minimax(
            (4, 4), (4, 4), depth=1, alpha=float("-inf"), beta=float("inf"),
            maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=self.far_future_deadline,
        )
        self.assertLess(immediate, later)

    def test_expired_deadline_raises_search_timeout(self):
        expired_deadline = agent_module.time.perf_counter() - 1
        with self.assertRaises(_SearchTimeout):
            self.agent._minimax(
                (0, 0), (4, 4), depth=3, alpha=float("-inf"), beta=float("inf"),
                maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=expired_deadline,
            )

    def test_deterministic_given_same_inputs(self):
        # không có random trong minimax - gọi 2 lần với đúng cùng tham số phải ra
        # đúng 1 giá trị, khớp luật đề bài (mỗi trận chỉ chạy 1 lần, không may rủi).
        val_a = self.agent._minimax(
            (4, 4), (0, 0), depth=2, alpha=float("-inf"), beta=float("inf"),
            maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=self.far_future_deadline,
        )
        val_b = self.agent._minimax(
            (4, 4), (0, 0), depth=2, alpha=float("-inf"), beta=float("inf"),
            maximizing=True, map_state=self.map, pac_dist_map=self.dist_map, deadline=self.far_future_deadline,
        )
        self.assertEqual(val_a, val_b)


class TestGhostAgentGreedyFallback(unittest.TestCase):
    """
    Hàm này là logic của bản initial, giữ nguyên - so sánh với công thức
    gốc (BFS distance * 10 + mobility) để bảo vệ khỏi bị đổi ngầm khi refactor.
    """

    def test_matches_initial_formula_on_small_map(self):
        m = map_from_ascii([
            "#####",
            "#...#",
            "#.#.#",
            "#...#",
            "#####",
        ])
        agent = GhostAgent()
        my_pos, pac_pos = (3, 3), (1, 1)
        move = agent._greedy_fallback(my_pos, pac_pos, m)

        dist_map = bfs_distances(m, pac_pos)
        best_move, best_score = Move.STAY, -1
        for npos, mv in get_neighbors(my_pos, m) + [(my_pos, Move.STAY)]:
            dist = dist_map.get(npos, -1)
            if dist == -1:
                continue
            mobility = len(get_neighbors(npos, m))
            score = dist * 10 + mobility
            if score > best_score:
                best_score, best_move = score, mv

        self.assertEqual(move, best_move)

    def test_accepts_precomputed_dist_map(self):
        m = open_map(5, 5)
        pac_pos = (2, 2)
        dist_map = bfs_distances(m, pac_pos)
        move_with_map = GhostAgent()._greedy_fallback((0, 0), pac_pos, m, dist_map=dist_map)
        move_without_map = GhostAgent()._greedy_fallback((0, 0), pac_pos, m)
        self.assertEqual(move_with_map, move_without_map)


# ---------------------------------------------------------------------------
# GhostAgent.step - hành vi tổng thể + an toàn
# ---------------------------------------------------------------------------

class TestGhostAgentStep(unittest.TestCase):
    def test_enemy_none_returns_stay(self):
        agent = GhostAgent()
        m = open_map(5, 5)
        self.assertEqual(agent.step(m, (2, 2), None, 1), Move.STAY)

    def test_returns_valid_move_type_on_normal_map(self):
        agent = GhostAgent()
        m = open_map(9, 9)
        move = agent.step(m, (4, 4), (0, 0), 1)
        self.assertIsInstance(move, Move)

    def test_no_crash_on_single_cell_map(self):
        m = map_from_ascii(["#"])
        agent = GhostAgent()
        # không có láng giềng nào cả -> phải rơi về Move.STAY, không được crash
        move = agent.step(m, (0, 0), (0, 0), 1)
        self.assertEqual(move, Move.STAY)

    def test_never_raises_on_malformed_input(self):
        agent = GhostAgent()
        m = open_map(5, 5)
        move = agent.step(m, None, (1, 1), 1)
        self.assertEqual(move, Move.STAY)

    def test_respects_time_budget_on_largest_map(self):
        # bản đồ thật trong đề bài là 21x21 - 1 bước phải luôn nằm trong TIME_BUDGET
        # (có biên an toàn dưới 1s thật sự của đề bài), dù iterative deepening có
        # thể chạy nhiều vòng bên trong.
        import time as _time
        agent = GhostAgent()
        m = open_map(21, 21)
        t0 = _time.perf_counter()
        move = agent.step(m, (10, 10), (0, 0), 1)
        elapsed = _time.perf_counter() - t0
        self.assertIsInstance(move, Move)
        self.assertLess(elapsed, TIME_BUDGET + 0.3)  # chừa biên cho overhead ngoài search

    def test_falls_back_gracefully_when_time_budget_already_spent(self):
        agent = GhostAgent()
        m = open_map(9, 9)
        original_budget = agent_module.TIME_BUDGET
        try:
            # ép TIME_BUDGET âm -> deadline luôn nằm trong quá khứ ngay khi vừa tính
            # xong, buộc _search_best_move phải dừng ngay từ vòng depth=1 và trả về
            # kết quả của _greedy_fallback thay vì crash hay treo.
            agent_module.TIME_BUDGET = -1.0
            move = agent.step(m, (4, 4), (0, 0), 1)
            self.assertIsInstance(move, Move)
        finally:
            agent_module.TIME_BUDGET = original_budget

    def test_deterministic_given_same_state(self):
        # vị trí khởi tạo cố định + không có random trong logic -> 2 lần gọi
        # step với cùng input phải cho cùng 1 kết quả (khớp đúng luật đề bài:
        # mỗi trận chỉ chạy 1 lần, không có yếu tố may rủi).
        m = open_map(9, 9)
        agent_a = GhostAgent()
        agent_b = GhostAgent()
        move_a = agent_a.step(m, (4, 4), (0, 0), 1)
        move_b = agent_b.step(m, (4, 4), (0, 0), 1)
        self.assertEqual(move_a, move_b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
