#!/usr/bin/env python3
"""Render a mock Plasma desktop with the uwu theme, without Plasma.

Draws the theme's SVGs the way Plasma does: 9-slice frames (corners as-is,
edges tiled, centre stretched), content margins from the hint-* elements,
colours injected from the colour scheme into each SVG's
"current-color-scheme" stylesheet, and shadows from the shadow-* pieces.
The panel, launcher, tooltip and window contents are mock-ups (Plasma's real
widgets aren't available here), but every themed surface uses the real files.

    pip install PySide6
    python3 preview.py --variant night --size 1920x1080 --out night.png
    python3 preview.py --variant day --size 1080x1920 --out day-portrait.png
"""
import argparse
import configparser
import re
import sys
from pathlib import Path

from PySide6.QtCore import QByteArray, QPointF, QRectF, QSizeF, Qt
from PySide6.QtGui import (QColor, QFont, QFontDatabase, QGuiApplication, QImage, QPainter, QPainterPath, QPen,
                           QPixmap)
from PySide6.QtSvg import QSvgRenderer

HERE = Path(__file__).resolve().parent
THEME = HERE.parent
FONT_DIR = THEME.parent / "lockscreen" / "lockscreen" / "fonts"


# ─────────────────────────────── colours ───────────────────────────────
def load_scheme(name):
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    cp.optionxform = str
    cp.read(THEME / "color-schemes" / f"{name}.colors")

    def c(group, key):
        r, g, b = (int(v) for v in cp[f"Colors:{group}"][key].split(","))
        return QColor(r, g, b)

    return {
        "Text": c("Window", "ForegroundNormal"), "Background": c("Window", "BackgroundNormal"),
        "Highlight": c("Selection", "BackgroundNormal"), "HighlightedText": c("Selection", "ForegroundNormal"),
        "ViewBackground": c("View", "BackgroundNormal"), "ViewText": c("View", "ForegroundNormal"),
        "ButtonBackground": c("Button", "BackgroundNormal"), "ButtonHover": c("Button", "DecorationHover"),
        "ButtonFocus": c("Button", "DecorationFocus"), "NeutralText": c("Window", "ForegroundNeutral"),
        "PositiveText": c("Window", "ForegroundPositive"), "NegativeText": c("Window", "ForegroundNegative"),
        "Inactive": c("Window", "ForegroundInactive"), "Header": c("Header", "BackgroundNormal"),
        "WindowAlt": c("Window", "BackgroundAlternate"), "ViewAlt": c("View", "BackgroundAlternate"),
    }


