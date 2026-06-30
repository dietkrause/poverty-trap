"""Regime presets: named parameter sets standing in for country/policy settings.

These are **illustrative**, not calibrated estimates of any real country. They
exist to demonstrate the mechanism in section 7.9: run the *same* agents (same
seed) under different structural dials and watch the mobility numbers move. Tune
them against real data (IGE, generations-to-mean) before drawing conclusions.
"""

from __future__ import annotations

from ..core.config import ModelParams

#: A harsh regime: a steeper cost-of-living drag and poverty premium, concentrated
#: opportunity, no safety net.
HARSH = ModelParams().evolve(
    mu_base_poor=-0.025,
    premium=0.012,
    lambda0=0.06,
    pareto_a=1.3,          # heavier tail = more concentrated opportunity
    welfare_floor=None,
    redistribution=0.0,
)

#: A protective regime: a lighter cost-of-living drag, lower premium, an education
#: head-start, broader opportunity, and redistribution. (No hard welfare floor: a
#: reflecting floor removes the ruin exit and unrealistically lifts almost everyone
#: at this calibration - see docs/literature/calibration.md.)
PROTECTIVE = ModelParams().evolve(
    mu_base_poor=-0.006,
    premium=0.001,
    lambda0=0.16,
    pareto_a=1.9,          # lighter tail = less concentrated opportunity
    redistribution=0.05,
    education_headstart=0.18,
)

#: A middling regime between the two.
MIXED = ModelParams().evolve(
    premium=0.006,
    lambda0=0.10,
    pareto_a=1.5,
    welfare_floor=None,
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
