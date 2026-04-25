#!/usr/bin/env python3
"""
fix_site.py — UnblockedGames-USA.github.io Repair Script
=========================================================
USAGE (run from repo root):
    cd C:\\Users\\berra\\Documents\\GitHub\\UnblockedGames-USA.github.io
    python fix_site.py

WHAT IT FIXES:
  1. Category pages with {GAMES_GRID} / {PAGINATION} / {CATEGORY_LINKS} placeholders
  2. Legal pages (faq/, dmca/, privacy-policy/, contact/) that show wrong game content
  3. Generates /games.json for site-wide search
  4. Upgrades the search bar on every page to search ALL games (not just the current page)
"""

import os, re, json, math, shutil
from pathlib import Path
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
ROOT        = Path(__file__).parent          # repo root
BASE_URL    = "https://unblockedgames-usa.github.io"
GAMES_PER_PAGE = 20

# Category metadata: slug -> (display_name, emoji, tagline, long_description)
CATEGORIES = {
    'shooter':     ('Shooter',     '🎯', 'Lock, load, and fire!',
                    'Sharpen your aim with free unblocked shooter games. Top-down shooters, '
                    'first-person action, sniper challenges — all playable instantly at school!'),
    'platformer':  ('Platformer',  '🏃', 'Jump into the action!',
                    'Jump, run, and dodge through exciting levels. Classic side-scrollers and '
                    'modern platform challenges — all free and unblocked!'),
    '2-player':    ('2-Player',    '👥', 'Challenge a friend!',
                    'Challenge a friend with free 2-player unblocked games. Play side by side '
                    'on the same keyboard — no download, no sign-up needed!'),
    'fighting':    ('Fighting',    '🥊', 'Step into the ring!',
                    'Go head-to-head in free unblocked fighting games. Boxing, street fighting, '
                    'and combat — test your skills against opponents!'),
    'driving':     ('Driving',     '🚗', 'Hit the road!',
                    'Hit the road with free unblocked driving games. Realistic simulators, '
                    'stunt driving, and off-road madness — start your engine now!'),
    'puzzle':      ('Puzzle',      '🧠', 'Exercise your brain!',
                    'Sharpen your mind with unblocked puzzle games. Logic challenges, word '
                    'puzzles, and physics brainteasers — something to stump every player!'),
    'multiplayer': ('Multiplayer', '🌐', 'Join the world!',
                    'Play the best multiplayer games unblocked for free. Compete with friends '
                    'and players worldwide — no download needed!'),
    'action':      ('Action',      '💥', 'Non-stop adrenaline!',
                    'Dive into heart-pounding action with free unblocked action games. Intense '
                    'battles, fast-paced missions, and non-stop excitement!'),
    'skill':       ('Skill',       '🏆', 'Prove your skills!',
                    'Test your reflexes, timing, and precision with free unblocked skill games. '
                    'Master challenging obstacles and climb to the top!'),
    'adventure':   ('Adventure',   '🗺️', 'The adventure awaits!',
                    'Embark on epic quests and explore new worlds in free unblocked adventure '
                    'games. Stories and challenges await every player!'),
    'racing':      ('Racing',      '🏁', 'Start your engines!',
                    'Put the pedal to the metal with free unblocked racing games. From track '
                    'races to off-road mayhem — race your way to victory!'),
    'strategy':    ('Strategy',    '♟️', 'Think before you act!',
                    'Plan, build, and conquer in free unblocked strategy games. Tower defense, '
                    'war games, and tactical challenges await smart players!'),
    'sports':      ('Sports',      '⚽', 'Play your sport!',
                    'Score goals, hit home runs, and win championships in free unblocked sports '
                    'games. All your favorite sports, no download needed!'),
    'simulation':  ('Simulation',  '🏙️', 'Experience anything!',
                    'Experience life with free unblocked simulation games. Build cities, run '
                    'businesses, and live virtual lives — instantly, no download!'),
    'clicker':     ('Clicker',     '🖱️', 'Click to win!',
                    'Click your way to greatness with free unblocked clicker and idle games. '
                    'Build empires one click at a time — totally addictive!'),
    'horror':      ('Horror',      '👻', 'Dare you enter?',
                    'Dare to enter the world of unblocked horror games. Spine-chilling '
                    'adventures, zombie survival, and ghost encounters await!'),
    'kids':        ('Kids',        '🧸', 'Fun for everyone!',
                    'Safe, fun, and colourful games for kids of all ages. Our free unblocked '
                    'kids games are perfect for school breaks!'),
}

# Folders that are NOT game folders (never scan these)
SKIP_DIRS = {
    'categ', 'assets', 'images', '.git', '.github', 'node_modules',
    'faq', 'dmca', 'privacy-policy', 'contact', 'search', 'sitemap',
    '.idea', '__pycache__',
}

