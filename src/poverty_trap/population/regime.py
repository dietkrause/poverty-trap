"""Regime policies: the active parts of a country/policy configuration (section 7.9).

Most of a regime is just parameter values (premium scale, opportunity rate,
inequality, base drifts), which live in :class:`~poverty_trap.core.config.ModelParams`.
The two *behavioural* levers - a welfare floor that catches falling agents and a
redistribution transfer - are applied here as a population process so they run
each tick on the settled wealth.
"""

from __future__ import annotations

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState


class RegimePolicy:
    """Applies the welfare floor and redistribution defined by the parameters.

    * **Welfare floor** (``params.welfare_floor``): a reflecting barrier - no
      agent can fall below it. With a floor, ruin is no longer absorbing; the
      safety net catches people before collapse.
    * **Redistribution** (``params.redistribution``): a per-period tax on wealth
      above the rich threshold, paid out as an equal lift to below-line agents.
    """

    name = "regime_policy"

    def step(self, state: AgentState, ctx: SimContext) -> None:
        p = ctx.params

        if p.welfare_floor is not None:
            np.maximum(state.wealth, p.welfare_floor, out=state.wealth)

        if p.redistribution > 0.0:
            rich = state.wealth > p.rich_threshold
            pot = float(np.sum((state.wealth[rich] - p.rich_threshold) * p.redistribution))
            if pot > 0.0:
                state.wealth[rich] -= (state.wealth[rich] - p.rich_threshold) * p.redistribution
                recipients = state.wealth < p.poverty_line
                k = int(np.count_nonzero(recipients))
                if k > 0:
                    state.wealth[recipients] += pot / k
