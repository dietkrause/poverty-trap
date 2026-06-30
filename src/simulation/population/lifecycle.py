"""Lifecycle: skill growth, first-passage accounting, and birth policies (section 7.8).

A *life* runs until it resolves - it reaches the rich threshold, hits ruin, or
ages out. :class:`FirstPassageMonitor` detects resolutions, tallies the outcomes
that the model is about (left poverty vs became rich, by birth class), and then
respawns the slot through an injected :class:`~simulation.core.protocols.BirthPolicy`.
Swapping the birth policy switches between "everyone restarts fresh" and "wealth,
talent and place are inherited", without touching the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..core.context import SimContext
from ..core.state import AgentState
from ..dynamics.effort import EffortPolicy

_EPS = 1e-9


class SkillGrowth:
    """Per-tick human-capital accrual (denser resource nodes in the rich zone)."""

    name = "skill_growth"

    def step(self, state: AgentState, ctx: SimContext) -> None:
        p = ctx.params
        growth = np.where(state.zone == 0, p.skill_growth_poor, p.skill_growth_rich)
        np.clip(state.skill + growth, 0.05, 1.0, out=state.skill)


# --------------------------------------------------------------------------- #
# Birth policies (Strategy pattern, injected into the monitor)
# --------------------------------------------------------------------------- #


class SimpleRestart:
    """Respawn a resolved slot as a fresh life of the same class (v1 behaviour).

    No inheritance: the next generation starts from scratch in the same zone.
    Useful as a clean baseline and for measuring a stable per-life escape rate.
    """

    name = "simple_restart"

    def __init__(self, effort_policy: EffortPolicy) -> None:
        self.effort_policy = effort_policy

    def spawn(self, state: AgentState, idx: np.ndarray, ctx: SimContext) -> None:
        p, rng = ctx.params, ctx.rng
        poor = state.zone[idx] == 0
        state.wealth[idx] = np.where(poor, p.start_poor, p.start_rich)
        state.talent[idx] = rng.standard_normal(idx.size)
        state.skill[idx] = np.clip(
            0.5 + 0.15 * state.talent[idx] + np.where(poor, -0.1, 0.1), 0.05, 0.95
        )
        state.stressors[idx] = rng.exponential(1.0, idx.size) * np.where(poor, 1.0, 0.3)
        state.generation[idx] += 1
        state.parent_wealth[idx] = np.nan
        state.birth_wealth[idx] = state.wealth[idx]
        state.ever_left_poverty[idx] = False
        state.resolved[idx] = 0
        self.effort_policy.assign(state, idx, ctx)


class GenerationalTransmission:
    """Respawn a resolved slot as the *child* of the life that just ended.

    The child inherits a fraction of the parent's final wealth, a correlated
    talent draw, the same zone (barring a rare mobility event), and an education
    head-start if the parent finished above the poverty line. Calibrating
    ``inherit_fraction`` and ``talent_heritability`` lets the simulated
    intergenerational elasticity match real data (section 7.8).
    """

    name = "generational_transmission"

    def __init__(self, effort_policy: EffortPolicy) -> None:
        self.effort_policy = effort_policy

    def spawn(self, state: AgentState, idx: np.ndarray, ctx: SimContext) -> None:
        p, rng = ctx.params, ctx.rng
        parent_final = state.wealth[idx].copy()

        # Rare mobility: the child may be born into the other zone.
        flip = rng.random(idx.size) < p.move_probability
        state.zone[idx] = np.where(flip, 1 - state.zone[idx], state.zone[idx])
        poor = state.zone[idx] == 0

        base = np.where(poor, p.start_poor, p.start_rich)
        eps = rng.normal(0.0, 0.02, idx.size)
        child_w = p.inherit_fraction * parent_final + (1.0 - p.inherit_fraction) * base + eps
        floor = p.welfare_floor if p.welfare_floor is not None else p.ruin
        state.wealth[idx] = np.maximum(child_w, floor + 1e-3)

        rho = p.talent_heritability
        state.talent[idx] = rho * state.talent[idx] + np.sqrt(1.0 - rho * rho) * rng.standard_normal(
            idx.size
        )
        above = parent_final >= p.poverty_line
        state.skill[idx] = np.clip(
            0.4 + p.education_headstart * above + 0.15 * state.talent[idx], 0.05, 0.95
        )
        state.stressors[idx] = rng.exponential(1.0, idx.size) * np.where(poor, 1.0, 0.3)

        state.generation[idx] += 1
        state.parent_wealth[idx] = parent_final
        state.birth_wealth[idx] = state.wealth[idx]
        state.ever_left_poverty[idx] = False
        state.resolved[idx] = 0
        self.effort_policy.assign(state, idx, ctx)


# --------------------------------------------------------------------------- #
# First-passage accounting + respawn
# --------------------------------------------------------------------------- #


@dataclass
class _Counter:
    attempts: int = 0
    reached_rich: int = 0
    left_poverty: int = 0

    def rate_rich(self) -> float:
        return self.reached_rich / self.attempts if self.attempts else 0.0

    def rate_left_poverty(self) -> float:
        return self.left_poverty / self.attempts if self.attempts else 0.0


class FirstPassageMonitor:
    """Resolves lives, tallies outcomes, and respawns via the birth policy.

    A life resolves when it reaches the rich threshold, hits ruin, or ages out
    after ``lifespan_ticks``. For each resolved life we record, separately for
    those born poor and born rich, whether it became rich and whether it ever
    left poverty - the two distinct probabilities the continuum reports. We also
    collect (log parent wealth, log child final wealth) pairs to estimate the
    intergenerational elasticity (IGE).
    """

    name = "first_passage"

    def __init__(self, births, lifespan_ticks: int = 4000) -> None:
        self.births = births
        self.lifespan = int(lifespan_ticks)
        self.poor = _Counter()
        self.rich = _Counter()
        self._age: np.ndarray | None = None
        self._ige_parent: list[float] = []
        self._ige_child: list[float] = []

    def step(self, state: AgentState, ctx: SimContext) -> None:
        p = ctx.params
        if self._age is None:
            self._age = np.zeros(state.n, dtype=np.int64)

        # Track "ever left poverty" for the current life.
        state.ever_left_poverty |= state.wealth >= p.poverty_line
        self._age += 1

        reached_rich = state.wealth >= p.rich_threshold
        ruined = state.wealth <= p.ruin
        aged = self._age >= self.lifespan
        resolved = reached_rich | ruined | aged
        idx = np.flatnonzero(resolved)
        if idx.size == 0:
            return

        born_poor = state.zone[idx] == 0
        escaped = reached_rich[idx]
        left = state.ever_left_poverty[idx]

        self.poor.attempts += int(np.count_nonzero(born_poor))
        self.poor.reached_rich += int(np.count_nonzero(escaped & born_poor))
        self.poor.left_poverty += int(np.count_nonzero(left & born_poor))
        self.rich.attempts += int(np.count_nonzero(~born_poor))
        self.rich.reached_rich += int(np.count_nonzero(escaped & ~born_poor))
        self.rich.left_poverty += int(np.count_nonzero(left & ~born_poor))

        # Intergenerational pairs (only where this life had a recorded parent).
        pw = state.parent_wealth[idx]
        valid = np.isfinite(pw) & (pw > _EPS)
        if np.any(valid):
            fw = np.maximum(state.wealth[idx][valid], _EPS)
            self._ige_parent.extend(np.log(pw[valid]).tolist())
            self._ige_child.extend(np.log(fw).tolist())

        # Respawn the resolved slots and reset their age.
        self.births.spawn(state, idx, ctx)
        self._age[idx] = 0

    def ige(self) -> float | None:
        """Estimate the intergenerational elasticity, or ``None`` if too few pairs."""
        if len(self._ige_parent) < 50:
            return None
        slope, _ = np.polyfit(self._ige_parent, self._ige_child, 1)
        return float(slope)

    def report(self) -> dict:
        """Summarise the two distinct mobility probabilities (and IGE)."""
        return {
            "birth_policy": getattr(self.births, "name", "?"),
            "poor": {
                "attempts": self.poor.attempts,
                "became_rich": round(self.poor.rate_rich(), 4),
                "left_poverty": round(self.poor.rate_left_poverty(), 4),
            },
            "rich": {
                "attempts": self.rich.attempts,
                "became_rich": round(self.rich.rate_rich(), 4),
                "left_poverty": round(self.rich.rate_left_poverty(), 4),
            },
            "ige": self.ige(),
        }
