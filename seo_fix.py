#!/usr/bin/env python3
"""
SEO Fix for UnblockedGames-USA.github.io
=========================================
What this script fixes vs competitor analysis:

COMPETITOR (incredibox-sprunki.github.io) does:
  ✅ Unique "About [Game]" paragraph per game (200+ words, rich keywords)
  ✅ Unique "How to Play [Game]" with actual controls
  ✅ Game-specific title tag: "Slope Unbanned - Skill Action Racing Game Online"
  ✅ No duplicate nav menus / "Browse by Category" only at bottom of game pages
  ✅ Clean footer (no duplicate nav menu above it)
  ✅ H1 = game name only (no "Unblocked" spam)

OUR FIXES:
  1. AI-generated unique About + How to Play per game (via Claude API)
  2. Title tag = "[Game Name] Unblocked - [Genre] Game Online | Unblocked Games USA"
  3. Remove duplicate nav/menu above footer on game pages
  4. Remove duplicate footer nav menu (keep only one clean footer)
  5. Category pages: proper H1, meta, clean structure
  6. Homepage: remove duplicate nav above footer
  7. Sitemap.xml generation
  8. robots.txt generation

Run: python seo_fix.py [--all] [--slug=slope] [--batch=50] [--resume]
"""

import os, re, json, time, argparse, random
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# ── CONFIG ────────────────────────────────────────────────────────────────────
REPO     = Path('.')
BASE_URL = 'https://unblockedgames-usa.github.io'
IMG_BASE = f'{BASE_URL}/images'
GTAG_ID  = 'G-L6FNHSMWF4'
PER_PAGE = 50
API_URL  = 'https://api.anthropic.com/v1/messages'
# No API key needed - script uses Anthropic API via claude.ai proxy if available
# Otherwise set: export ANTHROPIC_API_KEY=sk-ant-...
API_KEY  = os.environ.get('ANTHROPIC_API_KEY', '')

SKIP_DIRS = {'categ','assets','.git','images','privacy-policy','contact','faq',
             'dmca','node_modules','search','.github'}

CATS = {
    'shooter':    '🎯 Shooter',
    'platformer': '🏃 Platformer',
    '2-player':   '👥 2-Player',
    'fighting':   '🥊 Fighting',
    'driving':    '🚗 Driving',
    'puzzle':     '🧠 Puzzle',
    'multiplayer':'🌐 Multiplayer',
    'action':     '💥 Action',
    'skill':      '🏆 Skill',
    'adventure':  '🗺️ Adventure',
    'racing':     '🏁 Racing',
    'strategy':   '♟️ Strategy',
    'sports':     '⚽ Sports',
    'simulation': '🏙️ Simulation',
    'clicker':    '🖱️ Clicker',
    'horror':     '👻 Horror',
    'kids':       '🧸 Kids',
}

