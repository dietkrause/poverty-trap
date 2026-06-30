"""Diffusion shocks: the random hits of life (section 7.4, the noise term).

Each tick wealth gets a mean-zero gaussian shock scaled by ``sqrt(dt)`` so the
discrete walk approximates Brownian motion. The poor draw a larger volatility:
the same kind of event (a medical bill, a lost job) lands harder when there is
no cushion. Asymmetric volatility is part of why the trap is sticky.
"""

from __future__ import annotations

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState


class DiffusionShocks:
    """Mean-zero gaussian increment with zone-dependent volatility.

    Implements the noise term ``sigma_i * sqrt(dt) * Z`` with ``Z ~ N(0, 1)``.
    All randomness is drawn from ``ctx.rng`` for reproducibility.
    """

    name = "diffusion"

    def increment(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        p = ctx.params
        sigma = np.where(state.zone == 0, p.sigma_poor, p.sigma_rich)
        z = ctx.rng.standard_normal(state.n)
        return sigma * np.sqrt(p.dt) * z
