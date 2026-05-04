#!/usr/bin/env python3
"""
fix_header_final.py — run from repo root
- Removes ALL previously injected style tags (Mobile nav fix, Similar games fix)
- Replaces main style tag nav/header CSS with clean version:
    * Logo + search bar on top row
    * Nav pills ALWAYS visible below the red line (no hamburger ever)
    * On mobile: nav scrolls horizontally in one row (no wrap, no hamburger)
    * Removes nav-toggle button from HTML entirely
    * Google-friendly: no layout shift, no CLS issues
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(".")
DRY_RUN   = False
SKIP      = {".git", "node_modules", ".github"}

# ── The one canonical header/nav CSS block ───────────────────────────────────
HEADER_CSS = """
/* ══ HEADER & NAV — canonical, mobile-first ══ */
.site-header{
  background:linear-gradient(90deg,#001a6e,#0d1f6e 40%,#1a0a2e 65%,#8b0000);
  border-bottom:3px solid #c0392b;
  position:sticky;top:0;z-index:100;
  box-shadow:0 4px 20px rgba(0,0,0,.7);
}
.hdr-inner{
  display:flex;align-items:center;gap:12px;
  padding:10px 16px;max-width:1280px;margin:0 auto;
}
.logo{
  font-weight:800;font-size:1.25rem;color:#fff;
  white-space:nowrap;text-shadow:0 0 16px rgba(192,57,43,.7);flex-shrink:0;
}
.logo:hover{text-shadow:0 0 24px rgba(192,57,43,1)}
.search-wrap{
  display:flex;position:relative;margin-left:auto;
}
.search-wrap input{
  padding:.4rem .9rem;
  border:1px solid rgba(255,255,255,.15);
  border-radius:20px 0 0 20px;
  background:rgba(255,255,255,.12);color:#fff;
  font-size:.88rem;width:180px;outline:none;
}
.search-wrap input::placeholder{color:rgba(255,255,255,.45)}
.search-wrap input:focus{background:rgba(255,255,255,.2);width:220px;transition:width .2s}
.search-wrap button{
  background:#c0392b;color:#fff;border:none;
  border-radius:0 20px 20px 0;padding:.4rem .9rem;
  cursor:pointer;font-size:.9rem;flex-shrink:0;
}

/* Nav — always visible, scrolls horizontally on small screens */
.nav-toggle{display:none!important}
.main-nav{
  background:linear-gradient(90deg,#001050,#0d1560 40%,#1a0825 70%,#500010);
  border-top:1px solid rgba(255,255,255,.06);
}
.main-nav ul{
  list-style:none;
  display:flex!important;        /* always shown */
  flex-wrap:nowrap;              /* single row */
  overflow-x:auto;               /* scroll on mobile */
  -webkit-overflow-scrolling:touch;
  scrollbar-width:none;          /* hide scrollbar Firefox */
  gap:4px;padding:7px 12px;
  max-width:1280px;margin:0 auto;
}
.main-nav ul::-webkit-scrollbar{display:none}  /* hide scrollbar Chrome */
.main-nav a{
  color:rgba(255,255,255,.85);
  padding:5px 12px;border-radius:20px;
  font-size:.8rem;font-weight:600;
  border:1px solid transparent;white-space:nowrap;
  flex-shrink:0;
  transition:background .15s,color .15s;
}
.main-nav a:hover,.main-nav a.active{
  background:rgba(192,57,43,.35);color:#fff;
  border-color:rgba(192,57,43,.4);
}

/* Search dropdown */
#searchDrop{
  position:absolute;top:calc(100% + 6px);left:0;right:0;
  background:#0a1535;border:1px solid rgba(192,57,43,.3);
  border-radius:10px;max-height:280px;overflow-y:auto;
  z-index:300;display:none;box-shadow:0 8px 28px rgba(0,0,0,.8);
}
#searchDrop.open{display:block}
#searchDrop a{
  display:flex;align-items:center;gap:10px;padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,.06);
  font-size:.85rem;font-weight:600;
}
#searchDrop a:hover{background:rgba(192,57,43,.2);color:#fff}
#searchDrop img{width:36px;height:26px;object-fit:cover;border-radius:4px;flex-shrink:0}
#searchDrop .no-res{
  padding:12px;color:rgba(255,255,255,.4);
  text-align:center;font-size:.83rem;
}

