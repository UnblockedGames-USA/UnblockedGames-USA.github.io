#!/usr/bin/env python3
"""Static site generator for Unblocked Games USA.

Run from the repo root:   python3 tools/build.py
Reads data/games.json and writes:
  game/<slug>/index.html      one crawlable page per game
  category/<cat>/index.html   one hub page per category
  games/index.html            A-Z index of every game
  sitemap.xml, game.html (redirect for old ?id= links)
Optional per-game fields in data/games.json (they override the generic copy):
  frame ("tall" = portrait-friendly player for word/puzzle games), poster (square image shown before Play),
  description, howToPlay (list), controls (string), tips (list), features (list), faq ([[q,a],...]),
  seoTitle (title tag override), h1 (visible heading override), alt (poster alt text),
  sections ([{id, h2, html}, ...] extra content panels shown before the FAQ)
Also writes /games-like-wordle/ (hub page listing the site's word games).
"""
import json, re, os, html, hashlib, datetime, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import CATEGORIES, DEFAULT
from icons import ic

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://unblockedgames-usa.github.io"
BRAND = "Unblocked Games USA"
GA, ADS = "G-L6FNHSMWF4", "ca-pub-4672956141931257"
TODAY = datetime.date.today().isoformat()
esc = html.escape

PATH_OVERRIDE = {"word-guess": "/wordle-unlimited/"}  # games served at a custom URL
def gpath(slug): return PATH_OVERRIDE.get(slug, f"/game/{slug}/")
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
# Markup and CSS classes follow /classroom6x/ so both sites share one look (assets/site.css is the shared base).
def head(title, desc, canonical, og_image=None, og_type="website", ld=(), robots="index, follow, max-image-preview:large"):
    og_image = og_image or f"{SITE}/images/basketball-superstars.jpg"
    lds = "\n".join(f'  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>' for x in ld)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc, quote=True)}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="robots" content="{robots}" />
  <meta name="theme-color" content="#1d6b52" />
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
  <link rel="preconnect" href="https://api.fontshare.com" />
  <link href="https://api.fontshare.com/v2/css?f[]=chillax@500,600,700&f[]=general-sans@400,500,600,700&display=swap" rel="stylesheet" />
  <script>(function(){{try{{var t=localStorage.getItem('c6x-theme');if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.dataset.theme=t}}catch(e){{}}}})()</script>
  <link rel="stylesheet" href="/assets/site.css?v=1" />
  <link rel="stylesheet" href="/assets/site-extra.css?v=1" />
</head>
'''

LOGO = f'<a class="logo" href="/" aria-label="{BRAND} home"><span class="logo-word">Unblocked</span><span class="logo-badge">Games</span></a>'

def side_link(href, label, icon, current=False):
    return f'<a class="side-link" href="{href}"{" aria-current=\"page\"" if current else ""}>{ic(icon)}<span>{label}</span></a>'

def header_nav(active=None):
    """Top bar + sidebar (becomes a drawer on phones). `active` is a category id, 'home', 'az' or 'hub'."""
    cats = "".join(side_link(f"/category/{c}/", esc(cat(c)["label"]), c, active == c) for c in cat_order if len(by_cat[c]) > 1)
    return f'''<body data-root="/">
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <button class="icon-btn menu-btn" id="menuBtn" aria-label="Open categories" aria-controls="sidebar" aria-expanded="false" type="button">{ic("menu")}</button>
  {LOGO}
  <form class="search" role="search" action="/" method="get" autocomplete="off">
    {ic("search", "ic search-ic")}
    <input id="q" name="q" type="search" placeholder="Search {len(games)} games" aria-label="Search games">
    <div class="search-pop" id="searchPop" role="listbox" hidden></div>
  </form>
  <div class="top-actions">
    <a class="btn-random" href="/games/" id="randomBtn">{ic("random")}<span>Random</span></a>
    <button class="icon-btn" id="themeBtn" aria-label="Toggle dark mode" type="button">{ic("moon", "ic i-moon")}{ic("sun", "ic i-sun")}</button>
  </div>
