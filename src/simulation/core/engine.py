"""The simulation engine: a deterministic orchestrator over pluggable components.

The engine knows *nothing* about the specific model. It holds ordered lists of
components (each satisfying one of the protocols in :mod:`simulation.core.protocols`)
and runs them in a fixed order every tick:

1. **drift terms**  -> sum into ``mu``      (flows, scaled by ``dt``)
2. **noise terms**  -> sum into increment   (shocks, scaled by ``sqrt(dt)``)
3. apply ``wealth += mu*dt + increment``
4. **event processes** (discrete jumps, e.g. opportunities)
5. **population processes** (barriers, births/deaths, network rewiring)
6. **observers** (record metrics; never mutate)

Adding a new mechanism means appending a component, never editing this file
(Open/Closed). Because every stochastic draw flows through ``ctx.rng``, a run is
fully reproducible from its seed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import ModelParams
from .context import SimContext
from .protocols import (
    DriftTerm,
    EventProcess,
    NoiseTerm,
    Observer,
    PopulationProcess,
)
from .state import AgentState


@dataclass(slots=True)
class SimulationResult:
    """Lightweight container returned by :meth:`Simulation.run`.

    Holds the final state plus whatever each observer chose to expose via its
    own ``report()`` method (collected into ``reports`` keyed by observer name).
    """

    ticks: int
    final_state: AgentState
    reports: dict[str, object] = field(default_factory=dict)


class Simulation:
    """Composable, deterministic simulation engine.

    Parameters
    ----------
    params:
        Immutable model parameters.
    seed:
        Seed for the single random generator (reproducibility).
    drift_terms, noise_terms, event_processes, population_processes, observers:
        Ordered component lists. The order within each list is the order of
        execution, which can matter for population processes (e.g. resolve
        barriers before respawning).

    Notes
    -----
    The engine validates parameters once at construction so misconfiguration
    fails fast. Components are stored by reference; they may hold their own
    state (e.g. a metrics accumulator) and expose a ``report()`` method that the
    engine harvests at the end of a run.
    """

    def __init__(
        self,
        params: ModelParams,
        *,
        seed: int = 0,
        drift_terms: list[DriftTerm] | None = None,
        noise_terms: list[NoiseTerm] | None = None,
        event_processes: list[EventProcess] | None = None,
        population_processes: list[PopulationProcess] | None = None,
        observers: list[Observer] | None = None,
    ) -> None:
        params.validate()
        self.params = params
        self.ctx = SimContext(params=params, rng=np.random.default_rng(seed))
        self.state = AgentState.initialize(params, self.ctx.rng)

        self.drift_terms = list(drift_terms or [])
        self.noise_terms = list(noise_terms or [])
        self.event_processes = list(event_processes or [])
        self.population_processes = list(population_processes or [])
        self.observers = list(observers or [])

    # --- One step -----------------------------------------------------------

    def step(self) -> None:
        """Advance the simulation by exactly one tick (see module docstring)."""
        state, ctx, p = self.state, self.ctx, self.params
        ctx.bus.clear()

        # 1-2. Accumulate drift and noise without mutating wealth mid-sum.
        mu = np.zeros(state.n, dtype=np.float64)
        for term in self.drift_terms:
            mu += term.drift(state, ctx)
        state.last_drift = mu

        increment = mu * p.dt
        for noise in self.noise_terms:
            increment = increment + noise.increment(state, ctx)

        # 3. Apply the economic update.
        state.wealth = state.wealth + increment

        # 4. Discrete events (opportunities) jump wealth directly.
        for event in self.event_processes:
            event.apply(state, ctx)

        # 5. Population dynamics: barriers, births/deaths, network.
        for pop in self.population_processes:
            pop.step(state, ctx)

        # 6. Observers read the settled state.
        for obs in self.observers:
            obs.observe(state, ctx)

        ctx.advance()

    # --- Full run -----------------------------------------------------------

    def run(self, ticks: int) -> SimulationResult:
        """Run ``ticks`` steps and return the result with every component report.

        Any component (observer, population process, event process, ...) that
        exposes a callable ``report()`` has it harvested here, keyed by class
        name. This lets metric-bearing components live in whichever pipeline
        stage they belong to without special-casing.
        """
        for _ in range(ticks):
            self.step()
        reports: dict[str, object] = {}
        components = (
            *self.drift_terms,
            *self.noise_terms,
            *self.event_processes,
            *self.population_processes,
            *self.observers,
        )
        for component in components:
            report = getattr(component, "report", None)
            if callable(report):
                reports[type(component).__name__] = report()
        return SimulationResult(ticks=ticks, final_state=self.state, reports=reports)
