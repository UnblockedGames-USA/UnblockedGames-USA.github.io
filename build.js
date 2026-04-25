#!/usr/bin/env node
/**
 * build.js — UnblockedGames-USA (SAFE VERSION)
 * ============================================
 * Never modifies game iframe or original content.
 * Only appends "Similar Games" AFTER </main>.
 *
 * Run: node build.js
 */

'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const SITE_BASE = 'https://unblockedgames-usa.github.io';
const GAMES_PER_PAGE = 48;
const SIMILAR_COUNT = 12;

const CATS = [
  { slug:'shooter', emoji:'🎯', label:'Shooter' },
  { slug:'platformer', emoji:'🏃', label:'Platformer' },
  { slug:'2-player', emoji:'👥', label:'2-Player' },
  { slug:'fighting', emoji:'🥊', label:'Fighting' },
  { slug:'driving', emoji:'🚗', label:'Driving' },
  { slug:'puzzle', emoji:'🧠', label:'Puzzle' },
  { slug:'multiplayer',emoji:'🌐', label:'Multiplayer'},
  { slug:'action', emoji:'💥', label:'Action' },
  { slug:'skill', emoji:'🏆', label:'Skill' },
  { slug:'adventure', emoji:'🗺️', label:'Adventure' },
  { slug:'racing', emoji:'🏁', label:'Racing' },
  { slug:'strategy', emoji:'♟️', label:'Strategy' },
  { slug:'sports', emoji:'⚽', label:'Sports' },
  { slug:'simulation', emoji:'🏙️', label:'Simulation' },
  { slug:'clicker', emoji:'🖱️', label:'Clicker' },
  { slug:'horror', emoji:'👻', label:'Horror' },
  { slug:'kids', emoji:'🧸', label:'Kids' },
];

const SKIP_DIRS = new Set([
  'assets','images','categ','node_modules','.git',
  'privacy-policy','contact','faq','dmca',
]);

const read = f => { try { return fs.readFileSync(f,'utf8'); } catch { return null; } };
const write = (f, c) => { fs.mkdirSync(path.dirname(f),{recursive:true}); fs.writeFileSync(f,c,'utf8'); };

function slugToTitle(slug) {
  return slug.split('-').map(w => w[0].toUpperCase()+w.slice(1)).join(' ');
}

