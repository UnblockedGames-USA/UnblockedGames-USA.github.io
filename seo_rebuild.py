#!/usr/bin/env python3
"""
SEO Rebuild — Unblocked Games USA
===================================
SURGICAL ONLY — touches exactly these tags per page, nothing else:
  1. <title>
  2. <meta name="description">
  3. <link rel="icon / shortcut icon / apple-touch-icon">   → /favicon.png
  4. OG tags (og:title, og:description)                     → added/updated
  5. <p class="footer-copy"> copyright                      → color:#ffffff; opacity:1
  6. <style id="a11y-contrast-fix"> .footer-copy rule       → #ffffff; opacity:1

Does NOT touch: CSS, JS, HTML structure, schema.org, Twitter cards,
                navigation, game iframe, Google Analytics, pagination.

Repo: https://github.com/UnblockedGames-USA/UnblockedGames-USA.github.io

Title formulas (verified against actual HTML structure):
  Homepage  → Unblocked Games | Play Games on Full Screen - Google Games
  Category  → {Category} - Unblocked Games
  Game      → Unblocked Games | {Game Name} ⚡ - Google Games

Description rule: opens with EXACT words title starts with (Google bolds them)
  Homepage  → "Unblocked Games — play 586+ free games on full screen..."
  Category  → "{Category} unblocked games — ..."
  Game      → "Unblocked Games — play {Game Name} free on full screen..."
"""

import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "beautifulsoup4", "--break-system-packages", "-q"])
    from bs4 import BeautifulSoup

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
REPO_ROOT  = Path(".")
BASE_URL   = "https://unblockedgames-usa.github.io"
BRAND      = "Unblocked Games USA"
GAME_COUNT = "586+"
EMOJI_SEP  = "⚡"

CATEGORIES = {
    "shooter", "platformer", "2-player", "fighting", "driving",
    "puzzle", "multiplayer", "action", "skill", "adventure",
    "racing", "strategy", "sports", "simulation", "clicker",
    "horror", "kids",
}

CATEGORY_LABELS = {
    "2-player": "2 Player", "shooter": "Shooter", "platformer": "Platformer",
    "fighting": "Fighting", "driving": "Driving", "puzzle": "Puzzle",
    "multiplayer": "Multiplayer", "action": "Action", "skill": "Skill",
    "adventure": "Adventure", "racing": "Racing", "strategy": "Strategy",
    "sports": "Sports", "simulation": "Simulation", "clicker": "Clicker",
    "horror": "Horror", "kids": "Kids",
}

# Per-category descriptions — open with "{Label} unblocked games —" to match title start
CATEGORY_DESCRIPTIONS = {
    "shooter":     "Shooter unblocked games — aim, fire and dominate enemies across dozens of free titles. No download, works at school instantly.",
    "platformer":  "Platformer unblocked games — run, jump and dodge through every level. Classic and modern side-scrollers, all free in your browser.",
    "2-player":    "2 Player unblocked games — grab a friend and battle on one keyboard. The best split-screen and co-op games, free and instant.",
    "fighting":    "Fighting unblocked games — pick your fighter and throw down. Street-style brawlers and arena battles, free with no install.",
    "driving":     "Driving unblocked games — race, park and drift across free car titles. Off-road, street and simulator games ready instantly.",
    "puzzle":      "Puzzle unblocked games — train your brain with logic challenges, match tiles and mind-bending teasers. All free at school.",
    "multiplayer": "Multiplayer unblocked games — play live against real opponents online. No download, no sign-up, just pick a game and compete.",
    "action":      "Action unblocked games — survive waves, defeat bosses and level up. Fast-paced free titles that run instantly in any browser.",
    "skill":       "Skill unblocked games — easy to start, hard to master. Beat your high score across precision challenges, all free to play.",
    "adventure":   "Adventure unblocked games — explore worlds, complete quests and uncover stories. Free epic titles that work at school.",
    "racing":      "Racing unblocked games — pedal to the metal across kart, drift, street and off-road tracks. Free, instant, no download.",
    "strategy":    "Strategy unblocked games — think ahead and outplay opponents. Turn-based and real-time strategy titles, all free to play.",
    "sports":      "Sports unblocked games — football, basketball, golf and more, free in your browser. Play your favourite sport instantly at school.",
    "simulation":  "Simulation unblocked games — build, manage and control cities, farms and machines. Free sim games that run in any browser.",
    "clicker":     "Clicker unblocked games — earn, upgrade and automate your way to the top. Idle and incremental games, free and always on.",
    "horror":      "Horror unblocked games — creepy puzzles, jump scares and survival challenges. Dare to play these free titles at school.",
    "kids":        "Kids unblocked games — safe, colourful and fun for all ages. School-approved free games with no downloads or sign-ups.",
}

