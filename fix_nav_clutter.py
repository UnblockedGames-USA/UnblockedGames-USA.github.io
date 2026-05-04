#!/usr/bin/env python3
"""
fix_nav_clutter.py  —  run from repo root
Fixes ONLY:
  1. Game pages  — remove .browse-section (redundant category pills, nav already shows them)
  2. Home page   — remove .cat-browse section (same reason)
  3. Category pages — remove footer-cats from footer IF they got re-added
  4. All pages   — inject iframe max-height cap via CSS (game pages only)
"""

from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(".")
DRY_RUN   = False

SKIP = {".git", "node_modules", ".github"}

def page_type(path: Path):
    parts = path.relative_to(REPO_ROOT).parts
    if parts == ("index.html",):                          return "home"
    if parts[0] == "categ":                               return "categ"
    skip = {"privacy-policy","contact","faq","dmca","about"}
    if len(parts)==2 and parts[1]=="index.html" and parts[0] not in skip:
        return "game"
    return "other"

def process(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    original = str(soup)
    ptype = page_type(path)

    # ── GAME pages ────────────────────────────────────────────────────────────
    if ptype == "game":
        # 1. Remove the "Browse by Category" box (class browse-section wraps it)
        for tag in soup.find_all("div", class_="browse-section"):
            tag.decompose()
        # Also catch if it's directly a section.browse-by-category not wrapped
        for tag in soup.find_all("section", class_="browse-by-category"):
            tag.decompose()

        # 2. Ensure iframe height is capped — inject CSS in <head> if not already there
        head = soup.find("head")
        marker = "max-height:520px"
        if head and marker not in str(head):
            style = soup.new_tag("style")
            style.string = (
                ".game-frame-wrap{"
                "aspect-ratio:16/9;"
                "max-height:520px;"
                "width:100%;"
                "position:relative;"
                "background:#000;"
                "border-radius:12px;"
                "overflow:hidden;"
                "border:2px solid rgba(192,57,43,.3);"
                "margin-bottom:16px"
                "}"
                "@media(max-width:768px){"
                ".game-frame-wrap{max-height:56vw}"
                "}"
            )
            head.append(style)

    # ── HOME page ─────────────────────────────────────────────────────────────
    elif ptype == "home":
        # Remove "Browse by Category" pills (cat-browse div + its preceding h2)
        cat_browse = soup.find("div", class_="cat-browse")
        if cat_browse:
            # Remove the h2 right before it too
            prev = cat_browse.find_previous_sibling(["h2","h3"])
            if prev and ("browse" in prev.get_text().lower() or "categor" in prev.get_text().lower()):
                prev.decompose()
            cat_browse.decompose()

        # Remove footer-cats in footer (empty or populated)
        footer = soup.find("footer")
        if footer:
            for d in footer.find_all("div", class_="footer-cats"):
                d.decompose()

    # ── CATEGORY pages ────────────────────────────────────────────────────────
    elif ptype == "categ":
        # Remove footer-cats if present
        footer = soup.find("footer")
        if footer:
            for d in footer.find_all("div", class_="footer-cats"):
                d.decompose()
        # Remove "other-cats" div if still present
        for d in soup.find_all("div", class_="other-cats"):
            d.decompose()

    new_html = str(soup)
    if new_html == original:
        return False
    if not DRY_RUN:
        path.write_text(new_html, encoding="utf-8")
    return True


def main():
    files = [p for p in REPO_ROOT.rglob("*.html")
             if not (set(p.parts) & SKIP)]
    print(f"Scanning {len(files)} files…\n")
    changed = errors = 0
    for f in sorted(files):
        try:
            if process(f):
                changed += 1
                print(f"  ✓  [{page_type(f):6}]  {f.relative_to(REPO_ROOT)}")
        except Exception as e:
            errors += 1
            print(f"  ✗  {f.relative_to(REPO_ROOT)}: {e}")
    print(f"\nDone — {changed} changed, {errors} errors.")

if __name__ == "__main__":
    main()
