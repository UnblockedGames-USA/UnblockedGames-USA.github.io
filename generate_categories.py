#!/usr/bin/env python3
"""
generate_categories.py
======================
Generates all category index.html pages for unblockedgames-usa.github.io
Run from the ROOT of your cloned repository:
    python3 generate_categories.py

Each category folder (categ/<slug>/index.html) will be created/overwritten.
"""

import os, math

# ─────────────────────────────────────────────
# 1.  CATEGORY DEFINITIONS
# ─────────────────────────────────────────────
CATEGORIES = [
    {
        "slug": "action",
        "emoji": "💥",
        "name": "Action Games",
        "tagline": "Non-stop adrenaline — run, gun, and survive!",
        "accent": "#E8192C",
        "description": "Dive into heart-pounding action with our collection of unblocked action games. From intense shooters to fast-paced brawlers, every title is available instantly — no downloads, no restrictions.",
        "h3": "Unlimited Action Unblocked",
        "h3desc": "Whether you're at school or home, our action games are always unblocked and ready to play. Pick your fighter, load your weapon, and get into the action right now.",
    },
    {
        "slug": "adventure",
        "emoji": "🗺️",
        "name": "Adventure Games",
        "tagline": "Explore vast worlds and epic quests.",
        "accent": "#00a86b",
        "description": "Embark on epic journeys with our unblocked adventure games. Explore dungeons, solve mysteries, and uncover hidden treasures across hundreds of thrilling titles — all free to play.",
        "h3": "Adventure Awaits — Unblocked",
        "h3desc": "Our adventure games are fully unblocked so you can explore new worlds anytime, anywhere. No downloads required — just click and play!",
    },
    {
        "slug": "clicker",
        "emoji": "🖱️",
        "name": "Clicker Games",
        "tagline": "Click your way to ultimate power!",
        "accent": "#ff9900",
        "description": "Start with a single click and build empires in our addictive unblocked clicker games. Idle mechanics, upgrades, and prestige systems will keep you hooked for hours.",
        "h3": "Idle & Clicker Games Unblocked",
        "h3desc": "No install needed — jump straight into the best idle clicker games available unblocked. Perfect for a quick session or a long idle grind.",
    },
    {
        "slug": "driving",
        "emoji": "🚗",
        "name": "Driving Games",
        "tagline": "Hit the road and feel the speed!",
        "accent": "#1e90ff",
        "description": "Get behind the wheel in our huge collection of unblocked driving games. From realistic simulators to wacky physics racers, there's something for every speed demon.",
        "h3": "Unblocked Driving Games for Everyone",
        "h3desc": "All driving games here are unblocked — race, drift, and explore open roads with no restrictions. Jump in and start your engine!",
    },
    {
        "slug": "fighting",
        "emoji": "🥊",
        "name": "Fighting Games",
        "tagline": "Step into the arena and dominate!",
        "accent": "#E8192C",
        "description": "Master combos and crush your opponents in our unblocked fighting games. Whether you prefer one-on-one duels or chaotic brawls, our collection has something for every fighter.",
        "h3": "Free Unblocked Fighting Games",
        "h3desc": "All fighting games are unblocked and free — no downloads, no sign-ups. Challenge the AI or go head-to-head with a friend on the same keyboard.",
    },
    {
        "slug": "horror",
        "emoji": "👻",
        "name": "Horror Games",
        "tagline": "Face your fears — if you dare!",
        "accent": "#6a0dad",
        "description": "Enter dark worlds and terrifying scenarios with our unblocked horror games. Survive jump scares, solve spine-chilling puzzles, and escape the monsters before time runs out.",
        "h3": "Unblocked Horror Games — Play Free",
        "h3desc": "Our horror games work anywhere — no downloads or installs required. Turn off the lights and prepare for the scare of your life.",
    },
    {
        "slug": "kids",
        "emoji": "🧸",
        "name": "Kids Games",
        "tagline": "Safe, fun, and educational for young players!",
        "accent": "#ff69b4",
        "description": "Discover a world of fun with our safe, unblocked kids games. Designed for younger players, these colorful adventures and puzzles are entertaining and age-appropriate.",
        "h3": "Safe Unblocked Games for Kids",
        "h3desc": "Every kids game here is unblocked, safe, and completely free. Perfect for school breaks — just click and play with no downloads needed!",
    },
    {
        "slug": "multiplayer",
        "emoji": "🌐",
        "name": "Multiplayer Games",
        "tagline": "Connect and compete with players worldwide!",
        "accent": "#2655cc",
        "description": "Experience the thrill of playing with others in our extensive collection of multiplayer games. Whether you want to team up with friends or compete against players from around the globe, this is the place to be. All titles are unblocked — connect and play instantly, no downloads required.",
        "h3": "Unblocked Multiplayer for Everyone",
        "h3desc": "Every game here is unblocked, providing unrestricted access at school, work, or home. Gather your friends and jump in today to see who comes out on top.",
    },
    {
        "slug": "platformer",
        "emoji": "🏃",
        "name": "Platformer Games",
        "tagline": "Jump, run, and dash through epic levels!",
        "accent": "#00c8a0",
        "description": "Run and jump through hundreds of challenging levels in our unblocked platformer games. Classic side-scrollers, precision platformers, and endless runners — all free to play.",
        "h3": "Classic Platformers Unblocked",
        "h3desc": "Every platformer here loads instantly with no downloads. Test your timing and reflexes in the best unblocked platform games around.",
    },
    {
        "slug": "puzzle",
        "emoji": "🧠",
        "name": "Puzzle Games",
        "tagline": "Exercise your brain with mind-bending challenges!",
        "accent": "#9b59b6",
        "description": "Sharpen your mind with our collection of unblocked puzzle games. From logic challenges to word puzzles and physics brainteasers, our library has something to stump every player.",
        "h3": "Free Unblocked Puzzle Games",
        "h3desc": "All puzzle games are instantly accessible — no install, no account. Challenge yourself with the best free puzzle games available unblocked!",
    },
    {
        "slug": "racing",
        "emoji": "🏁",
        "name": "Racing Games",
        "tagline": "Go full throttle and cross the finish line first!",
        "accent": "#FFB300",
        "description": "Race to the top in our massive collection of unblocked racing games. Kart racers, street racing, and off-road challenges — all available free and unblocked in your browser.",
        "h3": "Unblocked Racing Games — Play Free",
        "h3desc": "No downloads, no restrictions — our racing games are always unblocked and ready to play. Choose your car, hit the track, and chase the podium!",
    },
    {
        "slug": "shooter",
        "emoji": "🎯",
        "name": "Shooter Games",
        "tagline": "Lock, load, and take down your enemies!",
        "accent": "#E8192C",
        "description": "Lock and load in our huge collection of unblocked shooter games. First-person shooters, top-down blasters, and archery challenges — all free and instantly playable in your browser.",
        "h3": "Unblocked Shooter Games",
        "h3desc": "All shooter games here are fully unblocked — no VPN, no proxy needed. Just open your browser and start shooting!",
    },
    {
        "slug": "simulation",
        "emoji": "🏙️",
        "name": "Simulation Games",
        "tagline": "Build, manage, and simulate real life!",
        "accent": "#17a2b8",
        "description": "Build cities, run businesses, and simulate life in our unblocked simulation games. From farming to space exploration, our collection covers every kind of sim you could want.",
        "h3": "Free Unblocked Simulation Games",
        "h3desc": "Our simulation games are 100% unblocked — no downloads, no waiting. Start building your virtual world right now!",
    },
    {
        "slug": "skill",
        "emoji": "🏆",
        "name": "Skill Games",
        "tagline": "Master your reflexes and precision!",
        "accent": "#f39c12",
        "description": "Put your skills to the test in our collection of unblocked skill games. Precision platformers, reflex challenges, and timing-based puzzles will push your abilities to the limit.",
        "h3": "Unblocked Skill Games — Test Yourself",
        "h3desc": "All skill games here are free and unblocked. No installations — just pure challenge. Compete for high scores and prove you're the best!",
    },
    {
        "slug": "sports",
        "emoji": "⚽",
        "name": "Sports Games",
        "tagline": "Score goals, hit homers, and win championships!",
        "accent": "#27ae60",
        "description": "Step onto the virtual field with our unblocked sports games. Football, basketball, soccer, golf, and more — compete solo or with friends for the ultimate sports experience.",
        "h3": "Unblocked Sports Games for Everyone",
        "h3desc": "All sports games are unblocked and free. Whether you love soccer, basketball, or tennis, we've got the game for you — no downloads needed!",
    },
    {
        "slug": "strategy",
        "emoji": "♟️",
        "name": "Strategy Games",
        "tagline": "Outsmart your opponents with cunning tactics!",
        "accent": "#2980b9",
        "description": "Think before you act in our collection of unblocked strategy games. Build armies, manage resources, and outwit opponents in tower defense, turn-based, and real-time strategy titles.",
        "h3": "Free Unblocked Strategy Games",
        "h3desc": "Our strategy games are fully unblocked — play anywhere, any time. Plan your moves carefully and lead your faction to victory!",
    },
    {
        "slug": "2-player",
        "emoji": "👥",
        "name": "2 Player Games",
        "tagline": "Challenge a friend on the same screen!",
        "accent": "#e74c3c",
        "description": "Challenge your friends in our collection of unblocked 2 player games. Share a keyboard and go head-to-head in everything from sports to fighting games — no online connection needed.",
        "h3": "Unblocked 2 Player Games",
        "h3desc": "All 2 player games here work on a single keyboard — no extra hardware required. Perfect for school or home, always unblocked and free!",
    },
]

