#!/usr/bin/env node
/**
 * UnblockedGames-USA Build Script
 * ================================
 * Run: node build.js
 *
 * What it does:
 *  1. Scans every game folder (any dir with an index.html that has <iframe>)
 *  2. Extracts title, thumbnail, categories, tags from each game's index.html
 *  3. Writes games.json (full data) + search-index.json (lightweight for client)
 *  4. Regenerates all categ/<category>/index.html pages with FULL game lists + pagination
 *  5. Patches every game's index.html to replace the static "similar games" section
 *     with dynamically chosen games from the same categories
 *
 * Requirements: Node.js 16+  (no npm install needed – uses only built-ins)
 */

const fs   = require('fs');
const path = require('path');

// ─── CONFIG ────────────────────────────────────────────────────────────────
const ROOT        = process.cwd();          // run from repo root
const IMAGES_BASE = 'https://unblockedgames-usa.github.io/images/';
const SITE_BASE   = 'https://unblockedgames-usa.github.io/';
const GAMES_PER_PAGE = 48;                  // games per category page
const SIMILAR_COUNT  = 12;                  // similar games to show per game page

const CATEGORIES = [
  { slug: 'shooter',     emoji: '🎯', label: 'Shooter' },
  { slug: 'platformer',  emoji: '🏃', label: 'Platformer' },
  { slug: '2-player',    emoji: '👥', label: '2-Player' },
  { slug: 'fighting',    emoji: '🥊', label: 'Fighting' },
  { slug: 'driving',     emoji: '🚗', label: 'Driving' },
  { slug: 'puzzle',      emoji: '🧠', label: 'Puzzle' },
  { slug: 'multiplayer', emoji: '🌐', label: 'Multiplayer' },
  { slug: 'action',      emoji: '💥', label: 'Action' },
  { slug: 'skill',       emoji: '🏆', label: 'Skill' },
  { slug: 'adventure',   emoji: '🗺️', label: 'Adventure' },
  { slug: 'racing',      emoji: '🏁', label: 'Racing' },
  { slug: 'strategy',    emoji: '♟️', label: 'Strategy' },
  { slug: 'sports',      emoji: '⚽', label: 'Sports' },
  { slug: 'simulation',  emoji: '🏙️', label: 'Simulation' },
  { slug: 'clicker',     emoji: '🖱️', label: 'Clicker' },
  { slug: 'horror',      emoji: '👻', label: 'Horror' },
  { slug: 'kids',        emoji: '🧸', label: 'Kids' },
];

// Folders to skip (non-game directories)
const SKIP_DIRS = new Set([
  'assets', 'images', 'categ', 'node_modules', '.git',
  'privacy-policy', 'contact', 'faq', 'dmca',
]);

// ─── HELPERS ───────────────────────────────────────────────────────────────

function readFile(filePath) {
  try { return fs.readFileSync(filePath, 'utf8'); }
  catch { return null; }
}

function writeFile(filePath, content) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content, 'utf8');
}

