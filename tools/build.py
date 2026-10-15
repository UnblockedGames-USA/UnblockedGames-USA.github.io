#!/usr/bin/env python3
"""Static site generator for Unblocked Games USA.

Run from the repo root:   python3 tools/build.py
Reads data/games.json and writes:
  game/<slug>/index.html      one crawlable page per game
  category/<cat>/index.html   one hub page per category
  games/index.html            A-Z index of every game
  sitemap.xml, game.html (redirect for old ?id= links)
Optional per-game fields in data/games.json (they override the generic copy):
  description, howToPlay (list), controls (string), tips (list), features (list), faq ([[q,a],...])
"""
import json, re, os, html, hashlib, datetime, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import CATEGORIES, DEFAULT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://unblockedgames-usa.github.io"
BRAND = "Unblocked Games USA"
GA, ADS = "G-L6FNHSMWF4", "ca-pub-4672956141931257"
TODAY = datetime.date.today().isoformat()
esc = html.escape

def slugify(i): return re.sub(r"-+", "-", i).strip("-")
def h(s): return int(hashlib.md5(s.encode()).hexdigest(), 16)
def pick(seq, key, n):
    seq = list(seq); start = h(key) % len(seq); return [seq[(start + k) % len(seq)] for k in range(min(n, len(seq)))]
def cat(c): return CATEGORIES.get(c, {**DEFAULT, "label": c.title(), "h1": f"Free {c.title()} Games"})
def an(w): return "an" if w[:1].lower() in "aeiou" else "a"
def trunc(s, n):
    if len(s) <= n: return s
    return s[:n-1].rsplit(" ", 1)[0].rstrip(",;:.- ") + "…"
def abs_url(p): return p if p.startswith("http") else SITE + "/" + p.lstrip("/")
def write(path, text):
    full = os.path.join(ROOT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)

games = json.load(open(os.path.join(ROOT, "data/games.json"), encoding="utf-8"))
for g in games:
    g["slug"] = slugify(g["id"]); g["title"] = g["title"].strip() or g["id"].replace("-", " ").title()
    g["cats"] = g.get("categories") or ["casual"]; g["primary"] = g["cats"][0]
assert len({g["slug"] for g in games}) == len(games), "slug collision"
by_cat = {}
for g in games:
    for c in g["cats"]: by_cat.setdefault(c, []).append(g)
cat_order = sorted(by_cat, key=lambda c: -len(by_cat[c]))

# ---------- shared fragments ----------
ICON = {
 "home": '<path d="M3 10.5 12 3l9 7.5V21h-6v-6h-6v6H3z"/>',
 "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
 "tag": '<path d="M20 12 12 20 4 12V4h8z"/><circle cx="8.5" cy="8.5" r="1.2"/>',
 "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 8h.01"/>',
}
def svg(k): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>'

def head(title, desc, canonical, og_image=None, og_type="website", ld=(), robots="index, follow, max-image-preview:large"):
    og_image = og_image or f"{SITE}/images/basketball-superstars.jpg"
    lds = "\n".join(f'  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>' for x in ld)
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc, quote=True)}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="robots" content="{robots}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="{BRAND}" />
  <meta property="og:title" content="{esc(title, quote=True)}" />
  <meta property="og:description" content="{esc(desc, quote=True)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{og_image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title, quote=True)}" />
  <meta name="twitter:description" content="{esc(desc, quote=True)}" />
  <meta name="twitter:image" content="{og_image}" />
{lds}
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA}');</script>
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wdth,wght@75..125,400..700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/base.css" />
  <link rel="stylesheet" href="/assets/style.css" />
  <link rel="stylesheet" href="/assets/seo.css?v=2" />
  <link rel="stylesheet" href="/assets/fun.css?v=2" />
