#!/usr/bin/env python3
"""
Comprehensive fix for UnblockedGames-USA.github.io
Fixes:
1. Category pages show all games → build proper slug→category mapping
2. Search broken (search-index.json missing) → generate it
3. Game titles have "— Free 2" suffix → clean them
4. gtag not integrated → add to all pages
5. Nav category links broken (using /categ/ but no categ folder) → fix to relative paths
Run: python3 fix_all.py  (from repo root)
"""
import os, re, json
from pathlib import Path

REPO     = Path('/home/claude/repo')
BASE_URL = 'https://unblockedgames-usa.github.io'
IMG_BASE = f'{BASE_URL}/images'
PER_PAGE = 50
GTAG_ID  = 'G-L6FNHSMWF4'

SKIP_DIRS = {'categ','assets','.git','images','privacy-policy','contact','faq','dmca',
             'node_modules','search'}

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

# ── KEYWORD-BASED CATEGORY MAPPING ──────────────────────────────────────────
# Maps slug keywords → categories. A game can match multiple categories.
KEYWORD_RULES = [
    # SHOOTER
    (['shooter', 'sniper', 'gun', 'bullet', 'shoot', 'swat', 'force', 'armed',
      'pixel-gun', 'skibidi-shooter', 'funny-shooter', 'masked-forces', 'leader-strike',
      'nightpoint', 'starblast', 'alien-invaders', 'cat-gunner', 'total-recoil',
      'neon-war', 'recoil', 'james-gun', 'shoot', 'shootz', 'cannon'], 'shooter'),

    # PLATFORMER
    (['platformer', 'platformer', 'fancy-pants', 'super-mario', 'vex-', 'ovo',
      'dreadhead', 'parkour', 'flip-runner', 'stickman-run', 'stickman-climb',
      'stickman-parkour', 'stickman-school-run', 'running-fred', 'electron-dash',
      'subway-runner', 'subway-surfers', 'temple-run', 'rabbit-samurai',
      'red-ball', 'jump', 'hop', 'run', 'platform', 'squish-run', 'dark-runner',
      'bunny-hop', 'geometry-dash', 'color-tunnel', 'tunnel-rush', 'super-tunnel',
      'crazy-tunnel', 'slope', 'slopey', 'descent', 'stair-race', 'stack-bump',
      'rolly-vortex', 'doodle-jump', 'candy-jump', 'bottle-flip', 'sling-kong',
      'tomb-of-the-mask', 'ape-sling', 'noob-hook', 'stickman-hook',
      'blumgi-rocket', 'blumgi-slime', 'poor-bunny', 'double-panda',
      'icy-purple-head', 'heart-star', 'odd-bot-out', 'escape', 'fleeing',
      'bob-the-robber', 'stealing', 'breaking-the-bank'], 'platformer'),

    # 2-PLAYER
    (['2-player', 'duo-', '2player', 'multiplayer-2', 'thumb-fighter',
      'drunken-duel', 'boxing-random', 'volleyball-challenge', 'volley-random',
      'basket-random', 'sumo-party', 'tube-jumpers', 'rowdy-wrestling',
      'rowdy-city-wrestling', 'getaway-shootout', 'rooftop-snipers',
      'minibattles', '12-mini-battles', '12-minibattles', '1v1-battle',
      'basketball-legends', 'football-legends', 'soccer-random',
      'tictactoe', 'ultimate-tic-tac-toe', 'impossible-tic-tac-toe',
      'four-in-a-row', 'moto-space-racing-2-player', 'ludo-multiplayer',
      'tank-trouble', 'gun-mayhem', 'bumper-cars-soccer', 'ping-pong-chaos',
      'air-hockey', 'paper-fighter', 'flip-bros', 'dino-bros', 'kart-bros',
      'zoom-be', 'fireboy-and-watergirl', 'house-of-hazards',
      'stickman-army-team', 'strikers-dummies'], '2-player'),

    # FIGHTING
    (['fighting', 'fight', 'boxing', 'brawl', 'battle', 'warrior', 'wrestler',
      'wrestling', 'combat', 'duel', 'martial', 'punch', 'kick', 'iron-snout',
      'big-shot-boxing', 'bearsus', 'wrassling', 'stick-fighter', 'stickman-fight',
      'stickman-fighter', 'stickman-boxing', 'stickman-warriors', 'paper-fighter',
      'robot', 'puppet-master', 'happy-room', 'ragdoll', 'stickman-ragdoll',
      'stickman-crazy-box', 'gang', 'mafia', 'street-ball-jam'], 'fighting'),

    # DRIVING
    (['driving', 'driver', 'car-', 'cars-', 'truck', 'vehicle', 'road-',
      'traffic-', 'parking', 'drift', 'burnin-rubber', 'burnout', 'madalin',
      'extreme-car', 'city-car', 'real-car', 'real-city-driving', 'evo-city',
      'draw-the-hill', 'drive-mad', 'eggy-car', 'death-chase', 'jelly-truck',
      'noob-drive', 'blocky-cars', 'kart-', 'go-kart', 'car-climb', 'car-rush',
      'car-eats-car', 'car-simulator', 'demolition', 'school-bus', 'truck-loader',
      'moving-truck', 'off-road', 'offroader', 'monster-track', 'monsters-wheels',
      'real-simulator-monster', '3d-monster-truck', '3d-car-simulator',
      'impossible-monster-truck', 'stock-car', 'grand-prix', 'slot-car',
      'cyber-cars', 'merge-cyber-racers', 'merge-round-racers', 'merge-car',
      'tiny-town-racing', 'stunt-car', 'city-rider', 'car-rush',
      '18-wheeler', '4x4-drive', 'city-bike', 'mad-truck', 'short-ride',
      'shortcut-race'], 'driving'),

    # PUZZLE
    (['puzzle', 'brain', 'block-puzzle', 'block-the-pig', 'bloxorz', 'tetra',
      'tetris', 'element-block', 'wood-block', 'color-sort', 'water-color',
      'maze', 'minesweeper', 'solitaire', 'spider-solitaire', 'wordle',
      'word-city', 'words-search', 'mosaic', 'yarn-untangle', 'shape-fold',
      'detective', 'mystery', 'infinity-loop', 'cat-trap', 'blob-drop',
      'blumgi-bloom', 'blumgi-ball', 'factory-balls', 'snail-bob',
      'two-neon-boxes', 'boxrob', 'odd-bot', 'free-the-key', 'escape',
      'forgotten-hill', 'there-is-no-game', 'brain-test', 'arithmetica',
      '2048', 'master-chess', 'master-checkers', 'hextris', 'four-in-a-row',
      'snakes-and-ladders', 'ludo-', 'panda-bubble', 'bubble-shooter',
      'amazing-bubble', 'mystical-birdlink', 'bubbles-cool', 'bubble-trouble',
      'pop-it', 'merge-cakes', 'merge-fellas', 'merge-party', 'super-hexbee',
      'cubes-king', 'cubito', 'stack', 'stacktris', 'doodle-champ',
      'farm', 'craftomation', 'pack-a-bag', 'three-goblets', 'who-is',
      'sink-it', 'tap-road-beat', 'slime-road', 'slime-laboratory',
      'perfect-peel', 'where-is-my-cat', 'grass-land', 'chicken-merge',
      'pig-block', 'apple'], 'puzzle'),

    # MULTIPLAYER
    (['multiplayer', '-io', 'sharkio', 'paper-io', 'vectaria', 'nightpoint',
      'slope-2-multiplayer', 'pixwars', 'ludo-multiplayer', 'smash-karts',
      'kart-wars', 'bomb', 'house-of-hazards', 'hide-and-smash',
      'among-us', 'narrow-one', 'getaway-shootout', 'starblast'], 'multiplayer'),

    # ACTION
    (['action', 'zombie', 'war-', 'battle', 'defend', 'defense', 'tower-defense',
      'bloons', 'age-of-war', 'blumgi-castle', 'blumgi-dragon', 'hills-of-steel',
      'angry', 'beast', 'monster', 'zombie-derby', 'zombie-siege', 'zombie-outbreak',
      'stupid-zombies', 'eggbot-vs-zombie', 'cat-gunner', 'survivor-',
      'bullet-force', 'bullet-bros', 'fury-wars', 'neon-war', 'pixwars',
      'shoot-stickman', 'stickman-archero', 'stickman-army', 'stick-defenders',
      'gangster', 'mob-city', 'mafia-wars', 'murder', 'rio-rex',
      'superbrawl', 'supernova', 'superbattle', 'zombie', 'lands-of-blight',
      'izowave', 'fortz', 'happy-room', 'ragdoll-playground', 'bacon-may-die',
      'scrap-divers', 'cave-blast', 'guns', 'gun-mayhem', 'gunspin',
      'hammer', 'fruits', 'fruit-ninja', 'mad-day', 'blumgi-slime', 'avalanche',
      'dyna-boy', 'earn-to-die', 'burrito-bison', 'falling', 'explosion',
      'total-recoil', 'bomb', 'bomber', 'clash-of-tanks', 'tank-trouble',
      'awesome-tanks', 'rusher-crusher', 'running', 'rush'], 'action'),

    # SKILL
    (['skill', 'dunk', 'flappy', 'hyper', 'geometry', 'ball', 'curve-ball',
      'darts', 'archery', 'archer', 'blumgi-rocket', 'stack-ball',
      'rolly-vortex', 'slope', 'tunnel', 'roll', 'flip', 'trick', 'tricks',
      'a-dance-of-fire', 'tap', 'twitch', 'reflexes', 'aim', 'crossy',
      'stickman-bridge', 'bridge', 'marble-dash', 'squish', 'two-button',
      'g-switch', 'bouncy', 'doodle-jump', 'color-tunnel', 'cluster-rush',
      'icy-purple', 'dead', 'duck-life', 'athletics', 'javelin', 'long-jump',
      'sprint', 'run', 'speed', 'surf', 'score', 'shot', 'penalty',
      'free-kick', 'dunkbrush', 'dunk-perfect', 'bottle-flip', 'dunkers',
      'street-ball', 'basketball-frvr', 'basket-and-ball', 'basket-swooshes',
      'blumgi-ball', 'raft-wars', 'rocket-pult', 'sausage-flip', 'noob-hook',
      'stickman-hook', 'ape-sling', 'swingo', 'sling-drift', 'ring',
      'dart', 'bowl', 'bowling-stars', 'golf', 'golfinity', 'battle-golf',
      'stickman-golf', '8-ball-pool', '9-ball-pool', 'pool-club'], 'skill'),

    # ADVENTURE
    (['adventure', 'rpg', 'quest', 'explore', 'dungeon', 'hero', 'legend',
      'wizard', 'dragon', 'kingdom', 'castle', 'blumgi-castle', 'blumgi-dragon',
      'tower-of-destiny', 'life-the-game', 'bitlife', 'eugenes-life',
      'duck-life', 'dog-simulator', 'cat-', 'animal-arena', 'fox-simulator',
      'tiger-simulator', 'horse-simulator', 'panda-simulator', 'deer-simulator',
      'dragon-simulator', 'village-craft', 'minecraft', 'craftomation',
      'dog', 'cow-bay', 'cozy', 'misland', 'island', 'snail-bob',
      'doodle-champion', 'crossy-road', 'temple-of-boom', 'three-goblets',
      'forgotten-hill', 'there-is-no-game', 'all-star-blast', 'among-us',
      'bacon-may-die', 'bearsus', 'a-pretty-odd-bunny', 'fnf', 'music',
      'rhythm', 'westoon', 'game-of-farmers', 'orange', 'blumgi-bloom',
      'shady-bears', 'dog-', 'fish', 'tiny-fishing', 'world-cup',
      'cricket-world-cup', 'amazing-', 'aqua-thrills', 'catpad',
      'lovely-fox', 'doodle', 'deep', 'deepest-sword'], 'adventure'),

    # RACING
    (['racing', 'race', 'racer', 'moto-x3m', 'moto-road', 'moto-trial',
      'moto-maniac', 'highway-bike', 'highway-racer', 'highway-rider',
      'superbike', 'super-bike', 'super-mx', 'super-racing', 'stickman-bike',
      'bike-trials', 'blocky-trials', 'moto-', 'motorbike', 'dirt-bike',
      'speed-boat', 'speed-stars', 'drift-boss', 'drift-hunters',
      'smash-karts', 'kart-race', 'kart-bros', 'go-kart', 'slot-car',
      'grand-prix', 'furious-racing', 'shortcut-race', 'rally',
      'turbo-moto', 'extreme-off-road', '3d-moto', 'retro-highway',
      'death-run', 'death-chase', 'cluster-rush', 'stunt-car',
      'super-star-car', 'top-speed', 'tanuki-sunset', 'road-', 'trail',
      '4x4', 'atv', 'vehicle-race', 'my-pony', 'horse-race', 'bicycle',
      'unicycle', 'hover-racer', '2048-watermelon', '11-11'], 'racing'),

    # STRATEGY
    (['strategy', 'chess', 'checkers', 'tower-defense', 'bloons', 'idle',
      'merge', 'tycoon', 'clicker', 'miner', 'mining', 'empire', 'city',
      'build', 'craft', 'simulate', 'manage', 'war', 'age-of-war',
      'izowave', 'fortz', 'stick-merge', 'blumgi-castle', 'stick-defenders',
      'mini-battles', 'master-chess', 'master-checkers', 'snakes-and-ladders',
      'ludo-', 'four-in-a-row', 'gobble', 'solitaire', 'lands-of-blight',
      'stickman-army', 'gun-mayhem', 'village-craft', 'game-of-farmers',
      'craftomation'], 'strategy'),

    # SPORTS
    (['sport', 'football', 'soccer', 'basketball', 'baseball', 'tennis',
      'golf', 'boxing', 'volleyball', 'cricket', 'rugby', 'hockey',
      'ping-pong', 'badminton', 'archery', 'athletics', 'swimming',
      'head-soccer', 'heads-arena', 'football-legends', 'football-blitz',
      'football-masters', 'football-penalty', 'foot-chinko', 'free-kick',
      'penalty-shooters', 'soccer-skills', 'soccer-random', 'a-small-world-cup',
      'kix-dream-soccer', 'super-liquid-soccer', 'bumper-cars-soccer',
      'rocket-soccer-derby', 'basketball-stars', 'basketball-legends',
      'basketball-frvr', 'basket-', 'bouncy-basketball', 'dunk',
      'court-kings', 'retro-bowl', '4th-and-goal', 'linebacker',
      'touchdown', 'rugby-rush', 'little-master-cricket', 'bowler',
      'bowling-stars', 'darts-pro', 'volley-random', 'volleyball-challenge',
      'power-badminton', 'street-ball', 'battle-golf', 'golf-champions',
      'golfinity', 'stickman-golf', 'slalom-hero', 'wrestling',
      'rowdy-wrestling', 'rowdy-city-wrestling', 'air-hockey', 'sumo',
      'snow-rider', '2-minute-football', '8-ball-pool', '9-ball-pool',
      'pool-club', 'curve-ball', 'dunkbrush', 'dunkers', 'basket-bro',
      'basketbros'], 'sports'),

    # SIMULATION
    (['simulation', 'simulator', 'sim', 'life', 'manage', 'idle', 'tycoon',
      'build', 'city', 'bitlife', 'life-the-game', 'eugenes-life',
      'dog-simulator', 'fox-simulator', 'tiger-simulator', 'horse-simulator',
      'panda-simulator', 'deer-simulator', 'dragon-simulator', 'village-craft',
      'minecraft', 'craftomation', 'game-of-farmers', 'monkey-mart',
      'papas-', 'cozy-room', 'tiny-fishing', 'park-it', 'parking',
      'truck-loader', 'become-a-puppy', 'horse-shoeing', 'doctor-hero',
      'idle-ants', 'idle-breakout', 'idle-digging', 'idle-gold',
      'idle-lumber', 'idle-mining', 'idle-startup', 'idle-zoo',
      'doge-miner', 'space-major-miner', 'digging-master',
      'cookie-clicker', 'blobby-clicker', 'italian-brainrot-clicker',
      'misland', 'chicky-farm', 'real-city-driving'], 'simulation'),

    # CLICKER
    (['clicker', 'cookie-clicker', 'idle', 'blobby-clicker', 'italian-brainrot',
      'doge-miner', 'idle-ants', 'idle-breakout', 'idle-digging',
      'idle-gold', 'idle-lumber', 'idle-mining', 'idle-startup', 'idle-zoo',
      'space-major-miner', 'digging-master'], 'clicker'),

    # HORROR
    (['horror', 'five-nights', 'fnaf', 'scary', 'zombie', 'ghost',
      'dark', 'spooky', 'evil', 'creep', 'moto-x3m-spooky',
      'forgotten-hill', 'murder', 'survival', 'survivor', 'escape',
      'breaking-the-bank', 'bob-the-robber', 'stealing', 'fleeing',
      'escaping'], 'horror'),

    # KIDS
    (['kids', 'pony', 'puppy', 'dressup', 'peppa', 'baby', 'cute',
      'animal', 'bunny', 'kitty', 'duck-life', 'chicky', 'chicken',
      'a-pretty-odd-bunny', 'lovely-fox', 'cozy-room', 'panda',
      'become-a-puppy', 'horse-shoeing', 'dinosaur-game', 'google-snake',
      'doodle-jump', 'flappy-bird', 'crossy-road', 'pac-man',
      'monkey-mart', 'papas-', 'merge-cakes', 'fruit-ninja',
      'candy', 'bubble', 'pop-it', 'snail-bob', 'shape-fold'], 'kids'),
]