function extractTitle(html) {
  const og = html.match(/<meta[^>]+(?:property|name)=["']og:title["'][^>]+content=["']([^"']+)["']/i)
           || html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+(?:property|name)=["']og:title["']/i);
  if (og) return og[1].replace(/\s*[-|].*$/,'').trim();
  const t = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  if (t) return t[1].replace(/\s*[-|].*$/,'').trim();
  return null;
}

function extractCats(html) {
  const found = new Set();
  for (const m of html.matchAll(/\/categ\/([a-z0-9-]+)/gi)) {
    const s = m[1].toLowerCase();
    if (CATS.find(c=>c.slug===s)) found.add(s);
  }
  for (const cat of CATS) {
    if (html.includes(`"${cat.slug}"`) || html.includes(`'${cat.slug}'`)) found.add(cat.slug);
  }
  return [...found];
}

function extractImage(slug, html) {
  for (const ext of ['png','jpg','webp']) {
    const p = path.join(ROOT,'images',`${slug}.${ext}`);
    if (fs.existsSync(p)) return `${SITE_BASE}/images/${slug}.${ext}`;
  }
  const og = html.match(/<meta[^>]+(?:property|name)=["']og:image["'][^>]+content=["']([^"']+)["']/i)
           || html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+(?:property|name)=["']og:image["']/i);
  if (og) return og[1];
  return `${SITE_BASE}/images/${slug}.png`;
}

function simpleHash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (Math.imul(31,h)+str.charCodeAt(i))|0;
  return Math.abs(h);
}

const SIMILAR_CSS = `<style id="ug-similar-css">
.ug-similar{font-family:system-ui,sans-serif;padding:24px 16px;max-width:1280px;margin:0 auto}
.ug-similar h2{font-size:1.2rem;color:#58a6ff;margin-bottom:16px}
.ug-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.ug-card{display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:8px;overflow:hidden;color:#e6edf3;text-decoration:none;transition:transform .15s}
.ug-card:hover{transform:translateY(-3px)}
.ug-card img{width:100%;height:110px;object-fit:cover}
.ug-card span{padding:6px;font-size:.78rem;text-align:center}
</style>`;

function navHtml(prefix) {
  const links = CATS.map(c=>`<li><a href="${prefix}categ/${c.slug}">${c.emoji} ${c.label}</a></li>`).join('');
  return `<nav style="background:linear-gradient(90deg,#1a0533,#8b0000);padding:10px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-family:system-ui,sans-serif">
  <a href="${prefix||'/'}" style="color:#fff;font-weight:700;text-decoration:none;font-size:1rem">Unblocked Games USA</a>
  <ul style="display:flex;list-style:none;gap:6px;flex-wrap:wrap;flex:1;margin:0;padding:0">
    ${links}
  </ul>
  <form action="${prefix||'/'}index.html" method="get" style="display:flex;gap:6px;margin-left:auto" onsubmit="event.preventDefault();window.location='${prefix||'/'}?q='+encodeURIComponent(this.q.value)">
    <input name="q" type="search" placeholder="Search games…" style="padding:5px 12px;border-radius:20px;border:none;background:rgba(255,255,255,.15);color:#fff;width:160px">
    <button type="submit" style="background:#c0392b;color:#fff;border:none;border-radius:50%;width:30px;height:30px;cursor:pointer">🔍</button>
  </form>
</nav>`;
}

function footerHtml(prefix) {
  const cats = CATS.map(c=>`<a href="${prefix}categ/${c.slug}" style="background:rgba(255,255,255,.08);padding:5px 11px;border-radius:16px;font-size:.8rem;color:#e6edf3;text-decoration:none">${c.emoji} ${c.label}</a>`).join(' ');
  return `<footer style="background:#161b22;padding:28px 20px;margin-top:40px;text-align:center;font-family:system-ui,sans-serif">
  <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:14px">${cats}</div>
  <div style="display:flex;gap:14px;justify-content:center;margin-bottom:10px;font-size:.83rem;opacity:.7">
    <a href="${prefix}privacy-policy" style="color:#e6edf3">Privacy Policy</a>
    <a href="${prefix}contact" style="color:#e6edf3">Contact Us</a>
    <a href="${prefix}faq" style="color:#e6edf3">FAQ</a>
    <a href="${prefix}dmca" style="color:#e6edf3">DMCA</a>
  </div>
  <p style="font-size:.78rem;opacity:.45">&copy; Unblocked Games USA. All rights reserved.</p>
</footer>`;
}

function card(g, prefix) {
  return `<a class="ug-card" href="${prefix}${g.slug}"><img src="${g.image}" alt="${g.title}" loading="lazy" width="150" height="110"><span>${g.title}</span></a>`;
}

function scanGames() {
  console.log('📂 Scanning game folders…');
  const games = [];
  for (const e of fs.readdirSync(ROOT,{withFileTypes:true})) {
    if (!e.isDirectory() || SKIP_DIRS.has(e.name) || e.name.startsWith('.')) continue;
    const html = read(path.join(ROOT,e.name,'index.html'));
    if (!html || !/<iframe/i.test(html)) continue;
    games.push({
      slug: e.name,
      title: extractTitle(html) || slugToTitle(e.name),
      image: extractImage(e.name, html),
      categories: extractCats(html),
    });
  }
  console.log(` ✓ ${games.length} games found`);
  return games.sort((a,b)=>a.title.localeCompare(b.title));
}

function writeData(games) {
  write(path.join(ROOT,'games.json'), JSON.stringify(games,null,2));
  write(path.join(ROOT,'search-index.json'), JSON.stringify(
    games.map(g=>({slug:g.slug,title:g.title,image:g.image,categories:g.categories}))
  ));
  console.log('📄 games.json + search-index.json written');
}

function buildCategoryPages(games) {
  console.log('📁 Building category pages…');
  for (const cat of CATS) {
    const list = games.filter(g=>g.categories.includes(cat.slug));
    const total = Math.max(1, Math.ceil(list.length/GAMES_PER_PAGE));
    for (let page = 1; page <= total; page++) {
      const slice = list.slice((page-1)*GAMES_PER_PAGE, page*GAMES_PER_PAGE);
      const dir = page===1 ? `categ/${cat.slug}` : `categ/${cat.slug}-page-${page}`;
      const pfx = '../../';
      const canonical = page===1 ? `${SITE_BASE}/categ/${cat.slug}/` : `${SITE_BASE}/categ/${cat.slug}-page-${page}/`;

      let pag = '';
      if (total > 1) {
        pag = '<div style="display:flex;gap:8px;justify-content:center;margin:24px 0;flex-wrap:wrap">';
        if (page>1) pag += `<a href="${pfx}categ/${page===2?cat.slug:`${cat.slug}-page-${page-1}`}/" style="padding:7px 14px;background:#161b22;border-radius:6px;color:#e6edf3;text-decoration:none">&laquo; Prev</a>`;
        for (let i=1;i<=total;i++) {
          const href = i===1?`${pfx}categ/${cat.slug}/`:`${pfx}categ/${cat.slug}-page-${i}/`;
          const active = i===page?'background:#58a6ff;color:#000':'background:#161b22;color:#e6edf3';
          pag += `<a href="${href}" style="padding:7px 14px;${active};border-radius:6px;text-decoration:none">${i}</a>`;
        }
        if (page<total) pag += `<a href="${pfx}categ/${cat.slug}-page-${page+1}/" style="padding:7px 14px;background:#161b22;border-radius:6px;color:#e6edf3;text-decoration:none">Next &raquo;</a>`;
        pag += '</div>';
      }

      const cards = slice.map(g=>card(g,pfx)).join('\n ');
      const otherCats = CATS.filter(c=>c.slug!==cat.slug)
        .map(c=>`<a href="${pfx}categ/${c.slug}" style="background:#21262d;padding:6px 12px;border-radius:16px;font-size:.82rem;color:#e6edf3;text-decoration:none">${c.emoji} ${c.label}</a>`).join(' ');

      write(path.join(ROOT,dir,'index.html'), `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${cat.emoji} ${cat.label} Games Unblocked – Free Online${page>1?' – Page '+page:''}</title>
<meta name="description" content="Play ${list.length} free unblocked ${cat.label} games. No downloads.">
<link rel="canonical" href="${canonical}">
<style>
*{box-sizing:border-box;margin:0;padding:0}body{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif}
a{color:inherit;text-decoration:none}
nav ul li a{background:rgba(255,255,255,.1);padding:4px 10px;border-radius:20px;font-size:.8rem;color:#fff;text-decoration:none;display:inline-block}
nav ul li a:hover{background:rgba(255,255,255,.25)}
main{max-width:1280px;margin:0 auto;padding:24px 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:20px 0}
.gc{display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:9px;overflow:hidden;transition:transform .15s}
.gc:hover{transform:translateY(-3px)}
.gc img{width:100%;height:110px;object-fit:cover}
.gc span{padding:7px 5px;font-size:.8rem;text-align:center}
</style>
</head>
<body>
${navHtml(pfx)}
<main>
  <h1 style="font-size:1.7rem;margin-bottom:6px">${cat.emoji} ${cat.label} Games</h1>
  <p style="color:#8b949e;margin-bottom:20px">${list.length} free unblocked ${cat.label} games — play instantly, no downloads!</p>
  <div class="grid">
    ${cards}
  </div>
  ${pag}
  <h2 style="font-size:1.1rem;color:#58a6ff;margin:28px 0 14px">🎮 Other Categories</h2>
  <div style="display:flex;flex-wrap:wrap;gap:8px">${otherCats}</div>
</main>
${footerHtml(pfx)}
</body>
</html>`);
    }
    console.log(` ✓ ${cat.slug}: ${list.length} games, ${total} page(s)`);
  }
}

function buildHomepage(games) {
  const featured = games.slice(0,48);
  const featuredCards = featured.map(g=>card(g,'/')).join('\n ');
  const catLinks = CATS.map(c=>`<a href="/categ/${c.slug}" style="background:#21262d;padding:7px 14px;border-radius:20px;font-size:.85rem;color:#e6edf3;text-decoration:none">${c.emoji} ${c.label}</a>`).join('\n ');

  write(path.join(ROOT,'index.html'), `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unblocked Games USA | Free Games To Play Online Instantly</title>
<meta name="description" content="Free unblocked games. No downloads, no sign-ups. Hundreds of games.">
<style>
*{box-sizing:border-box;margin:0;padding:0}body{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif}
a{color:inherit;text-decoration:none}
nav ul li a{background:rgba(255,255,255,.1);padding:4px 10px;border-radius:20px;font-size:.8rem;color:#fff;text-decoration:none;display:inline-block}
nav ul li a:hover{background:rgba(255,255,255,.25)}
main{max-width:1280px;margin:0 auto;padding:24px 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:16px 0 32px}
.gc{display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:9px;overflow:hidden;transition:transform .15s}
.gc:hover{transform:translateY(-3px)}
.gc img{width:100%;height:110px;object-fit:cover}
.gc span{padding:7px 5px;font-size:.8rem;text-align:center}
#so{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9999;overflow-y:auto;padding:70px 20px 20px}
#so.on{display:block}
#sc{position:fixed;top:14px;right:18px;background:#c0392b;color:#fff;border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:1.1rem;z-index:10000}
#si{width:100%;max-width:860px;display:block;margin:0 auto 20px;padding:12px 18px;font-size:1.1rem;border-radius:10px;border:none;background:#161b22;color:#fff;outline:none}
#sg{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;max-width:860px;margin:0 auto}
</style>
</head>
<body>
${navHtml('/')}
<div id="so">
  <button id="sc" onclick="closeSO()">✕</button>
  <input id="si" type="search" placeholder="Search all ${games.length} games…" oninput="doSearch(this.value)" autofocus>
  <div id="sg"></div>
</div>
<main>
  <div style="text-align:center;padding:36px 0 24px">
    <h1 style="font-size:2rem;margin-bottom:8px">🎮 Unblocked Games USA</h1>
    <p style="color:#8b949e;max-width:560px;margin:0 auto 20px">Free games for every break. No downloads, no sign-ups.</p>
    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:24px">
      <span style="background:#21262d;padding:6px 14px;border-radius:20px;font-size:.85rem">✅ No Downloads</span>
      <span style="background:#21262d;padding:6px 14px;border-radius:20px;font-size:.85rem">🎮 100% Free</span>
      <span style="background:#21262d;padding:6px 14px;border-radius:20px;font-size:.85rem">⚡ Play Instantly</span>
      <span style="background:#21262d;padding:6px 14px;border-radius:20px;font-size:.85rem">🏫 School Friendly</span>
    </div>
    <button onclick="openSO()" style="background:#58a6ff;color:#000;border:none;padding:10px 28px;border-radius:24px;font-size:1rem;cursor:pointer;font-weight:700">🔍 Search All ${games.length} Games</button>
  </div>
  <h2 style="font-size:1.2rem;color:#58a6ff;margin-bottom:12px">🔥 Popular Games</h2>
  <div class="grid">
    ${featuredCards}
  </div>
  <h2 style="font-size:1.2rem;color:#58a6ff;margin:28px 0 14px">🎮 Browse by Category</h2>
  <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:40px">
    ${catLinks}
  </div>
</main>
${footerHtml('/')}
<script>
var _games = null;
function loadGames(cb) {
  if (_games) return cb(_games);
  fetch('/search-index.json').then(r=>r.json()).then(d=>{ _games=d; cb(d); }).catch(()=>cb([]));
}
function openSO() {
  document.getElementById('so').classList.add('on');
  document.body.style.overflow='hidden';
  document.getElementById('si').focus();
  loadGames(function(){});
}
function closeSO() {
  document.getElementById('so').classList.remove('on');
  document.body.style.overflow='';
}
document.addEventListener('keydown',function(e){ if(e.key==='Escape') closeSO(); });
document.querySelector('form').addEventListener('submit',function(e){
  e.preventDefault();
  var q=this.q.value.trim();
  if(q){ openSO(); setTimeout(function(){ document.getElementById('si').value=q; doSearch(q); },50); }
});
function doSearch(q) {
  loadGames(function(games) {
    var t=q.toLowerCase().trim();
    var el=document.getElementById('sg');
    if(!t){ el.innerHTML='<p style="color:#8b949e;text-align:center;grid-column:1/-1">Start typing…</p>'; return; }
    var res=games.filter(function(g){
      return g.title.toLowerCase().includes(t)||
        g.slug.replace(/-/g,' ').includes(t)||
        (g.categories||[]).some(function(c){ return c.replace(/-/g,' ').includes(t); });
    }).slice(0,72);
    if(!res.length){ el.innerHTML='<p style="color:#f85149;text-align:center;grid-column:1/-1">No games found for &ldquo;'+q+'&rdquo;</p>'; return; }
    el.innerHTML=res.map(function(g){
      return '<a href="/'+g.slug+'" style="display:flex;flex-direction:column;align-items:center;background:#161b22;border-radius:8px;overflow:hidden;color:#e6edf3;text-decoration:none">'+
        '<img src="'+g.image+'" alt="'+g.title+'" loading="lazy" style="width:100%;height:110px;object-fit:cover">'+
        '<span style="padding:6px;font-size:.78rem;text-align:center">'+g.title+'</span></a>';
    }).join('');
  });
}
</script>
</body>
</html>`);
  console.log('🏠 Homepage built');
}

function patchGamePages(games) {
  console.log('🔗 Adding similar games sections (safe mode)…');
  let done = 0;
  for (const game of games) {
    const fp = path.join(ROOT, game.slug, 'index.html');
    let html = read(fp);
    if (!html) continue;

    // Remove any old injected block
    html = html.replace(/\n?<!-- UG_SIMILAR_START -->[\s\S]*?<!-- UG_SIMILAR_END -->\n?/g, '');

    const similar = games
      .filter(g => g.slug !== game.slug && g.categories.some(c => game.categories.includes(c)))
      .sort((a,b) => simpleHash(game.slug+a.slug) - simpleHash(game.slug+b.slug))
      .slice(0, SIMILAR_COUNT);

    if (!similar.length) { write(fp, html); done++; continue; }

    const cards = similar.map(g =>
      `<a class="ug-card" href="../${g.slug}"><img src="${g.image}" alt="${g.title}" loading="lazy" width="150" height="110"><span>${g.title}</span></a>`
    ).join('\n ');

    const block = `
<!-- UG_SIMILAR_START -->
${SIMILAR_CSS}
<div class="ug-similar">
  <h2>🎮 Similar Games</h2>
  <div class="ug-grid">
    ${cards}
  </div>
</div>
<!-- UG_SIMILAR_END -->`;

    if (html.includes('</main>')) {
      html = html.replace('</main>', '</main>' + block);
    } else if (html.includes('</body>')) {
      html = html.replace('</body>', block + '\n</body>');
    } else {
      html += block;
    }

    write(fp, html);
    done++;
  }
  console.log(` ✓ Processed ${done} game pages`);
}

(function main() {
  console.log('\n🚀 UnblockedGames-USA Build — Safe Version\n');
  const games = scanGames();
  if (!games.length) { console.error('❌ No games found. Run from repo root.'); process.exit(1); }
  writeData(games);
  buildCategoryPages(games);
  buildHomepage(games);
  patchGamePages(games);
  console.log('\n✅ Build complete! Now run:');
  console.log(' git add -A');
  console.log(' git commit -m "build: safe version - never touches game content"');
  console.log(' git push\n');
})();