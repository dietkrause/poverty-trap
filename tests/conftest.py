"""Shared pytest fixtures: a small, fast world for component tests."""

from __future__ import annotations

import numpy as np
import pytest

from poverty_trap.core.config import ModelParams
from poverty_trap.core.context import SimContext
from poverty_trap.core.state import AgentState


@pytest.fixture
def params() -> ModelParams:
    return ModelParams(n_agents=120)


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(0)


@pytest.fixture
def ctx(params: ModelParams, rng: np.random.Generator) -> SimContext:
    return SimContext(params=params, rng=rng)


@pytest.fixture
def state(params: ModelParams, rng: np.random.Generator) -> AgentState:
    return AgentState.initialize(params, rng)
