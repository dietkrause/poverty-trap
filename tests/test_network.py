"""Network: connectedness in [0,1], NetworkDrift, and peer spillover direction."""

from __future__ import annotations

import numpy as np

from simulation.population.network import NetworkDrift, PeerInfluence, SocialNetwork


def test_connectedness_in_unit_interval(state, ctx) -> None:
    SocialNetwork().step(state, ctx)
    assert np.all((state.connectedness >= 0.0) & (state.connectedness <= 1.0))
    assert state.peer_mean_wealth is not None


def test_network_drift_scales_with_connectedness(state, ctx) -> None:
    state.connectedness[:] = 1.0
    d = NetworkDrift().drift(state, ctx)
    assert np.allclose(d, ctx.params.beta_network)


def test_peer_pull_sign(state, ctx) -> None:
    state.wealth[:] = 0.3
    state.peer_mean_wealth = np.where(np.arange(state.n) < state.n // 2, 0.9, 0.0)
    d = PeerInfluence().drift(state, ctx)
    assert d[0] > 0 and d[-1] < 0
