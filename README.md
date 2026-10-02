# ♡ opencode-web-uwu ✧

A super duper kawaii theme for the **OpenCode v2 web UI** (`@opencode/cli` 2.x), applied
as a Firefox `userContent.css`. No extensions needed.

| 🌙 Strawberry-milk night | 🌸 Sakura cream day |
| --- | --- |
| ![dark session](screenshots/session-dark.png) | ![light session](screenshots/session-light.png) |
| ![dark home](screenshots/home-dark.png) | ![light dialog](screenshots/dialog-light.png) |

## What you get

- Pastel pink / lavender / mint palette for **both** dark and light mode (follows OpenCode's own scheme toggle)
- Rounded **Nunito** font and **Fira Code** for code
- Gradient chat bubbles, an "opencode-chan" badge on replies, and ♡ list bullets
- Pastel syntax highlighting and "window dots" on code blocks
- Glowing rounded composer, gradient send/connect buttons, and bouncy hover effects
- Polka-dot background, a welcome banner on the home page, and a heart cursor
- Respects `prefers-reduced-motion`

## Install (Firefox)

1. Open `about:config`, then set
   `toolkit.legacyUserProfileCustomizations.stylesheets` → `true`.
2. Open `about:profiles`. Under the profile you use, click **Open Directory**
   next to *Root Directory*.
3. Create a folder named `chrome` there if it doesn't exist.
4. Copy [`chrome/userContent.css`](chrome/userContent.css) into that folder.
   If you already have a `userContent.css`, paste this file's contents at the end of it.
   Keep the `@import` line at the very top of the file.
5. Restart Firefox, then open your OpenCode web UI (`opencode serve`, or wherever
   your OpenCode server runs).

> **Tip:** You can use a dedicated profile for OpenCode, e.g.
> `firefox -P opencode --new-instance http://127.0.0.1:4096`.

## How it's scoped

All rules are nested under `:root:has(#oc-theme-preload-script)`. Only the OpenCode
web app ships that script tag, so the theme follows OpenCode to any host or port and leaves
other sites alone. It needs Firefox 121 or later for `:has()` and CSS nesting.

The theme mostly overrides OpenCode v2's own design tokens (`--v2-*`, `--syntax-*`), so
it should survive most UI updates.

## Fonts offline?

The theme loads Nunito and Fira Code from Google Fonts. If you'd rather not fetch
anything, delete the `@import` line and install the fonts locally. The font stack falls back to
`M PLUS Rounded 1c`, `Quicksand`, `Varela Round`, and then your system UI font.
