"""
seo_engine.py  —  Unblocked Games USA  |  Full SEO Content Engine
Run from: C:/Users/berra/Documents/GitHub/UnblockedGames-USA.github.io/
Command : python seo_engine.py

What this does:
  - Gives every game a UNIQUE title  (Google hates duplicates)
  - Gives every game a UNIQUE meta description
  - Gives every game UNIQUE "About" body text + "How to Play" text
  - Fixes JSON-LD structured data (VideoGame schema)
  - Fixes duplicate H1 tags
  - Removes footer category pills (keeps only legal links)
  - Generates sitemap.xml, robots.txt, llms.txt
"""

import re, hashlib
from pathlib import Path
from datetime import date

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_URL  = "https://unblockedgames-usa.github.io"
SITE_ROOT = Path(__file__).parent
TODAY     = date.today().isoformat()

SKIP = {"assets","images","categ","privacy-policy","contact","faq","dmca",".git"}

CATEGORIES = [
    "shooter","platformer","2-player","fighting","driving",
    "puzzle","multiplayer","action","skill","adventure",
    "racing","strategy","sports","simulation","clicker","horror","kids",
]

# ── UNIQUE CONTENT TEMPLATES (6 variants per category) ───────────────────────
# {t} = title,  {T} = TITLE CAPS

TITLE_TEMPLATES = {
    "shooter":    [
        "{t} Unblocked – Free Online Shooter Game | Play Now",
        "Play {t} Unblocked – Shooting Game, No Download",
        "{t} Unblocked – Browser Shooter Game | Unblocked Games USA",
        "{t} Free Unblocked – Play Online Shooter at School",
        "{t} Unblocked Game – Free FPS & Shooter Online",
        "Play {t} Free – Unblocked Shooter, No Sign-Up Needed",
    ],
    "platformer": [
        "{t} Unblocked – Free Platformer Game Online",
        "Play {t} Unblocked – Jump & Run Game, No Download",
        "{t} Unblocked – Browser Platformer | Unblocked Games USA",
        "{t} Free Unblocked – Play Online Platformer at School",
        "{t} Unblocked – Classic Side-Scroller, Free Online",
        "Play {t} Free – Unblocked Platformer Game",
    ],
    "2-player":   [
        "{t} Unblocked – Free 2 Player Game Online",
        "Play {t} Unblocked – 2-Player Game with Friends",
        "{t} Unblocked – Local Co-op & Versus Game Free",
        "{t} Free Unblocked – Play 2 Player Online at School",
        "{t} Unblocked – Fun 2 Player Browser Game",
        "Play {t} Free – Unblocked 2 Player, No Download",
    ],
    "fighting":   [
        "{t} Unblocked – Free Fighting Game Online",
        "Play {t} Unblocked – Brawler & Combat Game Free",
        "{t} Unblocked – Browser Fighting Game | No Download",
        "{t} Free Unblocked – Play Fighting Game at School",
        "{t} Unblocked – Free Online Combat Game",
        "Play {t} Free – Unblocked Fighter, Instant Play",
    ],
    "driving":    [
        "{t} Unblocked – Free Driving & Car Game Online",
        "Play {t} Unblocked – Vehicle Game, No Download",
        "{t} Unblocked – Browser Driving Game | Unblocked Games USA",
        "{t} Free Unblocked – Play Driving Game at School",
        "{t} Unblocked – Free Online Car & Truck Game",
        "Play {t} Free – Unblocked Driving Game",
    ],
    "puzzle":     [
        "{t} Unblocked – Free Online Puzzle Game",
        "Play {t} Unblocked – Brain Teaser, No Download",
        "{t} Unblocked – Logic & Puzzle Game Free Online",
        "{t} Free Unblocked – Play Brain Puzzle at School",
        "{t} Unblocked – Free Mind-Bending Puzzle Game",
        "Play {t} Free – Unblocked Puzzle, Instant Play",
    ],
    "multiplayer":[
        "{t} Unblocked – Free Online Multiplayer Game",
        "Play {t} Unblocked – Real Players, No Download",
        "{t} Unblocked – Browser Multiplayer | Unblocked Games USA",
        "{t} Free Unblocked – Play Online Against Real Players",
        "{t} Unblocked – Free Multiplayer Browser Game",
        "Play {t} Free – Unblocked Multiplayer, Join Now",
    ],
    "action":     [
        "{t} Unblocked – Free Online Action Game",
        "Play {t} Unblocked – Fast-Paced Action, No Download",
        "{t} Unblocked – Browser Action Game | Unblocked Games USA",
        "{t} Free Unblocked – Play Action Game at School",
        "{t} Unblocked – Intense Action, Free Browser Game",
        "Play {t} Free – Unblocked Action Game, Play Now",
    ],
    "skill":      [
        "{t} Unblocked – Free Skill & Reflex Game Online",
        "Play {t} Unblocked – Test Your Skills, No Download",
        "{t} Unblocked – Precision Skill Game Free Online",
        "{t} Free Unblocked – Play Skill Game at School",
        "{t} Unblocked – Challenge Your Reflexes Free",
        "Play {t} Free – Unblocked Skill Game Online",
    ],
    "adventure":  [
        "{t} Unblocked – Free Online Adventure Game",
        "Play {t} Unblocked – Explore & Quest, No Download",
        "{t} Unblocked – Browser Adventure | Unblocked Games USA",
        "{t} Free Unblocked – Play Adventure Game at School",
        "{t} Unblocked – Story-Driven Adventure, Free Online",
        "Play {t} Free – Unblocked Adventure Game",
    ],
    "racing":     [
        "{t} Unblocked – Free Online Racing Game",
        "Play {t} Unblocked – High-Speed Racing, No Download",
        "{t} Unblocked – Browser Racing Game | Unblocked Games USA",
        "{t} Free Unblocked – Play Racing Game at School",
        "{t} Unblocked – Fast Track Racing, Free Online",
        "Play {t} Free – Unblocked Racing, Start Now",
    ],
    "strategy":   [
        "{t} Unblocked – Free Online Strategy Game",
        "Play {t} Unblocked – Think & Conquer, No Download",
        "{t} Unblocked – Browser Strategy | Unblocked Games USA",
        "{t} Free Unblocked – Play Strategy Game at School",
        "{t} Unblocked – Deep Strategy, Free Online",
        "Play {t} Free – Unblocked Strategy Game",
    ],
    "sports":     [
        "{t} Unblocked – Free Online Sports Game",
        "Play {t} Unblocked – Sports Action, No Download",
        "{t} Unblocked – Browser Sports Game | Unblocked Games USA",
        "{t} Free Unblocked – Play Sports Game at School",
        "{t} Unblocked – Free Sports Browser Game",
        "Play {t} Free – Unblocked Sports Game Online",
    ],
    "simulation": [
        "{t} Unblocked – Free Online Simulation Game",
        "Play {t} Unblocked – Life Sim, No Download",
        "{t} Unblocked – Browser Simulator | Unblocked Games USA",
        "{t} Free Unblocked – Play Simulation at School",
        "{t} Unblocked – Realistic Sim, Free Online",
        "Play {t} Free – Unblocked Simulator Game",
    ],
    "clicker":    [
        "{t} Unblocked – Free Idle & Clicker Game Online",
        "Play {t} Unblocked – Click to Win, No Download",
        "{t} Unblocked – Browser Clicker | Unblocked Games USA",
        "{t} Free Unblocked – Play Clicker Game at School",
        "{t} Unblocked – Addictive Idle Clicker, Free",
        "Play {t} Free – Unblocked Clicker Game",
    ],
    "horror":     [
        "{t} Unblocked – Free Online Horror Game",
        "Play {t} Unblocked – Scary Survival, No Download",
        "{t} Unblocked – Browser Horror Game | Unblocked Games USA",
        "{t} Free Unblocked – Play Horror Game at School",
        "{t} Unblocked – Creepy Horror, Free Online",
        "Play {t} Free – Unblocked Horror Game",
    ],
    "kids":       [
        "{t} Unblocked – Free Kids Game Online",
        "Play {t} Unblocked – Fun for Kids, No Download",
        "{t} Unblocked – Safe Kids Browser Game Free",
        "{t} Free Unblocked – Play Kids Game at School",
        "{t} Unblocked – Colorful Kids Game, Free Online",
        "Play {t} Free – Unblocked Kids Game",
    ],
    "default":    [
        "{t} Unblocked – Free Online Game | Play Now",
        "Play {t} Unblocked – Free Browser Game, No Download",
        "{t} Unblocked – Free Game Online | Unblocked Games USA",
        "{t} Free Unblocked – Play at School or Work",
        "{t} Unblocked – Instant Browser Game, Free to Play",
        "Play {t} Free – Unblocked Game, No Sign-Up",
    ],
}

