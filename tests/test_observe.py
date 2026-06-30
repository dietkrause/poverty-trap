"""Metrics and the snapshot emitter (the read-only viewer feed)."""

from __future__ import annotations

import json

import numpy as np

from simulation.observe.metrics import gini
from simulation.observe.stream import SnapshotEmitter


def test_gini_bounds() -> None:
    assert gini(np.ones(100)) == 0.0
    spike = np.zeros(100); spike[0] = 100.0
    assert gini(spike) > 0.9
    assert gini(np.array([])) == 0.0


def test_emitter_fires_on_cadence_and_is_serializable(state, ctx) -> None:
    frames = []
    em = SnapshotEmitter(frames.append, every=5, max_agents=50)
    ctx.tick = 5
    em.observe(state, ctx)
    ctx.tick = 6
    em.observe(state, ctx)            # not on cadence
    assert len(frames) == 1
    snap = frames[0]
    json.dumps(snap)                  # must be JSON-serialisable
    assert len(snap["agents"]["wealth"]) <= 60
    assert 0.0 <= snap["gini"] <= 1.0
