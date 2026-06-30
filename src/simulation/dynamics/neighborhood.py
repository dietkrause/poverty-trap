"""Neighbourhood base drift (Chetty 2014: where you are born sets your trajectory)."""

from __future__ import annotations

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState


class NeighborhoodDrift:
    """The structural base drift set by the agent's zone.

    The poor zone has a negative base drift (without effort you slide toward
    ruin); the rich zone has a positive one. This is the simplest, most direct
    encoding of the geography-of-opportunity result: the neighbourhood, not the
    person, sets the baseline rate of change.
    """

    name = "neighborhood"

    def drift(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        p = ctx.params
        return np.where(state.zone == 0, p.mu_base_poor, p.mu_base_rich)
