#!/usr/bin/env python3
"""
Fix script for UnblockedGames-USA.github.io
Run from repo root: python fix_site.py
Fixes: game launch, duplicate similar games, "Free 2" spam, unified nav, SEO, mobile
"""
import os, re
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
REPO      = Path(__file__).parent
BASE_URL  = "https://unblockedgames-usa.github.io"
IMG_BASE  = f"{BASE_URL}/images"
PER_PAGE  = 50
SKIP_DIRS = {"categ","assets",".git","images","privacy-policy","contact","faq","dmca","node_modules"}

CATS = {
    "shooter":    "🎯 Shooter",
    "platformer": "🏃 Platformer",
    "2-player":   "👥 2-Player",
    "fighting":   "🥊 Fighting",
    "driving":    "🚗 Driving",
    "puzzle":     "🧠 Puzzle",
    "multiplayer":"🌐 Multiplayer",
    "action":     "💥 Action",
    "skill":      "🏆 Skill",
    "adventure":  "🗺️ Adventure",
    "racing":     "🏁 Racing",
    "strategy":   "♟️ Strategy",
    "sports":     "⚽ Sports",
    "simulation": "🏙️ Simulation",
    "clicker":    "🖱️ Clicker",
    "horror":     "👻 Horror",
    "kids":       "🧸 Kids",
}

# ── HELPERS ──────────────────────────────────────────────────────────────────

def slug_to_title(slug):
    """10-minutes-till-dawn → 10 Minutes Till Dawn"""
    return " ".join(w.capitalize() for w in slug.replace("-"," ").split())

def clean_title(t):
    """Remove 'Unblocked — Free 2', '— Free 2', etc."""
    t = re.sub(r'\s*[—–-]+\s*Free\s*2\b.*', '', t, flags=re.I)
    t = re.sub(r'\s*Unblocked\b.*', '', t, flags=re.I)
    return t.strip()

def read_html(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except:
        return ""

def get_iframe_src(html):
    """Extract real iframe URL (data-src preferred, then src != about:blank)."""
    m = re.search(r'data-src=["\']([^"\']+)["\']', html)
    if m: return m.group(1)
    m = re.search(r'<iframe[^>]+src=["\'](?!about:blank)([^"\']+)["\']', html, re.I)
    if m: return m.group(1)
    return ""

def get_game_cats(html):
    """Extract category slugs from existing page."""
    found = re.findall(
        r'href=["\'](?:https?://[^"\']+)?(?:/categ/|../../categ/|categ/)([a-z0-9-]+)[/"\'?]',
        html
    )
    seen, out = set(), []
    for c in found:
        c = c.rstrip("/")
        if c in CATS and c not in seen:
            seen.add(c); out.append(c)
    return out

def get_description(html):
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if m: return m.group(1)
    m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html, re.I)
    if m: return m.group(1)
    return ""

def all_games():
    games = []
    for d in sorted(REPO.iterdir()):
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith("."):
            if (d / "index.html").exists():
                games.append(d.name)
    return games

# ── SHARED COMPONENTS ─────────────────────────────────────────────────────────

def nav_html(depth=0):
    """Unified nav — depth=0 means root (/), depth=1 means one level deep (/game/)"""
    prefix = "../" * depth if depth > 0 else "/"
    links = "\n          ".join(
        f'<li><a href="{prefix}categ/{k}">{v}</a></li>'
        for k, v in CATS.items()
    )
    logo_href = prefix if prefix.endswith("/") else prefix
    return f'''<header class="site-header">
  <div class="wrap hdr-inner">
    <a href="{logo_href}" class="logo">🎮 Unblocked Games USA</a>
    <div class="search-wrap">
      <input type="text" id="searchInput" placeholder="Search games…" autocomplete="off">
      <button id="searchBtn" aria-label="Search">🔍</button>
      <div id="searchDrop"></div>
    </div>
    <button class="nav-toggle" id="navToggle" aria-label="Menu">☰</button>
  </div>
  <nav class="main-nav">
    <ul id="navMenu">
          {links}
    </ul>
  </nav>
</header>'''

def footer_html(depth=0):
    prefix = "../" * depth if depth > 0 else "/"
    cats = " ".join(
        f'<a href="{prefix}categ/{k}">{v}</a>'
        for k, v in CATS.items()
    )
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-cats">{cats}</div>
    <div class="footer-links">
      <a href="{prefix}privacy-policy">Privacy Policy</a>
      <a href="{prefix}contact">Contact Us</a>
      <a href="{prefix}faq">FAQ</a>
      <a href="{prefix}dmca">DMCA</a>
    </div>
    <p class="footer-copy">&copy; <span class="yr"></span> Unblocked Games USA. All rights reserved.</p>
  </div>
