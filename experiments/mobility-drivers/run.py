#!/usr/bin/env python3
"""Experiment: which levers move mobility, by how much, and do they interact?

This is a **factorial** experiment. Instead of sweeping one variable, it runs the
full canonical model across every combination of four levers and measures the two
mobility outcomes the model reports for a poor-born life:

  * P(became rich | born poor) - reaching the rich threshold; and
  * P(left poverty | born poor) - ever crossing the poverty line upward.

The four levers (factors) and their levels:

  * regime       : harsh | mixed | protective   (the structural / policy dial Theta)
  * effort       : 0.0 | 0.5 | 1.0              (value-creation magnitude)
  * opportunity  : on | off                     (the heavy-tailed "luck" process)
  * network      : on | off                     (social ties, peer spillover, pooling)

Inheritance (generational transmission) is left ON for every cell, so the result
is the canonical model, and the intergenerational elasticity (IGE) is meaningful.

Design notes aimed at keeping the conclusions honest (see also the README):

  * Balanced full factorial. Every combination is run, each averaged over the same
    set of seeds, so no cell is over- or under-sampled.
  * Main effects are estimated as *marginal means* (the average over all other
    factors). In a balanced design this is an unbiased main-effect estimate and
    does not depend on which other cells we happened to pick.
  * We report BOTH outcomes. They can move in different directions, and reporting
    only one ("escape rate") would hide that.
  * We report the born-rich vs born-poor gap explicitly as the structural baseline
    the levers are measured against.
  * The auto-written findings use fixed numeric thresholds and neutral templates,
    not hand-picked narrative, and every conclusion is stated as conditional on
    the model and its calibration - not as an empirical claim about the world.

Run:
    python experiments/mobility-drivers/run.py
    python experiments/mobility-drivers/run.py --ticks 8000 --seeds 6
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Bootstrap src/ onto the path so no install is required.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from simulation.builder import build_simulation  # noqa: E402
from simulation.core.config import ModelParams  # noqa: E402
from simulation.regimes.presets import get_preset  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

# The factorial design. Order is fixed for reproducible enumeration.
FACTORS: dict[str, list] = {
    "regime": ["harsh", "mixed", "protective"],
    "effort": [0.0, 0.5, 1.0],
    "opportunity": [True, False],
    "network": [True, False],
}

# Outcomes we score for each cell. Keys are stable; labels are for humans.
OUTCOMES: dict[str, str] = {
    "poor_became_rich": "P(became rich | born poor)",
    "poor_left_poverty": "P(left poverty | born poor)",
    "birth_gap_became_rich": "born-rich minus born-poor P(became rich)",
    "gini": "Gini (final living population)",
}


# --------------------------------------------------------------------------- #
# Running cells
# --------------------------------------------------------------------------- #
def run_cell(regime: str, effort: float, opportunity: bool, network: bool,
             *, ticks: int, seeds: int) -> dict:
    """Run one factor combination over ``seeds`` seeds; return mean and std metrics."""
    params = get_preset(regime)
    per_seed: dict[str, list[float]] = {
        "poor_became_rich": [], "poor_left_poverty": [],
        "rich_became_rich": [], "birth_gap_became_rich": [],
        "ige": [], "gini": [],
    }
    for seed in range(seeds):
        sim = build_simulation(
            params,
            seed=seed,
            effort=effort,
            generational=True,
            with_opportunity=opportunity,
            with_network=network,
        )
        reports = sim.run(ticks).reports
        fp = reports["FirstPassageMonitor"]
        pm = reports["PopulationMetrics"]
        poor, rich = fp["poor"], fp["rich"]
        per_seed["poor_became_rich"].append(poor["became_rich"])
        per_seed["poor_left_poverty"].append(poor["left_poverty"])
        per_seed["rich_became_rich"].append(rich["became_rich"])
        per_seed["birth_gap_became_rich"].append(rich["became_rich"] - poor["became_rich"])
        if fp.get("ige") is not None:
            per_seed["ige"].append(fp["ige"])
        per_seed["gini"].append(pm["gini"])

    def agg(vals: list[float]) -> dict:
        if not vals:
            return {"mean": None, "std": None, "n": 0}
        arr = np.asarray(vals, dtype=float)
        return {"mean": round(float(arr.mean()), 4),
                "std": round(float(arr.std(ddof=0)), 4),
                "n": int(arr.size)}

    return {k: agg(v) for k, v in per_seed.items()}


def run_design(ticks: int, seeds: int) -> list[dict]:
    """Run every cell of the factorial design; return a flat list of records."""
    levels = list(itertools.product(*FACTORS.values()))
    keys = list(FACTORS.keys())
    records: list[dict] = []
    total = len(levels)
    for i, combo in enumerate(levels, 1):
        factors = dict(zip(keys, combo))
        metrics = run_cell(**factors, ticks=ticks, seeds=seeds)
        records.append({"factors": factors, "metrics": metrics})
        pr = metrics["poor_became_rich"]["mean"]
        lp = metrics["poor_left_poverty"]["mean"]
        tag = (f"regime={factors['regime']:>10} effort={factors['effort']:.1f} "
               f"opp={'Y' if factors['opportunity'] else 'N'} "
               f"net={'Y' if factors['network'] else 'N'}")
        print(f"  [{i:>2}/{total}] {tag} | P(rich|poor)={pr:.3f} P(left|poor)={lp:.3f}")
    return records


# --------------------------------------------------------------------------- #
# Analysis (balanced main effects + one interaction)
# --------------------------------------------------------------------------- #
def _cell_means(records: list[dict], outcome: str) -> list[tuple[dict, float]]:
    """(factors, mean) pairs for an outcome, dropping cells with no value."""
    out = []
    for r in records:
        m = r["metrics"].get(outcome, {}).get("mean")
        if m is not None:
            out.append((r["factors"], m))
    return out


def main_effects(records: list[dict], outcome: str) -> dict:
    """Marginal mean of ``outcome`` at each level of each factor, plus its range.

    In a balanced design the marginal mean (unweighted average of the cell means
    at a given level) is the standard, design-unbiased main-effect estimate.
    """
    pairs = _cell_means(records, outcome)
    grand = float(np.mean([v for _, v in pairs])) if pairs else None
    result: dict = {"grand_mean": round(grand, 4) if grand is not None else None, "factors": {}}
    for factor, levels in FACTORS.items():
        level_means = {}
        for lvl in levels:
            vals = [v for f, v in pairs if f[factor] == lvl]
            level_means[str(lvl)] = round(float(np.mean(vals)), 4) if vals else None
        present = [v for v in level_means.values() if v is not None]
        rng = round(max(present) - min(present), 4) if present else None
        result["factors"][factor] = {"level_means": level_means, "effect_range": rng}
    return result


def effort_by_regime(records: list[dict], outcome: str) -> dict:
    """Interaction view: outcome marginal mean for each (regime, effort) pair."""
    table: dict[str, dict[str, float]] = {}
    for regime in FACTORS["regime"]:
        row = {}
        for effort in FACTORS["effort"]:
            vals = [r["metrics"][outcome]["mean"] for r in records
                    if r["factors"]["regime"] == regime
                    and r["factors"]["effort"] == effort
                    and r["metrics"][outcome]["mean"] is not None]
            row[str(effort)] = round(float(np.mean(vals)), 4) if vals else None
        table[regime] = row
    return table


def rank_drivers(effects: dict) -> list[tuple[str, float]]:
    """Factors sorted by absolute effect range (largest mover first)."""
    items = [(f, d["effect_range"]) for f, d in effects["factors"].items()
             if d["effect_range"] is not None]
    return sorted(items, key=lambda kv: abs(kv[1]), reverse=True)


# --------------------------------------------------------------------------- #
# Findings document (neutral, template-driven)
# --------------------------------------------------------------------------- #
def _direction(level_means: dict, levels: list) -> str:
    """Describe monotonicity of an outcome across an ordered factor's levels."""
    seq = [level_means[str(l)] for l in levels if level_means.get(str(l)) is not None]
    if len(seq) < 2:
        return "insufficient data"
    diffs = np.diff(seq)
    if np.all(diffs >= -1e-9):
        return "increases monotonically"
    if np.all(diffs <= 1e-9):
        return "decreases monotonically"
    return "moves non-monotonically"


