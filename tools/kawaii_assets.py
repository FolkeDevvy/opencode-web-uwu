#!/usr/bin/env python3
"""Generate the drawn assets for uwu-code's Kawaii Workbench and file icons.

Writes:
  vscode/uwu-code/workbench/uwu-kawaii-assets.css   CSS variables holding the
      activity-bar icons, window petals, mascot and logo as data URIs
  vscode/uwu-code/fileicons/                        the "uwu cuties" file icon theme
  terminal/uwu-term/renderer/assets.css             mascot, logo and petals for uwu-term

    python3 tools/kawaii_assets.py
"""
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from petals import STATIC_LAYERS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "vscode" / "uwu-code"


def data_uri(svg):
    return "url(\"data:image/svg+xml," + urllib.parse.quote(svg, safe=" =:/;,.-_()'#") .replace("#", "%23") + "\")"


def svg(body, size=24, extra=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" {extra}>{body}</svg>'


# ─────────────────────────── activity bar icons ───────────────────────────
# Drawn as single-colour shapes; the CSS uses them as masks so they take the
# theme colour (and gradients) of the item they sit in.
S = 'fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
ACTIVITY = {
    # folder with a heart on it
    "explorer": svg(
        f'<path {S} d="M3 7.5a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<path fill="#000" d="M12 16.6c-2.3-1.6-3.2-2.7-3.2-3.8 0-.9.7-1.6 1.6-1.6.7 0 1.2.4 1.6 1 .4-.6.9-1 1.6-1 .9 0 1.6.7 1.6 1.6 0 1.1-.9 2.2-3.2 3.8z"/>'
    ),
    # magnifying glass with a sparkle in the lens
    "search": svg(
        f'<circle {S} cx="10.5" cy="10.5" r="6"/><path {S} d="M15 15l5 5"/>'
        '<path fill="#000" d="M10.5 7.2l.8 2.5 2.5.8-2.5.8-.8 2.5-.8-2.5-2.5-.8 2.5-.8z"/>'
    ),
    # branch with heart nodes
    "scm": svg(
        f'<path {S} d="M7 6v12M7 13c0-3 2-4.5 5-4.5h2.5"/>'
        '<path fill="#000" d="M7 7.6C5.3 6.4 4.7 5.6 4.7 4.8c0-.7.5-1.2 1.2-1.2.5 0 .9.3 1.1.7.2-.4.6-.7 1.1-.7.7 0 1.2.5 1.2 1.2 0 .8-.6 1.6-2.3 2.8zM7 21.6c-1.7-1.2-2.3-2-2.3-2.8 0-.7.5-1.2 1.2-1.2.5 0 .9.3 1.1.7.2-.4.6-.7 1.1-.7.7 0 1.2.5 1.2 1.2 0 .8-.6 1.6-2.3 2.8zM17.3 10.3c-1.7-1.2-2.3-2-2.3-2.8 0-.7.5-1.2 1.2-1.2.5 0 .9.3 1.1.7.2-.4.6-.7 1.1-.7.7 0 1.2.5 1.2 1.2 0 .8-.6 1.6-2.3 2.8z"/>'
    ),
    # play button with bunny ears
    "run": svg(
        f'<path {S} d="M8.5 6.5C7.8 3.6 8.4 2 9.4 2.2s1.1 2.4.6 4.6M14 6.8c.3-2.6 1.3-4 2.2-3.7.9.3.6 2.3-.6 4.3"/>'
        f'<rect {S} x="4" y="7" width="16" height="13" rx="6"/><path fill="#000" d="M10.5 10.6v5.8l4.6-2.9z"/>'
    ),
    # gift box with a bow
    "extensions": svg(
        f'<rect {S} x="4" y="9" width="16" height="11" rx="2.5"/><path {S} d="M3 9h18M12 9v11"/>'
        f'<path {S} d="M12 9C10 5 6.5 5.5 7.4 7.6 8 9 12 9 12 9zM12 9c2-4 5.5-3.5 4.6-1.4C16 9 12 9 12 9z"/>'
    ),
    # cat face
    "accounts": svg(
        f'<path {S} d="M5 9.5 4.6 3.8l4.6 2.6a8.3 8.3 0 0 1 5.6 0l4.6-2.6L19 9.5c1 1.4 1.5 3 1.5 4.6 0 4-3.8 6.4-8.5 6.4s-8.5-2.4-8.5-6.4c0-1.6.5-3.2 1.5-4.6z"/>'
        '<circle cx="9" cy="13" r="1.2" fill="#000"/><circle cx="15" cy="13" r="1.2" fill="#000"/>'
        f'<path {S} d="M10.7 16.2c.7.6 1.9.6 2.6 0"/>'
    ),
    # sakura blossom (instead of a gear)
    "settings": svg(
        "".join(
            f'<path {S} transform="rotate({a} 12 12)" d="M12 11.2c-1.6-1.4-2.6-3-2.4-4.6.2-1.4 1.5-2.4 2.4-1.6.9-.8 2.2.2 2.4 1.6.2 1.6-.8 3.2-2.4 4.6z"/>'
            for a in (0, 72, 144, 216, 288)
        )
        + '<circle cx="12" cy="12" r="1.6" fill="#000"/>'
    ),
}

# ─────────────────────────── mascot & logo ───────────────────────────
MASCOT = svg(
    # a round mochi bunny with blush, sitting on a little petal
    '<defs><radialGradient id="b" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#ffe0ef"/></radialGradient></defs>'
    '<ellipse cx="60" cy="112" rx="34" ry="6" fill="#ff8fc8" opacity=".25"/>'
    '<path d="M38 40C30 14 36 2 44 4s10 18 6 34M82 40c8-26 2-38-6-36s-10 18-6 34" fill="url(#b)" stroke="#ff8fc8" stroke-width="3"/>'
    '<path d="M42 30c-3-12-1-19 3-19M78 30c3-12 1-19-3-19" stroke="#ffb3d9" stroke-width="4" stroke-linecap="round" fill="none"/>'
    '<ellipse cx="60" cy="74" rx="44" ry="38" fill="url(#b)" stroke="#ff8fc8" stroke-width="3"/>'
    '<ellipse cx="38" cy="82" rx="7" ry="4.5" fill="#ff9fcf" opacity=".7"/><ellipse cx="82" cy="82" rx="7" ry="4.5" fill="#ff9fcf" opacity=".7"/>'
    '<path d="M44 70c2-4 8-4 10 0M66 70c2-4 8-4 10 0" stroke="#57264c" stroke-width="3.2" stroke-linecap="round" fill="none"/>'
    '<path d="M55 80c2 3 8 3 10 0" stroke="#57264c" stroke-width="3" stroke-linecap="round" fill="none"/>'
    '<path d="M86 38l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" fill="#ffe59a"/>',
    size=120,
)

LOGO = svg(
    '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff9fd0"/><stop offset="1" stop-color="#b98bff"/></linearGradient>'
    '<radialGradient id="p" cx=".5" cy=".75" r=".8"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#ffd1e6"/></radialGradient>'
    '<path id="q" d="M0 -22 C5 -30 17 -33 20 -22 C26 -8 18 14 0 34 C-18 14 -26 -8 -20 -22 C-17 -33 -5 -30 0 -22 Z" transform="translate(0 -44)"/></defs>'
    '<rect x="8" y="8" width="240" height="240" rx="64" fill="url(#g)"/>'
    '<g transform="translate(128 132) rotate(-12)">'
    + "".join(f'<use href="#q" fill="url(#p)" transform="rotate({a})"/>' for a in (0, 72, 144, 216, 288))
    + '<circle r="15" fill="#ff6fb5"/></g>',
    size=256,
)

# a big empty-editor watermark: the mascot on a cloud with sparkles
WATERMARK = svg(
    '<g opacity=".9"><ellipse cx="160" cy="236" rx="120" ry="22" fill="#ff8fc8" opacity=".18"/>'
    '<path d="M60 220c-30 0-34-40-6-44 0-30 40-38 54-16 14-26 60-24 66 6 30-8 52 22 32 44 28 6 18 40-10 40H70c-26 0-30-30-10-30z" fill="#ff8fc8" opacity=".14"/></g>'
    '<g transform="translate(100 60)">' + MASCOT[MASCOT.index(">") + 1:MASCOT.rindex("</svg>")] + "</g>"
    '<g fill="#ffe59a"><path d="M60 70l3 9 9 3-9 3-3 9-3-9-9-3 9-3z"/><path d="M262 120l2 6 6 2-6 2-2 6-2-6-6-2 6-2z"/></g>'
    '<g fill="#c7a2ff"><path d="M250 46l2.5 7.5 7.5 2.5-7.5 2.5-2.5 7.5-2.5-7.5-7.5-2.5 7.5-2.5z"/></g>',
    size=320,
)


# a ribbon bow for the corner of the editor card
BOW = svg(
    '<defs><linearGradient id="r" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffb3d9"/><stop offset="1" stop-color="#ff5fae"/></linearGradient></defs>'
    '<path d="M32 30C20 14 4 12 4 24s16 14 28 6zM32 30c12-16 28-18 28-6s-16 14-28 6z" fill="url(#r)" stroke="#d63d8a" stroke-width="2" stroke-linejoin="round"/>'
    '<path d="M27 33l-7 20 7-4 4 7 3-21M37 33l7 20-7-4-4 7-3-21" fill="url(#r)" stroke="#d63d8a" stroke-width="2" stroke-linejoin="round"/>'
    '<rect x="27" y="24" width="10" height="11" rx="4" fill="#ff8fc8" stroke="#d63d8a" stroke-width="2"/>'
    '<path d="M12 22c2-3 6-4 9-2M43 20c3-2 7-1 9 2" stroke="#fff" stroke-width="2" stroke-linecap="round" fill="none" opacity=".7"/>',
    size=64,
)


def assets_css():
    lines = ["/* Generated by tools/kawaii_assets.py. Do not edit by hand. */", ":root {"]
    for name, s in ACTIVITY.items():
        lines.append(f"  --uwu-icon-{name}: {data_uri(s)};")
    lines.append(f"  --uwu-mascot: {data_uri(MASCOT)};")
    lines.append(f"  --uwu-logo: {data_uri(LOGO)};")
    lines.append(f"  --uwu-watermark: {data_uri(WATERMARK)};")
    lines.append(f"  --uwu-bow: {data_uri(BOW)};")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ─────────────────────────── file icon theme ───────────────────────────
# Each file type is a pastel squircle with a tiny blushing face and a label.
TYPES = {
    # id: (fill, ink, label, extensions, file names, language ids)
    "js": ("#ffe59a", "#8a6a00", "JS", ["js", "mjs", "cjs"], [], ["javascript"]),
    "jsx": ("#ffe59a", "#8a6a00", "JSX", ["jsx"], [], ["javascriptreact"]),
    "ts": ("#9fd8ff", "#1f5f8f", "TS", ["ts", "mts", "cts"], [], ["typescript"]),
    "tsx": ("#9fd8ff", "#1f5f8f", "TSX", ["tsx"], [], ["typescriptreact"]),
    "json": ("#ffd59a", "#8f5a12", "{ }", ["json", "jsonc", "json5"], [], ["json", "jsonc"]),
    "md": ("#c7a2ff", "#5a2fa8", "MD", ["md", "markdown", "mdx"], ["README"], ["markdown"]),
    "css": ("#ff9fcf", "#a3256a", "CSS", ["css", "scss", "sass", "less"], [], ["css", "scss", "less"]),
    "html": ("#ffb79a", "#a64a20", "</>", ["html", "htm", "xml", "svelte", "vue"], [], ["html", "xml"]),
    "py": ("#8ff5cf", "#1d7a5a", "PY", ["py", "pyi", "ipynb"], [], ["python"]),
    "rs": ("#ffb79a", "#8f3f1a", "RS", ["rs"], [], ["rust"]),
    "go": ("#9fe8ff", "#1a6f8a", "GO", ["go"], [], ["go"]),
    "java": ("#ffc0a0", "#8f3f1a", "JV", ["java", "kt", "kts"], [], ["java", "kotlin"]),
    "c": ("#b8c8ff", "#33449a", "C", ["c", "h"], [], ["c"]),
    "cpp": ("#b8c8ff", "#33449a", "C++", ["cpp", "cc", "cxx", "hpp", "hh"], [], ["cpp"]),
    "sh": ("#b8f0a8", "#2f7a1f", "$_", ["sh", "bash", "zsh", "fish", "ps1"], [], ["shellscript", "powershell"]),
    "yaml": ("#ffc9e0", "#a3256a", "YML", ["yml", "yaml", "toml", "ini", "cfg"], [], ["yaml", "toml", "ini"]),
    "lock": ("#d9c9e8", "#5e4a73", "🔒", ["lock"], ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "Cargo.lock"], []),
    "git": ("#ffb3c4", "#a3253f", "GIT", [], [".gitignore", ".gitattributes", ".gitmodules", ".gitkeep"], ["ignore"]),
    "env": ("#ffe59a", "#8a6a00", "ENV", ["env"], [".env", ".env.local", ".env.example"], ["dotenv"]),
    "image": ("#c9f2e6", "#1d7a5a", "IMG", ["png", "jpg", "jpeg", "gif", "webp", "svg", "ico", "bmp"], [], []),
    "txt": ("#f2e6ee", "#6e4a63", "TXT", ["txt", "log"], ["LICENSE", "LICENSE.md", "OFL.txt"], ["plaintext"]),
    "docker": ("#9fd8ff", "#1f5f8f", "🐳", ["dockerfile"], ["Dockerfile", "docker-compose.yml", "compose.yaml"], ["dockerfile"]),
}


