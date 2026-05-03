#!/usr/bin/env python3
"""
fix_broken_pages.py — Unblocked Games USA
==========================================
Fixes ONLY game pages that were broken by the previous script.
A broken page = has <link rel="stylesheet" href="/assets/style.css"> 
but NO <style> block in <head> (the CSS was wiped).

Run from repo root:
  C:\\Users\\berra\\Documents\\GitHub\\UnblockedGames-USA.github.io

Usage:
  python fix_broken_pages.py           # dry-run
  python fix_broken_pages.py --write   # apply fixes
"""

import re, shutil, argparse
from pathlib import Path

SKIP_FOLDERS = {
    "assets","images","categ","css","js","fonts",
    "privacy-policy","contact","faq","dmca",
    ".git",".github","node_modules",
}

# The full CSS block that belongs in every game page head
# Copied exactly from a known-good page (basket-random, 12-mini-battles-2)
GAME_PAGE_CSS = """<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,sans-serif;background:#0a0e1a;color:#dce8ff;line-height:1.6;min-height:100vh}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.wrap{max-width:1280px;margin:0 auto;padding:0 16px}
.site-header{background:linear-gradient(90deg,#001a6e,#0d1f6e 40%,#1a0a2e 65%,#8b0000);
  border-bottom:3px solid #c0392b;position:sticky;top:0;z-index:100;
  box-shadow:0 4px 20px rgba(0,0,0,.7)}
.hdr-inner{display:flex;align-items:center;gap:12px;padding:10px 16px;flex-wrap:wrap}
.logo{font-weight:800;font-size:1.25rem;color:#fff;white-space:nowrap;text-shadow:0 0 16px rgba(192,57,43,.7)}
.logo:hover{text-shadow:0 0 24px rgba(192,57,43,1)}
.search-wrap{display:flex;position:relative;margin-left:auto}
.search-wrap input{padding:.4rem .9rem;border:1px solid rgba(255,255,255,.15);
  border-radius:20px 0 0 20px;background:rgba(255,255,255,.12);color:#fff;
  font-size:.88rem;width:200px;outline:none}
.search-wrap input::placeholder{color:rgba(255,255,255,.45)}
.search-wrap input:focus{background:rgba(255,255,255,.2);width:240px;transition:width .2s}
.search-wrap button{background:#c0392b;color:#fff;border:none;
  border-radius:0 20px 20px 0;padding:.4rem .9rem;cursor:pointer;font-size:.9rem}
#searchDrop{position:absolute;top:calc(100% + 6px);left:0;right:0;
  background:#0a1535;border:1px solid rgba(192,57,43,.3);border-radius:10px;
  max-height:280px;overflow-y:auto;z-index:300;display:none;
  box-shadow:0 8px 28px rgba(0,0,0,.8)}
#searchDrop.open{display:block}
#searchDrop a{display:flex;align-items:center;gap:10px;padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;font-weight:600}
#searchDrop a:hover{background:rgba(192,57,43,.2);color:#fff}
#searchDrop img{width:36px;height:26px;object-fit:cover;border-radius:4px;flex-shrink:0}
#searchDrop .no-res,.no-res{padding:12px;color:rgba(255,255,255,.4);text-align:center;font-size:.83rem}
.nav-toggle{display:none;background:none;border:none;color:#fff;font-size:1.4rem;cursor:pointer;padding:.3rem .5rem}
.main-nav{background:linear-gradient(90deg,#001050,#0d1560 40%,#1a0825 70%,#500010);
  border-top:1px solid rgba(255,255,255,.06)}
.main-nav ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;
  gap:4px;padding:8px 16px;max-width:1280px;margin:0 auto}
.main-nav a{color:rgba(255,255,255,.85);padding:4px 11px;border-radius:20px;
  font-size:.8rem;font-weight:600;border:1px solid transparent;white-space:nowrap;
  transition:background .15s,color .15s}
.main-nav a:hover,.main-nav a.active{background:rgba(192,57,43,.35);color:#fff;border-color:rgba(192,57,43,.4)}
.site-footer{background:#060b18;border-top:2px solid #c0392b;padding:28px 16px;margin-top:48px;text-align:center}
.footer-cats{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-bottom:14px}
.footer-cats a{background:rgba(255,255,255,.07);padding:4px 11px;border-radius:16px;font-size:.78rem}
.footer-cats a:hover{background:rgba(192,57,43,.3)}
.footer-links{display:flex;gap:16px;justify-content:center;margin-bottom:10px;font-size:.82rem;opacity:.7;flex-wrap:wrap}
.footer-links a:hover{opacity:1}
.footer-copy{font-size:.75rem;opacity:.35}
.games-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:16px 0}
.game-card{display:flex;flex-direction:column;background:#111827;border-radius:10px;
  overflow:hidden;border:1px solid rgba(255,255,255,.07);transition:transform .2s,box-shadow .2s,border-color .2s}
.game-card:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,0,0,.5);border-color:rgba(192,57,43,.4)}
.game-card img{width:100%;height:110px;object-fit:cover}
.game-card span{padding:7px 8px;font-size:.78rem;text-align:center;font-weight:500;line-height:1.3}
.game-section{padding:24px 0}
.game-title-bar{margin-bottom:16px}
.game-title-bar h1{font-size:clamp(1.4rem,3vw,2rem);font-weight:800;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.game-title-bar p{color:rgba(255,255,255,.55);margin-top:6px;font-size:.9rem}
.game-frame-wrap{position:relative;width:100%;aspect-ratio:16/9;background:#000;
  border-radius:12px;overflow:hidden;border:2px solid rgba(192,57,43,.3);margin-bottom:20px;max-height:600px}
.game-thumb{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1}
.game-overlay{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
  justify-content:center;z-index:2;cursor:pointer;background:rgba(0,0,0,.45);
  transition:background .2s}
.game-overlay:hover{background:rgba(0,0,0,.3)}
.play-btn{background:#c0392b;border:none;border-radius:50%;width:72px;height:72px;
  color:#fff;font-size:2rem;cursor:pointer;display:flex;align-items:center;
  justify-content:center;box-shadow:0 4px 20px rgba(192,57,43,.6);
  transition:transform .15s,box-shadow .15s}
.play-btn:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(192,57,43,.8)}
.play-label{color:#fff;font-weight:700;font-size:1rem;margin-top:10px;letter-spacing:.05em}
.game-frame{position:absolute;inset:0;width:100%;height:100%;border:none;display:none;z-index:3}
.game-frame.active{display:block}
.fs-btn{position:absolute;bottom:10px;right:10px;z-index:4;background:rgba(0,0,0,.6);
  color:#fff;border:1px solid rgba(255,255,255,.2);border-radius:6px;
  padding:5px 10px;font-size:.8rem;cursor:pointer}
.fs-btn:hover{background:rgba(192,57,43,.7)}
.game-desc{background:#111827;border-radius:12px;padding:20px;margin-bottom:20px;
  border:1px solid rgba(255,255,255,.07)}
.game-desc h2{font-size:1.1rem;font-weight:700;color:#4fa3ff;margin-bottom:10px}
.game-desc h3{font-size:.95rem;font-weight:600;color:#dce8ff;margin:12px 0 6px}
.game-desc p{color:rgba(255,255,255,.7);font-size:.88rem}
.game-thumb-sm{float:left;width:120px;height:80px;object-fit:cover;border-radius:8px;
  margin:0 16px 10px 0}
.cat-tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.cat-tag{background:rgba(192,57,43,.2);border:1px solid rgba(192,57,43,.3);
  padding:4px 12px;border-radius:16px;font-size:.78rem;font-weight:600}
.cat-tag:hover{background:rgba(192,57,43,.4)}
.similar-section{margin-bottom:20px}
.section-heading{font-size:1.1rem;font-weight:700;color:#4fa3ff;margin-bottom:12px}
.browse-section{margin:20px 0}
.browse-by-category{background:#111827;border-radius:12px;padding:20px;
  border:1px solid rgba(255,255,255,.07)}
.browse-by-category h2{font-size:1rem;font-weight:700;color:#4fa3ff;margin-bottom:12px}
.cat-pills{display:flex;flex-wrap:wrap;gap:8px}
.cat-pill{background:rgba(255,255,255,.07);padding:5px 13px;border-radius:16px;
  font-size:.8rem;font-weight:600;border:1px solid rgba(255,255,255,.1);
  transition:background .15s}
.cat-pill:hover{background:rgba(192,57,43,.3);border-color:rgba(192,57,43,.4)}
@media(max-width:900px){
  .nav-toggle{display:block}
  .main-nav ul{display:none;flex-direction:column;align-items:flex-start;padding:8px 16px}
  .main-nav ul.open{display:flex}
  .hdr-inner{flex-wrap:wrap}
  .search-wrap{order:3;width:100%}
  .search-wrap input{width:100%;border-radius:20px 0 0 20px}
}
@media(max-width:600px){
  .games-grid{grid-template-columns:repeat(2,1fr)}
  .logo{font-size:1.1rem}
  .game-thumb-sm{float:none;width:100%;height:auto;margin:0 0 12px}
}
</style>"""


