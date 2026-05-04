#!/usr/bin/env python3
"""
cleanup_old_injections.py
=========================
Strips the injections made by the FIRST run of fix_website.py so the
updated script can re-apply them correctly (nav after last <hr>, no gap).

Run this ONCE, then immediately run fix_website.py again.

Usage:
  cd C:\\Users\\berra\\Documents\\GitHub\\UnblockedGames-USA.github.io
  python cleanup_old_injections.py
  python fix_website.py
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

# ── patterns to erase ────────────────────────────────────────────────────────

# 1. The <style id="a11y-contrast-fix"> … </style> block
CSS_BLOCK_RE = re.compile(
    r'\s*<style\s+id=["\']a11y-contrast-fix["\'][^>]*>.*?</style>',
    re.DOTALL | re.IGNORECASE,
)

# 2. The <nav class="bottom-nav-bar" … </nav> block
NAV_BLOCK_RE = re.compile(
    r'\s*<nav\s+class=["\']bottom-nav-bar["\'][^>]*>.*?</nav>',
    re.DOTALL | re.IGNORECASE,
)

def clean_file(path: Path) -> bool:
    try:
        raw = path.read_bytes()
        try:
            html = raw.decode("utf-8");  enc = "utf-8"
        except UnicodeDecodeError:
            html = raw.decode("latin-1"); enc = "latin-1"

        cleaned = CSS_BLOCK_RE.sub("", html)
        cleaned = NAV_BLOCK_RE.sub("", cleaned)

        if cleaned != html:
            path.write_text(cleaned, encoding=enc)
            return True
        return False
    except Exception as e:
        print(f"  ERROR {path}: {e}")
        return False

def main():
    html_files = sorted(REPO_ROOT.rglob("*.html"))
    if not html_files:
        sys.exit("No .html files found — check REPO_ROOT.")

    changed = 0
    for f in html_files:
        if clean_file(f):
            print(f"  cleaned  {f.relative_to(REPO_ROOT)}")
            changed += 1

    print(f"\nDone. Stripped old injections from {changed} / {len(html_files)} files.")
    print("\nNow run:  python fix_website.py")

if __name__ == "__main__":
    main()
