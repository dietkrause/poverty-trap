"""Capital returns: wealth-dependent r(w), and gating by savings and positivity."""

from __future__ import annotations

import numpy as np

from poverty_trap.dynamics.capital_returns import CapitalReturns


def test_returns_rise_with_wealth(state, ctx) -> None:
    state.skill[:] = 0.95          # high skill -> positive savings share
    state.wealth[:] = 0.2
    low = CapitalReturns().drift(state, ctx).mean()
    state.wealth[:] = 0.9
    high = CapitalReturns().drift(state, ctx).mean()
    assert high > low > 0


def test_no_returns_on_nonpositive_wealth(state, ctx) -> None:
    state.wealth[:] = -0.5
    assert np.all(CapitalReturns().drift(state, ctx) == 0.0)


def test_poor_low_skill_save_little(state, ctx) -> None:
    state.skill[:] = 0.05
    state.wealth[:] = 0.05         # below subsistence -> s = 0
    assert np.allclose(CapitalReturns().drift(state, ctx), 0.0)