</footer>
<script>document.querySelectorAll('.yr').forEach(e=>e.textContent=new Date().getFullYear());</script>'''

# ── CSS ───────────────────────────────────────────────────────────────────────

SHARED_CSS = '''<style>
/* ── RESET & BASE ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,sans-serif;background:#0a0e1a;color:#dce8ff;line-height:1.6;min-height:100vh}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.wrap{max-width:1280px;margin:0 auto;padding:0 16px}

/* ── HEADER ── */
.site-header{background:linear-gradient(90deg,#001a6e,#0d1f6e 40%,#1a0a2e 65%,#8b0000);
  border-bottom:3px solid #c0392b;position:sticky;top:0;z-index:100;
  box-shadow:0 4px 20px rgba(0,0,0,.7)}
.hdr-inner{display:flex;align-items:center;gap:12px;padding:10px 16px;flex-wrap:wrap}
.logo{font-weight:800;font-size:1.25rem;color:#fff;white-space:nowrap;
  text-shadow:0 0 16px rgba(192,57,43,.7)}
.logo:hover{text-shadow:0 0 24px rgba(192,57,43,1)}

/* SEARCH */
.search-wrap{display:flex;position:relative;margin-left:auto}
.search-wrap input{padding:.4rem .9rem;border:1px solid rgba(255,255,255,.15);
  border-radius:20px 0 0 20px;background:rgba(255,255,255,.12);color:#fff;
  font-size:.88rem;width:200px;outline:none}
.search-wrap input::placeholder{color:rgba(255,255,255,.45)}
.search-wrap input:focus{background:rgba(255,255,255,.2);width:240px;transition:width .2s}
.search-wrap button{background:#c0392b;color:#fff;border:none;
  border-radius:0 20px 20px 0;padding:.4rem .9rem;cursor:pointer;font-size:.9rem}
#searchDrop{position:absolute;top:calc(100% + 6px);left:0;right:0;
  background:#0a1535;border:1px solid rgba(192,57,43,.3);border-radius:10px;
  max-height:280px;overflow-y:auto;z-index:300;display:none;
  box-shadow:0 8px 28px rgba(0,0,0,.8)}
#searchDrop.open{display:block}
#searchDrop a{display:flex;align-items:center;gap:10px;padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;font-weight:600}
#searchDrop a:hover{background:rgba(192,57,43,.2);color:#fff}
#searchDrop img{width:36px;height:26px;object-fit:cover;border-radius:4px;flex-shrink:0}
#searchDrop .no-res{padding:12px;color:rgba(255,255,255,.4);text-align:center;font-size:.83rem}

/* NAV TOGGLE */
.nav-toggle{display:none;background:none;border:none;color:#fff;
  font-size:1.4rem;cursor:pointer;padding:.3rem .5rem}

/* NAV BAR */
.main-nav{background:linear-gradient(90deg,#001050,#0d1560 40%,#1a0825 70%,#500010);
  border-top:1px solid rgba(255,255,255,.06)}
.main-nav ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;
  gap:4px;padding:8px 16px;max-width:1280px;margin:0 auto}
.main-nav a{color:rgba(255,255,255,.85);padding:4px 11px;border-radius:20px;
  font-size:.8rem;font-weight:600;border:1px solid transparent;white-space:nowrap;
  transition:background .15s,color .15s}
.main-nav a:hover,.main-nav a.active{background:rgba(192,57,43,.35);color:#fff;
  border-color:rgba(192,57,43,.4)}

/* ── FOOTER ── */
.site-footer{background:#060b18;border-top:2px solid #c0392b;
  padding:28px 16px;margin-top:48px;text-align:center}
.footer-cats{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-bottom:14px}
.footer-cats a{background:rgba(255,255,255,.07);padding:4px 11px;border-radius:16px;font-size:.78rem}
.footer-cats a:hover{background:rgba(192,57,43,.3)}
.footer-links{display:flex;gap:16px;justify-content:center;margin-bottom:10px;
  font-size:.82rem;opacity:.7;flex-wrap:wrap}
.footer-links a:hover{opacity:1}
.footer-copy{font-size:.75rem;opacity:.35}