# ─────────────────────────────── FrameSvg ───────────────────────────────
class Svg:
    def __init__(self, path, colours):
        text = Path(path).read_text()
        style = "\n".join(f".ColorScheme-{k} {{ color:{v.name()}; }}" for k, v in colours.items())
        text = re.sub(r'(<style[^>]*id="current-color-scheme"[^>]*>)(.*?)(</style>)',
                      lambda m: m.group(1) + style + m.group(3), text, flags=re.S)
        self.r = QSvgRenderer(QByteArray(text.encode()))
        self.stretch_borders = self.has("hint-stretch-borders")
        self.tile_center = self.has("hint-tile-center")

    def has(self, eid):
        return self.r.elementExists(eid)

    def size(self, eid):
        if not self.has(eid):
            return QSizeF(0, 0)
        return self.r.transformForElement(eid).mapRect(self.r.boundsOnElement(eid)).size()

    def draw(self, p, eid, rect):
        if self.has(eid) and rect.width() > 0 and rect.height() > 0:
            self.r.render(p, eid, rect)

    def tile(self, p, eid, rect, horizontal):
        if not self.has(eid) or rect.width() <= 0 or rect.height() <= 0:
            return
        if self.stretch_borders:
            return self.draw(p, eid, rect)
        s = self.size(eid)
        tw = max(1, round(s.width())) if horizontal else max(1, round(rect.width()))
        th = max(1, round(rect.height())) if horizontal else max(1, round(s.height()))
        img = QImage(tw, th, QImage.Format_ARGB32_Premultiplied)
        img.fill(0)
        ip = QPainter(img)
        self.r.render(ip, eid, QRectF(0, 0, tw, th))
        ip.end()
        p.save()
        p.setClipRect(rect)
        p.drawTiledPixmap(rect, QPixmap.fromImage(img), QPointF(0, 0))
        p.restore()

    def margins(self, prefix=""):
        pre = f"{prefix}-" if prefix else ""
        out = []
        for side, el, attr in (("left", "left", "width"), ("top", "top", "height"),
                               ("right", "right", "width"), ("bottom", "bottom", "height")):
            hint = f"{pre}hint-{side}-margin"
            v = self.size(hint) if self.has(hint) else self.size(pre + el)
            out.append(getattr(v, attr)())
        return out  # l, t, r, b

    def frame(self, p, rect, prefix="", borders="tlbr"):
        pre = f"{prefix}-" if prefix else ""
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        l = self.size(pre + "left").width() if "l" in borders else 0
        r = self.size(pre + "right").width() if "r" in borders else 0
        t = self.size(pre + "top").height() if "t" in borders else 0
        b = self.size(pre + "bottom").height() if "b" in borders else 0
        if "t" in borders and "l" in borders:
            self.draw(p, pre + "topleft", QRectF(x, y, l, t))
        if "t" in borders and "r" in borders:
            self.draw(p, pre + "topright", QRectF(x + w - r, y, r, t))
        if "b" in borders and "l" in borders:
            self.draw(p, pre + "bottomleft", QRectF(x, y + h - b, l, b))
        if "b" in borders and "r" in borders:
            self.draw(p, pre + "bottomright", QRectF(x + w - r, y + h - b, r, b))
        if t:
            self.tile(p, pre + "top", QRectF(x + l, y, w - l - r, t), True)
        if b:
            self.tile(p, pre + "bottom", QRectF(x + l, y + h - b, w - l - r, b), True)
        if l:
            self.tile(p, pre + "left", QRectF(x, y + t, l, h - t - b), False)
        if r:
            self.tile(p, pre + "right", QRectF(x + w - r, y + t, r, h - t - b), False)
        self.draw(p, pre + "center", QRectF(x + l, y + t, w - l - r, h - t - b))

    def shadow(self, p, rect):
        if not self.has("shadow-top"):
            return
        m = self.margins("shadow")
        out = rect.adjusted(-m[0], -m[1], m[2], m[3])
        self.frame(p, out, "shadow")


