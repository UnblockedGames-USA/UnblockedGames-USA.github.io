"""
fix_seo.py — Unblocked Games USA SEO Fixer (Improved)
Run from your repo root:
    python fix_seo.py
"""

import os
import re
from datetime import date
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────────────────────────
BASE_URL = "https://unblockedgames-usa.github.io"
SITE_ROOT = Path(__file__).parent
TODAY = date.today().isoformat()

CATEGORIES = [
    "shooter", "platformer", "2-player", "fighting", "driving",
    "puzzle", "multiplayer", "action", "skill", "adventure",
    "racing", "strategy", "sports", "simulation", "clicker",
    "horror", "kids",
]

SKIP_FOLDERS = {"assets", "images", "categ", "privacy-policy", "contact", "faq", "dmca", ".git"}


# ── HELPERS ────────────────────────────────────────────────────────────────────
def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("-", " ").split())


def get_game_folders() -> list[Path]:
    games = []
    for item in sorted(SITE_ROOT.iterdir()):
        if item.is_dir() and not item.name.startswith(".") and item.name not in SKIP_FOLDERS:
            if (item / "index.html").exists():
                games.append(item)
    return games


def build_description(title: str) -> str:
    return (
        f"Play {title} unblocked at school or work. "
        "Free browser game — no download, no sign-up, instant play."
    )


def fix_game_page(folder: Path) -> bool:
    """Fix one game page. Returns True if file was changed."""
    html_path = folder / "index.html"
    try:
        original = html_path.read_text(encoding="utf-8", errors="replace")
        html = original
        slug = folder.name
        title = slug_to_title(slug)

        changed = False

        # 1. Add meta description if missing
        if 'name="description"' not in html:
            desc = build_description(title)
            meta = f'<meta name="description" content="{desc}">\n'
            # Insert after <title> tag
            html = re.sub(r'(</title>\s*)', r'\1' + meta, html, count=1)
            changed = True

        # 2. Fix duplicate H1s (keep only one real H1)
        h1_count = len(re.findall(r'<h1[\s>]', html, re.IGNORECASE))
        if h1_count >= 2:
            # Find all h1 blocks
            pattern = re.compile(r'<h1([^>]*)>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
            blocks = list(pattern.finditer(html))

            if len(blocks) >= 2:
                # Demote the first H1 (usually the nav/logo) to a div
                first = blocks[0]
                inner = first.group(2)
                replacement = f'<div class="site-logo"{first.group(1)}>{inner}</div>'
                html = html[:first.start()] + replacement + html[first.end():]
                changed = True

        if changed:
            html_path.write_text(html, encoding="utf-8")
            return True
        return False

    except Exception as e:
        print(f"   ❌ Error in {folder.name}: {e}")
        return False


# ── SITEMAP ────────────────────────────────────────────────────────────────────
def build_sitemap(game_folders: list[Path]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    def entry(loc, priority, changefreq="weekly"):
        return (
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{TODAY}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    # Homepage
    lines.append(entry(BASE_URL + "/", "1.0", "daily"))

    # Categories
    for cat in CATEGORIES:
        lines.append(entry(f"{BASE_URL}/categ/{cat}/", "0.8"))

    # Games
    for folder in game_folders:
        lines.append(entry(f"{BASE_URL}/{folder.name}/", "0.6", "monthly"))

    lines.append("</urlset>")
    return "\n".join(lines)


# ── ROBOTS + LLMS ──────────────────────────────────────────────────────────────
ROBOTS_TXT = f"""User-agent: *
Allow: /
Disallow: /assets/
Sitemap: {BASE_URL}/sitemap.xml
"""

LLMS_TXT = f"""# Unblocked Games USA
> Free unblocked games for school, work, and home. No downloads. Instant play.

Website: {BASE_URL}
Total Games: 500+
Updated: {TODAY}

## Categories
{', '.join(CATEGORIES)}

## Popular Games
- 1v1.LOL: {BASE_URL}/1v1-lol/
- Among Us: {BASE_URL}/among-us/
- Basketball Legends: {BASE_URL}/basketball-legends/
- Bloxorz: {BASE_URL}/bloxorz/
- BitLife: {BASE_URL}/bitlife/
- 2048: {BASE_URL}/2048/

Full list: {BASE_URL}/sitemap.xml
"""


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    print("🔍 Scanning for game folders...")
    game_folders = get_game_folders()
    print(f"   Found {len(game_folders)} games\n")

    fixed = 0
    for folder in game_folders:
        if fix_game_page(folder):
            fixed += 1
            print(f"   ✅ Fixed: {folder.name}")

    print(f"\n📝 Fixed {fixed} / {len(game_folders)} game pages\n")

    # Write files
    (SITE_ROOT / "sitemap.xml").write_text(build_sitemap(game_folders), encoding="utf-8")
    print("🗺️  sitemap.xml updated")

    (SITE_ROOT / "robots.txt").write_text(ROBOTS_TXT, encoding="utf-8")
    print("🤖 robots.txt created")

    (SITE_ROOT / "llms.txt").write_text(LLMS_TXT, encoding="utf-8")
    print("🤖 llms.txt created")

    print("\n✅ All done!")
    print("\nNext steps:")
    print("   git add -A")
    print('   git commit -m "SEO: meta descriptions + H1 fix + sitemap + robots + llms.txt"')
    print("   git push")


if __name__ == "__main__":
    main()