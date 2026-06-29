"""AgentState: initialisation shapes, masks, and scratch fields."""

from __future__ import annotations

import numpy as np

from poverty_trap.core.state import AgentState


def test_initialize_shapes(params, rng) -> None:
    s = AgentState.initialize(params, rng)
    n = params.n_agents
    for arr in (s.wealth, s.talent, s.skill, s.effort, s.stressors,
                s.connectedness, s.zone, s.generation, s.peer_mean_wealth):
        assert arr.shape == (n,)
    assert set(np.unique(s.zone)).issubset({0, 1})
    assert np.all((s.skill >= 0.05) & (s.skill <= 0.95))


def test_poor_and_below_line_masks(params, rng) -> None:
    s = AgentState.initialize(params, rng)
    assert s.poor_mask().dtype == bool
    s.wealth[:] = 0.05
    assert np.all(s.below_line(params))
    s.wealth[:] = 0.9
    assert not np.any(s.below_line(params))


def test_peer_mean_initialised_to_wealth(params, rng) -> None:
    s = AgentState.initialize(params, rng)
    assert np.allclose(s.peer_mean_wealth, s.wealth)
