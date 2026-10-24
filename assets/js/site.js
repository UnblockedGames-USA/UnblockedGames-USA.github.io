/* Unblocked Games USA: shared behaviour (theme, drawer menu, search, random game, game player).
   Mirrors /classroom6x/assets/app.js. The theme key is shared, so the light/dark choice carries across both sites. */
(function () {
  'use strict';
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); };
  var OVERRIDE = { 'word-guess': '/wordle-unlimited/' };

  function slug(id) { return id.replace(/-+/g, '-').replace(/^-|-$/g, ''); }
  function gameUrl(g) { return OVERRIDE[g.id] || '/game/' + slug(g.id) + '/'; }
  function toast(msg) {
    var t = $('.toast');
    if (!t) { t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove('show'); }, 1800);
  }

  /* theme (same storage key as Classroom 6X) */
  var themeBtn = $('#themeBtn');
  if (themeBtn) themeBtn.addEventListener('click', function () {
    var t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = t;
    try { localStorage.setItem('c6x-theme', t); } catch (e) {}
  });

  /* sidebar drawer (phones and tablets) */
  var side = $('#sidebar'), scrim = $('#scrim'), menuBtn = $('#menuBtn');
  function setMenu(open) {
    if (!side) return;
    side.classList.toggle('open', open);
    if (scrim) scrim.hidden = !open;
    if (menuBtn) menuBtn.setAttribute('aria-expanded', String(open));
  }
  if (menuBtn) menuBtn.addEventListener('click', function () { setMenu(!side.classList.contains('open')); });
  if (scrim) scrim.addEventListener('click', function () { setMenu(false); });

  /* game index (loaded on demand) */
  var dataP = null;
  function loadData() {
    if (!dataP) dataP = fetch('/data/games.json').then(function (r) { return r.json(); });
    return dataP;
  }
  function norm(s) { return s.toLowerCase().normalize('NFKD').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim(); }
  function search(data, q) {
    q = norm(q); if (!q) return [];
    var words = q.split(' '), out = [];
    for (var i = 0; i < data.length; i++) {
      var g = data[i];
      var t = g._n || (g._n = norm(g.title + ' ' + (g.categories || []).join(' ')));
      var name = g._t || (g._t = norm(g.title));
      var ok = true;
      for (var w = 0; w < words.length; w++) if (t.indexOf(words[w]) === -1) { ok = false; break; }
      if (!ok) continue;
      var score = name === q ? 0 : name.indexOf(q) === 0 ? 1 : (' ' + name).indexOf(' ' + q) > -1 ? 2 : 3;
      out.push([score, name.length, g]);
    }
    out.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
    return out.map(function (x) { return x[2]; });
  }
  function tileHTML(g) {
    return '<a class="tile" href="' + gameUrl(g) + '" title="' + esc(g.title) + '"><span class="tile-img"><img src="/' + esc(g.image) +
      '" alt="' + esc(g.title) + ' – play free online" width="480" height="270" loading="lazy" decoding="async"></span><span class="tile-name">' + esc(g.title) + '</span></a>';
  }

  /* header search with live suggestions */
  var q = $('#q'), pop = $('#searchPop'), sel = -1;
  if (q && pop) {
    q.addEventListener('focus', loadData, { once: true });
    q.addEventListener('input', function () {
      var v = q.value.trim();
      if (!v) { pop.hidden = true; return; }
      loadData().then(function (data) {
        var res = search(data, v), top = res.slice(0, 8);
        sel = -1;
        pop.innerHTML = top.length
          ? top.map(function (g) { return '<a role="option" href="' + gameUrl(g) + '"><img src="/' + esc(g.image) + '" alt="" loading="lazy">' + esc(g.title) + '</a>'; }).join('') +
            (res.length > 8 ? '<a class="all" href="/?q=' + encodeURIComponent(v) + '">See all ' + res.length + ' results</a>' : '')
          : '<div class="none">No games found for “' + esc(v) + '”</div>';
        pop.hidden = false;
      });
    });
    q.addEventListener('keydown', function (e) {
      var items = pop.querySelectorAll('a');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!items.length) return;
        e.preventDefault();
        sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items.forEach(function (a, i) { a.setAttribute('aria-selected', i === sel ? 'true' : 'false'); });
      } else if (e.key === 'Enter' && sel > -1 && items[sel]) {
        e.preventDefault(); location.href = items[sel].href;
      } else if (e.key === 'Escape') { pop.hidden = true; q.blur(); }
    });
    document.addEventListener('click', function (e) { if (!e.target.closest('.search')) pop.hidden = true; });
  }

  /* search results on the homepage (?q=...) */
  var results = $('#searchResults');
  var term = new URLSearchParams(location.search).get('q');
  if (results && term) {
    if (q) q.value = term;
    loadData().then(function (data) {
      var res = search(data, term);
      $('#searchTitle').textContent = 'Results for “' + term + '” (' + res.length + ')';
      $('#searchGrid').innerHTML = res.slice(0, 240).map(tileHTML).join('');
      $('#searchEmpty').hidden = res.length > 0;
      results.hidden = false;
      var shelves = $('#shelves'); if (shelves) shelves.hidden = true;
      var hero = $('#hero'); if (hero) hero.hidden = true;
    });
  }

  /* random game, picked in the browser so there is no extra page hop */
  var rb = $('#randomBtn');
  if (rb) rb.addEventListener('click', function (e) {
    e.preventDefault();
    loadData().then(function (d) { location.href = gameUrl(d[Math.floor(Math.random() * d.length)]); })
      .catch(function () { location.href = rb.href; });
  });

  /* game player */
  var player = $('#player');
  if (player) {
    var title = player.dataset.title, src = player.dataset.src, iframe = null;
    var fsBtn = $('#fsBtn'), shareBtn = $('#shareBtn'), reloadBtn = $('#reloadBtn');

    function start() {
      if (iframe) { iframe.src = src; return; }
      var poster = $('#poster');
      var load = document.createElement('div');
      load.className = 'loading'; load.innerHTML = '<div><div class="spinner"></div>Loading ' + esc(title) + '…</div>';
      iframe = document.createElement('iframe');
      iframe.src = src;
      iframe.title = title + ' game';
      iframe.allow = 'autoplay; fullscreen; gamepad; clipboard-write';
      iframe.setAttribute('allowfullscreen', '');
      iframe.addEventListener('load', function () { load.style.opacity = '0'; setTimeout(function () { load.remove(); }, 400); });
      player.appendChild(iframe); player.appendChild(load);
      if (poster) poster.remove();
      iframe.focus();
    }
    var playBtn = $('#playBtn');
    if (playBtn) playBtn.addEventListener('click', start);
    if (reloadBtn) reloadBtn.addEventListener('click', start);

    function setExpanded(on) {
      player.classList.toggle('is-expanded', on);
      document.body.classList.toggle('player-expanded', on);
      if (fsBtn) fsBtn.setAttribute('aria-expanded', String(on));
    }
    if (fsBtn) fsBtn.addEventListener('click', function () {
      start();
      var req = player.requestFullscreen || player.webkitRequestFullscreen;
      if (req) { try { req.call(player); return; } catch (e) {} }
      setExpanded(!player.classList.contains('is-expanded')); /* phones without element fullscreen */
    });
    if (shareBtn) shareBtn.addEventListener('click', function () {
      var url = location.href;
      if (navigator.share) { navigator.share({ title: title + ' on Unblocked Games USA', url: url }).catch(function () {}); return; }
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { toast('Link copied'); }, function () { toast(url); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && player.classList.contains('is-expanded')) setExpanded(false);
    });
  }

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
})();