def file_svg(fill, ink, label):
    size = 10 if len(label) <= 2 else 8 if len(label) == 3 else 9
    return svg(
        f'<path d="M8 3h11l6 6v17a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3z" fill="{fill}" stroke="{ink}" stroke-width="1.4" stroke-linejoin="round"/>'
        f'<path d="M19 3v4a2 2 0 0 0 2 2h4" fill="none" stroke="{ink}" stroke-width="1.4" stroke-linejoin="round"/>'
        f'<circle cx="10" cy="14" r="1.1" fill="{ink}"/><circle cx="20" cy="14" r="1.1" fill="{ink}"/>'
        f'<path d="M13.6 15.4c.8.8 2 .8 2.8 0" stroke="{ink}" stroke-width="1.1" fill="none" stroke-linecap="round"/>'
        f'<ellipse cx="8.2" cy="16.4" rx="1.6" ry="1" fill="#ff6fb5" opacity=".55"/><ellipse cx="21.8" cy="16.4" rx="1.6" ry="1" fill="#ff6fb5" opacity=".55"/>'
        f'<text x="15" y="26.2" font-family="Nunito, Verdana, sans-serif" font-weight="900" font-size="{size}" text-anchor="middle" fill="{ink}">{label}</text>',
        size=30,
    )


def folder_svg(open_, fill="#ffc9e0", ink="#a3256a", heart="#ff6fb5"):
    body = (
        f'<path d="M3 8a3 3 0 0 1 3-3h6l3 3h9a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z" fill="{fill}" stroke="{ink}" stroke-width="1.4" stroke-linejoin="round"/>'
    )
    if open_:
        body += f'<path d="M3 23l3.4-9a2.5 2.5 0 0 1 2.3-1.6H28a1.5 1.5 0 0 1 1.4 2l-3 8.4a3 3 0 0 1-2.8 2H6a3 3 0 0 1-3-3z" fill="#fff0f7" stroke="{ink}" stroke-width="1.4" stroke-linejoin="round"/>'
        body += f'<path d="M16.5 23.4c-2.6-1.8-3.6-3-3.6-4.3 0-1 .8-1.8 1.8-1.8.8 0 1.4.5 1.8 1.1.4-.6 1-1.1 1.8-1.1 1 0 1.8.8 1.8 1.8 0 1.3-1 2.5-3.6 4.3z" fill="{heart}"/>'
    else:
        body += f'<path d="M15 22c-2.6-1.8-3.6-3-3.6-4.3 0-1 .8-1.8 1.8-1.8.8 0 1.4.5 1.8 1.1.4-.6 1-1.1 1.8-1.1 1 0 1.8.8 1.8 1.8 0 1.3-1 2.5-3.6 4.3z" fill="{heart}"/>'
    return svg(body, size=30)


