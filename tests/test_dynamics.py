"""Unit tests for individual drift/noise/efficiency components."""

from __future__ import annotations

import numpy as np

from poverty_trap.core.config import ModelParams
from poverty_trap.core.context import SimContext
from poverty_trap.core.state import AgentState
from poverty_trap.dynamics.neighborhood import NeighborhoodDrift
from poverty_trap.dynamics.poverty_premium import PovertyPremium
from poverty_trap.dynamics.value_creation import (
    ValueCreation,
    effort_efficiency,
    effort_quality,
)
from poverty_trap.observe.metrics import gini


def _ctx(params: ModelParams) -> tuple[AgentState, SimContext]:
    rng = np.random.default_rng(0)
    return AgentState.initialize(params, rng), SimContext(params=params, rng=rng)


def test_neighborhood_drift_sign() -> None:
    p = ModelParams()
    state, ctx = _ctx(p)
    mu = NeighborhoodDrift().drift(state, ctx)
    assert np.all(mu[state.zone == 0] == p.mu_base_poor)
    assert np.all(mu[state.zone == 1] == p.mu_base_rich)


def test_poverty_premium_only_below_line() -> None:
    p = ModelParams()
    state, ctx = _ctx(p)
    state.wealth[:] = np.linspace(0.0, p.rich_threshold, state.n)
    pen = PovertyPremium().drift(state, ctx)
    below = state.wealth < p.poverty_line
    assert np.all(pen[below] == -p.premium)
    assert np.all(pen[~below] == 0.0)


def test_efficiency_rises_with_wealth() -> None:
    p = ModelParams()
    state, ctx = _ctx(p)
    state.stressors[:] = 0.0
    state.wealth[:] = 0.0
    low = effort_efficiency(state, p)
    state.wealth[:] = 1.0
    high = effort_efficiency(state, p)
    assert np.all(high > low)
    assert np.all((low >= p.eta_min) & (high <= 1.0))


def test_quality_in_range_and_monotone() -> None:
    p = ModelParams()
    state, ctx = _ctx(p)
    state.skill[:] = 0.0
    q_low = effort_quality(state, p)
    state.skill[:] = 1.0
    q_high = effort_quality(state, p)
    assert np.all((q_low >= p.q_min - 1e-9) & (q_high <= 1.0 + 1e-9))
    assert np.all(q_high > q_low)


def test_value_creation_zero_without_effort() -> None:
    p = ModelParams()
    state, ctx = _ctx(p)
    state.effort[:] = 0.0
    assert np.allclose(ValueCreation().drift(state, ctx), 0.0)


def test_gini_bounds() -> None:
    assert gini(np.ones(100)) == 0.0
    spike = np.zeros(100)
    spike[0] = 100.0
    assert gini(spike) > 0.9
