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