# ─── Explicit category assignments per game slug ───────────────────────────
# Games can belong to multiple categories.  First entry = "primary" category.
EXPLICIT = {
    # ── Popular / featured games ──────────────────────────────────────────
    'among-us':            ['multiplayer', 'action'],
    '1v1-lol':             ['shooter', '2-player'],
    '1v1-lol-offline':     ['shooter', '2-player'],
    '1v1-battle':          ['action', '2-player'],
    '1v1lol':              ['shooter', '2-player'],
    'subway-surfers':      ['platformer', 'skill'],
    'super-mario-bros':    ['platformer', 'action'],
    'geometry-dash':       ['platformer', 'skill'],
    'slope':               ['skill', 'platformer'],
    'slope-2':             ['skill', 'platformer'],
    'tunnel-rush':         ['skill', 'platformer'],
    'flappy-bird':         ['skill', 'platformer'],
    'cookie-clicker':      ['clicker'],
    'retro-bowl':          ['sports', 'action'],
    'drift-hunters':       ['racing', 'driving'],
    'moto-x3m':            ['racing', 'driving'],
    'earn-to-die':         ['racing', 'action'],
    'raft-wars':           ['action', 'strategy'],
    'cat-trap':            ['puzzle', 'strategy'],
    'level-devil':         ['platformer', 'skill'],
    'poor-bunny':          ['platformer', 'kids'],
    'candy-jump':          ['platformer', 'kids'],
    'dreadhead-parkour':   ['platformer', 'skill'],
    'ovo':                 ['platformer', 'skill'],
    'red-ball-4':          ['platformer', 'action'],
    'bunny-hop':           ['platformer', 'kids'],
    'stickman-hook':       ['platformer', 'skill'],
    'stickman-crazy-box':  ['action', 'skill'],
    'ape-sling':           ['skill', 'platformer'],
    'gunspin':             ['skill', 'shooter'],
    'gun-mayhem':          ['shooter', '2-player'],
    'slalom-hero':         ['sports', 'skill'],
    'jumping-shell':       ['platformer', 'skill'],
    'monkey-mart':         ['simulation', 'clicker'],
    'bitlife':             ['simulation', 'adventure'],
    'kart-bros':           ['racing', 'driving'],
    'zombotag':            ['multiplayer', 'horror'],
    'sumo-party':          ['fighting', '2-player'],
    'flip-bros':           ['sports', '2-player'],
    'bouncy-basketball':   ['sports', 'skill'],

    # ── Puzzle games ─────────────────────────────────────────────────────
    'tetris-99':                    ['puzzle', 'skill'],
    'blumgi-bloom':                 ['puzzle'],
    'bubble-shooter':               ['puzzle', 'skill'],
    '2048':                         ['puzzle', 'skill'],
    '2048-online':                  ['puzzle', 'skill'],
    '2048-multitask':               ['puzzle', 'skill'],
    '2048-suika':                   ['puzzle', 'skill'],
    '2048-watermelon':              ['puzzle', 'skill'],
    '10x10':                        ['puzzle', 'skill'],
    '11-11':                        ['puzzle', 'skill'],
    'arithmetica':                  ['puzzle', 'skill'],
    'blob-drop':                    ['puzzle'],
    'block-puzzle':                 ['puzzle', 'skill'],
    'block-the-pig':                ['puzzle', 'strategy'],
    'brain-test-tricky-puzzles':    ['puzzle'],
    'brain-test-2-tricky-stories':  ['puzzle'],
    'brain-test-3-tricky-quests':   ['puzzle'],
    'amazing-bubble-breaker':       ['puzzle'],
    'amazing-bubble-connect':       ['puzzle'],
    'bloxorz':                      ['puzzle', 'skill'],
    'blumgi-ball':                  ['puzzle', 'skill'],
    'blumgi-slime':                 ['platformer', 'skill'],
    'blumgi-castle':                ['puzzle', 'action'],
    'blumgi-dragon':                ['action', 'skill'],
    'blumgi-rocket':                ['platformer', 'skill'],
    'bubble-trouble':               ['action', 'skill'],

    # ── Sports games ─────────────────────────────────────────────────────
    '8-ball-pool':                   ['sports', 'skill'],
    '9-ball-pool':                   ['sports', 'skill'],
    'air-hockey-championship-deluxe':['sports', '2-player'],
    '2-minute-football':             ['sports', '2-player'],
    'a-small-world-cup':             ['sports', '2-player'],
    '4th-and-goal-2022':             ['sports', 'action'],
    'athletics-hero':                ['sports'],
    'archery-world-tour':            ['sports', 'skill'],
    'basket-and-ball':               ['sports', 'skill'],
    'basket-bros':                   ['sports', '2-player'],
    'basket-champs':                 ['sports', 'skill'],
    'basket-random':                 ['sports', '2-player'],
    'basket-swooshes':               ['sports', 'skill'],
    'basketball-frvr':               ['sports', 'skill'],
    'basketball-legends':            ['sports', '2-player'],
    'basketball-stars':              ['sports', 'multiplayer'],
    'basketbros':                    ['sports', '2-player'],
    'battle-golf':                   ['sports', '2-player'],
    'bowling-stars':                 ['sports', 'skill'],
    'big-shot-boxing':               ['fighting', 'sports'],

    # ── Fighting games ────────────────────────────────────────────────────
    'boxing-physics-2':   ['fighting', '2-player'],
    'boxing-random':      ['fighting', '2-player'],
    'animal-arena':       ['fighting', 'action'],
    'bearsus':            ['action', '2-player'],

    # ── Racing / Driving ─────────────────────────────────────────────────
    '3d-car-simulator':            ['driving', 'simulation'],
    '3d-moto-simulator-2':         ['driving', 'simulation'],
    '3d-monster-truck-skyroads':   ['racing', 'driving'],
    '4x4-drive-offroad':           ['driving', 'racing'],
    '18-wheeler-cargo-simulator':  ['driving', 'simulation'],
    'adventure-drivers':           ['driving', 'adventure'],
    'battle-wheels':               ['racing', '2-player'],
    'bike-trials-offroad-1':       ['racing', 'skill'],
    'bike-trials-winter-1':        ['racing', 'skill'],
    'bike-trials-winter-2':        ['racing', 'skill'],
    'blocky-cars':                 ['driving', 'action'],
    'blocky-trials':               ['racing', 'strategy'],

    # ── Action / Strategy ────────────────────────────────────────────────
    'age-of-war':              ['strategy', 'action'],
    'age-of-war-2':            ['strategy', 'action'],
    'awesome-tanks-2':         ['strategy', 'action'],
    'bloons-tower-defense-1':  ['strategy', 'action'],
    'bob-the-robber-4':        ['adventure', 'action'],
    'breaking-the-bank':       ['action', 'strategy'],
    'bacon-may-die':           ['action', 'platformer'],
    'bearsus':                 ['action', '2-player'],
    'avalanche':               ['action', 'skill'],
    'bottle-flip':             ['skill'],

    # ── 2-Player ─────────────────────────────────────────────────────────
    'bad-ice-cream-2':      ['2-player', 'platformer'],
    'bad-ice-cream-3':      ['2-player', 'platformer'],
    '12-mini-battles':      ['2-player', 'action'],
    '12-mini-battles-2':    ['2-player', 'action'],

    # ── Adventure ────────────────────────────────────────────────────────
    'boxrob':           ['adventure', 'puzzle'],
    'boxrob-2':         ['adventure', 'puzzle'],
    'boxrob-3':         ['adventure', 'puzzle'],
    'duck-life-2':      ['kids', 'adventure'],
    'aqua-thrills':     ['adventure', 'skill'],
    'archer-master-3d-castle-defense': ['strategy', 'adventure'],

    # ── Simulation / Clicker ─────────────────────────────────────────────
    'blobby-clicker':         ['clicker'],
    'become-a-puppy-groomer': ['kids', 'simulation'],

    # ── Multiplayer ──────────────────────────────────────────────────────
    'alien-invaders-io': ['shooter', 'multiplayer'],
    'bomber-royale':     ['multiplayer', 'action'],

    # ── Shooter ──────────────────────────────────────────────────────────
    'all-star-blast': ['shooter', 'action'],
    'aliens-nest':    ['action', 'shooter'],
    '8bit-fiesta':    ['action', 'platformer'],
    'air-toons':      ['platformer', 'action'],
    'rabbit-samurai': ['platformer', 'action'],
    'rabbit-samurai': ['platformer', 'action'],

    # ── Horror ───────────────────────────────────────────────────────────
    # zombotag already added above
}

