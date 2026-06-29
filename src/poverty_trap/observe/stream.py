"""Snapshot emitter: a read-only Observer that publishes the state for a viewer.

This keeps visualization fully decoupled from the engine: the emitter takes a
plain callback and pushes a compact, JSON-serialisable snapshot every ``every``
ticks. The UX server passes a callback that forwards to a WebSocket; nothing in
the engine knows about the web. Agents are subsampled so the payload stays small.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from ..core.bands import band_shares, classify
from ..core.context import SimContext
from ..core.state import AgentState
from .metrics import gini


class SnapshotEmitter:
    """Calls ``sink(snapshot)`` every ``every`` ticks with a compact view."""

    def __init__(self, sink: Callable[[dict], None], every: int = 20, max_agents: int = 300) -> None:
        self.sink = sink
        self.every = max(int(every), 1)
        self.max_agents = max_agents

    def observe(self, state: AgentState, ctx: SimContext) -> None:
        if ctx.tick % self.every != 0:
            return
        n = state.n
        step = max(1, n // self.max_agents)
        idx = np.arange(0, n, step)
        bands = classify(state.wealth[idx], ctx.params)
        snap = {
            "tick": ctx.tick,
            "agents": {
                "wealth": np.round(state.wealth[idx], 4).tolist(),
                "zone": state.zone[idx].tolist(),
                "band": bands.tolist(),
                "talent": np.round(state.talent[idx], 3).tolist(),
            },
            "gini": round(gini(state.wealth), 4),
            "bands": {k: round(v, 4) for k, v in band_shares(state.wealth, ctx.params).items()},
            "poverty_line": ctx.params.poverty_line,
            "rich_threshold": ctx.params.rich_threshold,
        }
        self.sink(snap)
