#!/usr/bin/env python3
"""Generate the opencode TUI themes in tui/themes/ from one shared palette.

Colours come from tools/palette.py (shared with the web and VS Code themes).

    python3 tools/tui_theme.py
"""
import json
from pathlib import Path

from palette import PALETTE as DEFS

OUT = Path(__file__).resolve().parent.parent / "opencode" / "tui" / "themes"


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
