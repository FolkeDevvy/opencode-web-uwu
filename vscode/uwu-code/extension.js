// ♡ uwu-code ✧ kawaii effects for the VS Code editor.
//
// Everything visual here is built from the editor decoration API. The petals
// and sparkle bursts use the well-known `textDecoration` trick: VS Code puts
// that value straight into the decoration's CSS rule, so extra declarations
// after "none;" let a decoration's ::before/::after become a free-floating,
// click-through layer. It is unofficial, so every effect can be switched off.

const vscode = require('vscode');
const path = require('path');
const petalLayers = require('./petals');
const kawaii = require('./kawaii-workbench');

const KAOMOJI = {
  happy: ['(｡♥‿♥｡)', '(｡♥‿♥｡)', '(｡♥‿♥｡)', '(｡-‿-｡)'],
  worried: ['(・_・;)', '(・_・;)', '(・_・;)', '(-_-;)'],
  sad: ['(；へ：)', '(；へ：)', '(；へ：)', '(；ー：)'],
  party: '(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧',
};
const ERROR_FACES = ['(；へ：)', '(╥﹏╥)', '(っ˘̩╭╮˘̩)っ', '(｡•́︿•̀｡)', '( ´•̥̥̥ω•̥̥̥` )'];

const cfg = () => vscode.workspace.getConfiguration('uwu');

/** @param {vscode.ExtensionContext} context */
function activate(context) {
  const petals = new Petals();
  const hearts = new GutterHearts(context);
  const kaomoji = new ErrorKaomoji();
  const mascot = new Mascot();
  const bridge = new Bridge();
  context.subscriptions.push(petals, hearts, kaomoji, mascot, bridge);

  context.subscriptions.push(
    vscode.commands.registerCommand('uwu.togglePetals', () => {
      cfg().update('petals.enabled', !cfg().get('petals.enabled'), vscode.ConfigurationTarget.Global);
    }),
    vscode.commands.registerCommand('uwu.sparkle', () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) burst(editor);
      mascot.celebrate();
    }),
    vscode.commands.registerCommand('uwu.clearHearts', () => hearts.clearAll()),
    vscode.commands.registerCommand('uwu.enableKawaiiWorkbench', () => setKawaii(context, true)),
    vscode.commands.registerCommand('uwu.disableKawaiiWorkbench', () => setKawaii(context, false)),
    vscode.workspace.onDidSaveTextDocument((doc) => {
      hearts.clear(doc);
      const editor = vscode.window.activeTextEditor;
      if (editor && editor.document === doc && cfg().get('sparkleOnSave')) burst(editor);
      mascot.celebrate();
    }),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (!e.affectsConfiguration('uwu')) return;
      petals.rebuild();
      hearts.refreshAll();
      kaomoji.refreshAll();
      mascot.refresh();
      bridge.refresh();
    }),
  );
  checkKawaiiAfterUpdate(context);
}

// ─────────────────────────────── Kawaii Workbench ───────────────────────────────

// Editor settings that make the kawaii look complete. They're only applied
// where you haven't set your own value, and are put back on disable.
const KAWAII_SETTINGS = {
  'workbench.iconTheme': 'uwu-cuties',
  'window.title': '${dirty}${activeEditorShort}${separator}${rootName}${separator}✿ uwu IDE',
  'window.commandCenter': true,
  'window.menuBarVisibility': 'compact',
  'workbench.layoutControl.enabled': false,
  'workbench.startupEditor': 'none',
  'workbench.list.smoothScrolling': true,
  'workbench.tree.indent': 14,
  'workbench.tree.renderIndentGuides': 'always',
  'editor.cursorBlinking': 'expand',
  'editor.cursorSmoothCaretAnimation': 'on',
  'editor.cursorWidth': 3,
  'editor.smoothScrolling': true,
  'editor.roundedSelection': true,
  'editor.minimap.enabled': false,
  'editor.renderLineHighlight': 'all',
  'editor.bracketPairColorization.enabled': true,
  'editor.guides.bracketPairs': 'active',
  'editor.padding.top': 10,
  'terminal.integrated.smoothScrolling': true,
};

const ENABLED_KEY = 'uwu.kawaii.enabled';
const CHANGED_KEY = 'uwu.kawaii.changedSettings';

