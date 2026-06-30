# poverty-trap

An agent-based simulation engine for the dynamics of poverty traps: how
structure, effort, opportunity, social networks, and inheritance combine to
decide who escapes poverty and who does not.

It started as a one-minute video ("are poor people poor because they want to
be?") and grew, with a lot of thoughtful audience feedback, into a proper,
extensible model grounded in published research.

## The thesis (two truths at once)

1. **The trap is real.** Where you are born sets your starting point and the
   direction you drift. Shocks hit the poor harder, and below a critical
   threshold you slide down rather than up.
2. **Effort is the lever you control, and it has non-linear leverage** - but it
   is not a guarantee, and it does not erase structure. The model keeps both
   truths honest, and (per the audience) separates *leaving poverty* from
   *becoming rich*: two different events with two different probabilities.

The full model, math, and the analysis of the community feedback that shaped it
are in **[`docs/README.md`](docs/README.md)**.

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/diet-krause/poverty-trap
cd poverty-trap
pip install -e .            # add ".[dev,viz]" for tests, lint, and plotting
```

## Quickstart

Command line:

```bash
# one run at 50% effort
poverty-trap run --effort 0.5 --ticks 20000

# sweep effort from 0 to 1 and print the two mobility probabilities
poverty-trap sweep --steps 11 --ticks 20000

# run an (illustrative) policy regime on the same seed
poverty-trap regime --name protective --effort 0.5
```

Python:

```python
from simulation.builder import build_simulation

sim = build_simulation(seed=0, effort=0.5, generational=True)
result = sim.run(20000)
print(result.reports["FirstPassageMonitor"])  # left-poverty vs became-rich, by class
print(result.reports["PopulationMetrics"])     # Gini, band shares, wealth gap
```

## Usage

This section is the end-to-end guide: how to run a simulation, what numbers come
back, how to read them, and how to chain parameters to ask different questions.
The `poverty-trap` command is installed by `pip install -e .`. If you have not
installed it, every command also works as `python -m simulation.cli ...` (from
the repo root, with `src` on `PYTHONPATH`).

### 1. Run one simulation

```bash
poverty-trap run --effort 0.5 --ticks 20000
```

A run simulates a population of agents (default 240) for `--ticks` steps. Lives
resolve when they reach the rich threshold, hit ruin, or age out, and are then
respawned (by default as their *children*, carrying inheritance). The command
prints a JSON report:

```json
{
  "effort": 0.5,
  "mobility": {
    "birth_policy": "generational_transmission",
    "poor": { "attempts": 6758, "became_rich": 0.3711, "left_poverty": 0.6761 },
    "rich": { "attempts": 8120, "became_rich": 0.9999, "left_poverty": 1.0 },
    "ige": 3.49
  },
  "gini": 0.236,
  "band_shares": {
    "pobreza": 0.1042, "vulnerable": 0.1792, "media": 0.2625,
    "acomodado": 0.4542, "rico": 0.0
  }
}
```

### 2. How to read the results

This is the important part - the model deliberately reports **two different
mobility events**, not one "success rate".

- **`mobility.poor` vs `mobility.rich`** - outcomes split by where the agent was
  *born* (the poor zone vs the rich zone). The gap between these two blocks *is*
  the poverty trap: same rules, different starting line.
- **`became_rich`** - probability a life reached the rich threshold `w*`
  (`rich_threshold`, default `1.0`). This is "became rich".
- **`left_poverty`** - probability a life *ever* crossed the poverty line `w_p`
  (`poverty_line`, default `0.20`) upward at least once. This is "escaped
  poverty" and is a **strictly easier, distinct event** - which is why
  `left_poverty` is always >= `became_rich`. Separating these two answers the #1
  audience critique: *leaving poverty is not the same as getting rich.*
- **`attempts`** - how many lives resolved in that group over the run (more ticks
  -> more attempts -> tighter probability estimates).
- **`ige`** - intergenerational elasticity: the slope of `log(child wealth)` vs
  `log(parent wealth)`. Higher = more inherited advantage = *less* mobility (the
  Great Gatsby axis). It needs >= 50 parent-child pairs or it returns `null`; on
  short runs it is noisy (and can even go negative), so trust it only on long,
  generational runs.
- **`gini`** - inequality of the living population at the final snapshot
  (`0` = everyone equal, `1` = maximally unequal).
- **`band_shares`** - the *continuum*: the fraction of the living population in
  each wealth band (`pobreza` < `vulnerable` < `media` < `acomodado` < `rico`).
  `rico` is typically ~`0` because reaching the rich threshold **resolves** a
  life (it respawns), so the snapshot shows the living distribution *below* the
  finish line, not a pile-up at it.

Reading the two examples together: at **effort 0.0** the poor become rich ~17% of
the time; at **effort 0.5** that jumps to ~37%, while the born-rich stay at
~98-100%. Effort moves the poor a lot and the rich barely at all - effort is a
real lever, but it does not erase the structural head start.

### 3. Chaining parameters to ask different questions

The CLI flags compose. Each flag isolates one mechanism so you can attribute a
change in the numbers to a specific cause.

**Common flags** (work on `run`, `sweep`, and `regime`):

| Flag | Effect |
|------|--------|
| `--effort FLOAT` | effort level in `[0, 1]` applied to everyone |
| `--ticks INT` | number of steps (more = more attempts = tighter estimates) |
| `--seed INT` | RNG seed; **fix it to compare scenarios on the same agents** |
| `--no-generational` | respawn fresh instead of inheriting (turns off the trap's memory) |
| `--no-opportunity` | disable the heavy-tailed opportunity (luck) process |
| `--no-network` | disable social network, peer spillover, and pooling |

**Isolate effort's marginal impact** (same seed, only effort changes):

```bash
poverty-trap run --effort 0.0 --seed 0 --ticks 40000
poverty-trap run --effort 0.5 --seed 0 --ticks 40000
poverty-trap run --effort 1.0 --seed 0 --ticks 40000
# compare mobility.poor.became_rich across the three
```

**Sweep effort automatically** from 0 to 1 and print the two probabilities at
each level (this is the data behind the "effort curve"):

```bash
poverty-trap sweep --steps 11 --ticks 20000        # 0.0, 0.1, ... 1.0
```

**Measure what one mechanism contributes** by toggling it off and diffing:

```bash
poverty-trap run --effort 0.5 --seed 0                     # full model
poverty-trap run --effort 0.5 --seed 0 --no-opportunity    # remove luck
poverty-trap run --effort 0.5 --seed 0 --no-network        # remove networks
# the drop in mobility.poor is that mechanism's contribution
```

**Compare policy regimes on the *same* agents** (the honest country comparison -
identical seed, different structural dials):

```bash
poverty-trap regime --name harsh      --effort 0.5 --seed 0
poverty-trap regime --name mixed      --effort 0.5 --seed 0
poverty-trap regime --name protective --effort 0.5 --seed 0
```

`protective` adds a welfare floor, redistribution, and an education head-start;
`harsh` has a steep poverty premium and concentrated opportunity. Watch
`mobility.poor.left_poverty` and `gini` move while the rich stay roughly fixed.
These presets are **illustrative, not calibrated** to any real country.

### 4. The Python API (full control)

The CLI exposes the common knobs; the Python API exposes *every* parameter via
the immutable `ModelParams` dataclass. Derive a variant with `.evolve(...)` and
pass it to `build_simulation`:

```python
from simulation.builder import build_simulation
from simulation.core.config import ModelParams

# A custom regime: gentle welfare floor + lighter shocks for the poor.
params = ModelParams().evolve(welfare_floor=0.05, sigma_poor=0.15, premium=0.002)

sim = build_simulation(
    params,
    seed=0,
    effort=0.5,
    generational=True,      # children inherit (set False to break the trap's memory)
    with_opportunity=True,  # heavy-tailed "luck" process
    with_network=True,      # social network + peer spillover + pooling
)
result = sim.run(20000)

mob = result.reports["first_passage"]
print(mob["poor"]["became_rich"], mob["poor"]["left_poverty"], mob["ige"])
print(result.reports["PopulationMetrics"]["gini"])
```

`build_simulation` also accepts a custom `EffortPolicy` instead of a scalar
(e.g. to give effort a distribution across agents rather than one global value),
plus `lifespan_ticks` (how long before an unresolved life ages out) and
`metrics_every` (snapshot cadence). Every numeric parameter, its meaning, and its
default live in `src/simulation/core/config.py` and are documented in
`docs/README.md` section 7.

### 5. Let the simulation adjudicate (experiments)

For questions that deserve a controlled answer over many seeds, use the
[`experiments/`](experiments/) framework instead of a single run - it sweeps a
variable, averages over seeds, and writes a `summary.json` plus a plot:

```bash
python experiments/effort-marginal-impact/run.py
```

## How it is built

The engine is a small, composable core that runs an ordered pipeline of
single-responsibility components each tick (drift terms, noise, events,
population processes, observers). New mechanisms are added as new components, not
by editing the engine. It is vectorised with NumPy (thousands of agents),
deterministic from a seed, and documented in-code. See
**[`docs/design/architecture.md`](docs/design/architecture.md)**.

```
src/simulation/
  core/         engine, state, config, protocols, bands, context
  dynamics/     drift & noise: neighbourhood, premium, value creation, capital, diffusion, effort
  events/       opportunity (marked Poisson / Pareto)
  population/   skill growth, social network, regime policy, generational lifecycle
  observe/      metrics (Gini, bands, wealth gap)
  regimes/      illustrative policy presets
  builder.py    wires the canonical pipeline
  cli.py        command-line interface
```

## Documentation

- [`docs/README.md`](docs/README.md) - the model: thesis, full math (sections
  7.1-7.13), the interface plan, and the roadmap.
- [`docs/design/architecture.md`](docs/design/architecture.md) - how the engine
  works and how to extend it.
- [`docs/literature/`](docs/literature/) - the research the model rests on, with
  one note per paper. (Paper PDFs are not redistributed here; a fetch/convert
  workflow downloads and converts them locally for study.)

## Experiments

The [`experiments/`](experiments/) folder is where the simulation **adjudicates**
questions instead of where we assert answers. Each experiment is a self-contained
subfolder that sweeps a variable, averages over seeds, and reports what the model
produces. The first one,
[`effort-marginal-impact/`](experiments/effort-marginal-impact/), measures
whether effort (value creation) always raises the probability of escape, by how
much, and how that impact varies with structural position - including a condition
that removes the efficiency floor, so the "effort always helps" property is
*measured*, not built in.

```bash
python experiments/effort-marginal-impact/run.py
```

## Roadmap

The model is built to grow one mechanism at a time. The next steps (each a
self-contained extension) are the continuum/middle-class reporting, generational
calibration to real mobility data, effort efficiency, talent-vs-luck, social
networks, and policy regimes. Details in `docs/README.md` sections 4 and 8.

## Status

Alpha. The defaults are illustrative, not calibrated estimates of any country.
Only the parameters noted in `docs/README.md` should be tuned to real targets
(IGE, generations-to-mean, escape rates); the rest are structural and fixed.

## Contributing

Issues and pull requests are welcome. Please read
[`CONTRIBUTING.md`](CONTRIBUTING.md) - it covers the dev setup, the "add a
component, not an edit" extension pattern, coding standards, and the literature
policy. Contributors are listed in [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

## License

[MIT](LICENSE) (c) 2026 Dietmar Luther Krause Gutierrez.

## Acknowledgements

The v2 research agenda came largely from the community that engaged with the
original video. Thank you - the analysis of that feedback is in `docs/README.md`.