function slugToTitle(slug) {
  return slug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function extractMeta(html, tag, attr) {
  const re = new RegExp(`<meta[^>]+${attr}=["']${tag}["'][^>]*content=["']([^"']+)["']`, 'i');
  const re2 = new RegExp(`<meta[^>]+content=["']([^"']+)["'][^>]*${attr}=["']${tag}["']`, 'i');
  const m = html.match(re) || html.match(re2);
  return m ? m[1].trim() : null;
}

function extractTitle(html) {
  // Try og:title first, then <title> tag
  const og = extractMeta(html, 'og:title', 'property') || extractMeta(html, 'og:title', 'name');
  if (og) return og.replace(/\s*[-|].*$/, '').trim();
  const t = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  if (t) return t[1].replace(/\s*[-|].*$/, '').trim();
  return null;
}

function extractCategories(html) {
  const cats = [];
  // Look for category tags like: data-category="adventure" or class="tag adventure" or links to categ/
  const tagLinks = html.matchAll(/href=["'][^"']*\/categ\/([a-z0-9-]+)[/"']/gi);
  for (const m of tagLinks) cats.push(m[1].toLowerCase());

  // Also look for explicit tag spans/buttons
  const tagSpans = html.matchAll(/(?:category|tag)[^>]*>([A-Za-z0-9 -]+)</gi);
  for (const m of tagSpans) {
    const slug = m[1].trim().toLowerCase().replace(/\s+/g, '-');
    if (CATEGORIES.find(c => c.slug === slug)) cats.push(slug);
  }

  // Also search for keywords in the page text
  const lower = html.toLowerCase();
  for (const cat of CATEGORIES) {
    if (lower.includes(`"${cat.slug}"`) || lower.includes(`'${cat.slug}'`)) {
      if (!cats.includes(cat.slug)) cats.push(cat.slug);
    }
  }

  return [...new Set(cats)].filter(c => CATEGORIES.find(x => x.slug === c));
}

function extractImage(slug, html) {
  // Prefer images/<slug>.png/jpg
  const candidates = [
    `images/${slug}.png`,
    `images/${slug}.jpg`,
    `images/${slug}.webp`,
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(ROOT, c))) return `${SITE_BASE}${c}`;
  }
  // Try og:image
  const og = extractMeta(html, 'og:image', 'property') || extractMeta(html, 'og:image', 'name');
  if (og) return og;
  return `${SITE_BASE}images/${slug}.png`; // fallback (may 404 but still reference)
}

function hasIframe(html) {
  return /<iframe/i.test(html);
}

// ─── NAV HTML ──────────────────────────────────────────────────────────────

function navHtml(prefix = '') {
  const links = CATEGORIES.map(c =>
    `<li><a href="${prefix}categ/${c.slug}">${c.emoji} ${c.label}</a></li>`
  ).join('\n      ');
  return `<nav>
    <a class="logo" href="${prefix || '/'}">Unblocked Games USA</a>
    <ul>
      ${links}
    </ul>
    <form class="search-form" action="${prefix || '/'}index.html" method="get">
      <input type="search" name="q" placeholder="Search games..." autocomplete="off">
      <button type="submit">🔍</button>
    </form>
  </nav>`;
}

function footerHtml(prefix = '') {
  const cats = CATEGORIES.map(c =>
    `<a href="${prefix}categ/${c.slug}">${c.emoji} ${c.label}</a>`
  ).join('\n    ');
  return `<footer>
  <div class="footer-cats">
    ${cats}
  </div>
  <div class="footer-links">
    <a href="${prefix}privacy-policy">Privacy Policy</a>
    <a href="${prefix}contact">Contact Us</a>
    <a href="${prefix}faq">FAQ</a>
    <a href="${prefix}dmca">DMCA</a>
  </div>
  <p>&copy; Unblocked Games USA. All rights reserved.</p>
</footer>`;
}

// ─── GAME CARD ──────────────────────────────────────────────────────────────

function gameCard(game, prefix = '') {
  const url = `${prefix || '/'}${game.slug}`;
  return `<a class="game-card" href="${url}">
      <img src="${game.image}" alt="${game.title}" loading="lazy" width="200" height="150">
      <span>${game.title}</span>
    </a>`;
}

// ─── PAGINATION ─────────────────────────────────────────────────────────────

function paginationHtml(catSlug, currentPage, totalPages) {
  if (totalPages <= 1) return '';
  let html = '<div class="pagination">';
  if (currentPage > 1) {
    const href = currentPage === 2
      ? `../../categ/${catSlug}/`
      : `../../categ/${catSlug}-page-${currentPage - 1}/`;
    html += `<a href="${href}">&laquo; Previous</a>`;
  }
  for (let i = 1; i <= totalPages; i++) {
    const href = i === 1
      ? `../../categ/${catSlug}/`
      : `../../categ/${catSlug}-page-${i}/`;
    const active = i === currentPage ? ' class="active"' : '';
    html += `<a href="${href}"${active}>${i}</a>`;
  }
  if (currentPage < totalPages) {
    const href = `../../categ/${catSlug}-page-${currentPage + 1}/`;
    html += `<a href="${href}">Next &raquo;</a>`;
  }
  html += '</div>';
  return html;
}

