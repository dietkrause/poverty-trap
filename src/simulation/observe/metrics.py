"""Observers: read-only metric collectors (section 8.1, headless metrics).

Observers never mutate the state. They expose a ``report()`` that the engine
harvests at the end of a run, so every on-screen claim ("X% left poverty",
"the gap widened") is backed by a recorded number. The first-passage mobility
rates live on :class:`~simulation.population.lifecycle.FirstPassageMonitor`;
this module covers *population-level* snapshots: inequality and band structure.
"""

from __future__ import annotations

import numpy as np

from ..core.bands import band_shares
from ..core.context import SimContext
from ..core.state import AgentState


def gini(wealth: np.ndarray) -> float:
    """Gini coefficient of a non-negative wealth array (0 = equal, 1 = maximal).

    Uses the sorted, mean-normalised formulation. Negative wealth (debt) is
    clipped to zero so the coefficient stays in ``[0, 1]``.
    """
    w = np.sort(np.clip(wealth, 0.0, None))
    n = w.size
    if n == 0 or w.sum() == 0.0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((np.sum((2 * index - n - 1) * w)) / (n * w.sum()))


class PopulationMetrics:
    """Records inequality and band composition on a fixed sampling cadence.

    Parameters
    ----------
    every:
        Record a snapshot every ``every`` ticks (keeps memory bounded on long
        runs). The final ``report()`` returns the last snapshot plus the wealth
        gap time series (mean wealth of the poor vs rich zone).
    """

    def __init__(self, every: int = 50) -> None:
        self.every = max(int(every), 1)
        self.gap_poor: list[float] = []
        self.gap_rich: list[float] = []
        self._last_gini: float = 0.0
        self._last_bands: dict[str, float] = {}

    def observe(self, state: AgentState, ctx: SimContext) -> None:
        if ctx.tick % self.every != 0:
            return
        poor = state.zone == 0
        self.gap_poor.append(float(np.mean(state.wealth[poor])) if np.any(poor) else 0.0)
        self.gap_rich.append(float(np.mean(state.wealth[~poor])) if np.any(~poor) else 0.0)
        self._last_gini = gini(state.wealth)
        self._last_bands = band_shares(state.wealth, ctx.params)

    def report(self) -> dict:
        return {
            "gini": round(self._last_gini, 4),
            "band_shares": {k: round(v, 4) for k, v in self._last_bands.items()},
            "wealth_gap_series": {"poor": self.gap_poor, "rich": self.gap_rich},
        }