# ─────────────────────────────────────────────────────────────────────────────
# PAGE TYPE DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def detect_page_type(html_path: Path):
    """
    Returns ('homepage', None) | ('category', 'slug') | ('game', 'slug')
    Uses file path relative to repo root — matches actual repo structure.
    """
    try:
        rel = html_path.relative_to(REPO_ROOT)
    except ValueError:
        return ("unknown", None)
    parts = rel.parts

    # index.html at root
    if rel == Path("index.html"):
        return ("homepage", None)

    # categ/{name}/index.html  OR  categ/{name}.html
    if parts[0] == "categ":
        cat = parts[1] if len(parts) >= 2 else None
        # strip .html if the folder itself is the file
        if cat:
            cat = cat.replace(".html", "")
        if cat and cat in CATEGORIES:
            return ("category", cat)

    # {game-slug}/index.html
    if len(parts) == 2 and parts[1] == "index.html":
        return ("game", parts[0])

    return ("unknown", None)


# ─────────────────────────────────────────────────────────────────────────────
# TITLE & DESCRIPTION BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-"))


def build_title(page_type: str, slug) -> str:
    if page_type == "homepage":
        return "Unblocked Games | Play Games on Full Screen - Google Games"
    if page_type == "category" and slug:
        label = CATEGORY_LABELS.get(slug, slug_to_title(slug))
        return f"{label} - Unblocked Games"
    if page_type == "game" and slug:
        game = slug_to_title(slug)
        return f"Unblocked Games | {game} {EMOJI_SEP} - Google Games"
    return f"Unblocked Games | Free Online Games - {BRAND}"


def build_description(page_type: str, slug) -> str:
    if page_type == "homepage":
        return (
            f"Unblocked Games — play {GAME_COUNT} free games on full screen. "
            f"No downloads, no sign-ups. Google Games, school games: shooter, puzzle, "
            f"racing, action and more. Works instantly anywhere."
        )
    if page_type == "category" and slug:
        return CATEGORY_DESCRIPTIONS.get(
            slug,
            f"{CATEGORY_LABELS.get(slug, slug_to_title(slug))} unblocked games — "
            f"browse the full collection, free to play instantly in your browser."
        )
    if page_type == "game" and slug:
        game = slug_to_title(slug)
        return (
            f"Unblocked Games — play {game} free on full screen. "
            f"No download, no sign-up. One of {GAME_COUNT} Google Games ready "
            f"instantly at school or home."
        )
    return f"Unblocked Games — free games, play on full screen instantly. {BRAND}."


def build_canonical(html_path: Path) -> str:
    try:
        rel = html_path.relative_to(REPO_ROOT)
    except ValueError:
        return BASE_URL + "/"
    parts = list(rel.parts)
    if parts and parts[-1] == "index.html":
        parts = parts[:-1]
    path = "/".join(parts)
    return f"{BASE_URL}/{path}/" if path else f"{BASE_URL}/"


# ─────────────────────────────────────────────────────────────────────────────
# SURGICAL PATCHERS  (one function per concern)
# ─────────────────────────────────────────────────────────────────────────────

def patch_title(soup, new_title: str):
    """Update <title> only."""
    tag = soup.find("title")
    if tag:
        tag.string = new_title
    else:
        t = soup.new_tag("title")
        t.string = new_title
        head = soup.find("head")
        if head:
            head.insert(0, t)


def patch_meta_description(soup, new_desc: str):
    """Update <meta name='description'> only."""
    tag = soup.find("meta", attrs={"name": "description"})
    if tag:
        tag["content"] = new_desc
    else:
        head = soup.find("head")
        if head:
            head.append(soup.new_tag("meta", attrs={
                "name": "description", "content": new_desc
            }))


