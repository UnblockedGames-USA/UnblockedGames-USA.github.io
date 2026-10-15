/* Word Guess — daily five-letter word game.
   Vanilla JS, no build step. Progress is stored in this browser only (no accounts).
   */
(() => {
'use strict';

const CFG = window.CONFIG;
const L = CFG.WORD_LENGTH, MAXG = CFG.MAX_GUESSES;
const ANSWERS = window.ANSWERS;
const VALID = new Set([...ANSWERS, ...window.EXTRA]);
const $ = (s, el = document) => el.querySelector(s);
const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const reduceMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ------------------------------------------------------------------ storage (safe) */
const mem = {};
const store = {
  get(k) { try { const v = localStorage.getItem(k); return v == null ? null : JSON.parse(v); } catch { return k in mem ? JSON.parse(mem[k]) : null; } },
  set(k, v) { const s = JSON.stringify(v); try { localStorage.setItem(k, s); } catch { mem[k] = s; } },
  del(k) { try { localStorage.removeItem(k); } catch { delete mem[k]; } }
};

/* ------------------------------------------------------------------ dates / words */
function todayIndex() {
  const n = new Date();
  const utc = Date.UTC(n.getFullYear(), n.getMonth(), n.getDate());
  const e = Date.UTC(...CFG.EPOCH);
  return Math.floor((utc - e) / 86400000);
}
const wordForDay = d => ANSWERS[((d % ANSWERS.length) + ANSWERS.length) % ANSWERS.length];
const randomWord = () => ANSWERS[Math.floor(Math.random() * ANSWERS.length)];

function evaluate(guess, answer) {
  const res = Array(L).fill('absent');
  const left = {};
  for (let i = 0; i < L; i++) {
    if (guess[i] === answer[i]) res[i] = 'correct';
    else left[answer[i]] = (left[answer[i]] || 0) + 1;
  }
  for (let i = 0; i < L; i++) {
    if (res[i] === 'correct') continue;
    if (left[guess[i]] > 0) { res[i] = 'present'; left[guess[i]]--; }
  }
  return res;
}

/* ------------------------------------------------------------------ progress model */
const blankStats = () => ({ played: 0, wins: 0, streak: 0, maxStreak: 0, dist: [0, 0, 0, 0, 0, 0], lastWinDay: null, lastDay: null });
const blankProgress = () => ({ stats: blankStats(), daily: { day: null, guesses: [], status: 'playing' } });

function sanitizeProgress(p) {
  const out = blankProgress();
  if (!p || typeof p !== 'object') return out;
  const s = p.stats || {};
  const n = v => (Number.isFinite(v) && v >= 0 && v < 1e6 ? Math.floor(v) : 0);
  out.stats = {
    played: n(s.played), wins: n(s.wins), streak: n(s.streak), maxStreak: n(s.maxStreak),
    dist: Array.isArray(s.dist) && s.dist.length === 6 ? s.dist.map(n) : [0, 0, 0, 0, 0, 0],
    lastWinDay: Number.isFinite(s.lastWinDay) ? s.lastWinDay : null,
    lastDay: Number.isFinite(s.lastDay) ? s.lastDay : null
  };
  const d = p.daily || {};
  if (Number.isFinite(d.day)) {
    out.daily = {
      day: d.day,
      guesses: Array.isArray(d.guesses) ? d.guesses.filter(g => typeof g === 'string' && /^[a-z]{5}$/.test(g)).slice(0, MAXG) : [],
      status: ['playing', 'won', 'lost'].includes(d.status) ? d.status : 'playing'
    };
  }
  return out;
}
function mergeProgress(a, b) {
  // Never lose history: keep the richer stats and the more advanced daily game.
  const stats = (b.stats.played > a.stats.played || (b.stats.played === a.stats.played && b.stats.maxStreak > a.stats.maxStreak)) ? b.stats : a.stats;
  let daily = a.daily;
  if (b.daily.day != null && (a.daily.day == null || b.daily.day > a.daily.day ||
      (b.daily.day === a.daily.day && (b.daily.status !== 'playing' && a.daily.status === 'playing' || b.daily.guesses.length > a.daily.guesses.length)))) daily = b.daily;
  return { stats, daily };
}

/* ------------------------------------------------------------------ settings */
let settings = Object.assign(
  { hard: false, dark: matchMedia('(prefers-color-scheme: dark)').matches, contrast: false },
  store.get('wg:settings') || {}
);
function applySettings() {
  document.documentElement.dataset.theme = settings.dark ? 'dark' : 'light';
  document.documentElement.dataset.contrast = settings.contrast ? 'on' : 'off';
  const m = document.querySelector('meta[name=theme-color]');
  if (m) m.content = settings.dark ? '#15171c' : '#f5f0e6';
  store.set('wg:settings', settings);
}

/* ------------------------------------------------------------------ app state */
let progress = blankProgress();
let mode = 'daily';
let game = null;       // { mode, answer, guesses, status, current }
let busy = false;      // true while flip animation plays
let day = todayIndex();

const saveProgress = () => store.set('wg:progress', progress);

function newDailyGame() {
  const answer = wordForDay(day);
  if (progress.daily.day !== day) progress.daily = { day, guesses: [], status: 'playing' };
  return { mode: 'daily', answer, guesses: progress.daily.guesses, status: progress.daily.status, current: '' };
}
function newPracticeGame() { return { mode: 'practice', answer: randomWord(), guesses: [], status: 'playing', current: '' }; }

/* ------------------------------------------------------------------ rendering */
const boardEl = $('#board'), kbEl = $('#keyboard'), afterEl = $('#after');
const KEYS = ['qwertyuiop', 'asdfghjkl', '+zxcvbnm-'];

function buildBoard() {
  boardEl.innerHTML = '';
  for (let r = 0; r < MAXG; r++) {
    const row = el('div', 'row'); row.setAttribute('role', 'row');
    for (let c = 0; c < L; c++) {
      const t = el('div', 'tile'); t.setAttribute('role', 'gridcell'); t.dataset.state = 'empty'; row.appendChild(t);
    }
    boardEl.appendChild(row);
  }
}
function buildKeyboard() {
  kbEl.innerHTML = '';
  KEYS.forEach((row, ri) => {
    const r = el('div', 'krow');
    if (ri === 1) r.appendChild(el('div', 'spacer'));
    for (const ch of row) {
      let b;
      if (ch === '+') { b = el('button', 'key wide', 'Enter'); b.dataset.key = 'enter'; }
      else if (ch === '-') {
        b = el('button', 'key wide'); b.dataset.key = 'back'; b.setAttribute('aria-label', 'Backspace');
        b.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M21 5H9l-6 7 6 7h12a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1z"/><path d="M17 9.5l-5 5M12 9.5l5 5"/></svg>';
      } else { b = el('button', 'key', ch); b.dataset.key = ch; }
      b.type = 'button';
      r.appendChild(b);
    }
    if (ri === 1) r.appendChild(el('div', 'spacer'));
    kbEl.appendChild(r);
  });
}
const rowEl = i => boardEl.children[i];
const tileEl = (r, c) => boardEl.children[r].children[c];

function paintRow(r, word, states, animate) {
  for (let c = 0; c < L; c++) {
    const t = tileEl(r, c);
    t.textContent = word[c] || '';
    t.dataset.state = states ? states[c] : (word[c] ? 'filled' : 'empty');
    t.classList.remove('flip', 'bounce');
    if (states) t.setAttribute('aria-label', `${word[c]}, ${states[c]}`);
    if (animate && states) {
      void t.offsetWidth;
      t.style.animationDelay = (reduceMotion() ? 0 : c * 300) + 'ms';
      t.classList.add('flip');
    } else t.style.animationDelay = '';
  }
}
function keyStates() {
  const rank = { absent: 1, present: 2, correct: 3 }, m = {};
  game.guesses.forEach(g => evaluate(g, game.answer).forEach((s, i) => {
    if (!m[g[i]] || rank[s] > rank[m[g[i]]]) m[g[i]] = s;
  }));
  return m;
}
function paintKeyboard() {
  const m = keyStates();
  kbEl.querySelectorAll('.key').forEach(k => { const s = m[k.dataset.key]; if (s) k.dataset.state = s; else delete k.dataset.state; });
}
function renderAll() {
  buildBoard();
  game.guesses.forEach((g, i) => paintRow(i, g, evaluate(g, game.answer), false));
  if (game.status === 'playing') paintRow(game.guesses.length, game.current, null, false);
  paintKeyboard();
  renderAfter();
  $('#daily-no').textContent = '#' + (day + 1).toLocaleString('en');
  document.querySelectorAll('.mode').forEach(b => b.classList.toggle('is-active', b.dataset.mode === mode));
}
function renderAfter() {
  afterEl.innerHTML = '';
  if (game.status === 'playing') { afterEl.hidden = true; return; }
  afterEl.hidden = false;
  const v = el('span', 'verdict');
  if (game.status === 'won') v.textContent = `Solved in ${game.guesses.length}/${MAXG}`;
  else { v.append('The word was '); v.appendChild(el('b', '', game.answer)); }
  afterEl.appendChild(v);
  if (mode === 'daily') {
    const s = el('button', 'btn', 'Stats & share'); s.onclick = openStats; afterEl.appendChild(s);
  } else {
    const n = el('button', 'btn', 'New word'); n.onclick = () => startMode('practice', true); afterEl.appendChild(n);
  }
}

/* ------------------------------------------------------------------ toasts */
function toast(msg, ms = 1800) {
  const t = el('div', 'toast', msg); $('#toasts').prepend(t);
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 300); }, ms);
}