</header>
<div class="shell"><aside class="sidebar" id="sidebar" aria-label="Categories">
  <nav>
    {side_link("/", "Home", "home", active == "home")}{side_link("/games/", "All games A–Z", "grid", active == "az")}{side_link("/games-like-wordle/", "Games like Wordle", "word", active == "hub")}
    <a class="side-link side-partner" href="/classroom6x/">{ic("backpack")}<span>Classroom 6X<small>2,300+ more games</small></span></a>
    <div class="side-sep"></div>
    <p class="side-title">Categories</p>
    {cats}
  </nav>
</aside>
<div class="scrim" id="scrim" hidden></div>
'''

def footer():
    popular = "".join(f'<li><a href="/category/{c}/">{esc(cat(c)["label"])} Games</a></li>' for c in cat_order[:10] if len(by_cat[c]) > 1)
    return f'''</div>
<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      {LOGO}
      <p>Free browser games for study breaks and lunch. No downloads, no accounts, just press play.</p>
    </div>
    <div>
      <p class="footer-h">Popular</p>
      <ul>{popular}</ul>
    </div>
    <div>
      <p class="footer-h">Explore</p>
      <ul>
        <li><a href="/games/">All games A–Z</a></li>
        <li><a href="/games-like-wordle/">Games like Wordle</a></li>
        <li><a href="/classroom6x/">Classroom 6X</a></li>
        <li><a href="/about%20us.html">About us</a></li>
      </ul>
    </div>
    <div>
      <p class="footer-h">Legal</p>
      <ul>
        <li><a href="/terms.html">Terms of use</a></li>
        <li><a href="/privacy-policy.html">Privacy policy</a></li>
        <li><a href="/dmca.html">DMCA</a></li>
      </ul>
    </div>
  </div>
  <p class="footer-fine">&copy; {TODAY[:4]} {BRAND}. Games and trademarks belong to their respective developers and publishers. <a href="/dmca.html">Copyright requests</a>.</p>
