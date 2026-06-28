#!/usr/bin/env python3
"""Experiment: does effort (value creation) always raise the odds of escape?

We do NOT assume the answer. We sweep the effort level, measure the probability
that a poor-born life crosses the poverty line ("left poverty") and reaches the
rich threshold ("became rich"), and read off effort's marginal impact - the slope
dP/d(effort). We repeat under several structural conditions so the model itself
tells us whether the impact is always positive, how large it is, and how it
varies with circumstance.

Crucially, one condition removes the effort-efficiency FLOOR (eta_min = 0). The
"effort always helps" property is mathematically guaranteed only while that floor
is positive; this condition exposes whether the property is a finding or an
artifact of that calibration choice. The floor itself is motivated in
docs/literature/calibration.md section 4 (Mani 2013: scarcity degrades but does
not eliminate cognitive capacity).

Channel isolation: opportunity and network are turned OFF so we measure the pure
value-creation drift term alpha * e * eta * q, which is what the hypothesis is
about. Each life is a single first-passage attempt (no inheritance).

Run:
    python experiments/effort-marginal-impact/run.py
    python experiments/effort-marginal-impact/run.py --ticks 12000 --seeds 5 --steps 11
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Bootstrap src/ onto the path so no install is required.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from poverty_trap.builder import build_simulation  # noqa: E402
from poverty_trap.core.config import ModelParams  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def conditions() -> dict[str, ModelParams]:
    """The structural settings we compare. Each holds everything fixed except the
    stated change, so differences are attributable to that change."""
    base = ModelParams()
    return {
        # As calibrated (efficiency floor eta_min = 0.30).
        "baseline": base,
        # A deeper trap: more negative neighbourhood drift, larger premium and shocks.
        "harsh_structure": base.evolve(mu_base_poor=-0.020, premium=0.008, sigma_poor=0.25),
        # The honesty probe: let effort efficiency collapse to zero when deeply poor.
        "no_efficiency_floor": base.evolve(eta_min=0.0),
    }


def escape_rates(params: ModelParams, effort: float, *, ticks: int, seeds: int) -> tuple[float, float]:
    """Average poor-born (became_rich, left_poverty) over ``seeds`` runs.

    Opportunity and network are off and lives do not inherit, so this isolates the
    value-creation drift channel.
    """
    rich, left = [], []
    for seed in range(seeds):
        sim = build_simulation(
            params,
            seed=seed,
            effort=effort,
            generational=False,
            with_opportunity=False,
            with_network=False,
        )
        rep = sim.run(ticks).reports["FirstPassageMonitor"]["poor"]
        rich.append(rep["became_rich"])
        left.append(rep["left_poverty"])
    return float(np.mean(rich)), float(np.mean(left))


def marginal(efforts: list[float], probs: list[float]) -> list[float]:
    """Central-difference slope dP/d(effort); a measure of effort's local impact."""
    e = np.asarray(efforts)
    p = np.asarray(probs)
    return np.gradient(p, e).tolist()


def run(ticks: int, seeds: int, steps: int) -> dict:
    efforts = [round(i / (steps - 1), 4) for i in range(steps)]
    out: dict[str, dict] = {"efforts": efforts, "conditions": {}}
    for name, params in conditions().items():
        became_rich, left_poverty = [], []
        for e in efforts:
            r, l = escape_rates(params, e, ticks=ticks, seeds=seeds)
            became_rich.append(round(r, 4))
            left_poverty.append(round(l, 4))
            print(f"  {name:>20} | effort={e:.2f} | became_rich={r:.3f} left_poverty={l:.3f}")
        slope_rich = marginal(efforts, became_rich)
        out["conditions"][name] = {
            "became_rich": became_rich,
            "left_poverty": left_poverty,
            "marginal_impact_became_rich": [round(s, 4) for s in slope_rich],
            "min_marginal_impact": round(float(np.min(slope_rich)), 5),
            "monotonic_non_decreasing": bool(np.all(np.diff(became_rich) >= -1e-9)),
        }
    return out


def verdict(out: dict) -> list[str]:
    """Turn the numbers into plain statements the experiment demonstrates.

    Headline metrics are robust to sampling noise: the total lift in P(rich) from
    zero to full effort, whether the rise is monotone, and the ceiling (does it
    ever reach 1, i.e. a guarantee). Local slopes are noisy at low seed counts, so
    they inform but do not drive the wording.
    """
    lines = []
    for name, c in out["conditions"].items():
        br = c["became_rich"]
        p0, p1 = br[0], br[-1]
        lift = round(p1 - p0, 4)
        mono = c["monotonic_non_decreasing"]
        ceiling = max(br)
        if mono and lift > 0.01:
            char = (f"effort always helps: P(rich) rises monotonically by {lift:+.3f} "
                    f"({p0:.2f} -> {p1:.2f})")
        elif lift > 0.01:
            char = (f"effort helps on net (+{lift:.3f}) but NOT monotonically - a near-flat / "
                    f"dead region appears, so 'always strictly positive' is not clean here")
        elif lift > -0.01:
            char = f"effort barely moves the outcome (lift {lift:+.3f}, within noise) - impact ~0"
        else:
            char = f"effort's net impact is NEGATIVE ({lift:+.3f})"
        guarantee = "never reaches a guarantee" if ceiling < 0.95 else "approaches a guarantee"
        lines.append(f"- {name}: {char}; ceiling P(rich)={ceiling:.2f} ({guarantee}).")
    return lines


def plot(out: dict) -> str | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    e = out["efforts"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    for name, c in out["conditions"].items():
        ax1.plot(e, c["became_rich"], marker="o", label=name)
        ax2.plot(e, c["marginal_impact_became_rich"], marker="o", label=name)
    ax1.set_title("P(became rich | born poor) vs effort")
    ax1.set_xlabel("effort"); ax1.set_ylabel("probability"); ax1.set_ylim(0, 1); ax1.legend()
    ax2.axhline(0.0, color="#888", ls="--", lw=1)
    ax2.set_title("Marginal impact of effort  dP/d(effort)")
    ax2.set_xlabel("effort"); ax2.set_ylabel("slope"); ax2.legend()
    fig.tight_layout()
    dest = RESULTS / "effort_impact.png"
    fig.savefig(dest, dpi=150)
    return str(dest)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticks", type=int, default=6000, help="steps per run (default 6000)")
    ap.add_argument("--seeds", type=int, default=3, help="runs to average per point (default 3)")
    ap.add_argument("--steps", type=int, default=11, help="effort levels from 0 to 1 (default 11)")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    print(f"Sweeping effort ({args.steps} levels), {args.seeds} seeds, {args.ticks} ticks per run...\n")
    out = run(args.ticks, args.seeds, args.steps)

    lines = verdict(out)
    out["verdict"] = lines
    (RESULTS / "summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    png = plot(out)

    print("\n=== What the simulation demonstrates ===")
    for line in lines:
        print(line)
    print(f"\nSaved: {RESULTS / 'summary.json'}" + (f" and {png}" if png else " (install matplotlib for the plot)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
