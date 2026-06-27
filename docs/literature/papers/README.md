# Papers

Two things live here:

1. **Notes** - one Markdown file per reference: an original summary (citation,
   links, what it says in our words, and how the model uses it). Committed,
   because they are our own writing.
2. **Full text** - generated locally from the PDFs into the git-ignored
   `fulltext/` folder (workflow below). The full text of copyrighted papers is
   **not** committed; doing so in a public repo would infringe.

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

| Note | Reference | Open version | Used for |
|------|-----------|--------------|----------|
| [chetty-2014.md](chetty-2014.md) | Chetty, Hendren, Kline & Saez (2014), QJE | NBER w19843 | neighbourhood / geography of mobility |
| [barrett-carter-2006.md](barrett-carter-2006.md) | Barrett & Carter (2006), J. Dev. Studies | paywalled (DOI) | Micawber threshold / asset trap |
| [azariadis-stachurski-2005.md](azariadis-stachurski-2005.md) | Azariadis & Stachurski (2005), Handbook of Econ. Growth | author working paper | S-shaped map / multiple equilibria |
| [ghatak-2015.md](ghatak-2015.md) | Ghatak (2015), World Bank Econ. Review | LSE author PDF | poverty premium |
| [mani-2013.md](mani-2013.md) | Mani, Mullainathan, Shafir & Zhao (2013), Science | author/HKS copy | effort efficiency / scarcity tax |
| [corak-2013.md](corak-2013.md) | Corak (2013), J. Econ. Perspectives | IZA dp7520 | IGE / Great Gatsby Curve |
| [oecd-2018.md](oecd-2018.md) | OECD (2018), A Broken Social Elevator? | OECD open | generations to mean income |
| [chetty-2022-social-capital.md](chetty-2022-social-capital.md) | Chetty, Jackson et al. (2022), Nature | open access | social capital / connectedness |
| [granovetter-1973.md](granovetter-1973.md) | Granovetter (1973), Am. J. Sociology | author/JSTOR | weak ties / opportunity access |
| [barabasi-albert-1999.md](barabasi-albert-1999.md) | Barabasi & Albert (1999), Science | arXiv cond-mat/9910332 | preferential attachment / power law |
| [merton-1968.md](merton-1968.md) | Merton (1968), Science | open scans | Matthew effect / cumulative advantage |
| [pluchino-2018.md](pluchino-2018.md) | Pluchino, Biondo & Rapisarda (2018), Adv. Complex Syst. | arXiv 1802.07068 | talent normal, outcome power-law |

> Some sources are paywalled at the publisher. The notes always link the
> official DOI plus the best freely available alternative. Please respect the
> licenses of the downloaded files; they are for personal study and are not
> redistributed by this repository.