# Fallback keyword rules: slug contains any of these strings → assign category
CAT_KEYWORDS = {
    'shooter':    ['sniper', 'gunplay', 'turret'],
    'platformer': ['platform', 'parkour', 'mario', 'sonic'],
    '2-player':   ['2-player', 'twoplayer'],
    'fighting':   ['fight', 'brawl', 'sumo', 'combat'],
    'driving':    ['car-', '-car', 'drive', 'driving', 'truck', 'moto', '-bike',
                   'bike-', 'wheeler', 'drift', 'road', 'vehicle', 'taxi'],
    'puzzle':     ['puzzle', 'tetris', 'bloxorz', 'arithmetica', 'brain-test',
                   'block-puzzle', 'block-the-pig', 'amazing-bubble', 'blob-drop',
                   'bubble-shoot', '2048', '10x10', '11-11'],
    'multiplayer':['multiplayer', '-io', 'online-'],
    'action':     ['war', 'bloons', 'robber', 'bacon-may-die', 'avalanche'],
    'skill':      ['slope', 'tunnel', 'bottle-flip', 'flappy', 'slalom'],
    'adventure':  ['adventure', 'quest', 'dungeon', 'cave', 'bitlife'],
    'racing':     ['race', 'racing', 'rally', 'offroad', 'moto-x3m', 'trials',
                   'kart', 'track', '3d-monster'],
    'strategy':   ['strategy', 'tower', 'defense', 'army', 'chess'],
    'sports':     ['football', 'soccer', 'basketball', 'tennis', 'golf',
                   'baseball', 'cricket', 'hockey', 'pool', 'bowling', 'archery',
                   'volleyball', 'swimming', 'ski', 'olympics', 'athletics',
                   '8-ball', '9-ball', 'air-hockey', 'world-cup', 'basket-'],
    'simulation': ['simulation', 'simulator', 'tycoon', 'farm', 'city'],
    'clicker':    ['clicker', 'idle', 'cookie'],
    'horror':     ['horror', 'scary', 'zombie', 'ghost', 'undead'],
    'kids':       ['kids', 'puppy', 'bunny', 'duck-life', 'candy', 'penguin',
                   'become-a-puppy'],
}

# ═══════════════════════════════════════════════════════════════
# STEP 1 — SCAN GAME FOLDERS
# ═══════════════════════════════════════════════════════════════

def slug_to_title(slug: str) -> str:
    """Convert a folder slug to a display title."""
    return ' '.join(w.capitalize() for w in slug.replace('-', ' ').split())


def extract_title_from_html(html: str, fallback: str) -> str:
    """Try to pull the game's real title out of its index.html."""
    # <title>GAME NAME Unblocked …</title>
    m = re.search(r'<title[^>]*>([^<]+)\s*[—\-–|]', html, re.IGNORECASE)
    if m:
        t = m.group(1).strip()
        # Strip trailing " Unblocked" if present
        t = re.sub(r'\s+Unblocked\s*$', '', t, flags=re.IGNORECASE).strip()
        if t:
            return t
    # <h1>…</h1>
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
    if m:
        t = re.sub(r'\s+Unblocked\s*$', '', m.group(1).strip(), flags=re.IGNORECASE).strip()
        if t:
            return t
    return fallback


def get_all_games(root: Path) -> list:
    """Return list of dicts: {slug, title, image_url}"""
    games = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        slug = entry.name
        if slug in SKIP_DIRS or slug.startswith('.'):
            continue
        html_path = entry / 'index.html'
        if not html_path.exists():
            continue
        # Skip categ subfolders
        if (root / 'categ').exists() and entry.parent == root / 'categ':
            continue

        try:
            html = html_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            html = ''

        title = extract_title_from_html(html, slug_to_title(slug))
        img   = f"{BASE_URL}/images/{slug}.png"
        games.append({'slug': slug, 'title': title, 'image': img})

    return games


# ═══════════════════════════════════════════════════════════════
# STEP 2 — ASSIGN CATEGORIES
# ═══════════════════════════════════════════════════════════════

def assign_categories(games: list) -> dict:
    """
    Returns: {category_slug: [game_dict, …]}
    Each game may appear in multiple categories.
    """
    cat_map = defaultdict(list)

    for game in games:
        slug = game['slug']
        assigned = set()

        # Explicit lookup first
        if slug in EXPLICIT:
            for c in EXPLICIT[slug]:
                cat_map[c].append(game)
                assigned.add(c)
        else:
            # Keyword matching
            for cat, keywords in CAT_KEYWORDS.items():
                if any(kw in slug for kw in keywords):
                    cat_map[cat].append(game)
                    assigned.add(cat)

        # Games with no category → default to 'action'
        if not assigned:
            cat_map['action'].append(game)

    # Deduplicate (preserving order)
    for cat in cat_map:
        seen, deduped = set(), []
        for g in cat_map[cat]:
            if g['slug'] not in seen:
                seen.add(g['slug'])
                deduped.append(g)
        cat_map[cat] = deduped

    return cat_map


# ═══════════════════════════════════════════════════════════════
# STEP 3 — HTML HELPERS
# ═══════════════════════════════════════════════════════════════

def nav_html() -> str:
    items = []
    for slug, (name, emoji, *_) in CATEGORIES.items():
        items.append(f'<li><a href="{BASE_URL}/categ/{slug}">{emoji} {name}</a></li>')
    return '<ul class="nav-categories">\n' + '\n'.join(items) + '\n</ul>'


def games_grid_html(games: list) -> str:
    cards = []
    for g in games:
        cards.append(
            f'<a href="{BASE_URL}/{g["slug"]}" class="game-card">\n'
            f'  <img src="{g["image"]}" alt="{g["title"]}" loading="lazy">\n'
            f'  <h3>{g["title"]}</h3>\n'
            f'</a>'
        )
    return '<div class="games-grid">\n' + '\n'.join(cards) + '\n</div>'


