"""Regime presets: named parameter sets standing in for country/policy settings.

These are **illustrative**, not calibrated estimates of any real country. They
exist to demonstrate the mechanism in section 7.9: run the *same* agents (same
seed) under different structural dials and watch the mobility numbers move. Tune
them against real data (IGE, generations-to-mean) before drawing conclusions.
"""

from __future__ import annotations

from ..core.config import ModelParams

#: A harsh regime: a steep poverty premium, concentrated opportunity, no floor.
HARSH = ModelParams().evolve(
    premium=0.006,
    lambda0=0.07,
    pareto_a=1.3,          # heavier tail = more concentrated opportunity
    welfare_floor=None,
    redistribution=0.0,
)

#: A protective regime: a welfare floor, redistribution, broader opportunity.
PROTECTIVE = ModelParams().evolve(
    premium=0.002,
    lambda0=0.14,
    pareto_a=1.8,          # lighter tail = less concentrated opportunity
    welfare_floor=0.06,
    redistribution=0.05,
    education_headstart=0.18,
)

#: A middling regime between the two.
MIXED = ModelParams().evolve(
    premium=0.004,
    lambda0=0.10,
    pareto_a=1.5,
    welfare_floor=0.0,
    redistribution=0.0,
)

#: Registry so presets can be selected by name (e.g. from the CLI).
PRESETS: dict[str, ModelParams] = {
    "harsh": HARSH,
    "mixed": MIXED,
    "protective": PROTECTIVE,
}


def get_preset(name: str) -> ModelParams:
    """Return a named preset, or raise ``KeyError`` listing the valid names."""
    try:
        return PRESETS[name]
    except KeyError as exc:
        raise KeyError(f"unknown regime '{name}'. Options: {sorted(PRESETS)}") from exc
