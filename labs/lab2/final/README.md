# Lab 2 Final — Blind Adversary

## Files to submit
Only `agent.py` and `belief.py` are required by this solution. Put both in the same `group_id/` directory before zipping.

## Main ideas
- **EnemyTracker** keeps a probability distribution over enemy locations.
- **Pacman / Seek** uses systematic first-sighting exploration, belief pursuit when the Ghost is hidden, and a small adversarial interception search when the Ghost is visible.
- **Ghost / Hide** models Pacman as a speed-2 opponent, moves between junctions while hidden to avoid corridor oscillation, and uses risk-aware adversarial evasion when Pacman is visible.
- Walls are treated as static structure (`map_state == 1`); fog cells are traversable in the provided grading framework because walls remain visible.

## Local tests
From the repository root:

```bash
python labs/lab2/final/test_belief.py
python labs/lab2/final/test_agent.py
```

For Arena testing, copy `agent.py` and `belief.py` into a folder under `labs/lab1/HideSeek/pacman/submissions/`, then run with both observation radii enabled.
