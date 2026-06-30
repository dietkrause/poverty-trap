"""Pooling: conserves total wealth and can push one member over the threshold."""

from __future__ import annotations

import numpy as np

from simulation.core.config import ModelParams
from simulation.core.context import SimContext
from simulation.core.state import AgentState
from simulation.population.pooling import CollectivePooling


def test_disabled_when_rate_zero() -> None:
    p = ModelParams(pool_rate=0.0)
    s = AgentState.initialize(p, np.random.default_rng(0))
    before = s.wealth.copy()
    CollectivePooling().step(s, SimContext(params=p, rng=np.random.default_rng(0)))
    assert np.array_equal(s.wealth, before)


def test_conserves_total_wealth_and_lifts_one() -> None:
    p = ModelParams(n_agents=60, pool_rate=1.0, pool_size=6)
    s = AgentState.initialize(p, np.random.default_rng(0))
    s.wealth[:] = 0.19  # below line; six of them sum past w*=1.0
    total = s.wealth.sum()
    CollectivePooling().step(s, SimContext(params=p, rng=np.random.default_rng(0)))
    assert abs(s.wealth.sum() - total) < 1e-9          # conserved
    assert s.wealth.max() >= p.rich_threshold          # someone crossed
