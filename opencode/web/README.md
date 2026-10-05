# ♡ uwu for the opencode web UI ✧

A Firefox `userContent.css` that makes the **opencode v2 web UI** (`@opencode/cli` 2.x)
super duper kawaii. No extensions needed.

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
- **Fun animations:**
  - new messages pop in
  - the composer gets a rainbow border while you type
  - the send button does a heartbeat
  - your chat bubble shimmers as it arrives
  - the title-bar text shimmers when you hover it
  - the ✿ before headings spins
  - icon buttons wiggle, the code-block dots twinkle, and home rows slide in
- Polka-dot background, a welcome banner on the home page, and a heart cursor
- Respects `prefers-reduced-motion`, which turns off all animation

## Install (Firefox)

> **Quick way:** `./uwu.sh install web` from the repo root does all of this (for every Firefox profile), and
> `./uwu.sh uninstall web` takes it back out.

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

## Performance

Everything animates on the compositor (`transform` and `opacity` only) or plays briefly, so
nothing repaints the page every frame:
- **No backdrop blur anywhere:** opencode keeps an invisible blurred drop-zone over the chat, and
  any animation behind a blur forces it to be recomputed every frame.
- **Main-thread effects run briefly:** the bubble shimmer plays only as a message arrives, and the
  title-bar rainbow only on hover.

There used to be falling sakura petals in the background. They were removed because they
distracted from the chat.

## Fonts offline?

The theme loads Nunito and Fira Code from Google Fonts. If you'd rather not fetch
anything, delete the `@import` line and install the fonts locally. The font stack falls back to
`M PLUS Rounded 1c`, `Quicksand`, `Varela Round`, and then your system UI font.
