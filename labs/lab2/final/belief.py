"""Probabilistic enemy tracker for the Blind Adversary lab.

The public interface is intentionally tiny because ``agent.py`` only relies on:
    EnemyTracker()
    update(map_state, my_pos, enemy_pos, step)
    get_target(my_pos)

``max_enemy_speed`` is a configurable attribute (default 1).  GhostAgent sets
it to 2 because the opponent Pacman may move one or two cells in a straight
line per arena step.  Method signatures remain unchanged.
"""

import numpy as np


class EnemyTracker:
    def __init__(self):
        self.belief = None
        self.last_seen = None
        self.last_seen_step = None
        self.max_enemy_speed = 1

        self._shape = None
        self._wall_mask = None
        self._open_flat = None
        self._transition = None
        self._transition_speed = None

    @staticmethod
    def _as_map_array(map_state):
        arr = np.asarray(map_state)
        if arr.ndim != 2 or arr.size == 0:
            raise ValueError("map_state must be a non-empty 2D array")
        return arr

    def _needs_transition_rebuild(self, map_array):
        wall_mask = np.asarray(map_array == 1, dtype=bool)
        return (
            self._transition is None
            or self._shape != map_array.shape
            or self._transition_speed != max(1, int(self.max_enemy_speed))
            or self._wall_mask is None
            or not np.array_equal(self._wall_mask, wall_mask)
        )

    def _build_transition(self, map_array):
        """Build a small transition matrix over walkable cells.

        From one source cell the enemy may stay, or move 1..speed cells in one
        cardinal direction.  For speed 2 this intentionally excludes an L turn
        inside the same arena step, matching the Pacman movement rule.
        """
        walkable = map_array != 1
        open_flat = np.flatnonzero(walkable.ravel())
        h, w = map_array.shape
        n = int(open_flat.size)
        speed = max(1, int(self.max_enemy_speed))

        index_of_flat = {int(flat): i for i, flat in enumerate(open_flat)}
        transition = np.zeros((n, n), dtype=np.float64)

        for i, flat in enumerate(open_flat):
            r, c = divmod(int(flat), w)
            destinations = [(r, c)]  # STAY is legal for both agents.

            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cr, cc = r, c
                for _ in range(speed):
                    nr, nc = cr + dr, cc + dc
                    if not (0 <= nr < h and 0 <= nc < w):
                        break
                    if not walkable[nr, nc]:
                        break
                    destinations.append((nr, nc))
                    cr, cc = nr, nc

            probability = 1.0 / len(destinations)
            for dr, dc in destinations:
                dst_flat = dr * w + dc
                j = index_of_flat[dst_flat]
                transition[i, j] += probability

        self._shape = map_array.shape
        self._wall_mask = np.asarray(map_array == 1, dtype=bool).copy()
        self._open_flat = open_flat
        self._transition = transition
        self._transition_speed = speed

    def _ensure_model(self, map_array):
        if self._needs_transition_rebuild(map_array):
            self._build_transition(map_array)

    def _set_uniform(self, map_array, unseen_only=False):
        walkable = map_array != 1
        mask = walkable.copy()
        if unseen_only:
            unseen = map_array == -1
            if np.any(unseen & walkable):
                mask = unseen & walkable

        count = int(np.count_nonzero(mask))
        belief = np.zeros(map_array.shape, dtype=np.float64)
        if count > 0:
            belief[mask] = 1.0 / count
        self.belief = belief

    def _ensure_initialized(self, map_array):
        self._ensure_model(map_array)
        if self.belief is None or self.belief.shape != map_array.shape:
            self._set_uniform(map_array, unseen_only=False)

    def _predict(self, map_array):
        self._ensure_model(map_array)
        if self.belief is None:
            self._set_uniform(map_array, unseen_only=False)
            return

        clean = np.nan_to_num(
            np.asarray(self.belief, dtype=np.float64),
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )
        clean[map_array == 1] = 0.0
        clean[clean < 0.0] = 0.0

        source_prob = clean.ravel()[self._open_flat]
        predicted_open = source_prob @ self._transition
        predicted = np.zeros(map_array.size, dtype=np.float64)
        predicted[self._open_flat] = predicted_open
        self.belief = predicted.reshape(map_array.shape)

    def _normalize_or_reset(self, map_array):
        walkable = map_array != 1
        belief = np.nan_to_num(
            np.asarray(self.belief, dtype=np.float64),
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )
        belief[~walkable] = 0.0
        belief[belief < 0.0] = 0.0
        total = float(belief.sum())

        if np.isfinite(total) and total > 1e-15:
            belief /= total
            self.belief = belief
        else:
            # Observation contradicted all predicted states.  Prefer unseen
            # walkable cells; if there are none, fall back to every walkable cell.
            self._set_uniform(map_array, unseen_only=True)

    def update(self, map_state, my_pos, enemy_pos, step):
        """Predict one arena step, then condition on the new observation.

        The method is exception-safe by design: malformed input never propagates
        an exception to the arena.  A valid previous belief is restored on error.
        """
        old_belief = None if self.belief is None else self.belief.copy()
        old_last_seen = self.last_seen
        old_last_seen_step = self.last_seen_step

        try:
            map_array = self._as_map_array(map_state)
            self._ensure_initialized(map_array)
            self._predict(map_array)

            if enemy_pos is not None:
                row = int(enemy_pos[0])
                col = int(enemy_pos[1])
                h, w = map_array.shape
                if not (0 <= row < h and 0 <= col < w):
                    raise ValueError("enemy_pos outside map")
                if map_array[row, col] == 1:
                    raise ValueError("enemy_pos cannot be a wall")

                self.belief.fill(0.0)
                self.belief[row, col] = 1.0
                self.last_seen = (row, col)
                self.last_seen_step = int(step)
                return

            # Empty cells in the current cross-shaped observation are known not
            # to contain the enemy.  Walls already carry zero probability.
            self.belief[map_array == 0] = 0.0
            self._normalize_or_reset(map_array)

        except Exception:
            self.belief = old_belief
            self.last_seen = old_last_seen
            self.last_seen_step = old_last_seen_step

    def get_target(self, my_pos):
        """Return the MAP estimate; ties prefer the candidate nearest to me."""
        try:
            if self.belief is None or self.belief.size == 0:
                return None

            belief = np.nan_to_num(
                np.asarray(self.belief, dtype=np.float64),
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )
            max_prob = float(np.max(belief))
            if not np.isfinite(max_prob) or max_prob <= 0.0:
                return None

            candidates = np.argwhere(
                np.isclose(belief, max_prob, rtol=1e-12, atol=1e-15)
            )
            if candidates.size == 0:
                return None

            try:
                mr, mc = int(my_pos[0]), int(my_pos[1])
            except Exception:
                mr, mc = 0, 0

            best = min(
                candidates,
                key=lambda rc: (
                    abs(int(rc[0]) - mr) + abs(int(rc[1]) - mc),
                    int(rc[0]),
                    int(rc[1]),
                ),
            )
            return int(best[0]), int(best[1])
        except Exception:
            return self.last_seen
