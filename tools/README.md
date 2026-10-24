# Build tools
`python3 tools/build.py` regenerates every page from `data/games.json`: `index.html`, `game/`, `category/`, `games/`, `games-like-wordle/`,
the four static pages (`about us.html`, `dmca.html`, `privacy-policy.html`, `terms.html`), plus `sitemap.xml`, `robots.txt` and the `game.html` redirect.
Run it after adding or editing games or copy, then commit the generated files.

- Optional per-game fields in `data/games.json` override the generic copy: `description`, `metaDescription`, `howToPlay`, `controls`, `tips`, `features`, `faq`.
- Category copy lives in `tools/content.py`.
- Text of About / DMCA / Privacy / Terms lives in `tools/pages/*.html` (edit there, not in the generated root files).
- Icons live in `tools/icons.py` (same icon set as /classroom6x/).

## Shared look with /classroom6x/
`assets/site.css` is the same file as `classroom6x/assets/style.css`. If you change one, copy it to the other.
`assets/site-extra.css` only holds styles specific to this site (16:9 thumbnails, long game text, A-Z list).
The light/dark choice is stored under the same key (`c6x-theme`), so it carries between both sites.
`404.html` redirects instantly to the main site root with no button.