def write_file_icons():
    out = EXT / "fileicons"
    icons = out / "icons"
    icons.mkdir(parents=True, exist_ok=True)
    theme = {
        "iconDefinitions": {},
        "file": "file", "folder": "folder", "folderExpanded": "folder-open",
        "rootFolder": "root", "rootFolderExpanded": "root-open",
        "fileExtensions": {}, "fileNames": {}, "languageIds": {},
        "hidesExplorerArrows": False,
    }

    def add(name, svg_text):
        (icons / f"{name}.svg").write_text(svg_text)
        theme["iconDefinitions"][name] = {"iconPath": f"./icons/{name}.svg"}

    add("file", file_svg("#ffe4f1", "#a3256a", "♡"))
    add("folder", folder_svg(False))
    add("folder-open", folder_svg(True))
    add("root", folder_svg(False, fill="#d9c4ff", ink="#5a2fa8", heart="#ff8fc8"))
    add("root-open", folder_svg(True, fill="#d9c4ff", ink="#5a2fa8", heart="#ff8fc8"))
    for tid, (fill, ink, label, exts, names, langs) in TYPES.items():
        add(tid, file_svg(fill, ink, label))
        for e in exts:
            theme["fileExtensions"][e] = tid
        for n in names:
            theme["fileNames"][n] = tid
        for lang in langs:
            theme["languageIds"][lang] = tid
    (out / "uwu-icon-theme.json").write_text(json.dumps(theme, indent=2, ensure_ascii=False) + "\n")
    return len(theme["iconDefinitions"])


def terminal_assets_css():
    """The same mascot, logo and petals for uwu-term (terminal/uwu-term)."""
    near, far = STATIC_LAYERS
    return "\n".join([
        "/* Generated by tools/kawaii_assets.py. Do not edit by hand. */",
        ":root {",
        f"  --uwu-mascot: {data_uri(MASCOT)};",
        f"  --uwu-logo: {data_uri(LOGO)};",
        f"  --uwu-petals: {near[0]}, {far[0]};",
        f"  --uwu-petals-size: {near[1]}px {near[2]}px, {far[1]}px {far[2]}px;",
        "}",
    ]) + "\n"


def main():
    term = ROOT / "terminal" / "uwu-term"
    (term / "renderer" / "assets.css").write_text(terminal_assets_css())
    (term / "assets" / "icon.svg").write_text(LOGO)
    print("wrote", term / "renderer" / "assets.css")
    css = EXT / "workbench" / "uwu-kawaii-assets.css"
    css.parent.mkdir(parents=True, exist_ok=True)
    css.write_text(assets_css())
    print("wrote", css)
    print("wrote", write_file_icons(), "file icons")


if __name__ == "__main__":
    main()
