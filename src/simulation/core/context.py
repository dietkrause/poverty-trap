"""Per-run context: the shared, read-mostly environment handed to every component.

The context carries the immutable parameters, the single random generator, and
the running clock (tick index and elapsed time). Passing one ``SimContext`` to
every component means randomness is centralised (reproducible) and no component
needs a back-reference to the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import ModelParams


@dataclass(slots=True)
class SimContext:
    """Read-mostly environment shared across a single simulation run.

    Parameters
    ----------
    params:
        The immutable model parameters for this run.
    rng:
        The single NumPy generator. **All** stochastic draws in the engine must
        come from here so that a fixed seed fully determines a run.
    tick:
        Integer step counter, advanced by the engine.
    time:
        Elapsed model time (``tick * params.dt``).
    """

    params: ModelParams
    rng: np.random.Generator
    tick: int = 0
    time: float = 0.0
    # Scratch channel for components to publish per-tick events (e.g. the
    # opportunities captured this tick) for observers to read. Cleared by the
    # engine at the start of each tick.
    bus: dict = field(default_factory=dict)

    def advance(self) -> None:
        """Advance the clock by one step. Called by the engine each tick."""
        self.tick += 1
        self.time += self.params.dt
