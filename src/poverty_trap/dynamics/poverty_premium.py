"""The poverty premium (Ghatak 2015: being poor is more expensive)."""

from __future__ import annotations

import numpy as np

from ..core.bands import effective_poverty_line
from ..core.context import SimContext
from ..core.state import AgentState


class PovertyPremium:
    """An extra negative drift that switches on below the poverty line.

    The same shock costs a poor agent more (payday loans, no safety net, no bulk
    buying), so below the line every period carries an additional drag. This is
    the term that makes the low-wealth region self-reinforcing.
    """

    name = "poverty_premium"

    def drift(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        p = ctx.params
        line = effective_poverty_line(state.wealth, p)
        below = state.wealth < line
        return np.where(below, -p.premium, 0.0)
