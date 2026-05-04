#!/usr/bin/env python3
"""
fix_remaining.py  —  Unblocked Games USA  —  run from repo root
Fixes:
  1. Game page h1 — remove "Unblocked" from visible heading
  2. Game page subtitle paragraph — rewrite generic keyword-stuffed text
  3. Game iframe — cap height so page content stays visible (max 520px, aspect-ratio kept)
  4. Category footer — remove the repeated category pill links inside <footer>
  5. Category page — collapse the empty whitespace between last card row and footer
"""

import os, re, json
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

REPO_ROOT = Path(".")
DRY_RUN   = False   # set True to preview only

# ── helpers ──────────────────────────────────────────────────────────────────

def slug_to_title(slug: str) -> str:
    stop = {"a","an","the","of","and","or","in","on","at","vs","for"}
    words = slug.replace("-", " ").split()
    return " ".join(
        w if (i > 0 and w in stop) else w.capitalize()
        for i, w in enumerate(words)
    )

def rel(path): return path.relative_to(REPO_ROOT)

def page_type(path: Path):
    parts = path.relative_to(REPO_ROOT).parts
    if parts == ("index.html",):
        return "home"
    if parts[0] == "categ":
        return "categ"
    skip = {"privacy-policy","contact","faq","dmca","about"}
    if len(parts) == 2 and parts[1] == "index.html" and parts[0] not in skip:
        return "game"
    return "other"

# ── creative descriptions per genre ──────────────────────────────────────────
GENRE_DESC = {
    "action":     "{name} drops you straight into the action — fast reflexes, zero loading screens.",
    "shooter":    "Lock, aim, fire. {name} is a shooter that runs in your browser with zero install.",
    "platformer": "Jump, dodge, survive. {name} is a platformer built for quick sessions anywhere.",
    "puzzle":     "{name} bends your brain in the best way — free, instant, no sign-up.",
    "racing":     "Floor it. {name} puts you behind the wheel with no download required.",
    "driving":    "Get behind the wheel — {name} is a driving game you can play right now, no install.",
    "strategy":   "Think three moves ahead. {name} rewards patience and planning.",
    "adventure":  "A new world awaits. {name} is an adventure you can start in seconds.",
    "sports":     "{name} brings the competition to your browser — free, fast, no download.",
    "multiplayer":"{name} lets you face real opponents instantly — no account, no download.",
    "2-player":   "Grab a friend. {name} is a 2-player game you can play on one keyboard right now.",
    "fighting":   "Step into the ring. {name} is a fighting game that launches instantly in your browser.",
    "simulation": "Run the show. {name} is a simulation game you can dive into without any install.",
    "skill":      "Test your precision. {name} rewards practice and sharp timing — free in your browser.",
    "clicker":    "Satisfying, addictive, unstoppable. {name} keeps your fingers busy.",
    "horror":     "Enter if you dare. {name} is a horror game that runs right in your browser.",
    "kids":       "Safe, fun, and instantly playable — {name} is perfect for a quick break.",
    "adventure":  "Explore without limits. {name} is an adventure game that starts in one click.",
}
DEFAULT_DESC = "{name} is a free browser game — no download, no sign-up. Play instantly anywhere."

def make_description(game_name: str, genres: list) -> str:
    for g in genres:
        slug = g.lower().strip()
        if slug in GENRE_DESC:
            return GENRE_DESC[slug].format(name=game_name)
    return DEFAULT_DESC.format(name=game_name)

# ── iframe CSS fix (injected once per game page) ─────────────────────────────
IFRAME_CSS = """
/* ── Compact iframe: max 520px, scrolls content below ── */
.game-frame-wrap{
  aspect-ratio:16/9;
  max-height:520px;
  width:100%;
  border-radius:12px;
  overflow:hidden;
  border:2px solid rgba(192,57,43,.3);
  margin-bottom:16px;
  position:relative;
  background:#000;
}
@media(max-width:768px){
  .game-frame-wrap{ max-height:56vw; }
}
"""

# ── per-file fixes ────────────────────────────────────────────────────────────

