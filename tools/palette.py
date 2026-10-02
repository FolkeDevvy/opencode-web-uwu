"""The shared uwu palette: (dark, light) pairs.

Mirrors opencode/web/chrome/userContent.css (strawberry-milk night / sakura
cream day). The TUI and VS Code generators both build from this so every
flavour of the theme stays in sync.
"""

# name: (dark, light)
PALETTE = {
    "bg":            ("#21142a", "#fff7fb"),
    "bgPanel":       ("#2b1a36", "#fff0f7"),
    "bgElement":     ("#362143", "#ffe4f1"),
    "border":        ("#5a376c", "#f3b6d4"),
    "borderSubtle":  ("#3a2447", "#ffd3e9"),
    "text":          ("#ffeaf6", "#57264c"),
    "textMuted":     ("#b98aab", "#9a5f8a"),
    "ink":           ("#2a0c22", "#ffffff"),
    "pink":          ("#ff8fc8", "#e8438f"),
    "hotPink":       ("#ff9fd0", "#c2337e"),
    "lavender":      ("#c7a2ff", "#8a4fe0"),
    "mint":          ("#8ff5cf", "#13936a"),
    "sky":           ("#9fd8ff", "#2f86c9"),
    "butter":        ("#ffe59a", "#b07d00"),
    "peach":         ("#ffb79a", "#e0703f"),
    "cherry":        ("#ff8aa5", "#e0325e"),
    "blush":         ("#d9a9cb", "#9a5f8a"),
    "plum":          ("#9a7a9a", "#b592ab"),
    "operator":      ("#ffb3da", "#d14d93"),
    "punct":         ("#c79dbb", "#a77396"),
    "lineNo":        ("#7f5a78", "#c08db2"),
    "addBg":         ("#12352b", "#e3fbf1"),
    "addLnBg":       ("#0f2b23", "#d3f5e6"),
    "delBg":         ("#3a1426", "#ffe6ec"),
    "delLnBg":       ("#2e0f1e", "#ffd6e0"),
    "addHi":         ("#b8ffe4", "#0e7a52"),
    "delHi":         ("#ffb3c4", "#c21f4a"),
}