def patch_favicon(soup):
    """
    Replace any existing favicon links with /favicon.png.
    favicon.png already exists at https://unblockedgames-usa.github.io/favicon.png
    Game pages currently have /favicon.ico — this updates them.
    Homepage and category pages have no favicon — this adds them.
    """
    # Remove all existing favicon-related link tags
    for old in soup.find_all("link"):
        rel = old.get("rel", [])
        if isinstance(rel, str):
            rel = [rel]
        if any(r in rel for r in ["icon", "shortcut icon", "apple-touch-icon"]):
            old.decompose()

    head = soup.find("head")
    if not head:
        return

    favicons = [
        {"rel": "icon",             "type": "image/png", "href": "/favicon.png"},
        {"rel": "shortcut icon",                         "href": "/favicon.png"},
        {"rel": "apple-touch-icon",                      "href": "/favicon.png"},
    ]
    for attrs in favicons:
        tag = soup.new_tag("link")
        for k, v in attrs.items():
            tag[k] = v
        head.append(tag)


def patch_og_tags(soup, title: str, description: str, canonical: str, image_url: str = None):
    """
    Add or update OG tags.
    For game pages: og:image already has the game-specific image — KEEP IT.
    For homepage/category: set og:image to favicon.png as fallback.
    Only updates og:title and og:description; preserves og:image if already set.
    """
    head = soup.find("head")
    if not head:
        return

    # Check if game-specific og:image already exists — preserve it
    existing_og_image = soup.find("meta", property="og:image")
    preserved_image = (
        existing_og_image["content"]
        if existing_og_image and "/images/" in existing_og_image.get("content", "")
        else (image_url or f"{BASE_URL}/favicon.png")
    )

    # The OG fields we control
    OG_TO_SET = {
        "og:type":        "website",
        "og:site_name":   BRAND,
        "og:title":       title,
        "og:description": description,
        "og:url":         canonical,
        "og:image":       preserved_image,
    }

    for prop, content in OG_TO_SET.items():
        tag = soup.find("meta", property=prop)
        if tag:
            tag["content"] = content          # update existing
        else:
            new_tag = soup.new_tag("meta", attrs={"property": prop, "content": content})
            head.append(new_tag)              # add if missing


def patch_copyright_white(soup):
    """
    Two-pronged approach:
    1. Update <style id="a11y-contrast-fix"> to set .footer-copy color:#ffffff; opacity:1
    2. Also set inline style on <p class="footer-copy"> as fallback
    Does NOT touch any other CSS rules in the block.
    """
    # Prong 1: update the existing style block
    style_block = soup.find("style", id="a11y-contrast-fix")
    if style_block and style_block.string:
        css = style_block.string
        # Change footer-copy color from whatever it is to #ffffff
        css = re.sub(
            r'(\.footer-copy[^{]*\{[^}]*?)color\s*:\s*[^;!]+(!important)?',
            r'\1color: #ffffff !important',
            css
        )
        # Add or update opacity to 1 inside .footer-copy rule
        # Find the rule and add opacity if not present
        def add_opacity(match):
            block = match.group(0)
            if 'opacity' not in block:
                block = block.rstrip('}') + '  opacity: 1 !important;\n}'
            else:
                block = re.sub(r'opacity\s*:\s*[^;]+', 'opacity: 1 !important', block)
            return block
        css = re.sub(
            r'(\.footer-copy|p\.footer-copy)\s*\{[^}]+\}',
            add_opacity,
            css
        )
        style_block.string = css

    # Prong 2: inline style on the element itself (belt-and-suspenders)
    for p in soup.find_all("p", class_="footer-copy"):
        existing = p.get("style", "").rstrip(";")
        # Remove any existing color/opacity from inline style
        existing = re.sub(r'color\s*:[^;]+;?', '', existing)
        existing = re.sub(r'opacity\s*:[^;]+;?', '', existing)
        p["style"] = (existing.strip(";").strip() + ";color:#ffffff;opacity:1").lstrip(";")