def write_findings(records: list[dict], cfg: dict) -> str:
    eff_rich = main_effects(records, "poor_became_rich")
    eff_left = main_effects(records, "poor_left_poverty")
    eff_gini = main_effects(records, "gini")
    gap = main_effects(records, "birth_gap_became_rich")
    inter_rich = effort_by_regime(records, "poor_became_rich")

    drivers = rank_drivers(eff_rich)
    L = []
    L.append("# Findings: what moves mobility in the model")
    L.append("")
    L.append(f"*Generated {cfg['timestamp']} by `experiments/mobility-drivers/run.py`.*")
    L.append("")
    L.append("> **Read this as a conditional result.** An agent-based model does not "
             "prove a social fact; it shows the logical consequences of its micro-rules. "
             "Every statement below means: *within this model, calibrated as in "
             "`docs/literature/calibration.md`, this is what happens.* None of it is an "
             "empirical causal claim about any real economy. The numbers are model "
             "outputs, with sampling noise quantified by the across-seed standard "
             "deviation in `summary.json`.")
    L.append("")

    # Design block.
    L.append("## Design")
    L.append("")
    L.append(f"- **Cells:** {cfg['n_cells']} factor combinations (full factorial, balanced).")
    L.append(f"- **Seeds per cell:** {cfg['seeds']} (same seed set in every cell).")
    L.append(f"- **Ticks per run:** {cfg['ticks']}.")
    L.append(f"- **Total simulations:** {cfg['n_cells'] * cfg['seeds']}.")
    L.append("- **Varied factors:** "
             + ", ".join(f"`{k}` ({', '.join(map(str, v))})" for k, v in FACTORS.items()) + ".")
    L.append("- **Held fixed:** inheritance ON (generational transmission); all other "
             "parameters at their calibrated defaults / regime-preset values; "
             f"{cfg['n_agents']} agents.")
    L.append("")

    # Structural baseline.
    bg = gap["grand_mean"]
    L.append("## The structural baseline (what the levers are measured against)")
    L.append("")
    L.append(f"Averaged across every cell, the **born-rich minus born-poor** gap in "
             f"P(became rich) is **{bg:+.3f}**. This gap is the starting-position effect: "
             "two lives under identical rules and levers, differing only in birth zone. "
             "Read every lever's effect below relative to this baseline.")
    L.append("")

    # Main effects table for the two outcomes.
    L.append("## Main effects (marginal means)")
    L.append("")
    L.append("Each number is the outcome averaged over all cells at that factor level "
             "(balanced marginal mean). `effect range` is max minus min across the "
             "factor's levels - a model-internal effect size for that lever.")
    L.append("")
    for title, eff in [
        ("P(became rich | born poor)", eff_rich),
        ("P(left poverty | born poor)", eff_left),
    ]:
        L.append(f"### {title}  (grand mean = {eff['grand_mean']:.3f})")
        L.append("")
        L.append("| factor | levels (level: marginal mean) | effect range |")
        L.append("|--------|-------------------------------|--------------|")
        for factor, d in eff["factors"].items():
            lm = d["level_means"]
            cells = ", ".join(f"{lvl}: {lm[str(lvl)]:.3f}" for lvl in FACTORS[factor]
                              if lm.get(str(lvl)) is not None)
            L.append(f"| `{factor}` | {cells} | {d['effect_range']:+.3f} |")
        L.append("")

    # Ranked drivers.
    L.append("## Levers ranked by effect size (on P(became rich | born poor))")
    L.append("")
    for i, (factor, rng) in enumerate(drivers, 1):
        direction = (_direction(eff_rich["factors"][factor]["level_means"], FACTORS[factor])
                     if factor in ("effort",) else "varies by level")
        L.append(f"{i}. **`{factor}`** - effect range {rng:+.3f}"
                 + (f"; as effort rises, the outcome {direction}." if factor == "effort" else "."))
    L.append("")
    L.append("> Effect range here is a *within-model* magnitude, not a real-world "
             "elasticity. A lever can rank low simply because its two tested settings "
             "are close, or high because its levels are far apart; the levels are stated "
             "in the Design block so the comparison is transparent.")
    L.append("")

    # Interaction.
    L.append("## Interaction: does effort pay off equally under every regime?")
    L.append("")
    L.append("Marginal mean of P(became rich | born poor) for each (regime, effort) pair:")
    L.append("")
    efforts = FACTORS["effort"]
    L.append("| regime | " + " | ".join(f"effort {e}" for e in efforts) + " | lift 0->max |")
    L.append("|--------|" + "|".join(["---"] * (len(efforts) + 1)) + "|")
    for regime, row in inter_rich.items():
        vals = [row[str(e)] for e in efforts]
        lift = (vals[-1] - vals[0]) if (vals[0] is not None and vals[-1] is not None) else None
        cells = " | ".join(f"{v:.3f}" if v is not None else "-" for v in vals)
        L.append(f"| {regime} | {cells} | {lift:+.3f} |")
    L.append("")
    lifts = {regime: (row[str(efforts[-1])] - row[str(efforts[0])])
             for regime, row in inter_rich.items()
             if row[str(efforts[0])] is not None and row[str(efforts[-1])] is not None}
    if lifts:
        hi = max(lifts, key=lifts.get)
        lo = min(lifts, key=lifts.get)
        if abs(lifts[hi] - lifts[lo]) > 0.02:
            L.append(f"The payoff to effort is **not constant across regimes**: the lift from "
                     f"zero to full effort is largest under `{hi}` ({lifts[hi]:+.3f}) and "
                     f"smallest under `{lo}` ({lifts[lo]:+.3f}). In this model, structure and "
                     "effort interact rather than add independently.")
        else:
            L.append("The lift from zero to full effort is **similar across regimes** "
                     f"(range {min(lifts.values()):+.3f} to {max(lifts.values()):+.3f}), so "
                     "in this model effort and regime act roughly additively on this outcome.")
    L.append("")

    # Auto conclusions (neutral, threshold-driven, both outcomes).
    L.append("## Conclusions the runs support")
    L.append("")
    for line in _conclusions(eff_rich, eff_left, eff_gini, gap):
        L.append(f"- {line}")
    L.append("")

    # Bias controls / limitations.
    L.append("## Limitations and bias controls")
    L.append("")
    L.append("- **Conditional, not empirical.** Results follow from the calibrated "
             "micro-rules; a different calibration could move them. Treat as "
             "*if-then*, per `experiments/README.md`.")
    L.append("- **Two outcomes reported, not one.** Leaving poverty and becoming rich "
             "are distinct events and are scored separately so neither hides the other.")
    L.append("- **Balanced design + marginal means.** Every cell is equally sampled and "
             "main effects average over all other factors, so no single combination "
             "drives a headline.")
    L.append("- **Uncertainty retained.** Per-cell across-seed standard deviations are in "
             "`summary.json`; small effects within that noise should not be over-read.")
    L.append("- **Effect sizes are level-dependent.** A lever's 'effect range' depends on "
             "the two/three levels chosen here; the levels are stated explicitly.")
    L.append("- **Presets are illustrative.** The `harsh/mixed/protective` regimes are "
             "stand-ins, not calibrated to any country; their gaps are directional.")
    L.append("- **Reproducible.** Same seeds, same code, same output. Re-run with more "
             "`--seeds`/`--ticks` to tighten the estimates.")
    L.append("")
    return "\n".join(L)


