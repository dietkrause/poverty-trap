"""Effort policies (the controllable lever).

Effort is an agent attribute, not a force, so it is set by a *policy* (a Strategy
object) at birth and on respawn rather than computed in the drift pipeline. This
keeps "how much effort each agent exerts" swappable - a global constant, a
distribution across the population, or (later) an adaptive rule - without
touching the engine. The drift contribution of effort lives in
:class:`~simulation.dynamics.value_creation.ValueCreation`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState


@runtime_checkable
class EffortPolicy(Protocol):
    """Assigns the effort attribute for a set of agents."""

    name: str

    def assign(self, state: AgentState, idx: np.ndarray, ctx: SimContext) -> None:
        """Set ``state.effort`` in place for the integer positions ``idx``."""
        ...


class ConstantEffort:
    """Every agent exerts the same effort level in ``[0, 1]``.

    This is the v1 behaviour and the cleanest way to sweep a single "effort"
    knob from 0 to 1 and read off the escape rate.
    """

    name = "constant_effort"

    def __init__(self, level: float) -> None:
        self.level = float(np.clip(level, 0.0, 1.0))

    def assign(self, state: AgentState, idx: np.ndarray, ctx: SimContext) -> None:
        state.effort[idx] = self.level


class HeterogeneousEffort:
    """Effort drawn per agent from a Beta distribution around a target mean.

    Models a population where people differ in how hard they push. The Beta is
    parameterised by its mean and a concentration; higher concentration means
    everyone is closer to the mean.
    """

    name = "heterogeneous_effort"

    def __init__(self, mean: float, concentration: float = 4.0) -> None:
        self.mean = float(np.clip(mean, 1e-3, 1 - 1e-3))
        self.concentration = float(max(concentration, 1e-3))

    def assign(self, state: AgentState, idx: np.ndarray, ctx: SimContext) -> None:
        a = self.mean * self.concentration
        b = (1.0 - self.mean) * self.concentration
        state.effort[idx] = ctx.rng.beta(a, b, size=len(idx))