/**
 * @param {vscode.ExtensionContext} context
 * @param {boolean} enable
 */
async function setKawaii(context, enable) {
  const appRoot = vscode.env.appRoot;
  if (appRoot.startsWith('/snap/')) {
    vscode.window.showErrorMessage(
      "uwu: the Snap version of VS Code is read-only, so the Kawaii Workbench can't be installed. The .deb/.rpm or tarball versions work. (The editor effects still work everywhere ♡)",
    );
    return;
  }
  if (enable) {
    const ok = await vscode.window.showWarningMessage(
      'Turn VS Code into uwu IDE? ✿',
      {
        modal: true,
        detail:
          "This restyles the whole window by adding uwu-code's stylesheet and script to VS Code's own files (backups are kept, and 'uwu: Disable Kawaii Workbench' undoes it). After a VS Code update you'll be offered to re-apply it.",
      },
      'Make it kawaii',
    );
    if (ok !== 'Make it kawaii') return;
  }
  let p;
  try {
    p = kawaii.plan(appRoot, path.join(context.extensionPath, 'workbench'), enable);
  } catch (err) {
    vscode.window.showErrorMessage(`uwu: ${err.message}`);
    return;
  }
  let needsSudo = false;
  try {
    kawaii.apply(p);
  } catch (err) {
    if (!['EACCES', 'EPERM', 'EROFS'].includes(err.code)) {
      vscode.window.showErrorMessage(`uwu: couldn't update VS Code's files: ${err.message}`);
      return;
    }
    needsSudo = true;
  }
  await context.globalState.update(ENABLED_KEY, enable);
  await applySettings(context, enable);
  if (needsSudo) {
    const script = kawaii.stage(p, path.join(context.globalStorageUri.fsPath, 'kawaii-staging'));
    const cmd = `sudo sh '${script}'`;
    const pick = await vscode.window.showInformationMessage(
      `uwu: VS Code is installed system-wide, so this last step needs your password. Run this in a terminal, then reload: ${cmd}`,
      'Run in terminal',
      'Copy command',
    );
    if (pick === 'Copy command') await vscode.env.clipboard.writeText(cmd);
    if (pick === 'Run in terminal') {
      const term = vscode.window.createTerminal('uwu IDE ✿');
      term.show();
      term.sendText(cmd);
    }
    return;
  }
  const again = await vscode.window.showInformationMessage(
    enable ? 'uwu IDE is ready ✿ reload to see it!' : 'Kawaii Workbench removed. Reload to finish.',
    'Reload now',
  );
  if (again === 'Reload now') vscode.commands.executeCommand('workbench.action.reloadWindow');
}

/**
 * @param {vscode.ExtensionContext} context
 * @param {boolean} enable
 */
async function applySettings(context, enable) {
  const conf = vscode.workspace.getConfiguration();
  const G = vscode.ConfigurationTarget.Global;
  if (enable) {
    /** @type {Record<string, unknown>} key -> previous value (undefined = unset) */
    const changed = context.globalState.get(CHANGED_KEY, {});
    const theme = conf.inspect('workbench.colorTheme');
    const current = theme && (theme.globalValue || theme.defaultValue);
    if (!String(current).startsWith('uwu ')) {
      if (!('workbench.colorTheme' in changed)) changed['workbench.colorTheme'] = theme && theme.globalValue;
      await conf.update('workbench.colorTheme', 'uwu strawberry-milk night', G);
    }
    for (const [key, value] of Object.entries(KAWAII_SETTINGS)) {
      const info = conf.inspect(key);
      const mine = key in changed;
      if (info && info.globalValue !== undefined && !mine && key !== 'workbench.iconTheme') continue;
      if (!mine) changed[key] = info && info.globalValue;
      await conf.update(key, value, G);
    }
    await context.globalState.update(CHANGED_KEY, changed);
  } else {
    const changed = context.globalState.get(CHANGED_KEY, {});
    for (const [key, previous] of Object.entries(changed)) await conf.update(key, previous, G);
    await context.globalState.update(CHANGED_KEY, undefined);
  }
}

