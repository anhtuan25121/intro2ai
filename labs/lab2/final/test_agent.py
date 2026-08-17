"""Smoke tests for Lab 2 final agents.

Run from repository root:
    python labs/lab2/final/test_agent.py
"""

import importlib.util
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "labs" / "lab1" / "HideSeek" / "pacman" / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

from environment import Environment, Move

spec = importlib.util.spec_from_file_location("lab2_final_agent", HERE / "agent.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PacmanAgent = module.PacmanAgent
GhostAgent = module.GhostAgent


def assert_pacman_action(action, speed=2):
    if isinstance(action, Move):
        return
    assert isinstance(action, tuple) and len(action) == 2, action
    move, steps = action
    assert isinstance(move, Move), action
    assert 1 <= int(steps) <= speed, action


def main():
    env = Environment(
        max_steps=200,
        deterministic_starts=True,
        capture_distance_threshold=2,
        pacman_speed=2,
    )
    p = PacmanAgent(pacman_speed=2)
    g = GhostAgent()

    max_p_ms = 0.0
    max_g_ms = 0.0

    # Exercise both visible and blind observations without depending on an opponent.
    for step in range(25):
        p_obs, p_pos, p_enemy = env.get_observation("pacman", 5, 5)
        g_obs, g_pos, g_enemy = env.get_observation("ghost", 5, 5)

        t0 = time.perf_counter()
        pa = p.step(p_obs, p_pos, p_enemy, step)
        max_p_ms = max(max_p_ms, (time.perf_counter() - t0) * 1000)
        assert_pacman_action(pa, 2)

        t0 = time.perf_counter()
        ga = g.step(g_obs, g_pos, g_enemy, step)
        max_g_ms = max(max_g_ms, (time.perf_counter() - t0) * 1000)
        assert isinstance(ga, Move), ga

        done, _, _ = env.step(pa, ga)
        if done:
            break

    assert max_p_ms < 1000.0, max_p_ms
    assert max_g_ms < 1000.0, max_g_ms
    print(f"[OK] Pacman action hợp lệ; max {max_p_ms:.2f} ms/step")
    print(f"[OK] Ghost action hợp lệ; max {max_g_ms:.2f} ms/step")


if __name__ == "__main__":
    main()
