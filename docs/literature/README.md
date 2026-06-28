# Literature

This folder grounds the model in published research. Every structural assumption
in the simulation traces back to a paper here, so the conclusions are
defensible rather than opinion.

## What is in here

- [`calibration.md`](calibration.md) - **the evidence ledger**: every model
  assumption mapped to the study, number, or formula that backs it; the gaps
  where we are assuming without evidence; and the data-driven values to
  calibrate the engine. Start here.
- [`papers/`](papers/) - the references themselves. `fetch_papers.py` downloads
  the freely available PDFs locally and `convert_papers.py` turns them into full
  Markdown (in a git-ignored `fulltext/` folder) for offline / AI-assisted study.

## A note on copyright (why there are no PDFs in the repo)

This is a public, open-source repository, so we do **not** commit publisher PDFs:
redistributing copyrighted articles would be infringement. Instead we commit our
own notes and links, and `.gitignore` excludes `*.pdf` / `*.html` under
`papers/`. Run the fetch script to pull the open versions locally:

```bash
python docs/literature/papers/fetch_papers.py
```

Where only a paywalled version exists, the note links to the official DOI and to
the best freely available alternative (preprint, author copy, or working paper).

## How the literature maps to the model

The full ledger (with numbers) is in [`calibration.md`](calibration.md). In brief:

| Model piece (see ../README.md) | Strongest data source |
|--------------------------------|-----------------------|
| Neighbourhood base drift | Chetty & Hendren 2018 (~4%/yr exposure) |
| The Micawber threshold | Balboni et al. 2022 (RCT threshold); Lybbert 2004 |
| ...and the counter-case | Kraay & McKenzie 2014 (traps are not universal) |
| The poverty premium | Davies 2016 / Davies & Evans 2023 (~GBP 490/yr) |
| Effort efficiency (scarcity tax) | Mani et al. 2013; caveat Carvalho et al. 2016 |
| Effort quality / savings | Psacharopoulos 2018 (~9%/yr); Dynan 2004 |
| Capital returns rise with wealth | Fagereng et al. 2020; Bach et al. 2020 |
| Power-law wealth tail (~1.5) | Vermeulen 2018; Benhabib & Bisin 2018; Gabaix 2016 |
| Social networks / connectedness | Chetty, Jackson et al. 2022 (+20% income) |
| Generational transmission / IGE | Corak 2013; Jantti 2006; Chetty 2014 |
| Talent normal, outcome power-law | Pluchino et al. 2018; Barabasi & Albert 1999 |