/* ------------------------------------------------------------------ input */
function typeLetter(ch) {
  if (busy || game.status !== 'playing' || game.current.length >= L) return;
  game.current += ch;
  paintRow(game.guesses.length, game.current, null, false);
  tileEl(game.guesses.length, game.current.length - 1).dataset.state = 'filled';
}
function backspace() {
  if (busy || game.status !== 'playing' || !game.current.length) return;
  game.current = game.current.slice(0, -1);
  paintRow(game.guesses.length, game.current, null, false);
}
function hardModeError(guess) {
  const prev = game.guesses;
  for (const g of prev) {
    const ev = evaluate(g, game.answer);
    for (let i = 0; i < L; i++) {
      if (ev[i] === 'correct' && guess[i] !== g[i]) return `${ord(i + 1)} letter must be ${g[i].toUpperCase()}`;
    }
    for (let i = 0; i < L; i++) {
      if (ev[i] === 'present' && !guess.includes(g[i])) return `Guess must contain ${g[i].toUpperCase()}`;
    }
  }
  return null;
}
const ord = n => ['1st', '2nd', '3rd', '4th', '5th'][n - 1];

function rejectRow(msg) {
  toast(msg);
  const r = rowEl(game.guesses.length); r.classList.remove('shake'); void r.offsetWidth; r.classList.add('shake');
  setTimeout(() => r.classList.remove('shake'), 500);
}