// ─── CSS (shared, embedded in pages) ────────────────────────────────────────

const SHARED_CSS = `
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,sans-serif;background:#0d1117;color:#e6edf3;min-height:100vh}
  a{color:inherit;text-decoration:none}
  nav{background:linear-gradient(90deg,#1a0533,#8b0000);padding:12px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
  .logo{font-weight:700;font-size:1.1rem;white-space:nowrap}
  nav ul{display:flex;list-style:none;gap:8px;flex-wrap:wrap;flex:1}
  nav ul li a{background:rgba(255,255,255,.1);padding:4px 10px;border-radius:20px;font-size:.82rem;white-space:nowrap;transition:background .2s}
  nav ul li a:hover{background:rgba(255,255,255,.25)}
  .search-form{display:flex;gap:6px;margin-left:auto}
  .search-form input{padding:6px 12px;border-radius:20px;border:none;background:rgba(255,255,255,.15);color:#fff;width:180px}
  .search-form input::placeholder{color:rgba(255,255,255,.5)}
  .search-form button{background:#c0392b;color:#fff;border:none;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:1rem}
  main{max-width:1280px;margin:0 auto;padding:24px 16px}
  h1{font-size:1.8rem;margin-bottom:8px}
  .subtitle{color:#8b949e;margin-bottom:24px}
  .games-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px;margin-bottom:32px}
  .game-card{display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:10px;overflow:hidden;transition:transform .2s,box-shadow .2s}
  .game-card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.4)}
  .game-card img{width:100%;height:120px;object-fit:cover}
  .game-card span{padding:8px;font-size:.82rem;text-align:center;font-weight:500}
  .section-title{font-size:1.3rem;margin:32px 0 16px;color:#58a6ff}
  .pagination{display:flex;gap:8px;justify-content:center;margin:24px 0;flex-wrap:wrap}
  .pagination a{padding:8px 14px;background:#161b22;border-radius:6px;transition:background .2s}
  .pagination a:hover,.pagination a.active{background:#58a6ff;color:#000}
  .cat-grid{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:32px}
  .cat-grid a{background:#161b22;padding:8px 14px;border-radius:20px;font-size:.85rem;transition:background .2s}
  .cat-grid a:hover{background:#58a6ff;color:#000}
  footer{background:#161b22;padding:32px 24px;margin-top:48px;text-align:center}
  .footer-cats{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:16px}
  .footer-cats a{background:rgba(255,255,255,.08);padding:6px 12px;border-radius:16px;font-size:.82rem}
  .footer-links{display:flex;gap:16px;justify-content:center;margin-bottom:12px;font-size:.85rem;opacity:.7}
  footer p{font-size:.8rem;opacity:.5}
  /* Search results */
  #search-results-section{margin-bottom:32px}
  #no-results{color:#f85149;margin:16px 0;display:none}
  /* Game page */
  .game-frame-wrap{background:#000;border-radius:10px;overflow:hidden;margin-bottom:32px;position:relative;padding-top:56.25%}
  .game-frame-wrap iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:none}
  .game-meta{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
  .game-meta .tag{background:#21262d;padding:4px 12px;border-radius:16px;font-size:.82rem}
  /* Search overlay */
  #search-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.85);z-index:1000;overflow-y:auto;padding:80px 24px 24px}
  #search-overlay.active{display:block}
  #search-close{position:fixed;top:16px;right:24px;background:#c0392b;color:#fff;border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:1.2rem;z-index:1001}
  #search-box{max-width:800px;margin:0 auto}
  #search-input-big{width:100%;padding:12px 20px;font-size:1.1rem;border-radius:10px;border:none;background:#161b22;color:#fff;margin-bottom:24px}
  #search-results-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}
`;

// ─── SCAN GAMES ─────────────────────────────────────────────────────────────