</footer>
<script src="/assets/js/site.js?v=1" defer></script>
</body>
</html>
'''

def ad():
    return f'''<div class="ad-unit" aria-label="Advertisement"><ins class="adsbygoogle" style="display:block" data-ad-client="{ADS}" data-ad-slot="4436716876" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script></div>'''

def breadcrumb(trail):
    crumbs = "".join(f'<a href="{u}">{esc(n)}</a>{ic("chevron")}' for n, u in trail[:-1]) + f'<span aria-current="page">{esc(trail[-1][0])}</span>'
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(trail)]}
    return f'<nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>', ld

def tile(g, big=False, eager=False):
    t = esc(g["title"], quote=True)
    return (f'<a class="tile{" big" if big else ""}" href="{gpath(g["slug"])}" title="{t}"><span class="tile-img">'
            f'<img src="/{g["image"]}" alt="{t} – play free online" width="480" height="270" loading="{"eager" if eager else "lazy"}" decoding="async"></span>'
            f'<span class="tile-name">{esc(g["title"])}</span></a>')

def grid(items, cls="grid grid--wide"): return f'<div class="{cls}">' + "".join(tile(g) for g in items) + "</div>"
def rail(items): return '<div class="rail rail--wide">' + "".join(tile(g) for g in items) + "</div>"

def row(rid, icon, title, more_href, more_label, inner):
    return (f'<section class="row" aria-labelledby="{rid}"><div class="row-head"><h2 id="{rid}">{ic(icon, "ic row-ic")}{title}</h2>'
            f'<a class="row-more" href="{more_href}">{more_label}{ic("chevron")}</a></div>{inner}</section>')

def cat_chips(exclude=None, counts=True):
    return "".join(f'<a class="chip" href="/category/{o}/">{ic(o)}{esc(cat(o)["label"])}' + (f'<small>{len(by_cat[o])}</small>' if counts else "") + '</a>'
                   for o in cat_order if o != exclude and len(by_cat[o]) > 1)

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
    t, slug, c0 = g["title"], g["slug"], cat(g["primary"]); url = SITE + gpath(slug)
    genre = c0["label"]; low = genre.lower()
    seo_title = f"{t} – Play Free {genre} Game Online | {BRAND}"
    if len(seo_title) > 66: seo_title = f"{t} – Play Free Online | {BRAND}"
    if len(seo_title) > 66: seo_title = trunc(f"{t} – Play Free Online", 66)
    seo_title = g.get("seoTitle") or seo_title
    h1 = g.get("h1") or t
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
      [f"How do I start playing {t}?", f"Click the Play Now button on this page. The game loads inside the page and you can begin as soon as it finishes loading. Use the Fullscreen button for a larger play area."],
      [f"{t} will not load. What should I do?", "Refresh the page, check your internet connection and make sure you are using an up-to-date browser. Some school or work networks block game content, and in that case the game may not load on that network."],
      list(c0["faq"]),
    ]
    extra_secs = "".join(f'<section class="about" aria-labelledby="sec-{x["id"]}"><h2 id="sec-{x["id"]}">{esc(x["h2"])}</h2>{x["html"]}</section>' for x in g.get("sections", []))
    crumb_html, crumb_ld = breadcrumb([("Home", "/"), (f"{genre} Games", f"/category/{g['primary']}/"), (t, gpath(slug))])
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
    tags = "".join(f'<a class="tag" href="/category/{c}/">{esc(cat(c)["label"])} Games</a>' for c in g["cats"])
    genres = " · ".join(esc(cat(c)["label"]) for c in g["cats"])
    rel = related_for(g)
    side_pool = [x for x in by_cat[g["primary"]] if x["id"] != g["id"] and x not in rel]
    side = (side_pool + rel)[:10]
    minis = "".join(f'<a class="mini" href="{gpath(x["slug"])}"><img src="/{x["image"]}" alt="" width="64" height="64" loading="lazy" decoding="async"><span>{esc(x["title"])}</span></a>' for x in side)
    poster = g.get("poster")
    poster_alt = esc(g.get("alt") or f"Play {t} online free — {low} game", quote=True)
    tall = g.get("frame") == "tall"
    body = f'''  <main id="main" class="main">
    <div class="game-layout">
      <article class="game-main">
        {crumb_html}
        <div class="player{' player--tall' if tall else ''}" id="player" role="region" aria-label="Play {esc(t, quote=True)}" data-src="{esc(embed, quote=True)}" data-slug="{slug}" data-title="{esc(t, quote=True)}">
          <div class="player-poster" id="poster">
            <img class="poster-bg" src="/{poster or g['image']}" alt="" aria-hidden="true">
            <div class="poster-card">
              <img{'' if poster else ' class="poster-wide"'} src="/{poster or g['image']}" alt="{poster_alt}" width="{'160' if poster else '320'}" height="{'160' if poster else '180'}" fetchpriority="high">
              <p class="poster-title">{esc(t)}</p>
              <button class="play-btn" id="playBtn" type="button">{ic("play")}<span>Play Now</span></button>
            </div>
          </div>
          <noscript><p class="noscript-note">Please enable JavaScript to play {esc(t)}.</p></noscript>
        </div>
        <div class="game-bar">
          <div class="game-id">
            <img src="/{g['image']}" alt="" width="44" height="44">
            <div>
              <h1>{esc(h1)}</h1>
              <p class="muted">{genres}</p>
            </div>
          </div>
          <div class="game-actions">
            <button class="act" id="reloadBtn" type="button" aria-label="Restart game">{ic("restart")}<span>Restart</span></button>
            <button class="act" id="shareBtn" type="button" aria-label="Copy link">{ic("share")}<span>Share</span></button>
            <button class="act act-primary" id="fsBtn" type="button" aria-label="Fullscreen" aria-expanded="false">{ic("expand")}<span>Fullscreen</span></button>
          </div>
        </div>
        <p class="game-hint">Click the game once to focus it. If the keyboard stops responding, click the game area again.</p>

        <section class="about" aria-labelledby="about"><h2 id="about">About {esc(t)}</h2><p>{esc(about)}</p>
          <p>It is part of our collection of {len(by_cat[g["primary"]])} free <a href="/category/{g["primary"]}/">{esc(low)} games</a>, inside a library of {len(games)} browser games you can play without installing anything.</p>
          <div class="tags">{tags}</div></section>
        <section class="about" aria-labelledby="howto"><h2 id="howto">How to Play {esc(t)}</h2>
          <ol class="steps">{"".join(f"<li>{esc(s)}</li>" for s in steps)}</ol></section>
        <section class="about" aria-labelledby="controls"><h2 id="controls">Controls</h2>
          <dl class="controls"><div><dt>Desktop</dt><dd>{esc(controls_d)}</dd></div><div><dt>Mobile and tablet</dt><dd>{esc(controls_m)}</dd></div></dl>
          <p class="note">Controls can differ between games. Check the start screen or tutorial of {esc(t)} for the exact keys.</p></section>
        <section class="about" aria-labelledby="tips"><h2 id="tips">Tips and Tricks for {esc(t)}</h2>
          <ul class="ticks">{"".join(f"<li>{esc(s)}</li>" for s in tips)}</ul></section>
        <section class="about" aria-labelledby="features"><h2 id="features">Features</h2>
          <ul class="ticks">{"".join(f"<li>{esc(s)}</li>" for s in feats)}</ul></section>
        {extra_secs}
        <section class="about" aria-labelledby="faq"><h2 id="faq">Frequently Asked Questions</h2>
          <div class="faq">{"".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)}</div></section>
      </article>

      <aside class="game-side" aria-label="Game details and more games">
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
        <p class="side-h">More {esc(low)} games</p>
        <div class="mini-list">{minis}</div>
        <a class="btn btn-primary" href="/category/{g["primary"]}/">All {len(by_cat[g["primary"]])} {esc(low)} games</a>
      </aside>
    </div>

    {row("relatedTitle", g["primary"], "You may also like", f"/category/{g['primary']}/", "See all", rail(rel))}
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
              {"@type": "ListItem", "position": i + 1, "url": SITE + gpath(g['slug']), "name": g["title"]} for i, g in enumerate(items[:100])]}]
    body = f'''  <main id="main" class="main">
    {crumb_html}
    <header class="page-head"><h1>{esc(info["h1"])}</h1><p class="lede">{esc(info["intro"])}</p>
      <p class="lede">{len(items)} {esc(label.lower())} games, all free, all in your browser, on desktop, tablet and mobile.{' Fans of five-letter guessing games should see our <a href="/games-like-wordle/">games like Wordle</a> page.' if c == 'word' else ''}</p>
      <p class="count">{len(items)} games</p></header>
    {grid(items)}
    {ad()}
    <section class="cats-block" aria-labelledby="moreCats"><h2 id="moreCats">More categories</h2><div class="chips">{cat_chips(exclude=c)}</div></section>
  </main>
'''
    return head(title, desc, url, og_image=abs_url(items[0]["image"]), ld=ld) + header_nav(c) + body + footer()