async function submit() {
  if (busy || game.status !== 'playing') return;
  const g = game.current;
  if (g.length < L) return rejectRow('Not enough letters');
  if (!VALID.has(g)) return rejectRow('Not in word list');
  if (settings.hard) { const err = hardModeError(g); if (err) return rejectRow(err); }

  busy = true;
  const r = game.guesses.length;
  const states = evaluate(g, game.answer);
  game.guesses.push(g);
  game.current = '';
  const won = g === game.answer;
  const lost = !won && game.guesses.length >= MAXG;
  game.status = won ? 'won' : lost ? 'lost' : 'playing';

  paintRow(r, g, states, true);
  if (game.mode === 'daily') { progress.daily = { day, guesses: game.guesses, status: game.status }; if (game.status !== 'playing') recordResult(won); saveProgress(); }

  await sleep(reduceMotion() ? 50 : (L - 1) * 300 + 560);
  paintKeyboard();
  busy = false;

  if (won) {
    for (let c = 0; c < L; c++) { const t = tileEl(r, c); t.classList.remove('flip'); void t.offsetWidth; t.style.animationDelay = (reduceMotion() ? 0 : c * 90) + 'ms'; t.classList.add('bounce'); }
    toast(['Genius', 'Magnificent', 'Impressive', 'Splendid', 'Great', 'Phew'][r], 2000);
  } else if (lost) toast(game.answer.toUpperCase(), 2400);
  if (game.status !== 'playing') {
    renderAfter();
    if (game.mode === 'daily') setTimeout(openStats, won ? 1700 : 2600);
  } else paintRow(game.guesses.length, '', null, false);
}

function recordResult(won) {
  const s = progress.stats;
  s.played++; s.lastDay = day;
  if (won) {
    s.wins++; s.dist[game.guesses.length - 1]++;
    s.streak = s.lastWinDay === day - 1 ? s.streak + 1 : 1;
    s.maxStreak = Math.max(s.maxStreak, s.streak);
    s.lastWinDay = day;
  } else s.streak = 0;
}
const currentStreak = () => (progress.stats.lastWinDay != null && progress.stats.lastWinDay >= day - 1) ? progress.stats.streak : 0;

