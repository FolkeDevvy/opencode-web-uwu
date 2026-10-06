# ♡ uwu ✧

Super duper kawaii themes in one pastel palette (🌙 strawberry-milk night and 🌸 sakura cream
day), with sparkles, confetti and a bunny wherever we can get away with it.

![uwu IDE demo](vscode/screenshots/uwu-ide-demo.gif)

**▶ [Watch the showcase](showcase/uwu-showcase.mp4)**: everything below working together, from boot splash to lock
screen (1080p60).

## Install

One script installs and removes everything. Pick what you want from a menu:

```sh
git clone https://github.com/folkedevvy/opencode-web-uwu.git
cd opencode-web-uwu
./uwu.sh
```

```
  ♡ uwu ✧ kawaii everything installer

  [♥]  1  opencode web         ✓ installed
  [ ]  2  opencode TUI         ·
  [♥]  3  uwu IDE (VS Code)    ·
  ...
  1-6 pick · a all · n none · i install · u uninstall · d Plasma day/night · q quit
```

Or say it directly:

```sh
./uwu.sh install web tui vscode     # just these
./uwu.sh install all                # everything
./uwu.sh install plasma --day       # the Plasma theme in uwu day
./uwu.sh uninstall lockscreen       # take one back out
./uwu.sh status                     # what's installed
```

| Name | What | Needs |
| --- | --- | --- |
| `web` | opencode web theme, added to every Firefox profile | Firefox |
| `tui` | opencode TUI themes, set as your theme | |
| `vscode` | the uwu IDE extension | VS Code, Code - OSS or VSCodium |
| `term` | uwu-term, in your app launcher | npm and build tools (Arch: `base-devel`); uses Arch's `electron` if installed |
| `plasma` | the whole Plasma desktop theme | KDE Plasma 6 |
| `lockscreen` | the lock screen | KDE Plasma 6.1+ |

Everything installs per user (no root). Uninstalling only removes what the installer added:
- Your own `userContent.css` and `user.js` lines stay.
- Your previous opencode theme is restored.
- Your previous Plasma look is restored.

Each section's README also explains how to install it by hand.

## What's inside

| | | |
| --- | --- | --- |
| **opencode** | [**web**](opencode/web/) | Firefox `userContent.css` for the opencode v2 web UI: gradient chat bubbles, a rainbow composer, bouncy everything |
| | [**tui**](opencode/tui/) | Terminal theme for the opencode v2 TUI (`uwu` and `uwu-transparent`) |
| **VS Code** | [**uwu IDE**](vscode/) | VS Code extension that turns VS Code into a kawaii IDE: themes, file icons, a full window makeover with splash screen, mascot, sparkles and confetti |
| **KDE Plasma** | [**desktop theme**](kde/plasma/) | The whole desktop: candy task bar, start menu, popups, pastel window title bars, night & day colours, a sakura wallpaper (portrait sizes too) and a bunny splash screen |
| | [**lock screen**](kde/lockscreen/) | A kawaii lock screen for Plasma 6: sakura, a bunny that sleeps, pouts and cheers, heart-shaped password dots, and a layout for monitors turned 90° |
| **Terminal** | [**uwu-term**](terminal/uwu-term/) | A kawaii terminal emulator for Arch + KDE Plasma (Wayland): sakura petals, candy tabs, a bunny mascot that reacts to your commands, confetti |

## Repo layout

```
uwu.sh          one installer for everything (./uwu.sh)
opencode/
  web/          Firefox userContent.css for the opencode web UI
  tui/          opencode TUI themes
vscode/
  uwu-code/     the VS Code extension (source)
  uwu-code-0.4.1.vsix   ready-to-install package
kde/
  plasma/       the Plasma desktop theme (./install.sh)
  lockscreen/   the Plasma lock screen (./install.sh)
terminal/
  uwu-term/     the kawaii terminal emulator (Electron + xterm.js)
    packaging/arch/  PKGBUILD for makepkg -si
showcase/       the all-in-one video and the scripts that make it
tools/          generators shared by everything above
  palette.py      the shared colour palette
  petals.py       sakura petal tiles (uwu-term)
  tui_theme.py    builds the opencode TUI themes
  vscode_theme.py builds the VS Code colour themes
  kawaii_assets.py draws the uwu IDE + uwu-term icons, mascot and file icons
  lockscreen_assets.py draws the lock screen's bunny moods and petals
  plasma_theme.py builds the Plasma style, colour schemes and title bars
  plasma_extras.py draws the sakura wallpaper, splash screen and global themes
```

Each section has its own README with screenshots and manual install steps.

| opencode web | opencode TUI |
| --- | --- |
| ![web](opencode/web/screenshots/session-dark.png) | ![tui](opencode/tui/screenshots/tui-diff-dark.png) |

| VS Code | Terminal |
| --- | --- |
| ![vscode](vscode/screenshots/uwu-ide-dark.png) | ![terminal](terminal/uwu-term/screenshots/dark.png) |

| KDE Plasma | KDE Plasma (day) |
| --- | --- |
| ![plasma](kde/plasma/screenshots/desktop-night.png) | ![plasma day](kde/plasma/screenshots/desktop-day.png) |

| Lock screen | Lock screen on a rotated monitor |
| --- | --- |
| ![lock screen](kde/lockscreen/screenshots/awake.png) | ![lock screen portrait](kde/lockscreen/screenshots/portrait.png) |