def _conclusions(eff_rich: dict, eff_left: dict, eff_gini: dict, gap: dict) -> list[str]:
    """Neutral, numeric conclusions derived from the effects (no narrative picking)."""
    out: list[str] = []
    bg = gap["grand_mean"]
    out.append(f"Starting position is a first-order driver: born-rich lives reach the rich "
               f"threshold {bg:+.3f} more often than born-poor lives under the same levers.")

    # Effort, on each outcome, with monotonicity.
    for label, eff in [("P(became rich)", eff_rich), ("P(left poverty)", eff_left)]:
        d = eff["factors"]["effort"]
        rng = d["effect_range"]
        direction = _direction(d["level_means"], FACTORS["effort"])
        if rng is not None and rng > 0.01:
            out.append(f"Effort raises {label} for the poor by {rng:+.3f} across the tested "
                       f"range and {direction}.")
        elif rng is not None and rng > -0.01:
            out.append(f"Effort's effect on {label} for the poor is small here "
                       f"({rng:+.3f}, within or near sampling noise).")
        else:
            out.append(f"Effort's net effect on {label} for the poor is negative here ({rng:+.3f}).")

    # Regime effect on the two outcomes.
    for label, eff in [("becoming rich", eff_rich), ("leaving poverty", eff_left)]:
        d = eff["factors"]["regime"]["level_means"]
        if all(d.get(r) is not None for r in FACTORS["regime"]):
            best = max(FACTORS["regime"], key=lambda r: d[r])
            worst = min(FACTORS["regime"], key=lambda r: d[r])
            spread = round(d[best] - d[worst], 4)
            out.append(f"Among the illustrative regimes, P({label} | born poor) is highest "
                       f"under `{best}` and lowest under `{worst}` (spread {spread:+.3f}).")

    # Opportunity and network main effects on becoming rich.
    for factor in ("opportunity", "network"):
        d = eff_rich["factors"][factor]["level_means"]
        on, off = d.get("True"), d.get("False")
        if on is not None and off is not None:
            delta = round(on - off, 4)
            verb = "raises" if delta > 0.01 else ("lowers" if delta < -0.01 else "barely changes")
            out.append(f"Turning the {factor} mechanism on {verb} P(became rich | born poor) "
                       f"by {delta:+.3f} on average.")

    # Inequality.
    gini_grand = eff_gini["grand_mean"]
    if gini_grand is not None:
        ranked = rank_drivers(eff_gini)
        if ranked:
            f0, r0 = ranked[0]
            out.append(f"Final-population inequality (Gini) averages {gini_grand:.3f}; among "
                       f"the levers, `{f0}` shifts it the most (range {r0:+.3f}).")
    return out


