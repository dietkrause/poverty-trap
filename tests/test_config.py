"""Config: validation rules and immutable evolution."""

from __future__ import annotations

import pytest

from poverty_trap.core.config import ModelParams


def test_defaults_validate() -> None:
    ModelParams().validate()


def test_evolve_is_immutable_copy() -> None:
    base = ModelParams()
    changed = base.evolve(premium=0.5)
    assert changed.premium == 0.5
    assert base.premium != 0.5  # original untouched


@pytest.mark.parametrize("bad", [
    {"n_agents": 0},
    {"dt": 0.0},
    {"poverty_line": 1.5},           # not < rich_threshold
    {"poor_fraction": 1.5},
    {"pareto_a": 0.9},               # must be > 1 for finite mean
    {"talent_heritability": 1.5},
])
def test_invalid_params_raise(bad: dict) -> None:
    with pytest.raises(ValueError):
        ModelParams().evolve(**bad).validate()


def test_band_ordering_enforced() -> None:
    with pytest.raises(ValueError):
        ModelParams(band_acomodado=0.3, band_vulnerable=0.45).validate()
