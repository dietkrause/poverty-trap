"""Social network and economic connectedness (section 7.6).

Agents sit on a graph generated with homophily (similar agents connect), so
segregation emerges rather than being imposed. An agent's *connectedness* is the
share of its ties that sit above the poverty line - Chetty's "economic
connectedness", which empirically predicts mobility. Connectedness feeds two
channels: a small direct drift (this module's :class:`NetworkDrift`) and a higher
opportunity-arrival rate (handled in the opportunity process).
"""

from __future__ import annotations

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState


class SocialNetwork:
    """Builds a homophilous graph and keeps each agent's connectedness current.

    The adjacency is a row-normalised weight matrix ``W`` (``n x n``); a single
    matrix-vector product turns "who is above the line" into each agent's
    connectedness, so the per-tick update stays vectorised. The graph is rebuilt
    every ``rewire_every`` ticks to reflect shifting neighbourhoods.
    """

    name = "network"

    def __init__(self, rewire_every: int = 200) -> None:
        self.rewire_every = max(int(rewire_every), 1)
        self._w: np.ndarray | None = None  # row-normalised adjacency

    def _build(self, state: AgentState, ctx: SimContext) -> None:
        p = ctx.params
        n = state.n
        rng = ctx.rng
        # Connection propensity: homophily by zone. Higher when zones match.
        same_zone = state.zone[:, None] == state.zone[None, :]
        base = np.where(same_zone, p.homophily, 1.0 - p.homophily)
        np.fill_diagonal(base, 0.0)
        # Keep roughly `network_degree` ties per node by thresholding random draws.
        prob = base / base.sum(axis=1, keepdims=True) * p.network_degree
        adj = (rng.random((n, n)) < np.clip(prob, 0.0, 1.0)).astype(np.float64)
        adj = np.maximum(adj, adj.T)  # symmetric
        np.fill_diagonal(adj, 0.0)
        degree = adj.sum(axis=1, keepdims=True)
        degree[degree == 0.0] = 1.0
        self._w = adj / degree

    def step(self, state: AgentState, ctx: SimContext) -> None:
        if self._w is None or ctx.tick % self.rewire_every == 0:
            self._build(state, ctx)
        assert self._w is not None
        above = (state.wealth > ctx.params.poverty_line).astype(np.float64)
        state.connectedness = self._w @ above


class NetworkDrift:
    """Drift term ``beta_network * c`` - the lift from social capital."""

    name = "network_drift"

    def drift(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        return ctx.params.beta_network * state.connectedness