# Keyword-based category mapping (same as fix_all.py)
KEYWORD_RULES = [
    (['shooter','sniper','gun','bullet','shoot','swat','force','armed',
      'pixel-gun','skibidi-shooter','funny-shooter','masked-forces','leader-strike',
      'nightpoint','starblast','alien-invaders','cat-gunner','total-recoil',
      'neon-war','recoil','james-gun','shootz','cannon'],'shooter'),
    (['fancy-pants','vex-','ovo','dreadhead','parkour','flip-runner','stickman-run',
      'stickman-climb','stickman-parkour','stickman-school-run','running-fred',
      'electron-dash','subway','temple-run','rabbit-samurai','red-ball',
      'geometry-dash','color-tunnel','tunnel-rush','slope','rolly-vortex',
      'doodle-jump','bottle-flip','sling-kong','tomb-of-the-mask','ape-sling',
      'noob-hook','stickman-hook','blumgi-rocket','blumgi-slime','poor-bunny',
      'double-panda','icy-purple-head','heart-star','odd-bot-out','bob-the-robber',
      'platformer','hop','jump','run','platform'],'platformer'),
    (['2-player','duo-','thumb-fighter','drunken-duel','boxing-random',
      'volleyball-challenge','volley-random','basket-random','sumo-party',
      'tube-jumpers','rowdy-wrestling','getaway-shootout','rooftop-snipers',
      'minibattles','12-mini-battles','1v1-battle','basketball-legends',
      'football-legends','soccer-random','tictactoe','four-in-a-row',
      'tank-trouble','gun-mayhem','bumper-cars-soccer','ping-pong-chaos',
      'air-hockey','paper-fighter','flip-bros','dino-bros','kart-bros',
      'zoom-be','fireboy','house-of-hazards','stickman-army-team'],'2-player'),
    (['fighting','fight','boxing','brawl','warrior','wrestler','wrestling',
      'combat','duel','martial','punch','kick','iron-snout','big-shot-boxing',
      'bearsus','wrassling','stick-fighter','stickman-fight','stickman-fighter',
      'stickman-warriors','puppet-master','happy-room','ragdoll','gang'],'fighting'),
    (['driving','driver','car-','cars-','truck','vehicle','road-','traffic-',
      'parking','drift','burnin-rubber','madalin','extreme-car','city-car',
      'draw-the-hill','drive-mad','eggy-car','death-chase','jelly-truck',
      'noob-drive','blocky-cars','kart-','go-kart','car-climb','car-rush',
      'car-eats-car','car-simulator','demolition','school-bus','truck-loader',
      'monster-track','3d-car','4x4-drive','city-bike','mad-truck',
      'short-ride','shortcut-race','18-wheeler','off-road','offroader'],'driving'),
    (['puzzle','brain','block-puzzle','bloxorz','tetra','tetris','element-block',
      'wood-block','color-sort','water-color','maze','minesweeper','solitaire',
      'wordle','word-city','infinity-loop','cat-trap','blob-drop','blumgi-bloom',
      'factory-balls','snail-bob','two-neon-boxes','escape','brain-test',
      '2048','master-chess','master-checkers','hextris','panda-bubble',
      'bubble-shooter','amazing-bubble','pop-it','merge-cakes','merge-fellas',
      'cubes-king','stacktris','craftomation','pack-a-bag','sink-it','apple',
      'arithmetica','doodle-champ','where-is-my-cat'],'puzzle'),
    (['multiplayer','-io','sharkio','paper-io','vectaria','nightpoint',
      'slope-2-multiplayer','pixwars','ludo-multiplayer','smash-karts',
      'kart-wars','house-of-hazards','hide-and-smash','among-us',
      'narrow-one','getaway-shootout','starblast'],'multiplayer'),
    (['zombie','war-','defend','defense','tower-defense','bloons','age-of-war',
      'blumgi-castle','blumgi-dragon','hills-of-steel','angry','beast','monster',
      'zombie-derby','zombie-siege','stupid-zombies','survivor-','bullet-force',
      'bullet-bros','fury-wars','neon-war','pixwars','shoot-stickman',
      'stickman-archero','stickman-army','stick-defenders','gangster','murder',
      'rio-rex','gunspin','guns','gun-mayhem','hammer','mad-day','avalanche',
      'dyna-boy','earn-to-die','burrito-bison','explosion','clash-of-tanks',
      'awesome-tanks','action'],'action'),
    (['dunk','flappy','hyper','curve-ball','darts','archery','archer',
      'stack-ball','g-switch','bouncy','duck-life','athletics','javelin',
      'long-jump','sprint','speed','surf','penalty','free-kick','dunkbrush',
      'dunkers','street-ball','basketball-frvr','basket-and-ball','blumgi-ball',
      'raft-wars','rocket-pult','sausage-flip','swingo','sling-drift','ring',
      'dart','bowl','bowling-stars','golf','golfinity','battle-golf',
      '8-ball-pool','9-ball-pool','pool-club','skill'],'skill'),
    (['adventure','rpg','quest','explore','dungeon','hero','legend','wizard',
      'dragon','kingdom','castle','tower-of-destiny','life-the-game','bitlife',
      'duck-life','dog-simulator','fox-simulator','tiger-simulator',
      'horse-simulator','panda-simulator','deer-simulator','dragon-simulator',
      'village-craft','minecraft','craftomation','snail-bob','crossy-road',
      'temple-of-boom','forgotten-hill','there-is-no-game','all-star-blast',
      'among-us','bacon-may-die','bearsus','a-pretty-odd-bunny','westoon',
      'game-of-farmers','tiny-fishing','world-cup','aqua-thrills'],'adventure'),
    (['racing','race','racer','moto-x3m','moto-road','moto-trial','moto-maniac',
      'highway-bike','highway-racer','highway-rider','superbike','super-bike',
      'moto-','motorbike','dirt-bike','speed-boat','speed-stars','drift-boss',
      'drift-hunters','smash-karts','kart-race','grand-prix','furious-racing',
      'shortcut-race','rally','turbo-moto','3d-moto','retro-highway',
      'death-run','death-chase','cluster-rush','stunt-car','top-speed',
      'tanuki-sunset','trail','atv','hover-racer'],'racing'),
    (['strategy','chess','checkers','tower-defense','bloons','idle','merge',
      'tycoon','clicker','miner','mining','empire','city','build','craft',
      'simulate','manage','war','age-of-war','izowave','fortz','stick-merge',
      'mini-battles','master-chess','master-checkers','snakes-and-ladders',
      'four-in-a-row','lands-of-blight','stickman-army','village-craft',
      'game-of-farmers','craftomation'],'strategy'),
    (['sport','football','soccer','basketball','baseball','tennis','golf',
      'boxing','volleyball','cricket','rugby','hockey','ping-pong','badminton',
      'athletics','swimming','head-soccer','heads-arena','football-legends',
      'foot-chinko','free-kick','penalty-shooters','soccer-skills',
      'a-small-world-cup','basketball-stars','basketball-legends',
      'basketball-frvr','bouncy-basketball','retro-bowl','4th-and-goal',
      'rugby-rush','little-master-cricket','bowling-stars','darts-pro',
      'volley-random','volleyball-challenge','power-badminton','sumo',
      '2-minute-football','8-ball-pool','9-ball-pool','pool-club',
      'curve-ball','dunkers','basketbros','basket-bro'],'sports'),
    (['simulation','simulator','sim','manage','idle','tycoon','build','city',
      'bitlife','life-the-game','dog-simulator','fox-simulator','tiger-simulator',
      'horse-simulator','panda-simulator','deer-simulator','dragon-simulator',
      'village-craft','minecraft','craftomation','game-of-farmers','monkey-mart',
      'papas-','tiny-fishing','park-it','parking','truck-loader','become-a-puppy',
      'horse-shoeing','idle-ants','idle-breakout','idle-digging','idle-gold',
      'idle-lumber','idle-mining','idle-startup','idle-zoo','doge-miner',
      'digging-master','cookie-clicker','misland','chicky-farm'],'simulation'),
    (['clicker','cookie-clicker','idle','blobby-clicker','italian-brainrot',
      'doge-miner','idle-ants','idle-breakout','idle-digging','idle-gold',
      'idle-lumber','idle-mining','idle-startup','idle-zoo','digging-master'],'clicker'),
    (['horror','five-nights','fnaf','scary','ghost','spooky','evil','creep',
      'moto-x3m-spooky','forgotten-hill','survival','survivor'],'horror'),
    (['kids','pony','puppy','dressup','peppa','baby','cute','bunny','kitty',
      'duck-life','chicky','chicken','a-pretty-odd-bunny','lovely-fox',
      'become-a-puppy','horse-shoeing','dinosaur-game','google-snake',
      'doodle-jump','flappy-bird','crossy-road','pac-man','monkey-mart',
      'papas-','merge-cakes','fruit-ninja','candy','bubble','pop-it',
      'snail-bob','shape-fold'],'kids'),
]

# Unique controls per game category (for "How to Play" fallback when AI not used)
CONTROLS_BY_CAT = {
    'shooter':    'Mouse to aim and shoot, WASD to move, R to reload, Space to jump',
    'platformer': 'Arrow keys or WASD to move, Space/Up to jump, double-tap for double jump',
    'fighting':   'Arrow keys to move, Z/X/C or A/S/D to punch, kick, and block',
    '2-player':   'Player 1: WASD + G/H. Player 2: Arrow keys + K/L',
    'driving':    'Arrow keys or WASD to steer, accelerate and brake. Space for handbrake',
    'puzzle':     'Mouse to select and place pieces. Think before you move!',
    'multiplayer':'Mouse to navigate, WASD to move, interact with other players online',
    'action':     'WASD to move, mouse to aim, left-click to attack, Space to dodge',
    'skill':      'Arrow keys or mouse — timing and precision are everything',
    'adventure':  'WASD or Arrow keys to move, E to interact, Space to jump or use items',
    'racing':     'Arrow keys to steer and accelerate, Space to brake or drift',
    'strategy':   'Mouse to select units, click to move/attack, manage resources carefully',
    'sports':     'Arrow keys to move, Space/Z to shoot or jump. Timing is key!',
    'simulation': 'Mouse to click and manage. Build, expand, and keep your citizens happy',
    'clicker':    'Click as fast as you can! Spend coins on upgrades to automate',
    'horror':     'WASD to move, E to interact, hold Shift to run. Stay quiet!',
    'kids':       'Mouse or Arrow keys — simple controls perfect for all ages!',
}

# ── HELPERS ──────────────────────────────────────────────────────────────────

def slug_to_title(slug):
    return ' '.join(w.capitalize() for w in slug.replace('-', ' ').split())