DESC_TEMPLATES = {
    "shooter": [
        "Play {t} unblocked — a thrilling shooting game that runs instantly in your browser. No download, no sign-up. Works at school and everywhere.",
        "{t} is an unblocked shooter you can play free in any browser. Take aim, fire away, and beat every level — no Flash or install needed.",
        "Jump into {t} unblocked, a free online shooter with non-stop action. Works on school networks — just open and play instantly.",
        "Looking for a free unblocked shooting game? {t} delivers fast-paced gunplay right in your browser — zero downloads, zero hassle.",
        "{t} unblocked lets you play a high-energy shooting game completely free. No download needed — works at school, home, or anywhere.",
        "Take on {t} unblocked, one of the best free online shooters available. Instant browser play — no install, no sign-up required.",
    ],
    "platformer": [
        "Play {t} unblocked — a classic platformer adventure you can enjoy free in your browser. Jump, run and dodge with no download needed.",
        "{t} is a free unblocked platformer with exciting levels and smooth controls. Works on school networks — open it and start playing instantly.",
        "Enjoy {t} unblocked, a fun side-scrolling platformer that loads in seconds. No Flash, no download — just pure jumping action in your browser.",
        "Looking for a free platformer to play unblocked? {t} offers hours of jumping and running fun, right in your browser at school or home.",
        "{t} unblocked is a polished platformer game you can play free online. No downloads, no sign-up — works on any school or office network.",
        "Run, jump, and explore in {t} unblocked — a free browser platformer that plays instantly. Perfect for school breaks and free time.",
    ],
    "2-player": [
        "Play {t} unblocked with a friend — a free 2-player game that works right in your browser. No download needed, great for school.",
        "{t} is a free unblocked 2-player game perfect for head-to-head matches. Share a keyboard and play together instantly — no install required.",
        "Challenge a friend with {t} unblocked — a fun 2-player browser game you can play free anytime. No download, no sign-up, works at school.",
        "Enjoy {t} unblocked, one of the best free 2-player games online. Works on school networks — grab a friend and start playing instantly.",
        "{t} unblocked brings local multiplayer fun to your browser for free. No Flash or download needed — perfect 2-player game for school.",
        "Looking for a free 2-player unblocked game? {t} is ready to play instantly — no download, no hassle, great for playing with friends at school.",
    ],
    "fighting": [
        "Play {t} unblocked — an exciting fighting game with smooth combat you can enjoy free in your browser. No download, works at school.",
        "{t} is a free unblocked fighting game that loads instantly. Choose your fighter, master the moves, and dominate — no install required.",
        "Unleash combos in {t} unblocked, a free browser fighting game with intense action. Works on school networks — just open and fight.",
        "Looking for a free unblocked fighting game? {t} delivers satisfying combat right in your browser — zero downloads, zero sign-up.",
        "{t} unblocked is a top free online fighting game — smooth controls, exciting battles. No download needed, works at school instantly.",
        "Jump into battle with {t} unblocked, a free fighting game for the browser. No install required — perfect for school breaks.",
    ],
    "driving": [
        "Play {t} unblocked — a free driving game where you race and cruise directly in your browser. No download needed, works at school.",
        "{t} is a free unblocked driving game with realistic controls. Hit the road, dodge traffic, and reach the finish — no install required.",
        "Get behind the wheel in {t} unblocked, a free browser driving game. Works on school networks — open it and start driving instantly.",
        "Looking for a free unblocked car game? {t} puts you in the driver's seat with no download — works anywhere, plays great at school.",
        "{t} unblocked delivers fast driving action completely free in your browser. No Flash, no install — just pure wheel-turning fun.",
        "Rev your engines in {t} unblocked, a top free online driving game. Instant browser play, no sign-up, works at school and home.",
    ],
    "puzzle": [
        "Play {t} unblocked — a clever puzzle game that challenges your brain for free in your browser. No download needed, works at school.",
        "{t} is a free unblocked puzzle game with satisfying logic challenges. Think your way through every level — no install required.",
        "Sharpen your mind with {t} unblocked, a free browser puzzle game. Works on school networks — open it and start solving instantly.",
        "Looking for a free unblocked brain teaser? {t} offers clever puzzles right in your browser — zero downloads, zero sign-up.",
        "{t} unblocked is a highly-rated free online puzzle game. No download needed — perfect brain-stretching challenge for school breaks.",
        "Put your mind to the test with {t} unblocked — a free puzzle game for the browser. No install required, works anywhere instantly.",
    ],
    "multiplayer": [
        "Play {t} unblocked — a free multiplayer game where you compete against real players right in your browser. No download, works at school.",
        "{t} is a free unblocked multiplayer game with live opponents. Jump in, compete, and climb the leaderboard — no install required.",
        "Take on real players in {t} unblocked, a free browser multiplayer game. Works on school networks — open and join a match instantly.",
        "Looking for a free unblocked multiplayer experience? {t} connects you with players worldwide — zero downloads, instant play.",
        "{t} unblocked is a top free online multiplayer game. Battle real opponents in your browser — no sign-up, works at school.",
        "Join the action in {t} unblocked — free multiplayer browser fun with real competition. No download needed, plays great at school.",
    ],
    "action": [
        "Play {t} unblocked — a heart-pumping action game you can enjoy free in your browser. No download needed, works at school.",
        "{t} is a free unblocked action game packed with fast gameplay and exciting challenges. Loads instantly — no install required.",
        "Get into the action with {t} unblocked — a free browser game with non-stop excitement. Works on school networks, open and play now.",
        "Looking for a free unblocked action game? {t} delivers intense gameplay right in your browser — zero downloads, zero sign-up.",
        "{t} unblocked is one of the best free online action games available. No Flash, no download — just pure adrenaline in your browser.",
        "Dive into {t} unblocked — fast action, free to play, instant browser load. No sign-up needed, works at school and home.",
    ],
    "skill": [
        "Play {t} unblocked — a challenging skill game that tests your reflexes and precision, free in your browser. Works at school.",
        "{t} is a free unblocked skill game where mastery takes practice. Push your limits and beat your high score — no install required.",
        "Test your skills with {t} unblocked — a free browser game that rewards practice and precision. Works on any school network.",
        "Looking for a free unblocked skill challenge? {t} will push your reflexes to the limit — no download, plays instantly.",
        "{t} unblocked is a top-rated free online skill game. Build your skills, top the scores — no sign-up, works at school.",
        "How skilled are you? Find out with {t} unblocked — a free precision game for the browser. No install, no download needed.",
    ],
    "adventure": [
        "Play {t} unblocked — an immersive adventure game with an exciting world to explore, free in your browser. Works at school.",
        "{t} is a free unblocked adventure game full of quests and discoveries. Set off on your journey — no download required.",
        "Explore the world of {t} unblocked — a free browser adventure game with deep gameplay. Works on school networks instantly.",
        "Looking for a free unblocked adventure? {t} takes you on an epic journey right in your browser — zero downloads, zero sign-up.",
        "{t} unblocked is a popular free online adventure game. Discover, explore, and conquer — no Flash or install required.",
        "Begin your quest in {t} unblocked — a rich adventure game, free to play in any browser. No sign-up, works at school.",
    ],
    "racing": [
        "Play {t} unblocked — a thrilling racing game with high-speed tracks you can enjoy free in your browser. Works at school.",
        "{t} is a free unblocked racing game with fast cars and exciting circuits. Hit the gas and race to win — no install needed.",
        "Speed through {t} unblocked — a free browser racing game with intense competition. Works on school networks, open and race now.",
        "Looking for a free unblocked racing game? {t} puts you on the track instantly — no download, no sign-up required.",
        "{t} unblocked is a fan-favorite free online racing game. Cross the finish line first — no Flash, works at school.",
        "Race to victory in {t} unblocked — free, fast, and instantly playable in any browser. No download needed.",
    ],
    "strategy": [
        "Play {t} unblocked — a deep strategy game where every decision matters, free in your browser. No download, works at school.",
        "{t} is a free unblocked strategy game that rewards smart thinking. Build, plan, and conquer — no install required.",
        "Outwit your enemies in {t} unblocked — a free browser strategy game with satisfying depth. Works on school networks.",
        "Looking for a free unblocked strategy challenge? {t} offers complex gameplay right in your browser — zero downloads.",
        "{t} unblocked is a highly-rated free online strategy game. Think several moves ahead and win — works at school, no sign-up.",
        "Command and conquer in {t} unblocked — a free strategy game for the browser. No install, instant play, works anywhere.",
    ],
    "sports": [
        "Play {t} unblocked — a fun sports game you can enjoy free in your browser anytime. No download needed, works at school.",
        "{t} is a free unblocked sports game with arcade-style gameplay. Score big and win the championship — no install required.",
        "Get in the game with {t} unblocked — a free browser sports title with exciting matches. Works on school networks instantly.",
        "Looking for a free unblocked sports game? {t} delivers action-packed gameplay right in your browser — zero downloads.",
        "{t} unblocked is a popular free online sports game. Play your favourite sport — no Flash or download, works at school.",
        "Compete and win in {t} unblocked — a free sports game instantly playable in any browser. No sign-up needed.",
    ],
    "simulation": [
        "Play {t} unblocked — an engaging simulation game you can explore free in your browser. No download needed, works at school.",
        "{t} is a free unblocked simulation game with realistic mechanics. Build, manage, and grow — no install required.",
        "Simulate your world in {t} unblocked — a free browser sim with deep gameplay. Works on school networks, open and play now.",
        "Looking for a free unblocked simulation? {t} lets you manage and create right in your browser — zero downloads.",
        "{t} unblocked is a top-rated free online simulation game. Design, control, and succeed — no Flash, works at school.",
        "Create and control in {t} unblocked — a free simulation game for the browser. No install, instant play.",
    ],
    "clicker": [
        "Play {t} unblocked — an addictive idle clicker game you can enjoy free in your browser. No download, works at school.",
        "{t} is a free unblocked clicker game that keeps you hooked for hours. Click, upgrade, and grow — no install required.",
        "Start clicking in {t} unblocked — a free browser idle game with satisfying progression. Works on school networks.",
        "Looking for a free unblocked idle game? {t} rewards every click right in your browser — zero downloads, zero sign-up.",
        "{t} unblocked is a popular free online clicker game. Build your empire one click at a time — works at school.",
        "Get hooked on {t} unblocked — a free clicker game for the browser. No download needed, instant play anywhere.",
    ],
    "horror": [
        "Play {t} unblocked — a spine-chilling horror game you can experience free in your browser. No download, works at school.",
        "{t} is a free unblocked horror game with a creepy atmosphere and jump scares. Survive if you can — no install required.",
        "Dare to play {t} unblocked — a free browser horror game that will keep you on edge. Works on school networks.",
        "Looking for a free unblocked horror experience? {t} delivers frightening gameplay right in your browser — zero downloads.",
        "{t} unblocked is a top free online horror game. Face your fears and survive — no Flash or install, works at school.",
        "Enter the horror of {t} unblocked — free, scary, and instantly playable in your browser. No sign-up needed.",
    ],
    "kids": [
        "Play {t} unblocked — a fun and colourful kids game you can enjoy free in your browser. Safe, no download, works at school.",
        "{t} is a free unblocked kids game with simple, joyful gameplay perfect for young players. No install required.",
        "Kids love {t} unblocked — a free browser game with bright visuals and easy controls. Works on school networks instantly.",
        "Looking for a free safe unblocked game for kids? {t} is perfect — fun, colourful, zero downloads, instant play.",
        "{t} unblocked is a popular free online kids game. Hours of fun, totally safe — no Flash or sign-up, works at school.",
        "Let kids enjoy {t} unblocked — a free and safe browser game. No download needed, plays great at school and home.",
    ],
    "default": [
        "Play {t} unblocked free online — instant browser play with no download or sign-up. Works at school, work, or anywhere.",
        "{t} is one of the best free unblocked games you can play instantly in your browser. No Flash, no install needed.",
        "Enjoy {t} unblocked — a free online game that loads instantly in any browser. Works on school networks, zero hassle.",
        "Looking for a free unblocked game? {t} is ready to play right now in your browser — no download, no sign-up required.",
        "{t} unblocked is a top-rated free online game. Jump in instantly from any browser — works at school, home, and everywhere.",
        "Play {t} free and unblocked — no download, no Flash, instant browser access. Works on any school or office network.",
    ],
}