</head>
'''

EMOJI = {'action':'⚡','arcade':'🕹️','puzzle':'🧩','simulation':'🏗️','clicker':'👆','driving':'🏎️','adventure':'🗺️','casual':'🌈','shooting':'🎯','sports':'⚽','beauty':'💄','strategy':'♟️','word':'🔤','skill':'🏅','board':'🎲'}
def cat_bar(active=None):
    pills = ''.join(f'<a class="cat-pill{" is-active" if c == active else ""}" href="/category/{c}/"><span aria-hidden="true">{EMOJI.get(c, "🎮")}</span>{esc(cat(c)["label"])}</a>' for c in cat_order if len(by_cat[c]) > 1)
    return f'<nav class="cat-bar" aria-label="Game categories"><div class="container cat-bar-inner"><a class="cat-pill{" is-active" if active == "home" else ""}" href="/"><span aria-hidden="true">🏠</span>Home</a>{pills}<a class="cat-pill" href="/games/"><span aria-hidden="true">🔤</span>A–Z</a></div></nav>'

def header_nav(active=None):
    items = [f'<li><a href="/">{svg("home")}Home</a></li>', f'<li><a href="/games/">{svg("grid")}All games A–Z</a></li>']
    items += [f'<li><a href="/category/{c}/">{svg("tag")}{esc(cat(c)["label"])}</a></li>' for c in cat_order if len(by_cat[c]) > 1]
    items += [f'<li><a href="/about%20us.html">{svg("info")}About us</a></li>', f'<li><a href="/dmca.html">{svg("info")}DMCA</a></li>',
              f'<li><a href="/privacy-policy.html">{svg("info")}Privacy policy</a></li>', f'<li><a href="/terms.html">{svg("info")}Terms of use</a></li>']
    return f'''<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/" aria-label="{BRAND} — home">
        <svg class="brand-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true"><rect x="2" y="2" width="28" height="28" rx="7" stroke="currentColor" stroke-width="2.5"/><path d="M12 10.5v11l9-5.5-9-5.5z" fill="currentColor"/><rect x="20.5" y="21" width="3" height="3" fill="currentColor"/><rect x="24.5" y="21" width="3" height="3" fill="currentColor" opacity=".45"/></svg>
        <span class="brand-name">Unblocked<span class="brand-accent">Games</span></span>
      </a>
      <form class="header-search" action="/" method="get" role="search">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>
        <input name="q" type="search" placeholder="Search {len(games)} games…" aria-label="Search games" autocomplete="off" />
      </form>
      <button class="icon-btn" data-theme-toggle aria-label="Switch to light mode" type="button"></button>
      <button class="icon-btn menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" type="button"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
    {cat_bar(active)}
  </header>
  <div class="menu-backdrop" id="menuBackdrop" hidden></div>
  <nav class="menu-panel" id="menuPanel" aria-label="Site menu" hidden>
    <div class="menu-head"><span class="menu-title">Menu</span><button class="icon-btn" id="menuClose" aria-label="Close menu" type="button"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>
    <ul class="menu-list">
      {chr(10).join("      " + i for i in items).strip()}
    </ul>
  </nav>
'''

def footer():
    cats = " ".join(f'<a href="/category/{c}/">{esc(cat(c)["label"])}</a>' for c in cat_order if len(by_cat[c]) > 1)
    return f'''  <footer class="site-footer">
    <div class="container footer-inner">
      <nav class="footer-cats" aria-label="Game categories"><strong>Categories:</strong> {cats} <a href="/games/">All games A–Z</a></nav>
      <p>{BRAND} — free browser games, always.</p>
      <nav class="footer-legal" aria-label="Legal">
        <a href="/about%20us.html">About</a><a href="/dmca.html">DMCA</a><a href="/privacy-policy.html">Privacy Policy</a><a href="/terms.html">Terms of Use</a>
      </nav>
    </div>
  </footer>
  <script src="/assets/js/page.js?v=2" defer></script>
