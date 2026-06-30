"""Collective pooling: people combining resources to cross the threshold (spec 7.6).

Real escape is often not solitary - cooperatives, savings groups, and family
support let several below-line households pool resources so that one of them
crosses the Micawber threshold. This is the cooperative counterpart to the
poverty premium: where the premium drags individuals down, pooling lets a group
push one member up. Implemented as a population process so it acts on settled
wealth, vectorised over randomly formed groups.
"""

from __future__ import annotations

import numpy as np

from ..core.bands import effective_poverty_line
from ..core.context import SimContext
from ..core.state import AgentState


class CollectivePooling:
    """Below-line agents occasionally pool to send one member across the line.

    Each tick, with probability ``pool_rate``, eligible below-line agents are
    grouped (size ``pool_size``); a group whose combined wealth reaches the
    poverty line lifts its wealthiest member just across it, funded equally by
    the others (savings groups / cooperatives helping one member escape poverty).
    Conserves total wealth; disabled when ``pool_rate`` is 0.
    """

    name = "pooling"

    def step(self, state: AgentState, ctx: SimContext) -> None:
        p, rng = ctx.params, ctx.rng
        if p.pool_rate <= 0.0 or p.pool_size < 2:
            return
        line = effective_poverty_line(state.wealth, p)
        eligible = np.flatnonzero((state.wealth < line) & (rng.random(state.n) < p.pool_rate))
        if eligible.size < p.pool_size:
            return
        rng.shuffle(eligible)
        events = 0
        for g in range(0, eligible.size - p.pool_size + 1, p.pool_size):
            grp = eligible[g:g + p.pool_size]
            total = float(np.sum(state.wealth[grp]))
            if total >= line:
                winner = grp[int(np.argmax(state.wealth[grp]))]
                contributors = grp[grp != winner]
                # Send the winner just across the line; split the rest among the others.
                state.wealth[winner] = line
                state.wealth[contributors] = (total - line) / contributors.size
                events += 1
        if events:
            # Publish for observers (so the UI can flash collective-escape events).
            ctx.bus["pooling"] = {"events": events}
