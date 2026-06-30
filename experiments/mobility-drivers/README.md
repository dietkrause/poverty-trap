# mobility-drivers

**Question it adjudicates:** Across the model's main levers - *starting position,
effort, policy regime, opportunity, and social networks* - which ones move the two
mobility outcomes, by how much, and do they interact? In particular: is effort's
payoff the same under every regime, or does structure change what effort buys?

This complements [`effort-marginal-impact/`](../effort-marginal-impact/): that one
sweeps effort in isolation; this one runs the **full canonical model** and lets
every lever vary at once, so we can compare levers on the same footing and detect
interactions.

## Method

A **balanced full-factorial** experiment. Every combination of four factors is run
and averaged over the same set of seeds:

| factor | levels | what it is |
|--------|--------|------------|
| `regime` | harsh, mixed, protective | the structural / policy dial Theta (preset parameter sets) |
| `effort` | 0.0, 0.5, 1.0 | value-creation magnitude applied to everyone |
| `opportunity` | on, off | the heavy-tailed ("luck") arrival process |
| `network` | on, off | social ties, peer spillover, and collective pooling |

That is `3 x 3 x 2 x 2 = 36` cells. Inheritance (generational transmission) is left
**on** in every cell, so this is the canonical model and the IGE is meaningful.

For each cell we record, separately for born-poor and born-rich lives:

- `P(became rich)` - reached the rich threshold `w*`;
- `P(left poverty)` - ever crossed the poverty line `w_p` upward (a distinct,
  strictly easier event);
- the **born-rich minus born-poor** gap in `P(became rich)` (the structural baseline);
- the population Gini, and the IGE where enough parent-child pairs exist.

## How bias is controlled

This experiment is designed so the conclusions are not smuggled in:

- **Balanced design.** Every cell is run with the same seeds, so no combination is
  over-sampled.
- **Marginal means for main effects.** A factor's effect is the outcome averaged
  over *all* settings of the other factors. In a balanced design this is the
  standard, design-unbiased main-effect estimate; it does not depend on a
  hand-picked baseline.
- **Both outcomes reported.** "Left poverty" and "became rich" can diverge, so we
  never collapse them into one "success rate".
- **The structural baseline is shown explicitly**, so each lever is read relative
  to the birth-position gap rather than in a vacuum.
- **Conclusions are template-generated** from fixed numeric thresholds, not written
  by hand, and every one is phrased as conditional on the model's calibration.
- **Uncertainty is kept.** Per-cell across-seed standard deviations are written to
  `summary.json`.

What the experiment **cannot** do: prove anything about a real economy. Per
[`../README.md`](../README.md), an agent-based model demonstrates the consequences
of its micro-rules. The regime presets are illustrative, not calibrated countries.

## Run

```bash
python experiments/mobility-drivers/run.py                 # default: 36 cells x 4 seeds x 5000 ticks
python experiments/mobility-drivers/run.py --ticks 8000 --seeds 6   # tighter estimates
```

Plots need the optional viz extra: `pip install matplotlib`.

## Output (written to `results/`)

- **`findings.md`** - the auto-generated, neutral write-up: design, the structural
  baseline, main-effect tables for both outcomes, levers ranked by effect size, the
  effort x regime interaction, conclusions, and a limitations section.
- **`summary.json`** - everything machine-readable: every cell's mean and std for
  every metric, plus the computed main effects and the interaction table.
- **`mobility_drivers.png`** - two panels: a tornado of main-effect magnitudes on
  `P(became rich | born poor)`, and the effort x regime interaction curves.

## How to read the results

Start with `findings.md`. The headline comparisons are robust to seed noise: the
born-poor vs born-rich gap, the ranking of levers by effect size, and whether
effort's lift differs across regimes. Treat any effect smaller than the relevant
per-cell std (in `summary.json`) as "within noise". Because the levels are fixed
and stated, a lever's effect size is a statement about *those levels*, not a
universal elasticity - widen the levels or re-calibrate to ask a different question.
