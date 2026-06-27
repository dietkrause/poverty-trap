"""Component interfaces (the seams of the engine).

These ``Protocol`` classes are the only thing the engine depends on
(Dependency Inversion). Each interface is intentionally tiny (Interface
Segregation): a component implements exactly the one role it plays. The engine
runs them in a fixed, well-defined order each tick (see ``engine.py``).

A component may implement more than one protocol if it genuinely fills more
than one role, but prefer one class per responsibility.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from .context import SimContext
from .state import AgentState


@runtime_checkable
class DriftTerm(Protocol):
    """Contributes an additive term to the expected per-agent drift ``mu``.

    Implementations are pure: they must **not** mutate the state. They return a
    ``(n,)`` float array that is summed with the other drift terms. This is how
    neighbourhood drift, the poverty premium, value creation, social capital and
    capital returns each plug in independently.
    """

    name: str

    def drift(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        """Return this term's contribution to ``mu`` for every agent."""
        ...


@runtime_checkable
class NoiseTerm(Protocol):
    """Contributes a stochastic increment added to wealth each tick.

    Separated from :class:`DriftTerm` because noise scales with ``sqrt(dt)``
    while drift scales with ``dt``; keeping them distinct keeps the numerical
    integration correct and the responsibilities clean.
    """

    name: str

    def increment(self, state: AgentState, ctx: SimContext) -> np.ndarray:
        """Return the additive stochastic increment for every agent."""
        ...


@runtime_checkable
class EventProcess(Protocol):
    """Applies discrete, in-place changes to the state (e.g. opportunity jumps).

    Unlike drift/noise (which the engine sums and applies), an event process
    mutates the state directly, because its effect is a jump, not a flow.
    """

    name: str

    def apply(self, state: AgentState, ctx: SimContext) -> None:
        """Mutate ``state`` in place to apply this tick's events."""
        ...


@runtime_checkable
class PopulationProcess(Protocol):
    """Changes who/where the agents are: births, deaths, barriers, rewiring.

    Runs after the economic update so that resolution (hitting a barrier) and
    reproduction see the post-update wealth.
    """

    name: str

    def step(self, state: AgentState, ctx: SimContext) -> None:
        """Mutate ``state`` in place (resolve barriers, respawn, rewire...)."""
        ...


@runtime_checkable
class Observer(Protocol):
    """Reads the state to record metrics. Must never mutate it.

    Observers run last each tick. Because they only read, any number of them can
    be attached without affecting the dynamics (e.g. a live UI and a metrics
    recorder at the same time).
    """

    def observe(self, state: AgentState, ctx: SimContext) -> None:
        """Record whatever this observer tracks for the current tick."""
        ...


@runtime_checkable
class BirthPolicy(Protocol):
    """Strategy for (re)spawning an agent once its life resolves.

    Injected into the barrier/lifecycle process so that "simple restart" and
    "generational transmission" are swappable without touching the engine
    (Open/Closed, Dependency Inversion).
    """

    name: str

    def spawn(self, state: AgentState, idx: np.ndarray, ctx: SimContext) -> None:
        """Reinitialise the agents at integer positions ``idx`` in place."""
        ...