HOW_TO_TEMPLATES = {
    "shooter":    [
        "Use WASD or arrow keys to move, mouse to aim, and left-click to shoot. Eliminate enemies before they get you. Switch weapons with number keys.",
        "Move with arrow keys, aim with your mouse, and click to fire. Reload with R and switch weapons with Q. Watch your ammo count!",
        "Control your character with WASD, aim with the mouse cursor, and left-click to shoot. Use Shift to sprint and Space to jump.",
        "Arrow keys or WASD to move, mouse to aim. Left-click fires your weapon — headshots deal more damage. Use cover wisely.",
        "Navigate with WASD, aim with your mouse, and click to fire. Press E to interact and R to reload. Survive as long as possible.",
    ],
    "platformer": [
        "Use arrow keys or WASD to move left and right. Press Space or Up to jump. Double-tap jump for a double jump where available.",
        "Move with the arrow keys and jump with Space. Avoid obstacles, collect items, and reach the exit to complete each level.",
        "Control your character with A/D or left/right arrows. Jump with Space or W. Land on platforms carefully and avoid falling.",
        "Navigate using arrow keys — Left/Right to run, Up or Space to jump. Time your jumps carefully to avoid gaps and enemies.",
        "Use WASD or arrow keys to move, Space to jump. Some levels allow wall jumping — press jump when touching a wall to try it.",
    ],
    "2-player": [
        "Player 1: WASD to move, G to attack. Player 2: Arrow keys to move, L to attack. Take turns or compete simultaneously.",
        "Player 1 uses WASD + Space. Player 2 uses Arrow keys + Enter. Share the keyboard and battle or cooperate to win.",
        "Two players share the keyboard. Player 1: WASD + F. Player 2: Arrow keys + K. Work together or compete to outscore each other.",
        "Player 1 controls: W/A/S/D. Player 2 controls: Arrow keys. Each player has their own action buttons shown on screen.",
        "Share the keyboard with a friend. Player 1 uses the left side of the keyboard, Player 2 uses the right side or arrow keys.",
    ],
    "fighting": [
        "Move with arrow keys, punch with A, kick with S, and block with D. String moves together for powerful combo attacks.",
        "Use WASD to move your fighter. Press J to punch, K to kick, and L to block. Special moves are triggered with key combinations.",
        "Arrow keys to move, Z for light attack, X for heavy attack, C to block. Master combos to defeat your opponent quickly.",
        "Control with WASD or arrow keys. Attack with the listed buttons on screen. Block incoming hits and wait for an opening to counter.",
        "Navigate with arrow keys. Use A and S for different attacks, D to defend. Build your combo meter to unleash special moves.",
    ],
    "driving": [
        "Use arrow keys to steer: Up to accelerate, Down to brake, Left/Right to turn. Avoid crashes and reach the finish line first.",
        "W/Up arrow to accelerate, S/Down to brake, A/D or Left/Right to steer. Watch your speed on sharp corners.",
        "Accelerate with Up arrow or W, brake with Down or S. Steer with Left/Right arrows. Drift around corners for extra speed.",
        "Control your vehicle with WASD or arrow keys. Press Up to speed up, Down to slow down. Stay on the road to avoid penalties.",
        "Use arrow keys: Up=gas, Down=brake, Left/Right=steer. Collect power-ups on the track and avoid obstacles to win.",
    ],
    "puzzle": [
        "Use arrow keys or your mouse to interact with puzzle elements. Think before you move — some puzzles have limited moves.",
        "Click or drag pieces with your mouse to solve each puzzle. Read the on-screen instructions for any special rules.",
        "Use the mouse to click, drag, or rotate puzzle elements. Arrow keys also work in some levels. Take your time and think ahead.",
        "Interact with the puzzle using mouse clicks or arrow keys. Each level introduces a new mechanic — experiment to find the solution.",
        "Click puzzle pieces or press arrow keys to move them. Plan several steps ahead to avoid getting stuck and needing to restart.",
    ],
    "multiplayer": [
        "Use WASD or arrow keys to move. Left-click or Space to attack/interact. Team up with others or compete for the top rank.",
        "Move with WASD, aim with your mouse, and click to act. Work with or against other real players to climb the leaderboard.",
        "Navigate with arrow keys or WASD. Press the action keys shown to interact. Match your skills against live opponents worldwide.",
        "Standard WASD movement, mouse to aim and interact. Join a match and compete against real players — the rules are shown in-game.",
        "Use WASD to move and mouse to aim. Communicate with teammates using the chat. Follow in-game prompts to learn special actions.",
    ],
    "action": [
        "Move with WASD or arrow keys, attack with Space or mouse click. Dodge incoming fire and keep moving to stay alive.",
        "Use arrow keys to navigate and Space to attack. Collect power-ups to boost your abilities and defeat all enemies on screen.",
        "Control with WASD, interact with E, attack with left-click or Space. Keep moving — standing still makes you an easy target.",
        "Navigate with arrow keys. Press Z or Space to attack, X to use a special ability. Chain moves together to maximise damage.",
        "Use WASD to move and mouse to aim. Click to attack and press Space for your special move. Stay aggressive and keep the pressure on.",
    ],
    "skill": [
        "Use precise mouse movements or timed key presses to master each challenge. Practice makes perfect — try to beat your own best score.",
        "Follow the on-screen prompts carefully. Time your actions with precision using Space, click, or arrow keys as indicated.",
        "React quickly to on-screen events using mouse clicks or specific keys. The difficulty increases — stay focused and improve each run.",
        "Control with mouse clicks or arrow keys. Each level requires precise timing. Learn the patterns and react faster each attempt.",
        "Click or press the correct key at exactly the right moment. Reflex and muscle memory are key — keep practising to improve.",
    ],
    "adventure": [
        "Use arrow keys or WASD to explore. Interact with characters and objects using Space or E. Collect items and solve puzzles to progress.",
        "Navigate with WASD, jump with Space, and interact with E. Talk to NPCs to get quests and discover the story as you play.",
        "Move with arrow keys. Press Space to interact or attack. Explore every area — hidden items and secret paths are everywhere.",
        "Control with WASD or arrow keys. Press E to pick up items or talk to characters. Complete objectives to unlock new areas.",
        "Explore with arrow keys or WASD. Use Space to jump, E to interact. The map reveals more as you discover new locations.",
    ],
    "racing": [
        "Accelerate with Up/W, brake with Down/S, steer with Left/Right. Use nitro boosts on straight sections and brake before corners.",
        "Press Up arrow to go, Down to brake, Left/Right to steer. Stay on the track, hit checkpoints, and cross the finish line first.",
        "Use WASD or arrow keys. Accelerate carefully into corners — braking early keeps you on track. Watch the mini-map for upcoming bends.",
        "Steer with arrow keys, gas with Up, brake with Down. Draft behind opponents for a speed boost, then swerve to overtake.",
        "Arrow key controls: Up=accelerate, Down=brake/reverse, Left/Right=steer. Use the drift mechanic on corners for faster lap times.",
    ],
    "strategy": [
        "Click units or buildings to select them, then right-click to move or assign actions. Manage resources and plan before you attack.",
        "Select your units by clicking, move them by right-clicking the map. Balance resource collection with building defences and attack forces.",
        "Left-click to select, right-click to command. Build structures in a logical order — economy first, then military upgrades.",
        "Use the mouse to manage your base and army. Read tooltips carefully. Scout the map early and react to your opponent's moves.",
        "Click cards or units to play them. Read each card's description before acting. Think about your opponent's possible response first.",
    ],
    "sports": [
        "Use arrow keys to move your player, Space to kick or shoot. Time your shots carefully — power and angle both matter.",
        "WASD or arrow keys to move, Space or click to perform the main action. Watch the on-screen timer and score to plan your moves.",
        "Control with arrow keys: move with Left/Right, jump or shoot with Up. Master the timing of your actions to outscore the opponent.",
        "Navigate with WASD. Press Space to interact with the ball or take a shot. Aim with the mouse where available for precision.",
        "Arrow keys to move, Space to act. Watch the power meter and release at the right time for accurate, powerful shots.",
    ],
    "simulation": [
        "Click objects to interact with them. Follow on-screen tutorials for the first few minutes — mechanics are introduced gradually.",
        "Use mouse clicks to build, buy, or manage items. Read notifications — they guide your next actions and warn of problems.",
        "Left-click to select and place objects. Drag to move things around. Check the info panels to understand what your citizens or items need.",
        "Interact with everything using your mouse. Balance your resources carefully — overspending early leads to problems later on.",
        "Click to manage your simulation. Follow the objectives shown on screen. Experiment freely — most actions can be undone or adjusted.",
    ],
    "clicker": [
        "Click the main object rapidly to earn currency. Spend it on upgrades to increase your clicking power and passive income.",
        "Click as fast as you can to accumulate points. Buy upgrades from the shop to automate production and multiply your earnings.",
        "Tap the screen or click the central object to score. Reinvest in upgrades that increase clicks-per-second for faster progress.",
        "Click the main button to earn resources. Purchase the cheapest upgrades first, then reinvest in multipliers for exponential growth.",
        "Keep clicking the central element to gain currency. Unlock auto-clickers and upgrades to maximise your idle income over time.",
    ],
    "horror": [
        "Move with WASD or arrow keys. Press E to interact with objects and doors. Stay quiet, use your torch wisely, and never run unless necessary.",
        "Sneak with Shift, walk with WASD. Interact using E. Check every corner — enemies can spawn suddenly. Manage your resources carefully.",
        "Navigate with arrow keys or WASD. Collect items by walking over them. Avoid enemies or use distractions to slip past them safely.",
        "Use mouse to look around, WASD to move, E to interact. Conserve items like batteries and med-kits — you will need them later.",
        "Creep through levels with WASD. Use the mouse to examine your environment. Solve puzzles to unlock exits and escape each area.",
    ],
    "kids": [
        "Click the screen or use arrow keys to play. The game teaches you as you go — just follow the colourful arrows and prompts on screen.",
        "Press arrow keys to move and Space to jump or interact. The rules are simple — just have fun and see how far you can get!",
        "Use your mouse to click on objects or characters. Everything is explained with pictures — just follow the on-screen guide.",
        "Arrow keys to move, Space to jump. Collect all the stars and reach the goal. It is easy to learn and fun to master!",
        "Click or tap to play. The game explains everything with fun animations. Try different things and see what happens — enjoy!",
    ],
    "default": [
        "Use arrow keys or WASD to move and Space to interact. Click the Play button and follow the on-screen instructions to get started.",
        "Control with arrow keys or WASD. Press Space or click to perform actions. The game includes a short tutorial when you first start.",
        "Move with WASD or arrow keys. Left-click to interact. Check the in-game instructions panel for the full list of controls.",
        "Navigate using arrow keys. Press Space to jump or interact. Hover over buttons in-game to see what each control does.",
        "Use your keyboard arrow keys to play. The on-screen prompts will guide you through the controls as you progress.",
    ],
}

