"""Bands: classification, shares, and the effective poverty line."""

from __future__ import annotations

import numpy as np

from simulation.core.bands import Band, band_shares, classify, effective_poverty_line
from simulation.core.config import ModelParams


def test_classify_maps_to_five_bands() -> None:
    p = ModelParams()
    w = np.array([0.0, 0.1, 0.3, 0.5, 0.8, 1.0])
    b = classify(w, p)
    assert b[0] == Band.POBREZA
    assert b[2] == Band.VULNERABLE     # between poverty_line and band_vulnerable
    assert b[-1] == Band.RICO
    assert b.tolist() == sorted(b.tolist())


def test_band_shares_sum_to_one() -> None:
    p = ModelParams()
    w = np.linspace(0, 1, 100)
    shares = band_shares(w, p)
    assert abs(sum(shares.values()) - 1.0) < 1e-9


def test_effective_line_absolute_by_default() -> None:
    p = ModelParams()
    w = np.full(50, 0.8)
    assert effective_poverty_line(w, p) == p.poverty_line


def test_effective_line_relative_when_enabled() -> None:
    p = ModelParams(relative_line_theta=0.5)
    w = np.full(50, 1.0)            # median 1.0 -> 0.5 line beats absolute 0.2
    assert effective_poverty_line(w, p) == 0.5