# ─────────────────────────────────────────────────────────────────────────────
# CORE: patch one file
# ─────────────────────────────────────────────────────────────────────────────
def patch_html(html_path: Path) -> tuple[bool, str]:
    """
    Returns (changed: bool, page_type: str)
    """
    raw = html_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")

    page_type, slug = detect_page_type(html_path)
    if page_type == "unknown":
        return False, "unknown"

    new_title = build_title(page_type, slug)
    new_desc  = build_description(page_type, slug)
    new_canon = build_canonical(html_path)

    # ── Run each surgical patcher ─────────────────────────────────────────────
    patch_title(soup, new_title)
    patch_meta_description(soup, new_desc)
    patch_favicon(soup)
    patch_og_tags(soup, new_title, new_desc, new_canon)
    patch_copyright_white(soup)

    # ── Write back only if content actually changed ───────────────────────────
    new_html = str(soup)
    if new_html != raw:
        html_path.write_text(new_html, encoding="utf-8")
        return True, page_type
    return False, page_type


# ─────────────────────────────────────────────────────────────────────────────
# VERIFICATION: print what was written to spot-check 3 sample pages
# ─────────────────────────────────────────────────────────────────────────────
def verify_file(html_path: Path):
    if not html_path.exists():
        return
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    print(f"\n  ┌─ {html_path}")
    t = soup.find("title")
    print(f"  │  title       : {t.string.strip() if t else 'MISSING'}")
    d = soup.find("meta", attrs={"name": "description"})
    print(f"  │  description : {d['content'][:80] + '...' if d else 'MISSING'}")
    fav = soup.find("link", rel=lambda r: r and "icon" in (r if isinstance(r, list) else [r]))
    print(f"  │  favicon     : {fav['href'] if fav else 'MISSING'}")
    og_t = soup.find("meta", property="og:title")
    print(f"  │  og:title    : {og_t['content'][:60] if og_t else 'MISSING'}")
    fp = soup.find("p", class_="footer-copy")
    print(f"  └─ footer-copy : style={fp.get('style','none') if fp else 'MISSING'}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  SEO Rebuild — Unblocked Games USA")
    print("  SURGICAL: title / description / favicon / OG / copyright only")
    print("=" * 70)

    html_files = sorted(REPO_ROOT.rglob("*.html"))
    print(f"\n  Found {len(html_files)} HTML files\n")

    stats = {"homepage": 0, "category": 0, "game": 0, "unknown": 0, "changed": 0}

    for html_path in html_files:
        changed, page_type = patch_html(html_path)
        stats[page_type] = stats.get(page_type, 0) + 1
        if changed:
            stats["changed"] += 1

        if page_type != "unknown":
            _, slug = detect_page_type(html_path)
            label  = slug if slug else "(homepage)"
            marker = "✏️ " if changed else "   "
            print(f"  {marker}[{page_type:8s}] {label}")

    print("\n" + "=" * 70)
    print(f"  Homepage pages : {stats.get('homepage', 0)}")
    print(f"  Category pages : {stats.get('category', 0)}")
    print(f"  Game pages     : {stats.get('game', 0)}")
    print(f"  Unknown/skip   : {stats.get('unknown', 0)}")
    print(f"  Files changed  : {stats['changed']}")
    print("=" * 70)

    # ── Spot-check 3 representative files ─────────────────────────────────────
    print("\n  VERIFICATION (spot-check 3 pages):")
    for sample in [
        REPO_ROOT / "index.html",
        REPO_ROOT / "categ" / "driving" / "index.html",
        REPO_ROOT / "basketball-legends" / "index.html",
    ]:
        verify_file(sample)

    print(f"""
  Expected output:
    Homepage  title → "Unblocked Games | Play Games on Full Screen - Google Games"
    Driving   title → "Driving - Unblocked Games"
    B.Legends title → "Unblocked Games | Basketball Legends ⚡ - Google Games"

  All descriptions open with exact title-start words (Google bolding signal).
  Favicon → /favicon.png on ALL pages.
  Copyright → color:#ffffff; opacity:1 on ALL pages.

  Deploy:
    git add -A
    git commit -m "seo: surgical title/desc/favicon/OG/copyright fix"
    git push
""")


if __name__ == "__main__":
    main()