# --------------------------------------------------------------------------- #
# Plot
# --------------------------------------------------------------------------- #
def plot(records: list[dict]) -> str | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    eff_rich = main_effects(records, "poor_became_rich")
    inter = effort_by_regime(records, "poor_became_rich")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: main-effect ranges (a tornado of lever magnitudes).
    drivers = rank_drivers(eff_rich)[::-1]
    names = [d[0] for d in drivers]
    ranges = [d[1] for d in drivers]
    ax1.barh(names, ranges, color="#4C72B0")
    ax1.set_title("Main-effect range on P(became rich | born poor)")
    ax1.set_xlabel("max - min marginal mean")
    ax1.axvline(0, color="#888", lw=1)

    # Right: effort x regime interaction.
    efforts = FACTORS["effort"]
    for regime, row in inter.items():
        ax2.plot(efforts, [row[str(e)] for e in efforts], marker="o", label=regime)
    ax2.set_title("Effort x regime: P(became rich | born poor)")
    ax2.set_xlabel("effort"); ax2.set_ylabel("probability")
    ax2.set_ylim(0, 1); ax2.legend(title="regime")

    fig.tight_layout()
    dest = RESULTS / "mobility_drivers.png"
    fig.savefig(dest, dpi=150)
    return str(dest)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticks", type=int, default=5000, help="steps per run (default 5000)")
    ap.add_argument("--seeds", type=int, default=4, help="seeds averaged per cell (default 4)")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    n_cells = int(np.prod([len(v) for v in FACTORS.values()]))
    print(f"Running {n_cells} cells x {args.seeds} seeds x {args.ticks} ticks "
          f"= {n_cells * args.seeds} simulations...\n")

    records = run_design(args.ticks, args.seeds)

    cfg = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "ticks": args.ticks,
        "seeds": args.seeds,
        "n_cells": n_cells,
        "n_agents": ModelParams().n_agents,
        "factors": FACTORS,
    }

    summary = {
        "config": cfg,
        "records": records,
        "main_effects": {k: main_effects(records, k) for k in OUTCOMES},
        "effort_by_regime_became_rich": effort_by_regime(records, "poor_became_rich"),
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    findings = write_findings(records, cfg)
    (RESULTS / "findings.md").write_text(findings, encoding="utf-8")

    png = plot(records)

    print("\n=== Findings written ===")
    print(f"  {RESULTS / 'findings.md'}")
    print(f"  {RESULTS / 'summary.json'}")
    print(f"  {png}" if png else "  (install matplotlib for the plot)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
