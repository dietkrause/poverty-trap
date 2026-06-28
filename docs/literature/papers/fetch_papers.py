#!/usr/bin/env python3
"""Download the freely available PDF of each referenced paper, locally.

Every entry below was selected because (a) it provides a numeric result, formula,
or distribution we use to justify or calibrate the model and (b) a free,
downloadable PDF exists (preprint, working paper, open access, or author copy).
Downloads land in this folder and are git-ignored; pair with ``convert_papers.py``
to turn each into full Markdown for offline / AI-assisted reading.

Usage:
    python docs/literature/papers/fetch_papers.py
"""

from __future__ import annotations

import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

# (filename, url). Grouped by the model assumption each source backs.
SOURCES: list[tuple[str, str]] = [
    # --- Poverty traps: thresholds, S-curves, escape RCTs --------------------
    ("balboni-2022-why-stay-poor.pdf", "https://www.nber.org/system/files/working_papers/w29340/w29340.pdf"),
    ("banerjee-2015-six-countries.pdf", "https://dspace.mit.edu/server/api/core/bitstreams/ebaa8833-5fdb-4614-84b8-2096537cb8b2/content"),
    ("lybbert-2004-stochastic-wealth.pdf", "https://arefiles.ucdavis.edu/uploads/filer_public/3a/78/3a78d81a-c983-4123-a8bb-88078f5d731c/2004_lybbert_et_al_ej_stochastic_wealth_dynamics.pdf"),
    ("santos-barrett-2018-heterogeneous-dynamics.pdf", "https://www.nber.org/system/files/chapters/c13835/c13835.pdf"),

    # --- Returns to wealth / compounding / power-law tail --------------------
    ("fagereng-2020-returns-to-wealth.pdf", "https://www.nber.org/system/files/working_papers/w22822/w22822.pdf"),
    ("benhabib-bisin-zhu-2011-wealth.pdf", "http://piketty.pse.ens.fr/files/BenhabibBisinZhu2011.pdf"),
    ("gabaix-2016-dynamics-of-inequality.pdf", "https://people.stern.nyu.edu/xgabaix/papers/dynamics.pdf"),
    ("benhabib-bisin-2018-skewed-wealth.pdf", "https://www.nber.org/system/files/working_papers/w21924/w21924.pdf"),
    ("dynan-2004-do-rich-save-more.pdf", "https://www.nber.org/system/files/working_papers/w7906/w7906.pdf"),

    # --- Neighbourhood / place effects / social capital ----------------------
    ("chetty-hendren-2018-neighborhoods-1.pdf", "https://opportunityinsights.org/wp-content/uploads/2018/03/movers_paper1.pdf"),
    ("chetty-hendren-2018-neighborhoods-2.pdf", "https://opportunityinsights.org/wp-content/uploads/2018/03/movers_paper2.pdf"),
    ("chetty-2018-opportunity-atlas.pdf", "https://opportunityinsights.org/wp-content/uploads/2018/10/atlas_paper.pdf"),
    ("chetty-2022-social-capital-1.pdf", "https://www.nber.org/system/files/working_papers/w30313/w30313.pdf"),
    ("chetty-2022-social-capital-2.pdf", "https://www.nber.org/system/files/working_papers/w30314/w30314.pdf"),
    ("bergman-2024-moves-to-opportunity.pdf", "https://www.nber.org/system/files/working_papers/w26164/w26164.pdf"),
    ("chetty-2014-land-of-opportunity.pdf", "https://www.nber.org/system/files/working_papers/w19843/w19843.pdf"),

    # --- Scarcity / effort efficiency ---------------------------------------
    ("mani-2013-poverty-cognitive.pdf", "https://zhaolab.psych.ubc.ca/pdfs/Zhao_2013_Science.pdf"),
    ("carvalho-2016-decision-payday.pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5167530/pdf/nihms834513.pdf"),
    ("haushofer-fehr-2014-psychology-poverty.pdf", "https://haushofer.ne.su.se/publications/Haushofer_Fehr_Science_2014.pdf"),

    # --- Poverty premium -----------------------------------------------------
    ("davies-2016-paying-to-be-poor.pdf", "https://www.bristol.ac.uk/media-library/sites/geography/pfrc/pfrc1615-poverty-premium-report.pdf"),
    ("davies-evans-2023-poverty-premium.pdf", "https://www.bristol.ac.uk/media-library/sites/geography/pfrc/documents/The%20poverty%20premium%20in%202022%20-%20Progress%20and%20problems.pdf"),

    # --- Intergenerational elasticity / returns to skill --------------------
    ("corak-2013-great-gatsby.pdf", "https://docs.iza.org/dp7520.pdf"),
    ("jantti-2006-american-exceptionalism.pdf", "https://docs.iza.org/dp1938.pdf"),
    ("mazumder-2015-ige-us.pdf", "https://www.chicagofed.org/-/media/publications/working-papers/2015/wp2015-04-pdf.pdf?sc_lang=en"),
    ("card-1999-education-earnings.pdf", "https://davidcard.berkeley.edu/papers/causal_educ_earnings.pdf"),
    ("heckman-2006-earnings-functions.pdf", "https://www.nber.org/system/files/working_papers/w11544/w11544.pdf"),
    ("psacharopoulos-2018-returns-education.pdf", "https://documents1.worldbank.org/curated/en/442521523465644318/pdf/WPS8402.pdf"),

    # --- Power-law networks / opportunity / talent-vs-luck -------------------
    ("barabasi-albert-1999-scaling.pdf", "https://arxiv.org/pdf/cond-mat/9910332"),
    ("pluchino-2018-talent-vs-luck.pdf", "https://arxiv.org/pdf/1802.07068"),
    ("ghatak-2015-poverty-traps.pdf", "https://personal.lse.ac.uk/ghatak/povertytraps.pdf"),
]

USER_AGENT = "Mozilla/5.0 (poverty-trap literature fetcher; personal study)"


def _open(url: str):
    """Open a URL, retrying without TLS verification on certificate errors."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        return urllib.request.urlopen(req, timeout=90)  # noqa: S310 (curated URLs)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, "reason", None), ssl.SSLError):
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=90, context=ctx)  # noqa: S310
        raise


def fetch(name: str, url: str, dest_dir: Path) -> bool:
    dest = dest_dir / name
    if dest.exists():
        print(f"  skip (exists): {name}")
        return True
    try:
        with _open(url) as resp:
            data = resp.read()
        if not data.startswith(b"%PDF"):
            print(f"  FAILED: {name} (not a PDF; host may require a browser/login)")
            return False
        dest.write_bytes(data)
        print(f"  ok: {name} ({len(data) // 1024} KB)")
        return True
    except Exception as exc:  # noqa: BLE001 - best-effort tool
        print(f"  FAILED: {name} ({exc})")
        return False


def main() -> int:
    here = Path(__file__).resolve().parent
    print(f"Downloading {len(SOURCES)} open papers into {here}\n")
    ok = sum(fetch(name, url, here) for name, url in SOURCES)
    print(f"\n{ok}/{len(SOURCES)} downloaded. Any failures need a manual source.")
    print("Next: python convert_papers.py")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
