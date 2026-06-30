#!/usr/bin/env python3
"""Experiment: is the calibrated default model in a realistic regime?

This is a *validation* experiment, not a single-mechanism probe. It runs the full
canonical model at its calibrated defaults and checks the headline outcomes
against target ranges taken from the literature the model cites. The point is to
make "the model is calibrated" an auditable claim instead of an assertion: re-run
it after any parameter change and the card tells you whether the model is still in
a realistic regime.

What it measures (born-poor unless noted), averaged over seeds, at three effort
levels, for the canonical pipeline (inheritance + opportunity + network on):

  * P(reached the rich threshold)            - lifetime probability of reaching the top
  * P(reached rich | whole population)       - the same, pooled over birth classes
  * time_above_line (durable escape)         - average share of a life above the line
  * P(ever left poverty)                     - first-passage (transient) crossing
  * IGE                                       - intergenerational elasticity (Great Gatsby)
  * the living wealth-band distribution       - is the mass bottom/middle-heavy?

Targets (and why):
  * Reaching the top is rare, not typical. A bounded drift-diffusion with upward
    drift makes "rich" trivially reachable; a realistic process keeps it a thin
    tail. Target: P(rich | population) is single-digit, not a majority.
  * IGE in roughly [0.3, 0.6] - the Great Gatsby range (Corak 2013; OECD 2018:
    ~5-6 generations to the mean).
  * Durable escape is more common than getting rich, and both are far below 1 -
    "leaving poverty != becoming rich" should show as a large gap.
  * The standing distribution is bottom/middle-heavy (most below the acomodado
    band), not piled just under the rich line.

These are illustrative targets, not a fit to any specific country.

Run:
    python experiments/calibration/run.py
    python experiments/calibration/run.py --ticks 30000 --seeds 5
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from simulation.builder import build_simulation  # noqa: E402
from simulation.core.bands import band_shares  # noqa: E402
from simulation.core.config import ModelParams  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

EFFORTS = [0.0, 0.5, 1.0]


def run_point(effort: float, ticks: int, seeds: int) -> dict:
    """Average the calibration metrics over ``seeds`` at one effort level."""
    acc: dict[str, list[float]] = {k: [] for k in
        ["poor_rich", "rich_rich", "global_rich", "poor_time_above", "poor_left", "ige"]}
    dist: list[list[float]] = []
    for seed in range(seeds):
        sim = build_simulation(seed=seed, effort=effort, generational=True,
                               with_opportunity=True, with_network=True)
        fp = next(p for p in sim.population_processes if type(p).__name__ == "FirstPassageMonitor")
        for _ in range(ticks):
            sim.step()
        r = fp.report()
        p, ri = r["poor"], r["rich"]
        n = p["attempts"] + ri["attempts"]
        acc["poor_rich"].append(p["became_rich"])
        acc["rich_rich"].append(ri["became_rich"])
        acc["global_rich"].append((p["became_rich"] * p["attempts"] + ri["became_rich"] * ri["attempts"]) / max(n, 1))
        acc["poor_time_above"].append(p["time_above_line"])
        acc["poor_left"].append(p["left_poverty"])
        if r["ige"] is not None:
            acc["ige"].append(r["ige"])
        bs = band_shares(sim.state.wealth, sim.params)
        dist.append([bs[k] for k in ("pobreza", "vulnerable", "media", "acomodado", "rico")])
    out: dict = {k: round(float(np.mean(v)), 4) if v else None for k, v in acc.items()}
    out["dist"] = {k: round(float(x), 4) for k, x in
                   zip(("pobreza", "vulnerable", "media", "acomodado", "rico"), np.mean(dist, axis=0))}
    out["effort"] = effort
    return out


def evaluate(points: dict[float, dict]) -> list[dict]:
    """Score the calibrated model against the realistic-regime targets."""
    mid = points[0.5]
    lo, hi = points[0.0], points[1.0]
    bottom_mid = mid["dist"]["pobreza"] + mid["dist"]["vulnerable"] + mid["dist"]["media"]
    checks = [
        {"metric": "P(rich | population), effort 0.5", "value": mid["global_rich"],
         "target": "<= 0.15 (reaching the top is rare)", "ok": mid["global_rich"] <= 0.15},
        {"metric": "P(rich | born poor), effort 0.5", "value": mid["poor_rich"],
         "target": "<= 0.10", "ok": mid["poor_rich"] <= 0.10},
        {"metric": "IGE (effort 0.5)", "value": mid["ige"],
         "target": "0.3 - 0.6 (Great Gatsby)", "ok": mid["ige"] is not None and 0.2 <= mid["ige"] <= 0.7},
        {"metric": "durable escape > getting rich (born poor)", "value": f"{mid['poor_time_above']} vs {mid['poor_rich']}",
         "target": "time_above_line >= 2x P(rich)", "ok": mid["poor_time_above"] >= 2 * mid["poor_rich"]},
        {"metric": "distribution bottom/middle-heavy (effort 0.5)", "value": round(bottom_mid, 4),
         "target": ">= 0.65 below the acomodado band", "ok": bottom_mid >= 0.65},
        {"metric": "effort raises P(rich | born poor)", "value": f"{lo['poor_rich']} -> {hi['poor_rich']}",
         "target": "monotone non-decreasing", "ok": hi["poor_rich"] >= lo["poor_rich"] - 1e-9},
    ]
    return checks


def write_findings(points: dict[float, dict], checks: list[dict], cfg: dict) -> str:
    L = ["# Calibration card: is the model in a realistic regime?", ""]
    L.append(f"*Generated {cfg['timestamp']} by `experiments/calibration/run.py` "
             f"({cfg['seeds']} seeds x {cfg['ticks']} ticks).*")
    L.append("")
    L.append("> Conditional result: these are the calibrated **defaults** of the model "
             "checked against illustrative targets from the cited literature, not a fit "
             "to any specific country. See `docs/literature/calibration.md`.")
    L.append("")
    L.append("## Checks")
    L.append("")
    L.append("| check | value | target | status |")
    L.append("|-------|-------|--------|--------|")
    for c in checks:
        L.append(f"| {c['metric']} | {c['value']} | {c['target']} | {'OK' if c['ok'] else 'OFF'} |")
    npass = sum(1 for c in checks if c["ok"])
    L.append("")
    L.append(f"**{npass}/{len(checks)} checks in range.**")
    L.append("")
    L.append("## Outcomes by effort (born poor, averaged over seeds)")
    L.append("")
    L.append("| effort | P(rich) | P(rich, pop) | time fuera | cruzo linea | IGE | dist pob/vul/med/aco/ric |")
    L.append("|--------|---------|--------------|-----------|-------------|-----|--------------------------|")
    for e in EFFORTS:
        pt = points[e]
        d = pt["dist"]
        dist = "/".join(f"{d[k]*100:.0f}" for k in ("pobreza", "vulnerable", "media", "acomodado", "rico"))
        ige = f"{pt['ige']:.2f}" if pt["ige"] is not None else "-"
        L.append(f"| {e} | {pt['poor_rich']*100:.1f}% | {pt['global_rich']*100:.1f}% | "
                 f"{pt['poor_time_above']*100:.0f}% | {pt['poor_left']*100:.0f}% | {ige} | {dist} |")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticks", type=int, default=25000, help="steps per run (default 25000)")
    ap.add_argument("--seeds", type=int, default=4, help="seeds averaged per point (default 4)")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    print(f"Calibration check: {args.seeds} seeds x {args.ticks} ticks at efforts {EFFORTS}...\n")
    points = {e: run_point(e, args.ticks, args.seeds) for e in EFFORTS}
    for e in EFFORTS:
        pt = points[e]
        print(f"  effort {e}: P(rich) pobre={pt['poor_rich']*100:4.1f}% global={pt['global_rich']*100:4.1f}% "
              f"| t_fuera={pt['poor_time_above']*100:3.0f}% | IGE={pt['ige']}")

    checks = evaluate(points)
    cfg = {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "ticks": args.ticks, "seeds": args.seeds,
           "defaults": {f: getattr(ModelParams(), f) for f in
                        ("start_poor", "start_rich", "poverty_line", "band_vulnerable", "band_acomodado",
                         "rich_threshold", "mu_base_poor", "mu_base_rich", "alpha", "r", "r_wealth_slope",
                         "kappa", "inherit_fraction", "talent_heritability")}}
    (RESULTS / "calibration.json").write_text(
        json.dumps({"config": cfg, "points": points, "checks": checks}, indent=2), encoding="utf-8")
    (RESULTS / "findings.md").write_text(write_findings(points, checks, cfg), encoding="utf-8")

    print("\n=== Calibration checks ===")
    for c in checks:
        print(f"  [{'OK ' if c['ok'] else 'OFF'}] {c['metric']}: {c['value']}  (target {c['target']})")
    print(f"\nSaved: {RESULTS / 'findings.md'} and {RESULTS / 'calibration.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
