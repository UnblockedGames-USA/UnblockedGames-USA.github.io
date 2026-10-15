/* Shared behaviour for static pages: menu, theme toggle, click-to-play, expand, restart */
(function () {
  'use strict';
  var root = document.documentElement;

  /* menu */
  var btn = document.getElementById('menuBtn'), closeBtn = document.getElementById('menuClose');
  var panel = document.getElementById('menuPanel'), backdrop = document.getElementById('menuBackdrop');
  function openMenu(o) { panel.hidden = !o; backdrop.hidden = !o; btn.setAttribute('aria-expanded', o ? 'true' : 'false'); document.body.style.overflow = o ? 'hidden' : ''; }
  if (btn && panel) {
    btn.addEventListener('click', function () { openMenu(true); });
    closeBtn.addEventListener('click', function () { openMenu(false); });
    backdrop.addEventListener('click', function () { openMenu(false); });
  }

  /* theme */
  var toggle = document.querySelector('[data-theme-toggle]');
  var theme = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  var SUN = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
  var MOON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  function setTheme(t) {
    theme = t; root.setAttribute('data-theme', t);
    if (toggle) { toggle.setAttribute('aria-label', 'Switch to ' + (t === 'dark' ? 'light' : 'dark') + ' mode'); toggle.innerHTML = t === 'dark' ? SUN : MOON; }
  }
  setTheme(theme);
  if (toggle) toggle.addEventListener('click', function () { setTheme(theme === 'dark' ? 'light' : 'dark'); });

  /* search: live suggestions on every page, results on the homepage */
  var form = document.querySelector('.header-search'), input = form && form.querySelector('input');
  var catalog = null;
  function load(cb) {
    if (catalog) return cb(catalog);
    fetch('/data/games.json').then(function (r) { return r.json(); }).then(function (d) { catalog = d; cb(d); });
  }
  function slug(id) { return id.replace(/-+/g, '-').replace(/^-|-$/g, ''); }
  function find(d, q) {
    q = q.trim().toLowerCase(); if (!q) return [];
    return d.filter(function (g) { return g.title.toLowerCase().indexOf(q) !== -1 || (g.categories || []).join(' ').indexOf(q) !== -1; });
  }
  if (input) {
    var box = document.createElement('div'); box.className = 'search-suggest'; box.setAttribute('role', 'listbox'); box.hidden = true; form.appendChild(box);
    input.addEventListener('input', function () {
      var v = input.value; if (v.trim().length < 2) { box.hidden = true; return; }
      load(function (d) {
        var hits = find(d, v).slice(0, 6); box.innerHTML = '';
        hits.forEach(function (g) {
          var a = document.createElement('a'); a.className = 'suggest-item'; a.href = '/game/' + slug(g.id) + '/';
          var im = document.createElement('img'); im.src = '/' + g.image; im.alt = ''; im.loading = 'lazy';
          var sp = document.createElement('span'); sp.textContent = g.title; a.appendChild(im); a.appendChild(sp); box.appendChild(a);
        });
        box.hidden = !hits.length;
      });
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) box.hidden = true; });
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') box.hidden = true; });
  }
  var results = document.getElementById('searchResults');
  var qParam = new URLSearchParams(location.search).get('q');
  if (results && qParam) {
    if (input) input.value = qParam;
    load(function (d) {
      var hits = find(d, qParam), grid = document.getElementById('searchGrid');
      document.getElementById('searchTitle').textContent = 'Results for "' + qParam + '" (' + hits.length + ')';
      hits.slice(0, 120).forEach(function (g) {
        var li = document.createElement('li'), a = document.createElement('a'); a.className = 'tile'; a.href = '/game/' + slug(g.id) + '/';
        var im = document.createElement('img'); im.src = '/' + g.image; im.alt = g.title + ' – play free online'; im.loading = 'lazy'; im.width = 480; im.height = 270;
        var t = document.createElement('span'); t.className = 'tile-title'; t.textContent = g.title; a.appendChild(im); a.appendChild(t); li.appendChild(a); grid.appendChild(li);
      });
      document.getElementById('searchEmpty').hidden = hits.length > 0;
      results.hidden = false; document.getElementById('shelves').hidden = true;
    });
  }

  /* player */
  var frame = document.getElementById('playerFrame');
  if (!frame) { document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel && !panel.hidden) openMenu(false); }); return; }
  var playBtn = document.getElementById('playBtn'), fsBtn = document.getElementById('fullscreenBtn'), reloadBtn = document.getElementById('reloadBtn');
  var embed = frame.getAttribute('data-embed'), title = frame.getAttribute('data-title') || 'Game', iframe = null;

  function start() {
    if (iframe) { iframe.src = embed; return; }
    iframe = document.createElement('iframe');
    iframe.title = title + ' game';
    iframe.setAttribute('allow', ['autoplay', 'gamepad', 'fullscreen'].join('; '));
    iframe.setAttribute('allowfullscreen', '');
    iframe.src = embed;
    frame.appendChild(iframe);
    if (playBtn) playBtn.remove();
    iframe.focus();
  }
  if (playBtn) playBtn.addEventListener('click', start);
  reloadBtn.addEventListener('click', start);

  function setExpanded(on) {
    document.body.classList.toggle('player-expanded', on);
    fsBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
    document.body.style.overflow = on ? 'hidden' : '';
    if (on && !iframe) start();
  }
  fsBtn.addEventListener('click', function () { setExpanded(!document.body.classList.contains('player-expanded')); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (document.body.classList.contains('player-expanded')) setExpanded(false);
    else if (panel && !panel.hidden) openMenu(false);
  });
})();