/* ── GAME GRID (shared) ── */
.games-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:16px 0}
.game-card{display:flex;flex-direction:column;background:#111827;border-radius:10px;
  overflow:hidden;border:1px solid rgba(255,255,255,.07);
  transition:transform .2s,box-shadow .2s,border-color .2s}
.game-card:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,0,0,.5);
  border-color:rgba(192,57,43,.4)}
.game-card img{width:100%;height:110px;object-fit:cover}
.game-card span{padding:7px 8px;font-size:.78rem;text-align:center;font-weight:500;line-height:1.3}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .nav-toggle{display:block}
  .main-nav ul{display:none;flex-direction:column;align-items:flex-start;padding:8px 16px}
  .main-nav ul.open{display:flex}
  .hdr-inner{flex-wrap:wrap}
  .search-wrap{order:3;width:100%}
  .search-wrap input{width:100%;border-radius:20px 0 0 20px}
}
@media(max-width:600px){
  .games-grid{grid-template-columns:repeat(2,1fr)}
  .logo{font-size:1.1rem}
}
</style>'''

SHARED_JS = '''<script>
/* ── NAV TOGGLE ── */
document.getElementById('navToggle')?.addEventListener('click',()=>
  document.getElementById('navMenu')?.classList.toggle('open'));

/* ── SEARCH ── */
(function(){
  const inp=document.getElementById('searchInput');
  const drop=document.getElementById('searchDrop');
  const btn=document.getElementById('searchBtn');
  if(!inp||!drop)return;
  function close(){drop.classList.remove('open');drop.innerHTML='';}
  function go(q){q=q.trim();if(!q)return;close();window.location='/?q='+encodeURIComponent(q);}
  inp.addEventListener('input',function(){
    const q=this.value.trim();
    if(!q){close();return;}
    drop.innerHTML=`<div class="no-res"><a href="/?q=${encodeURIComponent(q)}" style="color:#e74c3c">Search all games for "<b>${q}</b>"</a></div>`;
    drop.classList.add('open');
  });
  inp.addEventListener('keydown',e=>{if(e.key==='Enter')go(inp.value);if(e.key==='Escape')close();});
  btn.addEventListener('click',()=>go(inp.value));
  document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap'))close();});
})();
</script>'''

# ── GAME PAGE ─────────────────────────────────────────────────────────────────

GAME_CSS = SHARED_CSS + '''<style>
/* ── GAME AREA ── */
.game-section{padding:20px 0}
.game-title-bar{text-align:center;margin-bottom:16px}
.game-title-bar h1{font-size:clamp(1.4rem,4vw,2.2rem);font-weight:800;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.game-title-bar p{color:rgba(255,255,255,.6);font-size:.95rem;margin-top:6px}

/* IFRAME WRAPPER */
.game-frame-wrap{position:relative;width:100%;max-width:960px;margin:0 auto;
  background:#000;border-radius:10px;overflow:hidden;border:2px solid rgba(255,255,255,.08);
  aspect-ratio:16/9}
.game-thumb{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1}
.game-overlay{position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;z-index:3;
  background:rgba(0,0,0,.45);cursor:pointer;transition:background .2s}
.game-overlay:hover{background:rgba(0,0,0,.3)}
.play-btn{width:76px;height:76px;border-radius:50%;border:none;cursor:pointer;
  background:linear-gradient(135deg,#1a3a8a,#c0392b);color:#fff;
  font-size:2.2rem;display:flex;align-items:center;justify-content:center;
  padding-left:5px;box-shadow:0 0 0 4px rgba(192,57,43,.4),0 8px 30px rgba(0,0,0,.6);
  animation:pulse 2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(192,57,43,.4),0 8px 30px rgba(0,0,0,.6)}
  50%{box-shadow:0 0 0 12px rgba(192,57,43,.1),0 8px 30px rgba(0,0,0,.6)}}
.play-label{color:#fff;font-weight:700;font-size:1rem;letter-spacing:2px;
  margin-top:12px;background:rgba(0,0,0,.5);padding:4px 16px;border-radius:20px}
.game-frame{position:absolute;inset:0;width:100%;height:100%;border:none;
  display:none;z-index:2}
.game-frame.active{display:block}
.fs-btn{position:absolute;bottom:10px;right:10px;z-index:4;
  background:rgba(0,0,0,.65);color:#fff;border:none;border-radius:6px;
  padding:5px 12px;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:6px}
.fs-btn:hover{background:#c0392b}

/* DESCRIPTION */
.game-desc{background:#111827;border-radius:10px;padding:24px;margin:20px 0;
  border:1px solid rgba(255,255,255,.07)}
.game-desc h2{font-size:1.3rem;font-weight:700;color:#e74c3c;margin-bottom:10px}
.game-desc h3{font-size:1.05rem;font-weight:700;color:#e74c3c;margin:16px 0 8px}
.game-desc p{margin-bottom:10px;color:rgba(255,255,255,.8);font-size:.95rem}
.game-desc ul{padding-left:20px;margin-bottom:10px}
.game-desc li{margin-bottom:5px;color:rgba(255,255,255,.75);font-size:.93rem}
.game-thumb-sm{float:left;width:120px;border-radius:8px;margin:0 16px 12px 0;
  border:1px solid rgba(255,255,255,.1)}
.cat-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.cat-tag{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(192,57,43,.6));
  color:#fff;border-radius:20px;padding:.3rem .9rem;font-size:.82rem;font-weight:600;
  border:1px solid rgba(255,255,255,.1)}
.cat-tag:hover{background:linear-gradient(135deg,#1a3a8a,#c0392b)}

/* SIMILAR GAMES */
.similar-section{margin:28px 0}
.section-heading{font-size:1.25rem;font-weight:700;margin-bottom:14px;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

/* BROWSE CATEGORIES */
.browse-section{margin:28px 0}
.cat-grid{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;
  padding:16px 20px;background:linear-gradient(135deg,#0a1540,#1a0825);
  border-radius:40px;border:1px solid rgba(192,57,43,.2)}
.cat-item{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(192,57,43,.55));
  color:#fff;border-radius:20px;padding:.35rem 1rem;font-size:.85rem;font-weight:600;
  border:1px solid rgba(255,255,255,.1);white-space:nowrap}
.cat-item:hover{background:linear-gradient(135deg,#1a3a8a,#c0392b)}
@media(max-width:600px){
  .game-desc h2{font-size:1.1rem}
  .game-thumb-sm{display:none}
  .cat-grid{border-radius:20px}
}
</style>'''

GAME_JS = '''<script>
/* ── PLAY BUTTON ── */
(function(){
  var overlay=document.getElementById('gameOverlay');
  var frame=document.getElementById('gameFrame');
  var thumb=document.getElementById('gameThumb');
  if(!overlay||!frame)return;
  function launch(){
    var src=frame.getAttribute('data-src');
    if(!src){console.warn('No data-src on iframe');return;}
    frame.src=src;
    frame.classList.add('active');
    overlay.style.display='none';
    if(thumb)thumb.style.display='none';
  }
  overlay.addEventListener('click',launch);
  overlay.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' ')launch();});
})();

/* ── FULLSCREEN ── */
document.getElementById('fsBtn')?.addEventListener('click',function(){
  var el=document.getElementById('gameFrameWrap');
  (el.requestFullscreen||el.webkitRequestFullscreen||el.mozRequestFullScreen||
   function(){}).call(el);
});
</script>'''

def similar_section(current, all_g, count=12):
    """Pick similar games, exclude current, nearby alphabetically."""
    others = [g for g in all_g if g != current]
    idx = next((i for i,g in enumerate(others) if g >= current), 0)
    # take some before + after + wrap
    picks = (others[max(0,idx-2):idx+count] + others[:3])
    seen, final = set(), []
    for g in picks:
        if g not in seen:
            seen.add(g); final.append(g)
        if len(final) == count: break
    cards = "\n    ".join(
        f'<a class="game-card" href="/{g}">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{slug_to_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{slug_to_title(g)} Unblocked</span></a>'
        for g in final
    )
    return f'''<section class="similar-section">
  <h2 class="section-heading">🎮 Similar Games</h2>
  <div class="games-grid">
    {cards}
  </div>
</section>'''

def build_game_page(slug, iframe_src, cats, all_g, desc=""):
    title    = slug_to_title(slug)
    cat_tags = "\n    ".join(
        f'<a href="/categ/{c}" class="cat-tag">{CATS[c]}</a>'
        for c in cats if c in CATS
    ) or '<a href="/categ/action" class="cat-tag">💥 Action</a>'
    cat_items = "\n      ".join(
        f'<a href="/categ/{k}" class="cat-item">{v}</a>'
        for k,v in CATS.items()
    )
    if not iframe_src:
        iframe_src = f"https://iframe.unblocked-76-games.org/{slug}"
    desc_clean = re.sub(r'Unblocked\s*—\s*Free\s*2[^.]*\.?','',desc).strip()
    desc_short = desc_clean or f"Play {title} free in your browser — no download needed!"
    sim = similar_section(slug, all_g)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} Unblocked – Play Free Online | Unblocked Games USA</title>
<meta name="description" content="Play {title} unblocked online for free. {desc_short} Works at school instantly.">
<link rel="canonical" href="{BASE_URL}/{slug}">
<meta property="og:title" content="{title} Unblocked – Free Online">
<meta property="og:description" content="Play {title} free, no download, works at school.">
<meta property="og:url" content="{BASE_URL}/{slug}">
<meta property="og:image" content="{IMG_BASE}/{slug}.png">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow,max-image-preview:large">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"VideoGame",
"name":"{title}","url":"{BASE_URL}/{slug}",
"description":"{desc_short}",
"applicationCategory":"Game","operatingSystem":"Web Browser",
"offers":{{"@type":"Offer","price":"0","priceCurrency":"USD"}},
"image":"{IMG_BASE}/{slug}.png",
"provider":{{"@type":"Organization","name":"Unblocked Games USA","url":"{BASE_URL}/"}}}}</script>
<link rel="icon" href="/favicon.ico">
{GAME_CSS}
</head>
<body>

{nav_html(depth=1)}

<div class="wrap game-section">

  <div class="game-title-bar">
    <h1>{title} Unblocked</h1>
    <p>{desc_short}</p>
  </div>

  <div class="game-frame-wrap" id="gameFrameWrap">
    <img id="gameThumb" class="game-thumb"
         src="{IMG_BASE}/{slug}.png"
         alt="{title} preview">
    <div id="gameOverlay" class="game-overlay" role="button" tabindex="0"
         aria-label="Play {title}">
      <button class="play-btn" tabindex="-1">&#9654;</button>
      <span class="play-label">PLAY NOW</span>
    </div>
    <iframe id="gameFrame" class="game-frame"
            src="about:blank"
            data-src="{iframe_src}"
            title="{title} Unblocked Game"
            allowfullscreen
            allow="autoplay; fullscreen; pointer-lock; gamepad"></iframe>
    <button id="fsBtn" class="fs-btn" aria-label="Fullscreen">⛶ Fullscreen</button>
  </div>

  <div class="game-desc">
    <img src="{IMG_BASE}/{slug}.png" alt="{title}" class="game-thumb-sm" loading="lazy">
    <h2>About {title}</h2>
    <p>{desc_short}</p>
    <h3>How to Play</h3>
    <p>Use your mouse or keyboard to play. Click the Play button above to start instantly — no download needed!</p>
    <div class="cat-tags" style="clear:both">
      {cat_tags}
    </div>
  </div>

  {sim}

  <div class="browse-section">
    <h2 class="section-heading">🗂️ Browse by Category</h2>
    <div class="cat-grid">
      {cat_items}
    </div>
  </div>

</div>

{footer_html(depth=1)}

{SHARED_JS}
{GAME_JS}

</body>
</html>'''

# ── CATEGORY PAGE ─────────────────────────────────────────────────────────────

CATEG_CSS = SHARED_CSS + '''<style>
.categ-hero{text-align:center;padding:32px 16px 16px}
.categ-hero h1{font-size:clamp(1.5rem,4vw,2.4rem);font-weight:800;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.categ-hero p{color:rgba(255,255,255,.55);margin-top:8px}
.pagination{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:28px 0}
.pagination a{padding:7px 15px;background:#111827;color:#dce8ff;border-radius:8px;
  font-weight:600;font-size:.9rem;border:1px solid rgba(255,255,255,.08)}
.pagination a:hover{background:#1a2a4a;border-color:rgba(192,57,43,.4)}
.pagination a.cur{background:#c0392b;color:#fff;border-color:#c0392b}
.other-cats-section{margin:36px 0 0}
.other-cats-section h2{font-size:1.1rem;font-weight:700;color:#4fa3ff;margin-bottom:12px}
.other-cats-section div{display:flex;flex-wrap:wrap;gap:8px}
.other-cats-section a{background:#111827;padding:6px 13px;border-radius:16px;
  font-size:.82rem;border:1px solid rgba(255,255,255,.07)}
.other-cats-section a:hover{background:#1a2a4a}
</style>'''

def page_url(cat_slug, p):
    if p == 1: return f"/categ/{cat_slug}/"
    return f"/categ/{cat_slug}-page-{p}/"

def build_categ_page(cat_slug, cat_label, games_on_page, page_num, total_pages, total_count):
    cards = "\n    ".join(
        f'<a class="game-card" href="/{g}">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{slug_to_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{slug_to_title(g)} Unblocked</span></a>'
        for g in games_on_page
    )

    pag = ""
    if page_num > 1:
        pag += f'<a href="{page_url(cat_slug, page_num-1)}">&laquo; Prev</a>'
    for p in range(1, total_pages+1):
        cls = ' class="cur"' if p == page_num else ''
        pag += f'<a href="{page_url(cat_slug, p)}"{cls}>{p}</a>'
    if page_num < total_pages:
        pag += f'<a href="{page_url(cat_slug, page_num+1)}">Next &raquo;</a>'

    others = " ".join(
        f'<a href="/categ/{k}">{v}</a>'
        for k,v in CATS.items() if k != cat_slug
    )
    page_suffix = f" – Page {page_num}" if page_num > 1 else ""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cat_label} Games Unblocked{page_suffix} – Free Online | Unblocked Games USA</title>
<meta name="description" content="Play {total_count} free unblocked {cat_label} games online. No downloads, works at school instantly.">
<link rel="canonical" href="{BASE_URL}{page_url(cat_slug, page_num)}">
<meta name="robots" content="index,follow">
{CATEG_CSS}
</head>
<body>

{nav_html(depth=0)}

<div class="wrap">
  <div class="categ-hero">
    <h1>{cat_label} Unblocked Games</h1>
    <p>{total_count} free games — play instantly, no downloads needed</p>
  </div>

  <div class="games-grid">
    {cards}
  </div>

  <div class="pagination">{pag}</div>

  <div class="other-cats-section">
    <h2>🎮 Other Categories</h2>
    <div>{others}</div>
  </div>
</div>

{footer_html(depth=0)}

{SHARED_JS}

</body>
</html>'''

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    games = all_games()
    print(f"Found {len(games)} game directories")

    # Build category → games map
    print("Scanning category tags in existing pages…")
    cat_map = {k: [] for k in CATS}
    game_data = {}

    for slug in games:
        html = read_html(REPO / slug / "index.html")
        iframe = get_iframe_src(html)
        cats   = get_game_cats(html)
        desc   = get_description(html)
        game_data[slug] = {"iframe": iframe, "cats": cats, "desc": desc}
        for c in cats:
            if c in cat_map and slug not in cat_map[c]:
                cat_map[c].append(slug)

    # Games with no category detected → put in action as fallback
    no_cat = [s for s in games if not game_data[s]["cats"]]
    print(f"  {len(no_cat)} games have no detected category → assigned to 'action'")
    for s in no_cat:
        game_data[s]["cats"] = ["action"]
        if s not in cat_map["action"]:
            cat_map["action"].append(s)

    for k,v in cat_map.items():
        print(f"  {CATS[k]}: {len(v)} games")

    # ── Fix game pages ──
    print(f"\nWriting {len(games)} game pages…")
    for i, slug in enumerate(games):
        d = game_data[slug]
        html = build_game_page(slug, d["iframe"], d["cats"], games, d["desc"])
        (REPO / slug / "index.html").write_text(html, encoding="utf-8")
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{len(games)}")
    print(f"  Done — {len(games)} game pages written")

    # ── Fix category pages ──
    print("\nWriting category pages…")
    categ_root = REPO / "categ"
    categ_root.mkdir(exist_ok=True)

    for cat_slug, cat_label in CATS.items():
        cat_games = cat_map[cat_slug]
        if not cat_games:
            print(f"  SKIP {cat_label} (0 games)")
            continue
        total = len(cat_games)
        n_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
        for p in range(1, n_pages+1):
            chunk = cat_games[(p-1)*PER_PAGE : p*PER_PAGE]
            folder = categ_root / (cat_slug if p==1 else f"{cat_slug}-page-{p}")
            folder.mkdir(parents=True, exist_ok=True)
            html = build_categ_page(cat_slug, cat_label, chunk, p, n_pages, total)
            (folder / "index.html").write_text(html, encoding="utf-8")
        print(f"  {cat_label}: {total} games, {n_pages} page(s)")

    print("""
✅ All done!

Next steps:
  git add -A
  git commit -m "Rebuild: unified nav/footer, game launch fixed, clean titles, correct category pages"
  git push
""")

if __name__ == "__main__":
    main()