"""Diffusion: mean-zero shocks, sqrt(dt) and zone scaling, RNG-driven."""

from __future__ import annotations

import numpy as np

from poverty_trap.core.config import ModelParams
from poverty_trap.core.context import SimContext
from poverty_trap.core.state import AgentState
from poverty_trap.dynamics.diffusion import DiffusionShocks


def test_increment_mean_near_zero_std_matches_sigma() -> None:
    p = ModelParams(n_agents=20000)
    s = AgentState.initialize(p, np.random.default_rng(1))
    s.zone[:] = 0  # all poor
    ctx = SimContext(params=p, rng=np.random.default_rng(1))
    inc = DiffusionShocks().increment(s, ctx)
    assert abs(inc.mean()) < 0.01
    assert abs(inc.std() - p.sigma_poor * np.sqrt(p.dt)) < 0.005


def test_poor_more_volatile_than_rich() -> None:
    p = ModelParams(n_agents=20000)
    s = AgentState.initialize(p, np.random.default_rng(2))
    ctx = SimContext(params=p, rng=np.random.default_rng(2))
    inc = DiffusionShocks().increment(s, ctx)
    assert inc[s.zone == 0].std() > inc[s.zone == 1].std()