function scanGames() {
  console.log('📂 Scanning game folders…');
  const games = [];
  const entries = fs.readdirSync(ROOT, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (SKIP_DIRS.has(entry.name)) continue;
    if (entry.name.startsWith('.')) continue;

    const slug = entry.name;
    const indexPath = path.join(ROOT, slug, 'index.html');
    const html = readFile(indexPath);
    if (!html) continue;
    if (!hasIframe(html)) continue; // skip non-game pages

    const title = extractTitle(html) || slugToTitle(slug);
    const cats  = extractCategories(html);
    const image = extractImage(slug, html);

    games.push({ slug, title, image, categories: cats });
  }

  console.log(`✅ Found ${games.length} games`);
  return games.sort((a, b) => a.title.localeCompare(b.title));
}

// ─── WRITE games.json + search-index.json ───────────────────────────────────

function writeDataFiles(games) {
  writeFile(path.join(ROOT, 'games.json'), JSON.stringify(games, null, 2));

  const searchIndex = games.map(g => ({
    slug: g.slug,
    title: g.title,
    image: g.image,
    categories: g.categories,
  }));
  writeFile(path.join(ROOT, 'search-index.json'), JSON.stringify(searchIndex));
  console.log('📄 Wrote games.json + search-index.json');
}

// ─── CATEGORY PAGES ─────────────────────────────────────────────────────────

