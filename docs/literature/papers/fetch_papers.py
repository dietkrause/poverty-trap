#!/usr/bin/env python3
"""Download the freely available version of each referenced paper, locally.

This script fetches open-access / preprint / working-paper versions only, into
the folder it lives in. Downloaded files are git-ignored and are for personal
study; this repository does not redistribute them.

Usage:
    python docs/literature/papers/fetch_papers.py

It is best-effort: a paper with no stable free URL is skipped with a message and
its note still links the official source.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

# (filename, url). Only stable, freely available versions are listed. Paywalled
# items (e.g. Barrett & Carter) are intentionally absent; see their notes.
SOURCES: list[tuple[str, str]] = [
    ("chetty-2014.pdf", "https://www.nber.org/system/files/working_papers/w19843/w19843.pdf"),
    ("ghatak-2015.pdf", "https://personal.lse.ac.uk/ghatak/povertytraps.pdf"),
    ("corak-2013.pdf", "https://docs.iza.org/dp7520.pdf"),
    ("barabasi-albert-1999.pdf", "https://arxiv.org/pdf/cond-mat/9910332"),
    ("pluchino-2018.pdf", "https://arxiv.org/pdf/1802.07068"),
]

USER_AGENT = "Mozilla/5.0 (poverty-trap literature fetcher; personal study)"


def fetch(name: str, url: str, dest_dir: Path) -> bool:
    dest = dest_dir / name
    if dest.exists():
        print(f"  skip (exists): {name}")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 (trusted URLs)
            data = resp.read()
        dest.write_bytes(data)
        print(f"  ok: {name} ({len(data) // 1024} KB)")
        return True
    except Exception as exc:  # noqa: BLE001 - best-effort tool
        print(f"  FAILED: {name} <- {url}  ({exc})")
        return False


def main() -> int:
    here = Path(__file__).resolve().parent
    print(f"Downloading open-access papers into {here}")
    ok = sum(fetch(name, url, here) for name, url in SOURCES)
    print(f"\n{ok}/{len(SOURCES)} downloaded. Paywalled papers are linked in their notes.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