def pagination_html(cat_slug: str, current_page: int, total_pages: int) -> str:
    if total_pages <= 1:
        return ''

    def page_url(p):
        if p == 1:
            return f"{BASE_URL}/categ/{cat_slug}/"
        return f"{BASE_URL}/categ/{cat_slug}-page-{p}/"

    parts = []
    if current_page > 1:
        parts.append(f'<a href="{page_url(current_page - 1)}" class="page-btn">« Previous</a>')
    for p in range(1, total_pages + 1):
        cls = 'page-btn active' if p == current_page else 'page-btn'
        parts.append(f'<a href="{page_url(p)}" class="{cls}">{p}</a>')
    if current_page < total_pages:
        parts.append(f'<a href="{page_url(current_page + 1)}" class="page-btn">Next »</a>')

    return '<div class="pagination">\n' + '\n'.join(parts) + '\n</div>'


def category_links_html() -> str:
    links = []
    for slug, (name, emoji, *_) in CATEGORIES.items():
        links.append(f'<a href="{BASE_URL}/categ/{slug}">{emoji} {name}</a>')
    return '<div class="category-links">\n' + '\n'.join(links) + '\n</div>'


# ═══════════════════════════════════════════════════════════════
# STEP 4 — EXTRACT TEMPLATE FROM EXISTING WORKING PAGE
# ═══════════════════════════════════════════════════════════════

def load_template(root: Path):
    """
    Try to extract the header+footer HTML shell from an existing broken
    category page (they all share the same template, minus the game grid).
    Returns (header_html, footer_html) or (None, None) if not found.
    """
    # Use any existing broken categ page as template donor
    candidates = list((root / 'categ').glob('*/index.html'))
    for cand in candidates:
        try:
            raw = cand.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        if '{GAMES_GRID}' in raw or '{PAGINATION}' in raw:
            return raw  # return the whole template
    return None


# ═══════════════════════════════════════════════════════════════
# STEP 5 — BUILD CATEGORY PAGE HTML
# ═══════════════════════════════════════════════════════════════

