# ♡ uwu-code ✧

**Turn VS Code into uwu IDE.** Run `uwu: Enable Kawaii Workbench` for the full window makeover
(splash screen, candy panels, mascot, sparkles and confetti). See *Kawaii Workbench* below.

Super duper kawaii VS Code, with the same pastel palette as the uwu opencode themes.

![uwu IDE demo](https://raw.githubusercontent.com/FolkeDevvy/opencode-web-uwu/main/vscode/screenshots/uwu-ide-demo.gif)

## Features

- **Two colour themes:** 🌙 *uwu strawberry-milk night* and 🌸 *uwu sakura cream day*. They cover
  the whole workbench, the terminal, diffs, and syntax and semantic highlighting.
- **Sparkle burst on save:** hearts, stars and petals pop out of your cursor ✧
- **Gutter hearts:** a little 💗 marks every line you changed since your last save.
- **Error kaomoji:** lines with errors get a sad face at the end `(╥﹏╥)`.
- **Status-bar mascot:** a kaomoji that blinks, worries about warnings, cries over errors and
  parties when you save `(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧`. Click it for a sparkle burst.

- **uwu cuties file icons:** pastel files with tiny blushing faces, and heart folders.

## Kawaii Workbench

`uwu: Enable Kawaii Workbench` restyles the whole VS Code window into uwu IDE. It adds a boot
splash, floating candy panels, the Nunito UI font, custom activity icons,
candy-pill tabs, a rainbow command palette, a mascot, click bursts, typing sparkles and save
confetti.

VS Code doesn't let extensions do this through its API, so the command adds uwu-code's
stylesheet and script to VS Code's own files. Backups are kept and the file checksum is updated.

- **System installs:** you get a one-line `sudo` command.
- **VS Code updates:** you're offered to re-apply it.
- **Undo:** `uwu: Disable Kawaii Workbench` puts everything back.
- **Snap:** the read-only Snap install isn't supported.
- **Themes:** the restyle only shows while an uwu theme is active.

## Settings

| Setting | Default | |
| --- | --- | --- |
| `uwu.sparkleOnSave` | `true` | Burst on save |
| `uwu.gutterHearts` | `true` | Hearts on changed lines |
| `uwu.errorKaomoji` | `true` | Sad faces on error lines |
| `uwu.mascot` | `true` | Status-bar mascot |
| `uwu.workbench.splash` | `true` | Kawaii Workbench: boot splash |
| `uwu.workbench.clickBursts` | `true` | Kawaii Workbench: heart bursts on click |
| `uwu.workbench.typingSparkles` | `true` | Kawaii Workbench: sparkles while typing |
| `uwu.workbench.mascot` | `true` | Kawaii Workbench: floating mascot |
| `uwu.workbench.confetti` | `true` | Kawaii Workbench: confetti on save |

Commands (in the Command Palette, under **uwu**): *Enable / Disable Kawaii Workbench*,
*Sparkle! ✧*, and *Clear Gutter Hearts*.

The colour of the error kaomoji can be themed with `uwu.kaomojiForeground`.

## How it works (and the fine print)

VS Code extensions can only draw where VS Code lets them. Everything here uses editor decorations,
so the effects live **inside the editor**, not over the sidebar or panels.

The sparkle burst uses a well-known decoration trick: VS Code places decoration style values
directly into CSS, which lets a decoration become a free-floating, click-through layer. Popular
extensions rely on it, but it isn't officially supported, so a future VS Code update could break
it. Every effect has its own on/off setting.

If you're upgrading from 0.3 or older: the sakura petals are gone, and any `uwu.petals.*` settings
you still have are simply ignored.
