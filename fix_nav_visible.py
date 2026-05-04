#!/usr/bin/env python3
"""
fix_nav_visible.py — run from repo root
Surgical fix: injects a single <style> tag into every page that forces
the nav ul to always be visible (overrides the old .open class logic).
Also removes the nav-toggle button if still present.
"""

from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(".")
DRY_RUN   = False
SKIP      = {".git", "node_modules", ".github"}

# One tiny CSS block — forces nav always visible, horizontal scroll on mobile
NAV_FIX_CSS = """<style id="nav-fix">
.nav-toggle{display:none!important}
#navMenu{
  display:flex!important;
  flex-wrap:nowrap!important;
  overflow-x:auto!important;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:none;
  gap:4px;
  padding:7px 12px!important;
  list-style:none;
  max-width:1280px;
  margin:0 auto;
  align-items:center;
}
#navMenu::-webkit-scrollbar{display:none}
#navMenu li{flex-shrink:0}
#navMenu a{
  white-space:nowrap;
  flex-shrink:0;
  padding:5px 12px;
  border-radius:20px;
  font-size:.8rem;
  font-weight:600;
  color:rgba(255,255,255,.85);
  border:1px solid transparent;
}
#navMenu a:hover,#navMenu a.active{
  background:rgba(192,57,43,.35);
  color:#fff;
  border-color:rgba(192,57,43,.4);
}
</style>"""

def process(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")

    # Skip if already has our fix
    if 'id="nav-fix"' in html or "id='nav-fix'" in html:
        return False

    # Only process pages that have the navMenu
    if 'id="navMenu"' not in html and "id='navMenu'" not in html:
        return False

    soup = BeautifulSoup(html, "html.parser")

    # Remove nav-toggle button
    for btn in soup.find_all("button", id="navToggle"):
        btn.decompose()

    # Inject our fix CSS right before </head>
    head = soup.find("head")
    if not head:
        return False

    fix_style = BeautifulSoup(NAV_FIX_CSS, "html.parser")
    head.append(fix_style)

    new_html = str(soup)
    if new_html == html:
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
                print(f"  ✓  {f.relative_to(REPO_ROOT)}")
        except Exception as e:
            errors += 1
            print(f"  ✗  {f.relative_to(REPO_ROOT)}: {e}")
    print(f"\nDone — {changed} changed, {errors} errors.")

if __name__ == "__main__":
    main()
