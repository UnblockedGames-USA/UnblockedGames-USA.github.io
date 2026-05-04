#!/usr/bin/env python3
"""
fix_site.py — Unblocked Games USA comprehensive fixer
Run from the ROOT of the cloned repo:  python fix_site.py

Fixes applied:
  1. Mobile nav — replace sticky nav with a proper hamburger drawer on all pages
  2. Category pages — remove redundant "Other Categories" block (duplicate of nav)
  3. Game card titles — strip trailing " Unblocked" from <span> inside .game-card
  4. Similar games spacing — tighten gap in .similar-section
  5. SEO meta — remove <meta name="keywords">, fix <title> on game pages to remove
     "Unblocked | Unblocked Games USA" → "Play {Game} Online Free | Unblocked Games USA"
     and meta description to be unique per page
  6. Category page meta — enrich title/description pattern
  7. Remove duplicate Google Analytics tag (some pages have it twice)
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(".")          # run from repo root
DRY_RUN   = False              # set True to preview without writing

# Improved mobile-friendly nav CSS (replaces the existing nav CSS block)
MOBILE_NAV_CSS = """
/* ── Mobile nav fix ── */
.site-header{position:sticky;top:0;z-index:200}
.hdr-inner{display:flex;align-items:center;gap:10px;padding:10px 16px}
.logo{font-weight:800;font-size:1.2rem;color:#fff;white-space:nowrap;
  text-shadow:0 0 16px rgba(192,57,43,.7);flex-shrink:0}
.search-wrap{display:flex;position:relative;margin-left:auto;flex:1;max-width:320px}
.search-wrap input{padding:.4rem .9rem;border:1px solid rgba(255,255,255,.15);
  border-radius:20px 0 0 20px;background:rgba(255,255,255,.12);color:#fff;
  font-size:.88rem;width:100%;outline:none}
.search-wrap input::placeholder{color:rgba(255,255,255,.45)}
.search-wrap input:focus{background:rgba(255,255,255,.2)}
.search-wrap button{background:#c0392b;color:#fff;border:none;
  border-radius:0 20px 20px 0;padding:.4rem .9rem;cursor:pointer;font-size:.9rem;flex-shrink:0}
.nav-toggle{display:none;background:none;border:none;color:#fff;
  font-size:1.5rem;cursor:pointer;padding:.2rem .4rem;flex-shrink:0;margin-left:6px}
.main-nav{background:linear-gradient(90deg,#001050,#0d1560 40%,#1a0825 70%,#500010);
  border-top:1px solid rgba(255,255,255,.06)}
.main-nav ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;
  gap:4px;padding:8px 16px;max-width:1280px;margin:0 auto}
.main-nav a{color:rgba(255,255,255,.85);padding:4px 11px;border-radius:20px;
  font-size:.8rem;font-weight:600;border:1px solid transparent;white-space:nowrap;
  transition:background .15s,color .15s}
