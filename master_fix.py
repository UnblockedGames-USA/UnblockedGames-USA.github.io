#!/usr/bin/env python3
"""
master_fix.py — Unblocked Games USA — ONE SCRIPT, ALL FIXES
=============================================================
Place in repo root:
  C:\\Users\\berra\\Documents\\GitHub\\UnblockedGames-USA.github.io

FIXES:
  [A] ALL game pages  → Rewrites <head> with full SEO meta tags
  [B] ALL game pages  → Fixes "Browse by Category" section (was blank/broken)
                        Replaces it with proper pill-style category links
  [C] ALL category pages (categ/) → Removes duplicate inner Browse-by-Category block
  [D] ALL pages (homepage + game + categ) → Removes duplicate footer category nav

Usage:
  python master_fix.py            # dry-run: shows what would change
  python master_fix.py --write    # apply all fixes
  python master_fix.py --backup   # (add alongside --write) save .bak originals

Python 3.8+, zero external dependencies.
"""

import re, sys, shutil, argparse
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
BASE_URL  = "https://unblockedgames-usa.github.io"
SITE_NAME = "Unblocked Games USA"
GA_ID     = "G-L6FNHSMWF4"

SKIP_FOLDERS = {
    "assets","images","categ","css","js","fonts",
    "privacy-policy","contact","faq","dmca",
    ".git",".github","node_modules",
}

# Full ordered category list with emoji
CATEGORIES = [
    ("🎯","Shooter",   "shooter"),
    ("🏃","Platformer","platformer"),
    ("👥","2-Player",  "2-player"),
    ("🥊","Fighting",  "fighting"),
    ("🚗","Driving",   "driving"),
    ("🧠","Puzzle",    "puzzle"),
    ("🌐","Multiplayer","multiplayer"),
    ("💥","Action",    "action"),
    ("🏆","Skill",     "skill"),
    ("🗺️","Adventure", "adventure"),
    ("🏁","Racing",    "racing"),
    ("♟️","Strategy",  "strategy"),
    ("⚽","Sports",    "sports"),
    ("🏙️","Simulation","simulation"),
    ("🖱️","Clicker",   "clicker"),
    ("👻","Horror",    "horror"),
    ("🧸","Kids",      "kids"),
]

CATEGORY_HINTS = {
    "pool":"Sports","ball":"Sports","soccer":"Sports","football":"Sports",
    "basketball":"Sports","golf":"Sports","tennis":"Sports","bowling":"Sports",
    "racing":"Racing","car":"Racing","moto":"Racing","truck":"Racing",
    "kart":"Racing","drift":"Racing",
    "shooter":"Shooter","blast":"Shooter","sniper":"Shooter","alien":"Shooter",
    "war":"Action","fight":"Fighting","boxing":"Fighting","tank":"Action",
    "puzzle":"Puzzle","mahjong":"Puzzle","sudoku":"Puzzle","2048":"Puzzle",
    "bubble":"Puzzle","blox":"Puzzle","brain":"Puzzle","block":"Puzzle",
    "chess":"Strategy","strategy":"Strategy","tower":"Strategy","defense":"Strategy",
    "adventure":"Adventure","quest":"Adventure","bob":"Adventure",
    "platformer":"Platformer","jump":"Platformer","run":"Platformer",
    "idle":"Clicker","clicker":"Clicker",
    "horror":"Horror",
    "kids":"Kids","bunny":"Kids","puppy":"Kids","groomer":"Kids",
    "driving":"Driving","sim":"Simulation","simulator":"Simulation",
    "multiplayer":"Multiplayer","2-player":"2-Player","player":"2-Player",
    "skill":"Skill","archery":"Skill","archer":"Skill","athletics":"Skill",
}

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("-", " ").split())

def guess_category(slug: str) -> str:
    s = slug.lower()
    for kw, cat in CATEGORY_HINTS.items():
        if kw in s:
            return cat
    return "Action"

def get_cat_slug(cat_label: str) -> str:
    for _, label, slug in CATEGORIES:
        if label.lower() == cat_label.lower():
            return slug
    return cat_label.lower()

def has_ga(html: str) -> bool:
    return "googletagmanager.com" in html