</body>
</html>
'''

def ad():
    return f'''<div class="ad-unit" aria-label="Advertisement"><ins class="adsbygoogle" style="display:block" data-ad-client="{ADS}" data-ad-slot="4436716876" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script></div>'''

def breadcrumb(trail):
    lis = "".join(f'<li><a href="{u}">{esc(n)}</a></li>' for n, u in trail[:-1]) + f'<li aria-current="page">{esc(trail[-1][0])}</li>'
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(trail)]}
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{lis}</ol></nav>', ld

def card(g):
    labels = ", ".join(cat(c)["label"] for c in g["cats"][:2])
    return (f'<li><a class="game-card" href="/game/{g["slug"]}/" aria-label="Play {esc(g["title"], quote=True)}">'
            f'<img class="card-thumb" src="/{g["image"]}" alt="{esc(g["title"], quote=True)} — game thumbnail" loading="lazy" decoding="async" width="300" height="200" />'
            f'<div class="card-body"><span class="card-title">{esc(g["title"])}</span><span class="card-cat">{esc(labels)}</span></div></a></li>')

def tile(g, big=False):
    return (f'<li class="{"tile-big" if big else ""}"><a class="tile" href="/game/{g["slug"]}/" aria-label="Play {esc(g["title"], quote=True)}">'
            f'<img src="/{g["image"]}" alt="{esc(g["title"], quote=True)} – play free online" loading="lazy" decoding="async" width="480" height="270" />'
            f'<span class="tile-title">{esc(g["title"])}</span></a></li>')

def grid(items, cls="tile-grid"): return f'<ul class="{cls}">' + "".join(tile(g) for g in items) + "</ul>"

# ---------- game pages ----------
def related_for(g, n=12):
    pool = by_cat[g["primary"]]
    i = next(k for k, x in enumerate(pool) if x["id"] == g["id"])
    rel = [pool[(i + k) % len(pool)] for k in range(1, len(pool)) ][:n]
    if len(g["cats"]) > 1 and len(rel) >= 8:
        extra = [x for x in by_cat[g["cats"][1]] if x["id"] != g["id"] and x not in rel]
        rel = rel[:n - 4] + extra[:4] if len(extra) >= 4 else rel
    return rel[:n]

def game_page(g):
    t, slug, c0 = g["title"], g["slug"], cat(g["primary"]); url = f"{SITE}/game/{slug}/"
    genre = c0["label"]; low = genre.lower()
    seo_title = f"{t} – Play Free {genre} Game Online | {BRAND}"
    if len(seo_title) > 66: seo_title = f"{t} – Play Free Online | {BRAND}"
    if len(seo_title) > 66: seo_title = trunc(f"{t} – Play Free Online", 66)
    desc = g.get("metaDescription") or trunc(g.get("description") or f"Play {t} free online in your browser. No download, no sign-up. {an(low).capitalize()} {low} game on {BRAND}: instant play on desktop, tablet and mobile.", 158)
    img = abs_url(g["image"])
    intro_variants = [
      f"Play {t} online for free. It is {an(low)} {low} game that runs right in your browser, so there is nothing to download or install and no account to create. Press Play Now and you can start within a few seconds.",
      f"{t} is {an(low)} free {low} game you can play instantly in your browser. It works on desktop, tablet and phone, with no download and no registration, so you can jump in whenever you have a few minutes.",
      f"Ready to play {t}? This free {low} game loads in your browser in seconds. There is no installation, no sign-up and no cost, just press Play Now to start.",
      f"Looking for a quick {low} game? {t} is free to play online, works on any modern browser and needs no download, so you can try it right now.",
    ]
    about = g.get("description") or pick(intro_variants, slug, 1)[0]
    steps = g.get("howToPlay") or c0["steps"]
    controls_d = g.get("controls") or c0["controls_desktop"]
    controls_m = c0["controls_mobile"]
    tips = g.get("tips") or pick(c0["tips"], slug + "t", 5)
    feats = g.get("features") or c0["features"]
    faqs = g.get("faq") or [
      [f"Is {t} free to play?", f"Yes. {t} is free to play on {BRAND}. There is no registration, no download and no payment needed to play."],
      [f"Can I play {t} on mobile?", f"Yes. {t} runs in your browser, so it works on modern desktop, tablet and mobile browsers. Some controls may feel better with a keyboard and mouse, and landscape mode gives more room on a phone."],
      [f"How do I start playing {t}?", f"Click the Play Now button on this page. The game loads inside the page and you can begin as soon as it finishes loading. Use the Expand button for a larger play area."],
      [f"{t} will not load. What should I do?", "Refresh the page, check your internet connection and make sure you are using an up-to-date browser. Some school or work networks block game content, and in that case the game may not load on that network."],
      list(c0["faq"]),
    ]
    crumb_html, crumb_ld = breadcrumb([("Home", "/"), (f"{genre} Games", f"/category/{g['primary']}/"), (t, f"/game/{slug}/")])
    ld = [
      {"@context": "https://schema.org", "@type": "VideoGame", "name": t, "url": url, "image": img, "description": desc,
       "genre": [cat(c)["label"] for c in g["cats"]], "applicationCategory": "Game", "operatingSystem": "Any (web browser)",
       "playMode": "SinglePlayer", "gamePlatform": "Web browser", "inLanguage": "en", "isAccessibleForFree": True,
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "availability": "https://schema.org/InStock"},
       "publisher": {"@type": "Organization", "name": BRAND, "url": SITE + "/"}},
      crumb_ld,
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
    ]
    embed = g["embedUrl"] if g["embedUrl"].startswith("http") else "/" + g["embedUrl"].lstrip("/")
    chips = "".join(f'<a class="chip" href="/category/{c}/">{esc(cat(c)["label"])}</a>' for c in g["cats"])
    rel = related_for(g)
    more = [x for x in by_cat[g["primary"]] if x["id"] != g["id"]]
    side_pool = [x for x in by_cat[g["primary"]] if x["id"] != g["id"] and x not in rel]
    side = (side_pool + rel)[:10]
    body = f'''  <main id="main" class="container container--wide game-page">
    {crumb_html}
    <div class="play-layout">
      <div class="play-main">
        <div class="game-head">
          <h1>{esc(t)}</h1>
          <div class="game-meta">{chips}</div>
        </div>

        <section class="player" id="player" aria-label="Play {esc(t, quote=True)}">
          <div class="player-frame" id="playerFrame" data-embed="{esc(embed, quote=True)}" data-title="{esc(t, quote=True)}">
            <button class="play-poster" id="playBtn" type="button" aria-label="Play {esc(t, quote=True)} now">
              <img src="/{g['image']}" alt="Play {esc(t, quote=True)} online free — {low} game" width="640" height="360" fetchpriority="high" decoding="async" />
              <span class="play-cta"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>Play Now</span>
            </button>
            <noscript><p class="noscript-note">Please enable JavaScript to play {esc(t)}.</p></noscript>
          </div>
          <div class="player-bar">
            <p class="player-hint">Click the game once to focus it. If the keyboard stops responding, click the game area again.</p>
            <div class="player-actions">
              <button class="btn btn-ghost" id="reloadBtn" type="button">Restart</button>
              <button class="btn btn-primary" id="fullscreenBtn" type="button" aria-expanded="false">Expand</button>
            </div>
          </div>
        </section>

        <article class="game-content">
          <section class="panel" aria-labelledby="about"><h2 id="about">About {esc(t)}</h2><p>{esc(about)}</p>
            <p>It is part of our collection of {len(by_cat[g["primary"]])} free <a href="/category/{g["primary"]}/">{esc(low)} games</a>, inside a library of {len(games)} browser games you can play without installing anything.</p></section>
          <section class="panel" aria-labelledby="howto"><h2 id="howto">How to Play {esc(t)}</h2>
            <ol class="steps">{"".join(f"<li>{esc(s)}</li>" for s in steps)}</ol></section>
          <section class="panel" aria-labelledby="controls"><h2 id="controls">Controls</h2>
            <dl class="controls"><div><dt>Desktop</dt><dd>{esc(controls_d)}</dd></div><div><dt>Mobile and tablet</dt><dd>{esc(controls_m)}</dd></div></dl>
            <p class="note">Controls can differ between games. Check the start screen or tutorial of {esc(t)} for the exact keys.</p></section>
          <section class="panel" aria-labelledby="tips"><h2 id="tips">Tips and Tricks for {esc(t)}</h2>
            <ul class="ticks">{"".join(f"<li>{esc(s)}</li>" for s in tips)}</ul></section>
          <section class="panel" aria-labelledby="features"><h2 id="features">Features</h2>
            <ul class="ticks">{"".join(f"<li>{esc(s)}</li>" for s in feats)}</ul></section>
          <section class="panel" aria-labelledby="faq"><h2 id="faq">Frequently Asked Questions</h2>
            {"".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)}</section>
        </article>
      </div>

      <aside class="play-side" aria-label="Game details and more games">
        <section class="side-card">
          <h2>Game info</h2>
          <dl class="info">
            <div><dt>Title</dt><dd>{esc(t)}</dd></div>
            <div><dt>Genre</dt><dd>{" · ".join(f'<a href="/category/{c}/">{esc(cat(c)["label"])}</a>' for c in g["cats"])}</dd></div>
            <div><dt>Platform</dt><dd>Browser (desktop, mobile, tablet)</dd></div>
            <div><dt>Technology</dt><dd>HTML5</dd></div>
            <div><dt>Price</dt><dd>Free, no download</dd></div>
          </dl>
        </section>
        {ad()}
        <section class="side-card">
          <h2>More {esc(low)} games</h2>
          {grid(side, "tile-grid tile-grid--side")}
          <p class="see-all"><a class="btn btn-primary" href="/category/{g["primary"]}/">All {len(by_cat[g["primary"]])} {esc(low)} games</a></p>
        </section>
      </aside>
    </div>

    <section class="shelf" aria-labelledby="relatedTitle">
      <div class="shelf-head"><h2 id="relatedTitle">You may also like</h2><a class="shelf-link" href="/category/{g["primary"]}/">See all</a></div>
      {grid(rel)}
    </section>
  </main>