def index_page():
    url = f"{SITE}/games/"; crumb_html, crumb_ld = breadcrumb([("Home", "/"), ("All Games A–Z", "/games/")])
    letters = {}
    for g in sorted(games, key=lambda x: x["title"].lower()):
        k = g["title"][:1].upper(); k = k if k.isalpha() else "#"; letters.setdefault(k, []).append(g)
    order = sorted(letters, key=lambda k: ("~" if k == "#" else k))
    nav = "".join(f'<a href="#l-{k if k != "#" else "num"}">{k}</a>' for k in order)
    secs = "".join(f'<section class="az-section" aria-labelledby="l-{k if k != "#" else "num"}"><h2 id="l-{k if k != "#" else "num"}">{k}</h2><ul class="az-list">' +
                   "".join(f'<li><a href="{gpath(g["slug"])}">{esc(g["title"])}</a> <span>{esc(cat(g["primary"])["label"])}</span></li>' for g in letters[k]) + "</ul></section>"
                   for k in order)
    body = f'''  <main id="main" class="main">
    {crumb_html}
    <header class="page-head"><h1>All Free Browser Games A–Z</h1><p class="lede">Every one of our {len(games)} free games in alphabetical order. Pick a letter or jump to a category.</p></header>
    <section class="cats-block" aria-label="Categories"><div class="chips">{cat_chips()}</div></section>
    <nav class="letters" aria-label="Letters">{nav}</nav>
    {secs}
  </main>
'''
    return head(f"All Free Browser Games A–Z ({len(games)} Games) | {BRAND}", f"Browse all {len(games)} free browser games from A to Z. Action, arcade, puzzle, driving, simulation and more. No downloads, no sign-up.", url, ld=[crumb_ld]) + header_nav("az") + body + footer()

# ---------- HOME ----------