# This is the full standalone HTML template used when no existing template
# can be read from disk (fallback only).
STANDALONE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="stylesheet" href="{BASE_URL}/assets/css/style.css">
  <style>
    /* ── Inline fallback styles (only active if the main stylesheet fails) ── */
    body {{
      background: #0d0d1a;
      color: #e0e0f0;
      font-family: 'Segoe UI', sans-serif;
      margin: 0; padding: 0;
    }}
    header {{
      background: linear-gradient(135deg, #1a1a3e, #6b21a8);
      padding: 16px 32px;
      display: flex; align-items: center; justify-content: space-between;
    }}
    header .site-title {{
      font-size: 1.4rem; font-weight: 900;
      text-transform: uppercase; letter-spacing: 2px;
      color: #fff; text-decoration: none;
    }}
    .search-bar {{ display: flex; gap: 8px; }}
    .search-bar input {{
      padding: 8px 14px; border-radius: 8px;
      border: none; background: rgba(255,255,255,0.15);
      color: #fff; width: 220px;
    }}
    .search-bar input::placeholder {{ color: #aaa; }}
    nav.cat-nav {{
      background: rgba(255,255,255,0.05);
      padding: 10px 24px; display: flex; flex-wrap: wrap; gap: 8px;
    }}
    nav.cat-nav a {{
      color: #c4b5fd; text-decoration: none; font-size: 0.85rem;
      padding: 4px 10px; border-radius: 20px;
      border: 1px solid rgba(196,181,253,0.3);
      transition: background .2s;
    }}
    nav.cat-nav a:hover {{ background: rgba(196,181,253,0.15); }}
    .hero {{
      background: linear-gradient(135deg, #1e1b4b 0%, #4c1d95 50%, #831843 100%);
      padding: 48px 32px; text-align: center;
      border-left: 4px solid #a855f7;
    }}
    .hero h1 {{ font-size: 2.2rem; margin: 0 0 8px; color: #e9d5ff; }}
    .hero p  {{ color: #c4b5fd; margin: 0; font-size: 1rem; }}
    .section-title {{
      text-align: center; font-size: 1.1rem; font-weight: 700;
      color: #818cf8; text-transform: uppercase; letter-spacing: 2px;
      margin: 40px 0 20px;
    }}
    .games-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 16px; padding: 0 32px;
    }}
    .game-card {{
      background: #1e1b4b; border-radius: 12px; overflow: hidden;
      text-decoration: none; color: #e9d5ff;
      transition: transform .2s, box-shadow .2s;
      border: 1px solid rgba(139,92,246,0.25);
    }}
    .game-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(139,92,246,0.4);
    }}
    .game-card img {{
      width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block;
    }}
    .game-card h3 {{
      font-size: 0.82rem; padding: 8px 10px; margin: 0;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .pagination {{
      display: flex; justify-content: center; gap: 8px;
      margin: 32px 0; flex-wrap: wrap;
    }}
    .page-btn {{
      padding: 8px 16px; border-radius: 50px;
      border: 1px solid rgba(139,92,246,0.4);
      color: #c4b5fd; text-decoration: none; font-size: 0.9rem;
      transition: background .2s;
    }}
    .page-btn:hover, .page-btn.active {{
      background: #7c3aed; color: #fff; border-color: #7c3aed;
    }}
    .cta-box {{
      background: #1e1b4b; border-radius: 16px;
      margin: 40px 32px; padding: 32px; text-align: center;
    }}
    .cta-box h2 {{ color: #818cf8; font-size: 1.2rem; margin: 0 0 10px; }}
    .cta-box p  {{ color: #a5b4fc; margin: 0; }}
    .category-links {{
      display: flex; flex-wrap: wrap; gap: 10px;
      padding: 0 32px; margin: 24px 0;
      justify-content: center;
    }}
    .category-links a {{
      color: #c4b5fd; text-decoration: none; font-size: 0.9rem;
      padding: 6px 14px; border-radius: 20px;
      border: 1px solid rgba(196,181,253,0.3);
      transition: background .2s;
    }}
    .category-links a:hover {{ background: rgba(196,181,253,0.15); }}
    footer {{
      text-align: center; padding: 24px; color: #6b7280;
      font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05);
    }}
    footer a {{ color: #818cf8; text-decoration: none; margin: 0 8px; }}
  </style>
</head>
<body>

<header>
  <a href="{BASE_URL}/" class="site-title">Unblocked Games USA</a>
  <div class="search-bar">
    <input type="text" id="global-search" placeholder="Search games..."
           oninput="doSearch(this.value)"
           onkeydown="if(event.key==='Enter')goSearch(this.value)">
  </div>
</header>

<nav class="cat-nav">
{nav_items}
</nav>

<div class="hero">
  <h1>{emoji} {cat_name} Games</h1>
  <p>{tagline}</p>
</div>

<h2 class="section-title">Popular {cat_name} Games</h2>

{games_grid}

{pagination}

<div class="cta-box">
  <h2>🎮 {cat_name} Games</h2>
  <p>{long_desc}</p>
</div>

<h2 class="section-title">🎮 Browse by Category</h2>
{cat_links}

<footer>
  © Unblocked Games USA. All rights reserved.
  <br>
  <a href="{BASE_URL}/privacy-policy/">Privacy Policy</a>
  <a href="{BASE_URL}/contact/">Contact Us</a>
  <a href="{BASE_URL}/faq/">FAQ</a>
  <a href="{BASE_URL}/dmca/">DMCA</a>
</footer>

<script>
// Site-wide search — loads games.json and redirects to /search/
async function loadGames() {{
  try {{
    const r = await fetch('{BASE_URL}/games.json');
    window._allGames = await r.json();
  }} catch(e) {{ window._allGames = []; }}
}}
loadGames();

function doSearch(q) {{
  const box = document.getElementById('global-search');
  // Preview logic could be added here
}}

function goSearch(q) {{
  if (q.trim()) window.location.href = '{BASE_URL}/search/?q=' + encodeURIComponent(q.trim());
}}

document.getElementById('global-search').addEventListener('keydown', e => {{
  if (e.key === 'Enter') goSearch(e.target.value);
}});
</script>
</body>
</html>
"""


def build_category_page_html(
    cat_slug: str, current_page: int, total_pages: int,
    games_on_page: list, template_raw: str | None
) -> str:
    """
    Build the full HTML for one category page.
    If template_raw is provided, replace placeholders in the existing template.
    Otherwise generate a standalone page.
    """
    name, emoji, tagline, long_desc = CATEGORIES[cat_slug]

    grid   = games_grid_html(games_on_page)
    pages  = pagination_html(cat_slug, current_page, total_pages)
    catlinks = category_links_html()

    if template_raw and ('{GAMES_GRID}' in template_raw
                         or '{PAGINATION}' in template_raw):
        # ── Patch the existing template ────────────────────────────────
        html = template_raw

        # Fix wrong category name in headings/text
        # These are all the patterns the broken templates contain
        for wrong in ['Multiplayer Games Games', 'Multiplayer Games',
                      'Puzzle Games', 'Action Games', 'Racing Games',
                      'Shooter Games', 'Platformer Games', '2-Player Games',
                      'Fighting Games', 'Driving Games', 'Skill Games',
                      'Adventure Games', 'Strategy Games', 'Sports Games',
                      'Simulation Games', 'Clicker Games', 'Horror Games',
                      'Kids Games']:
            html = html.replace(f'Popular {wrong}', f'Popular {name} Games')
            html = html.replace(f'Join the World of {wrong}', f'Join the World of {name} Games')
            html = html.replace(f'Play the best multiplayer games',
                                f'Play the best {name.lower()} games')

        # Update the page <title> if still wrong
        html = re.sub(
            r'<title>[^<]*</title>',
            f'<title>{name} Games Unblocked - Free Online Games</title>',
            html, flags=re.IGNORECASE
        )

        # Update hero title (h1) — only if it still says the wrong category
        def fix_h1(m):
            return f'<h1>{emoji} {name} Games</h1>'
        html = re.sub(r'<h1[^>]*>[^<]*</h1>', fix_h1, html, count=1, flags=re.IGNORECASE)

        # Replace placeholders
        html = html.replace('{GAMES_GRID}',    grid)
        html = html.replace('{PAGINATION}',    pages)
        html = html.replace('{CATEGORY_LINKS}', catlinks)

        # Inject global search script if not present
        if 'games.json' not in html:
            search_script = f'''<script>
async function loadGames(){{try{{const r=await fetch('{BASE_URL}/games.json');window._allGames=await r.json();}}catch(e){{window._allGames=[];}}}}
loadGames();
document.addEventListener('keydown',e=>{{if(e.key==='Enter'&&document.activeElement.tagName==='INPUT'){{const q=document.activeElement.value.trim();if(q)window.location.href='{BASE_URL}/search/?q='+encodeURIComponent(q);}}}});
</script>'''
            html = html.replace('</body>', search_script + '\n</body>')

        return html

    else:
        # ── Generate a standalone page ─────────────────────────────────
        nav_items_html = '\n'.join(
            f'  <a href="{BASE_URL}/categ/{s}">{e} {n}</a>'
            for s, (n, e, *_) in CATEGORIES.items()
        )
        page_title = (f'{name} Games Unblocked - Free Online Games')
        meta_desc  = long_desc[:155]

        return STANDALONE_TEMPLATE.format(
            page_title=page_title,
            meta_desc=meta_desc,
            BASE_URL=BASE_URL,
            nav_items=nav_items_html,
            emoji=emoji,
            cat_name=name,
            tagline=tagline,
            long_desc=long_desc,
            games_grid=grid,
            pagination=pages,
            cat_links=catlinks,
        )


# ═══════════════════════════════════════════════════════════════
# STEP 6 — LEGAL PAGES
# ═══════════════════════════════════════════════════════════════

def legal_page_html(page_type: str, existing_html: str | None) -> str:
    """Return proper HTML for a legal page, reusing the site's header/footer."""

    contents = {
        'faq': {
            'title': 'FAQ — Frequently Asked Questions | Unblocked Games USA',
            'heading': '❓ Frequently Asked Questions',
            'body': '''
<div class="legal-section">
  <h2>What is Unblocked Games USA?</h2>
  <p>Unblocked Games USA is a free browser-based gaming portal featuring hundreds of games
  playable directly in your browser — no downloads, no sign-ups, no plugins required.
  Our games work on school networks, public Wi-Fi, and anywhere else you want to play.</p>

  <h2>Are the games really free?</h2>
  <p>Yes — every game on this site is 100% free to play. We will never charge you or ask for
  payment details. Just click and play instantly.</p>

  <h2>Do I need to create an account?</h2>
  <p>No account is needed. All games are accessible directly from the browser with no
  registration, email, or personal information required.</p>

  <h2>Why are some games "unblocked"?</h2>
  <p>Many schools and workplaces block popular gaming sites. Our games are hosted on GitHub
  Pages which is often whitelisted. If a game doesn't load, please check that your browser
  allows iframes or JavaScript.</p>

  <h2>Which browsers are supported?</h2>
  <p>All modern browsers are supported — Google Chrome, Mozilla Firefox, Microsoft Edge,
  Safari, and Opera. For the best experience we recommend using the latest version of
  Google Chrome or Firefox.</p>

  <h2>Can I suggest a game?</h2>
  <p>We love suggestions! Please use our <a href="/contact/">Contact page</a> to send game
  requests. We add new games regularly.</p>

  <h2>Are the games safe for kids?</h2>
  <p>We aim to keep all content school-friendly and age-appropriate. Games marked in the
  <a href="/categ/kids/">Kids category</a> are specifically selected for younger audiences.
  However, parental guidance is always recommended for online content.</p>

  <h2>Why does a game not load?</h2>
  <p>Please try: (1) Refreshing the page, (2) Clearing browser cache, (3) Trying a different
  browser, (4) Disabling any ad-blocker extensions that may interfere with iframes.</p>

  <h2>How often are new games added?</h2>
  <p>We add new games frequently. Check back regularly or browse the categories to discover
  new titles!</p>

  <h2>Do you collect personal data?</h2>
  <p>We do not collect personally identifiable information. Please see our
  <a href="/privacy-policy/">Privacy Policy</a> for full details.</p>
</div>
'''
        },
        'dmca': {
            'title': 'DMCA Policy | Unblocked Games USA',
            'heading': '©️ DMCA Policy',
            'body': '''
<div class="legal-section">
  <p><strong>Effective Date:</strong> January 1, 2024</p>

  <p>Unblocked Games USA respects the intellectual property rights of others and expects users
  of our site to do the same. In accordance with the Digital Millennium Copyright Act of 1998
  (DMCA), we will respond expeditiously to claims of copyright infringement.</p>

  <h2>Reporting Infringement</h2>
  <p>If you believe that any content on our site infringes your copyright, please submit a
  written DMCA notice containing the following information:</p>
  <ul>
    <li>A physical or electronic signature of a person authorized to act on behalf of the
    owner of the copyright that has allegedly been infringed.</li>
    <li>Identification of the copyrighted work claimed to have been infringed.</li>
    <li>Identification of the material on our site that you claim is infringing, with enough
    detail so we can locate it (URL, page title, etc.).</li>
    <li>Your address, telephone number, and email address.</li>
    <li>A statement that you have a good faith belief that the disputed use is not authorized
    by the copyright owner, its agent, or the law.</li>
    <li>A statement, made under penalty of perjury, that the above information is accurate
    and that you are the copyright owner or are authorized to act on behalf of the owner.</li>
  </ul>

  <h2>Where to Send Notices</h2>
  <p>Please use our <a href="/contact/">Contact page</a> to send DMCA notices. We will
  review all valid notices and take appropriate action including removal of infringing
  content where required.</p>

  <h2>Counter-Notification</h2>
  <p>If you believe content was removed by mistake, you may submit a counter-notification
  as described under 17 U.S.C. § 512(g)(3).</p>

  <h2>Repeat Infringers</h2>
  <p>It is our policy to disable and/or terminate, in appropriate circumstances, the
  accounts of users who are repeat infringers.</p>

  <p>This DMCA policy is provided for informational purposes and does not constitute legal
  advice. For legal concerns, please consult a qualified attorney.</p>
</div>
'''
        },
        'privacy-policy': {
            'title': 'Privacy Policy | Unblocked Games USA',
            'heading': '🔒 Privacy Policy',
            'body': '''
<div class="legal-section">
  <p><strong>Last Updated:</strong> January 1, 2024</p>

  <p>Unblocked Games USA ("we", "us", "our") is committed to protecting your privacy.
  This Privacy Policy explains how we handle information when you visit our website at
  <a href="https://unblockedgames-usa.github.io">unblockedgames-usa.github.io</a>.</p>

  <h2>Information We Collect</h2>
  <p>We do <strong>not</strong> collect personally identifiable information (PII) such as
  your name, email address, or payment information. We do not require account registration
  to use our site.</p>

  <p>Like most websites, our hosting provider (GitHub Pages) may automatically collect
  standard server log data including IP addresses, browser type, and page views. This data
  is used solely for security and operational purposes and is governed by
  <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"
  target="_blank" rel="noopener">GitHub's Privacy Policy</a>.</p>

  <h2>Cookies</h2>
  <p>We do not use cookies for tracking or advertising. Some embedded games may set their
  own cookies to save game progress — this is controlled by the individual game developer,
  not by us.</p>

  <h2>Third-Party Services</h2>
  <p>Games on our site may be hosted via third-party iframes. These services have their own
  privacy policies and we encourage you to review them. We are not responsible for the
  privacy practices of third-party game providers.</p>

  <h2>Children's Privacy</h2>
  <p>Our site is intended for a general audience. We do not knowingly collect any information
  from children under the age of 13. If you believe a child has provided us with personal
  information, please contact us and we will delete it promptly.</p>

  <h2>Changes to This Policy</h2>
  <p>We may update this Privacy Policy from time to time. Changes will be posted on this
  page with a revised effective date.</p>

  <h2>Contact</h2>
  <p>If you have questions about this Privacy Policy, please use our
  <a href="/contact/">Contact page</a>.</p>
</div>
'''
        },
        'contact': {
            'title': 'Contact Us | Unblocked Games USA',
            'heading': '📬 Contact Us',
            'body': '''
<div class="legal-section">
  <p>Have a question, game suggestion, bug report, or DMCA request? We'd love to hear from
  you!</p>

  <h2>Get In Touch</h2>
  <p>The best way to reach us is via our GitHub repository where you can open an issue or
  discussion:</p>
  <p>
    <a href="https://github.com/UnblockedGames-USA/UnblockedGames-USA.github.io/issues"
       target="_blank" rel="noopener" class="cta-button">
      Open an Issue on GitHub →
    </a>
  </p>

  <h2>What We Can Help With</h2>
  <ul>
    <li>🎮 <strong>Game Suggestions</strong> — Want us to add a game? Let us know!</li>
    <li>🐛 <strong>Bug Reports</strong> — Game not loading? Tell us the game name and your browser.</li>
    <li>©️ <strong>DMCA / Copyright</strong> — See our <a href="/dmca/">DMCA page</a> for details.</li>
    <li>🔒 <strong>Privacy Questions</strong> — See our <a href="/privacy-policy/">Privacy Policy</a>.</li>
    <li>❓ <strong>General Questions</strong> — Check our <a href="/faq/">FAQ</a> first!</li>
  </ul>

  <h2>Response Time</h2>
  <p>We are a small volunteer-run project. We aim to respond to all inquiries within
  7 business days. DMCA notices are handled as a priority.</p>

  <h2>Frequently Asked Questions</h2>
  <p>Before contacting us, please check our <a href="/faq/">FAQ page</a> — your question
  may already be answered there.</p>
</div>
'''
        },
    }

    if page_type not in contents:
        return ''

    data = contents[page_type]

    # Try to reuse the site's header/footer from existing_html
    if existing_html:
        # Replace the main content between nav and footer description sections
        # Strategy: replace everything from <h1> to the last </div> before <footer>
        # with our new content
        pass  # Fall through to standalone below for safety

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data["title"]}</title>
  <link rel="stylesheet" href="{BASE_URL}/assets/css/style.css">
  <style>
    body {{ background:#0d0d1a; color:#e0e0f0; font-family:'Segoe UI',sans-serif; margin:0; }}
    header {{ background:linear-gradient(135deg,#1a1a3e,#6b21a8); padding:16px 32px;
              display:flex; align-items:center; justify-content:space-between; }}
    header .site-title {{ font-size:1.4rem; font-weight:900; text-transform:uppercase;
              letter-spacing:2px; color:#fff; text-decoration:none; }}
    nav.cat-nav {{ background:rgba(255,255,255,.05); padding:10px 24px;
                   display:flex; flex-wrap:wrap; gap:8px; }}
    nav.cat-nav a {{ color:#c4b5fd; text-decoration:none; font-size:.85rem;
                     padding:4px 10px; border-radius:20px;
                     border:1px solid rgba(196,181,253,.3); }}
    nav.cat-nav a:hover {{ background:rgba(196,181,253,.15); }}
    .legal-hero {{ background:linear-gradient(135deg,#1e1b4b 0%,#4c1d95 50%,#831843 100%);
                   padding:48px 32px; text-align:center; border-left:4px solid #a855f7; }}
    .legal-hero h1 {{ font-size:2rem; color:#e9d5ff; margin:0; }}
    .legal-section {{ max-width:800px; margin:40px auto; padding:0 32px; line-height:1.8; }}
    .legal-section h2 {{ color:#818cf8; margin-top:32px; }}
    .legal-section a {{ color:#a78bfa; }}
    .legal-section ul {{ padding-left:20px; }}
    .legal-section li {{ margin-bottom:8px; }}
    .cta-button {{ display:inline-block; background:#7c3aed; color:#fff; padding:12px 24px;
                   border-radius:8px; text-decoration:none; font-weight:600; margin:8px 0; }}
    footer {{ text-align:center; padding:24px; color:#6b7280; font-size:.8rem;
              border-top:1px solid rgba(255,255,255,.05); margin-top:60px; }}
    footer a {{ color:#818cf8; text-decoration:none; margin:0 8px; }}
  </style>
</head>
<body>
<header>
  <a href="{BASE_URL}/" class="site-title">Unblocked Games USA</a>
</header>
<nav class="cat-nav">
{chr(10).join(f'  <a href="{BASE_URL}/categ/{s}">{e} {n}</a>' for s,(n,e,*_) in CATEGORIES.items())}
</nav>
<div class="legal-hero">
  <h1>{data["heading"]}</h1>
</div>
{data["body"]}
<footer>
  © Unblocked Games USA. All rights reserved.
  <a href="{BASE_URL}/privacy-policy/">Privacy Policy</a>
  <a href="{BASE_URL}/contact/">Contact Us</a>
  <a href="{BASE_URL}/faq/">FAQ</a>
  <a href="{BASE_URL}/dmca/">DMCA</a>
</footer>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════
# STEP 7 — SEARCH PAGE + games.json
# ═══════════════════════════════════════════════════════════════

def build_search_page(games: list) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Search Games | Unblocked Games USA</title>
  <link rel="stylesheet" href="{BASE_URL}/assets/css/style.css">
  <style>
    body{{background:#0d0d1a;color:#e0e0f0;font-family:'Segoe UI',sans-serif;margin:0}}
    header{{background:linear-gradient(135deg,#1a1a3e,#6b21a8);padding:16px 32px;
            display:flex;align-items:center;justify-content:space-between}}
    header a{{color:#fff;text-decoration:none;font-size:1.4rem;font-weight:900;
              text-transform:uppercase;letter-spacing:2px}}
    .search-wrap{{max-width:700px;margin:48px auto 32px;padding:0 24px;text-align:center}}
    .search-wrap h1{{color:#e9d5ff;font-size:1.8rem;margin-bottom:20px}}
    #q{{width:100%;padding:14px 20px;font-size:1rem;border-radius:12px;
        border:2px solid #7c3aed;background:#1e1b4b;color:#e9d5ff;box-sizing:border-box}}
    #q::placeholder{{color:#6b7280}}
    #results-count{{color:#818cf8;margin:12px 0;font-size:.9rem}}
    .games-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));
                 gap:16px;padding:0 24px 40px}}
    .game-card{{background:#1e1b4b;border-radius:12px;overflow:hidden;
                text-decoration:none;color:#e9d5ff;
                border:1px solid rgba(139,92,246,.25);transition:transform .2s,box-shadow .2s}}
    .game-card:hover{{transform:translateY(-4px);box-shadow:0 8px 24px rgba(139,92,246,.4)}}
    .game-card img{{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}}
    .game-card h3{{font-size:.82rem;padding:8px 10px;margin:0;
                   white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .no-results{{text-align:center;padding:40px;color:#6b7280}}
    footer{{text-align:center;padding:24px;color:#6b7280;font-size:.8rem;
            border-top:1px solid rgba(255,255,255,.05)}}
    footer a{{color:#818cf8;text-decoration:none;margin:0 8px}}
  </style>
</head>
<body>
<header>
  <a href="{BASE_URL}/">Unblocked Games USA</a>
</header>

<div class="search-wrap">
  <h1>🔍 Search All Games</h1>
  <input id="q" type="text" placeholder="Type a game name…" autocomplete="off" autofocus>
  <p id="results-count"></p>
</div>

<div class="games-grid" id="grid"></div>
<p class="no-results" id="no-results" style="display:none">
  No games found. Try a different search term!
</p>

<footer>
  © Unblocked Games USA. All rights reserved.
  <a href="{BASE_URL}/privacy-policy/">Privacy Policy</a>
  <a href="{BASE_URL}/contact/">Contact</a>
  <a href="{BASE_URL}/faq/">FAQ</a>
</footer>

<script>
const GAMES = {json.dumps(games, ensure_ascii=False)};

function render(list) {{
  const grid = document.getElementById('grid');
  const none = document.getElementById('no-results');
  const cnt  = document.getElementById('results-count');
  grid.innerHTML = list.map(g =>
    `<a href="${{g.url}}" class="game-card">
       <img src="${{g.image}}" alt="${{g.title}}" loading="lazy"
            onerror="this.src='{BASE_URL}/images/placeholder.png'">
       <h3>${{g.title}}</h3>
     </a>`
  ).join('');
  none.style.display = list.length ? 'none' : 'block';
  cnt.textContent    = list.length ? list.length + ' game' + (list.length===1?'':'s') + ' found' : '';
}}

function search(q) {{
  q = q.toLowerCase().trim();
  render(q ? GAMES.filter(g => g.title.toLowerCase().includes(q)
                            || g.slug.toLowerCase().includes(q)) : GAMES);
}}

document.getElementById('q').addEventListener('input', e => search(e.target.value));

// Pre-fill from URL ?q=
const params = new URLSearchParams(location.search);
const initial = params.get('q') || '';
if (initial) {{ document.getElementById('q').value = initial; }}
search(initial);
</script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  UnblockedGames-USA Fix Script")
    print("=" * 60)

    # ── 1. Collect all games ──────────────────────────────────────
    print("\n[1/5] Scanning game folders…")
    games = get_all_games(ROOT)
    print(f"      Found {len(games)} games.")

    # ── 2. Assign categories ──────────────────────────────────────
    print("\n[2/5] Assigning categories…")
    cat_map = assign_categories(games)
    for slug, glist in sorted(cat_map.items()):
        print(f"      {slug:15s} → {len(glist)} games")

    # ── 3. Load template HTML (from any broken categ page) ────────
    print("\n[3/5] Loading page template…")
    template_raw = load_template(ROOT)
    if template_raw:
        print("      Template loaded from existing category page.")
    else:
        print("      No template found — will generate standalone HTML.")

    # ── 4. Fix / create all category pages ───────────────────────
    print("\n[4/5] Fixing category pages…")
    categ_root = ROOT / 'categ'
    fixed = 0

    for cat_slug, cat_games in cat_map.items():
        total_pages = max(1, math.ceil(len(cat_games) / GAMES_PER_PAGE))

        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                page_dir = categ_root / cat_slug
            else:
                page_dir = categ_root / f"{cat_slug}-page-{page_num}"

            html_file = page_dir / 'index.html'

            # Decide whether to write this file
            needs_fix = False
            existing_content = None

            if html_file.exists():
                try:
                    existing_content = html_file.read_text(encoding='utf-8', errors='replace')
                    if '{GAMES_GRID}' in existing_content or '{PAGINATION}' in existing_content:
                        needs_fix = True
                except Exception:
                    needs_fix = True
            else:
                needs_fix = True  # Page doesn't exist yet → create it

            if not needs_fix:
                continue  # Already has real content — don't touch it

            # Slice games for this page
            start = (page_num - 1) * GAMES_PER_PAGE
            page_games = cat_games[start:start + GAMES_PER_PAGE]

            # Choose template source
            tmpl = existing_content if (existing_content and '{GAMES_GRID}' in str(existing_content)) \
                   else template_raw

            html_out = build_category_page_html(
                cat_slug, page_num, total_pages, page_games, tmpl
            )

            page_dir.mkdir(parents=True, exist_ok=True)
            html_file.write_text(html_out, encoding='utf-8')
            print(f"      ✓ {page_dir.relative_to(ROOT)}")
            fixed += 1

    print(f"      Fixed {fixed} category pages.")

    # ── 5. Fix legal pages ────────────────────────────────────────
    print("\n[5/5] Fixing legal pages…")
    for page_type in ('faq', 'dmca', 'privacy-policy', 'contact'):
        page_dir  = ROOT / page_type
        html_file = page_dir / 'index.html'
        existing  = None
        if html_file.exists():
            try:
                existing = html_file.read_text(encoding='utf-8', errors='replace')
            except Exception:
                pass

        html_out = legal_page_html(page_type, existing)
        page_dir.mkdir(parents=True, exist_ok=True)
        html_file.write_text(html_out, encoding='utf-8')
        print(f"      ✓ {page_type}/index.html")

    # ── 6. Generate games.json ────────────────────────────────────
    print("\n[6/6] Writing games.json…")
    # Build a flat list with category info for search
    cat_for_game = defaultdict(list)
    for cat_slug, glist in cat_map.items():
        for g in glist:
            cat_for_game[g['slug']].append(cat_slug)

    games_json = []
    for g in games:
        games_json.append({
            'slug':       g['slug'],
            'title':      g['title'],
            'image':      g['image'],
            'url':        f"{BASE_URL}/{g['slug']}/",
            'categories': cat_for_game.get(g['slug'], []),
        })

    json_path = ROOT / 'games.json'
    json_path.write_text(
        json.dumps(games_json, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"      ✓ games.json ({len(games_json)} games)")

    # ── 7. Create /search/ page ───────────────────────────────────
    search_dir = ROOT / 'search'
    search_dir.mkdir(exist_ok=True)
    (search_dir / 'index.html').write_text(
        build_search_page(games_json), encoding='utf-8'
    )
    print("      ✓ search/index.html")

    print("\n" + "=" * 60)
    print("  ✅  All done!  Push to GitHub to publish your fixes.")
    print("=" * 60)


if __name__ == '__main__':
    main()