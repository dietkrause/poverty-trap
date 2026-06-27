"""Opportunity as a marked Poisson process (section 7.5).

An opportunity is a discrete event, not a smooth drift, decomposed into three
independent questions:

* **Arrival** - opportunities knock at a Poisson rate that rises with the zone's
  opportunity density and the agent's connectedness (preferential attachment).
* **Size** - the payoff is heavy-tailed (Pareto): a few are life-changing, most
  are tiny.
* **Capture** - the payoff is realised only if the agent has the skill and the
  slack to act on it.

This single object cleanly separates *access* (the rate), *luck* (which payoff is
drawn), and *merit* (whether it can be seized).
"""

from __future__ import annotations

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState
from ..dynamics.value_creation import effort_efficiency


class OpportunityProcess:
    """Discrete opportunity arrivals with Pareto payoffs and a capture gate."""

    name = "opportunity"

    def apply(self, state: AgentState, ctx: SimContext) -> None:
        p = ctx.params
        rng = ctx.rng

        # --- Arrival: Bernoulli approximation of a Poisson over this step. ---
        # Zone opportunity density: rich zone is denser. Connectedness adds more.
        omega = np.where(state.zone == 0, 0.0, 1.0)
        rate = p.lambda0 * np.exp(p.g_zone * omega + p.g_conn * state.connectedness)
        arrives = rng.random(state.n) < (rate * p.dt)
        if not np.any(arrives):
            return

        idx = np.flatnonzero(arrives)

        # --- Size: Pareto(x_min, a) payoffs (heavy tail). -------------------
        # numpy's pareto returns Lomax (Pareto - 1); shift and scale to x_min.
        payoff = p.x_min * (1.0 + rng.pareto(p.pareto_a, size=idx.size))

        # --- Capture: need skill >= gate(payoff) and slack (e*eta) >= gate. -
        eta = effort_efficiency(state, p)
        slack = state.effort[idx] * eta[idx]
        skill_needed = p.skill_gate * payoff  # bigger opportunities demand more skill
        captured = (state.skill[idx] >= skill_needed) & (slack >= p.slack_gate)

        gain = p.kappa * payoff * captured
        state.wealth[idx] += gain

        # Publish a summary for observers (counts + captured share this tick).
        ctx.bus["opportunity"] = {
            "arrived": int(idx.size),
            "captured": int(np.count_nonzero(captured)),
            "captured_value": float(np.sum(gain)),
        }
