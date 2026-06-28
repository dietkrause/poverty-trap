#!/usr/bin/env python3
"""Download the freely available PDF of each referenced paper, locally.

Fetches open-access / preprint / working-paper / author copies only, into the
folder it lives in. Downloaded files are git-ignored (the repo does not
redistribute publisher PDFs). Pair with ``convert_papers.py`` to turn each PDF
into full Markdown.

Usage:
    python docs/literature/papers/fetch_papers.py
"""

from __future__ import annotations

import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

# (filename, url). Public / freely available versions only. Some entries are
# best-effort author or open-access copies and may move; failures are skipped.
SOURCES: list[tuple[str, str]] = [
    ("chetty-2014.pdf", "https://www.nber.org/system/files/working_papers/w19843/w19843.pdf"),
    ("chetty-2022-social-capital-1.pdf", "https://www.nature.com/articles/s41586-022-04996-4.pdf"),
    ("chetty-2022-social-capital-2.pdf", "https://www.nature.com/articles/s41586-022-04997-3.pdf"),
    ("ghatak-2015.pdf", "https://personal.lse.ac.uk/ghatak/povertytraps.pdf"),
    ("corak-2013.pdf", "https://docs.iza.org/dp7520.pdf"),
    ("mani-2013.pdf", "https://scholar.harvard.edu/files/sendhil/files/976.full_.pdf"),
    ("granovetter-1973.pdf",
     "https://snap.stanford.edu/class/cs224w-readings/granovetter73weakties.pdf"),
    ("barabasi-albert-1999.pdf", "https://arxiv.org/pdf/cond-mat/9910332"),
    ("pluchino-2018.pdf", "https://arxiv.org/pdf/1802.07068"),
]

USER_AGENT = "Mozilla/5.0 (poverty-trap literature fetcher; personal study)"


def _open(url: str):
    """Open a URL, retrying without TLS verification on certificate errors.

    Some legitimate document hosts present certificate chains that Python's
    default store rejects. For these public, read-only downloads we retry
    without verification rather than fail outright.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        return urllib.request.urlopen(req, timeout=60)  # noqa: S310 (curated URLs)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, "reason", None), ssl.SSLError):
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=60, context=ctx)  # noqa: S310
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
            print(f"  FAILED: {name} (not a PDF; the host may require login)")
            return False
        dest.write_bytes(data)
        print(f"  ok: {name} ({len(data) // 1024} KB)")
        return True
    except Exception as exc:  # noqa: BLE001 - best-effort tool
        print(f"  FAILED: {name} <- {url}  ({exc})")
        return False


def main() -> int:
    here = Path(__file__).resolve().parent
    print(f"Downloading open papers into {here}")
    ok = sum(fetch(name, url, here) for name, url in SOURCES)
    print(f"\n{ok}/{len(SOURCES)} downloaded. Paywalled papers with no free version are skipped.")
    print("Next: python convert_papers.py")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
