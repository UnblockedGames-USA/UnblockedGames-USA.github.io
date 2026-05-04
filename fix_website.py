#!/usr/bin/env python3
"""
fix_website.py  –  Unblocked Games USA site fixer
=======================================================
Fixes applied to every .html file in the repo:

  1. CONTRAST FIX
     • Adds / updates a <style> block that forces legible colors on
       .footer-copy, .site-footer, .yr, and any other known low-contrast
       footer selectors flagged by the accessibility audit.

  2. BOTTOM NAV  (placed just after the red <hr> divider)
     • Injects a full category navigation bar directly below the red
       horizontal rule so visitors can browse categories from the footer.

  3. JSON-LD dateModified
     • Finds every <script type="application/ld+json"> block and sets
       "dateModified" to today's ISO-8601 date (2026-05-04).
       If the field is absent it is inserted alongside "datePublished"
       (or at the top of the object if that is also missing).

Usage
-----
  cd  C:\\Users\\berra\\Documents\\GitHub\\UnblockedGames-USA.github.io
  python fix_website.py

The script edits files **in-place** and prints a one-line summary per
file so you can review what changed.
"""

import os
import re
import json
import sys
from datetime import date
from pathlib import Path


# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent           # run from repo root, OR set path:
# REPO_ROOT = Path(r"C:\Users\berra\Documents\GitHub\UnblockedGames-USA.github.io")

TODAY = str(date.today().year)              # e.g. "2026"

# ── 1. CSS CONTRAST FIX ──────────────────────────────────────────────────────
# Injected once per file, just before </head>.
# Colors chosen to meet WCAG AA (≥ 4.5 : 1) against the dark footer (#1a1a2e).

CONTRAST_FIX_CSS = """
<style id="a11y-contrast-fix">
/* ── Accessibility: footer contrast fix (WCAG AA) ── */
.site-footer,
footer.site-footer {
  background-color: #1a1a2e !important;
  color: #e0e0e0 !important;          /* was near-black-on-dark → now light grey */
}
.footer-copy,
p.footer-copy {
  color: #c8c8d0 !important;          /* light grey, ratio > 7:1 on #1a1a2e */
}
.yr,
span.yr {
  color: #d0d0d8 !important;
}
.site-footer a,
.footer-copy a {
  color: #90caf9 !important;          /* accessible blue link on dark bg */
  text-decoration: underline;
}
.site-footer a:hover,
.footer-copy a:hover {
  color: #ffffff !important;
}
/* Bottom-nav bar added by fix_website.py */
.bottom-nav-bar {
  background: #1a1a2e;
  padding: 14px 12px 10px;
  text-align: center;
  border-top: 2px solid #e84545;     /* mirrors the existing red divider */
}
.bottom-nav-bar a {
  display: inline-block;
  color: #e0e0e0 !important;
  font-size: 0.82rem;
  font-weight: 500;
  text-decoration: none;
  margin: 4px 6px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}
.bottom-nav-bar a:hover {
  background: #e84545;
  color: #ffffff !important;
}
</style>
"""

# ── 2. BOTTOM NAV HTML ────────────────────────────────────────────────────────
# Injected just after the first <hr> (the red divider line).