# ─────────────────────────────── scene helpers ───────────────────────────────
class Scene:
    def __init__(self, variant, w, h):
        self.variant = variant
        self.c = load_scheme("UwuNight" if variant == "night" else "UwuDay")
        self.w, self.h = w, h
        self.u = min(w, h) / 1080
        self.portrait = h > w
        d = THEME / "desktoptheme" / "uwu"
        self.svg = {name: Svg(d / f"{name}.svg", self.c) for name in
                    ("widgets/panel-background", "dialogs/background", "widgets/tooltip", "widgets/tasks",
                     "widgets/viewitem", "widgets/plasmoidheading", "widgets/lineedit", "widgets/tabbar",
                     "widgets/button")}
        deco = THEME / "aurorae" / f"uwu-{variant}"
        self.deco = Svg(deco / "decoration.svg", self.c)
        self.buttons = {b: Svg(deco / f"{b}.svg", self.c) for b in ("minimize", "maximize", "close")}
        self.rc = configparser.ConfigParser(interpolation=None, strict=False)
        self.rc.optionxform = str
        self.rc.read(deco / f"uwu-{variant}rc")
        self.img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        self.p = QPainter(self.img)
        self.p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        fams = QFontDatabase.families()
        self.font = next((f for f in ("Noto Sans", "DejaVu Sans", "Liberation Sans") if f in fams), "sans-serif")

    def text(self, x, y, s, size, colour, weight=QFont.Normal, align=Qt.AlignLeft | Qt.AlignVCenter, w=400, h=None, family=None):
        f = QFont(family or self.font)
        f.setPixelSize(round(size))
        f.setWeight(weight)
        self.p.setFont(f)
        self.p.setPen(colour)
        self.p.drawText(QRectF(x, y, w, h or size * 1.6), int(align), s)

    def icon(self, x, y, s, colour, glyph, round_=0.28):
        p = self.p
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, s, s), s * round_, s * round_)
        p.fillPath(path, QColor(colour))
        p.fillPath(self._gloss(x, y, s), QColor(255, 255, 255, 60))
        self.text(x, y, glyph, s * 0.52, QColor("#ffffff"), QFont.Bold, Qt.AlignCenter, s, s)

    def _gloss(self, x, y, s):
        g = QPainterPath()
        g.addRoundedRect(QRectF(x + s * 0.12, y + s * 0.08, s * 0.76, s * 0.36), s * 0.18, s * 0.18)
        return g

    def wallpaper(self):
        base = THEME / "wallpapers" / "uwu-sakura" / "contents" / ("images_dark" if self.variant == "night" else "images")
        best = min(base.glob("*.jpg"), key=lambda f: abs(int(f.stem.split("x")[0]) / int(f.stem.split("x")[1]) - self.w / self.h) * 10
                   + abs(int(f.stem.split("x")[0]) - self.w) / 10000)
        im = QImage(str(best)).scaled(self.w, self.h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.p.drawImage(0, 0, im)

    # ── a window with the uwu decoration ──
    def window(self, rect, title, active=True):
        p, rc = self.p, self.rc["Layout"]
        P = [int(rc[k]) for k in ("PaddingLeft", "PaddingTop", "PaddingRight", "PaddingBottom")]
        side = int(rc["BorderLeft"])
        top = int(rc["TitleEdgeTop"]) + int(rc["TitleHeight"]) + int(rc["TitleEdgeBottom"])
        deco = QRectF(rect.x() - side - P[0], rect.y() - top - P[1], rect.width() + 2 * side + P[0] + P[2],
                      rect.height() + top + side + P[1] + P[3])
        self.deco.frame(p, deco, "decoration" if active else "decoration-inactive")
        # title + buttons
        ty = rect.y() - top + int(rc["TitleEdgeTop"])
        tc = self.c["Text"] if active else self.c["Inactive"]
        self.text(rect.x(), ty, title, 14 * max(self.u, 0.9), tc, QFont.Bold, Qt.AlignCenter, rect.width(), int(rc["TitleHeight"]))
        bx = rect.right() - 8
        for i, b in enumerate(("close", "maximize", "minimize")):
            bx -= 24 + (4 if i else 0)
            state = "hover" if (b == "close" and active) else ("active" if active else "inactive")
            self.buttons[b].draw(p, f"{state}-center", QRectF(bx, ty + 1, 24, 24))
        # app icon on the left
        self.icon(rect.x() + 8, ty + 3, 20, "#c7a2ff", "✿", 0.35)
        return rect

    def files_app(self, r):
        """A mock file manager in the window, painted with the colour scheme."""
        p, c, u = self.p, self.c, max(self.u, 0.9)
        p.fillRect(r, c["ViewBackground"])
        side = QRectF(r.x(), r.y(), 200 * u, r.height())
        p.fillRect(side, c["Background"])
        tool = QRectF(r.x(), r.y(), r.width(), 44 * u)
        p.fillRect(tool, c["Header"])
        self.text(r.x() + 16, tool.y(), "‹  ›   ~/Pictures/sakura", 14 * u, c["Text"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, 400, tool.height())
        y = tool.bottom() + 12
        for i, name in enumerate(["♡ Home", "✿ Desktop", "☆ Documents", "❀ Pictures", "♪ Music"]):
            rr = QRectF(side.x() + 8, y, side.width() - 16, 32 * u)
            if i == 3:
                self.svg["widgets/viewitem"].frame(p, rr, "selected")
            self.text(rr.x() + 12, rr.y(), name, 14 * u, c["Text"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, 300, rr.height())
            y += 36 * u
        # files grid
        cols = max(2, int((r.width() - side.width() - 40) / (110 * u)))
        names = ["blossom.png", "moon.png", "bunny.png", "picnic.jpg", "petals.png", "tea.jpg", "stars.png", "kitty.jpg"]
        colours = ["#ff8fc8", "#c7a2ff", "#8ff5cf", "#ffe59a", "#9fd8ff", "#ff6fb5", "#c7a2ff", "#ffb3d9"]
        for i, nm in enumerate(names):
            gx = side.right() + 24 + (i % cols) * 110 * u
            gy = tool.bottom() + 20 + (i // cols) * 120 * u
            if gy + 100 * u > r.bottom():
                break
            if i == 2:
                path = QPainterPath()
                path.addRoundedRect(QRectF(gx - 6, gy - 6, 96 * u, 106 * u), 10, 10)
                p.fillPath(path, QColor(c["Highlight"].red(), c["Highlight"].green(), c["Highlight"].blue(), 70))
                p.setPen(QPen(c["Highlight"], 1.5))
                p.drawPath(path)
            self.icon(gx + 10 * u, gy, 64 * u, colours[i], "✿♡☆❀✧♥★✿"[i], 0.22)
            self.text(gx - 10, gy + 70 * u, nm, 12 * u, c["ViewText"], QFont.Normal, Qt.AlignHCenter | Qt.AlignTop, 104 * u)

    # ── the panel ──
    def panel(self):
        p, c = self.p, self.c
        u = max(self.u, 0.9)
        th = 48 * u
        gap = 8 * u
        rect = QRectF(gap, self.h - th - gap, self.w - 2 * gap, th)
        bg = self.svg["widgets/panel-background"]
        bg.shadow(p, rect)
        bg.frame(p, rect)
        ml, mt, mr, mb = bg.margins()
        inner = rect.adjusted(ml, mt, -mr, -mb)
        # launcher button
        logo = QSvgRenderer(str(THEME / "icons" / "uwu-launcher.svg"))
        s = inner.height()
        hov = QRectF(inner.x(), inner.y(), s + 4, s)
        self.svg["widgets/tasks"].frame(p, hov, "hover")
        logo.render(p, QRectF(inner.x() + 4, inner.y() + 4, s - 4, s - 8))
        # tasks
        tasks = [("focus", "#ff8fc8", "♡", "uwu-term"), ("normal", "#c7a2ff", "✿", "Files"),
                 ("hover", "#8ff5cf", "♪", "Music"), ("minimized", "#9fd8ff", "✉", "Mail"),
                 ("attention", "#ffe59a", "☺", "Chat")]
        x = hov.right() + 10 * u
        tw = 54 * u if self.portrait else 160 * u
        task_rects = []
        tsvg = self.svg["widgets/tasks"]
        for state, col, glyph, name in tasks:
            r = QRectF(x, inner.y(), tw, inner.height())
            tsvg.frame(p, r, state)
            l, t, rr_, b = tsvg.margins(state)
            ic = r.height() - t - b - 4
            self.icon(r.x() + l + 6, r.y() + t + 2, ic, col, glyph)
            if not self.portrait:
                self.text(r.x() + l + ic + 14, r.y(), name, 13 * u, c["Text"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, tw, r.height())
            task_rects.append(r)
            x += tw + 4 * u
        # system tray + clock
        clock_w = 86 * u
        self.text(inner.right() - clock_w, inner.y() - 2 * u, "21:42", 15 * u, c["Text"], QFont.Bold, Qt.AlignCenter, clock_w, inner.height() * 0.62)
        self.text(inner.right() - clock_w, inner.y() + inner.height() * 0.5, "Sat 3 Oct", 11 * u, c["Inactive"], QFont.Normal, Qt.AlignCenter, clock_w, inner.height() * 0.5)
        tx = inner.right() - clock_w - 8 * u
        for g in ("♥", "♪", "☾", "✧"):
            tx -= 30 * u
            self.text(tx, inner.y(), g, 17 * u, c["Text"], QFont.Normal, Qt.AlignCenter, 28 * u, inner.height())
        return rect, task_rects

    # ── the launcher (start menu) ──
    def launcher(self, panel_rect):
        p, c = self.p, self.c
        u = max(self.u, 0.9)
        w = (self.w - 40) if self.portrait and self.w < 700 else 520 * u
        h = min(640 * u, self.h * (0.5 if self.portrait else 0.66))
        rect = QRectF(panel_rect.x(), panel_rect.y() - h - 8 * u, w, h)
        dlg = self.svg["dialogs/background"]
        dlg.shadow(p, rect)
        dlg.frame(p, rect)
        head = self.svg["widgets/plasmoidheading"]
        hh = 64 * u
        header = QRectF(rect.x(), rect.y(), rect.width(), hh)
        head.frame(p, header, "header")
        # avatar + name + search
        av = QRectF(header.x() + 16 * u, header.y() + 12 * u, 40 * u, 40 * u)
        bunny = QSvgRenderer(str(THEME.parent / "lockscreen" / "lockscreen" / "assets" / "bunny-awake.svg"))
        path = QPainterPath()
        path.addEllipse(av)
        p.fillPath(path, c["ButtonBackground"])
        bunny.render(p, av.adjusted(3, 3, -3, -3))
        le = self.svg["widgets/lineedit"]
        sr = QRectF(av.right() + 14 * u, header.y() + 14 * u, header.right() - av.right() - 30 * u, 36 * u)
        le.frame(p, sr, "base")
        le.frame(p, sr, "focus")
        self.text(sr.x() + 14, sr.y(), "search… ♡", 14 * u, c["Inactive"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, 300, sr.height())
        # footer with tabs + power buttons
        fh = 52 * u
        footer = QRectF(rect.x(), rect.bottom() - fh, rect.width(), fh)
        head.frame(p, footer, "footer")
        tab = QRectF(footer.x() + 14 * u, footer.y() + 10 * u, 130 * u, 32 * u)
        self.svg["widgets/tabbar"].frame(p, tab, "north-active-tab")
        self.text(tab.x(), tab.y(), "✿ Applications", 13 * u, c["Text"], QFont.Bold, Qt.AlignCenter, tab.width(), tab.height())
        self.text(tab.right() + 8, tab.y(), "♡ Places", 13 * u, c["Inactive"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, 120, tab.height())
        bx = footer.right() - 14 * u
        btn = self.svg["widgets/button"]
        for i, g in enumerate(("⏻", "↻", "☾")):
            bx -= 34 * u
            br = QRectF(bx, footer.y() + 10 * u, 32 * u, 32 * u)
            if i == 2:
                btn.frame(p, br, "toolbutton-hover")
            self.text(br.x(), br.y(), g, 16 * u, c["Text"], QFont.Normal, Qt.AlignCenter, br.width(), br.height())
            bx -= 4 * u
        # categories + apps
        body = QRectF(rect.x() + 10 * u, header.bottom() + 8 * u, rect.width() - 20 * u, footer.y() - header.bottom() - 16 * u)
        cw = body.width() * 0.38
        cats = ["♡ Favourites", "✿ All Apps", "☆ Games", "♪ Multimedia", "✎ Office", "⚙ System", "❀ Utilities"]
        vi = self.svg["widgets/viewitem"]
        for i, cat in enumerate(cats):
            rr = QRectF(body.x(), body.y() + i * 38 * u, cw, 34 * u)
            if rr.bottom() > body.bottom():
                break
            if i == 0:
                vi.frame(p, rr, "selected")
            self.text(rr.x() + 12, rr.y(), cat, 14 * u, c["Text"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, cw, rr.height())
        apps = [("uwu-term", "#ff8fc8", "♡", "Terminal"), ("Files", "#c7a2ff", "✿", "File manager"),
                ("Firefox", "#ffb36b", "☺", "Web browser"), ("Music", "#8ff5cf", "♪", "Music player"),
                ("Notes", "#ffe59a", "✎", "Text editor"), ("Paint", "#9fd8ff", "✧", "Drawing"),
                ("Settings", "#ff6fb5", "⚙", "System Settings")]
        ax = body.x() + cw + 10 * u
        aw = body.right() - ax
        for i, (nm, col, g, desc) in enumerate(apps):
            rr = QRectF(ax, body.y() + i * 50 * u, aw, 46 * u)
            if rr.bottom() > body.bottom():
                break
            if i == 2:
                vi.frame(p, rr, "hover")
            self.icon(rr.x() + 8 * u, rr.y() + 7 * u, 32 * u, col, g)
            self.text(rr.x() + 50 * u, rr.y() + 4 * u, nm, 14 * u, c["Text"], QFont.Bold, Qt.AlignLeft | Qt.AlignVCenter, aw, 20 * u)
            self.text(rr.x() + 50 * u, rr.y() + 23 * u, desc, 12 * u, c["Inactive"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, aw, 18 * u)
        return rect

    def tooltip(self, task_rect, title, sub):
        p, c = self.p, self.c
        u = max(self.u, 0.9)
        w, h = 210 * u, 62 * u
        rect = QRectF(task_rect.center().x() - w / 2, task_rect.y() - h - 14 * u, w, h)
        tt = self.svg["widgets/tooltip"]
        tt.shadow(p, rect)
        tt.frame(p, rect)
        l, t, r, b = tt.margins()
        self.text(rect.x() + l + 4, rect.y() + t, title, 14 * u, c["Text"], QFont.Bold, Qt.AlignLeft | Qt.AlignTop, w)
        self.text(rect.x() + l + 4, rect.y() + t + 22 * u, sub, 12 * u, c["Inactive"], QFont.Normal, Qt.AlignLeft | Qt.AlignTop, w)

    def render(self, out):
        self.wallpaper()
        u = max(self.u, 0.9)
        if self.portrait:
            win = QRectF(60 * u, 140 * u, self.w - 120 * u, self.h * 0.32)
        else:
            win = QRectF(self.w * 0.36, 110 * u, self.w * 0.56, self.h * 0.56)
        back = QRectF(win.x() + win.width() * 0.25, win.y() + win.height() * 0.45, win.width() * 0.7, win.height() * 0.75)
        if self.portrait:
            back = QRectF(win.x() + 40 * u, win.bottom() - win.height() * 0.3, win.width() - 80 * u, win.height() * 0.62)
        self.window(back, "System Settings", active=False)
        self.p.fillRect(back, self.c["Background"])
        self.window(win, "Pictures ♡ Files")
        self.files_app(win)
        panel, tasks = self.panel()
        self.launcher(panel)
        if not self.portrait:   # on a narrow screen the open launcher would cover it
            self.tooltip(tasks[4], "Chat", "♡ 3 new messages")
        self.p.end()
        self.img.save(out)
        print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="night", choices=["night", "day"])
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--out", default="preview.png")
    a = ap.parse_args()
    app = QGuiApplication(sys.argv)
    for f in FONT_DIR.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(f))
    w, h = (int(v) for v in a.size.split("x"))
    Scene(a.variant, w, h).render(a.out)


if __name__ == "__main__":
    main()