function press(k) {
  if (k === 'enter') submit(); else if (k === 'back') backspace(); else if (/^[a-z]$/.test(k)) typeLetter(k);
}
kbEl.addEventListener('click', e => { const b = e.target.closest('.key'); if (b) { press(b.dataset.key); b.blur(); } });
addEventListener('keydown', e => {
  if (e.key === 'Escape' && !$('#overlay').hidden) return closeModal();
  if (!$('#overlay').hidden || e.ctrlKey || e.metaKey || e.altKey) return;
  const tag = (e.target.tagName || '').toLowerCase();
  if (tag === 'input') return;
  if (e.key === 'Enter') { if (tag === 'button') return; e.preventDefault(); press('enter'); }
  else if (e.key === 'Backspace') press('back');
  else if (/^[a-zA-Z]$/.test(e.key)) press(e.key.toLowerCase());
});

/* ------------------------------------------------------------------ modes */
function startMode(m, fresh) {
  if (busy) return;
  mode = m;
  game = m === 'daily' ? newDailyGame() : (fresh || !practiceGame ? (practiceGame = newPracticeGame()) : practiceGame);
  renderAll();
}
let practiceGame = null;
document.querySelectorAll('.mode').forEach(b => b.addEventListener('click', () => { if (b.dataset.mode !== mode) startMode(b.dataset.mode); }));

/* ------------------------------------------------------------------ modals */
let lastFocus = null, tickTimer = null;
function openModal(html, mount) {
  const body = $('#modal-body');
  body.innerHTML = '';
  if (typeof html === 'string') body.innerHTML = html; else body.appendChild(html);
  lastFocus = document.activeElement;
  $('#overlay').hidden = false;
  if (mount) mount(body);
  $('#modal').focus();
  $('#modal').scrollTop = 0;
}
function closeModal() {
  $('#overlay').hidden = true; clearInterval(tickTimer);
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}
$('#modal-close').addEventListener('click', closeModal);
$('#overlay').addEventListener('mousedown', e => { if (e.target.id === 'overlay') closeModal(); });

const exTile = (ch, st) => `<div class="tile" data-state="${st}">${ch}</div>`;
function openHelp() {
  openModal(`
    <h2>How to play</h2>
    <p>Guess the hidden word in <b>six tries</b>. Each guess must be a valid five-letter word. After every guess, the tiles show how close you were.</p>
    <hr>
    <p><b>Examples</b></p>
    <div class="ex-row">${exTile('W', 'correct')}${exTile('E', 'filled')}${exTile('A', 'filled')}${exTile('R', 'filled')}${exTile('Y', 'filled')}</div>
    <p><b>W</b> is in the word and in the right spot.</p>
    <div class="ex-row">${exTile('P', 'filled')}${exTile('I', 'present')}${exTile('L', 'filled')}${exTile('L', 'filled')}${exTile('S', 'filled')}</div>
    <p><b>I</b> is in the word but in the wrong spot.</p>
    <div class="ex-row">${exTile('V', 'filled')}${exTile('A', 'filled')}${exTile('G', 'filled')}${exTile('U', 'absent')}${exTile('E', 'filled')}</div>
    <p><b>U</b> is not in the word in any spot.</p>
    <hr>
    <p>There is a new <b>Daily</b> puzzle every day at midnight, the same for everyone. Your stats and streak are saved in this browser. <b>Unlimited</b> gives you endless random words that do not affect your stats.</p>
    <p style="margin-top:16px"><button class="btn block" id="help-go">Play</button></p>
  `, b => { $('#help-go', b).onclick = closeModal; });
  store.set('wg:seen-help', 1);
}

function shareText() {
  const sq = { correct: settings.contrast ? '🟧' : '🟩', present: settings.contrast ? '🟦' : '🟨', absent: settings.dark ? '⬛' : '⬜' };
  const rows = game.guesses.map(g => evaluate(g, game.answer).map(s => sq[s]).join('')).join('\n');
  const score = game.status === 'won' ? game.guesses.length : 'X';
  return `${CFG.NAME} #${day + 1} ${score}/${MAXG}${settings.hard ? '*' : ''}\n\n${rows}\n\n${CFG.URL}`;
}
async function copyText(t) {
  try { await navigator.clipboard.writeText(t); return true; } catch {}
  try {
    const ta = el('textarea'); ta.value = t; ta.style.cssText = 'position:fixed;opacity:0'; document.body.appendChild(ta); ta.select();
    const ok = document.execCommand('copy'); ta.remove(); return ok;
  } catch { return false; }
}