def get_categories(slug):
    cats = set()
    s = slug.lower()
    for keywords, cat in KEYWORD_RULES:
        for kw in keywords:
            if kw in s:
                cats.add(cat)
                break
    return sorted(cats) if cats else ['action']

def get_iframe_src(html):
    m = re.search(r'data-src=["\']([^"\']+)["\']', html)
    if m: return m.group(1)
    m = re.search(r'<iframe[^>]+src=["\'](?!about:blank)([^"\']+)["\']', html, re.I)
    if m: return m.group(1)
    return ''

def read_html(path):
    try: return path.read_text(encoding='utf-8', errors='ignore')
    except: return ''

def all_games():
    games = []
    for d in sorted(REPO.iterdir()):
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith('.'):
            if (d / 'index.html').exists():
                games.append(d.name)
    return games

def load_seo_cache():
    p = REPO / 'seo_cache.json'
    if p.exists():
        try: return json.loads(p.read_text(encoding='utf-8'))
        except: pass
    return {}

def save_seo_cache(cache):
    (REPO / 'seo_cache.json').write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

# ── AI CONTENT GENERATOR ─────────────────────────────────────────────────────

def ai_generate_game_content(slug, title, cats, controls_hint):
    """Call Claude API to generate unique SEO content for a game."""
    if not API_KEY:
        return None

    cat_names = ', '.join(cats)
    prompt = f"""You are an expert SEO writer for a free online games website called "Unblocked Games USA".
Write unique SEO content for the game: "{title}"
Game categories: {cat_names}
Default controls hint: {controls_hint}

Return ONLY valid JSON with these exact keys:
{{
  "title_suffix": "3-6 word subtitle describing the game genre/style for the HTML title tag",
  "meta_description": "150-160 char meta description starting with 'Play {title} unblocked free'",
  "about_h2": "Short engaging H2 heading for the About section (max 8 words)",
  "about_p1": "First paragraph about what the game is (80-120 words, natural, mention '{title} Unblocked' once)",
  "about_p2": "Second paragraph about what makes it special / tips (60-90 words)",
  "features": ["feature 1", "feature 2", "feature 3", "feature 4"],
  "howtoplay_intro": "One sentence intro for How to Play section",
  "controls": "Specific controls for this game (30-60 words, be specific to the game type)",
  "howtoplay_tip": "One strategic tip for this specific game (30-50 words)"
}}

Rules:
- Be specific to the actual game "{title}" — don't be generic
- Naturally include phrases like "unblocked", "play at school", "no download"  
- Controls must match the game category ({cat_names})
- Do NOT include quotes inside strings, use apostrophes instead
- Return ONLY the JSON object, no markdown, no extra text"""

    import urllib.request, urllib.error
    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 600,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')
    req = urllib.request.Request(API_URL, data=body, method='POST', headers={
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            text = data['content'][0]['text'].strip()
            # Strip markdown fences if present
            text = re.sub(r'^```json\s*|\s*```$', '', text, flags=re.M).strip()
            return json.loads(text)
    except Exception as e:
        print(f"    API error for {slug}: {e}")
        return None

def get_seo_content(slug, title, cats, cache, use_ai=True):
    """Get or generate SEO content, with cache."""
    if slug in cache and all(k in cache[slug] for k in ['about_p1','controls','meta_description']):
        return cache[slug]

    primary_cat = cats[0] if cats else 'action'
    controls_hint = CONTROLS_BY_CAT.get(primary_cat, 'Mouse or keyboard controls')

    content = None
    if use_ai and API_KEY:
        print(f"    🤖 AI generating content for: {title}")
        content = ai_generate_game_content(slug, title, cats, controls_hint)
        if content:
            time.sleep(0.3)  # Rate limit safety

    if not content:
        # Fallback: rule-based content
        cat_str = ' & '.join(c.capitalize() for c in cats[:2])
        content = {
            'title_suffix': f'Free {cat_str} Game Online',
            'meta_description': f'Play {title} unblocked free online — no download needed! Works at school instantly. One of the best {cat_str} games available.',
            'about_h2': f'About {title}',
            'about_p1': f'{title} Unblocked is an exciting free browser game in the {cat_str} genre that you can play instantly — no download required. Whether you\'re at school, work, or home, this game works right in your browser. Jump in and challenge yourself with fast-paced {primary_cat} gameplay that keeps you coming back for more.',
            'about_p2': f'What makes {title} stand out is its accessibility and instant playability. No sign-up, no waiting — just click Play and start immediately. Challenge your friends and see who can master the game first.',
            'features': [
                f'Free to play instantly, no download needed',
                f'Works unblocked at school or office',
                f'Exciting {cat_str} gameplay',
                f'Play on any device in your browser'
            ],
            'howtoplay_intro': f'Getting started with {title} is simple — just click the Play button above.',
            'controls': controls_hint,
            'howtoplay_tip': f'Practice regularly to improve your skills and climb the leaderboard. The more you play {title}, the better you get!'
        }

    cache[slug] = content
    return content

# ── HTML COMPONENTS ───────────────────────────────────────────────────────────

GTAG = f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GTAG_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GTAG_ID}');
</script>'''

BASE_CSS = '''<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,sans-serif;background:#0a0e1a;color:#dce8ff;line-height:1.6}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.wrap{max-width:1280px;margin:0 auto;padding:0 16px}

/* HEADER */
.site-header{background:linear-gradient(90deg,#001a6e,#0d1f6e 40%,#1a0a2e 65%,#8b0000);
  border-bottom:3px solid #c0392b;position:sticky;top:0;z-index:100;
  box-shadow:0 4px 20px rgba(0,0,0,.7)}
.hdr-inner{display:flex;align-items:center;gap:12px;padding:10px 16px;flex-wrap:wrap}
.logo{font-weight:800;font-size:1.25rem;color:#fff;white-space:nowrap}
.logo:hover{text-shadow:0 0 20px rgba(192,57,43,.9)}
.search-wrap{position:relative;margin-left:auto;display:flex}
.search-wrap input{padding:.4rem .9rem;border:1px solid rgba(255,255,255,.15);
  border-radius:20px 0 0 20px;background:rgba(255,255,255,.12);color:#fff;
  font-size:.88rem;width:200px;outline:none;transition:width .2s}
.search-wrap input::placeholder{color:rgba(255,255,255,.45)}
.search-wrap input:focus{background:rgba(255,255,255,.2);width:240px}
.search-wrap button{background:#c0392b;color:#fff;border:none;
  border-radius:0 20px 20px 0;padding:.4rem .9rem;cursor:pointer}
#searchDrop{position:absolute;top:calc(100% + 6px);left:0;right:0;
  background:#0a1535;border:1px solid rgba(192,57,43,.3);border-radius:10px;
  max-height:280px;overflow-y:auto;z-index:300;display:none;
  box-shadow:0 8px 28px rgba(0,0,0,.8)}
#searchDrop.open{display:block}
#searchDrop a{display:flex;align-items:center;gap:10px;padding:8px 12px;
  border-bottom:1px solid rgba(255,255,255,.06);font-size:.85rem;font-weight:600}
#searchDrop a:hover{background:rgba(192,57,43,.2)}
#searchDrop img{width:36px;height:26px;object-fit:cover;border-radius:4px;flex-shrink:0}
.no-res{padding:12px;color:rgba(255,255,255,.4);text-align:center;font-size:.83rem}
.nav-toggle{display:none;background:none;border:none;color:#fff;font-size:1.4rem;cursor:pointer;padding:.3rem .5rem}

/* NAV */
.main-nav{background:linear-gradient(90deg,#001050,#0d1560 40%,#1a0825 70%,#500010);
  border-top:1px solid rgba(255,255,255,.06)}
.main-nav ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;
  gap:4px;padding:8px 16px;max-width:1280px;margin:0 auto}
.main-nav a{color:rgba(255,255,255,.85);padding:4px 11px;border-radius:20px;
  font-size:.8rem;font-weight:600;border:1px solid transparent;white-space:nowrap}
.main-nav a:hover,.main-nav a.active{background:rgba(192,57,43,.35);color:#fff;border-color:rgba(192,57,43,.4)}

/* FOOTER — single clean footer, NO duplicate nav menu */
.site-footer{background:#060b18;border-top:2px solid #c0392b;padding:28px 16px;margin-top:48px;text-align:center}
.footer-links{display:flex;gap:16px;justify-content:center;margin-bottom:10px;
  font-size:.82rem;opacity:.7;flex-wrap:wrap}
.footer-links a:hover{opacity:1;color:#e74c3c}
.footer-copy{font-size:.75rem;opacity:.35}

/* CARDS */
.games-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:16px 0}
.game-card{display:flex;flex-direction:column;background:#111827;border-radius:10px;
  overflow:hidden;border:1px solid rgba(255,255,255,.07);transition:transform .2s,box-shadow .2s,border-color .2s}
.game-card:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,0,0,.5);border-color:rgba(192,57,43,.4)}
.game-card img{width:100%;height:110px;object-fit:cover}
.game-card span{padding:7px 8px;font-size:.78rem;text-align:center;font-weight:500;line-height:1.3}

/* PAGINATION */
.pagination{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:28px 0}
.pagination a{padding:7px 15px;background:#111827;color:#dce8ff;border-radius:8px;
  font-weight:600;font-size:.9rem;border:1px solid rgba(255,255,255,.08)}
.pagination a:hover{background:#1a2a4a;border-color:rgba(192,57,43,.4)}
.pagination a.cur{background:#c0392b;color:#fff;border-color:#c0392b}

@media(max-width:900px){
  .nav-toggle{display:block}
  .main-nav ul{display:none;flex-direction:column;align-items:flex-start;padding:8px 16px}
  .main-nav ul.open{display:flex}
  .search-wrap{order:3;width:100%}
  .search-wrap input{width:100%}
}
@media(max-width:600px){
  .games-grid{grid-template-columns:repeat(2,1fr)}
}
</style>'''

SHARED_JS = '''<script>
document.getElementById('navToggle')?.addEventListener('click',()=>
  document.getElementById('navMenu')?.classList.toggle('open'));
(function(){
  var inp=document.getElementById('searchInput');
  var drop=document.getElementById('searchDrop');
  var btn=document.getElementById('searchBtn');
  if(!inp||!drop)return;
  var _g=null;
  function load(cb){
    if(_g)return cb(_g);
    fetch('/search-index.json').then(r=>r.json()).then(d=>{_g=d;cb(d);}).catch(()=>cb([]));
  }
  function close(){drop.classList.remove('open');drop.innerHTML='';}
  inp.addEventListener('input',function(){
    var q=this.value.trim();
    if(!q){close();return;}
    load(function(games){
      var t=q.toLowerCase();
      var res=games.filter(g=>g.title.toLowerCase().includes(t)||
        g.slug.replace(/-/g,' ').includes(t)).slice(0,8);
      drop.innerHTML=res.length
        ? res.map(g=>'<a href="/'+g.slug+'"><img src="'+g.image+'" loading="lazy"><span>'+g.title+'</span></a>').join('')
        : '<div class="no-res">No results for "'+q+'"</div>';
      drop.classList.add('open');
    });
  });
  inp.addEventListener('keydown',function(e){
    if(e.key==='Enter'){var q=inp.value.trim();if(q){close();window.location='/?q='+encodeURIComponent(q);}}
    if(e.key==='Escape')close();
  });
  btn.addEventListener('click',function(){var q=inp.value.trim();if(q)window.location='/?q='+encodeURIComponent(q);});
  document.addEventListener('click',function(e){if(!e.target.closest('.search-wrap'))close();});
})();
</script>'''

def nav_html():
    links = '\n    '.join(f'<li><a href="/categ/{k}/">{v}</a></li>' for k,v in CATS.items())
    return f'''<header class="site-header">
  <div class="wrap hdr-inner">
    <a href="/" class="logo">🎮 Unblocked Games USA</a>
    <div class="search-wrap">
      <input type="text" id="searchInput" placeholder="Search games…" autocomplete="off" aria-label="Search games">
      <button id="searchBtn" aria-label="Search">🔍</button>
      <div id="searchDrop" role="listbox"></div>
    </div>
    <button class="nav-toggle" id="navToggle" aria-label="Toggle menu">☰</button>
  </div>
  <nav class="main-nav" aria-label="Game categories">
    <ul id="navMenu">
    {links}
    </ul>
  </nav>
</header>'''

def footer_html():
    # CLEAN footer — NO duplicate category nav menu, just legal links
    return f'''<footer class="site-footer" aria-label="Site footer">
  <div class="wrap">
    <div class="footer-links">
      <a href="/privacy-policy/">Privacy Policy</a>
      <a href="/contact/">Contact Us</a>
      <a href="/faq/">FAQ</a>
      <a href="/dmca/">DMCA</a>
    </div>
    <p class="footer-copy">&copy; <span id="yr"></span> Unblocked Games USA. All rights reserved.</p>
  </div>
</footer>
<script>document.getElementById('yr').textContent=new Date().getFullYear();</script>'''

# ── GAME PAGE ─────────────────────────────────────────────────────────────────

GAME_CSS = BASE_CSS + '''<style>
.game-wrap{padding:20px 0}
.game-header{text-align:center;margin-bottom:18px}
.game-header h1{font-size:clamp(1.5rem,4vw,2.2rem);font-weight:800;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.game-header .tagline{color:rgba(255,255,255,.55);margin-top:6px;font-size:.95rem}
.frame-box{position:relative;width:100%;max-width:960px;margin:0 auto;
  background:#000;border-radius:12px;overflow:hidden;border:2px solid rgba(255,255,255,.08);
  aspect-ratio:16/9}
.frame-thumb{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1}
.frame-overlay{position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;z-index:3;
  background:rgba(0,0,0,.45);cursor:pointer}
.frame-overlay:hover{background:rgba(0,0,0,.3)}
.play-btn{width:80px;height:80px;border-radius:50%;border:none;cursor:pointer;
  background:linear-gradient(135deg,#1a3a8a,#c0392b);color:#fff;font-size:2.4rem;
  display:flex;align-items:center;justify-content:center;padding-left:6px;
  box-shadow:0 0 0 4px rgba(192,57,43,.4),0 8px 30px rgba(0,0,0,.6);
  animation:pulse 2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(192,57,43,.4),0 8px 30px rgba(0,0,0,.6)}
  50%{box-shadow:0 0 0 14px rgba(192,57,43,.1),0 8px 30px rgba(0,0,0,.6)}}
.play-label{color:#fff;font-weight:700;font-size:1rem;letter-spacing:2px;
  margin-top:12px;background:rgba(0,0,0,.5);padding:4px 18px;border-radius:20px}
.game-iframe{position:absolute;inset:0;width:100%;height:100%;border:none;display:none;z-index:2}
.game-iframe.on{display:block}
.fs-btn{position:absolute;bottom:10px;right:10px;z-index:4;
  background:rgba(0,0,0,.65);color:#fff;border:none;border-radius:6px;
  padding:5px 12px;cursor:pointer;font-size:.82rem}
.fs-btn:hover{background:#c0392b}

/* INFO CARD */
.info-card{background:#111827;border-radius:12px;padding:28px;margin:24px 0;
  border:1px solid rgba(255,255,255,.07)}
.info-card::after{content:'';display:table;clear:both}
.info-thumb{float:left;width:130px;border-radius:8px;margin:0 20px 12px 0;
  border:1px solid rgba(255,255,255,.1)}
.info-card h2{font-size:1.3rem;font-weight:700;color:#e74c3c;margin-bottom:10px}
.info-card h3{font-size:1.05rem;font-weight:700;color:#e74c3c;margin:18px 0 8px}
.info-card p{color:rgba(255,255,255,.82);font-size:.95rem;margin-bottom:10px;line-height:1.7}
.features-list{list-style:none;margin:10px 0;padding:0}
.features-list li{padding:4px 0;color:rgba(255,255,255,.75);font-size:.9rem}
.features-list li::before{content:"✓ ";color:#27ae60;font-weight:700}
.controls-box{background:rgba(255,255,255,.05);border-radius:8px;padding:14px 16px;
  margin:10px 0;border-left:3px solid #c0392b;font-size:.9rem;color:rgba(255,255,255,.85)}
.cat-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;clear:both}
.cat-tag{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(192,57,43,.6));
  color:#fff;border-radius:20px;padding:.3rem .9rem;font-size:.82rem;font-weight:600;
  border:1px solid rgba(255,255,255,.1)}
.cat-tag:hover{background:linear-gradient(135deg,#1a3a8a,#c0392b)}

/* SECTIONS */
.section-h{font-size:1.2rem;font-weight:700;margin:28px 0 14px;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

/* POPULAR CATS — at bottom of game pages only */
.pop-cats{margin:32px 0 0}
.pop-cats h2{font-size:1.1rem;font-weight:700;color:#4fa3ff;margin-bottom:12px}
.pop-cats div{display:flex;flex-wrap:wrap;gap:8px}
.pop-cats a{background:#111827;padding:6px 13px;border-radius:16px;
  font-size:.82rem;border:1px solid rgba(255,255,255,.07)}
.pop-cats a:hover{background:#1a2a4a;border-color:rgba(192,57,43,.3)}
</style>'''

GAME_JS = '''<script>
(function(){
  var ov=document.getElementById('frameOverlay');
  var fr=document.getElementById('gameFrame');
  if(!ov||!fr)return;
  function launch(){
    var src=fr.getAttribute('data-src');
    if(!src)return;
    fr.src=src;
    fr.classList.add('on');
    ov.style.display='none';
    document.getElementById('frameThumb')?.remove();
  }
  ov.addEventListener('click',launch);
  ov.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' ')launch();});
})();
document.getElementById('fsBtn')?.addEventListener('click',function(){
  var el=document.getElementById('frameBox');
  (el.requestFullscreen||el.webkitRequestFullscreen||el.mozRequestFullScreen||function(){}).call(el);
});
</script>'''

def build_game_page(slug, iframe_src, cats, seo, all_g):
    title = slug_to_title(slug)
    title_suffix = seo.get('title_suffix', f'Free {cats[0].capitalize()} Game Online')
    meta_desc = seo.get('meta_description', f'Play {title} unblocked free online. No download needed, works at school instantly.')[:160]
    about_h2 = seo.get('about_h2', f'About {title}')
    about_p1 = seo.get('about_p1', f'Play {title} Unblocked free in your browser.')
    about_p2 = seo.get('about_p2', '')
    features = seo.get('features', [])
    htp_intro = seo.get('howtoplay_intro', f'Click Play to start {title} instantly.')
    controls = seo.get('controls', CONTROLS_BY_CAT.get(cats[0], 'Mouse or keyboard'))
    htp_tip = seo.get('howtoplay_tip', '')

    cat_tags_html = '\n    '.join(
        f'<a href="/categ/{c}/" class="cat-tag">{CATS[c]}</a>'
        for c in cats if c in CATS
    ) or '<a href="/categ/action/" class="cat-tag">💥 Action</a>'

    features_html = '\n'.join(f'<li>{f}</li>' for f in features) if features else ''
    features_block = f'<ul class="features-list">{features_html}</ul>' if features_html else ''
    about_p2_block = f'<p>{about_p2}</p>' if about_p2 else ''
    htp_tip_block = f'<p>{htp_tip}</p>' if htp_tip else ''

    # Similar games — pick 12 games from same categories
    same_cat = [g for g in all_g if g != slug and any(c in get_categories(g) for c in cats)]
    random.shuffle(same_cat)
    similar = (same_cat[:12] + [g for g in all_g if g != slug and g not in same_cat])[:12]
    sim_html = '\n    '.join(
        f'<a class="game-card" href="/{g}/">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{slug_to_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{slug_to_title(g)} Unblocked</span></a>'
        for g in similar
    )

    pop_cats_html = ' '.join(
        f'<a href="/categ/{k}/">{v}</a>'
        for k, v in CATS.items()
    )

    genre_tags = ', '.join(cats)
    if not iframe_src:
        iframe_src = f'https://iframe.unblocked-76-games.org/{slug}'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} Unblocked - {title_suffix} | Unblocked Games USA</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{BASE_URL}/{slug}/">
<meta property="og:title" content="{title} Unblocked - Play Free Online">
<meta property="og:description" content="{meta_desc}">
<meta property="og:url" content="{BASE_URL}/{slug}/">
<meta property="og:image" content="{IMG_BASE}/{slug}.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index,follow,max-image-preview:large">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"VideoGame",
"name":"{title}","url":"{BASE_URL}/{slug}/",
"description":"{meta_desc.replace(chr(34), chr(39))}",
"applicationCategory":"Game","operatingSystem":"Web Browser",
"offers":{{"@type":"Offer","price":"0","priceCurrency":"USD"}},
"image":"{IMG_BASE}/{slug}.png",
"genre":["{genre_tags}"],
"provider":{{"@type":"Organization","name":"Unblocked Games USA","url":"{BASE_URL}/"}}}}</script>
<link rel="icon" href="/favicon.ico">
{GTAG}
{GAME_CSS}
</head>
<body>
{nav_html()}
<div class="wrap game-wrap">
  <div class="game-header">
    <h1>{title} Unblocked</h1>
    <p class="tagline">Play {title} free online — no download, works at school!</p>
  </div>
  <div class="frame-box" id="frameBox">
    <img id="frameThumb" class="frame-thumb" src="{IMG_BASE}/{slug}.png" alt="{title} gameplay preview">
    <div id="frameOverlay" class="frame-overlay" role="button" tabindex="0" aria-label="Play {title}">
      <button class="play-btn" tabindex="-1" aria-hidden="true">&#9654;</button>
      <span class="play-label">PLAY NOW</span>
    </div>
    <iframe id="gameFrame" class="game-iframe"
            src="about:blank"
            data-src="{iframe_src}"
            title="{title} Unblocked Game"
            allowfullscreen
            allow="autoplay; fullscreen; pointer-lock; gamepad"></iframe>
    <button id="fsBtn" class="fs-btn">⛶ Fullscreen</button>
  </div>

  <div class="info-card">
    <img src="{IMG_BASE}/{slug}.png" alt="{title} Unblocked" class="info-thumb" loading="lazy">
    <h2>{about_h2}</h2>
    <p>{about_p1}</p>
    {about_p2_block}
    {features_block}
    <h3>How to Play {title} 🕹️</h3>
    <p>{htp_intro}</p>
    <div class="controls-box"><strong>Controls:</strong> {controls}</div>
    {htp_tip_block}
    <div class="cat-tags" style="clear:both">
      {cat_tags_html}
    </div>
  </div>

  <h2 class="section-h">🎮 Similar Games You'll Love</h2>
  <div class="games-grid">
    {sim_html}
  </div>

  <div class="pop-cats">
    <h2>🗂️ Browse All Categories</h2>
    <div>{pop_cats_html}</div>
  </div>
</div>
{footer_html()}
{SHARED_JS}
{GAME_JS}
</body>
</html>'''

# ── CATEGORY PAGE ─────────────────────────────────────────────────────────────

CATEG_CSS = BASE_CSS + '''<style>
.categ-hero{text-align:center;padding:36px 16px 20px}
.categ-hero h1{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:800;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.categ-hero p{color:rgba(255,255,255,.55);margin-top:8px}
.other-cats{margin:36px 0 0}
.other-cats h2{font-size:1.1rem;font-weight:700;color:#4fa3ff;margin-bottom:12px}
.other-cats div{display:flex;flex-wrap:wrap;gap:8px}
.other-cats a{background:#111827;padding:6px 13px;border-radius:16px;
  font-size:.82rem;border:1px solid rgba(255,255,255,.07)}
.other-cats a:hover{background:#1a2a4a}
</style>'''

def build_categ_page(cat_slug, cat_label, games_on_page, page_num, total_pages, total_count):
    cards = '\n    '.join(
        f'<a class="game-card" href="/{g}/">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{slug_to_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{slug_to_title(g)} Unblocked</span></a>'
        for g in games_on_page
    )
    pag = ''
    if page_num > 1:
        prev = f'/categ/{cat_slug}/' if page_num == 2 else f'/categ/{cat_slug}-page-{page_num-1}/'
        pag += f'<a href="{prev}">&laquo; Prev</a>'
    for p in range(1, total_pages+1):
        url = f'/categ/{cat_slug}/' if p==1 else f'/categ/{cat_slug}-page-{p}/'
        cls = ' class="cur"' if p==page_num else ''
        pag += f'<a href="{url}"{cls}>{p}</a>'
    if page_num < total_pages:
        pag += f'<a href="/categ/{cat_slug}-page-{page_num+1}/">Next &raquo;</a>'

    others = ' '.join(
        f'<a href="/categ/{k}/">{v}</a>'
        for k,v in CATS.items() if k != cat_slug
    )
    page_suffix = f' – Page {page_num}' if page_num > 1 else ''
    canon = f'{BASE_URL}/categ/{cat_slug}/' if page_num == 1 else f'{BASE_URL}/categ/{cat_slug}-page-{page_num}/'
    cat_emoji = cat_label.split()[0]
    cat_name = ' '.join(cat_label.split()[1:])
    meta_desc = f'Play {total_count} free unblocked {cat_name} games online instantly. No download required — works at school!'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cat_name} Games Unblocked{page_suffix} – {total_count} Free Online | Unblocked Games USA</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index,follow">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage",
"name":"{cat_name} Unblocked Games","url":"{canon}",
"description":"{meta_desc}",
"provider":{{"@type":"Organization","name":"Unblocked Games USA","url":"{BASE_URL}/"}}}}</script>
{GTAG}
{CATEG_CSS}
</head>
<body>
{nav_html()}
<div class="wrap">
  <div class="categ-hero">
    <h1>{cat_emoji} {cat_name} Unblocked Games</h1>
    <p>{total_count} free games — play instantly, no downloads needed</p>
  </div>
  <div class="games-grid">
    {cards}
  </div>
  <div class="pagination">{pag}</div>
  <div class="other-cats">
    <h2>🎮 Other Categories</h2>
    <div>{others}</div>
  </div>
</div>
{footer_html()}
{SHARED_JS}
</body>
</html>'''

# ── HOMEPAGE ──────────────────────────────────────────────────────────────────

def build_homepage(games):
    n = len(games)
    # Show 60 popular games on homepage
    popular = games[:60]
    cards = '\n    '.join(
        f'<a class="game-card" href="/{g}/">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{slug_to_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{slug_to_title(g)} Unblocked</span></a>'
        for g in popular
    )
    cat_pills = '\n '.join(
        f'<a href="/categ/{k}/" style="display:inline-flex;align-items:center;gap:6px;background:#111827;padding:8px 16px;border-radius:24px;font-size:.88rem;border:1px solid rgba(255,255,255,.08);color:#dce8ff">{v}</a>'
        for k,v in CATS.items()
    )

    home_css = BASE_CSS + '''<style>
.hero{text-align:center;padding:40px 0 28px}
.hero h1{font-size:clamp(1.8rem,5vw,3rem);font-weight:900;margin-bottom:10px;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero .sub{color:rgba(255,255,255,.6);max-width:560px;margin:0 auto 24px;font-size:1.05rem}
.badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:26px}
.badge{background:#111827;padding:7px 15px;border-radius:20px;font-size:.85rem;
  border:1px solid rgba(255,255,255,.08)}
.search-all-btn{background:linear-gradient(135deg,#1a3a8a,#c0392b);color:#fff;
  border:none;padding:12px 32px;border-radius:28px;font-size:1rem;cursor:pointer;
  font-weight:700;box-shadow:0 4px 20px rgba(192,57,43,.4)}
.search-all-btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(192,57,43,.5)}
.sec-h{font-size:1.25rem;font-weight:700;margin:32px 0 14px;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.cat-browse{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:8px 0 36px}
.site-desc{background:#111827;border-radius:12px;padding:28px;margin:28px 0;
  border:1px solid rgba(255,255,255,.07);color:rgba(255,255,255,.75);line-height:1.8}
.site-desc h2{color:#4fa3ff;font-size:1.2rem;margin-bottom:10px}

/* Full search modal */
#searchModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.93);z-index:9999;
  overflow-y:auto;padding:70px 20px 20px}
#searchModal.on{display:block}
#searchClose{position:fixed;top:14px;right:18px;background:#c0392b;color:#fff;border:none;
  border-radius:50%;width:38px;height:38px;cursor:pointer;font-size:1.1rem;z-index:10000}
#searchInput2{width:100%;max-width:860px;display:block;margin:0 auto 14px;
  padding:12px 18px;font-size:1.1rem;border-radius:10px;border:none;
  background:#161b22;color:#fff;outline:none}
#searchStatus{text-align:center;color:#f85149;margin-bottom:14px;max-width:860px;
  margin-left:auto;margin-right:auto;min-height:24px}
#searchGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
  gap:12px;max-width:860px;margin:0 auto}
</style>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unblocked Games USA – {n}+ Free Games To Play Online Instantly</title>
<meta name="description" content="Play {n}+ free unblocked games online instantly. No downloads, no sign-ups. Shooter, racing, puzzle, adventure and more — works at school!">
<link rel="canonical" href="{BASE_URL}/">
<meta property="og:title" content="Unblocked Games USA – Free Games Online">
<meta property="og:description" content="Play {n}+ free unblocked games online. No downloads needed!">
<meta property="og:url" content="{BASE_URL}/">
<meta property="og:image" content="{BASE_URL}/images/og-home.png">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite",
"name":"Unblocked Games USA","url":"{BASE_URL}/",
"description":"Free unblocked games online — play instantly at school",
"potentialAction":{{"@type":"SearchAction","target":"{BASE_URL}/?q={{search_term_string}}",
"query-input":"required name=search_term_string"}}}}</script>
{GTAG}
{home_css}
</head>
<body>
{nav_html()}
<main>
<div class="wrap">
  <div class="hero">
    <h1>🎮 Unblocked Games USA</h1>
    <p class="sub">Free games for every break. No downloads, no sign-ups. Play instantly!</p>
    <div class="badges">
      <span class="badge">✅ No Downloads</span>
      <span class="badge">🎮 100% Free</span>
      <span class="badge">⚡ Play Instantly</span>
      <span class="badge">🏫 School Friendly</span>
    </div>
    <button class="search-all-btn" onclick="openSearch()">🔍 Search All {n} Games</button>
  </div>

  <h2 class="sec-h">🗂️ Browse by Category</h2>
  <div class="cat-browse">
    {cat_pills}
  </div>

  <h2 class="sec-h">🔥 Popular Games</h2>
  <div class="games-grid">
    {cards}
  </div>

  <div class="site-desc">
    <h2>About Unblocked Games USA</h2>
    <p>Welcome to <strong>Unblocked Games USA</strong> — your ultimate destination for free browser games that work anywhere, including school and the office. We host {n}+ games across {len(CATS)} categories including shooter, racing, puzzle, adventure, sports, and more.</p>
    <p>Every game on our site is <strong>100% free to play</strong>, requires no download or installation, and launches instantly in your browser. Whether you have 5 minutes or 5 hours, we have the perfect game for you.</p>
  </div>
</div>
</main>

<div id="searchModal" role="dialog" aria-modal="true" aria-label="Search all games">
  <button id="searchClose" onclick="closeSearch()" aria-label="Close search">✕</button>
  <input id="searchInput2" type="search" placeholder="Search {n} games…" oninput="doSearch(this.value)" autofocus autocomplete="off">
  <div id="searchStatus" role="status" aria-live="polite"></div>
  <div id="searchGrid"></div>
</div>

{footer_html()}
{SHARED_JS}
<script>
var _ag=null;
function loadAll(cb){{if(_ag)return cb(_ag);fetch('/search-index.json').then(r=>r.json()).then(d=>{{_ag=d;cb(d);}}).catch(()=>cb([]));}}
function openSearch(){{document.getElementById('searchModal').classList.add('on');document.body.style.overflow='hidden';document.getElementById('searchInput2').focus();loadAll(function(){{}});}}
function closeSearch(){{document.getElementById('searchModal').classList.remove('on');document.body.style.overflow='';}}
document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeSearch();}});
function doSearch(q){{
  loadAll(function(games){{
    var t=q.toLowerCase().trim();
    var st=document.getElementById('searchStatus');
    var gr=document.getElementById('searchGrid');
    if(!t){{st.textContent='';gr.innerHTML='<p style="color:#8b949e;text-align:center;grid-column:1/-1">Start typing to search {n} games...</p>';return;}}
    var res=games.filter(function(g){{return g.title.toLowerCase().includes(t)||g.slug.replace(/-/g,' ').includes(t)||(g.categories||[]).some(function(c){{return c.includes(t);}});}}).slice(0,72);
    st.textContent=res.length?'':'No games found for "'+q+'"';
    gr.innerHTML=res.map(function(g){{return '<a href="/'+g.slug+'/" style="display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:8px;overflow:hidden;color:#e6edf3;border:1px solid rgba(255,255,255,.07)"><img src="'+g.image+'" alt="'+g.title+'" loading="lazy" style="width:100%;height:100px;object-fit:cover"><span style="padding:6px 4px;font-size:.78rem;text-align:center">'+g.title+'</span></a>';}}).join('');
  }});
}}
</script>
</body>
</html>'''

# ── SITEMAP ───────────────────────────────────────────────────────────────────

def build_sitemap(games):
    today = __import__('datetime').date.today().isoformat()
    urls = [f'''  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>''']
    for k in CATS:
        urls.append(f'''  <url>
    <loc>{BASE_URL}/categ/{k}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>''')
    for slug in games:
        urls.append(f'''  <url>
    <loc>{BASE_URL}/{slug}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>''')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(urls)
    xml += '\n</urlset>'
    return xml

def build_robots():
    return f'''User-agent: *
