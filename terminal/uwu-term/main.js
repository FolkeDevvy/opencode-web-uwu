// ♡ uwu-term ✧ main process: window, shells (pty), config.
const { app, BrowserWindow, ipcMain, nativeTheme, shell, clipboard } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const pty = require('node-pty');

// Native Wayland (KDE Plasma etc.), falling back to X11 automatically.
app.commandLine.appendSwitch('ozone-platform-hint', 'auto');
app.commandLine.appendSwitch('enable-features', 'WaylandWindowDecorations');
app.setName('uwu-term');
app.setDesktopName('uwu-term.desktop');

// ─────────────────────────────── config ───────────────────────────────
const CONFIG_DIR = path.join(process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config'), 'uwu-term');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const DEFAULTS = {
  theme: 'auto', // "auto" follows the desktop (KDE light/dark), or "dark" / "light"
  shell: '', // empty = your login shell ($SHELL)
  shellArgs: [],
  shellIntegration: true, // lets the mascot react to commands (bash, zsh, fish)
  fontFamily: "'JetBrains Mono', 'Fira Code', 'Hack', 'Noto Sans Mono', 'DejaVu Sans Mono', monospace",
  fontSize: 14,
  lineHeight: 1.15,
  cursorStyle: 'bar', // "bar" | "block" | "underline"
  scrollback: 10000,
  opacity: 0.86, // how solid the terminal card is (petals show through the rest)
  petals: true,
  sparkles: true, // sparkles while typing
  clickBursts: true,
  confetti: true, // when a long command (>= confettiAfter seconds) succeeds
  confettiAfter: 5,
  mascot: true,
  splash: true,
};

function loadConfig() {
  let user = {};
  try {
    user = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch (err) {
    if (err.code === 'ENOENT') {
      // first run: write the defaults so they're easy to find and tweak
      try {
        fs.mkdirSync(CONFIG_DIR, { recursive: true });
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(DEFAULTS, null, 2) + '\n');
      } catch {}
    } else {
      console.error(`uwu-term: couldn't read ${CONFIG_FILE}: ${err.message}`);
    }
  }
  return { ...DEFAULTS, ...user };
}
const config = loadConfig();

// ─────────────────────────────── shells ───────────────────────────────
const SHELL_DIR = path.join(__dirname, 'shell');

/** Work out how to launch the shell with uwu's shell integration (OSC 133 marks). */
function shellCommand() {
  const file = config.shell || process.env.SHELL || '/bin/bash';
  const name = path.basename(file);
  const env = { ...process.env, TERM: 'xterm-256color', COLORTERM: 'truecolor', TERM_PROGRAM: 'uwu-term' };
  // without any locale, shells treat ♡ and friends as several characters
  if (!env.LANG && !env.LC_ALL && !env.LC_CTYPE) env.LANG = 'C.UTF-8';
  let args = [...config.shellArgs];
  if (config.shellIntegration) {
    if (name === 'bash') {
      args = ['--rcfile', path.join(SHELL_DIR, 'uwu.bash'), ...args];
    } else if (name === 'zsh') {
      env.UWU_USER_ZDOTDIR = process.env.ZDOTDIR || os.homedir();
      env.ZDOTDIR = path.join(SHELL_DIR, 'zsh');
    } else if (name === 'fish') {
      args = ['--init-command', `source '${path.join(SHELL_DIR, 'uwu.fish')}'`, ...args];
    }
  }
  return { file, args, env };
}

const ptys = new Map();

function startPty(win, id, cols, rows, cwd) {
  const { file, args, env } = shellCommand();
  let dir = cwd && fs.existsSync(cwd) ? cwd : os.homedir();
  const p = pty.spawn(file, args, { name: 'xterm-256color', cols, rows, cwd: dir, env });
  ptys.set(id, p);
  p.onData((data) => !win.isDestroyed() && win.webContents.send('pty:data', id, data));
  p.onExit(({ exitCode }) => {
    ptys.delete(id);
    if (!win.isDestroyed()) win.webContents.send('pty:exit', id, exitCode);
  });
  return { shell: path.basename(file) };
}

// ─────────────────────────────── window ───────────────────────────────
function themeName() {
  if (config.theme === 'dark' || config.theme === 'light') return config.theme;
  return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 700,
    minWidth: 420,
    minHeight: 260,
    frame: false,
    transparent: true,
    backgroundColor: '#00000000',
    title: 'uwu-term',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  win.once('ready-to-show', () => win.show());
  win.on('maximize', () => win.webContents.send('win:state', 'maximized'));
  win.on('unmaximize', () => win.webContents.send('win:state', 'normal'));
  // links open in the real browser, never inside the terminal window
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:/.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
  win.webContents.on('will-navigate', (e) => e.preventDefault());
  return win;
}

const fromSender = (e) => BrowserWindow.fromWebContents(e.sender);

ipcMain.handle('config:get', () => ({ ...config, resolvedTheme: themeName(), configFile: CONFIG_FILE }));
ipcMain.handle('pty:spawn', (e, id, cols, rows, cwd) => startPty(fromSender(e), id, cols, rows, cwd));
ipcMain.on('pty:write', (_e, id, data) => ptys.get(id)?.write(data));
ipcMain.on('pty:resize', (_e, id, cols, rows) => {
  try {
    ptys.get(id)?.resize(Math.max(cols, 2), Math.max(rows, 1));
  } catch {}
});
ipcMain.on('pty:kill', (_e, id) => {
  try {
    ptys.get(id)?.kill();
  } catch {}
  ptys.delete(id);
});
ipcMain.on('clip:write', (_e, text) => clipboard.writeText(text));
ipcMain.handle('clip:read', () => clipboard.readText());
ipcMain.on('open:url', (_e, url) => /^https?:/.test(url) && shell.openExternal(url));
ipcMain.on('win:minimize', (e) => fromSender(e)?.minimize());
ipcMain.on('win:maximize', (e) => {
  const w = fromSender(e);
  if (w) w.isMaximized() ? w.unmaximize() : w.maximize();
});
ipcMain.on('win:close', (e) => fromSender(e)?.close());
ipcMain.on('win:new', () => createWindow());

nativeTheme.on('updated', () => {
  for (const w of BrowserWindow.getAllWindows()) w.webContents.send('theme', themeName());
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  for (const p of ptys.values()) {
    try {
      p.kill();
    } catch {}
  }
  app.quit();
});