/** After a VS Code update the patch is gone; offer to put it back. */
async function checkKawaiiAfterUpdate(context) {
  if (!context.globalState.get(ENABLED_KEY)) return;
  try {
    if (kawaii.isPatched(vscode.env.appRoot)) return;
  } catch {
    return;
  }
  const pick = await vscode.window.showInformationMessage(
    'uwu: VS Code was updated, so the Kawaii Workbench needs to be re-applied ✿',
    'Re-apply',
    'Not now',
  );
  if (pick === 'Re-apply') setKawaii(context, true);
}

// ─────────────────────────────── sakura petals ───────────────────────────────

// How the petals work: one decoration's ::before becomes a single big layer
// behind the text (click-through) that is attached to the *document*, like
// wallpaper: it is anchored to a line near the middle of the view and shifted
// up by that many line heights (CSS `lh`), so wherever it is anchored the
// petals land on exactly the same spot in the document. Re-anchoring while you
// scroll therefore never moves a single petal, and because the anchor sits half
// a screen from either edge it can't scroll out of view (and vanish) before the
// update arrives. The petal SVGs animate themselves (fall, sway, spin, wind).
const SPAN = 120; // lines the layer reaches above and below its anchor

class Petals {
  constructor() {
    this.type = undefined;
    /** @type {WeakMap<vscode.TextEditor, number>} last anchor per editor */
    this.anchors = new WeakMap();
    this.disposables = [
      vscode.window.onDidChangeVisibleTextEditors(() => this.applyAll()),
      vscode.window.onDidChangeTextEditorVisibleRanges((e) => this.apply(e.textEditor)),
      vscode.window.onDidChangeActiveColorTheme(() => this.rebuild()),
      vscode.workspace.onDidChangeTextDocument((e) => {
        for (const ed of vscode.window.visibleTextEditors) if (ed.document === e.document) this.apply(ed, true);
      }),
    ];
    this.rebuild();
  }

  rebuild() {
    if (this.type) this.type.dispose();
    this.type = undefined;
    this.anchors = new WeakMap();
    if (cfg().get('petals.enabled')) {
      const which = cfg().get('petals.layers');
      const layers = which === 'far' ? petalLayers.slice(2) : which === 'noFront' ? petalLayers.slice(1) : petalLayers;
      // pale petals almost vanish on a light background, so give them a boost there
      const kind = vscode.window.activeColorTheme.kind;
      const light = kind === vscode.ColorThemeKind.Light || kind === vscode.ColorThemeKind.HighContrastLight;
      const base = Math.max(0, Math.min(1, Number(cfg().get('petals.opacity')) || 0));
      const opacity = light ? Math.min(1, base * 1.3) : base;
      // "edges": keep the petals out of the code. Measured in text columns (ch),
      // they're invisible over the first ~24 columns, fade in by ~48 and are at
      // full strength past ~72, where lines usually end.
      const mask =
        cfg().get('petals.area') === 'everywhere'
          ? 'none'
          : 'linear-gradient(to right, transparent 0, transparent 24ch, rgba(0,0,0,.35) 48ch, black 72ch)';
      // the heavy part lives once in the decoration type; each anchor only
      // changes top / height / background-position (see apply)
      const shared = [
        'none',
        'position: absolute',
        'left: 0',
        'width: 100vw',
        'z-index: -1',
        'pointer-events: none',
        `opacity: ${opacity}`,
        `background-image: ${layers.map((l) => l.url).join(', ')}`,
        `background-size: ${layers.map((l) => `${l.width}px ${l.height}px`).join(', ')}`,
        'background-repeat: repeat',
        `-webkit-mask-image: ${mask}`,
        `mask-image: ${mask}`,
      ].join('; ');
      this.layerCount = layers.length;
      this.type = vscode.window.createTextEditorDecorationType({
        before: { contentText: '\u200b', textDecoration: shared },
        rangeBehavior: vscode.DecorationRangeBehavior.ClosedClosed,
      });
    }
    this.applyAll();
  }

  applyAll() {
    for (const ed of vscode.window.visibleTextEditors) this.apply(ed, true);
  }

