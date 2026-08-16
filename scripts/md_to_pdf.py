#!/usr/bin/env python3
"""Render the markdown deliverables to PDF for upload alongside the one-pager.

    python scripts/md_to_pdf.py

The repo already contains these as markdown; this exists because a Round 1 judge
scores from what is attached to the submission form, and the rigour evidence
(assumptions, sensitivity, limitations) should not depend on them cloning the
repo to find it.

Writes docs/methodology.pdf and docs/ai_briefings.pdf via headless Edge/Chrome.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import pathname2url

import markdown

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"

TARGETS = [
    ("methodology.md", "methodology.pdf"),
    ("ai_briefings.md", "ai_briefings.pdf"),
]

BROWSERS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]

CSS = """
@page { size: A4; margin: 16mm 16mm; }
body { font-family: "Segoe UI", system-ui, sans-serif; font-size: 10pt;
       line-height: 1.5; color: #12131a; max-width: 100%; }
h1 { font-size: 19pt; margin: 0 0 2mm; letter-spacing: -0.3pt; }
h2 { font-size: 12.5pt; margin: 7mm 0 2mm; padding-bottom: 1mm;
     border-bottom: 0.8pt solid #d8d8d4; color: #2a78d6; }
h3 { font-size: 10.5pt; margin: 5mm 0 1.5mm; }
p, li { margin: 0 0 2.4mm; }
code { font-family: Consolas, monospace; font-size: 9pt;
       background: #f4f4f2; padding: 0.3mm 1mm; border-radius: 1mm; }
pre { background: #f4f4f2; border-left: 2pt solid #2a78d6; padding: 2.5mm 3mm;
      overflow-x: auto; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 2mm 0 4mm; }
th { text-align: left; background: #f4f4f2; border-bottom: 0.8pt solid #d8d8d4;
     padding: 1.6mm 2mm; font-size: 8.4pt; text-transform: uppercase;
     letter-spacing: 0.4pt; color: #52514e; }
td { padding: 1.6mm 2mm; border-bottom: 0.5pt solid #ececea; }
blockquote { margin: 2mm 0; padding: 1.5mm 3mm; border-left: 2pt solid #eb6834;
             background: #fdf6f2; }
strong { font-weight: 650; }
"""


def find_browser() -> Path | None:
    for p in BROWSERS:
        if p.exists():
            return p
    for name in ("msedge", "chrome", "chromium"):
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def main() -> int:
    browser = find_browser()
    if browser is None:
        print("No Edge/Chrome found; cannot render PDF.", file=sys.stderr)
        return 1

    for src_name, out_name in TARGETS:
        src = DOCS / src_name
        if not src.exists():
            print(f"  skipped {src_name} (missing)")
            continue

        body = markdown.markdown(
            src.read_text(encoding="utf-8"),
            extensions=["tables", "fenced_code", "sane_lists"],
        )
        html = f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{body}"

        # Render from a temp file so the PDF lands beside the markdown cleanly.
        with tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(html)
            tmp = Path(fh.name)

        out = DOCS / out_name
        out.unlink(missing_ok=True)
        subprocess.run(
            [
                str(browser),
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={out}",
                "file:" + pathname2url(str(tmp)),
            ],
            check=False,
            capture_output=True,
            timeout=180,
        )
        tmp.unlink(missing_ok=True)

        if out.exists():
            pages = out.read_bytes().count(b"/Type /Page") or "?"
            print(f"  {out_name:<22} {out.stat().st_size / 1024:>6.0f} KB")
        else:
            print(f"  FAILED {out_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
