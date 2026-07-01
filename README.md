# poverty-trap

An agent-based simulation engine for the dynamics of poverty traps: a model of how
starting position, effort, opportunity, social networks, and inheritance interact
to determine whether an agent leaves poverty.

The model reports two distinct mobility outcomes rather than a single "success
rate" — *leaving poverty* (crossing the poverty line) and *becoming rich*
(reaching the upper threshold) — and is calibrated so that reaching the top is a
rare tail event (see [Status](#status)). The full specification and mathematics
are in **[`docs/README.md`](docs/README.md)**; the supporting literature is in
**[`docs/literature/`](docs/literature/)**.

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/dietkrause/poverty-trap
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
    "poor": { "attempts": 7138, "became_rich": 0.049, "time_above_line": 0.272, "left_poverty": 0.477 },
    "rich": { "attempts": 5273, "became_rich": 0.078, "time_above_line": 0.602, "left_poverty": 0.944 },
    "ige": 0.59
  },
  "gini": 0.338,
  "band_shares": {
    "pobreza": 0.10, "vulnerable": 0.32, "media": 0.45,
    "acomodado": 0.13, "rico": 0.0
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
  (`rich_threshold`, default `1.0`). At the calibrated defaults this is a rare,
  tail event (a few percent), not a typical outcome.
- **`time_above_line`** - the *average share of a life* spent at or above the
  poverty line: a **durability** measure. A life that touched the line once by a
  lucky shock and fell back scores near `0`; one that genuinely lived out of
  poverty scores near `1`. This sits between `left_poverty` and `became_rich`.
- **`left_poverty`** - probability a life *ever* crossed the poverty line `w_p`
  (`poverty_line`, default `0.10`) upward at least once. This is the most
  generous "escaped" event (first passage, possibly transient), which is why
  `left_poverty` >= `time_above_line` >= `became_rich`. Reporting these as separate
  events reflects that leaving poverty and becoming rich are distinct outcomes with
  distinct probabilities.
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

Reading the calibrated numbers: a poor-born life **ever crosses** the poverty line
~48% of the time, but spends only ~27% of its life durably above it, and **reaches
the top just ~5%** of the time; born-rich reach the top ~8%. The model is
calibrated so that becoming rich is a rare tail event and escaping poverty is far
more common than getting rich - the realistic shape. Effort still shifts the poor's
odds upward, but it does not erase the structural head start. The calibration
targets and an auditable check live in
[`experiments/calibration/`](experiments/calibration/).

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

**Compare policy regimes on the *same* agents** (identical seed, different
structural parameters, so any difference is attributable to the regime):

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

mob = result.reports["FirstPassageMonitor"]
print(mob["poor"]["became_rich"], mob["poor"]["left_poverty"], mob["ige"])
print(result.reports["PopulationMetrics"]["gini"])
```

`build_simulation` also accepts a custom `EffortPolicy` instead of a scalar
(e.g. to give effort a distribution across agents rather than one global value),
plus `lifespan_ticks` (how long before an unresolved life ages out) and
`metrics_every` (snapshot cadence). Every numeric parameter, its meaning, and its
default live in `src/simulation/core/config.py` and are documented in
`docs/README.md` section 7.

### 5. Run controlled experiments

For questions that need a controlled answer over many seeds, use the
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

## Live visualization (the dashboard)

`src/ux/` is a live web dashboard that renders **every dynamic of the model** as
you steer it: the agent field (color = band, size = effort, opacity = the scarcity
tax η), the two mobility probabilities (left poverty vs became rich) with IGE, the
wealth-band continuum, the effort decomposition (η/q/savings, poor vs rich),
inequality over time (Gini + wealth gap), opportunity (heavy-tailed payoffs),
networks/pooling, and a talent-vs-luck scatter. A FastAPI WebSocket backend
streams frames from the engine (via the read-only `SnapshotEmitter`); nothing in
`src/simulation/` depends on the UI.

Two processes, from the repo root:

```bash
# 1) backend  (streams ws://localhost:8000/ws)
pip install -r src/ux/server/requirements.txt
python -m uvicorn app:app --app-dir src/ux/server

# 2) frontend (opens http://localhost:5173)
cd src/ux/web
npm install
npm run dev
```

Then open <http://localhost:5173> and move the effort slider, switch regimes
(harsh / mixed / protective), or toggle mechanisms — the simulation rebuilds and
re-streams live. More detail in [`src/ux/README.md`](src/ux/README.md).

## Documentation

- [`docs/README.md`](docs/README.md) - the model specification: the full
  mathematics (sections 7.1-7.13), the design rationale, and the visualization
  plan.
- [`docs/design/architecture.md`](docs/design/architecture.md) - how the engine
  works and how to extend it.
- [`docs/literature/`](docs/literature/) - the research the model rests on, with
  one note per paper. (Paper PDFs are not redistributed here; a fetch/convert
  workflow downloads and converts them locally for study.)

## Experiments

The [`experiments/`](experiments/) folder holds controlled studies: each is a
self-contained subfolder that sweeps a variable, averages over seeds, and reports
the model's output. [`effort-marginal-impact/`](experiments/effort-marginal-impact/)
measures whether effort (value creation) raises the probability of escape, by how
much, and how that impact varies with structural position - including a condition
that removes the efficiency floor, so the "effort always helps" property is
*measured* rather than assumed. [`calibration/`](experiments/calibration/) checks
the calibrated defaults against the target ranges in
[`docs/literature/calibration.md`](docs/literature/calibration.md).

## Roadmap

Mechanisms are added one at a time as self-contained components. Planned
extensions and the visualization plan are described in `docs/README.md`
sections 4 and 8.

## Status

Alpha. The defaults are **calibrated to a realistic regime** - reaching the top is
a rare tail event (~5% of poor-born lives), the intergenerational elasticity sits
in the Great Gatsby range (IGE ~0.3-0.6), and the wealth distribution is
bottom/middle-heavy - but they are **not** fit to any specific country. The
calibration is checked, with its targets and sources, in
[`experiments/calibration/`](experiments/calibration/); re-run it after any
parameter change. The `harsh`/`mixed`/`protective` regimes are illustrative
contrasts, not models of real countries.

## Contributing

Issues and pull requests are welcome. Please read
[`CONTRIBUTING.md`](CONTRIBUTING.md) - it covers the dev setup, the "add a
component, not an edit" extension pattern, coding standards, and the literature
policy. Contributors are listed in [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

## License

[MIT](LICENSE) (c) 2026 Dietmar Luther Krause Gutierrez.
