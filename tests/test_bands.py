"""Bands: classification, shares, and the effective poverty line."""

from __future__ import annotations

import numpy as np

from simulation.core.bands import Band, band_shares, classify, effective_poverty_line
from simulation.core.config import ModelParams


def test_classify_maps_to_five_bands() -> None:
    p = ModelParams()
    # One representative wealth in each band, derived from the (calibrated) cutoffs
    # so the test stays valid if the bands are recalibrated.
    mids = np.array([
        (p.ruin + p.poverty_line) / 2,            # pobreza
        (p.poverty_line + p.band_vulnerable) / 2,  # vulnerable
        (p.band_vulnerable + p.band_acomodado) / 2,  # media
        (p.band_acomodado + p.rich_threshold) / 2,   # acomodado
        p.rich_threshold + 0.1,                    # rico
    ])
    b = classify(mids, p)
    assert b.tolist() == [Band.POBREZA, Band.VULNERABLE, Band.MEDIA, Band.ACOMODADO, Band.RICO]
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
