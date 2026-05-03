#!/usr/bin/env python3
"""
SEO Meta Tag Fixer — Unblocked Games USA
=========================================
Runs from the repo root: C:\\Users\\berra\\Documents\\GitHub\\UnblockedGames-USA.github.io

What it does:
  1. Scans every game subfolder (has its own index.html)
  2. Derives game name, category, and description from the folder slug and existing HTML
  3. Rebuilds the entire <head> with best-practice SEO meta tags:
       - <title>        (50-60 chars, keyword-rich)
       - meta description (140-160 chars)
       - canonical URL
       - Open Graph (og:title, og:description, og:image, og:url, og:type)
       - Twitter Card
       - robots, viewport (keeps existing if present)
  4. Writes changes in-place (backs up originals to .bak if --backup flag used)

Usage:
  python seo_fix_meta.py              # dry-run preview (no files changed)
  python seo_fix_meta.py --write      # apply changes
  python seo_fix_meta.py --write --backup   # apply + keep .bak originals
  python seo_fix_meta.py --slug 8-ball-pool --write  # single game only

Requires: Python 3.8+, no external packages.
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from html.parser import HTMLParser

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
BASE_URL = "https://unblockedgames-usa.github.io"
SITE_NAME = "Unblocked Games USA"
GA_ID = "G-L6FNHSMWF4"   # keep existing GA tag intact

# Folders that are NOT game pages
SKIP_FOLDERS = {
    "assets", "images", "categ", "css", "js", "fonts",
    "privacy-policy", "contact", "faq", "dmca",
    ".git", ".github", "node_modules",
}

# Slug-fragment → category label  (used for og:description variety)
CATEGORY_HINTS: dict[str, str] = {
    "pool": "Sports", "ball": "Sports", "soccer": "Sports",
    "football": "Sports", "basketball": "Sports", "golf": "Sports",
    "tennis": "Sports", "bowling": "Sports",
    "racing": "Racing", "car": "Racing", "moto": "Racing",
    "truck": "Racing", "kart": "Racing", "drift": "Racing",
    "shooter": "Shooter", "blast": "Shooter", "sniper": "Shooter",
    "war": "Action", "fight": "Fighting", "boxing": "Fighting",
    "tank": "Action",
    "puzzle": "Puzzle", "mahjong": "Puzzle", "sudoku": "Puzzle",
    "chess": "Strategy", "strategy": "Strategy", "tower": "Strategy",
    "adventure": "Adventure", "quest": "Adventure",
    "platformer": "Platformer", "jump": "Platformer", "run": "Platformer",
    "idle": "Clicker", "clicker": "Clicker",
    "horror": "Horror",
    "kids": "Kids", "bunny": "Kids", "puppy": "Kids",
    "driving": "Driving",
    "sim": "Simulation", "simulator": "Simulation",
    "multiplayer": "Multiplayer", "2-player": "2-Player",
    "skill": "Skill",
    "2048": "Puzzle", "bubble": "Puzzle",
}

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def slug_to_title(slug: str) -> str:
    """'8-ball-pool' → '8 Ball Pool'"""
    return " ".join(w.capitalize() for w in slug.replace("-", " ").split())


def guess_category(slug: str) -> str:
    s = slug.lower()
    for kw, cat in CATEGORY_HINTS.items():
        if kw in s:
            return cat
    return "Action"


def make_page_title(game_title: str) -> str:
    """≤60 chars: 'Game Name Unblocked – Play Free Online | Unblocked Games USA'"""
    base = f"{game_title} Unblocked – Play Free Online | {SITE_NAME}"
    if len(base) <= 60:
        return base
    # Shorten site name
    short = f"{game_title} Unblocked – Play Free | UG USA"
    if len(short) <= 60:
        return short
    return f"{game_title} Unblocked | {SITE_NAME}"[:60]


def make_description(game_title: str, category: str) -> str:
    """~150 chars, contains primary keyword naturally."""
    desc = (
        f"Play {game_title} unblocked free in your browser — no download, no sign-up. "
        f"Enjoy this {category} game instantly at school or work on Unblocked Games USA."
    )
    return desc[:160]


def make_og_description(game_title: str, category: str) -> str:
    return (
        f"{game_title} is a free {category} game you can play unblocked right now. "
        f"No install needed — launch directly in Chrome, Firefox, or Edge."
    )[:200]


class HeadParser(HTMLParser):
    """Extracts existing iframe src, GA script, and page category tag from body."""
    def __init__(self):
        super().__init__()
        self.iframe_src = ""
        self.ga_found = False
        self.category_tag = ""
        self._in_category = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "iframe" and "src" in attrs and not self.iframe_src:
            self.iframe_src = attrs["src"]
        if tag == "script" and attrs.get("src", "").startswith("https://www.googletagmanager.com"):
            self.ga_found = True
        if tag == "a" and "categ/" in attrs.get("href", ""):
            self._in_category = True

    def handle_data(self, data):
        if self._in_category and data.strip():
            self.category_tag = data.strip()
            self._in_category = False

    def handle_endtag(self, tag):
        if tag == "a":
            self._in_category = False


def build_head_block(slug: str, game_title: str, category: str,
                     image_url: str, parser: HeadParser) -> str:
    page_url = f"{BASE_URL}/{slug}/"
    og_image = image_url or f"{BASE_URL}/images/{slug}.png"

    title = make_page_title(game_title)
    desc = make_description(game_title, category)
    og_desc = make_og_description(game_title, category)

    # Schema.org VideoGame / SoftwareApplication JSON-LD
    jsonld = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "{game_title} Unblocked",
    "applicationCategory": "Game",
    "genre": "{category}",
    "operatingSystem": "Any",
    "offers": {{
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }},
    "url": "{page_url}",
    "image": "{og_image}",
    "description": "{desc}"
  }}
  </script>"""

    ga_block = ""
    if parser.ga_found:
        ga_block = f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>"""

    head = f"""<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- PRIMARY SEO -->
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{game_title} unblocked, {game_title} online, unblocked games, free browser games, play at school, {category.lower()} games unblocked">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{page_url}">

  <!-- OPEN GRAPH -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:url" content="{page_url}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="300">
  <meta property="og:image:height" content="200">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="en_US">

  <!-- TWITTER CARD -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{og_desc}">
  <meta name="twitter:image" content="{og_image}">

  <!-- SCHEMA.ORG -->
{jsonld}

  <!-- STYLESHEET -->
  <link rel="stylesheet" href="/assets/style.css">

  {ga_block}