# The correct category nav pill block (used in game pages)
def build_categ_nav_block() -> str:
    pills = "\n".join(
        f'    <a href="{BASE_URL}/categ/{slug}/" class="cat-pill">{emoji} {label}</a>'
        for emoji, label, slug in CATEGORIES
    )
    return f"""<section class="browse-by-category">
  <h2>🗂️ Browse by Category</h2>
  <div class="cat-pills">
{pills}
  </div>
</section>"""

CATEG_NAV_BLOCK = build_categ_nav_block()

# ═══════════════════════════════════════════════════════════════════════════════
# FIX A — SEO <head> rewrite (game pages)
# ═══════════════════════════════════════════════════════════════════════════════

def build_seo_head(slug: str, game: str, cat: str, html: str) -> str:
    url   = f"{BASE_URL}/{slug}/"
    img   = f"{BASE_URL}/images/{slug}.png"
    cat_slug = get_cat_slug(cat)

    title = f"{game} Unblocked – Play Free Online | {SITE_NAME}"
    if len(title) > 60:
        title = f"{game} Unblocked | {SITE_NAME}"[:60]

    desc = (f"Play {game} unblocked free in your browser — no download, no sign-up. "
            f"Enjoy this {cat} game instantly at school or work on Unblocked Games USA.")[:160]

    og_d = (f"{game} is a free {cat} game you can play unblocked right now. "
            f"No install needed — launch directly in Chrome, Firefox, or Edge.")[:200]

    ga = ""
    if has_ga(html):
        ga = f"""
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>"""

    return f"""<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- PRIMARY SEO -->
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{game} unblocked, {game} online, unblocked games, free browser games, play at school, {cat.lower()} games unblocked">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="/favicon.ico">

  <!-- OPEN GRAPH -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{og_d}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="300">
  <meta property="og:image:height" content="200">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="en_US">

  <!-- TWITTER CARD -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{og_d}">
  <meta name="twitter:image" content="{img}">

  <!-- SCHEMA.ORG -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "{game} Unblocked",
    "applicationCategory": "Game",
    "genre": "{cat}",
    "operatingSystem": "Any",
    "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
    "url": "{url}",
    "image": "{img}",
    "description": "{desc}"
  }}
  </script>

  <link rel="stylesheet" href="/assets/style.css">{ga}
</head>"""


# ═══════════════════════════════════════════════════════════════════════════════
# FIX B — Replace broken/empty Browse-by-Category block in game pages
# ═══════════════════════════════════════════════════════════════════════════════

# Matches the existing browse-by-category section (with or without content)
# Handles: <section class="browse-by-category"> or <div ...> wrappers
BROWSE_SECTION_RE = re.compile(
    r'<(?:section|div)[^>]*class="[^"]*browse-by-category[^"]*"[^>]*>.*?</(?:section|div)>',
    re.DOTALL | re.IGNORECASE,
)

# Also matches a heading-only pattern like:
#   <h2>🗂️ Browse by Category</h2>  followed by an empty or pill-less div
BROWSE_HEADING_RE = re.compile(
    r'<h[23][^>]*>[^<]*Browse by Category[^<]*</h[23]>\s*'
    r'(?:<div[^>]*>\s*</div>|<div[^>]*/>)?',
    re.DOTALL | re.IGNORECASE,
)


def fix_browse_section(html: str) -> str:
    """Replace any existing broken browse-by-category block with the correct one."""
    # Try section/div with class first
    new_html, n = BROWSE_SECTION_RE.subn(CATEG_NAV_BLOCK, html, count=1)
    if n > 0:
        return new_html
    # Try heading-only fallback
    new_html, n = BROWSE_HEADING_RE.subn(CATEG_NAV_BLOCK, html, count=1)
    if n > 0:
        return new_html
    # Nothing found — insert before </main> or before <footer>
    for marker in ["</main>", "<footer", "</body>"]:
        if marker in html:
            return html.replace(marker, CATEG_NAV_BLOCK + "\n" + marker, 1)
    return html


# ═══════════════════════════════════════════════════════════════════════════════
# FIX C — Remove duplicate Browse-by-Category in category pages
# ═══════════════════════════════════════════════════════════════════════════════

