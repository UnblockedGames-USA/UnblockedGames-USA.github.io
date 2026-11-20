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

  /* Native PWA installation. The banner only appears when this browser can
     open its real installation prompt; no fake/manual install instructions. */
  function setupPWAInstall() {
    if (!document.head) return;

    if (!document.querySelector('link[rel="manifest"]')) {
      var manifestLink = document.createElement('link');
      manifestLink.rel = 'manifest';
      manifestLink.href = '/manifest.webmanifest';
      document.head.appendChild(manifestLink);
    }
    if (!document.querySelector('link[rel="apple-touch-icon"]')) {
      var appleIcon = document.createElement('link');
      appleIcon.rel = 'apple-touch-icon';
      appleIcon.href = '/assets/pwa-icon-192.png';
      document.head.appendChild(appleIcon);
    }
    if (!document.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
      var appleCapable = document.createElement('meta');
      appleCapable.name = 'apple-mobile-web-app-capable';
      appleCapable.content = 'yes';
      document.head.appendChild(appleCapable);
    }
    if (!document.querySelector('meta[name="apple-mobile-web-app-title"]')) {
      var appleTitle = document.createElement('meta');
      appleTitle.name = 'apple-mobile-web-app-title';
      appleTitle.content = 'Unblocked Games';
      document.head.appendChild(appleTitle);
    }

    if ('serviceWorker' in navigator && location.protocol === 'https:') {
      window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {
          /* Browsers without service-worker support can still use the site normally. */
        });
      }, { once: true });
    }

    var standalone = window.matchMedia && window.matchMedia('(display-mode: standalone)').matches;
    if (standalone || navigator.standalone === true) return;

    var dismissedUntil = 0;
    var installedBefore = false;
    try {
      dismissedUntil = Number(localStorage.getItem('ugusa-pwa-dismissed-until') || 0);
      installedBefore = localStorage.getItem('ugusa-pwa-installed') === '1';
    } catch (e) {}
    if (installedBefore || dismissedUntil > Date.now()) return;

    var deferredInstall = null;
    var prompt = document.createElement('aside');
    prompt.className = 'pwa-install-prompt';
    prompt.hidden = true;
    prompt.setAttribute('aria-label', 'Install Unblocked Games');
    prompt.innerHTML =
      '<div class="pwa-install-heading">' +
        '<img class="pwa-install-icon" src="/assets/pwa-icon-192.png" width="48" height="48" alt="" />' +
        '<div class="pwa-install-copy"><span class="pwa-install-eyebrow">UNBLOCKED GAMES · QUICK ACCESS</span>' +
        '<h2>Play at home or at school</h2></div>' +
        '<button class="pwa-install-close" type="button" aria-label="Dismiss install notification">&times;</button>' +
      '</div>' +
      '<p class="pwa-install-description">Add Unblocked Games to your device and open your favorite games with one tap.</p>' +
      '<div class="pwa-install-actions"><button class="pwa-install-action" type="button">Install app</button>' +
      '<button class="pwa-install-later" type="button">Not now</button></div>';
    document.body.appendChild(prompt);

    var installButton = prompt.querySelector('.pwa-install-action');
    var closeButton = prompt.querySelector('.pwa-install-close');
    var laterButton = prompt.querySelector('.pwa-install-later');

    function showPrompt() {
      if (!document.body.contains(prompt) || !deferredInstall) return;
      prompt.hidden = false;
      window.requestAnimationFrame(function () { prompt.classList.add('is-visible'); });
    }

    function closePrompt(installed) {
      try {
        if (installed) localStorage.setItem('ugusa-pwa-installed', '1');
        else localStorage.setItem('ugusa-pwa-dismissed-until', String(Date.now() + 14 * 24 * 60 * 60 * 1000));
      } catch (e) {}
      prompt.classList.remove('is-visible');
      window.setTimeout(function () { prompt.remove(); }, 180);
    }

    window.addEventListener('beforeinstallprompt', function (event) {
      if (!document.body.contains(prompt) || dismissedUntil > Date.now()) return;
      event.preventDefault();
      deferredInstall = event;
      showPrompt();
    });

    window.addEventListener('appinstalled', function () {
      closePrompt(true);
    });

    installButton.addEventListener('click', function () {
      if (!deferredInstall) return;
      var installEvent = deferredInstall;
      deferredInstall = null;
      installButton.disabled = true;
      installButton.textContent = 'Opening…';

      installEvent.prompt();
      Promise.resolve(installEvent.userChoice).then(function (choice) {
        if (choice && choice.outcome === 'accepted') {
          closePrompt(true);
        } else {
          closePrompt(false);
        }
      }).catch(function () {
        closePrompt(false);
      });
    });

    closeButton.addEventListener('click', function () { closePrompt(false); });
    laterButton.addEventListener('click', function () { closePrompt(false); });
  }

  setupPWAInstall();

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
