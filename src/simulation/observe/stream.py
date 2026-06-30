"""Snapshot emitter: a read-only Observer that publishes the state for a viewer.

This keeps visualization fully decoupled from the engine: the emitter takes a
plain callback and pushes a compact, JSON-serialisable snapshot every ``every``
ticks. The UX server passes a callback that forwards to a WebSocket; nothing in
the engine knows about the web.

The snapshot is rich enough to drive a full dashboard of the model's dynamics:

* per-agent arrays (subsampled): wealth, zone, band, talent, skill, effort, the
  effort efficiency ``eta`` (scarcity tax), quality ``q``, savings share ``s``,
  connectedness and generation - so the UI can encode size/opacity/scatter;
* per-zone aggregates (poor vs rich): mean wealth, mean ``eta``/``q``/``s``,
  connectedness, and the share above the poverty / rich lines;
* the live continuum (band shares) and inequality (Gini);
* running tallies of discrete events read from ``ctx.bus`` every tick
  (cumulative since this emitter was attached): opportunities arrived/captured
  (+ a reservoir of payoff sizes for the power-law histogram) and successful
  pooling events.

Reading ``ctx.bus`` happens every tick (events are transient); the heavy
snapshot is only built and emitted every ``every`` ticks.
"""

from __future__ import annotations

from collections import deque
from typing import Callable

import numpy as np

from ..core.bands import band_shares, classify
from ..core.context import SimContext
from ..core.state import AgentState
from ..dynamics.value_creation import effort_efficiency, effort_quality, savings_share
from .metrics import gini


class SnapshotEmitter:
    """Calls ``sink(snapshot)`` every ``every`` ticks with a compact, rich view."""

    def __init__(self, sink: Callable[[dict], None], every: int = 15,
                 max_agents: int = 240, payoff_reservoir: int = 160) -> None:
        self.sink = sink
        self.every = max(int(every), 1)
        self.max_agents = max_agents
        # Cross-tick accumulators for discrete events (the bus is cleared each tick).
        self._opp_arrived = 0
        self._opp_captured = 0
        self._opp_value = 0.0
        self._pool_events = 0
        self._payoffs: deque[float] = deque(maxlen=payoff_reservoir)

    # --- per-tick: harvest transient events from the bus --------------------
    def _drain_bus(self, ctx: SimContext) -> None:
        opp = ctx.bus.get("opportunity")
        if opp:
            self._opp_arrived += int(opp.get("arrived", 0))
            self._opp_captured += int(opp.get("captured", 0))
            self._opp_value += float(opp.get("captured_value", 0.0))
            for x in opp.get("payoff_samples", ()):  # heavy-tail reservoir
                self._payoffs.append(float(x))
        pool = ctx.bus.get("pooling")
        if pool:
            self._pool_events += int(pool.get("events", 0))

    def observe(self, state: AgentState, ctx: SimContext) -> None:
        self._drain_bus(ctx)
        if ctx.tick % self.every != 0:
            return

        p = ctx.params
        n = state.n
        # Whole-population (cheap, vectorised) derived quantities.
        eta = effort_efficiency(state, p)
        q = effort_quality(state, p)
        s = savings_share(state, p)
        poor = state.zone == 0
        rich = ~poor

        def zone_stats(mask: np.ndarray) -> dict:
            if not np.any(mask):
                return {"count": 0, "wealth": 0.0, "eta": 0.0, "q": 0.0,
                        "savings": 0.0, "conn": 0.0, "above_line": 0.0, "above_rich": 0.0}
            w = state.wealth[mask]
            return {
                "count": int(mask.sum()),
                "wealth": round(float(w.mean()), 4),
                "eta": round(float(eta[mask].mean()), 4),
                "q": round(float(q[mask].mean()), 4),
                "savings": round(float(s[mask].mean()), 4),
                "conn": round(float(state.connectedness[mask].mean()), 4),
                "above_line": round(float(np.mean(w >= p.poverty_line)), 4),
                "above_rich": round(float(np.mean(w >= p.rich_threshold)), 4),
            }

        # Subsample agents for the field / scatter (keeps the payload small).
        step = max(1, n // self.max_agents)
        idx = np.arange(0, n, step)
        bands = classify(state.wealth[idx], p)

        snap = {
            "tick": ctx.tick,
            "cutoffs": {
                "poverty_line": p.poverty_line,
                "band_vulnerable": p.band_vulnerable,
                "band_acomodado": p.band_acomodado,
                "rich_threshold": p.rich_threshold,
            },
            "gini": round(gini(state.wealth), 4),
            "bands": {k: round(v, 4) for k, v in band_shares(state.wealth, p).items()},
            "agents": {
                "wealth": np.round(state.wealth[idx], 4).tolist(),
                "zone": state.zone[idx].tolist(),
                "band": bands.tolist(),
                "talent": np.round(state.talent[idx], 3).tolist(),
                "skill": np.round(state.skill[idx], 3).tolist(),
                "effort": np.round(state.effort[idx], 3).tolist(),
                "eta": np.round(eta[idx], 3).tolist(),
                "q": np.round(q[idx], 3).tolist(),
                "savings": np.round(s[idx], 3).tolist(),
                "conn": np.round(state.connectedness[idx], 3).tolist(),
                "generation": state.generation[idx].tolist(),
            },
            "zones": {"poor": zone_stats(poor), "rich": zone_stats(rich)},
            "opportunity": {
                "arrived": self._opp_arrived,
                "captured": self._opp_captured,
                "captured_value": round(self._opp_value, 3),
                "payoffs": [round(x, 4) for x in self._payoffs],
            },
            "pooling": {"events": self._pool_events},
        }
        self.sink(snap)
