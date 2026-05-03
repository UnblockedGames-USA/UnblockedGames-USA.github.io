"""
fix_seo_v2.py — Unblocked Games USA  ·  Full fix script
Place in: C:/Users/berra/Documents/GitHub/UnblockedGames-USA.github.io/
Run with: python fix_seo_v2.py

Fixes:
  1. Meta descriptions on every game page
  2. Duplicate H1 tags on every game page
  3. Footer: removes duplicate category nav pills from EVERY page (keeps only legal links)
  4. Homepage: replaces static "Popular Games" grid with a daily-rotating random selection
  5. Generates sitemap.xml, robots.txt, llms.txt
"""

import os, re
from datetime import date
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────────────────────────
BASE_URL   = "https://unblockedgames-usa.github.io"
SITE_ROOT  = Path(__file__).parent
TODAY      = date.today().isoformat()

CATEGORIES = [
    "shooter","platformer","2-player","fighting","driving",
    "puzzle","multiplayer","action","skill","adventure",
    "racing","strategy","sports","simulation","clicker","horror","kids",
]

SKIP_FOLDERS = {
    "assets","images","categ","privacy-policy",
    "contact","faq","dmca",".git",
}

# ── HELPERS ────────────────────────────────────────────────────────────────────

def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("-"," ").split())

def get_game_folders():
    return [
        f for f in sorted(SITE_ROOT.iterdir())
        if f.is_dir()
        and not f.name.startswith(".")
        and f.name not in SKIP_FOLDERS
        and (f / "index.html").exists()
    ]

def build_description(title):
    return (
        f"Play {title} unblocked at school or work — free browser game, "
        f"no download, no sign-up, works instantly."
    )

# ── FIX 1+2+3: Game pages (meta desc · single H1 · clean footer) ─────────────

def fix_game_page(folder: Path) -> bool:
    path = folder / "index.html"
    html = original = path.read_text(encoding="utf-8", errors="replace")
    slug  = folder.name
    title = slug_to_title(slug)

    # 1. Meta description ──────────────────────────────────────────────────────
    if 'name="description"' not in html.lower():
        tag = f'\n  <meta name="description" content="{build_description(title)}">'
        # Insert right after </title>
        html = re.sub(r'(</title>)', r'\1' + tag, html, count=1, flags=re.IGNORECASE)

    # 2. Fix duplicate H1 ──────────────────────────────────────────────────────
    # Pattern: find all <h1> blocks; demote the one that is the site logo/nav
    # (contains the site brand text or emoji) to <div class="site-logo">
    h1_blocks = list(re.finditer(r'<h1([^>]*)>(.*?)</h1>', html, re.IGNORECASE|re.DOTALL))
    if len(h1_blocks) >= 2:
        for blk in h1_blocks:
            inner = blk.group(2)
            # The nav logo H1 contains the site name or 🎮 emoji
            if "🎮" in inner or "Unblocked Games USA" in inner or "unblockedgames-usa.github.io" in inner:
                replacement = f'<div class="site-logo"{blk.group(1)}>{inner}</div>'
                html = html[:blk.start()] + replacement + html[blk.end():]
                break

    # 3. Remove footer category-pill duplicate ─────────────────────────────────
    html = remove_footer_cat_block(html)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


# ── FIX 3 HELPER: strip the footer category block ────────────────────────────
# The footer has a block of 17 <a href="/categ/..."> links right before the
# legal links.  We find that block and remove it, leaving only the legal links.

_CAT_BLOCK_RE = re.compile(
    # Matches a sequence of category links (flexible whitespace / newlines)
    r'(<a[^>]+/categ/[^>]+>.*?</a>\s*){3,}',   # 3+ consecutive categ links
    re.IGNORECASE | re.DOTALL
)

def remove_footer_cat_block(html: str) -> str:
    """
    Remove ONLY the footer duplicate category-links block.
    Strategy: find the LAST run of /categ/ links in the file and delete it.
    The nav (first occurrence) is untouched.
    """
    matches = list(_CAT_BLOCK_RE.finditer(html))
    if len(matches) >= 2:
        last = matches[-1]
        # Keep everything before and after
        html = html[:last.start()] + html[last.end():]
    return html


# ── FIX 4: Homepage daily-random games ────────────────────────────────────────