def fix_game_page(soup: BeautifulSoup, path: Path):
    slug      = path.parts[-2]
    game_name = slug_to_title(slug)

    # 1. h1 — strip "Unblocked" from visible heading
    h1 = soup.find("h1")
    if h1:
        raw = h1.get_text()
        cleaned = re.sub(r'\s*[Uu]nblocked\s*$', '', raw).strip()
        # keep gradient styling; just replace the text node
        for child in list(h1.children):
            if isinstance(child, NavigableString):
                child.replace_with(cleaned)
                break
        else:
            h1.string = cleaned

    # 2. Subtitle paragraph under h1 — rewrite if it's the generic staffed text
    title_bar = soup.find(class_="game-title-bar")
    if title_bar:
        p = title_bar.find("p")
        if p:
            old = p.get_text()
            # detect keyword-stuffed pattern
            if any(kw in old.lower() for kw in ["unblocked", "no download", "sign-up", "school"]):
                genres = [a.get_text(strip=True) for a in soup.find_all("a", class_="cat-tag")]
                # strip emoji from genre names
                genre_slugs = [re.sub(r'[^\w\s\-]','',g).strip().lower() for g in genres]
                p.string = make_description(game_name, genre_slugs)

    # 3. meta description — rewrite if still stuffed
    meta_desc = soup.find("meta", attrs={"name":"description"})
    if meta_desc:
        old = meta_desc.get("content","")
        if "unblocked" in old.lower() or "no download, no sign-up" in old.lower():
            genres = [a.get_text(strip=True) for a in soup.find_all("a", class_="cat-tag")]
            genre_slugs = [re.sub(r'[^\w\s\-]','',g).strip().lower() for g in genres]
            new_desc = make_description(game_name, genre_slugs)
            meta_desc["content"] = new_desc
            for og in soup.find_all("meta", property=re.compile(r"og:description|twitter:description")):
                og["content"] = new_desc

    # 4. <title> — fix if still has "Unblocked |"
    title_tag = soup.find("title")
    if title_tag and "unblocked" in (title_tag.string or "").lower():
        title_tag.string = f"Play {game_name} Online Free | Unblocked Games USA"

    # 5. schema name — strip Unblocked
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if "name" in data and "unblocked" in data["name"].lower():
                data["name"] = re.sub(r'\s*[Uu]nblocked\s*$','', data["name"]).strip()
                script.string = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # 6. Inject compact iframe CSS (once, before </head>)
    head = soup.find("head")
    if head and IFRAME_CSS.strip() not in str(head):
        style = soup.new_tag("style")
        style.string = IFRAME_CSS
        head.append(style)


def fix_categ_page(soup: BeautifulSoup, path: Path):
    # Remove footer-cats inside <footer> (duplicate nav links)
    footer = soup.find("footer")
    if footer:
        for div in footer.find_all("div", class_="footer-cats"):
            div.decompose()

    # Remove stray empty whitespace paragraphs before pagination
    # (some pages have <p>&nbsp;</p> or empty divs adding gap)
    for tag in soup.find_all(["p","div"]):
        text = tag.get_text(strip=True)
        if text in ("", "\xa0") and not tag.find(True):  # no child elements
            tag.decompose()


def fix_home_page(soup: BeautifulSoup, path: Path):
    # Remove footer-cats (also redundant on home — nav is sticky)
    footer = soup.find("footer")
    if footer:
        for div in footer.find_all("div", class_="footer-cats"):
            div.decompose()


# ── main loop ─────────────────────────────────────────────────────────────────

def process(path: Path) -> bool:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  SKIP (read error): {rel(path)} — {e}")
        return False

    soup = BeautifulSoup(html, "html.parser")
    original = str(soup)

    ptype = page_type(path)
    if ptype == "game":
        fix_game_page(soup, path)
    elif ptype == "categ":
        fix_categ_page(soup, path)
    elif ptype == "home":
        fix_home_page(soup, path)

    new_html = str(soup)
    if new_html == original:
        return False

    if not DRY_RUN:
        path.write_text(new_html, encoding="utf-8")
    return True


def main():
    skip_dirs = {".git","node_modules",".github"}
    files = [p for p in REPO_ROOT.rglob("*.html")
             if not (set(p.parts) & skip_dirs)]
    print(f"Scanning {len(files)} HTML files…\n")

    stats = {"game":0,"categ":0,"home":0,"changed":0,"errors":0}
    for f in sorted(files):
        ptype = page_type(f)
        if ptype in stats:
            stats[ptype] += 1
        try:
            if process(f):
                stats["changed"] += 1
                print(f"  ✓  [{ptype:6}]  {rel(f)}")
        except Exception as e:
            stats["errors"] += 1
            print(f"  ✗  ERROR  {rel(f)}: {e}")

    print(f"""
{'[DRY RUN] ' if DRY_RUN else ''}Complete.
  Game pages    : {stats['game']}
  Category pages: {stats['categ']}
  Home pages    : {stats['home']}
  Files changed : {stats['changed']}
  Errors        : {stats['errors']}
""")

if __name__ == "__main__":
    main()