def remove_duplicate_browse_block(html: str) -> str:
    """
    Category pages have the browse block appearing TWICE.
    Keep the first (or the one inside the proper section), remove the second.
    """
    marker = "Browse by Category"
    positions = [m.start() for m in re.finditer(re.escape(marker), html, re.IGNORECASE)]

    if len(positions) < 2:
        return html  # no duplicate

    # Find and remove the SECOND occurrence block
    second_pos = positions[1]
    body_before = html[:second_pos]

    tag_start = max(body_before.rfind("<section"), body_before.rfind("<div"))
    if tag_start == -1:
        return html

    tag_type  = "section" if html[tag_start:tag_start+8] == "<section" else "div"
    close_tag = f"</{tag_type}>"

    depth, pos = 1, tag_start
    while depth > 0:
        next_open  = html.find(f"<{tag_type}", pos + 1)
        next_close = html.find(close_tag, pos + 1)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open
        else:
            depth -= 1
            pos = next_close

    tag_end = pos + len(close_tag)
    block   = html[tag_start:tag_end]

    if "/categ/" not in block:
        return html  # safety check

    return html[:tag_start] + html[tag_end:]


# ═══════════════════════════════════════════════════════════════════════════════
# FIX D — Remove duplicate footer category nav (all pages)
# ═══════════════════════════════════════════════════════════════════════════════

# The footer has two nav blocks: one with class (keep) and one raw list (remove)
# Pattern: a <nav> or plain block of ONLY /categ/ links that appears after the footer starts
# We look for any <nav> or <div> that contains ONLY categ links and no other content

FOOTER_DUP_RE = re.compile(
    # Matches a block of pill/link elements that are purely category links (the duplicate)
    # It's the second group of categ links inside the footer
    r'(?:<nav[^>]*>|<div[^>]*class="[^"]*cat[^"]*"[^>]*>)'
    r'(?:\s*<a[^>]*/categ/[^>]*>[^<]*</a>\s*){5,}'  # 5+ consecutive categ links = it's the full list
    r'(?:</nav>|</div>)',
    re.DOTALL | re.IGNORECASE,
)

def remove_duplicate_footer_nav(html: str) -> str:
    """Remove second occurrence of the full category link list in footer."""
    # Find all categ-link-only blocks
    matches = list(FOOTER_DUP_RE.finditer(html))
    if len(matches) < 2:
        return html
    # Remove from second match onward
    result = html
    # Process in reverse to preserve positions
    for m in reversed(matches[1:]):
        result = result[:m.start()] + result[m.end():]
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS FILES
# ═══════════════════════════════════════════════════════════════════════════════

def process_game_page(folder: Path, write: bool, backup: bool) -> dict:
    index = folder / "index.html"
    if not index.exists():
        return {"slug": folder.name, "status": "skip"}

    slug = folder.name
    game = slug_to_title(slug)
    html = index.read_text(encoding="utf-8", errors="replace")

    # Detect category from existing categ link in body
    m = re.search(r'/categ/([a-z0-9-]+)[/"]', html)
    cat = slug_to_title(m.group(1)) if m else guess_category(slug)

    # [A] Rewrite <head>
    new_head = build_seo_head(slug, game, cat, html)
    html, n = re.subn(r'<head>.*?</head>', new_head, html, count=1,
                      flags=re.DOTALL | re.IGNORECASE)
    head_fixed = n > 0

    # [B] Fix Browse by Category section
    html_after_b = fix_browse_section(html)
    browse_fixed = html_after_b != html
    html = html_after_b

    # [D] Remove duplicate footer nav
    html_after_d = remove_duplicate_footer_nav(html)
    footer_fixed = html_after_d != html
    html = html_after_d

    original = index.read_text(encoding="utf-8", errors="replace")
    changed  = html != original

    if write and changed:
        if backup:
            shutil.copy2(index, index.with_suffix(".bak"))
        index.write_text(html, encoding="utf-8")

    fixes = []
    if head_fixed:   fixes.append("SEO")
    if browse_fixed: fixes.append("Browse")
    if footer_fixed: fixes.append("Footer")

    status = ("✓ " + "+".join(fixes)) if fixes else "— no change"
    if not write and changed:
        status = "would: " + "+".join(fixes)
    return {"slug": slug, "status": status}