RANDOM_GAME_JS = r"""
<script>
/* ── Daily-random "Popular Games" rotation ───────────────────────────────────
   Reads every .game-card inside #all-games-grid (hidden full list),
   seeds Math.random() from today's date so the same 40 games show all day,
   then fills #popular-grid with the random pick.
──────────────────────────────────────────────────────────────────────────── */
(function() {
  function seededRandom(seed) {
    // Simple mulberry32 seeded PRNG
    return function() {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  var today = new Date();
  var seed  = today.getFullYear() * 10000 + (today.getMonth()+1) * 100 + today.getDate();
  var rand  = seededRandom(seed);

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(rand() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  document.addEventListener('DOMContentLoaded', function() {
    var allGrid    = document.getElementById('all-games-grid');
    var popGrid    = document.getElementById('popular-grid');
    if (!allGrid || !popGrid) return;

    var cards  = Array.from(allGrid.querySelectorAll('.game-card'));
    var picked = shuffle(cards).slice(0, 40);

    popGrid.innerHTML = '';
    picked.forEach(function(card) {
      popGrid.appendChild(card.cloneNode(true));
    });
  });
})();
</script>
"""

def fix_homepage(games: list) -> bool:
    """
    1. Wraps the full game list in a hidden #all-games-grid div
    2. Replaces the visible #popular-grid (or first game grid) with an empty
       placeholder that JS fills with 40 daily-random picks
    3. Injects the JS before </body>
    """
    path = SITE_ROOT / "index.html"
    html = original = path.read_text(encoding="utf-8", errors="replace")

    # -- a) Make sure every <a> game card has class="game-card" ----------------
    # (so the JS can select them)
    # The homepage links look like: <a href="/game-slug/">...</a>
    # We add class="game-card" if not already present
    def add_game_card_class(m):
        tag = m.group(0)
        href = m.group(1)
        # Only game slugs (not categ/, not privacy-policy etc.)
        if '/categ/' in href or 'privacy' in href or 'contact' in href \
           or 'faq' in href or 'dmca' in href:
            return tag
        if 'game-card' in tag:
            return tag
        return tag.replace('<a ', '<a class="game-card" ', 1)

    html = re.sub(r'<a ([^>]*href="[^"]*unblockedgames-usa\.github\.io/[^"/]+/"[^>]*)>',
                  add_game_card_class, html)
    # Also catch relative hrefs
    html = re.sub(r'<a ([^>]*href="/[a-z0-9][a-z0-9\-]+/"[^>]*)>',
                  add_game_card_class, html)

    # -- b) Wrap the full game list in #all-games-grid (hidden) ----------------
    # Find the section that contains all game cards (the big Popular Games grid)
    # We'll look for the first <section> or <div> that contains many game links
    # Strategy: find the H2 "Popular Games" and wrap the content after it

    # Find the popular games section
    pop_h2 = re.search(
        r'(<h2[^>]*>.*?Popular.*?Games.*?</h2>)',
        html, re.IGNORECASE | re.DOTALL
    )

    if pop_h2:
        # Find the next section boundary (another H2 or a footer-like element)
        after_h2 = html[pop_h2.end():]
        next_section = re.search(r'<h2|<footer|<section', after_h2, re.IGNORECASE)
        if next_section:
            game_block = after_h2[:next_section.start()]
            rest       = after_h2[next_section.start():]

            new_block = (
                '\n<div id="popular-grid" class="games-grid">\n'
                '  <!-- filled by daily-random JS -->\n'
                '</div>\n'
                '<div id="all-games-grid" style="display:none">\n'
                + game_block.strip() + '\n'
                '</div>\n'
            )
            html = html[:pop_h2.end()] + new_block + rest

    # -- c) Remove footer category block (same as game pages) ------------------
    html = remove_footer_cat_block(html)

    # -- d) Inject JS before </body> -------------------------------------------
    if 'all-games-grid' in html and RANDOM_GAME_JS not in html:
        html = html.replace('</body>', RANDOM_GAME_JS + '\n</body>', 1)
        if '</body>' not in html:
            html += RANDOM_GAME_JS  # fallback

    if html != original:
        path.write_text(html, encoding="utf-8")
        print("   ✅ Homepage updated with daily-random games + footer fix")
        return True
    print("   ⚠️  Homepage: no changes detected (check HTML structure manually)")
    return False


# ── SITEMAP ────────────────────────────────────────────────────────────────────

