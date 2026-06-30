"""Command-line interface: run a simulation or sweep effort, print metrics as JSON.

Examples
--------
Run the full model once at 50% effort::

    poverty-trap run --effort 0.5 --ticks 20000

Sweep effort and print the two mobility probabilities at each level::

    poverty-trap sweep --ticks 20000

Compare regimes on the same seed::

    poverty-trap regime --name protective --effort 0.5
"""

from __future__ import annotations

import argparse
import json
import sys

from .builder import build_simulation
from .core.config import ModelParams
from .regimes.presets import get_preset


def _run_once(params: ModelParams, *, seed: int, effort: float, ticks: int,
              generational: bool, opportunity: bool, network: bool) -> dict:
    sim = build_simulation(
        params,
        seed=seed,
        effort=effort,
        generational=generational,
        with_opportunity=opportunity,
        with_network=network,
    )
    result = sim.run(ticks)
    fp = result.reports.get("FirstPassageMonitor", {})
    pm = result.reports.get("PopulationMetrics", {})
    return {
        "effort": effort,
        "mobility": fp,
        "gini": pm.get("gini") if isinstance(pm, dict) else None,
        "band_shares": pm.get("band_shares") if isinstance(pm, dict) else None,
    }


def _add_common(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--ticks", type=int, default=20000, help="number of steps to run")
    ap.add_argument("--seed", type=int, default=0, help="RNG seed (reproducibility)")
    ap.add_argument("--no-generational", action="store_true", help="restart fresh instead of inheriting")
    ap.add_argument("--no-opportunity", action="store_true", help="disable the opportunity process")
    ap.add_argument("--no-network", action="store_true", help="disable the social network")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="poverty-trap", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run a single simulation")
    p_run.add_argument("--effort", type=float, default=0.0, help="effort level in [0, 1]")
    _add_common(p_run)

    p_sweep = sub.add_parser("sweep", help="sweep effort from 0 to 1")
    p_sweep.add_argument("--steps", type=int, default=11, help="number of effort levels")
    _add_common(p_sweep)

    p_reg = sub.add_parser("regime", help="run a named regime preset")
    p_reg.add_argument("--name", required=True, help="preset name (harsh/mixed/protective)")
    p_reg.add_argument("--effort", type=float, default=0.5, help="effort level in [0, 1]")
    _add_common(p_reg)

    args = parser.parse_args(argv)
    common = dict(
        seed=args.seed,
        ticks=args.ticks,
        generational=not args.no_generational,
        opportunity=not args.no_opportunity,
        network=not args.no_network,
    )

    if args.command == "run":
        out = _run_once(ModelParams(), effort=args.effort, **common)
        print(json.dumps(out, indent=2))
    elif args.command == "sweep":
        rows = []
        for i in range(args.steps):
            effort = i / (args.steps - 1) if args.steps > 1 else 0.0
            rows.append(_run_once(ModelParams(), effort=effort, **common))
        print(json.dumps(rows, indent=2))
    elif args.command == "regime":
        params = get_preset(args.name)
        out = _run_once(params, effort=args.effort, **common)
        out["regime"] = args.name
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