# ─────────────────────────────────────────────
# 2.  GAME DATABASE  (slug → categories list)
#     Add / remove games here freely.
#     slug must match the folder name in your repo.
# ─────────────────────────────────────────────
GAMES = [
    # ── Multiplayer ──────────────────────────
    {"slug": "house-of-hazards",        "title": "House of Hazards",         "cats": ["multiplayer", "2-player", "action"]},
    {"slug": "12-mini-battles-2",       "title": "12 Mini Battles 2",        "cats": ["multiplayer", "2-player"]},
    {"slug": "starblast",               "title": "Starblast",                 "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "gun-mayhem-2",            "title": "Gun Mayhem 2",              "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "g-switch-4",              "title": "G-Switch 4",                "cats": ["multiplayer", "2-player", "skill"]},
    {"slug": "minibattles",             "title": "Minibattles",               "cats": ["multiplayer", "2-player"]},
    {"slug": "alien-invaders-io",       "title": "Alien Invaders.io",         "cats": ["multiplayer", "shooter"]},
    {"slug": "bomber-royale",           "title": "Bomber Royale",             "cats": ["multiplayer", "action"]},
    {"slug": "hills-of-steel",          "title": "Hills Of Steel",            "cats": ["multiplayer", "action", "driving"]},
    {"slug": "snakes-and-ladders",      "title": "Snakes And Ladders",        "cats": ["multiplayer", "strategy", "kids"]},
    {"slug": "fury-wars",               "title": "Fury Wars",                 "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "kart-wars",               "title": "Kart Wars",                 "cats": ["multiplayer", "racing", "action"]},
    {"slug": "leader-strike",           "title": "Leader Strike",             "cats": ["multiplayer", "shooter"]},
    {"slug": "clash-of-tanks",          "title": "Clash of Tanks",            "cats": ["multiplayer", "action", "strategy"]},
    {"slug": "madalin-stunt-cars-3",    "title": "Madalin Stunt Cars 3",      "cats": ["multiplayer", "driving", "racing"]},
    {"slug": "shootz",                  "title": "Shootz",                    "cats": ["multiplayer", "shooter"]},
    {"slug": "1v1lol",                  "title": "1v1LOL",                    "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "bullet-force",            "title": "Bullet Force",              "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "among-us",                "title": "Among Us",                  "cats": ["multiplayer", "strategy", "action"]},
    {"slug": "rocket-soccer-derby",     "title": "Rocket Soccer Derby",       "cats": ["multiplayer", "sports", "racing"]},
    {"slug": "speed-stars",             "title": "Speed Stars",               "cats": ["multiplayer", "racing", "sports"]},
    {"slug": "12-minibattles",          "title": "12 Minibattles",            "cats": ["multiplayer", "2-player"]},
    {"slug": "slope-2-multiplayer",     "title": "Slope 2 Multiplayer",       "cats": ["multiplayer", "skill", "racing"]},
    {"slug": "sharkio",                 "title": "Sharkio",                   "cats": ["multiplayer", "action"]},
    {"slug": "vectaria-io",             "title": "Vectaria.io",               "cats": ["multiplayer", "action", "adventure"]},
    {"slug": "kart-bros",               "title": "Kart Bros",                 "cats": ["multiplayer", "racing", "2-player"]},
    {"slug": "fortz",                   "title": "Fortz",                     "cats": ["multiplayer", "strategy"]},
    {"slug": "blocky-cars",             "title": "Blocky Cars",               "cats": ["multiplayer", "racing", "driving"]},
    {"slug": "animal-arena",            "title": "Animal Arena",              "cats": ["multiplayer", "action"]},
    {"slug": "g-switch-3",             "title": "G-Switch 3",                "cats": ["multiplayer", "2-player", "skill"]},
    {"slug": "temple-of-boom",          "title": "Temple Of Boom",            "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "narrow-one",              "title": "Narrow One",                "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "tank-trouble-2",          "title": "Tank Trouble 2",            "cats": ["multiplayer", "2-player", "action"]},
    {"slug": "battle-wheels",           "title": "Battle Wheels",             "cats": ["multiplayer", "racing", "action"]},
    {"slug": "cubito-mayhem",           "title": "Cubito Mayhem",             "cats": ["multiplayer", "action"]},
    {"slug": "basket-bros",             "title": "Basket Bros",               "cats": ["multiplayer", "sports", "2-player"]},
    {"slug": "go-kart-go-ultra",        "title": "Go Kart Go Ultra",          "cats": ["multiplayer", "racing"]},
    {"slug": "tetris-99",               "title": "Tetris 99",                 "cats": ["multiplayer", "puzzle", "skill"]},
    {"slug": "pixel-gun-survival",      "title": "Pixel Gun Survival",        "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "1v1-battle",              "title": "1v1 Battle",                "cats": ["multiplayer", "2-player", "action"]},
    {"slug": "masked-forces",           "title": "Masked Forces",             "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "ludo-hero",               "title": "Ludo Hero",                 "cats": ["multiplayer", "strategy", "kids"]},
    {"slug": "sumo-party",              "title": "Sumo Party",                "cats": ["multiplayer", "sports", "2-player"]},
    {"slug": "nightpoint-io",           "title": "Nightpoint io",             "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "air-toons",               "title": "Air Toons",                 "cats": ["multiplayer", "action"]},
    {"slug": "basketball-stars",        "title": "Basketball Stars",          "cats": ["multiplayer", "sports", "2-player"]},
    {"slug": "pixwars-2",               "title": "Pixwars 2",                 "cats": ["multiplayer", "strategy", "action"]},
    {"slug": "hide-and-smash",          "title": "Hide and Smash",            "cats": ["multiplayer", "action", "2-player"]},
    {"slug": "8bit-fiesta",             "title": "8Bit Fiesta",               "cats": ["multiplayer", "action", "skill"]},
    {"slug": "1v1-lol",                 "title": "1v1 Lol",                   "cats": ["multiplayer", "shooter", "action"]},
    {"slug": "parkour-race",            "title": "Parkour Race",              "cats": ["multiplayer", "racing", "platformer"]},

    # ── Action ───────────────────────────────
    {"slug": "bacon-may-die",           "title": "Bacon May Die",             "cats": ["action", "platformer"]},
    {"slug": "age-of-war",              "title": "Age of War",                "cats": ["action", "strategy"]},
    {"slug": "age-of-war-2",            "title": "Age of War 2",              "cats": ["action", "strategy"]},
    {"slug": "bloons-tower-defense-1",  "title": "Bloons Tower Defense",      "cats": ["action", "strategy"]},
    {"slug": "bob-the-robber-4",        "title": "Bob The Robber 4",          "cats": ["action", "adventure", "platformer"]},
    {"slug": "boxrob",                  "title": "BoxRob",                    "cats": ["action", "platformer"]},
    {"slug": "boxrob-2",                "title": "BoxRob 2",                  "cats": ["action", "platformer"]},
    {"slug": "boxrob-3",                "title": "BoxRob 3",                  "cats": ["action", "platformer"]},
    {"slug": "bad-ice-cream-2",         "title": "Bad Ice Cream 2",           "cats": ["action", "multiplayer", "kids"]},
    {"slug": "bad-ice-cream-3",         "title": "Bad Ice Cream 3",           "cats": ["action", "multiplayer", "kids"]},
    {"slug": "bearsus",                 "title": "Bearsus",                   "cats": ["action", "fighting"]},
    {"slug": "awesome-tanks-2",         "title": "Awesome Tanks 2",           "cats": ["action", "shooter"]},
    {"slug": "big-shot-boxing",         "title": "Big Shot Boxing",           "cats": ["action", "fighting", "sports"]},
    {"slug": "blumgi-slime",            "title": "Blumgi Slime",              "cats": ["action", "platformer", "skill"]},
    {"slug": "blumgi-rocket",           "title": "Blumgi Rocket",             "cats": ["action", "skill"]},
    {"slug": "blumgi-castle",           "title": "Blumgi Castle",             "cats": ["action", "strategy"]},
    {"slug": "blumgi-dragon",           "title": "Blumgi Dragon",             "cats": ["action", "adventure"]},
    {"slug": "blumgi-ball",             "title": "Blumgi Ball",               "cats": ["action", "sports", "skill"]},
    {"slug": "blumgi-bloom",            "title": "Blumgi Bloom",              "cats": ["action", "puzzle"]},
    {"slug": "breaking-the-bank",       "title": "Breaking The Bank",         "cats": ["action", "adventure"]},
    {"slug": "a-pretty-odd-bunny",      "title": "A Pretty Odd Bunny",        "cats": ["action", "platformer"]},
    {"slug": "a-dance-of-fire-and-ice", "title": "A Dance of Fire and Ice",   "cats": ["action", "skill", "rhythm"]},
    {"slug": "10-minutes-till-dawn",    "title": "10 Minutes Till Dawn",      "cats": ["action", "shooter", "horror"]},
    {"slug": "aliens-nest",             "title": "Aliens Nest",               "cats": ["action", "shooter"]},
    {"slug": "all-star-blast",          "title": "All Star Blast",            "cats": ["action", "shooter"]},

    # ── Shooter ──────────────────────────────
    {"slug": "archer-master-3d-castle-defense", "title": "Archer Master 3D",  "cats": ["shooter", "action", "strategy"]},
    {"slug": "archery-world-tour",      "title": "Archery World Tour",        "cats": ["shooter", "sports", "skill"]},
    {"slug": "bubble-shooter",          "title": "Bubble Shooter",            "cats": ["shooter", "puzzle", "skill"]},

    # ── Platformer ───────────────────────────
    {"slug": "a-pretty-odd-bunny-roast-it", "title": "A Pretty Odd Bunny: Roast It", "cats": ["platformer", "action"]},
    {"slug": "ape-sling",               "title": "Ape Sling",                 "cats": ["platformer", "skill"]},
    {"slug": "avalanche",               "title": "Avalanche",                 "cats": ["platformer", "action", "skill"]},

    # ── Racing / Driving ─────────────────────
    {"slug": "3d-car-simulator",        "title": "3D Car Simulator",          "cats": ["driving", "simulation", "racing"]},
    {"slug": "3d-moto-simulator-2",     "title": "3D Moto Simulator 2",       "cats": ["driving", "simulation", "racing"]},
    {"slug": "3d-monster-truck-skyroads","title": "3D Monster Truck Skyroads", "cats": ["driving", "racing"]},
    {"slug": "4x4-drive-offroad",       "title": "4x4 Drive Offroad",         "cats": ["driving", "racing", "simulation"]},
    {"slug": "18-wheeler-cargo-simulator","title": "18 Wheeler Cargo Simulator","cats": ["driving", "simulation"]},
    {"slug": "adventure-drivers",       "title": "Adventure Drivers",         "cats": ["driving", "racing", "adventure"]},
    {"slug": "aqua-thrills",            "title": "Aqua Thrills",              "cats": ["racing", "skill"]},

    # ── Puzzle ───────────────────────────────
    {"slug": "10x10",                   "title": "10x10",                     "cats": ["puzzle", "skill"]},
    {"slug": "11-11",                   "title": "11-11",                     "cats": ["puzzle", "skill"]},
    {"slug": "2048",                    "title": "2048",                      "cats": ["puzzle", "strategy", "skill"]},
    {"slug": "2048-online",             "title": "2048 Online",               "cats": ["puzzle", "strategy", "skill"]},
    {"slug": "2048-multitask",          "title": "2048 Multitask",            "cats": ["puzzle", "skill"]},
    {"slug": "2048-suika",              "title": "2048 Suika",                "cats": ["puzzle", "skill"]},
    {"slug": "2048-watermelon",         "title": "2048 Watermelon",           "cats": ["puzzle", "skill"]},
    {"slug": "arithmetica",             "title": "Arithmetica",               "cats": ["puzzle", "skill", "kids"]},
    {"slug": "block-puzzle",            "title": "Block Puzzle",              "cats": ["puzzle", "skill"]},
    {"slug": "block-the-pig",           "title": "Block The Pig",             "cats": ["puzzle", "strategy"]},
    {"slug": "bloxorz",                 "title": "Bloxorz",                   "cats": ["puzzle", "skill"]},
    {"slug": "brain-test-tricky-puzzles","title": "Brain Test: Tricky Puzzles","cats": ["puzzle", "kids"]},
    {"slug": "brain-test-2-tricky-stories","title": "Brain Test 2",          "cats": ["puzzle", "kids"]},
    {"slug": "brain-test-3-tricky-quests","title": "Brain Test 3",           "cats": ["puzzle", "kids"]},

    # ── Strategy ─────────────────────────────
    {"slug": "bitlife",                 "title": "BitLife",                   "cats": ["strategy", "simulation", "adventure"]},

    # ── Skill ────────────────────────────────
    {"slug": "a-small-world-cup",       "title": "A Small World Cup",         "cats": ["skill", "sports"]},
    {"slug": "air-hockey-championship-deluxe","title": "Air Hockey Deluxe",   "cats": ["skill", "sports", "2-player"]},
    {"slug": "amazing-bubble-breaker",  "title": "Amazing Bubble Breaker",    "cats": ["skill", "puzzle"]},
    {"slug": "amazing-bubble-connect",  "title": "Amazing Bubble Connect",    "cats": ["skill", "puzzle"]},
    {"slug": "athletics-hero",          "title": "Athletics Hero",            "cats": ["skill", "sports"]},

    # ── Sports ───────────────────────────────
    {"slug": "4th-and-goal-2022",       "title": "4th and Goal 2022",         "cats": ["sports", "action"]},
    {"slug": "8-ball-pool",             "title": "8 Ball Pool",               "cats": ["sports", "skill", "2-player"]},
    {"slug": "9-ball-pool",             "title": "9 Ball Pool",               "cats": ["sports", "skill"]},
    {"slug": "2-minute-football",       "title": "2 Minute Football",         "cats": ["sports", "action"]},
    {"slug": "basket-and-ball",         "title": "Basket And Ball",           "cats": ["sports", "skill", "platformer"]},
    {"slug": "basket-champs",           "title": "Basket Champs",             "cats": ["sports", "skill"]},
    {"slug": "basket-random",           "title": "Basket Random",             "cats": ["sports", "skill", "2-player"]},
    {"slug": "basket-swooshes",         "title": "Basket Swooshes",           "cats": ["sports", "skill"]},
    {"slug": "basketball-frvr",         "title": "Basketball FRVR",           "cats": ["sports", "skill"]},
    {"slug": "basketball-legends",      "title": "Basketball Legends",        "cats": ["sports", "action", "2-player"]},
    {"slug": "basketbros",              "title": "BasketBros",                "cats": ["sports", "action", "2-player"]},
    {"slug": "battle-golf",             "title": "Battle Golf",               "cats": ["sports", "skill", "2-player"]},
    {"slug": "bowling-stars",           "title": "Bowling Stars",             "cats": ["sports", "skill"]},
    {"slug": "bouncy-basketball",       "title": "Bouncy Basketball",         "cats": ["sports", "skill"]},

    # ── Fighting ─────────────────────────────
    {"slug": "boxing-physics-2",        "title": "Boxing Physics 2",          "cats": ["fighting", "sports", "2-player"]},
    {"slug": "boxing-random",           "title": "Boxing Random",             "cats": ["fighting", "sports", "2-player"]},

    # ── Horror ───────────────────────────────

    # ── Simulation ───────────────────────────
    {"slug": "become-a-puppy-groomer",  "title": "Become a Puppy Groomer",   "cats": ["simulation", "kids"]},
    {"slug": "bitlife",                 "title": "BitLife",                   "cats": ["simulation", "strategy", "adventure"]},

    # ── 2-player ─────────────────────────────
    {"slug": "2-player-tag",            "title": "2 Player Tag",              "cats": ["2-player", "action"]},

    # ── Kids ─────────────────────────────────
    {"slug": "blobby-clicker",          "title": "Blobby Clicker",            "cats": ["clicker", "kids"]},
    {"slug": "blob-drop",               "title": "Blob Drop",                 "cats": ["puzzle", "kids", "skill"]},

    # ── Clicker ──────────────────────────────
    {"slug": "bike-trials-offroad-1",   "title": "Bike Trials Offroad",       "cats": ["skill", "driving"]},
    {"slug": "bike-trials-winter-1",    "title": "Bike Trials Winter",        "cats": ["skill", "driving"]},
    {"slug": "bike-trials-winter-2",    "title": "Bike Trials Winter 2",      "cats": ["skill", "driving"]},
    {"slug": "blocky-trials",           "title": "Blocky Trials",             "cats": ["skill", "driving", "platformer"]},
]

# Remove duplicate slugs (keep first occurrence)
seen = set()
UNIQUE_GAMES = []
for g in GAMES:
    if g["slug"] not in seen:
        seen.add(g["slug"])
        UNIQUE_GAMES.append(g)
GAMES = UNIQUE_GAMES

GAMES_PER_PAGE = 50   # cards per page

# ─────────────────────────────────────────────
# 3.  NAV & CATEGORY LINK HELPERS
# ─────────────────────────────────────────────
NAV_ITEMS = [
    ("shooter",    "🎯 Shooter"),
    ("platformer", "🏃 Platformer"),
    ("2-player",   "👥 2-Player"),
    ("fighting",   "🥊 Fighting"),
    ("driving",    "🚗 Driving"),
    ("puzzle",     "🧠 Puzzle"),
    ("multiplayer","🌐 Multiplayer"),
    ("action",     "💥 Action"),
    ("skill",      "🏆 Skill"),
    ("adventure",  "🗺️ Adventure"),
    ("racing",     "🏁 Racing"),
    ("strategy",   "♟️ Strategy"),
    ("sports",     "⚽ Sports"),
    ("simulation", "🏙️ Simulation"),
    ("clicker",    "🖱️ Clicker"),
    ("horror",     "👻 Horror"),
    ("kids",       "🧸 Kids"),
]

CAT_GRID_ITEMS = NAV_ITEMS  # same list for the bottom pill grid


def build_nav(active_slug):
    items = ""
    for slug, label in NAV_ITEMS:
        cls = ' class="active"' if slug == active_slug else ""
        items += f'<li><a href="/categ/{slug}"{cls}>{label}</a></li>\n'
    return items


def build_cat_grid(active_slug):
    items = ""
    for slug, label in CAT_GRID_ITEMS:
        cls = "category-item active" if slug == active_slug else "category-item"
        items += f'<a href="/categ/{slug}" class="{cls}">{label}</a>\n'
    return items


# ─────────────────────────────────────────────
# 4.  CARD & PAGINATION HTML
# ─────────────────────────────────────────────
def game_card(game, cat_slug):
    slug  = game["slug"]
    title = game["title"]
    img   = f"https://unblockedgames-usa.github.io/images/{slug}.png"
    fallback = f"https://unblockedgames-usa.github.io/images/{cat_slug}.png"
    return f"""
        <div class="game-card">
          <a href="/{slug}" class="game-link">
            <div class="game-image">
              <img src="{img}" alt="{title}"
                   onerror="this.src='{fallback}'">
            </div>
            <div class="game-info">
              <h3 class="game-title">{title}</h3>
            </div>
          </a>
        </div>"""


def build_pagination(cat_slug, current_page, total_pages):
    if total_pages <= 1:
        return ""

    def page_url(p):
        if p == 1:
            return f"/categ/{cat_slug}"
        return f"/categ/{cat_slug}-page-{p}"

    parts = []
    # Previous
    if current_page == 1:
        parts.append('<span class="disabled">&laquo; Previous</span>')
    else:
        parts.append(f'<a href="{page_url(current_page-1)}">&laquo; Previous</a>')

    # Page numbers
    for p in range(1, total_pages + 1):
        if p == current_page:
            parts.append(f'<span class="current">{p}</span>')
        else:
            parts.append(f'<a href="{page_url(p)}">{p}</a>')

    # Next
    if current_page == total_pages:
        parts.append('<span class="disabled">Next &raquo;</span>')
    else:
        parts.append(f'<a href="{page_url(current_page+1)}">Next &raquo;</a>')

    return '<div class="pagination">\n' + "\n".join(parts) + "\n</div>"


# ─────────────────────────────────────────────
# 5.  FULL PAGE TEMPLATE
# ─────────────────────────────────────────────
def render_page(cat, games_html, pagination_html, nav_html, cat_grid_html):
    slug   = cat["slug"]
    name   = cat["name"]
    emoji  = cat["emoji"]
    accent = cat["accent"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-L6FNHSMWF4"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-L6FNHSMWF4');
</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} Unblocked - Play Free Online Games</title>
    <meta name="description" content="Play the best {name.lower()} unblocked for free. No download needed — instant browser play at school or home.">
    <meta name="keywords" content="{name.lower()}, unblocked games, free online games, play at school, {slug} games">
    <link rel="canonical" href="https://unblockedgames-usa.github.io/categ/{slug}" />
    <meta name="robots" content="index, follow">
    <meta name="author" content="Unblocked Games USA">
    <meta property="og:title" content="{name} Unblocked - Play Free Online Games" />
    <meta property="og:description" content="Play the best {name.lower()} unblocked for free." />
    <meta property="og:url" content="https://unblockedgames-usa.github.io/categ/{slug}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Unblocked Games USA" />
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{name} Unblocked - Play Free Online Games">
    <meta name="twitter:description" content="Play the best {name.lower()} unblocked for free.">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "{name} Unblocked - Play Free Online Games",
        "description": "Play the best {name.lower()} unblocked for free.",
        "url": "https://unblockedgames-usa.github.io/categ/{slug}"
    }}
    </script>

    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {{
            --red:        #E8192C;
            --blue:       #002868;
            --blue-mid:   #1a3a8a;
            --blue-light: #2655cc;
            --white:      #FFFFFF;
            --card-bg:    #07102b;
            --border:     rgba(255,255,255,0.08);
            --text:       #dce8ff;
            --grad:       linear-gradient(135deg, var(--blue) 0%, var(--blue-light) 50%, var(--red) 100%);
            --cat-accent: {accent};
        }}
        *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: 'Barlow', sans-serif;
            background: #000510;
            color: var(--text);
            min-height: 100vh;
            line-height: 1.6;
        }}
        body::before {{
            content: '';
            position: fixed; inset: 0;
            background-image:
                radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.4) 0%, transparent 100%),
                radial-gradient(1px 1px at 70% 15%, rgba(255,255,255,0.3) 0%, transparent 100%),
                radial-gradient(1px 1px at 45% 70%, rgba(255,255,255,0.25) 0%, transparent 100%),
                radial-gradient(1px 1px at 85% 55%, rgba(255,255,255,0.35) 0%, transparent 100%),
                radial-gradient(1px 1px at 10% 80%, rgba(255,255,255,0.2) 0%, transparent 100%);
            pointer-events: none; z-index: 0;
        }}
        .container {{ width:100%; max-width:1200px; margin:0 auto; padding:0 16px; position:relative; }}

        /* HEADER */
        header {{
            background: linear-gradient(90deg, var(--blue) 0%, #0d1f5c 40%, #1a0a2e 60%, var(--red) 100%);
            border-bottom: 3px solid;
            border-image: var(--grad) 1;
            position: sticky; top: 0; z-index: 100;
            transition: transform 0.3s ease;
            box-shadow: 0 4px 30px rgba(0,0,0,0.6);
        }}
        .header-hidden {{ transform: translateY(-100%); }}
        .header-content {{
            display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; gap: 10px; padding: 10px 0;
        }}
        .logo {{
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.9rem; letter-spacing: 2px; color: var(--white);
            text-decoration: none; display: flex; align-items: center; gap: 8px;
            text-shadow: 0 0 20px rgba(232,25,44,0.6); transition: text-shadow 0.3s;
        }}
        .logo:hover {{ text-shadow: 0 0 30px rgba(232,25,44,1), 0 0 60px rgba(0,40,104,0.8); }}

        /* SEARCH */
        .search-bar {{ display:flex; position:relative; }}
        .search-bar input {{
            padding: 0.45rem 1rem; border: 1px solid var(--border);
            border-radius: 50px 0 0 50px; outline: none;
            background: rgba(255,255,255,0.12); color: white;
            font-family: 'Barlow', sans-serif; font-size: 0.9rem;
            width: 200px; transition: background 0.2s, width 0.3s;
        }}
        .search-bar input:focus {{ background: rgba(255,255,255,0.18); width: 240px; }}
        .search-bar input::placeholder {{ color: rgba(255,255,255,0.5); }}
        .search-bar button {{
            background: var(--red); color: white; border: none;
            padding: 0.45rem 1rem; border-radius: 0 50px 50px 0;
            cursor: pointer; transition: background 0.2s;
        }}
        .search-bar button:hover {{ background: #c0101f; }}
        .search-dropdown {{
            position: absolute; top: calc(100% + 6px); left: 0; right: 0;
            background: #0a1535; border: 1px solid rgba(232,25,44,0.3);
            border-radius: 12px; overflow: hidden; z-index: 200;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
            display: none; max-height: 280px; overflow-y: auto;
        }}
        .search-dropdown.active {{ display: block; }}
        .search-dropdown a {{
            display: flex; align-items: center; gap: 10px;
            padding: 9px 14px; color: var(--text); text-decoration: none;
            font-size: 0.88rem; font-weight: 600;
            border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.15s;
        }}
        .search-dropdown a:last-child {{ border-bottom: none; }}
        .search-dropdown a:hover {{ background: rgba(232,25,44,0.2); color: white; }}
        .search-dropdown .no-results {{ padding: 12px 14px; color: rgba(255,255,255,0.45); font-size: 0.85rem; text-align: center; }}

        /* NAV */
        .main-nav {{ order: 1; width: 100%; }}
        .nav-toggle {{ display: none; background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; padding: 0.5rem; }}
        .main-nav ul {{
            list-style: none; display: flex; flex-wrap: wrap; justify-content: center; gap: 4px;
            padding: 10px 24px; margin: 6px 0 8px;
            background: linear-gradient(135deg, #001a5e 0%, #0d1f6e 40%, #1a0a2e 70%, #4a0a14 100%);
            border-radius: 50px;
            border: 2px solid rgba(255,255,255,0.75);
            box-shadow: 0 0 0 4px rgba(0,40,104,0.5), 0 6px 28px rgba(0,0,0,0.8),
                        0 0 35px rgba(232,25,44,0.25), 0 0 70px rgba(0,40,104,0.3),
                        inset 0 1px 0 rgba(255,255,255,0.1);
        }}
        .main-nav a {{
            color: rgba(255,255,255,0.88); text-decoration: none;
            padding: 4px 12px; border-radius: 50px;
            font-size: 0.82rem; font-weight: 600;
            transition: background 0.2s, color 0.2s;
            border: 1px solid transparent; white-space: nowrap;
        }}
        .main-nav a:hover, .main-nav a.active {{
            background: rgba(232,25,44,0.35); color: white;
            border-color: rgba(232,25,44,0.4);
        }}

        /* CATEGORY HEADER */
        .category-header {{
            border-radius: 14px; margin: 1.5rem 0; text-align: center;
            position: relative; overflow: hidden; padding: 2.5rem 2rem 2.2rem;
            background: linear-gradient(135deg,#000c2e 0%,#001a5e 25%,#0d1545 45%,#1a0a2e 65%,#3a0515 85%,#1a000a 100%);
            border: 2px solid transparent; background-clip: padding-box;
        }}
        .category-header::before {{
            content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 5px;
            background: linear-gradient(180deg,var(--blue-light) 0%,var(--cat-accent) 50%,var(--red) 100%);
            border-radius: 14px 0 0 14px;
        }}
        .category-header::after {{
            content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg,var(--blue) 0%,var(--blue-light) 30%,var(--cat-accent) 60%,var(--red) 100%);
        }}
        .category-header-glow {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
            width: 600px; height: 200px;
            background: radial-gradient(ellipse,rgba(38,85,204,0.18) 0%,transparent 70%);
            pointer-events: none;
        }}
        .category-header h1 {{
            font-family: 'Bebas Neue', sans-serif; font-size: 2.6rem; letter-spacing: 3px;
            background: linear-gradient(135deg,#ffffff 0%,#c8d8ff 50%,var(--red) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            margin-bottom: 0.5rem; position: relative; z-index: 1;
        }}
        .category-header p {{
            color: rgba(255,255,255,0.6); font-size: 1rem; max-width: 600px; margin: 0 auto;
            position: relative; z-index: 1; font-weight: 600; letter-spacing: 0.5px;
        }}

        /* SECTION TITLE */
        .section-title {{
            font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; font-size: 1.8rem;
            text-align: center; margin: 2rem 0 1.2rem;
            background: var(--grad); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text;
        }}

        /* GAMES GRID */
        .games-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1.2rem; margin-bottom: 2rem;
        }}
        .game-card {{
            background: var(--card-bg); border-radius: 10px; overflow: hidden;
            border: 1px solid var(--border); transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
        }}
        .game-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.5), 0 0 0 1px rgba(232,25,44,0.3);
            border-color: rgba(232,25,44,0.4);
        }}
        .game-link {{ text-decoration: none; color: inherit; display: block; }}
        .game-image {{
            height: 160px;
            background: linear-gradient(135deg, var(--blue), var(--red));
            display: flex; align-items: center; justify-content: center; overflow: hidden;
        }}
        .game-image img {{ width: 100%; height: 100%; object-fit: cover; }}
        .game-info {{ padding: 10px 12px; text-align: center; }}
        .game-title {{ font-family: 'Barlow', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--white); }}

        /* PAGINATION */
        .pagination {{
            display: flex; justify-content: center; align-items: center;
            margin: 1rem 0 2rem; gap: 0.5rem; flex-wrap: wrap;
        }}
        .pagination a, .pagination span {{
            color: var(--text); padding: 0.45rem 1rem; text-decoration: none;
            border: 1px solid rgba(255,255,255,0.15); border-radius: 50px;
            font-weight: 600; font-size: 0.85rem; transition: background 0.2s, border-color 0.2s;
        }}
        .pagination a:hover {{ background: rgba(232,25,44,0.3); border-color: rgba(232,25,44,0.4); color: white; }}
        .pagination .current {{ background: linear-gradient(135deg,var(--blue-mid),var(--red)); color: white; border-color: transparent; }}
        .pagination .disabled {{ color: rgba(255,255,255,0.25); cursor: default; }}

        /* DESCRIPTION BOX */
        .category-description {{
            background: var(--card-bg); border: 1px solid var(--border);
            border-radius: 12px; padding: 2rem; margin: 0 0 2rem;
        }}
        .category-description h2 {{
            font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; font-size: 1.5rem;
            background: var(--grad); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text;
            text-align: center; margin-bottom: 1rem;
        }}
        .category-description h3 {{
            font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; font-size: 1.2rem;
            color: var(--red); margin-top: 1.2rem; margin-bottom: 0.6rem; text-align: center;
        }}
        .category-description p {{
            color: rgba(220,232,255,0.72); font-size: 0.95rem; max-width: 820px;
            margin: 0 auto 0.8rem; text-align: center;
        }}

        /* CATEGORIES PILL */
        .categories {{ margin: 1rem 0 2rem; }}
        .categories-title {{
            font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; font-size: 1.8rem;
            text-align: center; margin-bottom: 1.2rem;
            background: var(--grad); -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; background-clip: text;
        }}
        .category-grid {{
            display: flex; flex-wrap: wrap; gap: 10px;
            justify-content: center; align-items: center;
            background: linear-gradient(135deg,#0a1a4a 0%,#0d1f5c 40%,#1a0a2e 70%,#3a0a10 100%);
            border: 1px solid rgba(232,25,44,0.25); border-radius: 60px;
            padding: 18px 28px;
            box-shadow: 0 0 0 1px rgba(0,40,104,0.4), 0 8px 32px rgba(0,0,0,0.6),
                        0 0 40px rgba(232,25,44,0.15), 0 0 80px rgba(0,40,104,0.2),
                        inset 0 1px 0 rgba(255,255,255,0.06);
        }}
        .category-item {{
            color: white; padding: 7px 16px; border-radius: 50px;
            text-decoration: none; font-weight: 700; font-size: 0.83rem;
            background: linear-gradient(135deg,rgba(26,58,138,0.7),rgba(232,25,44,0.6));
            border: 1px solid rgba(255,255,255,0.12);
            transition: transform 0.2s, box-shadow 0.2s, background 0.2s; white-space: nowrap;
        }}
        .category-item:hover {{
            transform: translateY(-2px);
            background: linear-gradient(135deg,var(--blue-mid),var(--red));
            box-shadow: 0 4px 18px rgba(232,25,44,0.45), 0 0 12px rgba(232,25,44,0.2);
            border-color: rgba(232,25,44,0.4);
        }}
        .category-item.active {{
            background: linear-gradient(135deg,var(--blue-mid),var(--red)) !important;
            border-color: rgba(232,25,44,0.5);
            box-shadow: 0 4px 18px rgba(232,25,44,0.4);
        }}

        /* SCROLL TOP */
        #scrollToTopBtn {{
            position: fixed; bottom: 22px; right: 22px; z-index: 99;
            border: none; outline: none; background: var(--grad); color: white;
            cursor: pointer; border-radius: 50%; width: 46px; height: 46px; font-size: 16px;
            display: flex; align-items: center; justify-content: center;
            opacity: 0; visibility: hidden; transition: opacity 0.3s, visibility 0.3s, transform 0.2s;
        }}
        #scrollToTopBtn.show {{ opacity: 1; visibility: visible; }}
        #scrollToTopBtn:hover {{ transform: scale(1.1); }}

        /* FOOTER */
        footer {{
            background: #010812; border-top: 2px solid;
            border-image: var(--grad) 1; padding: 1.5rem 0; margin-top: 1rem;
        }}
        .footer-bottom {{ text-align: center; color: #ffffff; font-size: 0.82rem; }}
        .footer-bottom p {{ color: #ffffff; }}
        .footer-links {{ display: flex; justify-content: center; gap: 1.2rem; margin-top: 0.5rem; flex-wrap: wrap; }}
        .footer-links a {{ color: #ffffff; text-decoration: none; transition: color 0.2s; }}
        .footer-links a:hover {{ color: rgba(255,255,255,0.65); }}

        /* RESPONSIVE */
        @media (max-width: 992px) {{
            .nav-toggle {{ display: block; }}
            .main-nav ul {{ display: none; flex-direction: column; align-items: center; border-radius: 20px; padding: 10px 16px; }}
            .main-nav ul.active {{ display: flex; }}
            .logo {{ font-size: 1.5rem; }}
        }}
        @media (max-width: 768px) {{
            .games-grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.9rem; }}
            .category-header h1 {{ font-size: 2rem; }}
            .category-grid {{ border-radius: 24px; padding: 16px 18px; gap: 8px; }}
            .category-item {{ font-size: 0.8rem; padding: 6px 13px; }}
        }}
        @media (max-width: 600px) {{
            .main-nav ul {{ border-radius: 16px; padding: 8px 12px; gap: 3px; }}
            .main-nav a {{ font-size: 0.76rem; padding: 4px 9px; }}
        }}
        @media (max-width: 480px) {{
            .games-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .search-bar input {{ width: 130px; }}
        }}
    </style>
</head>
<body>

<header>
    <div class="container header-content">
        <a href="/" class="logo">Unblocked Games USA</a>
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Search games..." autocomplete="off">
            <button id="searchBtn" aria-label="Search"><i class="fas fa-search"></i></button>
            <div class="search-dropdown" id="searchDropdown"></div>
        </div>
        <nav class="main-nav">
            <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation">
                <i class="fas fa-bars"></i>
            </button>
            <ul id="navMenu">
                {nav_html}
            </ul>
        </nav>
    </div>
</header>

<div class="container">

    <div class="category-header">
        <div class="category-header-glow"></div>
        <h1>{emoji} {name}</h1>
        <p>{cat["tagline"]}</p>
    </div>

    <h2 class="section-title">Popular {name}</h2>

    <div class="games-grid" id="gamesGrid">
        {games_html}
    </div>

    {pagination_html}

    <div class="category-description">
        <h2>{emoji} {name}</h2>
        <p>{cat["description"]}</p>
        <h3>{cat["h3"]}</h3>
        <p>{cat["h3desc"]}</p>
    </div>

    <div class="categories">
        <h2 class="categories-title">🎮 Browse by Category</h2>
        <div class="category-grid">
            {cat_grid_html}
        </div>
    </div>

</div>

<footer>
    <div class="container">
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
</footer>

<a href="#" id="scrollToTopBtn" title="Go to top"><i class="fas fa-arrow-up"></i></a>

<script>
    document.getElementById('currentYear').textContent = new Date().getFullYear();

    const navToggle = document.getElementById('navToggle');
    const navMenu   = document.getElementById('navMenu');
    navToggle?.addEventListener('click', () => navMenu.classList.toggle('active'));

    const header    = document.querySelector('header');
    const scrollBtn = document.getElementById('scrollToTopBtn');
    let lastScroll  = 0;
    window.addEventListener('scroll', () => {{
        const st = window.pageYOffset;
        header.classList.toggle('header-hidden', st > lastScroll && st > header.offsetHeight);
        lastScroll = st <= 0 ? 0 : st;
        scrollBtn.classList.toggle('show', st > 100);
    }});
    scrollBtn?.addEventListener('click', e => {{ e.preventDefault(); window.scrollTo({{ top:0, behavior:'smooth' }}); }});

    const searchInput = document.getElementById('searchInput');
    const searchBtn   = document.getElementById('searchBtn');
    const dropdown    = document.getElementById('searchDropdown');
    const allCards    = Array.from(document.querySelectorAll('.game-card'));

    function showDropdown(query) {{
        const q = query.trim().toLowerCase();
        if (!q) {{ closeDropdown(); return; }}
        const matches = allCards
            .filter(c => c.querySelector('.game-title').textContent.toLowerCase().includes(q))
            .slice(0, 8);
        if (matches.length === 0) {{
            dropdown.innerHTML = `<div class="no-results">No results — press Enter to search all games</div>`;
        }} else {{
            dropdown.innerHTML = matches.map(card => {{
                const title = card.querySelector('.game-title').textContent;
                const href  = card.querySelector('.game-link').getAttribute('href');
                const img   = card.querySelector('img')?.getAttribute('src') || '';
                return `<a href="${{href}}">
                    <img src="${{img}}" alt="${{title}}" style="width:32px;height:24px;object-fit:cover;border-radius:4px;flex-shrink:0;" onerror="this.style.display='none'">
                    ${{title}}
                </a>`;
            }}).join('');
        }}
        dropdown.classList.add('active');
    }}
    function closeDropdown() {{ dropdown.classList.remove('active'); dropdown.innerHTML = ''; }}
    function doSearch(q) {{
        if (!q.trim()) return;
        window.location.href = `/?q=${{encodeURIComponent(q.trim())}}`;
    }}
    searchInput.addEventListener('input', e => showDropdown(e.target.value));
    searchInput.addEventListener('keydown', e => {{
        if (e.key === 'Enter') doSearch(searchInput.value);
        if (e.key === 'Escape') closeDropdown();
    }});
    searchBtn.addEventListener('click', () => doSearch(searchInput.value));
    document.addEventListener('click', e => {{ if (!e.target.closest('.search-bar')) closeDropdown(); }});

    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q) {{ searchInput.value = q; showDropdown(q); }}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# 6.  BUILD ALL PAGES
# ─────────────────────────────────────────────
def main():
    base = os.path.dirname(os.path.abspath(__file__))
    pages_created = 0

    for cat in CATEGORIES:
        slug = cat["slug"]

        # Filter games that belong to this category
        cat_games = [g for g in GAMES if slug in g["cats"]]

        total_pages = max(1, math.ceil(len(cat_games) / GAMES_PER_PAGE))

        # Build nav / cat grid once (same for all pages of this category)
        nav_html      = build_nav(slug)
        cat_grid_html = build_cat_grid(slug)

        for page in range(1, total_pages + 1):
            start = (page - 1) * GAMES_PER_PAGE
            end   = start + GAMES_PER_PAGE
            page_games = cat_games[start:end]

            games_html      = "\n".join(game_card(g, slug) for g in page_games)
            pagination_html = build_pagination(slug, page, total_pages)

            html = render_page(cat, games_html, pagination_html, nav_html, cat_grid_html)

            # Determine output folder
            if page == 1:
                folder = os.path.join(base, "categ", slug)
            else:
                folder = os.path.join(base, "categ", f"{slug}-page-{page}")

            os.makedirs(folder, exist_ok=True)
            out_path = os.path.join(folder, "index.html")

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)

            pages_created += 1
            print(f"  ✓  {out_path}  ({len(page_games)} games)")

    print(f"\n✅  Done! {pages_created} page(s) generated.")
    print("   Commit and push the updated categ/ folder to GitHub.")


if __name__ == "__main__":
    main()