  /**
   * @param {vscode.TextEditor} editor
   * @param {boolean} [force] re-apply even if the anchor didn't change
   */
  apply(editor, force) {
    if (!this.type || editor.document.uri.scheme === 'output') return;
    const lineCount = editor.document.lineCount;
    const vis = editor.visibleRanges;
    const top = vis.length ? vis[0].start.line : 0;
    const bottom = vis.length ? vis[vis.length - 1].end.line : 0;
    const anchor = Math.min(lineCount - 1, Math.floor((top + bottom) / 2));
    if (!force && this.anchors.get(editor) === anchor) return;
    this.anchors.set(editor, anchor);
    // the layer starts `above` lines over the anchor; its background is shifted
    // by the line it starts on, which keeps every petal glued to the document
    const above = Math.min(anchor, SPAN);
    const start = anchor - above;
    const pos = `0 calc(${-start} * 1lh)`;
    const css = [
      'none',
      `top: calc(${-above} * 1lh)`,
      // reach SPAN lines below the anchor, and past the end of a short file
      `height: calc(${above + SPAN} * 1lh + 100vh)`,
      `background-position: ${Array(this.layerCount).fill(pos).join(', ')}`,
    ].join('; ');
    editor.setDecorations(this.type, [
      { range: new vscode.Range(anchor, 0, anchor, 0), renderOptions: { before: { contentText: '\u200b', textDecoration: css } } },
    ]);
  }

  dispose() {
    if (this.type) this.type.dispose();
    this.disposables.forEach((d) => d.dispose());
  }
}

// ─────────────────────────────── sparkle burst ───────────────────────────────

let burstCount = 0;

/** A one-shot animated SVG: hearts, sparkles and petals flying out and fading. */
function burstSvg(nonce) {
  const colors = ['#ff8fc8', '#c7a2ff', '#8ff5cf', '#ffe59a', '#9fd8ff', '#ff6fb5'];
  const shapes = {
    heart: 'M0 3.5 C-5 -1 -4 -6 0 -3.5 C4 -6 5 -1 0 3.5 Z',
    star: 'M0 -6 L1.5 -1.5 L6 0 L1.5 1.5 L0 6 L-1.5 1.5 L-6 0 L-1.5 -1.5 Z',
    petal: 'M0 -4 C1 -6 3 -6.5 4 -4.5 C5 -2 4 2 0 6 C-4 2 -5 -2 -4 -4.5 C-3 -6.5 -1 -6 0 -4 Z',
  };
  const kinds = ['heart', 'star', 'petal', 'star', 'heart', 'petal'];
  const n = 18;
  const dur = 1.3;
  let parts = '';
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 + (i % 2 ? 0.2 : -0.1);
    const dist = 62 + ((i * 37) % 34);
    const dx = (Math.cos(a) * dist).toFixed(1);
    const dy = (Math.sin(a) * dist - 10).toFixed(1);
    const s = (1.5 + ((i * 13) % 7) / 5).toFixed(2);
    const rot = ((i * 73) % 360) - 180;
    const delay = ((i % 4) * 0.03).toFixed(2);
    parts +=
      `<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.65;1" dur="${dur}s" begin="${delay}s" fill="freeze"/>` +
      `<animateTransform attributeName="transform" type="translate" from="0 0" to="${dx} ${dy}" dur="${dur}s" begin="${delay}s" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .3 1" fill="freeze"/>` +
      `<g><animateTransform attributeName="transform" type="rotate" from="0" to="${rot}" dur="${dur}s" begin="${delay}s" fill="freeze"/>` +
      `<path transform="scale(${s})" d="${shapes[kinds[i % kinds.length]]}" fill="${colors[i % colors.length]}"/></g></g>`;
  }
  const ring =
    '<circle r="4" fill="none" stroke="#ff8fc8" stroke-width="3" opacity=".9">' +
    '<animate attributeName="r" from="4" to="58" dur=".75s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .3 1"/>' +
    '<animate attributeName="opacity" from=".9" to="0" dur=".75s" fill="freeze"/>' +
    '<animate attributeName="stroke-width" from="3" to=".5" dur=".75s" fill="freeze"/></circle>';
  // the nonce makes every burst a brand-new image, so its animation always starts from 0
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" width="200" height="200">` +
    `<!-- ${nonce} -->${ring}${parts}</svg>`
  );
}