def is_broken(html: str) -> bool:
    """
    A page is broken if it has /assets/style.css link
    but NO <style> block in the <head>.
    """
    has_css_link = 'href="/assets/style.css"' in html
    has_style_block = bool(re.search(r'<style[\s>]', html, re.IGNORECASE))
    return has_css_link and not has_style_block


def fix_page(html: str) -> str:
    """
    Replace <link rel="stylesheet" href="/assets/style.css">
    with the full inline <style> block.
    """
    return html.replace(
        '<link rel="stylesheet" href="/assets/style.css">',
        GAME_PAGE_CSS,
        1
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).parent.resolve()
    print(f"\n{'='*60}")
    print(f"  Fix Broken Game Pages")
    print(f"  Mode: {'WRITE' if args.write else 'DRY-RUN'}")
    print(f"{'='*60}\n")

    broken_count = 0
    fixed_count  = 0

    folders = sorted(
        [f for f in root.iterdir()
         if f.is_dir() and f.name not in SKIP_FOLDERS and not f.name.startswith(".")],
        key=lambda f: f.name
    )

    for folder in folders:
        index = folder / "index.html"
        if not index.exists():
            continue

        html = index.read_text(encoding="utf-8", errors="replace")

        if not is_broken(html):
            continue

        broken_count += 1
        new_html = fix_page(html)

        if args.write:
            index.write_text(new_html, encoding="utf-8")
            print(f"  ✓ FIXED   {folder.name}")
            fixed_count += 1
        else:
            print(f"  ⚠ BROKEN  {folder.name}  (would fix)")

    print(f"\n{'='*60}")
    if not args.write:
        print(f"  Found {broken_count} broken pages.")
        print(f"  Run with --write to fix them all.")
    else:
        print(f"  Fixed {fixed_count} pages.")
        print(f"\n  Now push:")
        print(f"     git add -A")
        print(f'     git commit -m "fix: restore CSS on broken game pages"')
        print(f"     git push origin main")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
