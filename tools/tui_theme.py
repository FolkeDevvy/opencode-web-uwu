#!/usr/bin/env python3
"""Generate the opencode TUI themes in tui/themes/ from one shared palette.

The colours mirror chrome/userContent.css (strawberry-milk night / sakura
cream day) so the TUI and the web UI feel like the same theme.

    python3 tools/tui_theme.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "tui" / "themes"

# name: (dark, light)
DEFS = {
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

THEME = {
    "primary": "pink",
    "secondary": "lavender",
    "accent": "mint",
    "error": "cherry",
    "warning": "butter",
    "success": "mint",
    "info": "sky",
    "text": "text",
    "textMuted": "textMuted",
    "selectedListItemText": "ink",
    "background": "bg",
    "backgroundPanel": "bgPanel",
    "backgroundElement": "bgElement",
    "backgroundMenu": "bgPanel",
    "border": "border",
    "borderActive": "pink",
    "borderSubtle": "borderSubtle",
    "diffAdded": "mint",
    "diffRemoved": "cherry",
    "diffContext": "textMuted",
    "diffHunkHeader": "lavender",
    "diffHighlightAdded": "addHi",
    "diffHighlightRemoved": "delHi",
    "diffAddedBg": "addBg",
    "diffRemovedBg": "delBg",
    "diffContextBg": "bgPanel",
    "diffLineNumber": "lineNo",
    "diffAddedLineNumberBg": "addLnBg",
    "diffRemovedLineNumberBg": "delLnBg",
    "markdownText": "text",
    "markdownHeading": "pink",
    "markdownLink": "sky",
    "markdownLinkText": "lavender",
    "markdownCode": "mint",
    "markdownBlockQuote": "blush",
    "markdownEmph": "lavender",
    "markdownStrong": "hotPink",
    "markdownHorizontalRule": "border",
    "markdownListItem": "pink",
    "markdownListEnumeration": "lavender",
    "markdownImage": "sky",
    "markdownImageText": "lavender",
    "markdownCodeBlock": "text",
    "syntaxComment": "plum",
    "syntaxKeyword": "pink",
    "syntaxFunction": "lavender",
    "syntaxVariable": "text",
    "syntaxString": "mint",
    "syntaxNumber": "sky",
    "syntaxType": "butter",
    "syntaxOperator": "operator",
    "syntaxPunctuation": "punct",
}


def build(transparent=False):
    defs = {}
    for name, (dark, light) in DEFS.items():
        defs[f"{name}Dark"] = dark
        defs[f"{name}Light"] = light
    theme = {key: {"dark": f"{ref}Dark", "light": f"{ref}Light"} for key, ref in THEME.items()}
    if transparent:
        # let the terminal's own background (image, blur, ...) show through
        theme["background"] = "none"
    return {"$schema": "https://opencode.ai/theme.json", "defs": defs, "theme": theme}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, transparent in (("uwu", False), ("uwu-transparent", True)):
        (OUT / f"{name}.json").write_text(json.dumps(build(transparent), indent=2) + "\n")
        print("wrote", OUT / f"{name}.json")


if __name__ == "__main__":
    main()
