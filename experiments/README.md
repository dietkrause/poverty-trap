# Experiments

This folder is where the simulation **adjudicates** questions instead of us
asserting answers. Each experiment is a self-contained subfolder that runs the
engine under controlled conditions and reports what comes out - so a claim about
social dynamics becomes a measured result, not a design choice.

## The epistemology (read this first)

An agent-based model does not prove a social fact directly. It demonstrates the
**logical consequences of micro-rules**. So every experiment here answers a
*conditional* question:

> *If* agents follow the rules in `src/simulation/` calibrated to the values in
> [`../docs/literature/calibration.md`](../docs/literature/calibration.md),
> *then* what happens to the outcome we are measuring?

The data supplies the "if"; the experiment demonstrates the "then". An
experiment is only as objective as its calibration, so each one must state which
parameters it varies and which it holds fixed, and must avoid quietly encoding
its own conclusion (e.g. testing "does effort always help?" while hard-wiring a
floor that forces it to). Where a result depends on a contested assumption, the
experiment should **vary that assumption and show the dependence**.

## Layout

```
experiments/
  README.md                     # this file
  <experiment-name>/
    README.md                   # the question, method, how to run, how to read it
    run.py                      # runnable; writes to ./results/
    results/                    # generated output (git-ignored)
```

## Running an experiment

Each `run.py` bootstraps `src/` onto the path, so no install is required:

```bash
python experiments/<experiment-name>/run.py            # default (fast) settings
python experiments/<experiment-name>/run.py --help     # to scale it up
```

Plots need the optional viz extra: `pip install matplotlib`.

## Adding an experiment

1. Create `experiments/<name>/` with a `README.md` (question, method, expected
   output) and a `run.py`.
2. Build pipelines with `simulation.builder.build_simulation` (or assemble
   components directly), sweep the variable of interest, average over seeds, and
   write a `results/summary.json`.
3. State your calibration source and which assumptions you vary. If a finding
   hinges on one parameter, add a condition that varies it.

## Index

| Experiment | Question it adjudicates |
|------------|-------------------------|
| [`effort-marginal-impact/`](effort-marginal-impact/) | Does effort (value creation) always raise the probability of escape, by how much, and how does its impact vary with structural position? Is "always positive" a finding or an artifact of the efficiency floor? |
| [`mobility-drivers/`](mobility-drivers/) | Across starting position, effort, regime, opportunity, and networks, which levers move the two mobility outcomes most, and does effort pay off equally under every regime? (Balanced full-factorial; auto-writes a neutral findings document.) |
