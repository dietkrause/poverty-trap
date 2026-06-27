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
from poverty_trap.builder import build_simulation

sim = build_simulation(seed=0, effort=0.5, generational=True)
result = sim.run(20000)
print(result.reports["FirstPassageMonitor"])  # left-poverty vs became-rich, by class
print(result.reports["PopulationMetrics"])     # Gini, band shares, wealth gap
```

## How it is built

The engine is a small, composable core that runs an ordered pipeline of
single-responsibility components each tick (drift terms, noise, events,
population processes, observers). New mechanisms are added as new components, not
by editing the engine. It is vectorised with NumPy (thousands of agents),
deterministic from a seed, and documented in-code. See
**[`docs/design/architecture.md`](docs/design/architecture.md)**.

```
src/poverty_trap/
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