def slug_to_title(slug):
    return ' '.join(w.capitalize() for w in slug.replace('-', ' ').split())

def clean_title(slug):
    """Build a clean title from slug, no Unblocked/Free 2 suffix."""
    return slug_to_title(slug)

def get_categories(slug):
    """Return category list for a game based on keyword rules."""
    cats = set()
    slug_lower = slug.lower()
    for keywords, cat in KEYWORD_RULES:
        for kw in keywords:
            if kw in slug_lower:
                cats.add(cat)
                break
    if not cats:
        cats.add('action')  # fallback
    return sorted(cats)

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

# ── SHARED HTML COMPONENTS ────────────────────────────────────────────────────

GTAG = f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GTAG_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GTAG_ID}');
</script>'''

SHARED_CSS = '''<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,sans-serif;background:#0a0e1a;color:#dce8ff;line-height:1.6;min-height:100vh}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.wrap{max-width:1280px;margin:0 auto;padding:0 16px}
.site-header{background:linear-gradient(90deg,#001a6e,#0d1f6e 40%,#1a0a2e 65%,#8b0000);
  border-bottom:3px solid #c0392b;position:sticky;top:0;z-index:100;
  box-shadow:0 4px 20px rgba(0,0,0,.7)}
.hdr-inner{display:flex;align-items:center;gap:12px;padding:10px 16px;flex-wrap:wrap}
.logo{font-weight:800;font-size:1.25rem;color:#fff;white-space:nowrap;text-shadow:0 0 16px rgba(192,57,43,.7)}
.logo:hover{text-shadow:0 0 24px rgba(192,57,43,1)}
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
#searchDrop .no-res,.no-res{padding:12px;color:rgba(255,255,255,.4);text-align:center;font-size:.83rem}
.nav-toggle{display:none;background:none;border:none;color:#fff;font-size:1.4rem;cursor:pointer;padding:.3rem .5rem}
.main-nav{background:linear-gradient(90deg,#001050,#0d1560 40%,#1a0825 70%,#500010);
  border-top:1px solid rgba(255,255,255,.06)}
.main-nav ul{list-style:none;display:flex;flex-wrap:wrap;justify-content:center;
  gap:4px;padding:8px 16px;max-width:1280px;margin:0 auto}
.main-nav a{color:rgba(255,255,255,.85);padding:4px 11px;border-radius:20px;
  font-size:.8rem;font-weight:600;border:1px solid transparent;white-space:nowrap;
  transition:background .15s,color .15s}
.main-nav a:hover,.main-nav a.active{background:rgba(192,57,43,.35);color:#fff;border-color:rgba(192,57,43,.4)}
.site-footer{background:#060b18;border-top:2px solid #c0392b;padding:28px 16px;margin-top:48px;text-align:center}
.footer-cats{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-bottom:14px}
.footer-cats a{background:rgba(255,255,255,.07);padding:4px 11px;border-radius:16px;font-size:.78rem}
.footer-cats a:hover{background:rgba(192,57,43,.3)}
.footer-links{display:flex;gap:16px;justify-content:center;margin-bottom:10px;font-size:.82rem;opacity:.7;flex-wrap:wrap}
.footer-links a:hover{opacity:1}
.footer-copy{font-size:.75rem;opacity:.35}
.games-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:16px 0}
.game-card{display:flex;flex-direction:column;background:#111827;border-radius:10px;
  overflow:hidden;border:1px solid rgba(255,255,255,.07);transition:transform .2s,box-shadow .2s,border-color .2s}
.game-card:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,0,0,.5);border-color:rgba(192,57,43,.4)}
.game-card img{width:100%;height:110px;object-fit:cover}
.game-card span{padding:7px 8px;font-size:.78rem;text-align:center;font-weight:500;line-height:1.3}
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
document.getElementById('navToggle')?.addEventListener('click',()=>
  document.getElementById('navMenu')?.classList.toggle('open'));
(function(){
  var inp=document.getElementById('searchInput');
  var drop=document.getElementById('searchDrop');
  var btn=document.getElementById('searchBtn');
  if(!inp||!drop)return;
  var _games=null;
  function loadGames(cb){
    if(_games)return cb(_games);
    fetch('/search-index.json').then(r=>r.json()).then(d=>{_games=d;cb(d);}).catch(()=>cb([]));
  }
  function close(){drop.classList.remove('open');drop.innerHTML='';}
  inp.addEventListener('input',function(){
    var q=this.value.trim();
    if(!q){close();return;}
    loadGames(function(games){
      var t=q.toLowerCase();
      var res=games.filter(g=>g.title.toLowerCase().includes(t)||g.slug.replace(/-/g,' ').includes(t)).slice(0,8);
      if(!res.length){
        drop.innerHTML='<div class="no-res">No results for "'+q+'"</div>';
      } else {
        drop.innerHTML=res.map(g=>
          '<a href="/'+g.slug+'"><img src="'+g.image+'" alt="'+g.title+'" loading="lazy"><span>'+g.title+'</span></a>'
        ).join('');
      }
      drop.classList.add('open');
    });
  });
  inp.addEventListener('keydown',function(e){
    if(e.key==='Enter'){var q=inp.value.trim();if(q){close();window.location='/?q='+encodeURIComponent(q);}}
    if(e.key==='Escape')close();
  });
  btn.addEventListener('click',function(){var q=inp.value.trim();if(q){close();window.location='/?q='+encodeURIComponent(q);}});
  document.addEventListener('click',function(e){if(!e.target.closest('.search-wrap'))close();});
})();
</script>'''

def nav_html(prefix='/'):
    links = '\n    '.join(
        f'<li><a href="{prefix}categ/{k}/">{v}</a></li>'
        for k, v in CATS.items()
    )
    logo = prefix
    return f'''<header class="site-header">
  <div class="wrap hdr-inner">
    <a href="{logo}" class="logo">🎮 Unblocked Games USA</a>
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

def footer_html(prefix='/'):
    cats = ' '.join(
        f'<a href="{prefix}categ/{k}/">{v}</a>'
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

# ── CATEGORY PAGE BUILDER ─────────────────────────────────────────────────────

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
.other-cats{margin:36px 0 0}
.other-cats h2{font-size:1.1rem;font-weight:700;color:#4fa3ff;margin-bottom:12px}
.other-cats div{display:flex;flex-wrap:wrap;gap:8px}
.other-cats a{background:#111827;padding:6px 13px;border-radius:16px;font-size:.82rem;border:1px solid rgba(255,255,255,.07)}
.other-cats a:hover{background:#1a2a4a}
</style>'''

def build_categ_page(cat_slug, cat_label, games_on_page, page_num, total_pages, total_count):
    cards = '\n    '.join(
        f'<a class="game-card" href="/{g}/">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{clean_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{clean_title(g)} Unblocked</span></a>'
        for g in games_on_page
    )
    pag = ''
    if page_num > 1:
        prev_url = f'/categ/{cat_slug}/' if page_num == 2 else f'/categ/{cat_slug}-page-{page_num-1}/'
        pag += f'<a href="{prev_url}">&laquo; Prev</a>'
    for p in range(1, total_pages+1):
        url = f'/categ/{cat_slug}/' if p == 1 else f'/categ/{cat_slug}-page-{p}/'
        cls = ' class="cur"' if p == page_num else ''
        pag += f'<a href="{url}"{cls}>{p}</a>'
    if page_num < total_pages:
        next_url = f'/categ/{cat_slug}-page-{page_num+1}/'
        pag += f'<a href="{next_url}">Next &raquo;</a>'
    others = ' '.join(
        f'<a href="/categ/{k}/">{v}</a>'
        for k, v in CATS.items() if k != cat_slug
    )
    page_suffix = f' – Page {page_num}' if page_num > 1 else ''
    canon = f'{BASE_URL}/categ/{cat_slug}/' if page_num == 1 else f'{BASE_URL}/categ/{cat_slug}-page-{page_num}/'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cat_label} Games Unblocked{page_suffix} – Free Online | Unblocked Games USA</title>
<meta name="description" content="Play {total_count} free unblocked {cat_label} games online. No downloads, works at school instantly.">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index,follow">
{GTAG}
{CATEG_CSS}
</head>
<body>
{nav_html('/')}
<div class="wrap">
  <div class="categ-hero">
    <h1>{cat_label} Unblocked Games</h1>
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
{footer_html('/')}
{SHARED_JS}
</body>
</html>'''

# ── GAME PAGE BUILDER ─────────────────────────────────────────────────────────

GAME_CSS = SHARED_CSS + '''<style>
.game-section{padding:20px 0}
.game-title-bar{text-align:center;margin-bottom:16px}
.game-title-bar h1{font-size:clamp(1.4rem,4vw,2.2rem);font-weight:800;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.game-title-bar p{color:rgba(255,255,255,.6);font-size:.95rem;margin-top:6px}
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
.game-frame{position:absolute;inset:0;width:100%;height:100%;border:none;display:none;z-index:2}
.game-frame.active{display:block}
.fs-btn{position:absolute;bottom:10px;right:10px;z-index:4;
  background:rgba(0,0,0,.65);color:#fff;border:none;border-radius:6px;
  padding:5px 12px;cursor:pointer;font-size:.82rem}
.fs-btn:hover{background:#c0392b}
.game-desc{background:#111827;border-radius:10px;padding:24px;margin:20px 0;
  border:1px solid rgba(255,255,255,.07)}
.game-desc h2{font-size:1.3rem;font-weight:700;color:#e74c3c;margin-bottom:10px}
.game-desc h3{font-size:1.05rem;font-weight:700;color:#e74c3c;margin:16px 0 8px}
.game-desc p{margin-bottom:10px;color:rgba(255,255,255,.8);font-size:.95rem}
.game-thumb-sm{float:left;width:120px;border-radius:8px;margin:0 16px 12px 0;
  border:1px solid rgba(255,255,255,.1)}
.cat-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.cat-tag{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(192,57,43,.6));
  color:#fff;border-radius:20px;padding:.3rem .9rem;font-size:.82rem;font-weight:600;
  border:1px solid rgba(255,255,255,.1)}
.cat-tag:hover{background:linear-gradient(135deg,#1a3a8a,#c0392b)}
.similar-section{margin:28px 0}
.section-heading{font-size:1.25rem;font-weight:700;margin-bottom:14px;
  background:linear-gradient(135deg,#4fa3ff,#ff4444);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.browse-section{margin:28px 0}
.cat-grid{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;
  padding:16px 20px;background:linear-gradient(135deg,#0a1540,#1a0825);
  border-radius:40px;border:1px solid rgba(192,57,43,.2)}
.cat-item{background:linear-gradient(135deg,rgba(26,58,138,.7),rgba(192,57,43,.55));
  color:#fff;border-radius:20px;padding:.35rem 1rem;font-size:.85rem;font-weight:600;
  border:1px solid rgba(255,255,255,.1);white-space:nowrap}
.cat-item:hover{background:linear-gradient(135deg,#1a3a8a,#c0392b)}
</style>'''

GAME_JS = '''<script>
(function(){
  var overlay=document.getElementById('gameOverlay');
  var frame=document.getElementById('gameFrame');
  var thumb=document.getElementById('gameThumb');
  if(!overlay||!frame)return;
  function launch(){
    var src=frame.getAttribute('data-src');
    if(!src)return;
    frame.src=src;
    frame.classList.add('active');
    overlay.style.display='none';
    if(thumb)thumb.style.display='none';
  }
  overlay.addEventListener('click',launch);
  overlay.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' ')launch();});
})();
document.getElementById('fsBtn')?.addEventListener('click',function(){
  var el=document.getElementById('gameFrameWrap');
  (el.requestFullscreen||el.webkitRequestFullscreen||el.mozRequestFullScreen||function(){}).call(el);
});
</script>'''

def similar_games(current, all_g, count=12):
    others = [g for g in all_g if g != current]
    idx = next((i for i,g in enumerate(others) if g >= current), 0)
    picks = others[max(0,idx-2):idx+count] + others[:3]
    seen, final = set(), []
    for g in picks:
        if g not in seen:
            seen.add(g); final.append(g)
        if len(final) == count: break
    return '\n    '.join(
        f'<a class="game-card" href="/{g}/">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{clean_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{clean_title(g)} Unblocked</span></a>'
        for g in final
    )

def build_game_page(slug, iframe_src, cats, all_g):
    title = clean_title(slug)
    cat_tags = '\n    '.join(
        f'<a href="/categ/{c}/" class="cat-tag">{CATS[c]}</a>'
        for c in cats if c in CATS
    ) or f'<a href="/categ/action/" class="cat-tag">💥 Action</a>'
    cat_items = '\n      '.join(
        f'<a href="/categ/{k}/" class="cat-item">{v}</a>'
        for k, v in CATS.items()
    )
    if not iframe_src:
        iframe_src = f'https://iframe.unblocked-76-games.org/{slug}'
    desc = f'Play {title} free in your browser — no download needed!'
    sim = similar_games(slug, all_g)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} Unblocked – Play Free Online | Unblocked Games USA</title>
<meta name="description" content="Play {title} unblocked online for free. Works at school instantly — no download needed!">
<link rel="canonical" href="{BASE_URL}/{slug}/">
<meta property="og:title" content="{title} Unblocked – Free Online">
<meta property="og:description" content="Play {title} free, no download, works at school.">
<meta property="og:url" content="{BASE_URL}/{slug}/">
<meta property="og:image" content="{IMG_BASE}/{slug}.png">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow,max-image-preview:large">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"VideoGame",
"name":"{title}","url":"{BASE_URL}/{slug}/",
"description":"{desc}",
"applicationCategory":"Game","operatingSystem":"Web Browser",
"offers":{{"@type":"Offer","price":"0","priceCurrency":"USD"}},
"image":"{IMG_BASE}/{slug}.png",
"genre":{json.dumps(cats)},
"provider":{{"@type":"Organization","name":"Unblocked Games USA","url":"{BASE_URL}/"}}}}</script>
<link rel="icon" href="/favicon.ico">
{GTAG}
{GAME_CSS}
</head>
<body>
{nav_html('/')}
<div class="wrap game-section">
  <div class="game-title-bar">
    <h1>{title} Unblocked</h1>
    <p>{desc}</p>
  </div>
  <div class="game-frame-wrap" id="gameFrameWrap">
    <img id="gameThumb" class="game-thumb" src="{IMG_BASE}/{slug}.png" alt="{title} preview">
    <div id="gameOverlay" class="game-overlay" role="button" tabindex="0" aria-label="Play {title}">
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
    <p>{desc}</p>
    <h3>How to Play</h3>
    <p>Use your mouse or keyboard to play. Click the Play button above to start instantly — no download needed!</p>
    <div class="cat-tags" style="clear:both">
      {cat_tags}
    </div>
  </div>
  <section class="similar-section">
    <h2 class="section-heading">🎮 Similar Games</h2>
    <div class="games-grid">
      {sim}
    </div>
  </section>
  <div class="browse-section">
    <h2 class="section-heading">🗂️ Browse by Category</h2>
    <div class="cat-grid">
      {cat_items}
    </div>
  </div>
</div>
{footer_html('/')}
{SHARED_JS}
{GAME_JS}
</body>
</html>'''

# ── HOMEPAGE BUILDER ──────────────────────────────────────────────────────────

def build_homepage(games):
    n = len(games)
    cards = '\n    '.join(
        f'<a class="game-card" href="/{g}/">'
        f'<img src="{IMG_BASE}/{g}.png" alt="{clean_title(g)} Unblocked" loading="lazy" width="150" height="110">'
        f'<span>{clean_title(g)} Unblocked</span></a>'
        for g in games[:60]
    )
    cat_browse = '\n '.join(
        f'<a href="/categ/{k}/" style="background:#21262d;padding:7px 14px;border-radius:20px;font-size:.85rem;color:#e6edf3">{v}</a>'
        for k, v in CATS.items()
    )
    homepage_css = SHARED_CSS + '''<style>
.hero{text-align:center;padding:36px 0 24px}
.hero h1{font-size:2rem;margin-bottom:8px}
.badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:24px}
.badge{background:#21262d;padding:6px 14px;border-radius:20px;font-size:.85rem}
.search-all-btn{background:#58a6ff;color:#000;border:none;padding:10px 28px;border-radius:24px;font-size:1rem;cursor:pointer;font-weight:700}
.section-h{font-size:1.2rem;color:#58a6ff;margin-bottom:12px}
.cat-browse{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0 32px}
#fullSearchModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9999;overflow-y:auto;padding:70px 20px 20px}
#fullSearchModal.on{display:block}
#fullSearchClose{position:fixed;top:14px;right:18px;background:#c0392b;color:#fff;border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:1.1rem;z-index:10000}
#fullSearchInput{width:100%;max-width:860px;display:block;margin:0 auto 12px;padding:12px 18px;font-size:1.1rem;border-radius:10px;border:none;background:#161b22;color:#fff;outline:none}
#fullSearchStatus{text-align:center;color:#f85149;margin-bottom:12px;max-width:860px;margin-left:auto;margin-right:auto}
#fullSearchGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;max-width:860px;margin:0 auto}
</style>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unblocked Games USA – Free Games To Play Online Instantly</title>
<meta name="description" content="Play {n}+ free unblocked games online. No downloads, no sign-ups. Works at school instantly.">
<link rel="canonical" href="{BASE_URL}/">
<meta name="robots" content="index,follow">
{GTAG}
{homepage_css}
</head>
<body>
{nav_html('/')}
<main>
  <div class="wrap">
    <div class="hero">
      <h1>🎮 Unblocked Games USA</h1>
      <p style="color:#8b949e;max-width:560px;margin:0 auto 20px">Free games for every break. No downloads, no sign-ups.</p>
      <div class="badges">
        <span class="badge">✅ No Downloads</span>
        <span class="badge">🎮 100% Free</span>
        <span class="badge">⚡ Play Instantly</span>
        <span class="badge">🏫 School Friendly</span>
      </div>
      <button class="search-all-btn" onclick="openSearch()">🔍 Search All {n} Games</button>
    </div>
    <h2 class="section-h">🔥 Popular Games</h2>
    <div class="games-grid">
      {cards}
    </div>
    <h2 class="section-h" style="margin-top:32px">🗂️ Browse by Category</h2>
    <div class="cat-browse">
      {cat_browse}
    </div>
  </div>
</main>
{footer_html('/')}

<div id="fullSearchModal">
  <button id="fullSearchClose" onclick="closeSearch()">✕</button>
  <input id="fullSearchInput" type="search" placeholder="Search all {n} games…" oninput="fullSearch(this.value)" autofocus>
  <div id="fullSearchStatus"></div>
  <div id="fullSearchGrid"></div>
</div>

{SHARED_JS}
<script>
var _allGames=null;
function loadAllGames(cb){{
  if(_allGames)return cb(_allGames);
  fetch('/search-index.json').then(r=>r.json()).then(d=>{{_allGames=d;cb(d);}}).catch(()=>cb([]));
}}
function openSearch(){{
  document.getElementById('fullSearchModal').classList.add('on');
  document.body.style.overflow='hidden';
  var inp=document.getElementById('fullSearchInput');
  inp.focus();
  loadAllGames(function(){{}});
}}
function closeSearch(){{
  document.getElementById('fullSearchModal').classList.remove('on');
  document.body.style.overflow='';
}}
document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeSearch();}});
function fullSearch(q){{
  loadAllGames(function(games){{
    var t=q.toLowerCase().trim();
    var status=document.getElementById('fullSearchStatus');
    var grid=document.getElementById('fullSearchGrid');
    if(!t){{status.textContent='';grid.innerHTML='<p style="color:#8b949e;text-align:center;grid-column:1/-1">Start typing…</p>';return;}}
    var res=games.filter(function(g){{
      return g.title.toLowerCase().includes(t)||g.slug.replace(/-/g,' ').includes(t)||
        (g.categories||[]).some(function(c){{return c.replace(/-/g,' ').includes(t);}});
    }}).slice(0,72);
    if(!res.length){{
      status.innerHTML='<span style="color:#f85149">No games found for &ldquo;'+q+'&rdquo;</span>';
      grid.innerHTML='';
      return;
    }}
    status.textContent='';
    grid.innerHTML=res.map(function(g){{
      return '<a href="/'+g.slug+'/" style="display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:8px;overflow:hidden;color:#e6edf3">'+
        '<img src="'+g.image+'" alt="'+g.title+'" loading="lazy" style="width:100%;height:110px;object-fit:cover">'+
        '<span style="padding:6px;font-size:.78rem;text-align:center">'+g.title+'</span></a>';
    }}).join('');
  }});
}}
</script>
</body>
</html>'''

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    games = all_games()
    print(f'Found {len(games)} games')

    # Build category map
    cat_map = {k: [] for k in CATS}
    game_cats = {}
    for slug in games:
        cats = get_categories(slug)
        game_cats[slug] = cats
        for c in cats:
            if slug not in cat_map[c]:
                cat_map[c].append(slug)

    for k, v in cat_map.items():
        print(f'  {CATS[k]}: {len(v)} games')

    # Get iframe src from existing pages
    print('\nReading existing iframe sources...')
    iframe_map = {}
    for slug in games:
        html = read_html(REPO / slug / 'index.html')
        src = get_iframe_src(html)
        iframe_map[slug] = src

    # Build search-index.json
    print('Building search-index.json...')
    index = [
        {
            'slug': slug,
            'title': f'{clean_title(slug)} Unblocked',
            'image': f'{IMG_BASE}/{slug}.png',
            'categories': game_cats[slug]
        }
        for slug in games
    ]
    (REPO / 'search-index.json').write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')
    print(f'  Written {len(index)} entries to search-index.json')

    # Rebuild game pages
    print(f'\nRebuilding {len(games)} game pages...')
    for i, slug in enumerate(games):
        html = build_game_page(slug, iframe_map[slug], game_cats[slug], games)
        (REPO / slug / 'index.html').write_text(html, encoding='utf-8')
        if (i+1) % 100 == 0:
            print(f'  {i+1}/{len(games)}')
    print(f'  Done')

    # Rebuild category pages
    print('\nRebuilding category pages...')
    categ_root = REPO / 'categ'
    categ_root.mkdir(exist_ok=True)
    for cat_slug, cat_label in CATS.items():
        cat_games = cat_map[cat_slug]
        if not cat_games:
            print(f'  SKIP {cat_label} (0 games)')
            continue
        total = len(cat_games)
        n_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
        for p in range(1, n_pages+1):
            chunk = cat_games[(p-1)*PER_PAGE : p*PER_PAGE]
            folder_name = cat_slug if p == 1 else f'{cat_slug}-page-{p}'
            folder = categ_root / folder_name
            folder.mkdir(parents=True, exist_ok=True)
            html = build_categ_page(cat_slug, cat_label, chunk, p, n_pages, total)
            (folder / 'index.html').write_text(html, encoding='utf-8')
        print(f'  {cat_label}: {total} games, {n_pages} page(s)')

    # Rebuild homepage
    print('\nRebuilding homepage...')
    (REPO / 'index.html').write_text(build_homepage(games), encoding='utf-8')
    print('  Done')

    print('''
✅ All fixes applied!

Summary of fixes:
1. ✅ Category pages now show only relevant games (keyword-based mapping)
2. ✅ search-index.json generated (search now works)
3. ✅ Game titles cleaned (no more "— Free 2" suffix)
4. ✅ Google Analytics (gtag) added to all pages
5. ✅ Nav links use proper /categ/slug/ URLs
6. ✅ Homepage search modal works with search-index.json

Next steps:
  cd /home/claude/repo
  git add -A
  git commit -m "Fix: category filtering, search, titles, gtag integration"
  git push
''')

if __name__ == '__main__':
    main()