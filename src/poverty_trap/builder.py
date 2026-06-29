"""Builder: compose a standard simulation from the component library.

This module is the one place that wires the components together into the
canonical model. It exists so callers (the CLI, tests, a future UI) get a
correctly ordered pipeline without repeating the wiring, while still being free
to assemble their own pipeline directly against the engine if they need to.

The ordering encoded here matters and is documented inline.
"""

from __future__ import annotations

import numpy as np

from .core.config import ModelParams
from .core.engine import Simulation
from .dynamics.capital_returns import CapitalReturns
from .dynamics.diffusion import DiffusionShocks
from .dynamics.effort import ConstantEffort, EffortPolicy
from .dynamics.neighborhood import NeighborhoodDrift
from .dynamics.poverty_premium import PovertyPremium
from .dynamics.value_creation import ValueCreation
from .events.opportunity import OpportunityProcess
from .observe.metrics import PopulationMetrics
from .population.lifecycle import (
    FirstPassageMonitor,
    GenerationalTransmission,
    SimpleRestart,
    SkillGrowth,
)
from .population.network import NetworkDrift, PeerInfluence, SocialNetwork
from .population.regime import RegimePolicy


def build_simulation(
    params: ModelParams | None = None,
    *,
    seed: int = 0,
    effort: float | EffortPolicy = 0.0,
    generational: bool = True,
    with_opportunity: bool = True,
    with_network: bool = True,
    lifespan_ticks: int = 4000,
    metrics_every: int = 50,
) -> Simulation:
    """Assemble the canonical poverty-trap simulation.

    Parameters
    ----------
    params:
        Model parameters (defaults to :class:`ModelParams` defaults).
    seed:
        Seed for the single RNG (full reproducibility).
    effort:
        Either a scalar effort level applied to everyone (``ConstantEffort``) or
        a custom :class:`EffortPolicy`.
    generational:
        If ``True``, resolved lives are replaced by their *children*
        (inheritance); if ``False``, slots restart fresh (no inheritance).
    with_opportunity, with_network:
        Toggle the v2 opportunity and network mechanisms. Turning both off
        recovers the v1 drift-diffusion model.
    lifespan_ticks:
        Max ticks before an unresolved life ages out (counts as "did not become
        rich").
    metrics_every:
        Sampling cadence for population metrics.

    Returns
    -------
    Simulation
        A ready-to-run engine with the effort policy already applied to the
        initial cohort.
    """
    params = params or ModelParams()
    effort_policy: EffortPolicy = ConstantEffort(effort) if isinstance(effort, (int, float)) else effort

    # 1-2. Drift and noise. Order within drift does not matter (they are summed).
    drift_terms = [NeighborhoodDrift(), PovertyPremium(), ValueCreation(), CapitalReturns()]
    if with_network:
        drift_terms.append(NetworkDrift())
        drift_terms.append(PeerInfluence())
    noise_terms = [DiffusionShocks()]

    # 4. Discrete events.
    event_processes = [OpportunityProcess()] if with_opportunity else []

    # 5. Population processes - ORDER MATTERS:
    #    grow skill -> refresh network -> apply regime (welfare/redistribution)
    #    -> resolve barriers and respawn. Resolution must see post-regime wealth.
    births = (
        GenerationalTransmission(effort_policy) if generational else SimpleRestart(effort_policy)
    )
    population_processes = [SkillGrowth()]
    if with_network:
        population_processes.append(SocialNetwork())
    population_processes.append(RegimePolicy())
    population_processes.append(FirstPassageMonitor(births, lifespan_ticks=lifespan_ticks))

    # 6. Observers.
    observers = [PopulationMetrics(every=metrics_every)]

    sim = Simulation(
        params,
        seed=seed,
        drift_terms=drift_terms,
        noise_terms=noise_terms,
        event_processes=event_processes,
        population_processes=population_processes,
        observers=observers,
    )
    # Apply the effort policy to the initial cohort (births handle respawns).
    effort_policy.assign(sim.state, np.arange(sim.state.n), sim.ctx)
    return sim