/** @param {vscode.TextEditor} editor */
function burst(editor) {
  const svg = burstSvg(`${Date.now()}-${burstCount++}`);
  const url = `url("data:image/svg+xml,${encodeURIComponent(svg).replace(/'/g, '%27')}")`;
  const css = [
    'none',
    'position: absolute',
    'width: 240px',
    'height: 240px',
    'transform: translate(-50%, -50%)',
    'margin-top: 0.6em',
    'z-index: 20',
    'pointer-events: none',
    `background: ${url} center / contain no-repeat`,
  ].join('; ');
  const type = vscode.window.createTextEditorDecorationType({
    after: { contentText: '​', textDecoration: css },
  });
  const pos = editor.selection.active;
  editor.setDecorations(type, [new vscode.Range(pos, pos)]);
  setTimeout(() => type.dispose(), 1600);
}

// ─────────────────────────────── gutter hearts ───────────────────────────────

class GutterHearts {
  /** @param {vscode.ExtensionContext} context */
  constructor(context) {
    this.type = vscode.window.createTextEditorDecorationType({
      gutterIconPath: vscode.Uri.joinPath(context.extensionUri, 'media', 'heart.svg'),
      gutterIconSize: '70%',
    });
    /** @type {Map<string, Set<number>>} uri -> changed line numbers */
    this.lines = new Map();
    this.disposables = [
      vscode.workspace.onDidChangeTextDocument((e) => this.onChange(e)),
      vscode.workspace.onDidCloseTextDocument((doc) => this.lines.delete(doc.uri.toString())),
      vscode.window.onDidChangeVisibleTextEditors(() => this.refreshAll()),
    ];
  }

  /** @param {vscode.TextDocumentChangeEvent} e */
  onChange(e) {
    if (e.document.uri.scheme !== 'file' && e.document.uri.scheme !== 'untitled') return;
    if (!e.contentChanges.length) return;
    const key = e.document.uri.toString();
    let set = this.lines.get(key) || new Set();
    // apply bottom-up so earlier changes don't shift later ones
    const changes = [...e.contentChanges].sort((a, b) => b.range.start.line - a.range.start.line);
    for (const ch of changes) {
      const start = ch.range.start.line;
      const end = ch.range.end.line;
      const added = (ch.text.match(/\n/g) || []).length;
      const delta = added - (end - start);
      const next = new Set();
      for (const l of set) {
        if (l < start) next.add(l);
        else if (l > end) next.add(l + delta);
      }
      for (let l = start; l <= start + added; l++) next.add(l);
      set = next;
    }
    // undo back to the saved state? then nothing is changed any more
    if (!e.document.isDirty) set.clear();
    this.lines.set(key, set);
    this.refresh(e.document);
  }

  /** @param {vscode.TextDocument} doc */
  clear(doc) {
    this.lines.delete(doc.uri.toString());
    this.refresh(doc);
  }

  clearAll() {
    this.lines.clear();
    this.refreshAll();
  }

  refreshAll() {
    for (const ed of vscode.window.visibleTextEditors) this.refresh(ed.document);
  }

  /** @param {vscode.TextDocument} doc */
  refresh(doc) {
    const on = cfg().get('gutterHearts');
    const set = this.lines.get(doc.uri.toString());
    const ranges = on && set ? [...set].filter((l) => l < doc.lineCount).map((l) => new vscode.Range(l, 0, l, 0)) : [];
    for (const ed of vscode.window.visibleTextEditors) if (ed.document === doc) ed.setDecorations(this.type, ranges);
  }

  dispose() {
    this.type.dispose();
    this.disposables.forEach((d) => d.dispose());
  }
}

// ─────────────────────────────── error kaomoji ───────────────────────────────

class ErrorKaomoji {
  constructor() {
    this.type = vscode.window.createTextEditorDecorationType({
      after: {
        color: new vscode.ThemeColor('uwu.kaomojiForeground'),
        margin: '0 0 0 2.5em',
        fontStyle: 'normal',
      },
    });
    this.disposables = [
      vscode.languages.onDidChangeDiagnostics(() => this.refreshAll()),
      vscode.window.onDidChangeVisibleTextEditors(() => this.refreshAll()),
    ];
    this.refreshAll();
  }