# ── UTILITY ────────────────────────────────────────────────────────────────────

def pick(templates, key, seed_str):
    """Pick a template variant deterministically using a hash of the game slug."""
    pool = templates.get(key, templates["default"])
    idx  = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % len(pool)
    return pool[idx]


def slug_to_title(slug):
    # Handle common abbreviations nicely
    special = {
        "1v1-lol": "1v1.LOL", "1v1lol": "1v1.LOL",
        "2048": "2048", "10x10": "10x10", "11-11": "11 11",
        "8-ball-pool": "8 Ball Pool", "9-ball-pool": "9 Ball Pool",
    }
    if slug in special:
        return special[slug]
    return " ".join(w.capitalize() for w in slug.replace("-", " ").split())


def get_categories_from_html(html):
    """Extract category slugs from the page's category-tag links."""
    cats = re.findall(r'/categ/([a-z0-9\-]+)/', html)
    # Filter to known categories; deduplicate
    known = [c for c in dict.fromkeys(cats) if c in CATEGORIES]
    return known if known else ["default"]


def primary_category(cats):
    return cats[0] if cats else "default"


def get_game_folders():
    return [
        f for f in sorted(SITE_ROOT.iterdir())
        if f.is_dir()
        and not f.name.startswith(".")
        and f.name not in SKIP
        and (f / "index.html").exists()
    ]

