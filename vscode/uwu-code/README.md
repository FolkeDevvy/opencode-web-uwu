# ♡ uwu-code ✧

Super duper kawaii VS Code. It's the same pastel palette as the uwu opencode themes, with sakura
petals drifting behind your code.

![uwu-code demo](https://raw.githubusercontent.com/FolkeDevvy/opencode-web-uwu/main/vscode/screenshots/uwu-code-demo.gif)

## Features

- **Two colour themes:** 🌙 *uwu strawberry-milk night* and 🌸 *uwu sakura cream day*. They cover
  the whole workbench, the terminal, diffs, and syntax and semantic highlighting.
- **Sakura petals in the editor:** animated petals fall, sway, spin and blow in the wind
  *behind* your code. They keep out of the first ~24 text columns and drift through the
  empty space on the right, scroll smoothly with the document, and are click-through.
- **Sparkle burst on save:** hearts, stars and petals pop out of your cursor ✧
- **Gutter hearts:** a little 💗 marks every line you changed since your last save.
- **Error kaomoji:** lines with errors get a sad face at the end `(╥﹏╥)`.
- **Status-bar mascot:** a kaomoji that blinks, worries about warnings, cries over errors and
  parties when you save `(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧`. Click it to toggle the petals.

## Settings

| Setting | Default | |
| --- | --- | --- |
| `uwu.petals.enabled` | `true` | Petals behind the code |
| `uwu.petals.opacity` | `0.7` | 0 to 1 (automatically boosted a bit on light themes) |
| `uwu.petals.area` | `edges` | `edges` keeps petals out of your code (they fade in from ~24 to ~72 text columns); `everywhere` puts them behind all the text |
| `uwu.petals.layers` | `noFront` | `far` (lightest), `noFront` (near + far), `all` (adds big soft petals up front; heavier) |
| `uwu.sparkleOnSave` | `true` | Burst on save |
| `uwu.gutterHearts` | `true` | Hearts on changed lines |
| `uwu.errorKaomoji` | `true` | Sad faces on error lines |
| `uwu.mascot` | `true` | Status-bar mascot |

Commands (in the Command Palette, under **uwu**): *Toggle Sakura Petals*, *Sparkle! ✧*, and
*Clear Gutter Hearts*.

The colour of the error kaomoji can be themed with `uwu.kaomojiForeground`.

## How it works (and the fine print)

VS Code extensions can only draw where VS Code lets them. Everything here uses editor decorations,
so the petals and effects live **inside the editor**, not over the sidebar or panels.

The petals and the burst use a well-known decoration trick: VS Code places decoration style values
directly into CSS, which lets a decoration become a free-floating, click-through layer. Popular
extensions rely on it, but it isn't officially supported, so a future VS Code update could break
it. Every effect has its own on/off setting.

The petals are one layer pinned to the document with line-height offsets, so they scroll with
your code and never re-anchor visibly. With word wrap or folded code, they may shift slightly when
you scroll past a wrapped or folded spot.

The petals are self-animating SVGs, and the browser re-paints them every frame on the CPU.
The default (`noFront`) holds a steady 60fps even on a GPU-less test machine. `all` looks dreamier
but costs some frame rate on slower machines.
