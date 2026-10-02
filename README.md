# ♡ uwu ✧

Super duper kawaii themes in one pastel palette (🌙 strawberry-milk night and 🌸 sakura cream
day), with falling sakura wherever we can get away with it.

![sakura petals falling in the wind](opencode/web/screenshots/uwu-demo.gif)

## What's inside

| | | |
| --- | --- | --- |
| **opencode** | [**web**](opencode/web/) | Firefox `userContent.css` for the opencode v2 web UI: falling sakura, gradient bubbles, a rainbow composer, bouncy everything |
| | [**tui**](opencode/tui/) | Terminal theme for the opencode v2 TUI (`uwu` and `uwu-transparent`) |
| **VS Code** | [**uwu-code**](vscode/) | VS Code extension: colour theme, sakura petals behind your code, a sparkle burst on save, gutter hearts, error kaomoji and a status-bar mascot |

## Repo layout

```
opencode/
  web/          Firefox userContent.css for the opencode web UI
  tui/          opencode TUI themes
vscode/
  uwu-code/     the VS Code extension (source)
  uwu-code-0.1.1.vsix   ready-to-install package
tools/          generators shared by everything above
  palette.py      the shared colour palette
  petals.py       falling-sakura SVG tiles (web + VS Code)
  tui_theme.py    builds the opencode TUI themes
  vscode_theme.py builds the VS Code colour themes
```

Each section has its own README with install steps and screenshots.

| opencode web | opencode TUI | VS Code |
| --- | --- | --- |
| ![web](opencode/web/screenshots/session-dark.png) | ![tui](opencode/tui/screenshots/tui-diff-dark.png) | ![vscode](vscode/screenshots/dark-save-burst.png) |
