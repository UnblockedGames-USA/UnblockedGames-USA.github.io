/* Homepage: catalog grid, search, category filters, lazy rendering */
(function () {
  'use strict';

  var PAGE_SIZE = 30;
  var games = [];
  var filtered = [];
  var rendered = 0;
  var activeCategory = 'all';
  var query = '';

  var grid = document.getElementById('gameGrid');
  var sentinel = document.getElementById('gridSentinel');
  var chipsWrap = document.getElementById('categoryChips');
  var searchInput = document.getElementById('searchInput');
  var resultCount = document.getElementById('resultCount');
  var emptyState = document.getElementById('emptyState');
  var clearBtn = document.getElementById('clearFilters');
  var gridTitle = document.getElementById('gridTitle');
  var heroCards = document.getElementById('heroCards');

  fetch('data/games.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      initMenu();

      /* support ?q= search links (used by the JSON-LD SearchAction) */
      var urlQ = new URLSearchParams(window.location.search).get('q');
      if (urlQ) {
        searchInput.value = urlQ;
        query = urlQ;
        searchInput.focus();
      }
      games = data;
      /* keep visible counts in sync with the catalog */
      var n = games.length;
      var heroCount = document.getElementById('heroCount');
      var statGames = document.getElementById('statGames');
      var statCats = document.getElementById('statCats');
      if (heroCount) heroCount.textContent = n;
      if (statGames) statGames.textContent = n;
      if (statCats) {
        var cats = {};
        games.forEach(function (g) { (g.categories || []).forEach(function (c) { cats[c] = 1; }); });
        statCats.textContent = Object.keys(cats).length;
      }
      searchInput.placeholder = 'Search ' + n + ' games…';
      buildChips();
      buildHero();
      applyFilters();
    })
    .catch(function () {
      emptyState.hidden = false;
      emptyState.querySelector('h3').textContent = 'Could not load the game catalog';
      emptyState.querySelector('p').textContent = 'Check that data/games.json exists next to index.html.';
    });

  /* ---- chips ---- */
  function buildChips() {
    var counts = {};
    games.forEach(function (g) {
      (g.categories || []).forEach(function (c) { counts[c] = (counts[c] || 0) + 1; });
    });
    var cats = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; });
    var frag = document.createDocumentFragment();

    var all = makeChip('all', 'All games (' + games.length + ')');
    frag.appendChild(all);

    cats.forEach(function (c) {
      frag.appendChild(makeChip(c, c + ' (' + counts[c] + ')'));
    });
    chipsWrap.appendChild(frag);
  }

  function makeChip(cat, label) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chip';
    btn.textContent = label;
    btn.setAttribute('aria-pressed', cat === activeCategory ? 'true' : 'false');
    btn.addEventListener('click', function () {
      activeCategory = cat;
      chipsWrap.querySelectorAll('.chip').forEach(function (el) {
        el.setAttribute('aria-pressed', 'false');
      });
      btn.setAttribute('aria-pressed', 'true');
      applyFilters();
      document.getElementById('games').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    return btn;
  }

  /* ---- hero: 4 popular picks ---- */
  function buildHero() {
    var picks = ['basketball-superstars', 'crazy-drift', 'snake-clash-io', 'tape-escape'];
    var chosen = picks
      .map(function (id) { return games.find(function (g) { return g.id === id; }); })
      .filter(Boolean);
    if (chosen.length < 4) {
      chosen = games.slice(0, 4);
    }
    chosen.forEach(function (g) { heroCards.appendChild(cardEl(g, true)); });
  }

  /* ---- filtering ---- */
  function applyFilters() {
    var q = query.trim().toLowerCase();
    filtered = games.filter(function (g) {
      var okCat = activeCategory === 'all' || (g.categories || []).indexOf(activeCategory) !== -1;
      var okQ = !q || (g.title || '').toLowerCase().indexOf(q) !== -1 || g.id.indexOf(q) !== -1;
      return okCat && okQ;
    });
    rendered = 0;
    grid.innerHTML = '';
    gridTitle.textContent = activeCategory === 'all' ? 'All games' : activeCategory;
    resultCount.textContent = filtered.length + ' games';
    emptyState.hidden = filtered.length !== 0;
    renderMore();
  }

  function renderMore() {
    var end = Math.min(rendered + PAGE_SIZE, filtered.length);
    var frag = document.createDocumentFragment();
    for (var i = rendered; i < end; i++) {
      frag.appendChild(cardEl(filtered[i], false));
    }
    grid.appendChild(frag);
    rendered = end;
  }

  /* ---- card element ---- */
  function cardEl(g, featured) {
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
      img.replaceWith(fallbackThumb(g));
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
    if (featured) {
      var badge = document.createElement('span');
      badge.className = 'card-badge';
      badge.textContent = 'Popular';
      body.appendChild(badge);
    }
    a.appendChild(img);
    a.appendChild(body);
    li.appendChild(a);
    return li;
  }

  function fallbackThumb(g) {
    var d = document.createElement('div');
    d.className = 'card-thumb';
    d.setAttribute('role', 'img');
    d.setAttribute('aria-label', g.title);
    d.style.display = 'flex';
    d.style.alignItems = 'center';
    d.style.justifyContent = 'center';
    d.style.fontFamily = 'var(--font-display)';
    d.style.fontSize = 'var(--text-xl)';
    d.style.color = 'var(--color-text-faint)';
    var initials = (g.title || g.id).split(/\s+/).slice(0, 2)
      .map(function (w) { return w.charAt(0); }).join('');
    d.textContent = initials.toUpperCase();
    return d;
  }

  /* ---- infinite scroll ---- */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting && rendered < filtered.length) {
        renderMore();
        /* re-observe so the callback fires again if the sentinel is still in view */
        io.unobserve(sentinel);
        io.observe(sentinel);
      }
    }, { rootMargin: '600px 0px' });
    io.observe(sentinel);
  } else {
    window.addEventListener('scroll', function () {
      if (rendered < filtered.length &&
          window.innerHeight + window.scrollY > sentinel.offsetTop - 600) {
        renderMore();
      }
    });
  }

  /* ---- search ---- */
  var debounce;

  clearBtn.addEventListener('click', function () {
    searchInput.value = '';
    query = '';
    activeCategory = 'all';
    chipsWrap.querySelectorAll('.chip').forEach(function (el) {
      el.setAttribute('aria-pressed', el === chipsWrap.firstChild ? 'true' : 'false');
    });
    applyFilters();
  });

  /* ---- burger menu ---- */
  function initMenu() {
    var menuBtn = document.getElementById('menuBtn');
    var menuClose = document.getElementById('menuClose');
    var menuPanel = document.getElementById('menuPanel');
    var menuBackdrop = document.getElementById('menuBackdrop');
    if (!menuBtn || !menuPanel) return;

    function openMenu(open) {
      menuPanel.hidden = !open;
      menuBackdrop.hidden = !open;
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    }

    menuBtn.addEventListener('click', function () { openMenu(true); });
    menuClose.addEventListener('click', function () { openMenu(false); });
    menuBackdrop.addEventListener('click', function () { openMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menuPanel.hidden) openMenu(false);
    });

    /* category shortcuts inside the menu activate the matching chip */
    menuPanel.querySelectorAll('[data-menu-category]').forEach(function (link) {
      link.addEventListener('click', function () {
        openMenu(false);
        var cat = link.getAttribute('data-menu-category');
        var chip = Array.prototype.find.call(
          chipsWrap.querySelectorAll('.chip'),
          function (c) { return c.textContent.toLowerCase().indexOf(cat) === 0; }
        );
        if (chip) chip.click();
      });
    });
  }

  /* ---- live search suggestions ---- */
  var suggestWrap = document.createElement('div');
  suggestWrap.className = 'search-suggest';
  suggestWrap.setAttribute('role', 'listbox');
  suggestWrap.hidden = true;
  var headerSearch = document.querySelector('.header-search');
  headerSearch.appendChild(suggestWrap);
  var suggestIndex = -1;

  function renderSuggestions(items) {
    suggestWrap.innerHTML = '';
    if (!items.length) { suggestWrap.hidden = true; return; }
    suggestIndex = -1;
    items.forEach(function (g, i) {
      var a = document.createElement('a');
      a.className = 'suggest-item';
      a.href = 'game.html?id=' + encodeURIComponent(g.id);
      a.setAttribute('role', 'option');
      var img = document.createElement('img');
      img.src = g.image;
      img.alt = '';
      img.loading = 'lazy';
      var span = document.createElement('span');
      span.textContent = g.title;
      a.appendChild(img);
      a.appendChild(span);
      suggestWrap.appendChild(a);
    });
    suggestWrap.hidden = false;
  }

  function updateSuggestions() {
    var q = searchInput.value.trim().toLowerCase();
    if (!q || !games.length) { suggestWrap.hidden = true; return; }
    var hits = games.filter(function (g) {
      return (g.title || '').toLowerCase().indexOf(q) !== -1 || g.id.indexOf(q) !== -1;
    }).slice(0, 6);
    renderSuggestions(hits);
  }

  function moveSuggest(dir) {
    var items = suggestWrap.querySelectorAll('.suggest-item');
    if (!items.length) return;
    suggestIndex = (suggestIndex + dir + items.length) % items.length;
    items.forEach(function (el, i) {
      el.classList.toggle('active', i === suggestIndex);
      if (i === suggestIndex) el.setAttribute('aria-selected', 'true');
      else el.removeAttribute('aria-selected');
    });
  }

  searchInput.addEventListener('input', function () {
    clearTimeout(debounce);
    debounce = setTimeout(function () {
      query = searchInput.value;
      applyFilters();
      updateSuggestions();
    }, 120);
  });

  searchInput.addEventListener('keydown', function (e) {
    if (!suggestWrap.hidden) {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveSuggest(1); return; }
      if (e.key === 'ArrowUp') { e.preventDefault(); moveSuggest(-1); return; }
      if (e.key === 'Enter' && suggestIndex >= 0) {
        e.preventDefault();
        suggestWrap.querySelectorAll('.suggest-item')[suggestIndex].click();
        return;
      }
    }
    if (e.key === 'Escape') {
      suggestWrap.hidden = true;
      searchInput.blur();
    }
  });

  document.addEventListener('click', function (e) {
    if (!headerSearch.contains(e.target)) suggestWrap.hidden = true;
  });

  /* '/' focuses search from anywhere on the page */
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    }
  });

  /* ---- theme toggle ---- */
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
