# Architecture

This document explains how the simulation engine is put together and how to
extend it. The model itself (the economics and the math) lives in
[`../README.md`](../README.md); this is about the software.

## Goals

The engine is built to be **scalable** (thousands of agents via vectorised
NumPy), **extensible** (new mechanisms are new components, not edits to the
core), and **reproducible** (a seed fully determines a run). It follows SOLID,
and every module is documented in-code.

## The pipeline

A simulation is an ordered set of small components that the engine runs once per
tick, in this fixed order:

```
tick:
  1. DriftTerm.drift(...)        -> summed into mu        (flows, scaled by dt)
  2. NoiseTerm.increment(...)    -> summed into increment (shocks, ~ sqrt(dt))
  3. wealth += mu*dt + increment
  4. EventProcess.apply(...)     -> discrete jumps (opportunities)
  5. PopulationProcess.step(...) -> skill, network, regime, barriers, births
  6. Observer.observe(...)       -> record metrics (read-only)
```

The engine (`core/engine.py`) holds the component lists and does nothing
model-specific. To change the model you change the *list of components*, not the
engine.

## The seams (interfaces)

All interfaces are tiny `Protocol`s in `core/protocols.py`:

| Protocol | Responsibility | Example components |
|----------|----------------|--------------------|
| `DriftTerm` | add a term to expected drift `mu` | `NeighborhoodDrift`, `PovertyPremium`, `ValueCreation`, `CapitalReturns`, `NetworkDrift` |
| `NoiseTerm` | add a stochastic increment | `DiffusionShocks` |
| `EventProcess` | apply discrete jumps | `OpportunityProcess` |
| `PopulationProcess` | births/deaths/network/barriers | `SkillGrowth`, `SocialNetwork`, `RegimePolicy`, `FirstPassageMonitor` |
| `Observer` | record metrics (read-only) | `PopulationMetrics` |
| `BirthPolicy` | (re)spawn a resolved life | `SimpleRestart`, `GenerationalTransmission` |

## How SOLID shows up

- **Single Responsibility** - each component is one force or one bookkeeping
  job. `PovertyPremium` only knows about the premium; `OpportunityProcess` only
  knows about opportunities.
- **Open/Closed** - adding effort efficiency, opportunities, networks, or
  generations was done by adding components, never by editing the engine.
- **Liskov Substitution** - any `DriftTerm` can stand in for any other; the
  engine treats them uniformly.
- **Interface Segregation** - a component implements only the one protocol for
  the role it plays (drift vs noise vs event vs population vs observer).
- **Dependency Inversion** - the engine depends on the protocols, not on
  concrete components; the `FirstPassageMonitor` depends on the `BirthPolicy`
  abstraction, so "restart fresh" vs "inherit" is an injected strategy.

## State

`core/state.py` holds the population as a **structure of arrays** (one NumPy
array per attribute), so the whole population updates with vectorised math.
`AgentState` is a passive data container; the rules live in the components.

## Configuration and regimes

`core/config.py` defines a single frozen `ModelParams` dataclass - the one
source of truth for every constant. "Change the country/policy" means producing
a modified copy via `params.evolve(...)`; see `regimes/presets.py`. Nothing
mutates global state, which keeps runs reproducible.

## Determinism

Every stochastic draw flows through the single `numpy.random.Generator` carried
by `SimContext`. Given a seed, a run is bit-for-bit reproducible (enforced by
`tests/test_determinism.py`).

## Composing a run

`builder.py` wires the canonical pipeline (with the correct ordering of
population processes) and applies an effort policy to the initial cohort. The
CLI (`cli.py`) and the tests use it. You can also assemble a custom pipeline
directly against `Simulation` if you need something non-standard.

```python
from poverty_trap.builder import build_simulation

sim = build_simulation(seed=0, effort=0.5, generational=True)
result = sim.run(20000)
print(result.reports["FirstPassageMonitor"])  # mobility probabilities
```

## How to add a new mechanism (worked example)

Say you want to add **discrimination**: a penalty on value creation for a tagged
group.

1. Add any new fields to `ModelParams` (e.g. `discrimination_penalty`) and a
   group flag to `AgentState`.
2. Write a `Discrimination` class with a `drift(self, state, ctx) -> np.ndarray`
   method returning the (negative) per-agent term. Put it in `dynamics/`.
3. Append it to the `drift_terms` list in `builder.py` (or your own pipeline).
4. Add a test asserting the penalty applies only to the tagged group.

No engine change required. That is the whole point.

## Visualization

The engine is headless and numeric by design (separation of concerns). A
visualization layer (e.g. a Pygame or web renderer) is an **adapter** that reads
`AgentState` each tick and draws it; it attaches as an `Observer` so it cannot
affect the dynamics. The per-concept visual plan is in
[`../README.md`](../README.md) section 8.

## Testing

`tests/` covers determinism, per-component behaviour (drift signs, efficiency
monotonicity, Gini bounds), and engine-level qualitative facts (rich escape >
poor, effort raises poor escape, leaving poverty is easier than getting rich).
Run them with `pytest`.