'''
    return head(seo_title, desc, url, og_image=img, ld=ld) + header_nav(g['primary']) + body + footer()

# ---------- category pages ----------
def category_page(c):
    info, items = cat(c), by_cat[c]; label = info["label"]; url = f"{SITE}/category/{c}/"
    title = f"Free {label} Games – Play {len(items)} Online | {BRAND}"
    if len(title) > 66: title = f"Free {label} Games – Play Online | {BRAND}"
    desc = trunc(f"Play {len(items)} free {label.lower()} games online. No downloads, no sign-up. {info['intro']}", 158)
    crumb_html, crumb_ld = breadcrumb([("Home", "/"), (f"{label} Games", f"/category/{c}/")])
    ld = [crumb_ld, {"@context": "https://schema.org", "@type": "CollectionPage", "name": info["h1"], "url": url, "description": desc,
          "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE + "/"}},
          {"@context": "https://schema.org", "@type": "ItemList", "numberOfItems": len(items), "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/game/{g['slug']}/", "name": g["title"]} for i, g in enumerate(items[:100])]}]
    others = "".join(f'<a class="chip" href="/category/{o}/">{esc(cat(o)["label"])} ({len(by_cat[o])})</a>' for o in cat_order if o != c and len(by_cat[o]) > 1)
    body = f'''  <main id="main" class="container container--wide game-page">
    {crumb_html}
    <header class="cat-head panel"><h1><span aria-hidden="true">{EMOJI.get(c, "🎮")}</span> {esc(info["h1"])}</h1><p class="lead">{esc(info["intro"])}</p>
      <p class="lead">{len(items)} {esc(label.lower())} games, all free, all in your browser, on desktop, tablet and mobile.</p></header>
    {grid(items)}
    {ad()}
  </main>
