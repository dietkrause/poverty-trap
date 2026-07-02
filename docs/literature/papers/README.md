# Papers

What is tracked here (in version control):

1. **[`INDEX.md`](INDEX.md)** - the list of every referenced paper (citation +
   a link to a free source), grouped by the assumption it backs.
2. **The fetch/convert scripts** (`fetch_papers.py`, `convert_papers.py`) and this
   README.

What is **not** tracked (git-ignored):

- **The PDFs** (`*.pdf`) - copyrighted publisher/author works; redistributing them
  in a public repo would infringe.
- **Full-text conversions** (`fulltext/*.md`) - generated locally from the PDFs;
  they are the papers' text, so the same copyright applies.

Download and convert them locally with the workflow below; the numbers taken from
each paper are recorded in [`../calibration.md`](../calibration.md).

## Getting the full papers as Markdown (local workflow)

```bash
# 1. download the freely available PDFs into this folder (git-ignored)
python docs/literature/papers/fetch_papers.py

# 2. convert each PDF to Markdown in ./fulltext/ (git-ignored)
pip install pymupdf4llm           # best Markdown output; fallbacks exist
python docs/literature/papers/convert_papers.py
```

After step 2 you have the entire papers as Markdown under `fulltext/`, for
offline reading. They stay on your machine and are excluded from version control.
Only papers under a redistribution-permitting license (e.g. CC-BY) may be
committed as full text, with attribution.

The full evidence ledger - which paper backs which assumption, with the exact
numbers - is in [`../calibration.md`](../calibration.md). The table below lists
the papers whose **free PDF downloads and converts cleanly** (the set this repo
targets for offline / AI-assisted reading).

| File stem (in `fulltext/`) | Reference | Backs |
|----------------------------|-----------|-------|
| balboni-2022-why-stay-poor | Balboni et al. (2022), QJE | the threshold w* (~504 USD PPP) |
| banerjee-2015-six-countries | Banerjee et al. (2015), Science | big-push escape (graduation RCT) |
| lybbert-2004-stochastic-wealth | Lybbert et al. (2004), EJ | livestock Micawber threshold |
| santos-barrett-2018-heterogeneous-dynamics | Santos & Barrett (2018), NBER | shock-dependent threshold |
| chetty-2014-land-of-opportunity | Chetty et al. (2014), QJE | rank-rank slope 0.341 |
| chetty-hendren-2018-neighborhoods-1/2 | Chetty & Hendren (2018), QJE | ~4%/yr exposure effect |
| chetty-2018-opportunity-atlas | Chetty et al. (2018), NBER | 60% causal place effects |
| bergman-2024-moves-to-opportunity | Bergman et al. (2024), AER | relocation friction (+37.8 pp) |
| chetty-2022-social-capital-1/2 | Chetty, Jackson et al. (2022), Nature | connectedness -> +20% income |
| ghatak-2015-poverty-traps | Ghatak (2015), WBER | poverty-premium theory |
| davies-2016-paying-to-be-poor | Davies et al. (2016), PFRC | premium ~GBP 490/yr |
| davies-evans-2023-poverty-premium | Davies & Evans (2023), PFRC | premium incidence/tail |
| mani-2013-poverty-cognitive | Mani et al. (2013), Science | scarcity tax ~13 IQ pts |
| haushofer-fehr-2014-psychology-poverty | Haushofer & Fehr (2014), Science | stress/scarcity feedback |
| fagereng-2020-returns-to-wealth | Fagereng et al. (2020), Econometrica | returns rise +180 bps with wealth |
| benhabib-bisin-2018-skewed-wealth | Benhabib & Bisin (2018), JEL | Kesten tail, exponent ~1.5 |
| gabaix-2016-dynamics-of-inequality | Gabaix et al. (2016), Econometrica | zeta~1.54, slow transitions |
| dynan-2004-do-rich-save-more | Dynan et al. (2004), JPE | saving rate -2.7% -> 16.1% |
| psacharopoulos-2018-returns-education | Psacharopoulos & Patrinos (2018), WB | ~9%/yr returns to schooling |
| heckman-2006-earnings-functions | Heckman et al. (2006), NBER | Mincer earnings form |
| corak-2013-great-gatsby | Corak (2013), JEP | IGE by country; Great Gatsby |
| jantti-2006-american-exceptionalism | Jantti et al. (2006), IZA | father-son IGE by country |
| mazumder-2015-ige-us | Mazumder (2015), Chicago Fed | US IGE upper bound > 0.6 |
| barabasi-albert-1999-scaling | Barabasi & Albert (1999), Science | preferential attachment |
| pluchino-2018-talent-vs-luck | Pluchino et al. (2018), ACS | talent normal -> outcome power-law |

> A few sources have no clean free PDF and so are cited but not downloaded:
> Kraay & McKenzie (2014, JEP, the skeptical counter-case), Bach, Calvet & Sodini
> (2020, AER), Vermeulen (2018, RIW), Bell et al. (2019, QJE), Card (1999). See
> `../calibration.md` for their numbers and links.

