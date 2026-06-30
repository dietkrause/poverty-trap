"""simulation - an agent-based simulation engine for poverty-trap dynamics.

The engine models a population of agents whose wealth evolves as a drift-diffusion
between a ruin floor and a "Micawber" escape threshold, extended with effort
efficiency, opportunity (a marked Poisson / power-law process), social networks,
and generational transmission. See ``docs/README.md`` for the full model.

Design philosophy
-----------------
The engine is a small, composable core (``simulation.core``) that orchestrates a
pipeline of independent, single-responsibility components:

* ``DriftTerm``        - contributes to the expected per-agent wealth change (mu).
* ``NoiseTerm``        - contributes a stochastic increment (shocks).
* ``EventProcess``     - applies discrete jumps (e.g. opportunities).
* ``PopulationProcess``- births, deaths, network rewiring, barrier resolution.
* ``Observer``         - reads (never mutates) the state to record metrics.

New behaviour is added by writing a new component, never by editing the engine
(Open/Closed). The engine depends only on the ``Protocol`` interfaces in
``simulation.core.protocols`` (Dependency Inversion), and all randomness flows
through a single injected generator (deterministic, reproducible runs).
"""

from __future__ import annotations

__version__ = "0.1.0"

from .core.config import ModelParams
from .core.engine import Simulation, SimulationResult

__all__ = ["ModelParams", "Simulation", "SimulationResult", "__version__"]