'''
    return head(title, desc, url, og_image=abs_url(items[0]["image"]), ld=ld) + header_nav(c) + body + footer()

def index_page():
    url = f"{SITE}/games/"; crumb_html, crumb_ld = breadcrumb([("Home", "/"), ("All Games A–Z", "/games/")])
    letters = {}
    for g in sorted(games, key=lambda x: x["title"].lower()):
        k = g["title"][:1].upper(); k = k if k.isalpha() else "#"; letters.setdefault(k, []).append(g)
    nav = " ".join(f'<a class="chip" href="#l-{k if k != "#" else "num"}">{k}</a>' for k in sorted(letters, key=lambda k: ("~" if k == "#" else k)))
    secs = "".join(f'<section aria-labelledby="l-{k if k != "#" else "num"}"><h2 id="l-{k if k != "#" else "num"}">{k}</h2><ul class="az-list">' +
                   "".join(f'<li><a href="/game/{g["slug"]}/">{esc(g["title"])}</a> <span>{esc(cat(g["primary"])["label"])}</span></li>' for g in v) + "</ul></section>"
                   for k, v in sorted(letters.items(), key=lambda kv: ("~" if kv[0] == "#" else kv[0])))
    cats = "".join(f'<a class="chip" href="/category/{o}/">{esc(cat(o)["label"])} ({len(by_cat[o])})</a>' for o in cat_order if len(by_cat[o]) > 1)
    body = f'''  <main id="main" class="container container--wide game-page">
    {crumb_html}
    <header class="cat-head panel"><h1>All Free Browser Games A–Z</h1><p class="lead">Every one of our {len(games)} free games in alphabetical order. Pick a letter or jump to a category.</p></header>
    <nav class="chips cat-chips" aria-label="Categories">{cats}</nav>
    <nav class="chips cat-chips" aria-label="Letters">{nav}</nav>
    {secs}
  </main>
