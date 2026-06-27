#!/usr/bin/env python3
"""Convert downloaded paper PDFs to full Markdown - locally, for personal study.

Why this is a separate, local step (read this):
    The PDFs are copyrighted by their publishers. Converting a copyrighted PDF to
    Markdown does not change its copyright, so the FULL-TEXT output of this script
    is written into ``fulltext/``, which is git-ignored and therefore NOT
    published with this open-source repository. Use it to read the papers offline.
    Only open-licensed papers (e.g. CC-BY) may be committed; see README.md.

Pipeline:
    1. run ``fetch_papers.py`` to download the open PDFs into this folder, then
    2. run this script to turn each ``*.pdf`` here into ``fulltext/<name>.md``.

Converter backends (first available wins):
    * pymupdf4llm  - best Markdown structure          (pip install pymupdf4llm)
    * PyMuPDF/fitz - plain text fallback               (pip install pymupdf)
    * pdfminer.six - plain text fallback               (pip install pdfminer.six)
"""

from __future__ import annotations

import sys
from pathlib import Path


def _convert_one(pdf: Path) -> str:
    """Return the Markdown/text for ``pdf`` using the best available backend."""
    try:
        import pymupdf4llm  # type: ignore

        return pymupdf4llm.to_markdown(str(pdf))
    except Exception:
        pass
    try:
        import fitz  # PyMuPDF  # type: ignore

        with fitz.open(str(pdf)) as doc:
            return "\n\n".join(page.get_text("text") for page in doc)
    except Exception:
        pass
    try:
        from pdfminer.high_level import extract_text  # type: ignore

        return extract_text(str(pdf))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "No PDF backend available. Install one: pip install pymupdf4llm"
        ) from exc


def main() -> int:
    here = Path(__file__).resolve().parent
    out_dir = here / "fulltext"
    out_dir.mkdir(exist_ok=True)

    pdfs = sorted(here.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found. Run fetch_papers.py first.")
        return 1

    header = (
        "<!-- Full-text conversion for PERSONAL STUDY ONLY. The source paper is\n"
        "     copyrighted by its publisher; this file is git-ignored and must not\n"
        "     be redistributed. See ../README.md. -->\n\n"
    )
    ok = 0
    for pdf in pdfs:
        dest = out_dir / (pdf.stem + ".md")
        try:
            md = _convert_one(pdf)
            dest.write_text(header + md, encoding="utf-8")
            print(f"  ok: {dest.relative_to(here)} ({len(md) // 1024} KB)")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED: {pdf.name} ({exc})")
    print(f"\n{ok}/{len(pdfs)} converted into {out_dir.relative_to(here)}/ (git-ignored).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