def home_page():
    url = SITE + "/"
    # featured mosaic: round-robin over categories, 2 big + 16 small = 24 cells
    featured_ids = ["basketball-superstars", "crazy-drift", "snake-clash-io", "tape-escape", "word-guess"]
    feat = [next(x for x in games if x["id"] == i) for i in featured_ids if any(x["id"] == i for x in games)]
    seen = {x["id"] for x in feat}
    for round_ in range(6):
        for c in cat_order[:10]:
            pool = [x for x in by_cat[c] if x["id"] not in seen]
            if pool and len(feat) < 18:
                feat.append(pool[round_ * 3 % len(pool)]); seen.add(feat[-1]["id"])
    feat = feat[:18]
    mosaic = '<div class="mosaic mosaic--wide">' + "".join(tile(x, big=i in (0, 7), eager=i < 3) for i, x in enumerate(feat)) + "</div>"
    shelves = ""
    for c in cat_order[:8]:
        items = [x for x in by_cat[c] if x["id"] not in seen][:12]
        info = cat(c)
        shelves += row(f"s-{c}", c, f'{esc(info["label"])} Games', f"/category/{c}/", f"See all {len(by_cat[c])}", rail(items))
        if c == cat_order[1]: shelves += ad()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/",
           "potentialAction": {"@type": "SearchAction", "target": SITE + "/?q={search_term_string}", "query-input": "required name=search_term_string"}},
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Featured games", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": SITE + gpath(x['slug']), "name": x["title"]} for i, x in enumerate(feat)]}]
    cats_links = ", ".join(f'<a href="/category/{c}/">{esc(cat(c)["label"].lower())} games</a>' for c in cat_order[:6])
    body = f"""  <main id="main" class="main">
    <section class="hero" id="hero" aria-label="Welcome">
      <div class="hero-copy">
        <h1>Free period? Hit play.</h1>
        <p class="lede">{len(games) // 100 * 100}+ free games that load in seconds. No downloads, no logins, no waiting. Works on Chromebooks, laptops and phones.</p>
        <a class="pill-link" href="/classroom6x/">Want even more? Try Classroom 6X with 2,300+ extra games {ic("chevron")}</a>
      </div>
      {mosaic}
    </section>
    <section id="searchResults" class="row search-results" aria-labelledby="searchTitle" aria-live="polite" hidden>
      <div class="row-head"><h2 id="searchTitle">Search results</h2><a class="row-more" href="/">Clear search</a></div>
      <div class="grid grid--wide" id="searchGrid"></div>
      <p class="lede" id="searchEmpty" hidden>No games match that search. Try a shorter word, or browse a category in the menu.</p>
    </section>
    <div id="shelves">
      {shelves}
      <section class="cats-block" aria-labelledby="browseCats"><div class="row-head"><h2 id="browseCats">Browse by category</h2><a class="row-more" href="/games/">All games A–Z{ic("chevron")}</a></div><div class="chips">{cat_chips()}</div></section>
      <section class="about home-about" aria-labelledby="aboutTitle">
        <h2 id="aboutTitle">Free online games that run in your browser</h2>
        <p>Unblocked Games USA is a library of {len(games)} free browser games. Every game has its own page with a short guide, controls, tips and answers to common questions, so you know what to expect before you press play.</p>
        <p>Looking for something to try? Start with {cats_links}, or open the <a href="/games/">A–Z list</a> of every game. Word puzzle fans can try <a href="/wordle-unlimited/">Wordle, a free unlimited Wordle game</a> or browse more <a href="/games-like-wordle/">games like Wordle</a>. There are no downloads or installs, and games run on desktop, tablet and phone browsers, though availability can depend on your network.</p>
      </section>
    </div>
  </main>
"""
    return head(f"{BRAND} — Play {len(games)} Free Browser Games, No Downloads",
                f"Play {len(games)} free browser games instantly. No downloads, no sign-ups. Action, racing, puzzle, arcade, sports and more — works right in your browser.",
                url, og_image=f"{SITE}/images/basketball-superstars.jpg", ld=ld) + header_nav("home") + body + footer()