'''
    return head(f"All Free Browser Games A–Z ({len(games)} Games) | {BRAND}", f"Browse all {len(games)} free browser games from A to Z. Action, arcade, puzzle, driving, simulation and more. No downloads, no sign-up.", url, ld=[crumb_ld]) + header_nav() + body + footer()

# ---------- HOME ----------

def home_page():
    url = SITE + "/"
    # featured mosaic: round-robin over categories, 2 big + 16 small = 24 cells
    featured_ids = ["basketball-superstars", "crazy-drift", "snake-clash-io", "tape-escape"]
    feat = [next(x for x in games if x["id"] == i) for i in featured_ids if any(x["id"] == i for x in games)]
    seen = {x["id"] for x in feat}
    for round_ in range(6):
        for c in cat_order[:10]:
            pool = [x for x in by_cat[c] if x["id"] not in seen]
            if pool and len(feat) < 18:
                feat.append(pool[round_ * 3 % len(pool)]); seen.add(feat[-1]["id"])
    feat = feat[:18]
    mosaic = '<ul class="tile-grid tile-grid--mosaic">' + "".join(tile(x, big=i in (0, 7)) for i, x in enumerate(feat)) + "</ul>"
    shelves = ""
    for c in cat_order[:8]:
        items = [x for x in by_cat[c] if x["id"] not in seen][:12]
        info = cat(c)
        shelves += f'<section class="shelf" aria-labelledby="s-{c}"><div class="shelf-head"><h2 id="s-{c}"><span aria-hidden="true">{EMOJI.get(c,"🎮")}</span> {esc(info["label"])} Games</h2><a class="shelf-link" href="/category/{c}/">See all {len(by_cat[c])} ›</a></div>{grid(items, "tile-grid tile-grid--shelf")}</section>'
        if c == cat_order[1]: shelves += ad()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/",
           "potentialAction": {"@type": "SearchAction", "target": SITE + "/?q={search_term_string}", "query-input": "required name=search_term_string"}},
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Featured games", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/game/{x['slug']}/", "name": x["title"]} for i, x in enumerate(feat)]}]
    cats_links = ", ".join(f'<a href="/category/{c}/">{esc(cat(c)["label"].lower())} games</a>' for c in cat_order[:6])
    body = f"""  <main id="main" class="container container--wide home">
    <section class="home-intro" aria-label="Welcome">
      <h1>Play {len(games)} free online games</h1>
      <p>No downloads, no sign-ups. Pick a game and play right here in your browser, on your computer, tablet or phone.</p>
    </section>
    <section id="searchResults" class="shelf" aria-labelledby="searchTitle" aria-live="polite" hidden>
      <div class="shelf-head"><h2 id="searchTitle">Search results</h2><a class="shelf-link" href="/">Clear search</a></div>
      <ul class="tile-grid" id="searchGrid"></ul>
      <p class="lead" id="searchEmpty" hidden>No games match that search. Try a shorter word, or browse a category above.</p>
    </section>
    <div id="shelves">
      <section class="shelf" aria-labelledby="featTitle"><div class="shelf-head"><h2 id="featTitle">⭐ Featured games</h2><a class="shelf-link" href="/games/">All games A–Z ›</a></div>{mosaic}</section>
      {shelves}
      <section class="panel home-about" aria-labelledby="aboutTitle">
        <h2 id="aboutTitle">Free online games that run in your browser</h2>
        <p>Unblocked Games USA is a library of {len(games)} free browser games. Every game has its own page with a short guide, controls, tips and answers to common questions, so you know what to expect before you press play.</p>
        <p>Looking for something to try? Start with {cats_links}, or open the <a href="/games/">A–Z list</a> of every game. There are no downloads or installs, and games run on desktop, tablet and phone browsers, though availability can depend on your network.</p>
      </section>
    </div>
  </main>
"""
    return head(f"{BRAND} — Play {len(games)} Free Browser Games, No Downloads",
                f"Play {len(games)} free browser games instantly. No downloads, no sign-ups. Action, racing, puzzle, arcade, sports and more — works right in your browser.",
                url, og_image=f"{SITE}/images/basketball-superstars.jpg", ld=ld) + header_nav("home") + body + footer()

# ---------- build ----------
for d in ("game", "category", "games"):
    shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
for g in games: write(f"game/{g['slug']}/index.html", game_page(g))
for c in cat_order: write(f"category/{c}/index.html", category_page(c))
write("games/index.html", index_page())
write("index.html", home_page())

# old ?id= links -> new URLs (GitHub Pages cannot 301)
write("game.html", f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta name="robots" content="noindex" /><title>Redirecting… | {BRAND}</title>
<script>(function(){{var id=new URLSearchParams(location.search).get('id')||'';var s=id.replace(/-+/g,'-').replace(/^-|-$/g,'');location.replace(s?'/game/'+encodeURIComponent(s)+'/':'/');}})();</script>
<noscript><meta http-equiv="refresh" content="0; url=/" /></noscript></head><body><p>Redirecting to <a href="/">{BRAND}</a>…</p></body></html>
''')

urls = [(SITE + "/", "1.0", "daily"), (SITE + "/games/", "0.8", "weekly")]
urls += [(f"{SITE}/category/{c}/", "0.8", "weekly") for c in cat_order]
urls += [(f"{SITE}/game/{g['slug']}/", "0.7", "monthly") for g in games]
urls += [(f"{SITE}/{p}", "0.3", "yearly") for p in ("about%20us.html", "dmca.html", "privacy-policy.html", "terms.html")]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>\n" for u, p, f in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /game.html\n\nSitemap: {SITE}/sitemap.xml\n")
print(f"built {len(games)} game pages, {len(cat_order)} category pages, {len(urls)} sitemap URLs")
