# Unblocked Games USA — Modern Portal

A fast, static game portal. No build tools, no server, no database — it runs
anywhere that serves files, including GitHub Pages.

The catalog contains **704 game listings imported from puzzio.io** (loaded
through their game-file endpoints, which were technically tested and worked
in our tests) plus one self-hosted demo game. The previous library
(iframe.unblocked-76-games.org) was removed because that host stopped
serving games. Game files themselves remain externally hosted — nothing is
re-hosted in this repository.

**Files:**

```
├── index.html            Homepage: hero, search, category filters, game grid
├── game.html             Shared player page (?id=<game-id>)
├── 404.html              Not-found page
├── data/games.json       ⭐ THE ONE FILE YOU EDIT — the whole game catalog
└── assets/               Styles, scripts, favicon
```

## Add or replace a game (the only thing you need to know)

Open `data/games.json`. Every game is one block:

```json
{
  "id": "my-new-game",
  "title": "My New Game",
  "categories": ["action", "2-player"],
  "image": "images/my-new-game.png",
  "embedUrl": "https://iframe.example.com/my-new-game"
}
```

To add a game:

1. Find the game's embed URL — use a URL authorized by the game's owner or
   distributor (for example a distributor's official embed code: copy what is
   inside `src="…"` of the `<iframe>` they give you).
2. Paste it into `"embedUrl"`.
3. Pick a short lowercase `"id"` (letters, numbers, hyphens only) — it becomes
   the link: `game.html?id=my-new-game`.
4. Add a thumbnail and put its URL in `"image"`.
5. Copy an existing block, change the fields, save. Done — the game appears
   in the grid, in search, and in its categories automatically.

To replace a game's iframe: just change its `"embedUrl"` value.

## Thumbnails

The imported catalog uses puzzio.io's image CDN (`cdn.puzzio.io`) — an external
dependency, like the games themselves. If you prefer local thumbnails, put a
file in `images/` and point `"image"` at it (the included demo game does
this: `images/neon-breakout.svg`). Your old site's `images/` folder
(`unblockedgames-usa.github.io/images/<id>.png`) is also still live and can
be referenced the same way.

## 404 page base path

`404.html` contains a `SITE_BASE` setting near the bottom. Set it to `/` for
a username site (`yourname.github.io`) or to `/<repo-name>/` when deploying
as a project repository, so the "Back to all games" link points correctly.

## Updating your EXISTING repo (keeping the domain)

The domain `unblockedgames-usa.github.io` is served by the repo
`UnblockedGames-USA.github.io`. You can replace that repo's files with this
site and the domain stays the same. Do it in stages, with a backup:

**Step 0 — back up the old site first:**

```
git clone https://github.com/UnblockedGames-USA/UnblockedGames-USA.github.io.git
cd UnblockedGames-USA.github.io
git checkout -b backup-old-site
git push -u origin backup-old-site
git checkout main
```

Now the old site is preserved on a `backup-old-site` branch — you can
always restore it.

**Step 1 — check what to keep.** Look at the repo root and note anything
that must survive the swap: `ads.txt` (AdSense), any `CNAME` file, search-
console verification files, `robots.txt`, or GitHub Pages settings
(Settings → Pages stays configured by branch; it does not change).

**Step 2 — replace the files.** With the old site backed up, delete the
old content and copy this site's files in:

```
# from the repo root, on main:
find . -mindepth 1 -maxdepth 1 ! -name ".git" -exec rm -rf {} +

# then copy in everything from this ZIP (it includes an ads.txt with the
# exact same content as your current one), then:
git add -A
git commit -m "New game portal"
git push
```

A couple of minutes after pushing, the new site is live on the same
domain.

## AdSense after the swap

- **ads.txt** — this ZIP includes an `ads.txt` with the exact same content
  as your current one, so the Authorized status should carry over.
- **Ad code** — `index.html` and `game.html` each contain a marked
  `ADSENSE` comment in `<head>` with your publisher ID
  (`ca-pub-4672956141931257`) already filled in. Uncomment it when you
  want ads to show, and enable Auto ads in your AdSense account. Your
  Google Analytics tag is already active on both pages.
- **Expectations** — the same domain and ads.txt give this the best chance
  of continuing smoothly, but AdSense approval and rankings are never
  guaranteed by a redesign: the old site had one indexed page per game
  (`/1v1-lol/` …) which will now 404, so search traffic will likely dip
  before the new `game.html?id=…` pages get indexed. Watch the Sites page
  in AdSense after the swap.
- **Content rights** — the imported game listings are served from puzzio.io.
  Verify that your AdSense use of that content complies with Google's
  publisher policies (sites must own or have rights to monetize their
  content). If in doubt, replace listings with authorized distributor
  embeds or self-hosted games over time.

## Deploy on GitHub Pages (alternative: new repo)

1. Create a new repository (for example `games-portal`).
2. Upload all files in this folder to the repository root.
3. Repository → Settings → Pages → Source: `main` branch, `/ (root)`.
4. Wait ~2 minutes. Your site is at
   `https://<username>.github.io/games-portal/`.

No build step. Every link is relative, so it works under any subpath.

## Self-hosted games (optional)

The portal also works with games you host yourself. `local/neon-breakout.html` is
a small built-in game that ships with the site — its catalog entry uses a
relative `"embedUrl": "local/neon-breakout.html"`. To add your own game this
way: drop an HTML file into `local/`, give it an `"embedUrl": "local/your-game.html"`
entry, and it plays inside the same player.

## Categories

Categories come from the JSON — you do not configure them anywhere else.
Any value used in `"categories"` appears as a filter chip automatically
(present ones: action, arcade, puzzle, simulation, clicker, driving, adventure,
casual, shooting, sports, beauty, strategy, word, board, skill).

## Notes

- The player page is one shared file: `game.html?id=<id>`. There is nothing
  to regenerate when you add games.
- Keyboard shortcut: press `/` on the homepage to jump to search.
- Games load inside an iframe from an external host — currently puzzio.io's
game-file endpoints, tested working at import time. That also means they
control those URLs: if puzzio changes or blocks them, games stop working
and the catalog links would need updating. For a long-term source you
control, consider authorized game distributors (GameDistribution,
GameMonetize) or self-hosted games — drop them into `local/` like the
included demo game.
- Deploying this as a NEW repository keeps your old site and its `/<slug>/`
  pages untouched. If you later replace the old repository, its old page
  routes go away — external links to `unblockedgames-usa.github.io/<game>/`
  would need redirects.