function buildCategoryPages(games) {
  for (const cat of CATEGORIES) {
    const catGames = games.filter(g => g.categories.includes(cat.slug));
    const totalPages = Math.max(1, Math.ceil(catGames.length / GAMES_PER_PAGE));

    for (let page = 1; page <= totalPages; page++) {
      const slice = catGames.slice((page - 1) * GAMES_PER_PAGE, page * GAMES_PER_PAGE);
      const isFirst = page === 1;
      const dirName = isFirst ? `categ/${cat.slug}` : `categ/${cat.slug}-page-${page}`;
      const prefix  = '../../';
      const canonicalUrl = isFirst
        ? `${SITE_BASE}categ/${cat.slug}/`
        : `${SITE_BASE}categ/${cat.slug}-page-${page}/`;

      const pageTitle = page === 1
        ? `${cat.emoji} ${cat.label} Games Unblocked – Play Free Online`
        : `${cat.emoji} ${cat.label} Games – Page ${page}`;

      const cards = slice.map(g => gameCard(g, prefix)).join('\n    ');
      const pagination = paginationHtml(cat.slug, page, totalPages);
      const otherCats = CATEGORIES.filter(c => c.slug !== cat.slug)
        .map(c => `<a href="${prefix}categ/${c.slug}">${c.emoji} ${c.label}</a>`).join('\n    ');

      const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>${pageTitle}</title>
  <meta name="description" content="Play free unblocked ${cat.label} games online. No downloads, no sign-ups. ${catGames.length} games available.">
  <link rel="canonical" href="${canonicalUrl}">
  <meta property="og:title" content="${pageTitle}">
  <meta property="og:type" content="website">
  <style>${SHARED_CSS}</style>
</head>
<body>
${navHtml(prefix)}
<main>
  <h1>${cat.emoji} ${cat.label} Games</h1>
  <p class="subtitle">${catGames.length} free unblocked ${cat.label} games — no downloads, play instantly!</p>

  <div class="games-grid">
    ${cards}
  </div>

  ${pagination}

  <h2 class="section-title">🎮 Browse Other Categories</h2>
  <div class="cat-grid">
    ${otherCats}
  </div>
</main>
${footerHtml(prefix)}
</body>
</html>`;

      writeFile(path.join(ROOT, dirName, 'index.html'), html);
    }

    console.log(`  ✓ ${cat.slug}: ${catGames.length} games across ${totalPages} page(s)`);
  }
}

// ─── HOMEPAGE (search-enabled) ───────────────────────────────────────────────

function buildHomepage(games) {
  // Pick ~45 popular/featured games for the visible grid
  const featured = games.slice(0, 48);
  const cards = featured.map(g => gameCard(g, '')).join('\n    ');
  const catLinks = CATEGORIES.map(c =>
    `<a href="categ/${c.slug}">${c.emoji} ${c.label}</a>`
  ).join('\n    ');

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Unblocked Games USA | Free Games To Play Online Instantly</title>
  <meta name="description" content="Free unblocked games for school. No downloads, no sign-ups. Hundreds of games across every genre.">
  <link rel="canonical" href="${SITE_BASE}">
  <style>${SHARED_CSS}
  .hero{text-align:center;padding:40px 0 24px}
  .hero h1{font-size:2.2rem;margin-bottom:8px}
  .hero p{color:#8b949e;max-width:600px;margin:0 auto 24px}
  .badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:32px}
  .badges span{background:#21262d;padding:6px 14px;border-radius:20px;font-size:.85rem}
  </style>
</head>
<body>
${navHtml('')}

<!-- Search overlay -->
<div id="search-overlay">
  <button id="search-close" onclick="closeSearch()">✕</button>
  <div id="search-box">
    <input id="search-input-big" type="search" placeholder="Search games…" oninput="doSearch(this.value)" autofocus>
    <div id="search-results-grid"></div>
  </div>
</div>

<main>
  <div class="hero">
    <h1>🎮 Unblocked Games USA</h1>
    <p>Free online games for every break. No downloads, no sign-ups. Perfect for a quick break between classes.</p>
    <div class="badges">
      <span>✅ No Downloads</span>
      <span>🎮 100% Free</span>
      <span>⚡ Play Instantly</span>
      <span>🏫 School Friendly</span>
    </div>
    <button onclick="openSearch()" style="background:#58a6ff;color:#000;border:none;padding:10px 28px;border-radius:24px;font-size:1rem;cursor:pointer;font-weight:600">🔍 Search All ${games.length} Games</button>
  </div>

  <h2 class="section-title">🔥 Popular Games</h2>
  <div class="games-grid">
    ${cards}
  </div>

  <h2 class="section-title">🎮 Browse by Category</h2>
  <div class="cat-grid">
    ${catLinks}
  </div>
</main>
${footerHtml('')}

<script>
let allGames = null;

async function loadGames() {
  if (allGames) return allGames;
  try {
    const r = await fetch('/search-index.json');
    allGames = await r.json();
  } catch {
    allGames = [];
  }
  return allGames;
}

function openSearch() {
  document.getElementById('search-overlay').classList.add('active');
  document.getElementById('search-input-big').focus();
  loadGames();
}

function closeSearch() {
  document.getElementById('search-overlay').classList.remove('active');
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSearch(); });

// Also hook nav search form
document.querySelector('.search-form').addEventListener('submit', e => {
  e.preventDefault();
  const q = document.querySelector('.search-form input').value.trim();
  if (q) { openSearch(); setTimeout(() => { document.getElementById('search-input-big').value = q; doSearch(q); }, 50); }
});

async function doSearch(q) {
  const games = await loadGames();
  const term = q.toLowerCase().trim();
  const grid = document.getElementById('search-results-grid');
  if (!term) { grid.innerHTML = ''; return; }
  const results = games.filter(g =>
    g.title.toLowerCase().includes(term) ||
    (g.categories || []).some(c => c.includes(term)) ||
    g.slug.replace(/-/g,' ').includes(term)
  ).slice(0, 60);
  if (!results.length) {
    grid.innerHTML = '<p style="color:#f85149;text-align:center">No games found. Try different keywords.</p>';
    return;
  }
  grid.innerHTML = results.map(g =>
    '<a class="game-card" href="/' + g.slug + '">' +
    '<img src="' + g.image + '" alt="' + g.title + '" loading="lazy" width="200" height="150">' +
    '<span>' + g.title + '</span></a>'
  ).join('');
}
</script>
</body>
</html>`;

  writeFile(path.join(ROOT, 'index.html'), html);
  console.log('🏠 Homepage rebuilt with live search');
}

// ─── PATCH GAME PAGES (similar games) ───────────────────────────────────────

function buildSimilarGames(game, allGames) {
  // Find games in same categories, excluding itself
  const sameCategory = allGames.filter(g =>
    g.slug !== game.slug &&
    g.categories.some(c => game.categories.includes(c))
  );

  // Shuffle deterministically based on slug hash so it's stable but varies per game
  const shuffled = [...sameCategory].sort((a, b) => {
    const ha = simpleHash(game.slug + a.slug);
    const hb = simpleHash(game.slug + b.slug);
    return ha - hb;
  });

  return shuffled.slice(0, SIMILAR_COUNT);
}

function simpleHash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function patchGamePages(games) {
  let patched = 0;
  for (const game of games) {
    const indexPath = path.join(ROOT, game.slug, 'index.html');
    let html = readFile(indexPath);
    if (!html) continue;

    const similar = buildSimilarGames(game, games);
    if (!similar.length) continue;

    const cards = similar.map(g => {
      return `<a class="game-card" href="../${g.slug}">
        <img src="${g.image}" alt="${g.title}" loading="lazy" width="200" height="150">
        <span>${g.title}</span>
      </a>`;
    }).join('\n      ');

    const similarSection = `
<!-- SIMILAR_GAMES_START -->
<section class="similar-games">
  <h2 class="section-title">🎮 Similar Games</h2>
  <div class="games-grid">
    ${cards}
  </div>
</section>
<!-- SIMILAR_GAMES_END -->`;

    // Replace existing similar games block or append before </main>
    if (html.includes('<!-- SIMILAR_GAMES_START -->')) {
      html = html.replace(
        /<!-- SIMILAR_GAMES_START -->[\s\S]*?<!-- SIMILAR_GAMES_END -->/,
        similarSection
      );
    } else if (html.includes('SIMILAR GAMES') || html.includes('similar-games') || html.includes('Similar Games')) {
      // Try to replace existing section heading area
      html = html.replace(
        /<(?:section|div)[^>]*class="[^"]*similar[^"]*"[^>]*>[\s\S]*?<\/(?:section|div)>/i,
        similarSection
      );
      // If still not replaced, append
      if (!html.includes('SIMILAR_GAMES_START')) {
        html = html.replace('</main>', similarSection + '\n</main>');
      }
    } else {
      // Just append before </main>
      html = html.replace('</main>', similarSection + '\n</main>');
    }

    // Also inject shared CSS if not present
    if (!html.includes('SHARED_CSS_INJECTED')) {
      const styleTag = `<style>/* SHARED_CSS_INJECTED */
.similar-games{margin-top:32px}
.section-title{font-size:1.3rem;margin:32px 0 16px;color:#58a6ff}
.games-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px;margin-bottom:32px}
.game-card{display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:10px;overflow:hidden;transition:transform .2s,box-shadow .2s;color:#e6edf3;text-decoration:none}
.game-card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.4)}
.game-card img{width:100%;height:120px;object-fit:cover}
.game-card span{padding:8px;font-size:.82rem;text-align:center;font-weight:500}
</style>`;
      html = html.replace('</head>', styleTag + '\n</head>');
    }

    writeFile(indexPath, html);
    patched++;
  }
  console.log(`🔗 Patched similar games in ${patched} game pages`);
}

// ─── MAIN ───────────────────────────────────────────────────────────────────

function main() {
  console.log('\n🚀 UnblockedGames-USA Build Script\n');

  const games = scanGames();

  if (!games.length) {
    console.error('❌ No games found! Make sure you run this from the repo root.');
    process.exit(1);
  }

  writeDataFiles(games);
  console.log('\n📁 Building category pages…');
  buildCategoryPages(games);
  console.log('\n🏠 Building homepage…');
  buildHomepage(games);
  console.log('\n🔗 Patching game pages with smart similar games…');
  patchGamePages(games);

  console.log('\n✅ Build complete!\n');
  console.log('Next steps:');
  console.log('  git add -A');
  console.log('  git commit -m "fix: full rebuild — category pages, search, similar games"');
  console.log('  git push');
}

try {
  main();
} catch (err) {
  console.error(err);
  process.exit(1);
}