</head>"""
    return head


# ──────────────────────────────────────────────
# CORE LOGIC
# ──────────────────────────────────────────────

def process_game_folder(folder: Path, write: bool, backup: bool) -> dict:
    index_file = folder / "index.html"
    if not index_file.exists():
        return {"slug": folder.name, "status": "skipped (no index.html)"}

    slug = folder.name
    game_title = slug_to_title(slug)

    original = index_file.read_text(encoding="utf-8", errors="replace")

    # Parse existing content
    parser = HeadParser()
    parser.feed(original)

    # Determine category: prefer what's already tagged in page
    if parser.category_tag:
        # Strip emoji from category tag
        cat_clean = re.sub(r'[^\w\s-]', '', parser.category_tag).strip()
        category = cat_clean if cat_clean else guess_category(slug)
    else:
        category = guess_category(slug)

    image_url = f"{BASE_URL}/images/{slug}.png"

    new_head = build_head_block(slug, game_title, category, image_url, parser)

    # Replace <head>...</head> (non-greedy, DOTALL)
    new_html, n = re.subn(
        r'<head>.*?</head>',
        new_head,
        original,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if n == 0:
        return {"slug": slug, "status": "⚠ no <head> tag found — skipped"}

    changed = new_html != original
    status = "✓ updated" if changed else "— unchanged"

    if write and changed:
        if backup:
            shutil.copy2(index_file, index_file.with_suffix(".bak"))
        index_file.write_text(new_html, encoding="utf-8")

    return {
        "slug": slug,
        "title": make_page_title(game_title),
        "category": category,
        "status": status if write else ("would update" if changed else "no change needed"),
    }


def main():
    parser = argparse.ArgumentParser(description="SEO meta fixer for Unblocked Games USA")
    parser.add_argument("--write", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--backup", action="store_true", help="Save .bak before overwriting")
    parser.add_argument("--slug", type=str, default="", help="Process a single game slug only")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.resolve()
    print(f"\n{'='*60}")
    print(f"  Unblocked Games USA — SEO Meta Fixer")
    print(f"  Mode: {'WRITE' if args.write else 'DRY-RUN (no files changed)'}")
    print(f"  Repo: {repo_root}")
    print(f"{'='*60}\n")

    results = []

    if args.slug:
        target = repo_root / args.slug
        if not target.is_dir():
            print(f"ERROR: folder not found: {target}")
            sys.exit(1)
        results.append(process_game_folder(target, args.write, args.backup))
    else:
        folders = sorted(
            [f for f in repo_root.iterdir()
             if f.is_dir() and f.name not in SKIP_FOLDERS and not f.name.startswith(".")],
            key=lambda f: f.name,
        )
        print(f"Found {len(folders)} game folders to process...\n")
        for folder in folders:
            r = process_game_folder(folder, args.write, args.backup)
            results.append(r)
            print(f"  [{r['status']:>15}]  {r['slug']}")

    updated = sum(1 for r in results if "update" in r.get("status", ""))
    skipped = sum(1 for r in results if "skip" in r.get("status", ""))
    print(f"\n{'='*60}")
    print(f"  Total processed : {len(results)}")
    print(f"  Updated/would   : {updated}")
    print(f"  Skipped         : {skipped}")
    if not args.write:
        print(f"\n  ⚡ This was a DRY-RUN. Run with --write to apply changes.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