# ---------- Wordle-style hub ----------
def wordle_hub_page():
    url = f"{SITE}/games-like-wordle/"
    wg = next(x for x in games if x["id"] == "word-guess")
    others = [x for x in by_cat["word"] if x["id"] != "word-guess"]
    title = f"Games Like Wordle: Free Word Games Online | {BRAND}"
    desc = f"Looking for games like Wordle? Play Wordle, a free unlimited Wordle game, plus {len(others)} more word games in your browser. No sign-up, no download."
    faqs = [
      ["What are the best games like Wordle?", f"Wordle is our free unlimited Wordle game: guess a hidden five-letter word in six tries, with a daily puzzle and endless practice rounds. If you want other word challenges, this page also lists {len(others)} more free word games, from word searches to letter puzzles."],
      ["Is there an unlimited Wordle?", "The official Wordle by The New York Times gives one puzzle per day. Our Wordle is an independent Wordle-style game with an Unlimited mode, so you can play as many random five-letter words as you like."],
      ["Are these games official Wordle?", "No. The games on this page are independent and are not affiliated with or endorsed by The New York Times or Wordle. The official game is at nytimes.com/games/wordle."],
      ["Do I need an account or a download?", "No. Every game runs in your browser, with no sign-up and no install."],
      ["Can I play these at school or work?", "They are ordinary web pages, but whether they open depends on the filter on your network. We cannot guarantee access on every school or work network."],
    ]
    crumb_html, crumb_ld = breadcrumb([("Home", "/"), ("Games Like Wordle", "/games-like-wordle/")])
    ld = [crumb_ld,
      {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Games Like Wordle", "url": url, "description": desc,
       "isPartOf": {"@type": "WebSite", "name": BRAND, "url": SITE + "/"}},
      {"@context": "https://schema.org", "@type": "ItemList", "numberOfItems": len(others) + 1, "itemListElement": [
          {"@type": "ListItem", "position": i + 1, "url": SITE + gpath(x['slug']), "name": x["title"]} for i, x in enumerate([wg] + others)]},
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
          {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]
    body = f'''  <main id="main" class="main">
    {crumb_html}
    <header class="page-head"><h1>Games Like Wordle: Free Word Games to Play Online</h1>
      <p class="lede">Love guessing a hidden word in a few tries? These free browser games scratch the same itch. Start with Wordle, our free unlimited Wordle game, then try more word puzzles. Everything runs in your browser with no sign-up and no download.</p></header>
    <section class="about hub-feature" aria-labelledby="hubFeat">
      <a class="hub-feature-img" href="/wordle-unlimited/"><img src="/{wg['poster']}" alt="Wordle, a free unlimited Wordle game" width="300" height="300" loading="eager" decoding="async" /></a>
      <div>
        <h2 id="hubFeat">Wordle: the free unlimited Wordle game</h2>
        <p>Find the hidden five-letter word in six tries. Green, yellow and grey tiles show how close each guess is. There is a daily puzzle, an Unlimited mode for endless practice, hard mode, a colour-blind palette and shareable results, and no account is needed.</p>
        <ul class="ticks"><li>Daily puzzle plus unlimited random words</li><li>Over 12,900 accepted words</li><li>Works on desktop, tablet and phone</li></ul>
        <p><a class="btn btn-primary" href="/wordle-unlimited/">Play Wordle</a></p>
      </div>
    </section>
    {row("hubMore", "word", "More free word games", "/category/word/", "All word games", grid(others))}
    <section class="about about--full" aria-labelledby="hubChoose"><h2 id="hubChoose">How to choose a word game</h2>
      <ul class="ticks">
        <li>Want the classic five-letter guessing format? Play Wordle, with a daily puzzle and unlimited practice.</li>
        <li>Want to train spelling and vocabulary? Browse the other word games above and open any page for its short guide and controls.</li>
        <li>Short on time? Every game loads in your browser in seconds, so you can try a few and keep the ones you like.</li>
      </ul>
      <p>Looking for the official daily puzzle? It lives at <a href="https://www.nytimes.com/games/wordle/index.html" rel="noopener">nytimes.com/games/wordle</a>. Our Wordle and the other games here are independent and not affiliated with The New York Times.</p></section>
    <section class="about about--full" aria-labelledby="faq"><h2 id="faq">Frequently Asked Questions</h2>
      <div class="faq">{"".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)}</div></section>
    {ad()}
  </main>
'''
    return head(title, desc, url, og_image=abs_url(wg["image"]), ld=ld) + header_nav("hub") + body + footer()

# ---------- static pages (About, DMCA, Privacy, Terms) ----------
STATIC_PAGES = [("about us.html", "about", "About us"), ("dmca.html", "dmca", "DMCA"),
                ("privacy-policy.html", "privacy-policy", "Privacy policy"), ("terms.html", "terms", "Terms of use")]

def static_page(out_name, key):
    raw = open(os.path.join(ROOT, "tools", "pages", key + ".html"), encoding="utf-8").read()
    meta = dict(re.findall(r"<!--(\w+): (.*?)-->", raw))
    body = re.sub(r"<!--.*?-->\n?", "", raw).strip()
    url = f"{SITE}/{out_name.replace(' ', '%20')}"
    nav = "".join(f'<a href="/{f.replace(" ", "%20")}"{" aria-current=\"page\"" if f == out_name else ""}>{label}</a>' for f, _, label in STATIC_PAGES)
    updated = f'<p class="legal-updated">{meta["updated"]}</p>' if meta.get("updated") else ""
    page = f'''  <main id="main" class="main">
    <div class="legal">
      <nav class="legal-nav" aria-label="About and legal">{nav}</nav>
      <article class="legal-body">
        <h1>{meta["h1"]}</h1>
        {updated}
        <div class="prose legal-prose">
{body}
        </div>
      </article>
    </div>
  </main>
'''
    return head(meta["title"], meta["desc"], url, ld=[]) + header_nav() + page + footer()

# ---------- build ----------
for d in ("game", "category", "games", "games-like-wordle"):
    shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
def redirect_page(target, title):
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><title>{esc(title)} | {BRAND}</title>'
            f'<link rel="canonical" href="{SITE}{target}" /><meta name="robots" content="noindex, follow" />'
            f'<script>location.replace("{target}"+location.search+location.hash);</script>'
            f'<noscript><meta http-equiv="refresh" content="0; url={target}" /></noscript></head>'
            f'<body><p>Redirecting to <a href="{target}">{esc(title)}</a>…</p></body></html>\n')
