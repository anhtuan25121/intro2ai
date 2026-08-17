"""Kiểm thử độc lập cho EnemyTracker.

Chạy tại thư mục labs/lab2/init:
    python test_belief.py
"""

from time import perf_counter

import numpy as np

from belief import EnemyTracker


def make_observation(shape, my_pos, radius=2, extra_walls=()):
    """Tạo map fog giả giống framework: -1 ngoài tầm nhìn, 0 trong tầm nhìn."""
    h, w = shape
    obs = np.full((h, w), -1, dtype=np.int8)

    # Tường biên và tường thêm luôn nhìn thấy.
    obs[0, :] = 1
    obs[-1, :] = 1
    obs[:, 0] = 1
    obs[:, -1] = 1
    for r, c in extra_walls:
        obs[r, c] = 1

    r0, c0 = my_pos
    if 0 <= r0 < h and 0 <= c0 < w and obs[r0, c0] != 1:
        obs[r0, c0] = 0

    # Tầm nhìn chữ thập; tia dừng khi gặp tường.
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        for distance in range(1, radius + 1):
            r = r0 + dr * distance
            c = c0 + dc * distance
            if not (0 <= r < h and 0 <= c < w):
                break
            if obs[r, c] == 1:
                break
            obs[r, c] = 0

    return obs


def assert_distribution(tracker, map_state):
    belief = tracker.belief
    assert belief is not None
    assert belief.shape == map_state.shape
    assert np.all(np.isfinite(belief)), "belief chứa NaN/Inf"
    assert np.all(belief >= 0.0), "belief chứa xác suất âm"
    assert np.allclose(belief[map_state == 1], 0.0), "tường có xác suất"
    assert np.isclose(float(belief.sum()), 1.0, atol=1e-10), belief.sum()


def test_seen_enemy_is_exact():
    tracker = EnemyTracker()
    my_pos = (10, 8)
    enemy_pos = (10, 10)
    obs = make_observation((21, 21), my_pos, radius=5)

    tracker.update(obs, my_pos, enemy_pos, step=0)

    assert tracker.get_target(my_pos) == enemy_pos
    assert np.isclose(tracker.belief[enemy_pos], 1.0)
    assert np.count_nonzero(tracker.belief) == 1
    assert_distribution(tracker, obs)


def test_lost_enemy_spreads():
    tracker = EnemyTracker()
    seen_my_pos = (10, 8)
    enemy_pos = (10, 10)
    seen_obs = make_observation((21, 21), seen_my_pos, radius=5)
    tracker.update(seen_obs, seen_my_pos, enemy_pos, step=0)

    # Di chuyển người quan sát ra xa để vùng dự đoán quanh enemy nằm trong fog.
    my_pos = (2, 2)
    hidden_obs = make_observation((21, 21), my_pos, radius=2)

    support_sizes = []
    for step in range(1, 5):
        tracker.update(hidden_obs, my_pos, None, step=step)
        assert_distribution(tracker, hidden_obs)
        support_sizes.append(int(np.count_nonzero(tracker.belief > 1e-14)))

    # Với map mở, vùng có xác suất dương phải nở dần sau mỗi lần predict.
    assert support_sizes[0] >= 5, support_sizes
    assert all(b > a for a, b in zip(support_sizes, support_sizes[1:])), support_sizes


def test_zero_mass_resets_to_unseen():
    tracker = EnemyTracker()
    enemy_pos = (5, 5)
    initial_obs = make_observation((21, 21), (5, 4), radius=2)
    tracker.update(initial_obs, (5, 4), enemy_pos, step=0)

    # Cho vùng nhìn đủ phủ toàn bộ support sau 1 predict, khiến update triệt tiêu
    # toàn bộ khối lượng. Tracker phải reset đều trên các ô unseen.
    wide_obs = make_observation((21, 21), (5, 5), radius=6)
    tracker.update(wide_obs, (5, 5), None, step=1)

    assert_distribution(tracker, wide_obs)
    assert np.allclose(tracker.belief[wide_obs != -1], 0.0)
    assert tracker.get_target((5, 5)) is not None


def test_bad_input_never_raises():
    tracker = EnemyTracker()
    # Không được văng exception dù input lỗi.
    tracker.update(None, (0, 0), None, step=0)
    assert tracker.get_target((0, 0)) is None

    obs = make_observation((21, 21), (2, 2), radius=2)
    tracker.update(obs, (2, 2), (3, 3), step=1)
    old = tracker.belief.copy()
    tracker.update(obs, (2, 2), (999, 999), step=2)
    assert np.allclose(tracker.belief, old)


def benchmark_update():
    tracker = EnemyTracker()
    my_pos = (2, 2)
    obs = make_observation((21, 21), my_pos, radius=2)
    tracker.update(obs, my_pos, None, step=0)

    repetitions = 5000
    start = perf_counter()
    for step in range(1, repetitions + 1):
        tracker.update(obs, my_pos, None, step=step)
    elapsed_ms = (perf_counter() - start) * 1000.0 / repetitions

    assert_distribution(tracker, obs)
    assert elapsed_ms < 50.0, f"update quá chậm: {elapsed_ms:.3f} ms"
    return elapsed_ms


def main():
    test_seen_enemy_is_exact()
    print("[OK] Thấy địch -> target chính xác")

    test_lost_enemy_spreads()
    print("[OK] Mất dấu -> vùng xác suất lan rộng")

    test_zero_mass_resets_to_unseen()
    print("[OK] Tổng về 0 -> reset đều trên ô unseen")

    test_bad_input_never_raises()
    print("[OK] Input lỗi không làm văng exception")

    elapsed_ms = benchmark_update()
    print(f"[OK] Tổng xác suất = 1, không NaN; {elapsed_ms:.4f} ms/update")


if __name__ == "__main__":
    main()