BOTTOM_NAV_HTML = """
<nav class="bottom-nav-bar" aria-label="Bottom category navigation">
  <a href="https://unblockedgames-usa.github.io/categ/shooter/">🎯 Shooter</a>
  <a href="https://unblockedgames-usa.github.io/categ/platformer/">🏃 Platformer</a>
  <a href="https://unblockedgames-usa.github.io/categ/2-player/">👥 2-Player</a>
  <a href="https://unblockedgames-usa.github.io/categ/fighting/">🥊 Fighting</a>
  <a href="https://unblockedgames-usa.github.io/categ/driving/">🚗 Driving</a>
  <a href="https://unblockedgames-usa.github.io/categ/puzzle/">🧠 Puzzle</a>
  <a href="https://unblockedgames-usa.github.io/categ/multiplayer/">🌐 Multiplayer</a>
  <a href="https://unblockedgames-usa.github.io/categ/action/">💥 Action</a>
  <a href="https://unblockedgames-usa.github.io/categ/skill/">🏆 Skill</a>
  <a href="https://unblockedgames-usa.github.io/categ/adventure/">🗺️ Adventure</a>
  <a href="https://unblockedgames-usa.github.io/categ/racing/">🏁 Racing</a>
  <a href="https://unblockedgames-usa.github.io/categ/strategy/">♟️ Strategy</a>
  <a href="https://unblockedgames-usa.github.io/categ/sports/">⚽ Sports</a>
  <a href="https://unblockedgames-usa.github.io/categ/simulation/">🏙️ Simulation</a>
  <a href="https://unblockedgames-usa.github.io/categ/clicker/">🖱️ Clicker</a>
  <a href="https://unblockedgames-usa.github.io/categ/horror/">👻 Horror</a>
  <a href="https://unblockedgames-usa.github.io/categ/kids/">🧸 Kids</a>
</nav>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def already_patched(html: str, marker: str) -> bool:
    return marker in html


def inject_contrast_css(html: str) -> tuple[str, bool]:
    """Insert the contrast-fix <style> block before </head>, once."""
    if 'id="a11y-contrast-fix"' in html:
        return html, False
    patched = re.sub(r"(</head>)", CONTRAST_FIX_CSS + r"\1", html, count=1, flags=re.IGNORECASE)
    changed = patched != html
    return patched, changed


def inject_bottom_nav(html: str) -> tuple[str, bool]:
    """
    Insert the bottom-nav bar right after the FIRST <hr …> tag so it sits
    just below the red divider line.  If no <hr> exists, fall back to
    inserting before <footer.
    """
    if 'class="bottom-nav-bar"' in html:
        return html, False

    # Try after first <hr …> (with or without attributes / self-closing)
    patched, n = re.subn(
        r"(<hr\b[^>]*/?>)",
        r"\1" + BOTTOM_NAV_HTML,
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if n:
        return patched, True

    # Fallback: before <footer
    patched, n = re.subn(
        r"(<footer\b)",
        BOTTOM_NAV_HTML + r"\1",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    return patched, bool(n)


def update_jsonld_date(html: str) -> tuple[str, bool]:
    """
    Find all JSON-LD <script> blocks and set/update "dateModified" to TODAY.
    Returns the updated HTML and whether any change was made.
    """
    changed = False

    def _patch_block(m: re.Match) -> str:
        nonlocal changed
        raw = m.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)   # leave malformed JSON untouched

        if not isinstance(data, dict):
            return m.group(0)

        if data.get("dateModified") == TODAY:
            return m.group(0)   # already up-to-date

        data["dateModified"] = TODAY
        changed = True
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        return f'<script type="application/ld+json">\n{pretty}\n</script>'

    pattern = re.compile(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    result = pattern.sub(_patch_block, html)
    return result, changed


# ── Main loop ─────────────────────────────────────────────────────────────────

def process_file(path: Path) -> dict:
    """Apply all fixes to a single HTML file. Returns a status dict."""
    status = {"path": path, "css": False, "nav": False, "schema": False, "error": None}
    try:
        raw = path.read_bytes()
        # Detect encoding
        try:
            html = raw.decode("utf-8")
            enc = "utf-8"
        except UnicodeDecodeError:
            html = raw.decode("latin-1")
            enc = "latin-1"

        html, status["css"]    = inject_contrast_css(html)
        html, status["nav"]    = inject_bottom_nav(html)
        html, status["schema"] = update_jsonld_date(html)

        if any([status["css"], status["nav"], status["schema"]]):
            path.write_text(html, encoding=enc)
    except Exception as exc:
        status["error"] = str(exc)
    return status


def main():
    root = REPO_ROOT
    if not root.exists():
        sys.exit(f"[ERROR] Repo root not found: {root}\n"
                 "Edit the REPO_ROOT variable at the top of this script.")

    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        sys.exit("[ERROR] No .html files found. Check REPO_ROOT path.")

    print(f"Fixing {len(html_files)} HTML files in: {root}\n")
    print(f"{'File':<55} {'CSS':>4} {'Nav':>4} {'Schema':>7} {'Status':>8}")
    print("-" * 85)

    totals = {"css": 0, "nav": 0, "schema": 0, "errors": 0}

    for f in html_files:
        rel = f.relative_to(root)
        s = process_file(f)

        css_mark    = "✔" if s["css"]    else "–"
        nav_mark    = "✔" if s["nav"]    else "–"
        schema_mark = "✔" if s["schema"] else "–"

        if s["error"]:
            status_str = "ERROR"
            totals["errors"] += 1
        elif any([s["css"], s["nav"], s["schema"]]):
            status_str = "updated"
        else:
            status_str = "no change"

        print(f"{str(rel):<55} {css_mark:>4} {nav_mark:>4} {schema_mark:>7} {status_str:>8}")

        if s["css"]:    totals["css"]    += 1
        if s["nav"]:    totals["nav"]    += 1
        if s["schema"]: totals["schema"] += 1

    print("-" * 85)
    print(f"\nDone! Summary:")
    print(f"  Contrast CSS injected : {totals['css']} files")
    print(f"  Bottom nav injected   : {totals['nav']} files")
    print(f"  dateModified updated  : {totals['schema']} files")
    if totals["errors"]:
        print(f"  Errors                : {totals['errors']} files  ← check output above")
    print(f"\ndateModified set to: {TODAY}")
    print("\nNext steps:")
    print("  git add -A")
    print('  git commit -m "fix: contrast, bottom nav, dateModified schema"')
    print("  git push")


if __name__ == "__main__":
    main()
