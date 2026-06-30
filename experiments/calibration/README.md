# calibration

**Question it adjudicates:** is the model's **calibrated default regime realistic** -
i.e. is reaching the top a rare tail event, is intergenerational persistence in the
Great Gatsby range, and is durable escape from poverty distinct from (and more
common than) becoming rich?

This is a **validation card**, not a single-mechanism probe. It runs the full
canonical model at its defaults and checks the headline outcomes against target
ranges drawn from the literature the model cites. Re-run it after any parameter
change to confirm the model is still in a realistic regime.

## Why this experiment exists

An earlier (illustrative) calibration produced an unrealistic regime: a majority of
all lives reached the "rich" band and the IGE was far above 1. The defaults were
re-calibrated so that the wealth process is near-mean-reverting with a heavy-tailed
upside, making the top a rare destination. This experiment pins that result down as
an auditable check.

## What it measures (born poor unless noted, averaged over seeds, at three efforts)

| metric | meaning |
|--------|---------|
| `P(rich)` | lifetime probability of reaching the rich threshold |
| `P(rich, population)` | the same, pooled over born-poor and born-rich |
| `time_above_line` | average share of a life spent at/above the poverty line (durable escape) |
| `left_poverty` | first-passage: ever crossed the line (transient) |
| `IGE` | intergenerational elasticity (log child vs log parent wealth) |
| band distribution | the living population's share in each wealth band |

## Targets (illustrative, from the cited literature)

- **Reaching the top is rare:** `P(rich | population)` single-digit, not a majority.
  A bounded process with upward drift makes the top trivially reachable; a realistic
  one keeps it a thin tail.
- **IGE ~ 0.3 - 0.6:** the Great Gatsby range (Corak 2013; OECD 2018, ~5-6
  generations to the mean).
- **Durable escape > getting rich:** `time_above_line >= 2x P(rich)`, and both well
  below 1 - the "leaving poverty != becoming rich" gap.
- **Bottom/middle-heavy distribution:** most of the living mass below the *acomodado*
  band, not piled just under the rich line.

These are illustrative targets, not a fit to any specific country. See
[`../../docs/literature/calibration.md`](../../docs/literature/calibration.md).

## Run

```bash
python experiments/calibration/run.py                 # default: 4 seeds x 25000 ticks
python experiments/calibration/run.py --ticks 30000 --seeds 6
```

## Output (written to `results/`)

- **`findings.md`** - the calibration card: each check with its value, target, and
  OK/OFF status, plus the outcomes-by-effort table and the band distribution.
- **`calibration.json`** - machine-readable checks, per-effort metrics, and the
  exact calibrated default parameters used.
