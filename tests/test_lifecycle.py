"""Lifecycle: skill growth, restart vs inheritance births, first-passage tally."""

from __future__ import annotations

import numpy as np

from poverty_trap.dynamics.effort import ConstantEffort
from poverty_trap.population.lifecycle import (
    FirstPassageMonitor,
    GenerationalTransmission,
    SimpleRestart,
    SkillGrowth,
)


def test_skill_growth_clipped(state, ctx) -> None:
    state.skill[:] = 0.999
    SkillGrowth().step(state, ctx)
    assert np.all(state.skill <= 1.0)


def test_simple_restart_resets_to_class_start(state, ctx) -> None:
    idx = np.arange(5)
    state.wealth[idx] = 0.5
    SimpleRestart(ConstantEffort(0.5)).spawn(state, idx, ctx)
    poor = state.zone[idx] == 0
    assert np.all(state.wealth[idx][poor] == ctx.params.start_poor)
    assert np.all(state.generation[idx] == 1)


def test_generational_records_parent(state, ctx) -> None:
    idx = np.arange(5)
    state.wealth[idx] = 0.8
    GenerationalTransmission(ConstantEffort(0.5)).spawn(state, idx, ctx)
    assert np.all(state.parent_wealth[idx] == 0.8)          # parent recorded for IGE
    assert np.all(np.isfinite(state.wealth[idx]))


def test_monitor_counts_rich_resolution(state, ctx) -> None:
    mon = FirstPassageMonitor(SimpleRestart(ConstantEffort(0.0)), lifespan_ticks=10_000)
    state.wealth[:] = ctx.params.rich_threshold + 0.1      # everyone resolves rich
    mon.step(state, ctx)
    r = mon.report()
    assert r["poor"]["became_rich"] + r["rich"]["became_rich"] > 0
    assert r["poor"]["attempts"] + r["rich"]["attempts"] == state.n