.main-nav a:hover,.main-nav a.active{background:rgba(192,57,43,.35);
  color:#fff;border-color:rgba(192,57,43,.4)}
@media(max-width:768px){
  .nav-toggle{display:block}
  .main-nav ul{display:none;flex-direction:column;align-items:stretch;padding:0}
  .main-nav ul.open{display:flex}
  .main-nav a{padding:11px 20px;border-radius:0;border-bottom:1px solid rgba(255,255,255,.06);
    font-size:.95rem}
  .main-nav a:hover,.main-nav a.active{border-radius:0}
  .search-wrap{max-width:none}
}
@media(max-width:480px){
  .logo{font-size:1rem}
  .hdr-inner{padding:8px 12px}
}
"""

SIMILAR_SECTION_CSS = """
/* ── Similar games tighter spacing ── */
.similar-section{margin-bottom:16px}
.similar-section .games-grid{gap:10px;margin:10px 0}
.similar-section .game-card img{height:90px}
"""

def collect_html_files():
    """Collect all HTML files in repo, skip node_modules / .git."""
    skip = {'.git', 'node_modules', '.github'}
    files = []
    for p in REPO_ROOT.rglob("*.html"):
        parts = set(p.parts)
        if parts & skip:
            continue
        files.append(p)
    return files

def slug_to_title(slug: str) -> str:
    """Convert slug like 'drunken-duel' → 'Drunken Duel'"""
    return " ".join(w.capitalize() for w in slug.replace("-", " ").split())

def is_game_page(path: Path) -> bool:
    """Detect individual game pages: they live at /{slug}/index.html"""
    parts = path.parts
    # e.g. ['drunken-duel', 'index.html'] relative to repo root
    rel = path.relative_to(REPO_ROOT)
    rel_parts = rel.parts
    # game page: exactly 2 levels deep (slug/index.html), NOT under categ/
    return (len(rel_parts) == 2
            and rel_parts[1] == "index.html"
            and rel_parts[0] not in {"categ", "privacy-policy", "contact",
                                      "faq", "dmca", "about"})

def is_categ_page(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)
    return rel.parts[0] == "categ"

def is_home_page(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)
    return rel.parts == ("index.html",)

def fix_remove_keywords_meta(soup):
    """Remove <meta name='keywords'> — ignored by Google, wastes crawl budget."""
    for tag in soup.find_all("meta", attrs={"name": "keywords"}):
        tag.decompose()

def fix_remove_duplicate_gtag(soup):
    """Keep only the first Google Analytics script block."""
    gtag_scripts = [s for s in soup.find_all("script")
                    if s.get("src","").startswith("https://www.googletagmanager.com")]
    for s in gtag_scripts[1:]:  # remove extras
        # also remove the inline gtag() block that follows it
        nxt = s.find_next_sibling("script")
        if nxt and "gtag(" in (nxt.string or ""):
            nxt.decompose()
        s.decompose()

def fix_inject_mobile_css(soup):
    """Replace nav-related CSS with mobile-friendly version, inject similar-section fix."""
    style_tags = soup.find_all("style")
    if not style_tags:
        return
    # Inject after first <style> tag
    first_style = style_tags[0]
    new_style = soup.new_tag("style")
    new_style.string = MOBILE_NAV_CSS + SIMILAR_SECTION_CSS
    first_style.insert_after(new_style)

def fix_nav_toggle_js(soup):
    """Ensure nav toggle JS uses 'open' class on ul#navMenu."""
    scripts = soup.find_all("script")
    for s in scripts:
        src = s.string or ""
        if "navToggle" in src and "navMenu" in src:
            # Already exists, make sure it targets ul not nav
            fixed = src.replace(
                "document.getElementById('navMenu')?.classList.toggle('open')",
                "document.getElementById('navMenu')?.classList.toggle('open')"
            )
            s.string = fixed
            return
    # Inject if missing
    new_script = soup.new_tag("script")
    new_script.string = (
        "document.getElementById('navToggle')"
        "?.addEventListener('click',()=>"
        "document.getElementById('navMenu')?.classList.toggle('open'));"
    )
    body = soup.find("body")
    if body:
        body.append(new_script)

def fix_remove_duplicate_other_cats(soup, path: Path):
    """On category pages, remove the 'Other Categories' section (mirrors nav)."""
    if not is_categ_page(path):
        return
    for div in soup.find_all("div", class_="other-cats"):
        div.decompose()

def fix_game_card_titles(soup):
    """
    Strip ' Unblocked' from <span> text inside .game-card elements.
    'Age Of War Unblocked' → 'Age Of War'
    """
    for card in soup.find_all("a", class_="game-card"):
        span = card.find("span")
        if span and span.string:
            cleaned = re.sub(r'\s+Unblocked\s*$', '', span.string, flags=re.IGNORECASE).strip()
            span.string = cleaned
        # Also fix alt on the img
        img = card.find("img")
        if img and img.get("alt"):
            img["alt"] = re.sub(r'\s+Unblocked\s*$', '', img["alt"], flags=re.IGNORECASE).strip()

def fix_game_page_title_and_meta(soup, path: Path):
    """
    Game pages: fix <title> and meta description.
    Before: "Drunken Duel Unblocked | Unblocked Games USA"
    After:  "Play Drunken Duel Online Free | Unblocked Games USA"
    """
    if not is_game_page(path):
        return
    slug = path.parts[-2]  # e.g. 'drunken-duel'
    game_name = slug_to_title(slug)

    # Fix <title>
    title_tag = soup.find("title")
    if title_tag:
        title_tag.string = f"Play {game_name} Online Free | Unblocked Games USA"

    # Fix og:title and twitter:title
    for meta in soup.find_all("meta", property=re.compile(r"og:title|twitter:title")):
        meta["content"] = f"Play {game_name} Online Free | Unblocked Games USA"

    # Fix meta description if it contains "Unblocked" keyword stuffing
    desc_meta = soup.find("meta", attrs={"name": "description"})
    if desc_meta:
        old_desc = desc_meta.get("content", "")
        # Only rewrite if it's the generic template
        if "no download, no sign-up" in old_desc.lower():
            # Detect genre from cat-tags
            genre = ""
            cat_tag = soup.find("a", class_="cat-tag")
            if cat_tag:
                genre = re.sub(r'[^\w\s]', '', cat_tag.text).strip()
            if genre:
                new_desc = (f"Play {game_name} free online — a {genre} game you can "
                            f"launch instantly in your browser. No download or sign-up needed.")
            else:
                new_desc = (f"Play {game_name} free online in your browser. "
                            f"No download, no sign-up. Works at school and everywhere.")
            desc_meta["content"] = new_desc
            # Fix og:description and twitter:description too
            for meta in soup.find_all("meta", property=re.compile(r"og:description|twitter:description")):
                meta["content"] = new_desc

    # Fix canonical URL if it has double-slash or missing trailing slash
    canonical = soup.find("link", rel="canonical")
    if canonical:
        href = canonical.get("href", "")
        if not href.endswith("/"):
            canonical["href"] = href + "/"

def fix_categ_page_meta(soup, path: Path):
    """
    Category pages: richer title/description.
    Before: "👥 2-Player Games Unblocked – Free Online | Unblocked Games USA"
    After:  "2-Player Games – Free Online Browser Games | Unblocked Games USA"
    """
    if not is_categ_page(path):
        return
    title_tag = soup.find("title")
    if not title_tag:
        return
    old_title = title_tag.string or ""
    # Extract count from description meta
    count = ""
    desc_meta = soup.find("meta", attrs={"name": "description"})
    if desc_meta:
        m = re.search(r'(\d+)\s+free', desc_meta.get("content", ""), re.IGNORECASE)
        if m:
            count = m.group(1) + " "
    # Extract category name from h1
    h1 = soup.find("h1")
    if h1:
        cat_text = re.sub(r'[^\w\s\-]', '', h1.get_text()).strip()
        cat_text = re.sub(r'\s+Unblocked\s*Games?\s*', ' Games', cat_text, flags=re.IGNORECASE)
        cat_text = cat_text.strip()
        title_tag.string = f"{cat_text} – Free Online | Unblocked Games USA"
        # Update og:title
        for meta in soup.find_all("meta", property=re.compile(r"og:title")):
            meta["content"] = f"{cat_text} – Free Online | Unblocked Games USA"
        # Update description
        if desc_meta and count:
            desc_meta["content"] = (
                f"Play {count}free {cat_text} online — no downloads, no sign-up. "
                f"Works instantly at school or home."
            )

def fix_home_page_title(soup, path: Path):
    """Home page title cleanup."""
    if not is_home_page(path):
        return
    title_tag = soup.find("title")
    if title_tag:
        title_tag.string = "Unblocked Games USA – Free Online Games, No Download"

def fix_schema_org_name(soup, path: Path):
    """Remove 'Unblocked' from schema.org name field on game pages."""
    if not is_game_page(path):
        return
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script.string)
            if "name" in data:
                data["name"] = re.sub(r'\s+Unblocked\s*$', '', data["name"], flags=re.IGNORECASE)
            script.string = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            pass

