"""Wealth-band classification and barrier helpers (the continuum, section 7.10).

The single binary "escaped / trapped" of v1 is replaced by an ordered ladder of
bands. This module is the one place that knows the band cutoffs, so reporting
"left poverty" and "became rich" as *distinct* events stays consistent across the
engine and the observers.
"""

from __future__ import annotations

from enum import IntEnum

import numpy as np

from .config import ModelParams


def effective_poverty_line(wealth: np.ndarray, params: ModelParams) -> float:
    """The poverty line for this population: absolute, or relative if configured.

    With ``relative_line_theta > 0`` the line rises with the median (a relative
    poverty concept), so escaping gets harder as society gets richer. Otherwise
    the static ``poverty_line`` is returned. Used wherever "below the line"
    matters (premium, efficiency, bands) so the notion stays consistent.
    """
    if params.relative_line_theta <= 0.0:
        return params.poverty_line
    return max(params.poverty_line, params.relative_line_theta * float(np.median(wealth)))


class Band(IntEnum):
    """Ordered wealth bands used for reporting the continuum."""

    POBREZA = 0
    VULNERABLE = 1
    MEDIA = 2
    ACOMODADO = 3
    RICO = 4


# Human-readable Spanish labels (the audience-facing names from docs/README.md).
BAND_LABELS: dict[int, str] = {
    Band.POBREZA: "pobreza",
    Band.VULNERABLE: "vulnerable",
    Band.MEDIA: "media",
    Band.ACOMODADO: "acomodado",
    Band.RICO: "rico",
}


def classify(wealth: np.ndarray, params: ModelParams) -> np.ndarray:
    """Map a wealth array to band indices (see :class:`Band`).

    Cutoffs come solely from ``params`` so the bands are configurable and never
    duplicated. Returns an ``int8`` array the same shape as ``wealth``.
    """
    edges = np.array(
        [params.poverty_line, params.band_vulnerable, params.band_acomodado, params.rich_threshold]
    )
    # np.searchsorted gives 0..4 buckets matching the five bands.
    return np.searchsorted(edges, wealth, side="right").astype(np.int8)


def band_shares(wealth: np.ndarray, params: ModelParams) -> dict[str, float]:
    """Return the fraction of the population in each band, keyed by label."""
    bands = classify(wealth, params)
    n = max(len(wealth), 1)
    return {
        BAND_LABELS[b]: float(np.count_nonzero(bands == b)) / n
        for b in Band
    }
