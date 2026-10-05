// ♡ uwu IDE ✧ installs / removes the Kawaii Workbench in VS Code itself.
//
// VS Code's extension API can't restyle the window, so this adds our stylesheet
// and script to VS Code's own workbench page (the same technique "custom CSS"
// extensions use). It is opt-in, fully reversible, and keeps backups:
//   1. copy ./workbench (css, script, fonts) next to workbench.html
//   2. add three lines to workbench.html, between marker comments
//   3. update that file's checksum in product.json, so VS Code doesn't report
//      its installation as corrupt
// When VS Code's files aren't writable (a system install), everything is staged
// in the extension's storage and the user gets a one-line sudo command instead.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const START = '<!-- uwu-kawaii:start -->';
const END = '<!-- uwu-kawaii:end -->';
const DIR = 'uwu-kawaii';

function locate(appRoot) {
  const out = path.join(appRoot, 'out');
  for (const rel of ['vs/code/electron-browser/workbench/workbench.html', 'vs/code/electron-sandbox/workbench/workbench.html']) {
    const file = path.join(out, rel);
    if (fs.existsSync(file)) {
      return { html: file, htmlDir: path.dirname(file), checksumKey: rel, product: path.join(appRoot, 'product.json') };
    }
  }
  throw new Error(`couldn't find VS Code's workbench.html under ${out}`);
}

const checksum = (text) => crypto.createHash('sha256').update(text).digest('base64').replace(/=+$/, '');

function strip(html) {
  return html.replace(new RegExp(`\\s*${START}[\\s\\S]*?${END}`, 'g'), '');
}

function inject(html) {
  const clean = strip(html);
  const head = `${START}<link rel="stylesheet" href="./${DIR}/uwu-kawaii-assets.css"><link rel="stylesheet" href="./${DIR}/uwu-kawaii.css">${END}`;
  const body = `${START}<script src="./${DIR}/uwu-kawaii.js"></script>${END}`;
  if (!clean.includes('</head>') || !clean.includes('</html>')) throw new Error('workbench.html has an unexpected shape');
  return clean.replace('</head>', `\t${head}\n\t</head>`).replace('</html>', `\t${body}\n</html>`);
}

const isPatched = (appRoot) => fs.readFileSync(locate(appRoot).html, 'utf8').includes(START);

/** True when the copy inside VS Code matches this extension's workbench files (false after an uwu-code update). */
function isCurrent(appRoot, sourceDir) {
  const target = path.join(locate(appRoot).htmlDir, DIR);
  const same = (from, to) => fs.readdirSync(from, { withFileTypes: true }).every((e) => {
    const a = path.join(from, e.name);
    const b = path.join(to, e.name);
    if (e.isDirectory()) return fs.existsSync(b) && same(a, b);
    return fs.existsSync(b) && fs.readFileSync(a).equals(fs.readFileSync(b));
  });
  return same(sourceDir, target);
}

function productWith(productText, key, html) {
  const product = JSON.parse(productText);
  if (product.checksums && key in product.checksums) product.checksums[key] = checksum(html);
  return JSON.stringify(product, null, '\t');
}

/** Work out every file we'd write, without touching anything yet. */
function plan(appRoot, sourceDir, enable) {
  const loc = locate(appRoot);
  const html = fs.readFileSync(loc.html, 'utf8');
  const nextHtml = enable ? inject(html) : strip(html);
  const product = fs.readFileSync(loc.product, 'utf8');
  return {
    loc,
    enable,
    sourceDir,
    html: nextHtml,
    product: productWith(product, loc.checksumKey, nextHtml),
    originalHtml: html,
    originalProduct: product,
  };
}

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    const a = path.join(from, entry.name);
    const b = path.join(to, entry.name);
    if (entry.isDirectory()) copyDir(a, b);
    else fs.copyFileSync(a, b);
  }
}

/** Apply a plan directly. Throws EACCES/EPERM/EROFS if VS Code's files aren't writable. */
function apply(p) {
  const { loc } = p;
  const target = path.join(loc.htmlDir, DIR);
  // keep the originals once, the first time we ever touch them
  for (const [file, text] of [[loc.html, p.originalHtml], [loc.product, p.originalProduct]]) {
    if (!fs.existsSync(`${file}.uwu-backup`) && !text.includes(START)) fs.writeFileSync(`${file}.uwu-backup`, text);
  }
  if (p.enable) copyDir(p.sourceDir, target);
  else fs.rmSync(target, { recursive: true, force: true });
  fs.writeFileSync(loc.html, p.html);
  fs.writeFileSync(loc.product, p.product);
}

/** Stage a plan in a writable folder and return a shell script that applies it with sudo. */
function stage(p, stagingDir) {
  const { loc } = p;
  fs.rmSync(stagingDir, { recursive: true, force: true });
  fs.mkdirSync(stagingDir, { recursive: true });
  if (p.enable) copyDir(p.sourceDir, path.join(stagingDir, DIR));
  fs.writeFileSync(path.join(stagingDir, 'workbench.html'), p.html);
  fs.writeFileSync(path.join(stagingDir, 'product.json'), p.product);
  const q = (s) => `'${s.replace(/'/g, `'\\''`)}'`;
  const target = path.join(loc.htmlDir, DIR);
  const lines = [
    '#!/bin/sh',
    '# uwu-code: apply the Kawaii Workbench change to VS Code (generated; safe to re-run)',
    'set -e',
    `[ -f ${q(`${loc.html}.uwu-backup`)} ] || cp ${q(loc.html)} ${q(`${loc.html}.uwu-backup`)}`,
    `[ -f ${q(`${loc.product}.uwu-backup`)} ] || cp ${q(loc.product)} ${q(`${loc.product}.uwu-backup`)}`,
    `rm -rf ${q(target)}`,
    ...(p.enable ? [`cp -r ${q(path.join(stagingDir, DIR))} ${q(target)}`] : []),
    `cp ${q(path.join(stagingDir, 'workbench.html'))} ${q(loc.html)}`,
    `cp ${q(path.join(stagingDir, 'product.json'))} ${q(loc.product)}`,
    `echo ${q(p.enable ? 'uwu IDE installed ♡ now reload VS Code' : 'Kawaii Workbench removed. Now reload VS Code')}`,
  ];
  const script = path.join(stagingDir, 'apply.sh');
  fs.writeFileSync(script, lines.join('\n') + '\n', { mode: 0o755 });
  return script;
}

module.exports = { locate, isPatched, isCurrent, plan, apply, stage, inject, strip, checksum, START };
