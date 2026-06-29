"""Value creation: effort = magnitude x efficiency x direction (sections 7.2-7.4).

This is the agent's one controllable lever, made honest. Raw effort ``e`` is
scaled by an efficiency ``eta`` (the scarcity tax: poverty and stressors degrade
how much value an hour of effort yields) and a quality ``q`` (skill turns effort
into value; low-skill effort barely multiplies). The three helper functions are
exposed so observers and other components can read ``eta``, ``q`` and the savings
share ``s`` without recomputing them inconsistently.
"""

from __future__ import annotations

import numpy as np

from ..core.bands import effective_poverty_line
from ..core.config import ModelParams
from ..core.context import SimContext
from ..core.state import AgentState


def _logistic(x: np.ndarray) -> np.ndarray:
    """Numerically stable logistic ``S(x) = 1 / (1 + e^-x)``."""
    return 0.5 * (1.0 + np.tanh(0.5 * x))


def effort_efficiency(state: AgentState, p: ModelParams) -> np.ndarray:
    """``eta_i`` in ``[eta_min, 1]`` (section 7.2, the scarcity tax).

    Rises with slack above the poverty line and falls with the stressor load,
    so the same effort buys less when you are poor or burdened. Uses the
    effective (possibly relative) poverty line.
    """
    line = effective_poverty_line(state.wealth, p)
    x = p.k_w * (state.wealth - line) - p.k_s * state.stressors
    return p.eta_min + (1.0 - p.eta_min) * _logistic(x)


def effort_quality(state: AgentState, p: ModelParams) -> np.ndarray:
    """``q_i`` in ``[q_min, 1]`` (section 7.3): skill turns effort into value."""
    return p.q_min + (1.0 - p.q_min) * (state.skill / (state.skill + p.h_half))


def savings_share(state: AgentState, p: ModelParams) -> np.ndarray:
    """``s_i`` in ``[0, s_max]`` (section 7.3): share of surplus reinvested.

    Zero below subsistence (you cannot save what you do not have); rises with
    skill / financial literacy. Used by :class:`CapitalReturns`.
    """
    above_subsistence = (state.wealth > p.w_sub).astype(np.float64)
    return p.s_max * _logistic(p.k_h * (state.skill - p.h_bar)) * above_subsistence


class ValueCreation:
    """Drift term ``alpha * e * eta * q`` - the value the agent creates.

    Effort enters with a magnitude (``e``), an efficiency (``eta``), and a
    direction/quality (``q``). This is why two agents with identical effort can
    end up in very different places, and why effort has the largest leverage for
    those who can convert it.
    """

    name = "value_creation"

    def drift(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        p = ctx.params
        eta = effort_efficiency(state, p)
        q = effort_quality(state, p)
        return p.alpha * state.effort * eta * q