def process_category_page(index: Path, write: bool, backup: bool) -> dict:
    html     = index.read_text(encoding="utf-8", errors="replace")
    original = html

    # [C] Remove duplicate browse block
    html = remove_duplicate_browse_block(html)

    # [D] Remove duplicate footer nav
    html = remove_duplicate_footer_nav(html)

    changed = html != original
    label   = f"categ/{index.parent.name}"

    if write and changed:
        if backup:
            shutil.copy2(index, index.with_suffix(".bak"))
        index.write_text(html, encoding="utf-8")

    if changed:
        status = "✓ fixed" if write else "would fix"
    else:
        status = "— ok"
    return {"path": label, "status": status}


def process_homepage(root: Path, write: bool, backup: bool) -> dict:
    index = root / "index.html"
    if not index.exists():
        return {"path": "index.html", "status": "not found"}

    html     = index.read_text(encoding="utf-8", errors="replace")
    original = html

    # [D] Remove duplicate footer nav on homepage
    html = remove_duplicate_footer_nav(html)

    changed = html != original
    if write and changed:
        if backup:
            shutil.copy2(index, index.with_suffix(".bak"))
        index.write_text(html, encoding="utf-8")

    status = ("✓ footer fixed" if write else "would fix footer") if changed else "— ok"
    return {"path": "index.html (homepage)", "status": status}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Master fixer — Unblocked Games USA")
    ap.add_argument("--write",  action="store_true")
    ap.add_argument("--backup", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).parent.resolve()
    print(f"\n{'═'*64}")
    print(f"  Unblocked Games USA — Master Fix")
    print(f"  Mode  : {'WRITE' if args.write else 'DRY-RUN (no files changed)'}")
    print(f"  Root  : {root}")
    print(f"{'═'*64}\n")

    # ── Homepage ──────────────────────────────────────────────────────────────
    print("── Homepage ──────────────────────────────────────────────────\n")
    r = process_homepage(root, args.write, args.backup)
    print(f"  [{r['status']:>20}]  {r['path']}\n")

    # ── Game pages ────────────────────────────────────────────────────────────
    print("── Game pages [SEO + Browse + Footer] ───────────────────────\n")
    game_folders = sorted(
        [f for f in root.iterdir()
         if f.is_dir() and f.name not in SKIP_FOLDERS and not f.name.startswith(".")],
        key=lambda f: f.name,
    )
    game_results = []
    for folder in game_folders:
        r = process_game_page(folder, args.write, args.backup)
        game_results.append(r)
        print(f"  [{r['status']:>22}]  {r['slug']}")

    updated_games = sum(1 for r in game_results if "✓" in r["status"] or "would" in r["status"])
    print(f"\n  Game pages: {len(game_results)} total, {updated_games} {'updated' if args.write else 'to update'}\n")

    # ── Category pages ────────────────────────────────────────────────────────
    print("── Category pages [Remove dup + Footer] ─────────────────────\n")
    categ_root  = root / "categ"
    cat_results = []
    if categ_root.is_dir():
        for cf in sorted(categ_root.iterdir()):
            for idx in cf.rglob("index.html"):
                r = process_category_page(idx, args.write, args.backup)
                cat_results.append(r)
                print(f"  [{r['status']:>12}]  {r['path']}")
    else:
        print("  categ/ not found\n")

    updated_cats = sum(1 for r in cat_results if "✓" in r["status"] or "would" in r["status"])
    print(f"\n  Category pages: {len(cat_results)} total, {updated_cats} {'updated' if args.write else 'to update'}\n")

    # ── Summary ───────────────────────────────────────────────────────────────
    total = 1 + len(game_results) + len(cat_results)
    total_changed = (1 if "fix" in r["status"] or "✓" in r["status"] else 0) + updated_games + updated_cats
    print(f"{'═'*64}")
    print(f"  Files scanned : {total}")
    print(f"  Files changed : {total_changed}")
    if not args.write:
        print(f"\n  ⚡ DRY-RUN — add --write to apply all changes.")
    else:
        print(f"\n  ✅ Done! Now run:")
        print(f"     git add -A")
        print(f"     git commit -m \"fix: SEO + browse nav + duplicate footer\"")
        print(f"     git push origin main")
    print(f"{'═'*64}\n")


if __name__ == "__main__":
    main()
