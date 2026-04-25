#!/usr/bin/env python3
"""
Fix script for UnblockedGames-USA.github.io
Run from the repo root: python fix_site.py
"""
import os, re, json, sys, shutil
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────
REPO = Path(__file__).parent  # run from repo root
BASE_URL = "https://unblockedgames-usa.github.io"
IMAGES_BASE = f"{BASE_URL}/images"
PER_PAGE = 50

CATEGORIES = {
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

NAV_LINKS = "\n".join(
    f'        <li><a href="/categ/{k}">{v}</a></li>'
    for k, v in CATEGORIES.items()
)

FOOTER_CATS = " ".join(
    f'<a href="/categ/{k}" style="background:rgba(255,255,255,.08);padding:5px 11px;border-radius:16px;font-size:.8rem;color:#e6edf3;text-decoration:none">{v}</a>'
    for k, v in CATEGORIES.items()
)

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def slug_to_title(slug):
    return " ".join(w.capitalize() for w in slug.replace("-", " ").split())

def get_game_iframe_src(game_dir):
    """Read existing index.html and extract the real iframe src."""
    idx = game_dir / "index.html"
    if not idx.exists():
        return None
    html = idx.read_text(encoding="utf-8", errors="ignore")
    # Try data-src first (lazy load pattern)
    m = re.search(r'data-src=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    # Try direct src on iframe (not about:blank)
    m = re.search(r'<iframe[^>]+src=["\'](?!about:blank)([^"\']+)["\']', html)
    if m:
        return m.group(1)
    return None

def get_game_categories(game_dir):
    """Extract categories from existing index.html category tags."""
    idx = game_dir / "index.html"
    if not idx.exists():
        return []
    html = idx.read_text(encoding="utf-8", errors="ignore")
    # Look for category-tag-item links
    cats = re.findall(r'href=["\'](?:/categ/|../../categ/)([^/"\']+)["\']', html)
    # Deduplicate and filter to known categories
    seen = set()
    result = []
    for c in cats:
        c = c.strip("/")
        if c in CATEGORIES and c not in seen:
            seen.add(c)
            result.append(c)
    return result

def get_game_description(game_dir):
    """Extract about/description text from existing index.html."""
    idx = game_dir / "index.html"
    if not idx.exists():
        return ""
    html = idx.read_text(encoding="utf-8", errors="ignore")
    # Try to get the description meta tag
    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if m:
        return m.group(1)
    return ""

def get_all_games():
    """Return list of game slugs (directories with index.html, not categ/assets etc)."""
    skip = {"categ", "assets", ".git", "images", "privacy-policy", "contact", "faq", "dmca"}
    games = []
    for d in sorted(REPO.iterdir()):
        if d.is_dir() and d.name not in skip and not d.name.startswith("."):
            if (d / "index.html").exists():
                games.append(d.name)
    return games

def make_game_card_html(slug, href_prefix="../"):
    title = slug_to_title(slug) + " Unblocked — Free 2"
    return (
        f'    <a class="game-card" href="{href_prefix}{slug}">\n'
        f'      <img src="{IMAGES_BASE}/{slug}.png" alt="{title}" loading="lazy">\n'
        f'      <span>{title}</span>\n'
        f'    </a>'
    )

def make_similar_games_html(current_slug, all_games, count=12):
    """Pick similar games excluding the current one."""
    import random
    others = [g for g in all_games if g != current_slug]
    # Try to pick some near alphabetically for consistency, plus some random
    idx = others.index(current_slug) if current_slug in others else 0
    near = others[max(0, idx-3):idx+10]
    picks = (near + others)[:count]
    # Deduplicate
    seen = set()
    final = []
    for g in picks:
        if g not in seen:
            seen.add(g)
            final.append(g)
    final = final[:count]
    cards = "\n".join(make_game_card_html(g) for g in final)
    return f'''<section class="similar-games">
  <h2 class="section-title">🎮 Similar Games</h2>
  <div class="games-grid">
{cards}
  </div>
</section>'''

def make_nav_html():
    return f'''<header>
  <div class="container header-content">
    <a href="/" class="logo">🎮 Unblocked Games USA</a>
    <div class="search-bar">
      <input type="text" id="searchInput" placeholder="Search games..." autocomplete="off" aria-label="Search games">
      <button id="searchBtn" aria-label="Search"><i class="fas fa-search"></i></button>
      <div id="searchDropdown"></div>
    </div>
    <nav class="main-nav" aria-label="Game categories">
      <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation">
        <i class="fas fa-bars"></i>
      </button>
      <ul id="navMenu">
{NAV_LINKS}
      </ul>
    </nav>
  </div>
</header>'''

def make_footer_html():
    return f'''<footer>
  <div class="container">
    <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:14px">
      {FOOTER_CATS}
    </div>
    <div class="footer-bottom">
      <p>&copy; <span id="currentYear"></span> Unblocked Games USA. All rights reserved.</p>
      <div class="footer-links">
        <a href="/privacy-policy">Privacy Policy</a>
        <a href="/contact">Contact Us</a>
        <a href="/faq">FAQ</a>
        <a href="/dmca">DMCA</a>
      </div>
    </div>
  </div>
</footer>'''

# ─── GAME PAGE TEMPLATE ────────────────────────────────────────────────────────

GAME_PAGE_CSS = '''<style>
:root{--red:#E8192C;--blue:#002868;--blue-mid:#1a3a8a;--blue-light:#2655cc;
  --white:#fff;--card-bg:#07102b;--border:rgba(255,255,255,.08);--text:#dce8ff;
  --grad:linear-gradient(135deg,var(--blue) 0%,var(--blue-light) 50%,var(--red) 100%);}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Barlow',sans-serif;background:#000510;color:var(--text);min-height:100vh;line-height:1.6}
.container{width:100%;max-width:1200px;margin:0 auto;padding:0 16px;position:relative}
header{background:linear-gradient(90deg,var(--blue) 0%,#0d1f5c 40%,#1a0a2e 60%,var(--red) 100%);
  border-bottom:3px solid var(--red);position:sticky;top:0;z-index:100;
  box-shadow:0 4px 30px rgba(0,0,0,.6)}
.header-content{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:10px 0}
.logo{font-family:'Bebas Neue',sans-serif;font-size:1.9rem;letter-spacing:2px;color:var(--white);
  text-decoration:none;text-shadow:0 0 20px rgba(232,25,44,.6)}
.search-bar{display:flex;position:relative}
.search-bar input{padding:.45rem 1rem;border:1px solid var(--border);border-radius:50px 0 0 50px;
  outline:none;background:rgba(255,255,255,.12);color:white;font-size:.9rem;width:190px}
.search-bar input::placeholder{color:rgba(255,255,255,.5)}
.search-bar button{background:var(--red);color:white;border:none;padding:.45rem 1rem;
  border-radius:0 50px 50px 0;cursor:pointer;font-size:.95rem}
#searchDropdown{position:absolute;top:calc(100% + 6px);left:0;right:0;background:#0a1535;
  border:1px solid rgba(232,25,44,.3);border-radius:12px;max-height:300px;overflow-y:auto;
  z-index:200;display:none;box-shadow:0 8px 32px rgba(0,0,0,.7)}
#searchDropdown.open{display:block}
#searchDropdown a{display:flex;align-items:center;gap:10px;padding:8px 12px;text-decoration:none;
  color:var(--text);border-bottom:1px solid var(--border);font-size:.88rem;font-weight:600}
#searchDropdown a:hover{background:rgba(232,25,44,.18);color:white}
#searchDropdown img{width:38px;height:28px;object-fit:cover;border-radius:5px;flex-shrink:0}
#searchDropdown .no-results{padding:12px;color:rgba(255,255,255,.45);text-align:center}
.main-nav{order:1;width:100%}
.nav-toggle{display:none;background:none;border:none;color:white;font-size:1.5rem;cursor:pointer;padding:.5rem}
.main-nav ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;gap:4px;
  padding:10px 24px;margin:6px 0 8px;
  background:linear-gradient(135deg,#001a5e 0%,#0d1f6e 40%,#1a0a2e 70%,#4a0a14 100%);
  border-radius:50px;border:2px solid rgba(255,255,255,.75);
  box-shadow:0 0 0 4px rgba(0,40,104,.5),0 6px 28px rgba(0,0,0,.8)}
.main-nav a{color:rgba(255,255,255,.88);text-decoration:none;padding:4px 12px;border-radius:50px;
  font-size:.82rem;font-weight:600;transition:background .2s,color .2s;border:1px solid transparent;white-space:nowrap}
.main-nav a:hover{background:rgba(232,25,44,.35);color:white}
.game-header{background:linear-gradient(135deg,rgba(0,20,80,.95),rgba(10,5,30,.9),rgba(100,10,20,.95));
  border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:1.4rem 2rem;
  margin:1.2rem 0;text-align:center}
.game-header h1{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;letter-spacing:3px;
  background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;margin-bottom:.3rem}
.game-header p{color:rgba(255,255,255,.75);max-width:800px;margin:0 auto}
/* GAME FRAME */
.game-container{background:var(--card-bg);border-radius:10px;padding:1.5rem;
  margin:1.5rem 0;border:1px solid var(--border)}
.game-frame-wrapper{position:relative;width:100%;padding-bottom:56.25%;
  overflow:hidden;border-radius:8px;background:#000}
/* OVERLAY (click to play) */
.game-overlay{position:absolute;inset:0;display:flex;flex-direction:column;
  justify-content:center;align-items:center;z-index:5;border-radius:8px;cursor:pointer;
  background:rgba(0,5,20,.5);backdrop-filter:blur(4px);transition:opacity .3s}
.game-overlay.hidden{display:none}
.game-thumb{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  border-radius:8px;z-index:3}
.play-button{background:linear-gradient(135deg,var(--blue),var(--red));color:white;
  border:none;width:80px;height:80px;border-radius:50%;font-size:2.5rem;cursor:pointer;
  display:flex;justify-content:center;align-items:center;padding-left:5px;
  box-shadow:0 0 0 0 rgba(232,25,44,.7);animation:pulse 2s infinite;z-index:6}
.play-button:hover{transform:scale(1.1)}
.play-text{margin-top:1.2rem;color:white;font-family:'Bebas Neue',sans-serif;
  font-size:1.2rem;letter-spacing:2px;background:rgba(0,0,0,.5);
  padding:.4rem 1.4rem;border-radius:50px;z-index:6}
.game-frame{position:absolute;inset:0;width:100%;height:100%;border:none;display:none}
.game-frame.active{display:block}
.fullscreen-btn{position:absolute;bottom:12px;right:12px;background:rgba(0,0,0,.7);
  color:white;border:none;padding:.45rem .9rem;border-radius:4px;cursor:pointer;
  z-index:10;display:flex;align-items:center;gap:.4rem;font-size:.85rem}
.fullscreen-btn:hover{background:var(--red)}
/* DESCRIPTION */
.game-description{background:var(--card-bg);padding:2rem;border-radius:10px;
  margin:1.5rem 0;border:1px solid var(--border)}
.game-description h2{font-family:'Bebas Neue',sans-serif;color:var(--red);
  margin-bottom:1rem;font-size:1.6rem;letter-spacing:1px}
.game-description h3{font-family:'Bebas Neue',sans-serif;color:var(--red);
  margin-top:1.2rem;margin-bottom:.6rem;letter-spacing:1px;font-size:1.2rem}
.game-description p{margin-bottom:.9rem}
.game-description ul{list-style:none;padding-left:1rem}
.game-description li{margin-bottom:.5rem;padding-left:1.5rem;position:relative}
.game-description li::before{content:"▶";color:var(--red);position:absolute;left:0}
.game-description-image{width:100%;max-width:140px;float:left;margin:6px 18px 10px 0;
  border-radius:8px;border:1px solid var(--border)}
.game-category-tags{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem}
.category-tag-item{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(232,25,44,.6));
  color:white;border-radius:50px;border:1px solid rgba(255,255,255,.12);
  padding:.35rem .9rem;text-decoration:none;font-weight:600;font-size:.85rem}
.category-tag-item:hover{background:linear-gradient(135deg,#1a3a8a,#E8192C)}
/* SIMILAR GAMES */
.similar-games{margin:2rem 0}
.section-title,.categories-title{font-family:'Bebas Neue',sans-serif;letter-spacing:2px;
  font-size:1.8rem;text-align:center;margin:1.5rem 0 1rem;
  background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.games-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin-bottom:2rem}
@media(max-width:1100px){.games-grid{grid-template-columns:repeat(4,1fr)}}
@media(max-width:860px){.games-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:600px){.games-grid{grid-template-columns:repeat(2,1fr)}}
.game-card{background:var(--card-bg);border-radius:10px;overflow:hidden;
  border:1px solid var(--border);transition:transform .25s,box-shadow .25s,border-color .25s;
  text-decoration:none;color:inherit;display:block}
.game-card:hover{transform:translateY(-6px);box-shadow:0 12px 35px rgba(0,0,0,.5);
  border-color:rgba(232,25,44,.4)}
.game-card img{width:100%;height:150px;object-fit:cover;display:block}
.game-card span{display:block;padding:8px 10px;text-align:center;font-size:.88rem;font-weight:600}
/* CATEGORIES BAR */
.categories{margin:2rem 0}
.category-grid{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:18px 24px;
  background:linear-gradient(135deg,#0a1a4a,#1a0a2e,#3a0a10);
  border-radius:60px;border:1px solid rgba(232,25,44,.25)}
.category-item{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(232,25,44,.6));
  color:white;border-radius:50px;padding:.4rem 1rem;text-decoration:none;
  font-weight:600;font-size:.88rem;white-space:nowrap}
.category-item:hover{background:linear-gradient(135deg,#1a3a8a,#E8192C)}
/* FOOTER */
footer{background:#010812;color:white;padding:1.5rem 0;margin-top:2rem;border-top:2px solid var(--red)}
.footer-bottom{text-align:center;font-size:.82rem}
.footer-links{display:flex;justify-content:center;gap:1.2rem;margin-top:.5rem;flex-wrap:wrap}
.footer-links a{color:white;text-decoration:none}
/* SCROLL TOP */
#scrollToTopBtn{position:fixed;bottom:20px;right:22px;z-index:99;border:none;
  background:linear-gradient(135deg,var(--blue),var(--red));color:white;cursor:pointer;
  border-radius:50%;width:46px;height:46px;opacity:0;visibility:hidden;
  display:flex;align-items:center;justify-content:center;transition:opacity .3s,visibility .3s}
#scrollToTopBtn.show{opacity:1;visibility:visible}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(232,25,44,.7)}70%{box-shadow:0 0 0 20px rgba(232,25,44,0)}100%{box-shadow:0 0 0 0 rgba(232,25,44,0)}}
@media(max-width:992px){
  .nav-toggle{display:block}
  .main-nav ul{display:none;flex-direction:column;border-radius:20px;padding:10px 16px}
  .main-nav ul.active{display:flex}
}
@media(max-width:768px){
  .header-content{flex-direction:column;align-items:stretch}
  .category-grid{border-radius:24px;padding:14px 16px}
  .game-frame-wrapper{padding-bottom:60%}
}
</style>'''

GAME_PAGE_JS = '''<script>
/* SEARCH */
(function(){
  const inp=document.getElementById('searchInput');
  const dd=document.getElementById('searchDropdown');
  const btn=document.getElementById('searchBtn');
  function norm(s){return s.toLowerCase().replace(/[^a-z0-9]/g,'');}
  function closeDD(){dd.classList.remove('open');dd.innerHTML='';}
  function go(q){q=q.trim();if(!q)return;window.location.href='/?q='+encodeURIComponent(q);closeDD();}
  inp?.addEventListener('input',function(){
    const q=this.value.trim();
    if(!q){closeDD();return;}
    dd.innerHTML=`<div class="no-results"><a href="/?q=${encodeURIComponent(q)}" style="color:var(--red)">Search all games for "${q}"</a></div>`;
    dd.classList.add('open');
  });
  inp?.addEventListener('keydown',e=>{if(e.key==='Enter')go(inp.value);if(e.key==='Escape')closeDD();});
  btn?.addEventListener('click',()=>go(inp.value));
  document.addEventListener('click',e=>{if(!e.target.closest('.search-bar'))closeDD();});
})();

/* PLAY BUTTON - click overlay to load iframe */
document.addEventListener('DOMContentLoaded',function(){
  const overlay=document.getElementById('gameOverlay');
  const frame=document.getElementById('gameFrame');
  const wrapper=document.getElementById('gameFrameWrapper');
  const fsBtn=document.getElementById('fullscreenBtn');

  if(overlay && frame){
    overlay.addEventListener('click',function(){
      // Load the iframe
      frame.src=frame.dataset.src;
      frame.classList.add('active');
      // Hide overlay
      overlay.classList.add('hidden');
    });
  }

  // Fullscreen
  fsBtn?.addEventListener('click',function(){
    const el=wrapper||frame;
    (el.requestFullscreen||el.webkitRequestFullscreen||el.mozRequestFullScreen||function(){}).call(el);
  });

  // Nav toggle
  document.getElementById('navToggle')?.addEventListener('click',()=>
    document.getElementById('navMenu')?.classList.toggle('active'));

  // Scroll to top
  const stb=document.getElementById('scrollToTopBtn');
  window.addEventListener('scroll',()=>{
    if(stb)stb.classList.toggle('show',window.pageYOffset>100);
  });
  stb?.addEventListener('click',e=>{e.preventDefault();window.scrollTo({top:0,behavior:'smooth'});});

  // Year
  const yr=document.getElementById('currentYear');
  if(yr)yr.textContent=new Date().getFullYear();
});
</script>'''

def make_game_page(slug, iframe_src, cats, all_games, description=""):
    title = slug_to_title(slug)
    cat_tags = "\n      ".join(
        f'<a href="/categ/{c}" class="category-tag-item">{CATEGORIES[c]}</a>'
        for c in cats if c in CATEGORIES
    ) or f'<a href="/categ/action" class="category-tag-item">💥 Action</a>'

    cat_items = "\n      ".join(
        f'<a href="/categ/{k}" class="category-item">{v}</a>'
        for k, v in CATEGORIES.items()
    )

    if not iframe_src:
        iframe_src = f"https://iframe.unblocked-76-games.org/{slug}"

    similar_html = make_similar_games_html(slug, all_games)
    desc_short = description or f"{title} is a fun unblocked game. Play it instantly at school!"

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} Unblocked — Free Online | Unblocked Games USA</title>
<meta name="description" content="Play {title} unblocked free! {desc_short} No download needed.">
<link rel="canonical" href="{BASE_URL}/{slug}">
<meta property="og:title" content="{title} Unblocked — Free Online">
<meta property="og:description" content="Play {title} free, no download, works at school!">
<meta property="og:url" content="{BASE_URL}/{slug}">
<meta property="og:image" content="{IMAGES_BASE}/{slug}.png">
<meta property="og:type" content="website">
<link rel="icon" href="/favicon.ico" type="image/x-icon">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
{GAME_PAGE_CSS}
</head>
<body>

{make_nav_html()}

<div class="container">

  <div class="game-header">
    <h1>{title} Unblocked</h1>
    <p>{desc_short}</p>
  </div>

  <div class="game-container">
    <div class="game-frame-wrapper" id="gameFrameWrapper">

      <!-- Thumbnail shown until user clicks play -->
      <img src="{IMAGES_BASE}/{slug}.png" alt="{title} preview" class="game-thumb" id="gameThumb">

      <!-- Click overlay -->
      <div class="game-overlay" id="gameOverlay" role="button" tabindex="0" aria-label="Play {title}">
        <button class="play-button" aria-label="Play">&#9654;</button>
        <div class="play-text">CLICK TO PLAY</div>
      </div>

      <!-- Iframe loads only after click -->
      <iframe class="game-frame" id="gameFrame"
              src="about:blank"
              data-src="{iframe_src}"
              title="{title} Unblocked Game"
              allowfullscreen
              allow="autoplay; fullscreen; pointer-lock"></iframe>

      <button class="fullscreen-btn" id="fullscreenBtn">
        <i class="fas fa-expand"></i> Fullscreen
      </button>
    </div>
  </div>

  <div class="game-description">
    <img src="{IMAGES_BASE}/{slug}.png" alt="{title} gameplay" class="game-description-image" loading="lazy">
    <h2>About {title}</h2>
    <p>{desc_short}</p>
    <h3>How to Play</h3>
    <p>Use your mouse or keyboard to play {title}. Have fun!</p>
    <div class="game-category-tags">
      {cat_tags}
    </div>
  </div>

  {similar_html}

  <div class="categories">
    <h2 class="categories-title">🎮 Browse by Category</h2>
    <div class="category-grid">
      {cat_items}
    </div>
  </div>

</div>

{make_footer_html()}

<button id="scrollToTopBtn" title="Go to top" aria-label="Scroll to top">
  <i class="fas fa-arrow-up"></i>
</button>

{GAME_PAGE_JS}

</body>
</html>'''

# ─── CATEGORY PAGE TEMPLATE ────────────────────────────────────────────────────

CATEG_CSS = '''<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif}
a{color:inherit;text-decoration:none}
nav{background:linear-gradient(90deg,#1a0533,#8b0000);padding:10px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.nav-logo{color:#fff;font-weight:700;font-size:1rem}
.nav-links{display:flex;list-style:none;gap:6px;flex-wrap:wrap;flex:1;margin:0;padding:0}
.nav-links a{background:rgba(255,255,255,.1);padding:4px 10px;border-radius:20px;font-size:.8rem;color:#fff;display:inline-block}
.nav-links a:hover{background:rgba(255,255,255,.25)}
.search-form{display:flex;gap:6px;margin-left:auto}
.search-form input{padding:5px 12px;border-radius:20px 0 0 20px;border:none;background:rgba(255,255,255,.15);color:#fff;width:160px}
.search-form button{background:#c0392b;color:#fff;border:none;border-radius:0 20px 20px 0;padding:5px 12px;cursor:pointer}
main{max-width:1280px;margin:0 auto;padding:24px 16px}
h1{font-size:1.7rem;margin-bottom:6px}
.subtitle{color:#8b949e;margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:20px 0}
.gc{display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:9px;overflow:hidden;transition:transform .15s}
.gc:hover{transform:translateY(-3px)}
.gc img{width:100%;height:110px;object-fit:cover}
.gc span{padding:7px 5px;font-size:.8rem;text-align:center}
.pagination{display:flex;gap:8px;justify-content:center;margin:24px 0;flex-wrap:wrap}
.pagination a{padding:7px 14px;background:#161b22;color:#e6edf3;border-radius:6px}
.pagination a.active{background:#58a6ff;color:#000}
.other-cats h2{font-size:1.1rem;color:#58a6ff;margin:28px 0 14px}
.other-cats div{display:flex;flex-wrap:wrap;gap:8px}
.other-cats a{background:#21262d;padding:6px 12px;border-radius:16px;font-size:.82rem}
footer{background:#161b22;padding:28px 20px;margin-top:40px;text-align:center}
.footer-cats{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:14px}
.footer-cats a{background:rgba(255,255,255,.08);padding:5px 11px;border-radius:16px;font-size:.8rem}
.footer-meta{display:flex;gap:14px;justify-content:center;margin-bottom:10px;font-size:.83rem;opacity:.7}
.footer-meta a{color:#e6edf3}
.footer-copy{font-size:.78rem;opacity:.45}
</style>'''

def make_categ_nav():
    links = "\n    ".join(
        f'<li><a href="../../categ/{k}">{v}</a></li>'
        for k, v in CATEGORIES.items()
    )
    return f'''<nav>
  <a href="../../" class="nav-logo">🎮 Unblocked Games USA</a>
  <ul class="nav-links">
    {links}
  </ul>
  <form class="search-form" onsubmit="event.preventDefault();window.location='../../?q='+encodeURIComponent(this.q.value)">
    <input name="q" type="search" placeholder="Search games…">
    <button type="submit">🔍</button>
  </form>
</nav>'''

def make_categ_footer():
    cats = " ".join(
        f'<a href="../../categ/{k}">{v}</a>'
        for k, v in CATEGORIES.items()
    )
    return f'''<footer>
  <div class="footer-cats">{cats}</div>
  <div class="footer-meta">
    <a href="../../privacy-policy">Privacy Policy</a>
    <a href="../../contact">Contact Us</a>
    <a href="../../faq">FAQ</a>
    <a href="../../dmca">DMCA</a>
  </div>
  <p class="footer-copy">&copy; Unblocked Games USA. All rights reserved.</p>
</footer>'''

def make_categ_page(cat_slug, cat_label, games_on_page, page_num, total_pages, total_count):
    """Generate one category page."""
    cards = "\n ".join(
        f'<a class="gc" href="../../{g}"><img src="{IMAGES_BASE}/{g}.png" alt="{slug_to_title(g)} Unblocked" loading="lazy" width="150" height="110"><span>{slug_to_title(g)} Unblocked — Free 2</span></a>'
        for g in games_on_page
    )

    # Pagination
    def page_url(p):
        if p == 1:
            return f"../../categ/{cat_slug}/"
        return f"../../categ/{cat_slug}-page-{p}/"

    pag_items = ""
    if page_num > 1:
        pag_items += f'<a href="{page_url(page_num-1)}">&laquo; Prev</a>'
    for p in range(1, total_pages + 1):
        cls = ' class="active"' if p == page_num else ''
        pag_items += f'<a href="{page_url(p)}"{cls}>{p}</a>'
    if page_num < total_pages:
        pag_items += f'<a href="{page_url(page_num+1)}">Next &raquo;</a>'

    other_cats = " ".join(
        f'<a href="../../categ/{k}">{v}</a>'
        for k, v in CATEGORIES.items() if k != cat_slug
    )

    page_title = f"Page {page_num} — " if page_num > 1 else ""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}{cat_label} Games Unblocked – Free Online</title>
<meta name="description" content="Play {total_count} free unblocked {cat_label} games. No downloads needed.">
<link rel="canonical" href="{BASE_URL}/categ/{cat_slug}{'-page-'+str(page_num) if page_num>1 else ''}/"> 
{CATEG_CSS}
</head>
<body>
{make_categ_nav()}
<main>
  <h1>{cat_label} Games</h1>
  <p class="subtitle">{total_count} free unblocked {cat_label} games — play instantly, no downloads!</p>
  <div class="grid">
    {cards}
  </div>
  <div class="pagination">{pag_items}</div>
  <div class="other-cats">
    <h2>🎮 Other Categories</h2>
    <div>{other_cats}</div>
  </div>
</main>
{make_categ_footer()}
</body>
</html>'''

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    all_games = get_all_games()
    print(f"Found {len(all_games)} game directories")

    # Build category → game list mapping by reading existing pages
    print("Building category map from existing game pages...")
    cat_to_games = {k: [] for k in CATEGORIES}

    for slug in all_games:
        game_dir = REPO / slug
        cats = get_game_categories(game_dir)
        if not cats:
            # Default fallback if we can't detect
            cats = ["action"]
        for c in cats:
            if c in cat_to_games:
                if slug not in cat_to_games[c]:
                    cat_to_games[c].append(slug)

    for cat, games in cat_to_games.items():
        print(f"  {cat}: {len(games)} games")

    # Fix game pages
    print("\nFixing game pages...")
    fixed = 0
    for slug in all_games:
        game_dir = REPO / slug
        idx = game_dir / "index.html"

        iframe_src = get_game_iframe_src(game_dir)
        cats = get_game_categories(game_dir) or ["action"]
        description = get_game_description(game_dir)

        new_html = make_game_page(slug, iframe_src, cats, all_games, description)
        idx.write_text(new_html, encoding="utf-8")
        fixed += 1
        if fixed % 50 == 0:
            print(f"  Fixed {fixed}/{len(all_games)}...")

    print(f"  Fixed {fixed} game pages")

    # Fix/rebuild category pages
    print("\nRebuilding category pages...")
    categ_root = REPO / "categ"
    categ_root.mkdir(exist_ok=True)

    for cat_slug, cat_label in CATEGORIES.items():
        games = cat_to_games[cat_slug]
        if not games:
            print(f"  WARNING: No games found for category '{cat_slug}', skipping")
            continue

        total = len(games)
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * PER_PAGE
            end = start + PER_PAGE
            games_on_page = games[start:end]

            if page_num == 1:
                out_dir = categ_root / cat_slug
            else:
                out_dir = categ_root / f"{cat_slug}-page-{page_num}"

            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "index.html"
            html = make_categ_page(cat_slug, cat_label, games_on_page, page_num, total_pages, total)
            out_file.write_text(html, encoding="utf-8")

        print(f"  {cat_label}: {total} games → {total_pages} page(s)")

    print("\n✅ Done! All game pages and category pages have been fixed.")
    print("Now commit and push:")
    print("  git add -A && git commit -m 'Fix: clean game pages, deduplicated similar games, correct category pages' && git push")

if __name__ == "__main__":
    main()