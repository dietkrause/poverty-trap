"""Capital returns: the compounding engine (section 7.4).

Returns on already-owned capital, ``r * w * s``, are the quiet driver of
divergence. The poor have a savings share ``s ~ 0`` (no surplus to invest), so
this term is near-zero for them and grows multiplicatively for the wealthy: the
same effort buys a permanently steeper climb once you have a base. This is the
multiplicative ingredient that bends the wealth distribution into a heavy tail.
"""

from __future__ import annotations

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState
from .value_creation import savings_share


class CapitalReturns:
    """Drift term ``r * w * s`` - returns on invested capital."""

    name = "capital_returns"

    def drift(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        p = ctx.params
        s = savings_share(state, p)
        # Returns only accrue on positive wealth.
        return p.r * np.maximum(state.wealth, 0.0) * s