/* Mobile tweaks */
@media(max-width:600px){
  .logo{font-size:1rem}
  .hdr-inner{padding:8px 12px;gap:8px}
  .search-wrap input{width:130px}
  .search-wrap input:focus{width:160px}
}
/* ══ END HEADER & NAV ══ */
"""

# Markers from previous injected style blocks to remove entirely
INJECTED_MARKERS = [
    "Mobile nav fix",
    "Similar games tighter spacing",
    "Compact iframe",
    "max-height:520px",
]

def page_type(path: Path):
    parts = path.relative_to(REPO_ROOT).parts
    if parts == ("index.html",):                           return "home"
    if parts[0] == "categ":                                return "categ"
    skip = {"privacy-policy","contact","faq","dmca","about"}
    if len(parts)==2 and parts[1]=="index.html" and parts[0] not in skip:
        return "game"
    return "other"

def process(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    original = str(soup)

    # 1. Remove nav-toggle button from HTML
    for btn in soup.find_all("button", id="navToggle"):
        btn.decompose()

    # 2. Make sure navMenu ul is always visible (remove any inline display:none)
    nav_ul = soup.find("ul", id="navMenu")
    if nav_ul and nav_ul.get("style"):
        nav_ul["style"] = ""

    # 3. Remove previously injected <style> blocks (from old fix scripts)
    for style in soup.find_all("style"):
        content = style.string or ""
        if any(marker in content for marker in INJECTED_MARKERS):
            style.decompose()

    # 4. In the FIRST main style tag, replace the header/nav CSS section
    first_style = soup.find("style")
    if first_style and first_style.string:
        css = first_style.string

        # Remove old nav-toggle media query blocks
        css = re.sub(
            r'@media\s*\(max-width:\s*900px\)\s*\{[^}]*nav-toggle[^}]*\}[^}]*\}',
            '', css, flags=re.DOTALL
        )
        css = re.sub(
            r'@media\s*\(max-width:\s*[69]\d\dpx\)\s*\{[^{]*nav-toggle[^}]*\}[^}]*\}[^}]*\}',
            '', css, flags=re.DOTALL
        )

        # Remove old .nav-toggle, .main-nav, .site-header, .hdr-inner, .search-wrap,
        # .logo, #searchDrop rules — we'll replace them with HEADER_CSS
        patterns_to_remove = [
            r'\.nav-toggle\{[^}]*\}',
            r'\.main-nav\{[^}]*\}',
            r'\.main-nav\s+ul\{[^}]*\}',
            r'\.main-nav\s+a\{[^}]*\}',
            r'\.main-nav\s+a:[^{]+\{[^}]*\}',
            r'\.site-header\{[^}]*\}',
            r'\.hdr-inner\{[^}]*\}',
            r'\.logo\{[^}]*\}',
            r'\.logo:[^{]+\{[^}]*\}',
            r'\.search-wrap\{[^}]*\}',
            r'\.search-wrap\s+input\{[^}]*\}',
            r'\.search-wrap\s+input:[^{]+\{[^}]*\}',
            r'\.search-wrap\s+button\{[^}]*\}',
            r'#searchDrop\{[^}]*\}',
            r'#searchDrop\.open\{[^}]*\}',
            r'#searchDrop\s+a\{[^}]*\}',
            r'#searchDrop\s+a:[^{]+\{[^}]*\}',
            r'#searchDrop\s+img\{[^}]*\}',
            r'#searchDrop\s+\.[^{]+\{[^}]*\}',
        ]
        for pat in patterns_to_remove:
            css = re.sub(pat, '', css, flags=re.DOTALL)

        # Append clean header CSS
        first_style.string = css + HEADER_CSS

    # 5. Iframe height cap — inject once in <head> for game pages
    ptype = page_type(path)
    if ptype == "game":
        head = soup.find("head")
        if head and "game-frame-wrap" not in "".join(
            (s.string or "") for s in head.find_all("style")
            if "max-height" in (s.string or "")
        ):
            st = soup.new_tag("style")
            st.string = (
                ".game-frame-wrap{"
                "aspect-ratio:16/9;max-height:520px;width:100%;"
                "position:relative;background:#000;border-radius:12px;"
                "overflow:hidden;border:2px solid rgba(192,57,43,.3);margin-bottom:16px"
                "}"
                "@media(max-width:768px){.game-frame-wrap{max-height:56vw}}"
            )
            head.append(st)

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
    counts = {"changed":0,"errors":0}
    for f in sorted(files):
        try:
            if process(f):
                counts["changed"] += 1
                print(f"  ✓  {f.relative_to(REPO_ROOT)}")
        except Exception as e:
            counts["errors"] += 1
            print(f"  ✗  {f.relative_to(REPO_ROOT)}: {e}")
    print(f"\nDone — {counts['changed']} changed, {counts['errors']} errors.")

if __name__ == "__main__":
    main()
