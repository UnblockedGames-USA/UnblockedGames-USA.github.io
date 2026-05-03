"""
debug_html.py — Run this FIRST to check your HTML structure.
Place in: C:/Users/berra/Documents/GitHub/UnblockedGames-USA.github.io/
Run with: python debug_html.py

It will print the key parts of one game page so you can confirm
the fix script is targeting the right patterns.
"""

from pathlib import Path
import re

SITE_ROOT = Path(__file__).parent

# Pick the first game folder that has an index.html
game = next(
    (f for f in sorted(SITE_ROOT.iterdir())
     if f.is_dir() and not f.name.startswith(".")
     and f.name not in {"assets","images","categ","privacy-policy","contact","faq","dmca",".git"}
     and (f / "index.html").exists()),
    None
)

if not game:
    print("❌ No game folder found!")
    exit()

html = (game / "index.html").read_text(encoding="utf-8", errors="replace")
print(f"📄 Inspecting: {game.name}/index.html  ({len(html)} chars)\n")

# 1. Show <head> meta tags
head = re.search(r'<head>(.*?)</head>', html, re.DOTALL | re.IGNORECASE)
if head:
    print("── <head> tags ──────────────────────────────")
    for line in head.group(1).splitlines():
        line = line.strip()
        if line and any(x in line.lower() for x in ['<title','<meta','<link','<canonical']):
            print(" ", line[:120])

# 2. Show all H1 tags
print("\n── H1 tags ──────────────────────────────────")
for m in re.finditer(r'<h1[^>]*>.*?</h1>', html, re.DOTALL | re.IGNORECASE):
    print(" ", m.group()[:200].replace('\n',' '))

# 3. Show footer area (last 2000 chars)
print("\n── Footer area (last 1500 chars) ────────────")
footer_html = html[-1500:].replace('\n',' ')
# Collapse whitespace
footer_html = re.sub(r'\s+', ' ', footer_html)
print(" ", footer_html[:800])
print(" ", footer_html[800:])

# 4. Show categ link runs
print("\n── /categ/ link occurrences ─────────────────")
categ_links = re.findall(r'<a[^>]+/categ/[^>]+>[^<]*</a>', html, re.IGNORECASE)
print(f"  Total /categ/ links found: {len(categ_links)}")
print(f"  (Expected ~34 = 17 in nav + 17 in footer)")

print("\n✅ Debug complete. Share this output if the fix script didn't work.\n")