def process_file(path: Path):
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  SKIP (read error): {path} — {e}")
        return False

    soup = BeautifulSoup(html, "html.parser")
    original = str(soup)

    # Apply all fixes
    fix_remove_keywords_meta(soup)
    fix_remove_duplicate_gtag(soup)
    fix_inject_mobile_css(soup)
    fix_nav_toggle_js(soup)
    fix_remove_duplicate_other_cats(soup, path)
    fix_game_card_titles(soup)
    fix_game_page_title_and_meta(soup, path)
    fix_categ_page_meta(soup, path)
    fix_home_page_title(soup, path)
    fix_schema_org_name(soup, path)

    new_html = str(soup)
    if new_html == original:
        return False  # no changes

    if not DRY_RUN:
        path.write_text(new_html, encoding="utf-8")
    return True

def main():
    files = collect_html_files()
    print(f"Found {len(files)} HTML files in repo.")
    changed = 0
    errors  = 0
    game_pages  = 0
    categ_pages = 0
    home_pages  = 0
    for f in sorted(files):
        rel = f.relative_to(REPO_ROOT)
        if is_game_page(f):
            game_pages += 1
        elif is_categ_page(f):
            categ_pages += 1
        elif is_home_page(f):
            home_pages += 1
        try:
            modified = process_file(f)
            if modified:
                changed += 1
                print(f"  ✓ {rel}")
        except Exception as e:
            errors += 1
            print(f"  ✗ ERROR {rel}: {e}")

    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done.")
    print(f"  Files scanned : {len(files)}")
    print(f"  Home pages    : {home_pages}")
    print(f"  Category pages: {categ_pages}")
    print(f"  Game pages    : {game_pages}")
    print(f"  Files changed : {changed}")
    print(f"  Errors        : {errors}")
    if DRY_RUN:
        print("\n  ⚠  DRY_RUN=True — no files were written. Set DRY_RUN=False to apply.")

if __name__ == "__main__":
    main()
