// ♡ uwu IDE ✧ effects for the Kawaii Workbench (injected by uwu-code).
// Plain DOM only: VS Code's page enforces Trusted Types, so no innerHTML.
(() => {
  'use strict';

  const UWU_THEME = /uwu-code-themes-uwu-/;
  const PARTICLES = ['♥', '♡', '✧', '✦', '❀', '✿', '☆'];
  const COLORS = ['#ff8fc8', '#c7a2ff', '#8ff5cf', '#ffe59a', '#9fd8ff', '#ff5fae'];
  const TIPS = [
    "you're doing amazing ♡",
    'remember to drink some water ✧',
    'stretch your paws (=^･ω･^=)',
    'every bug is just a feature in disguise ✿',
    'commit early, commit often ♡',
    'take a tiny break? ☆',
    'this code is so pretty (｡♥‿♥｡)',
  ];
  const opts = { splash: true, clicks: true, typing: true, mascot: true, confetti: true };
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = (xs) => xs[Math.floor(Math.random() * xs.length)];
  const active = () => {
    const wb = document.querySelector('.monaco-workbench');
    return !!wb && UWU_THEME.test(wb.className);
  };
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ─────────────── particles ───────────────
  let live = 0;
  function burst(x, y, n, spread, size) {
    if (!active() || reduced()) return;
    for (let i = 0; i < n && live < 80; i++) {
      const el = document.createElement('div');
      el.className = 'uwu-fx uwu-particle';
      el.textContent = pick(PARTICLES);
      const a = rand(0, Math.PI * 2);
      const d = rand(spread * 0.5, spread);
      el.style.setProperty('--x0', `${x}px`);
      el.style.setProperty('--y0', `${y}px`);
      el.style.setProperty('--dx', `${Math.cos(a) * d}px`);
      el.style.setProperty('--dy', `${Math.sin(a) * d - spread * 0.4}px`);
      el.style.setProperty('--r', `${rand(-180, 180)}deg`);
      el.style.setProperty('--s', `${rand(0.8, 1.4)}`);
      el.style.setProperty('--d', `${rand(0.6, 1)}s`);
      el.style.color = pick(COLORS);
      el.style.fontSize = `${rand(size * 0.7, size * 1.3)}px`;
      live++;
      el.addEventListener('animationend', () => { el.remove(); live--; }, { once: true });
      document.body.appendChild(el);
    }
  }

  function confetti() {
    if (!active() || reduced() || !opts.confetti) return;
    for (let i = 0; i < 70; i++) {
      const el = document.createElement('div');
      el.className = 'uwu-fx uwu-confetti';
      el.style.setProperty('--x0', `${rand(0, innerWidth)}px`);
      el.style.setProperty('--dx', `${rand(-120, 120)}px`);
      el.style.setProperty('--r', `${rand(-900, 900)}deg`);
      el.style.setProperty('--d', `${rand(1.8, 3.2)}s`);
      el.style.animationDelay = `${rand(0, 0.5)}s`;
      el.style.background = pick(COLORS);
      if (Math.random() < 0.35) el.style.borderRadius = '50%';
      el.addEventListener('animationend', () => el.remove(), { once: true });
      document.body.appendChild(el);
    }
  }

  // ─────────────── clicks & typing ───────────────
  addEventListener('pointerdown', (e) => {
    if (opts.clicks && e.button === 0) burst(e.clientX, e.clientY, 7, 46, 14);
  }, true);

  let lastType = 0;
  addEventListener('keydown', (e) => {
    if (!opts.typing || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length !== 1 && e.key !== 'Enter' && e.key !== 'Backspace') return;
    const now = performance.now();
    if (now - lastType < 45) return;
    lastType = now;
    // the caret moves after the key is handled, so look one frame later
    requestAnimationFrame(() => {
      const caret = document.querySelector('.monaco-editor.focused .cursor');
      if (!caret) return;
      const r = caret.getBoundingClientRect();
      if (!r.height) return;
      burst(r.left + 2, r.top + r.height / 2, e.key === 'Enter' ? 6 : 3, 34, 15);
    });
  }, true);

  // ─────────────── mascot ───────────────
  let mascot, bubble, bubbleTimer;
  function say(text, ms = 3200) {
    if (!bubble) return;
    bubble.textContent = text;
    bubble.classList.add('show');
    clearTimeout(bubbleTimer);
    bubbleTimer = setTimeout(() => bubble.classList.remove('show'), ms);
  }
  function ensureMascot() {
    const want = active() && opts.mascot;
    if (want && !mascot) {
      mascot = document.createElement('div');
      mascot.className = 'uwu-fx uwu-mascot';
      mascot.title = 'pat me ♡';
      mascot.addEventListener('click', (e) => {
        mascot.classList.remove('jump');
        void mascot.offsetWidth;
        mascot.classList.add('jump');
        burst(e.clientX, e.clientY - 20, 10, 60, 16);
        say(pick(['hehe ♡', 'uwu', '(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)', 'more pats pls ✧', pick(TIPS)]));
      });
      bubble = document.createElement('div');
      bubble.className = 'uwu-fx uwu-bubble';
      document.body.append(mascot, bubble);
      setTimeout(() => say('hi hi! ready to code? ✧', 3500), 1800);
    } else if (!want && mascot) {
      mascot.remove();
      bubble.remove();
      mascot = bubble = undefined;
    }
  }
  setInterval(() => { if (mascot && Math.random() < 0.5) say(pick(TIPS)); }, 90000);

  // The extension's status-bar mascot tells us about saves and errors.
  let lastFace = '';
  let lastErrors = 0;
  function readStatus() {
    const item = [...document.querySelectorAll('.statusbar-item[id^="folkedevvy.uwu-code"]')].find((el) => !el.id.endsWith('uwu.bridge'));
    if (item) {
      const face = item.textContent || '';
      if (face !== lastFace) {
        if (face.includes('ﾉ◕ヮ◕')) {
          confetti();
          if (mascot) {
            mascot.classList.remove('sad', 'jump');
            void mascot.offsetWidth;
            mascot.classList.add('jump');
            say(pick(['saved! ✧', 'yay, saved ♡', 'good job!! (ﾉ◕ヮ◕)ﾉ']));
          }
        }
        // the party face hides the error count for a moment, so keep the old one
        const m = face.match(/[；ー].*?(\d+)/);
        const errors = face.includes('ﾉ◕ヮ◕') ? lastErrors : face.includes('；') && m ? Number(m[1]) : 0;
        if (mascot) mascot.classList.toggle('sad', errors > 0);
        if (errors > lastErrors && mascot) say(pick(["oh no, an error (；へ：)", "it's okay, we'll fix it ♡", 'bug spotted! ( •̀ᴗ•́ )و']));
        if (errors === 0 && lastErrors > 0 && mascot) say('all fixed!! ✧ (｡♥‿♥｡)');
        lastErrors = errors;
        lastFace = face;
      }
    }
    const bridge = document.querySelector('.statusbar-item[id$="uwu.bridge"]');
    if (bridge) {
      const t = bridge.textContent || '';
      for (const k of Object.keys(opts)) {
        const m = t.match(new RegExp(`${k}=(\\d)`));
        if (m) opts[k] = m[1] === '1';
      }
    }
    ensureMascot();
  }

  // ─────────────── boot splash ───────────────
  function splash() {
    const el = document.createElement('div');
    el.className = 'uwu-fx uwu-splash';
    if (matchMedia('(prefers-color-scheme: light)').matches) el.classList.add('light');
    const logo = document.createElement('div');
    logo.className = 'uwu-splash-logo';
    const title = document.createElement('div');
    title.className = 'uwu-splash-title';
    [...'uwu IDE'].forEach((ch, i) => {
      const s = document.createElement('span');
      s.textContent = ch === ' ' ? ' ' : ch;
      s.style.animationDelay = `${0.35 + i * 0.07}s`;
      title.appendChild(s);
    });
    const sub = document.createElement('div');
    sub.className = 'uwu-splash-sub';
    sub.textContent = 'warming up the sakura ✿';
    const dots = document.createElement('div');
    dots.className = 'uwu-splash-dots';
    for (const c of ['♥', '♥', '♥']) {
      const s = document.createElement('span');
      s.textContent = c;
      dots.appendChild(s);
    }
    el.append(logo, title, sub, dots);
    document.body.appendChild(el);
    const started = Date.now();
    const done = () => {
      el.classList.add('out');
      setTimeout(() => el.remove(), 700);
    };
    // leave once the workbench is ready (or after a few seconds no matter what)
    const iv = setInterval(() => {
      const ready = document.querySelector('.monaco-workbench .part.editor');
      if (ready && !active()) {
        // not an uwu theme: get out of the way immediately
        clearInterval(iv);
        el.remove();
      } else if ((ready && Date.now() - started > 1600) || Date.now() - started > 6000) {
        clearInterval(iv);
        done();
      }
    }, 100);
  }

  function start() {
    if (opts.splash && !reduced()) splash();
    setInterval(readStatus, 400);
  }
  if (document.body) start();
  else addEventListener('DOMContentLoaded', start, { once: true });
})();