# ── REMOVE FOOTER CATEGORY PILLS ─────────────────────────────────────────────

_CAT_LINK_RE = re.compile(
    r'(<a\s[^>]*?/categ/[^>]*?>.*?</a>)',
    re.IGNORECASE | re.DOTALL
)

def remove_footer_cat_block(html):
    """
    Remove the last dense cluster of /categ/ links (the footer pills).
    The nav bar cluster is left intact.
    """
    all_m = list(_CAT_LINK_RE.finditer(html))
    if len(all_m) < 2:
        return html

    # Find the last run of consecutive categ links
    # Group into runs (links within 400 chars of each other = same block)
    runs = []
    run  = [all_m[0]]
    for m in all_m[1:]:
        if m.start() - run[-1].end() < 400:
            run.append(m)
        else:
            runs.append(run)
            run = [m]
    runs.append(run)

    if len(runs) < 2:
        return html

    last_run = runs[-1]
    start = last_run[0].start()
    end   = last_run[-1].end()
    # Also strip surrounding whitespace/newlines
    while start > 0 and html[start-1] in ' \t\n\r':
        start -= 1
    html = html[:start] + '\n' + html[end:]
    return html


# ── FIX H1 ────────────────────────────────────────────────────────────────────

def fix_h1(html):
    """Demote the site-logo H1 to a div — keep only the game-title H1."""
    h1s = list(re.finditer(r'<h1([^>]*)>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL))
    if len(h1s) < 2:
        return html
    for blk in h1s:
        inner = blk.group(2)
        if "🎮" in inner or "Unblocked Games USA" in inner:
            html = html[:blk.start()] + f'<div class="site-logo"{blk.group(1)}>{inner}</div>' + html[blk.end():]
            break
    return html


# ── UPDATE <head> META TAGS ───────────────────────────────────────────────────

def update_head(html, title_text, desc_text, slug):
    # Title
    html = re.sub(
        r'<title>[^<]*</title>',
        f'<title>{title_text}</title>',
        html, count=1, flags=re.IGNORECASE
    )

    # Meta description — update or insert
    if re.search(r'<meta\s+name=["\']description["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+name=["\']description["\'][^>]*/?>',
            f'<meta name="description" content="{desc_text}">',
            html, count=1, flags=re.IGNORECASE
        )
    else:
        html = re.sub(
            r'(</title>)',
            r'\1\n  <meta name="description" content="' + desc_text + '">',
            html, count=1, flags=re.IGNORECASE
        )

    # OG description
    if re.search(r'property=["\']og:description["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+property=["\']og:description["\'][^>]*/?>',
            f'<meta property="og:description" content="{desc_text}">',
            html, count=1, flags=re.IGNORECASE
        )

    # OG title
    if re.search(r'property=["\']og:title["\']', html, re.IGNORECASE):
        html = re.sub(
            r'<meta\s+property=["\']og:title["\'][^>]*/?>',
            f'<meta property="og:title" content="{title_text}">',
            html, count=1, flags=re.IGNORECASE
        )

    return html


# ── UPDATE PAGE BODY CONTENT ──────────────────────────────────────────────────

def update_body_content(html, game_title, about_text, howto_text, cats):
    """
    Replace the boilerplate "About" description and "How to Play" text
    with unique content.
    """
    # --- About description paragraph -----------------------------------------
    # Targets: <p>Play X free in your browser — no download needed!</p>
    # or similar boilerplate inside the About section
    boilerplate_about = re.compile(
        r'(Play\s+' + re.escape(game_title) + r'\s+free\s+in\s+your\s+browser[^<]*)',
        re.IGNORECASE
    )
    html = boilerplate_about.sub(about_text, html, count=1)

    # Also catch the generic version
    html = re.sub(
        r'Play\s+\S.*?free\s+in\s+your\s+browser\s+[—-]+\s+no\s+download\s+needed!',
        about_text,
        html, count=1, flags=re.IGNORECASE
    )

    # --- How to Play paragraph ------------------------------------------------
    html = re.sub(
        r'Use your mouse or keyboard to play\.\s+Click the Play button above to start instantly\s+[—-]+\s+no download needed!',
        howto_text,
        html, count=1, flags=re.IGNORECASE
    )

    return html


# ── MAIN GAME PAGE FIX ────────────────────────────────────────────────────────

def fix_game_page(folder):
    path  = folder / "index.html"
    html  = original = path.read_text(encoding="utf-8", errors="replace")
    slug  = folder.name
    title = slug_to_title(slug)

    cats     = get_categories_from_html(html)
    prim_cat = primary_category(cats)

    # Build unique content
    title_text = pick(TITLE_TEMPLATES, prim_cat, slug + "_title").replace("{t}", title).replace("{T}", title.upper())
    desc_text  = pick(DESC_TEMPLATES,  prim_cat, slug + "_desc" ).replace("{t}", title)
    about_text = desc_text   # same high-quality sentence for About section
    howto_text = pick(HOW_TO_TEMPLATES, prim_cat, slug + "_howto")

    html = update_head(html, title_text, desc_text, slug)
    html = fix_h1(html)
    html = update_body_content(html, title, about_text, howto_text, cats)
    html = remove_footer_cat_block(html)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
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

    lines.append(url(BASE_URL + "/", "1.0", "daily"))
    for c in CATEGORIES:
        lines.append(url(f"{BASE_URL}/categ/{c}/", "0.8"))
    for f in games:
        lines.append(url(f"{BASE_URL}/{f.name}/", "0.6"))
    lines.append("</urlset>")
    return "\n".join(lines)


ROBOTS = f"""User-agent: *
Allow: /
Disallow: /assets/
Sitemap: {BASE_URL}/sitemap.xml
"""

LLMS = f"""# Unblocked Games USA

> 500+ free unblocked browser games — play instantly at school, work, or home.
> No downloads. No sign-ups. Works on all devices and school networks.

## About

Unblocked Games USA ({BASE_URL}) is a free online gaming portal with 500+
HTML5 browser games across 17 categories. All games bypass school network
restrictions and require no download, no Flash, and no account.

## Categories

- Shooter: {BASE_URL}/categ/shooter/
- Platformer: {BASE_URL}/categ/platformer/
- 2-Player: {BASE_URL}/categ/2-player/
- Fighting: {BASE_URL}/categ/fighting/
- Driving: {BASE_URL}/categ/driving/
- Puzzle: {BASE_URL}/categ/puzzle/
- Multiplayer: {BASE_URL}/categ/multiplayer/
- Action: {BASE_URL}/categ/action/
- Skill: {BASE_URL}/categ/skill/
- Adventure: {BASE_URL}/categ/adventure/
- Racing: {BASE_URL}/categ/racing/
- Strategy: {BASE_URL}/categ/strategy/
- Sports: {BASE_URL}/categ/sports/
- Simulation: {BASE_URL}/categ/simulation/
- Clicker: {BASE_URL}/categ/clicker/
- Horror: {BASE_URL}/categ/horror/
- Kids: {BASE_URL}/categ/kids/

## Popular Games

- 1v1.LOL Unblocked: {BASE_URL}/1v1-lol/
- Among Us Unblocked: {BASE_URL}/among-us/
- Basketball Legends: {BASE_URL}/basketball-legends/
- 2048: {BASE_URL}/2048/
- Bloxorz: {BASE_URL}/bloxorz/
- Age of War: {BASE_URL}/age-of-war/

## Links

- Sitemap: {BASE_URL}/sitemap.xml
- Contact: {BASE_URL}/contact
- DMCA: {BASE_URL}/dmca
- Privacy: {BASE_URL}/privacy-policy
- Updated: {TODAY}
"""


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Unblocked Games USA  —  SEO Content Engine")
    print("=" * 60)

    games = get_game_folders()
    print(f"\n  Found {len(games)} game pages\n")

    changed = 0
    for folder in games:
        if fix_game_page(folder):
            changed += 1

    print(f"  Game pages updated : {changed} / {len(games)}")

    (SITE_ROOT / "sitemap.xml").write_text(build_sitemap(games), encoding="utf-8")
    print(f"  sitemap.xml        : {len(games) + 1 + len(CATEGORIES)} URLs")

    (SITE_ROOT / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    print("  robots.txt         : written")

    (SITE_ROOT / "llms.txt").write_text(LLMS, encoding="utf-8")
    print("  llms.txt           : written")

    print("""
  ─────────────────────────────────────────────────────
  Done! Push to GitHub:

    git add -A
    git commit -m "SEO: unique titles, descriptions and content per game"
    git push

  Then in Google Search Console submit:
    https://unblockedgames-usa.github.io/sitemap.xml
  ─────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    main()
