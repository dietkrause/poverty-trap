# Literature

This folder grounds the model in published research. Every structural assumption
in the simulation traces back to a paper here, so the conclusions are
defensible rather than opinion.

## What is in here

- [`papers/`](papers/) - one Markdown **note** per reference: full citation,
  links, a short summary in our own words, the specific concept or equation we
  borrow, and how it maps to the model. These notes are original summaries, not
  copies of the papers.
- [`papers/fetch_papers.py`](papers/fetch_papers.py) - a script that downloads
  the **freely available** version of each paper (preprint, working paper, or
  open-access copy) to your local machine for offline reading.

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

| Model piece (see ../README.md) | Source |
|--------------------------------|--------|
| Neighbourhood sets the starting point | Chetty, Hendren, Kline & Saez 2014 |
| The Micawber threshold / poverty trap | Barrett & Carter 2006; Azariadis & Stachurski 2005 |
| The poverty premium | Ghatak 2015 |
| Effort efficiency (scarcity tax) | Mani, Mullainathan, Shafir & Zhao 2013 |
| Generational transmission / IGE | Corak 2013; OECD 2018 |
| Social networks / connectedness | Chetty, Jackson et al. 2022; Granovetter 1973 |
| Opportunity as a power law | Barabasi & Albert 1999; Merton 1968 |
| Talent normal, outcome power-law | Pluchino, Biondo & Rapisarda 2018 |