def build_sitemap(games):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    def url(loc, priority, freq="weekly"):
        return (f"  <url><loc>{loc}</loc>"
                f"<lastmod>{TODAY}</lastmod>"
                f"<changefreq>{freq}</changefreq>"
                f"<priority>{priority}</priority></url>")

    lines.append(url(BASE_URL + "/",     "1.0", "daily"))
    for c in CATEGORIES:
        lines.append(url(f"{BASE_URL}/categ/{c}/", "0.8"))
    for f in games:
        lines.append(url(f"{BASE_URL}/{f.name}/",  "0.6"))
    lines.append("</urlset>")
    return "\n".join(lines)

# ── ROBOTS.TXT ─────────────────────────────────────────────────────────────────

ROBOTS = f"""User-agent: *
Allow: /
Disallow: /assets/

Sitemap: {BASE_URL}/sitemap.xml
"""

# ── LLMS.TXT ───────────────────────────────────────────────────────────────────

LLMS = f"""# Unblocked Games USA

> Free unblocked browser games — play at school, work, or home instantly.
> No downloads. No sign-ups. 500+ games across 17 categories.

## What is Unblocked Games USA?

Unblocked Games USA ({BASE_URL}) is a free online gaming portal hosting 500+
browser games that work through school and office network restrictions. All
games run directly in the browser using HTML5 — no Flash, no downloads.

## Categories

- **Shooter** — {BASE_URL}/categ/shooter/
- **Platformer** — {BASE_URL}/categ/platformer/
- **2-Player** — {BASE_URL}/categ/2-player/
- **Fighting** — {BASE_URL}/categ/fighting/
- **Driving** — {BASE_URL}/categ/driving/
- **Puzzle** — {BASE_URL}/categ/puzzle/
- **Multiplayer** — {BASE_URL}/categ/multiplayer/
- **Action** — {BASE_URL}/categ/action/
- **Skill** — {BASE_URL}/categ/skill/
- **Adventure** — {BASE_URL}/categ/adventure/
- **Racing** — {BASE_URL}/categ/racing/
- **Strategy** — {BASE_URL}/categ/strategy/
- **Sports** — {BASE_URL}/categ/sports/
- **Simulation** — {BASE_URL}/categ/simulation/
- **Clicker** — {BASE_URL}/categ/clicker/
- **Horror** — {BASE_URL}/categ/horror/
- **Kids** — {BASE_URL}/categ/kids/

## Top Games

- 1v1.LOL Unblocked — {BASE_URL}/1v1-lol/
- Among Us Unblocked — {BASE_URL}/among-us/
- Basketball Legends — {BASE_URL}/basketball-legends/
- 2048 — {BASE_URL}/2048/
- Bloxorz — {BASE_URL}/bloxorz/
- Age of War — {BASE_URL}/age-of-war/
- Bad Ice Cream 2 — {BASE_URL}/bad-ice-cream-2/
- BitLife — {BASE_URL}/bitlife/
- Basket Bros — {BASE_URL}/basket-bros/
- Bob the Robber 4 — {BASE_URL}/bob-the-robber-4/

## Site Info

- URL: {BASE_URL}
- Sitemap: {BASE_URL}/sitemap.xml
- Updated: {TODAY}
- Contact: {BASE_URL}/contact
- DMCA: {BASE_URL}/dmca
- Privacy: {BASE_URL}/privacy-policy
"""

# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 58)
    print("  Unblocked Games USA — SEO + UX Fixer v2")
    print("=" * 58)

    games = get_game_folders()
    print(f"\n🔍 Found {len(games)} game folders\n")

    # Fix all game pages
    changed = 0
    for folder in games:
        if fix_game_page(folder):
            changed += 1
    print(f"✅ Game pages fixed: {changed} / {len(games)}\n")

    # Fix homepage
    print("🏠 Fixing homepage…")
    fix_homepage(games)

    # Write supporting files
    (SITE_ROOT / "sitemap.xml").write_text(build_sitemap(games), encoding="utf-8")
    print(f"\n🗺️  sitemap.xml  → {len(games) + 1 + len(CATEGORIES)} URLs")

    (SITE_ROOT / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    print("🤖 robots.txt written")

    (SITE_ROOT / "llms.txt").write_text(LLMS, encoding="utf-8")
    print("🤖 llms.txt written")

    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Done!  Now push to GitHub:

   git add -A
   git commit -m "SEO v2: random games, footer fix, meta descs, sitemap"
   git push

Then submit sitemap in Google Search Console:
  https://unblockedgames-usa.github.io/sitemap.xml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

if __name__ == "__main__":
    main()
