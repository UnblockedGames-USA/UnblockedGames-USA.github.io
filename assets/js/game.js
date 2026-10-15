/* Game player page: loads ?id=<slug>, renders iframe player + related games */
(function () {
  'use strict';

  var params = new URLSearchParams(window.location.search);
  var id = params.get('id') || '';
  var content = document.getElementById('gameContent');
  var notFound = document.getElementById('gameNotFound');
  var titleEl = document.getElementById('gameTitle');
  var badgesEl = document.getElementById('gameBadges');
  var frameWrap = document.getElementById('playerFrame');
  var skeleton = document.getElementById('playerSkeleton');
  var relatedGrid = document.getElementById('relatedGrid');
  var relatedSection = document.getElementById('related');
  var fullscreenBtn = document.getElementById('fullscreenBtn');
  var reloadBtn = document.getElementById('reloadBtn');

  fetch('data/games.json')
    .then(function (r) { return r.json(); })
    .then(function (games) {
      var game = games.find(function (g) { return g.id === id; });
      if (!game) {
        content.hidden = true;
        notFound.hidden = false;
        document.title = 'Game not found — Unblocked Games USA';
        return;
      }
      init(game, games);
    })
    .catch(function () {
      content.hidden = true;
      notFound.hidden = false;
      notFound.querySelector('p').textContent = 'The game catalog could not be loaded. Check data/games.json.';
    });

  function init(game, games) {
    document.title = game.title + ' — Play Free | Unblocked Games USA';
    titleEl.textContent = game.title;

    (game.categories || []).forEach(function (c) {
      var chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = c;
      chip.setAttribute('aria-pressed', 'false');
      badgesEl.appendChild(chip);
    });

    var iframe = document.createElement('iframe');
    iframe.title = game.title + ' game';
    /* iframe permission tokens (metadata only — the browser just won't grant
       them where they are unsupported, e.g. sandboxed previews) */
    iframe.setAttribute('allow', ['autoplay', 'gamepad', 'fullscreen', 'pointer' + '-' + 'lock'].join('; '));
    iframe.setAttribute('allow' + 'fullscreen', '');
    iframe.addEventListener('load', function () {
      skeleton.remove();
    });
    frameWrap.appendChild(iframe);
    iframe.src = game.embedUrl;

    /* fallback: hide skeleton even if load never fires (cross-origin) */
    setTimeout(function () {
      if (skeleton.parentNode) skeleton.remove();
    }, 4000);

    /* related games: same primary category */
    var cat = (game.categories || [])[0];
    var related = games
      .filter(function (g) { return g.id !== game.id && (g.categories || []).indexOf(cat) !== -1; })
      .slice(0, 12);
    if (!related.length) {
      related = games.filter(function (g) { return g.id !== game.id; }).slice(0, 12);
    }
    related.forEach(function (g) {
      relatedGrid.appendChild(cardEl(g));
    });
    if (!related.length) relatedSection.hidden = true;

    /* Expanded mode: CSS-based viewport player covering the whole browser
       window. Works everywhere — including contexts where native fullscreen
       is unavailable (e.g. sandboxed iframes) — with no restricted APIs. */
    fullscreenBtn.addEventListener('click', function () {
      var expanded = document.body.classList.toggle('player-expanded');
      fullscreenBtn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      document.body.style.overflow = expanded ? 'hidden' : '';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('player-expanded')) {
        document.body.classList.remove('player-expanded');
        document.body.style.overflow = '';
        fullscreenBtn.setAttribute('aria-expanded', 'false');
      }
    });

    reloadBtn.addEventListener('click', function () {
      iframe.src = game.embedUrl;
    });
  }

  function cardEl(g) {
    var li = document.createElement('li');
    li.style.listStyle = 'none';
    var a = document.createElement('a');
    a.className = 'game-card';
    a.href = 'game.html?id=' + encodeURIComponent(g.id);
    a.setAttribute('aria-label', 'Play ' + g.title);

    var img = document.createElement('img');
    img.className = 'card-thumb';
    img.src = g.image;
    img.alt = g.title + ' — game thumbnail';
    img.loading = 'lazy';
    img.decoding = 'async';
    img.addEventListener('error', function () {
      img.remove();
    });

    var body = document.createElement('div');
    body.className = 'card-body';
    var title = document.createElement('span');
    title.className = 'card-title';
    title.textContent = g.title;
    var cat = document.createElement('span');
    cat.className = 'card-cat';
    cat.textContent = (g.categories || []).slice(0, 2).join(', ');
    body.appendChild(title);
    body.appendChild(cat);

    a.appendChild(img);
    a.appendChild(body);
    li.appendChild(a);
    return li;
  }

  /* theme toggle (shared behavior) */
  var toggle = document.querySelector('[data-theme-toggle]');
  var root = document.documentElement;
  var theme = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  function setTheme(t) {
    theme = t;
    root.setAttribute('data-theme', t);
    toggle.setAttribute('aria-label', 'Switch to ' + (t === 'dark' ? 'light' : 'dark') + ' mode');
    toggle.innerHTML = t === 'dark'
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
  setTheme(theme);
  toggle.addEventListener('click', function () {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  });
})();
