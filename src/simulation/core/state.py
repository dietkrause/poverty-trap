"""Vectorised agent state.

All per-agent attributes are stored as parallel NumPy arrays of length ``n``
(structure-of-arrays), so a population of thousands evolves with vectorised
operations rather than Python-level loops. ``AgentState`` is a passive data
container: components read and write its arrays, but the *rules* live in the
components, not here (Single Responsibility).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import ModelParams


@dataclass(slots=True)
class AgentState:
    """Structure-of-arrays holding the live population.

    Every array has shape ``(n,)``. ``zone`` and ``generation`` are integer
    arrays; the rest are float64. Status arrays (``ever_left_poverty``,
    ``resolved``) support first-passage accounting without coupling the state
    to any particular metric.
    """

    n: int

    # Core economic attributes
    wealth: np.ndarray            # w_i
    talent: np.ndarray            # T_i  (fixed at birth, ~ Normal)
    skill: np.ndarray             # h_i  (human capital, accrues over life)
    effort: np.ndarray            # e_i  in [0, 1]
    stressors: np.ndarray         # St_i >= 0 (drag on effort efficiency)
    connectedness: np.ndarray     # c_i  in [0, 1] (share of ties above the line)
    zone: np.ndarray              # 0 = poor neighbourhood, 1 = rich neighbourhood
    generation: np.ndarray        # g_i  (lineage depth, integer)

    # Lineage / first-passage bookkeeping
    birth_wealth: np.ndarray      # wealth this life started with
    parent_wealth: np.ndarray     # parent's final wealth (NaN for generation 0)
    ever_left_poverty: np.ndarray # bool: this life has crossed the poverty line
    resolved: np.ndarray          # int8: 0 = striving, +1 = reached rich, -1 = ruined

    # Per-tick scratch space (filled by the drift pipeline / network, read by observers)
    last_drift: np.ndarray | None = field(default=None)
    peer_mean_wealth: np.ndarray | None = field(default=None)

    @classmethod
    def initialize(cls, params: ModelParams, rng: np.random.Generator) -> "AgentState":
        """Create the initial cohort from ``params``.

        Agents are split into a poor and a rich zone by ``poor_fraction``.
        Talent is drawn ``Normal(0, 1)`` (section 7.7); skill starts correlated
        with talent so that endowment matters from birth without fully
        determining outcomes.
        """
        n = params.n_agents
        zone = (rng.random(n) >= params.poor_fraction).astype(np.int64)  # 1 = rich
        poor = zone == 0

        wealth = np.where(poor, params.start_poor, params.start_rich).astype(np.float64)
        talent = rng.standard_normal(n)
        # Skill in [0, 1], nudged up by talent and by being in the rich zone.
        skill = np.clip(0.5 + 0.15 * talent + np.where(poor, -0.1, 0.1), 0.05, 0.95)
        effort = np.zeros(n, dtype=np.float64)          # set by an effort policy
        stressors = rng.exponential(1.0, n) * np.where(poor, 1.0, 0.3)
        connectedness = np.where(poor, 0.1, 0.7).astype(np.float64)

        return cls(
            n=n,
            wealth=wealth,
            talent=talent,
            skill=skill,
            effort=effort,
            stressors=stressors,
            connectedness=connectedness,
            zone=zone,
            generation=np.zeros(n, dtype=np.int64),
            birth_wealth=wealth.copy(),
            parent_wealth=np.full(n, np.nan),
            ever_left_poverty=np.zeros(n, dtype=bool),
            resolved=np.zeros(n, dtype=np.int8),
            last_drift=np.zeros(n, dtype=np.float64),
            peer_mean_wealth=wealth.copy(),
        )

    # --- Convenience masks (read-only views of the population) --------------

    def poor_mask(self) -> np.ndarray:
        """Boolean mask of agents currently in the poor zone."""
        return self.zone == 0

    def below_line(self, params: ModelParams) -> np.ndarray:
        """Boolean mask of agents currently below the poverty line."""
        return self.wealth < params.poverty_line