function openStats() {
  const s = progress.stats;
  const pct = s.played ? Math.round(s.wins / s.played * 100) : 0;
  const max = Math.max(1, ...s.dist);
  const finished = mode === 'daily' && game.status !== 'playing';
  const hlRow = finished && game.status === 'won' ? game.guesses.length - 1 : -1;
  const dist = s.dist.map((n, i) =>
    `<div class="dist-row"><span>${i + 1}</span><div class="dist-bar ${i === hlRow ? 'hl' : ''}" style="width:${Math.max(8, n / max * 100)}%">${n}</div></div>`).join('');
  openModal(`
    <h2>Statistics</h2>
    <div class="stat-grid">
      <div class="stat"><b>${s.played}</b><span>Played</span></div>
      <div class="stat"><b>${pct}</b><span>Win %</span></div>
      <div class="stat"><b>${currentStreak()}</b><span>Current streak</span></div>
      <div class="stat"><b>${s.maxStreak}</b><span>Max streak</span></div>
    </div>
    <h3>Guess distribution</h3>
    <div class="dist">${dist}</div>
    ${finished ? `<div class="share-row">
      <div class="next"><small>Next puzzle</small><b id="countdown">--:--:--</b></div>
      <div class="divider"></div>
      <button class="btn" id="share-btn">Share</button></div>` : ''}
  `, b => {
    const cd = $('#countdown', b);
    if (cd) {
      const tick = () => {
        const n = new Date(), nx = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1);
        let sec = Math.max(0, Math.floor((nx - n) / 1000));
        cd.textContent = [Math.floor(sec / 3600), Math.floor(sec / 60) % 60, sec % 60].map(v => String(v).padStart(2, '0')).join(':');
        if (sec === 0) location.reload();
      };
      tick(); tickTimer = setInterval(tick, 1000);
    }
    const sh = $('#share-btn', b);
    if (sh) sh.onclick = async () => {
      const t = shareText();
      if (navigator.share && matchMedia('(pointer: coarse)').matches) { try { await navigator.share({ text: t }); return; } catch {} }
      toast(await copyText(t) ? 'Copied to clipboard' : 'Could not copy');
    };
  });
}

function openSettings() {
  const locked = mode === 'daily' && game.status === 'playing' && game.guesses.length > 0;
  const row = (id, title, sub, on, dis) => `<div class="setting"><div><b>${title}</b><small>${sub}</small></div>
    <button class="switch" role="switch" id="${id}" aria-checked="${on}" aria-label="${title}" ${dis ? 'disabled' : ''}></button></div>`;
  openModal(`
    <h2>Settings</h2>
    ${row('set-hard', 'Hard mode', locked ? 'Available at the start of a new game.' : 'Any revealed hints must be used in later guesses.', settings.hard, locked)}
    ${row('set-dark', 'Dark theme', 'Easier on the eyes at night.', settings.dark)}
    ${row('set-contrast', 'Colour-blind mode', 'Uses orange and blue instead of green and yellow.', settings.contrast)}
    <hr>
    <p style="text-align:center;font-size:.8rem">${CFG.NAME} is an independent word puzzle by Unblocked Games USA.</p>
  `, b => {
    const wire = (id, key) => { const s = $('#' + id, b); s.onclick = () => { if (s.disabled) return; settings[key] = !settings[key]; s.setAttribute('aria-checked', settings[key]); applySettings(); }; };
    wire('set-hard', 'hard'); wire('set-dark', 'dark'); wire('set-contrast', 'contrast');
  });
}

/* ------------------------------------------------------------------ wiring + boot */
$('#btn-help').onclick = openHelp;
$('#btn-stats').onclick = openStats;
$('#btn-settings').onclick = openSettings;

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && todayIndex() !== day && mode === 'daily') { day = todayIndex(); startMode('daily'); }
});

(function boot() {
  applySettings();
  buildKeyboard();
  progress = sanitizeProgress(store.get('wg:progress'));
  startMode('daily');
  if (!store.get('wg:seen-help') && !progress.stats.played && !progress.daily.guesses.length) openHelp();
})();
})();
