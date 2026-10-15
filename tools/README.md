# Build tools
`python3 tools/build.py` regenerates every page under `game/`, `category/`, `games/`, plus `sitemap.xml`, `robots.txt` and the `game.html` redirect from `data/games.json`.
Run it after adding or editing games, then commit the generated files.
Optional per-game fields in `data/games.json` override the generic copy: `description`, `metaDescription`, `howToPlay`, `controls`, `tips`, `features`, `faq`.
Category copy lives in `tools/content.py`.