  refreshAll() {
    for (const ed of vscode.window.visibleTextEditors) this.refresh(ed);
  }

  /** @param {vscode.TextEditor} editor */
  refresh(editor) {
    if (!cfg().get('errorKaomoji')) return editor.setDecorations(this.type, []);
    const seen = new Set();
    const decos = [];
    for (const d of vscode.languages.getDiagnostics(editor.document.uri)) {
      if (d.severity !== vscode.DiagnosticSeverity.Error) continue;
      const line = d.range.end.line;
      if (seen.has(line) || line >= editor.document.lineCount) continue;
      seen.add(line);
      const end = editor.document.lineAt(line).range.end;
      decos.push({
        range: new vscode.Range(end, end),
        renderOptions: { after: { contentText: ERROR_FACES[line % ERROR_FACES.length] } },
        hoverMessage: `${ERROR_FACES[line % ERROR_FACES.length]} ${d.message}`,
      });
    }
    editor.setDecorations(this.type, decos);
  }

  dispose() {
    this.type.dispose();
    this.disposables.forEach((d) => d.dispose());
  }
}

// ─────────────────────────────── status-bar mascot ───────────────────────────────

class Mascot {
  constructor() {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 1000);
    this.item.command = 'uwu.togglePetals';
    this.frame = 0;
    this.partyUntil = 0;
    this.timer = setInterval(() => {
      this.frame++;
      this.render();
    }, 900);
    this.disposables = [vscode.languages.onDidChangeDiagnostics(() => this.render())];
    this.refresh();
  }

  refresh() {
    if (cfg().get('mascot')) {
      this.render();
      this.item.show();
    } else this.item.hide();
  }

  celebrate() {
    this.partyUntil = Date.now() + 2200;
    this.render();
  }

  counts() {
    let errors = 0;
    let warnings = 0;
    for (const [, diags] of vscode.languages.getDiagnostics()) {
      for (const d of diags) {
        if (d.severity === vscode.DiagnosticSeverity.Error) errors++;
        else if (d.severity === vscode.DiagnosticSeverity.Warning) warnings++;
      }
    }
    return { errors, warnings };
  }

  render() {
    if (!cfg().get('mascot')) return;
    const { errors, warnings } = this.counts();
    const petals = cfg().get('petals.enabled') ? 'on' : 'off';
    let face;
    let tip;
    if (Date.now() < this.partyUntil) {
      face = KAOMOJI.party;
      tip = 'saved! ✧';
    } else if (errors) {
      face = `${KAOMOJI.sad[this.frame % 4]} ${errors}`;
      tip = `${errors} error${errors > 1 ? 's' : ''}... you've got this ♡`;
    } else if (warnings) {
      face = `${KAOMOJI.worried[this.frame % 4]} ${warnings}`;
      tip = `${warnings} warning${warnings > 1 ? 's' : ''}, almost perfect!`;
    } else {
      face = KAOMOJI.happy[this.frame % 4];
      tip = 'no errors, you are doing amazing ♡';
    }
    this.item.text = face;
    this.item.tooltip = `uwu-code: ${tip}\nclick to turn petals ${petals === 'on' ? 'off' : 'on'}`;
  }

  dispose() {
    clearInterval(this.timer);
    this.item.dispose();
    this.disposables.forEach((d) => d.dispose());
  }
}

// ─────────────────────────────── settings bridge ───────────────────────────────

// The Kawaii Workbench script runs in the window, where it can't read settings.
// This hidden status-bar item carries them over (the stylesheet hides it).
class Bridge {
  constructor() {
    this.item = vscode.window.createStatusBarItem('uwu.bridge', vscode.StatusBarAlignment.Left, -10000);
    this.item.name = 'uwu-code settings bridge';
    this.refresh();
    this.item.show();
  }

  refresh() {
    const c = vscode.workspace.getConfiguration('uwu.workbench');
    const flag = (k) => (c.get(k) ? 1 : 0);
    this.item.text = `uwu:splash=${flag('splash')};clicks=${flag('clickBursts')};typing=${flag('typingSparkles')};mascot=${flag('mascot')};confetti=${flag('confetti')}`;
  }

  dispose() {
    this.item.dispose();
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
