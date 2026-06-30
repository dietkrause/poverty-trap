"""Opportunity: jumps are non-negative and gated by skill + slack."""

from __future__ import annotations

import numpy as np

from simulation.core.config import ModelParams
from simulation.core.context import SimContext
from simulation.core.state import AgentState
from simulation.events.opportunity import OpportunityProcess


def _setup(**over):
    p = ModelParams(n_agents=4000, **over)
    s = AgentState.initialize(p, np.random.default_rng(0))
    s.effort[:] = 1.0
    return s, SimContext(params=p, rng=np.random.default_rng(0))


def test_only_nonnegative_jumps() -> None:
    s, ctx = _setup()
    before = s.wealth.copy()
    OpportunityProcess().apply(s, ctx)
    assert np.all(s.wealth >= before - 1e-12)


def test_no_capture_without_skill() -> None:
    s, ctx = _setup(lambda0=5.0)
    s.skill[:] = 0.0          # cannot meet skill gate
    before = s.wealth.copy()
    OpportunityProcess().apply(s, ctx)
    assert np.allclose(s.wealth, before)


def test_no_capture_without_slack() -> None:
    s, ctx = _setup(lambda0=5.0)
    s.effort[:] = 0.0         # slack e*eta below gate
    before = s.wealth.copy()
    OpportunityProcess().apply(s, ctx)
    assert np.allclose(s.wealth, before)