Allow: /
Disallow: /seo_cache.json
Disallow: /fix_all.py
Disallow: /seo_fix.py

Sitemap: {BASE_URL}/sitemap.xml
'''

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='SEO Fix for Unblocked Games USA')
    parser.add_argument('--all', action='store_true', help='Rebuild everything')
    parser.add_argument('--slug', help='Rebuild single game by slug')
    parser.add_argument('--batch', type=int, default=0, help='Rebuild N games (with AI content)')
    parser.add_argument('--resume', action='store_true', help='Skip already-cached games')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI, use rule-based content only')
    parser.add_argument('--categ', action='store_true', help='Rebuild category pages only')
    parser.add_argument('--home', action='store_true', help='Rebuild homepage only')
    args = parser.parse_args()

    use_ai = not args.no_ai and bool(API_KEY)
    if use_ai:
        print(f'🤖 AI mode ON (API key found)')
    else:
        print(f'📝 Rule-based mode (set ANTHROPIC_API_KEY env var to enable AI content)')

    games = all_games()
    print(f'Found {len(games)} games\n')

    # Build category map
    cat_map = {k: [] for k in CATS}
    for slug in games:
        for c in get_categories(slug):
            if slug not in cat_map[c]:
                cat_map[c].append(slug)

    # Load SEO cache
    cache = load_seo_cache()
    print(f'SEO cache: {len(cache)} games already processed\n')

    # Get iframe sources
    def get_src(slug):
        html = read_html(REPO / slug / 'index.html')
        return get_iframe_src(html)

    if args.slug:
        # Single game rebuild
        slug = args.slug
        if not (REPO / slug).exists():
            print(f'ERROR: Game folder "{slug}" not found'); return
        cats = get_categories(slug)
        iframe_src = get_src(slug)
        seo = get_seo_content(slug, slug_to_title(slug), cats, cache, use_ai)
        save_seo_cache(cache)
        html = build_game_page(slug, iframe_src, cats, seo, games)
        (REPO / slug / 'index.html').write_text(html, encoding='utf-8')
        print(f'✅ Rebuilt: {slug}')

    elif args.categ or args.all:
        # Rebuild category pages
        print('Rebuilding category pages...')
        categ_root = REPO / 'categ'
        categ_root.mkdir(exist_ok=True)
        for cat_slug, cat_label in CATS.items():
            cat_games = cat_map[cat_slug]
            if not cat_games: continue
            total = len(cat_games)
            n_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
            for p in range(1, n_pages+1):
                chunk = cat_games[(p-1)*PER_PAGE : p*PER_PAGE]
                folder = categ_root / (cat_slug if p==1 else f'{cat_slug}-page-{p}')
                folder.mkdir(parents=True, exist_ok=True)
                html = build_categ_page(cat_slug, cat_label, chunk, p, n_pages, total)
                (folder / 'index.html').write_text(html, encoding='utf-8')
            print(f'  {cat_label}: {total} games, {n_pages} page(s)')
        if not args.all:
            print('\n✅ Category pages done!')
            return

    if args.home or args.all:
        print('Rebuilding homepage...')
        (REPO / 'index.html').write_text(build_homepage(games), encoding='utf-8')
        print('  Homepage done')

    if args.all:
        # Rebuild all game pages
        print(f'\nRebuilding all {len(games)} game pages...')
        for i, slug in enumerate(games):
            if args.resume and slug in cache:
                # Use cached seo but still rewrite page
                pass
            cats = get_categories(slug)
            iframe_src = get_src(slug)
            seo = get_seo_content(slug, slug_to_title(slug), cats, cache, use_ai=False)
            html = build_game_page(slug, iframe_src, cats, seo, games)
            (REPO / slug / 'index.html').write_text(html, encoding='utf-8')
            if (i+1) % 100 == 0:
                print(f'  {i+1}/{len(games)}')
        save_seo_cache(cache)

    elif args.batch > 0:
        # AI-generate content for N games, then rebuild their pages
        to_process = [s for s in games if s not in cache] if args.resume else games
        to_process = to_process[:args.batch]
        print(f'Processing {len(to_process)} games with AI content...\n')
        for i, slug in enumerate(to_process):
            print(f'[{i+1}/{len(to_process)}] {slug}')
            cats = get_categories(slug)
            iframe_src = get_src(slug)
            seo = get_seo_content(slug, slug_to_title(slug), cats, cache, use_ai)
            html = build_game_page(slug, iframe_src, cats, seo, games)
            (REPO / slug / 'index.html').write_text(html, encoding='utf-8')
            if (i+1) % 20 == 0:
                save_seo_cache(cache)
        save_seo_cache(cache)
        print(f'\n✅ Batch of {len(to_process)} games done! ({len(cache)} total in cache)')

    # Generate sitemap + robots
    print('\nGenerating sitemap.xml and robots.txt...')
    (REPO / 'sitemap.xml').write_text(build_sitemap(games), encoding='utf-8')
    (REPO / 'robots.txt').write_text(build_robots(), encoding='utf-8')
    print('  sitemap.xml and robots.txt written')

    # Rebuild search index
    print('Updating search-index.json...')
    index = [
        {'slug': s, 'title': f'{slug_to_title(s)} Unblocked',
         'image': f'{IMG_BASE}/{s}.png', 'categories': get_categories(s)}
        for s in games
    ]
    (REPO / 'search-index.json').write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')

    print(f'''
✅ SEO Fix Complete!

Usage guide:
  python seo_fix.py --all            # Rebuild everything (no AI, fast)
  python seo_fix.py --categ          # Only rebuild category pages
  python seo_fix.py --home           # Only rebuild homepage
  python seo_fix.py --slug=slope     # Rebuild single game page
  python seo_fix.py --batch=50       # AI-generate content for 50 games
  python seo_fix.py --batch=50 --resume  # Skip already-done games
  python seo_fix.py --all --no-ai    # Full rebuild, no AI calls

To use AI content generation:
  set ANTHROPIC_API_KEY=sk-ant-...   (Windows)
  export ANTHROPIC_API_KEY=sk-ant-...(Mac/Linux)
  python seo_fix.py --batch=586      # Then AI-generate all games

Then push:
  git add -A
  git commit -m "SEO: unique content, clean footer, sitemap, robots.txt"
  git push
''')

if __name__ == '__main__':
    main()