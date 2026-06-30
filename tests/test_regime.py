"""Regime: welfare floor reflects, redistribution moves wealth down the ladder."""

from __future__ import annotations

import numpy as np

from simulation.core.config import ModelParams
from simulation.core.context import SimContext
from simulation.core.state import AgentState
from simulation.population.regime import RegimePolicy


def test_welfare_floor_clamps() -> None:
    p = ModelParams(welfare_floor=0.05)
    s = AgentState.initialize(p, np.random.default_rng(0))
    s.wealth[:] = -1.0
    RegimePolicy().step(s, SimContext(params=p, rng=np.random.default_rng(0)))
    assert np.all(s.wealth >= 0.05)


def test_redistribution_taxes_rich_lifts_poor() -> None:
    p = ModelParams(n_agents=4, redistribution=0.5)
    s = AgentState.initialize(p, np.random.default_rng(0))
    s.wealth[:] = np.array([0.05, 0.05, 3.0, 3.0])
    RegimePolicy().step(s, SimContext(params=p, rng=np.random.default_rng(0)))
    assert s.wealth[2] < 3.0 and s.wealth[3] < 3.0   # rich taxed
    assert s.wealth[0] > 0.05 and s.wealth[1] > 0.05  # poor lifted
