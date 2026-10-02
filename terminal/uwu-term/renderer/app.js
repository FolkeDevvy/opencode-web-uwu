// ♡ uwu-term ✧ the window: tabs, terminals and all the kawaii.
/* global Terminal, FitAddon, WebLinksAddon, WebglAddon, uwu */
(async () => {
  'use strict';

  const cfg = await uwu.config();
  const root = document.documentElement;
  const $ = (s) => document.querySelector(s);
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = (xs) => xs[Math.floor(Math.random() * xs.length)];
  const COLORS = ['#ff8fc8', '#c7a2ff', '#8ff5cf', '#ffe59a', '#9fd8ff', '#ff5fae'];
  const PARTICLES = ['♥', '♡', '✧', '✦', '❀', '✿', '☆'];

  // ─────────────────────────────── colours ───────────────────────────────
  const THEMES = {
    dark: {
      background: '#00000000', foreground: '#ffeaf6', cursor: '#ff8fc8', cursorAccent: '#2a0c22',
      selectionBackground: '#ff8fc855', selectionInactiveBackground: '#c7a2ff33',
      black: '#2a1733', red: '#ff8aa5', green: '#8ff5cf', yellow: '#ffe59a', blue: '#9fd8ff', magenta: '#ff8fc8', cyan: '#7fe3e0', white: '#ffeaf6',
      brightBlack: '#8a6683', brightRed: '#ffb3c4', brightGreen: '#b8ffe4', brightYellow: '#fff0b8', brightBlue: '#c4e8ff', brightMagenta: '#ffb3da', brightCyan: '#b0f5f2', brightWhite: '#fff6fb',
    },
    light: {
      background: '#00000000', foreground: '#57264c', cursor: '#e8438f', cursorAccent: '#ffffff',
      selectionBackground: '#ff5fae38', selectionInactiveBackground: '#8a4fe024',
      black: '#57264c', red: '#e0325e', green: '#13936a', yellow: '#b07d00', blue: '#2f86c9', magenta: '#e8438f', cyan: '#1a8f8c', white: '#b592ab',
      brightBlack: '#9a5f8a', brightRed: '#ff5f84', brightGreen: '#1d9a6c', brightYellow: '#c99a00', brightBlue: '#3d9ad6', brightMagenta: '#ff5fae', brightCyan: '#21a6a2', brightWhite: '#3e1436',
    },
  };
  let theme = cfg.resolvedTheme;
  function applyTheme(t) {
    theme = t;
    root.classList.toggle('dark', t === 'dark');
    root.classList.toggle('light', t === 'light');
    for (const tab of tabs) tab.term.options.theme = THEMES[t];
  }
  root.style.setProperty('--opacity', String(cfg.opacity));
  root.classList.toggle('no-petals', !cfg.petals);
  root.classList.toggle('no-mascot', !cfg.mascot);
  uwu.onTheme((t) => cfg.theme === 'auto' && applyTheme(t));
  uwu.onWindowState((s) => root.classList.toggle('maximized', s === 'maximized'));

  // ─────────────────────────────── effects ───────────────────────────────
  let live = 0;
  function burst(x, y, n, spread, size) {
    for (let i = 0; i < n && live < 80; i++) {
      const el = document.createElement('div');
      el.className = 'fx particle';
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
    if (!cfg.confetti) return;
    for (let i = 0; i < 70; i++) {
      const el = document.createElement('div');
      el.className = 'fx confetti';
      el.style.setProperty('--x0', `${rand(0, innerWidth)}px`);
      el.style.setProperty('--dx', `${rand(-120, 120)}px`);
      el.style.setProperty('--r', `${rand(-900, 900)}deg`);
      el.style.setProperty('--d', `${rand(1.6, 3)}s`);
      el.style.animationDelay = `${rand(0, 0.4)}s`;
      el.style.background = pick(COLORS);
      if (Math.random() < 0.35) el.style.borderRadius = '50%';
      el.addEventListener('animationend', () => el.remove(), { once: true });
      document.body.appendChild(el);
    }
  }
  const mascot = $('#mascot');
  const bubble = $('#bubble');
  let bubbleTimer;
  function say(text, ms = 3200) {
    if (!cfg.mascot) return;
    bubble.textContent = text;
    bubble.classList.add('show');
    clearTimeout(bubbleTimer);
    bubbleTimer = setTimeout(() => bubble.classList.remove('show'), ms);
  }
  function hop() {
    mascot.classList.remove('jump', 'sad');
    void mascot.offsetWidth;
    mascot.classList.add('jump');
  }
  let sadTimer;
  function sad(ms = 4000) {
    mascot.classList.remove('jump');
    mascot.classList.add('sad');
    clearTimeout(sadTimer);
    sadTimer = setTimeout(() => mascot.classList.remove('sad'), ms);
  }
  mascot.addEventListener('click', (e) => {
    hop();
    burst(e.clientX, e.clientY + 10, 10, 50, 15);
    say(pick(['hehe ♡', 'uwu', '(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)', 'more pats pls ✧', 'you\'re doing great ♡', 'remember to stretch (=^･ω･^=)']));
  });
  addEventListener('pointerdown', (e) => {
    if (cfg.clickBursts && e.button === 0 && !e.target.closest('.menu')) burst(e.clientX, e.clientY, 7, 44, 13);
  }, true);

  function cursorPoint(tab) {
    const ta = tab.el.querySelector('.xterm-helper-textarea');
    if (!ta) return null;
    const r = ta.getBoundingClientRect();
    return { x: r.left + 2, y: r.top + r.height / 2 };
  }

  // ─────────────────────────────── tabs ───────────────────────────────
  const tabs = [];
  let active = null;
  let nextId = 1;
  let fontSize = cfg.fontSize;

  async function newTab(cwd) {
    const id = nextId++;
    const el = document.createElement('div');
    el.className = 'term';
    $('#terminals').appendChild(el);
    const term = new Terminal({
      allowTransparency: true,
      allowProposedApi: true,
      theme: THEMES[theme],
      fontFamily: cfg.fontFamily,
      fontSize,
      lineHeight: cfg.lineHeight,
      cursorBlink: true,
      cursorStyle: cfg.cursorStyle,
      cursorInactiveStyle: 'outline',
      scrollback: cfg.scrollback,
      macOptionIsMeta: true,
      rightClickSelectsWord: false,
    });
    const fit = new FitAddon.FitAddon();
    term.loadAddon(fit);
    term.loadAddon(new WebLinksAddon.WebLinksAddon((_e, url) => uwu.openUrl(url)));
    term.open(el);
    try {
      const gl = new WebglAddon.WebglAddon();
      gl.onContextLoss(() => gl.dispose());
      term.loadAddon(gl);
    } catch {
      /* falls back to the DOM renderer */
    }
    const btn = document.createElement('div');
    btn.className = 'tab';
    const title = document.createElement('span');
    title.className = 'title';
    const x = document.createElement('span');
    x.className = 'x';
    x.textContent = '✕';
    btn.append(title, x);
    $('#tabs').appendChild(btn);
    const tab = { id, el, term, fit, btn, title, cwd: cwd || '', shell: '', cmdStart: 0, lastFailed: false };
    tabs.push(tab);
    btn.addEventListener('click', (e) => (e.target === x ? closeTab(tab) : activate(tab)));
    btn.addEventListener('auxclick', (e) => e.button === 1 && closeTab(tab));

    term.onData((data) => {
      uwu.write(id, data);
      if (cfg.sparkles && tab === active && (data.length === 1 || data === '\r')) {
        requestAnimationFrame(() => requestAnimationFrame(() => {
          const p = cursorPoint(tab);
          if (p) burst(p.x, p.y, data === '\r' ? 4 : 2, 30, 13);
        }));
      }
    });
    term.onTitleChange((t) => setTitle(tab, t));
    term.onBell(() => {
      const p = cursorPoint(tab);
      if (p) burst(p.x, p.y, 10, 56, 16);
      hop();
      say('ding! ♡', 1500);
    });
    term.onResize(({ cols, rows }) => uwu.resize(id, cols, rows));
    // OSC 7: the shell's current folder (new tabs open there)
    term.parser.registerOscHandler(7, (data) => {
      const m = /^file:\/\/[^/]*(\/.*)$/.exec(data);
      if (m) tab.cwd = decodeURIComponent(m[1]);
      return true;
    });
    // OSC 133: command started / finished (from uwu's shell integration)
    term.parser.registerOscHandler(133, (data) => {
      const [kind, code] = data.split(';');
      if (kind === 'C') {
        tab.cmdStart = performance.now();
        tab.btn.classList.add('busy');
      } else if (kind === 'D') {
        tab.btn.classList.remove('busy');
        commandFinished(tab, Number(code || 0), (performance.now() - tab.cmdStart) / 1000);
      }
      return true;
    });
    term.attachCustomKeyEventHandler((e) => keys(e, tab));
    el.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      menu(e.clientX, e.clientY, tab);
    });

    activate(tab);
    fit.fit();
    const info = await uwu.spawn(id, term.cols, term.rows, tab.cwd);
    tab.shell = info.shell;
    setTitle(tab, '');
    return tab;
  }

  function setTitle(tab, t) {
    tab.title.textContent = t || tab.shell || 'shell';
    tab.btn.title = tab.title.textContent;
  }

  function activate(tab) {
    active = tab;
    for (const t of tabs) {
      t.el.classList.toggle('active', t === tab);
      t.btn.classList.toggle('active', t === tab);
    }
    requestAnimationFrame(() => {
      tab.fit.fit();
      tab.term.focus();
    });
  }

  function closeTab(tab) {
    const i = tabs.indexOf(tab);
    if (i < 0) return;
    uwu.kill(tab.id);
    tab.term.dispose();
    tab.el.remove();
    tab.btn.remove();
    tabs.splice(i, 1);
    if (!tabs.length) return uwu.close();
    if (active === tab) activate(tabs[Math.min(i, tabs.length - 1)]);
  }

  uwu.onData((id, data) => tabs.find((t) => t.id === id)?.term.write(data));
  uwu.onExit((id) => {
    const tab = tabs.find((t) => t.id === id);
    if (tab) closeTab(tab);
  });

  // ─────────────────────────────── mascot reacts to commands ───────────────────────────────
  function commandFinished(tab, code, seconds) {
    if (code === 0) {
      if (seconds >= cfg.confettiAfter) {
        confetti();
        hop();
        say(`all done! ✧ (took ${seconds < 60 ? `${Math.round(seconds)}s` : `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`})`);
      } else if (tab.lastFailed) {
        hop();
        say(pick(['fixed it! ✧ (｡♥‿♥｡)', 'yay, it worked ♡', 'see? you got this ✿']));
      } else if (Math.random() < 0.18) {
        hop();
      }
      tab.lastFailed = false;
    } else if (code === 130) {
      say('cancelled ✋ (・_・;)', 1800);
    } else {
      tab.lastFailed = true;
      sad();
      const why = code === 127 ? 'command not found?' : code === 126 ? "can't run that one…" : code === 1 ? "that didn't work…" : 'oh no…';
      say(`${why} exit ${code} ${pick(['(；へ：)', '(╥﹏╥)', '(｡•́︿•̀｡)'])}`, 4200);
      const p = cursorPoint(tab);
      if (p) burst(p.x, p.y, 3, 22, 12);
    }
  }

  // ─────────────────────────────── keys & menu ───────────────────────────────
  function zoom(delta) {
    fontSize = delta === 0 ? cfg.fontSize : Math.min(40, Math.max(7, fontSize + delta));
    for (const t of tabs) t.term.options.fontSize = fontSize;
    active.fit.fit();
  }
  async function paste(tab) {
    const text = await uwu.paste();
    if (text) tab.term.paste(text);
  }
  function step(dir) {
    const i = tabs.indexOf(active);
    activate(tabs[(i + dir + tabs.length) % tabs.length]);
  }
  function keys(e, tab) {
    if (e.type !== 'keydown') return true;
    const k = e.key.toLowerCase();
    if (e.ctrlKey && e.shiftKey) {
      if (k === 'c') { if (tab.term.hasSelection()) uwu.copy(tab.term.getSelection()); return false; }
      if (k === 'v') { paste(tab); return false; }
      if (k === 't') { newTab(active?.cwd); return false; }
      if (k === 'w') { closeTab(tab); return false; }
      if (k === 'n') { uwu.newWindow(); return false; }
      if (e.key === 'Tab') { step(-1); return false; }
    }
    if (e.ctrlKey && !e.shiftKey && !e.altKey) {
      if (e.key === 'Tab' || e.key === 'PageDown') { step(1); return false; }
      if (e.key === 'PageUp') { step(-1); return false; }
      if (e.key === '=' || e.key === '+') { zoom(1); return false; }
      if (e.key === '-') { zoom(-1); return false; }
      if (e.key === '0') { zoom(0); return false; }
    }
    if (e.shiftKey && e.key === 'Insert') { paste(tab); return false; }
    return true;
  }

  function menu(x, y, tab) {
    document.querySelector('.menu')?.remove();
    const m = document.createElement('div');
    m.className = 'menu';
    const item = (label, hint, fn) => {
      const d = document.createElement('div');
      const l = document.createElement('b');
      l.textContent = label;
      const h = document.createElement('span');
      h.textContent = hint;
      d.append(l, h);
      d.addEventListener('click', () => { m.remove(); fn(); tab.term.focus(); });
      m.appendChild(d);
    };
    const sep = () => m.appendChild(document.createElement('hr'));
    item('♡ copy', 'Ctrl+Shift+C', () => tab.term.hasSelection() && uwu.copy(tab.term.getSelection()));
    item('✧ paste', 'Ctrl+Shift+V', () => paste(tab));
    item('✿ select all', '', () => tab.term.selectAll());
    sep();
    item('＋ new tab', 'Ctrl+Shift+T', () => newTab(active?.cwd));
    item('❀ new window', 'Ctrl+Shift+N', () => uwu.newWindow());
    item('☆ clear', '', () => tab.term.clear());
    sep();
    item('✕ close tab', 'Ctrl+Shift+W', () => closeTab(tab));
    document.body.appendChild(m);
    const r = m.getBoundingClientRect();
    m.style.left = `${Math.min(x, innerWidth - r.width - 8)}px`;
    m.style.top = `${Math.min(y, innerHeight - r.height - 8)}px`;
    setTimeout(() => addEventListener('pointerdown', (e) => !m.contains(e.target) && m.remove(), { once: true }), 0);
  }

  // ─────────────────────────────── window ───────────────────────────────
  $('#min').addEventListener('click', () => uwu.minimize());
  $('#max').addEventListener('click', () => uwu.maximize());
  $('#close').addEventListener('click', () => uwu.close());
  $('#new-tab').addEventListener('click', () => newTab(active?.cwd));
  // clicking the title bar (mascot, tabs, buttons) never steals focus from the shell
  $('#titlebar').addEventListener('mousedown', (e) => e.preventDefault());
  $('#titlebar').addEventListener('dblclick', (e) => e.target.closest('#titlebar') && !e.target.closest('button, .tab, #mascot') && uwu.maximize());
  new ResizeObserver(() => active && active.fit.fit()).observe($('#terminals'));

  function splash() {
    const s = document.createElement('div');
    s.id = 'splash';
    const logo = document.createElement('div');
    logo.className = 'logo';
    const title = document.createElement('div');
    title.className = 'title';
    [...'uwu-term'].forEach((ch, i) => {
      const sp = document.createElement('span');
      sp.textContent = ch;
      sp.style.animationDelay = `${0.25 + i * 0.06}s`;
      title.appendChild(sp);
    });
    const sub = document.createElement('div');
    sub.className = 'sub';
    sub.textContent = 'warming up your shell ✿';
    s.append(logo, title, sub);
    $('#frame').appendChild(s);
    setTimeout(() => {
      s.classList.add('out');
      setTimeout(() => s.remove(), 600);
      say(pick(['hi hi! ready to hack? ✧', 'welcome back ♡', 'let\'s make something cute today ✿']), 3000);
    }, 1300);
  }

  applyTheme(theme);
  if (cfg.splash && !matchMedia('(prefers-reduced-motion: reduce)').matches) splash();
  await newTab();
})();
