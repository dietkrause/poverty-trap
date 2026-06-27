"""Determinism: a fixed seed must fully determine a run."""

from __future__ import annotations

import numpy as np

from poverty_trap.builder import build_simulation


def test_same_seed_identical() -> None:
    a = build_simulation(seed=7, effort=0.5).run(500)
    b = build_simulation(seed=7, effort=0.5).run(500)
    np.testing.assert_array_equal(a.final_state.wealth, b.final_state.wealth)


def test_different_seed_differs() -> None:
    a = build_simulation(seed=1, effort=0.5).run(500)
    b = build_simulation(seed=2, effort=0.5).run(500)
    assert not np.array_equal(a.final_state.wealth, b.final_state.wealth)
