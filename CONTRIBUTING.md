# Contributing

Thanks for considering a contribution. This project values discipline and
clarity: it is meant to be a credible, accountable model, so changes should keep
it correct, documented, and easy to extend.

## Code of conduct

Be respectful and assume good faith. Critique ideas, not people. Discussions
about the model's assumptions are welcome - that is how it improves.

## Getting set up

Requires Python 3.10+.

```bash
git clone https://github.com/dietkrause/poverty-trap
cd poverty-trap
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -e ".[dev,viz]"
```

Run the checks:

```bash
pytest            # tests
ruff check src    # lint
mypy src/simulation  # types
```

All three must pass before a PR is merged.

## How the codebase is organised

Read [`docs/design/architecture.md`](docs/design/architecture.md) first. The key
idea: the engine runs an ordered pipeline of small components, each implementing
one tiny `Protocol`. **You add behaviour by adding a component, never by editing
the engine.**

## Making a change

1. Open an issue describing the change (a new mechanism, a calibration, a bug)
   before large work, so we agree on the approach.
2. Branch from `main`: `git checkout -b feature/short-name`.
3. Keep commits focused and write a clear message.

### Adding a new model mechanism

This is the most common contribution. Worked example in
`docs/design/architecture.md` ("How to add a new mechanism"). In short:

- Add any new parameters to `ModelParams` (with a docstring and a default) and a
  range check in `ModelParams.validate`.
- Add any new agent fields to `AgentState`.
- Write one class implementing the appropriate protocol (`DriftTerm`,
  `NoiseTerm`, `EventProcess`, `PopulationProcess`, `Observer`, or `BirthPolicy`).
  One responsibility per class.
- Wire it into `builder.py` (or document a new preset pipeline).
- Add a test that pins its behaviour.
- If it rests on published research, add a literature note (see below) and cite
  it in the component's docstring and in `docs/README.md`.

## Coding standards

- **Type hints everywhere**; `mypy` is configured with `disallow_untyped_defs`.
- **Docstrings** on every public module, class, and function. Explain the *why*
  and the link to the model section, not just the *what*.
- **Vectorise** with NumPy; avoid Python-level per-agent loops in hot paths.
- **All randomness** must come from `ctx.rng` so runs stay reproducible. Never
  call `numpy.random` module-level functions or `random`.
- Keep components **pure** where the protocol says so (`DriftTerm.drift` and
  `NoiseTerm.increment` must not mutate state).
- `ruff` enforces formatting and lint (line length 100).

## Tests

Every behavioural change needs a test. We test three layers: determinism
(seed reproducibility), per-component behaviour, and engine-level qualitative
facts (e.g. rich escape > poor escape). See `tests/`.

## Literature and PDFs (please read)

This is a public repository. **Do not commit copyrighted paper PDFs or their
full-text conversions.** Add an original Markdown *note* under
`docs/literature/papers/` (citation, links, a short summary in your own words,
and how the model uses it), and link the official DOI plus a free version.
Full-text conversions belong in the git-ignored `fulltext/` folder produced by
`convert_papers.py`. Only papers under a redistribution-permitting license
(e.g. CC-BY) may have full text committed, with attribution.

## Documentation

If you change behaviour, update the relevant doc: the model spec
(`docs/README.md`), the architecture (`docs/design/architecture.md`), or a
literature note. Documentation changes do not need tests.

## Pull requests

- Reference the issue it closes.
- Describe what changed and why, and note any new parameters or assumptions.
- Confirm `pytest`, `ruff`, and `mypy` pass.
- Add yourself to [`CONTRIBUTORS.md`](CONTRIBUTORS.md) in the same PR.

## License of contributions

By contributing, you agree that your contribution is licensed under the project's
[MIT License](LICENSE).
