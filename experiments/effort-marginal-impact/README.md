# Effort marginal impact

## The question

Does effort - in the sense of **value creation** - always raise the probability
of escaping poverty, by how much, and how does that impact vary with structural
position? And is the "effort always helps" property a genuine finding of the
model, or an artifact of one calibration choice (the effort-efficiency floor)?

This is deliberately framed as a measurement: the experiment reports what the
model produces; it does not assume the answer.

## Why this is not circular

In the value-creation drift term `alpha * e * eta(w, St) * q(h)`, the marginal
impact of effort is `alpha * eta * q`. That is strictly positive *only while* the
efficiency floor `eta_min > 0`. If we simply fix `eta_min = 0.30` and then
"discover" effort always helps, we have proven nothing - we built the answer in.

So this experiment includes a condition with `eta_min = 0` (no floor) to expose
whether, and where, effort's impact can vanish. The floor used in the baseline is
itself motivated empirically (Mani 2013: extreme scarcity reduces cognitive
function by ~13 IQ points but does **not** eliminate it), as recorded in
[`../../docs/literature/calibration.md`](../../docs/literature/calibration.md)
section 4.

## Method

- **Channel isolated.** Opportunity and network are off, lives do not inherit, so
  we measure the pure value-creation channel as a single first-passage attempt.
- **Sweep.** Effort from 0 to 1; for each level we average the poor-born
  probabilities of *leaving poverty* (crossing `w_p`) and *becoming rich*
  (reaching `w*`) over several random seeds.
- **Impact.** We compute the local slope `dP/d(effort)` by central differences -
  this is "the impact effort has", the thing your hypothesis says varies.
- **Conditions.** `baseline` (as calibrated), `harsh_structure` (deeper trap:
  more negative neighbourhood drift, larger premium and shocks), and
  `no_efficiency_floor` (`eta_min = 0`).

## Run it

```bash
python experiments/effort-marginal-impact/run.py
# scale up for smoother curves:
python experiments/effort-marginal-impact/run.py --ticks 12000 --seeds 5 --steps 11
pip install matplotlib   # optional, for the plot
```

Outputs land in `results/` (git-ignored): `summary.json` and, if matplotlib is
installed, `effort_impact.png` (left: P(became rich) vs effort; right: the
marginal impact `dP/d(effort)`).

## How to read it

- **P(became rich) vs effort** should be increasing but stay below 1 (effort
  raises the odds, never guarantees).
- **Marginal impact**: if it stays strictly above 0 across the sweep, effort
  always helps under that condition; where it sits near 0, effort barely moves
  the outcome (the trap dominates).
- **Compare conditions**: a smaller slope in `harsh_structure` than `baseline`
  demonstrates that the *magnitude* of effort's impact is set by structure. The
  `no_efficiency_floor` condition shows whether the "always positive" property
  survives without the assumed floor.

The script prints a one-line **verdict** per condition (monotone? smallest local
impact? always positive, vanishing, or negative?). That verdict is the result -
whatever it turns out to be.

## Caveat

This demonstrates the *consequence* of the calibrated micro-rules, not an
empirical law. Read it together with the calibration ledger: the result is only
as strong as the parameter values that feed it.