for g in games:
    path = gpath(g["slug"]).strip("/")
    write(f"{path}/index.html", game_page(g))
    if path != f"game/{g['slug']}":
        write(f"game/{g['slug']}/index.html", redirect_page("/" + path + "/", g["title"]))
# /wordle/ is a short alias for Wordle Unlimited
write("wordle/index.html", redirect_page("/wordle-unlimited/", "Wordle Unlimited"))
for c in cat_order: write(f"category/{c}/index.html", category_page(c))
write("games/index.html", index_page())
write("games-like-wordle/index.html", wordle_hub_page())
write("index.html", home_page())
for out_name, key, _ in STATIC_PAGES: write(out_name, static_page(out_name, key))

# old ?id= links -> new URLs (GitHub Pages cannot 301)
write("game.html", f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta name="robots" content="noindex" /><title>Redirecting… | {BRAND}</title>
<script>(function(){{var id=new URLSearchParams(location.search).get('id')||'';var s=id.replace(/-+/g,'-').replace(/^-|-$/g,'');location.replace(s?'/game/'+encodeURIComponent(s)+'/':'/');}})();</script>
<noscript><meta http-equiv="refresh" content="0; url=/" /></noscript></head><body><p>Redirecting to <a href="/">{BRAND}</a>…</p></body></html>
''')

urls = [(SITE + "/", "1.0", "daily"), (SITE + "/games/", "0.8", "weekly"), (SITE + "/games-like-wordle/", "0.9", "weekly")]
urls += [(f"{SITE}/category/{c}/", "0.8", "weekly") for c in cat_order]
urls += [(SITE + gpath(g['slug']), "0.7", "monthly") for g in games]
urls += [(f"{SITE}/{p}", "0.3", "yearly") for p in ("about%20us.html", "dmca.html", "privacy-policy.html", "terms.html")]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>\n" for u, p, f in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /game.html\n\nSitemap: {SITE}/sitemap.xml\n")
print(f"built {len(games)} game pages, {len(cat_order)} category pages, {len(urls)} sitemap URLs")
