#!/usr/bin/env python3
"""♡ uwu showcase: one 1080p60 video of everything in this repo working together.

    boot splash → Plasma desktop → start menu → uwu-term → uwu IDE (VS Code)
    → opencode web → opencode TUI → switch to day → rotated monitor
    → lock screen → unlock → end card

What's real and what's staged:
  * the splash screen and the lock screen are the real QML, recorded at an
    exact 60 fps by qmlrec.py (run that first; see README)
  * uwu-term, the uwu IDE and opencode web are their real recordings
  * the desktop, panel, start menu and title bars are drawn from the real
    Plasma theme files, using kde/plasma/preview/preview.py's renderer
    (Plasma itself isn't running; the cursor and the window animations are
    staged)

Needs PySide6 and ffmpeg.  python3 showcase/make_showcase.py [--preview-every N]
"""
import argparse
import math
import random
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontDatabase, QGuiApplication, QImage, QLinearGradient,
                           QPainter, QPainterPath, QPen, QTransform)
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "kde" / "plasma" / "preview"))
import preview as pv  # noqa: E402

W, H, FPS = 1920, 1080, 60
CLIPS = Path(__file__).resolve().parent / "clips"
LOCK = ROOT / "kde" / "lockscreen" / "lockscreen"
SHOTS = {
    "term": ROOT / "terminal" / "uwu-term" / "screenshots" / "uwu-term-demo.mp4",
    "ide": ROOT / "vscode" / "screenshots" / "uwu-ide-demo.mp4",
    "web": ROOT / "opencode" / "web" / "screenshots" / "uwu-demo.mp4",
}


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def back_out(t, s=1.5):
    t = max(0.0, min(1.0, t)) - 1
    return t * t * ((s + 1) * t + s) + 1


def lerp(a, b, t):
    return a + (b - a) * t


# ─────────────────────────────── video clips ───────────────────────────────
class Clip:
    """Reads a video as 60 fps BGRA frames at a given size, sequentially."""

    def __init__(self, path, w, h, start=0.0):
        self.w, self.h = int(w), int(h)
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(path), "-vf",
             f"scale={self.w}:{self.h}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "bgra", "-"],
            stdout=subprocess.PIPE)
        self.index = -1
        self.img = QImage(self.w, self.h, QImage.Format_ARGB32)
        self.img.fill(0)
        self._buf = None

    def frame(self, i):
        while self.index < i:
            data = self.proc.stdout.read(self.w * self.h * 4)
            if len(data) < self.w * self.h * 4:
                break  # clip ended: hold the last frame
            self._buf = data
            self.img = QImage(self._buf, self.w, self.h, QImage.Format_ARGB32)
            self.index += 1
        return self.img


# ─────────────────────────────── shared drawing ───────────────────────────────
class Kit:
    def __init__(self):
        for f in (LOCK / "fonts").glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(f))
        self.night = pv.Scene("night", W, H)
        self.day = pv.Scene("day", W, H)
        self.night.p.end()
        self.day.p.end()
        self.wall = {v: self._wall(v) for v in ("night", "day")}
        self.petal_imgs = [QImage(str(LOCK / "assets" / f"petal-{i}.png")) for i in range(4)]
        self.soft_imgs = [QImage(str(LOCK / "assets" / f"petal-blur-{i}.png")) for i in range(3)]
        self.bunny = {m: QSvgRenderer(str(LOCK / "assets" / f"bunny-{m}.svg")) for m in ("awake", "love", "sleepy")}
        self.logo = QSvgRenderer(str(ROOT / "kde" / "plasma" / "icons" / "uwu-launcher.svg"))
        rnd = random.Random(5)
        self.petals = [dict(x=rnd.uniform(-0.2, 1.0), t0=rnd.random(), dur=rnd.uniform(9, 16), img=rnd.randrange(4),
                            s=rnd.uniform(14, 30), sway=rnd.uniform(20, 60), ph=rnd.uniform(0, 6.28),
                            spin=rnd.uniform(-1, 1) * 300, flip=rnd.uniform(0.5, 2)) for _ in range(46)]
        self.soft = [dict(x=rnd.uniform(0, 1), t0=rnd.random(), dur=rnd.uniform(16, 22), img=rnd.randrange(3),
                          s=rnd.uniform(110, 190), ph=rnd.uniform(0, 6.28)) for _ in range(4)]
        self._layers = {}

    def _wall(self, variant):
        sc = pv.Scene(variant, W, H)
        sc.wallpaper()
        sc.p.end()
        return sc.img

    def scene(self, variant):
        return self.night if variant == "night" else self.day

    # falling petals with wind, drawn straight onto the frame
    def draw_petals(self, p, time, alpha=1.0, w=W, h=H):
        wind = 40 * math.sin(time * 0.35) + 25
        for pt in self.petals:
            k = ((time / pt["dur"]) + pt["t0"]) % 1.0
            x = pt["x"] * w + k * (180 + wind) + math.sin(k * 6.28 * 1.4 + pt["ph"]) * pt["sway"]
            y = -40 + k * (h + 80)
            p.save()
            p.translate(x, y)
            p.rotate(pt["ph"] * 57 + k * pt["spin"])
            p.scale(0.35 + 0.65 * abs(math.cos(k * 6.28 * pt["flip"] + pt["ph"])), 1)
            p.setOpacity(alpha * 0.85 * min(1, k * 12, (1 - k) * 12))
            s = pt["s"]
            p.drawImage(QRectF(-s / 2, -s / 2, s, s), self.petal_imgs[pt["img"]])
            p.restore()
        for pt in self.soft:
            k = ((time / pt["dur"]) + pt["t0"]) % 1.0
            x = pt["x"] * w + k * 260 + math.sin(k * 6.28 + pt["ph"]) * 50
            y = -200 + k * (h + 400)
            s = pt["s"]
            p.save()
            p.setOpacity(alpha * 0.4 * min(1, k * 8, (1 - k) * 8))
            p.translate(x, y)
            p.rotate(pt["ph"] * 40 + k * 90)
            p.drawImage(QRectF(-s / 2, -s / 2, s, s), self.soft_imgs[pt["img"]])
            p.restore()
        p.setOpacity(1)

    def text(self, p, rect, s, size, colour, weight=QFont.Black, align=Qt.AlignCenter, family="Nunito"):
        f = QFont(family)
        f.setPixelSize(round(size))
        f.setWeight(weight)
        p.setFont(f)
        p.setPen(QColor(colour))
        p.drawText(rect, int(align), s)

    def caption(self, p, label, sub, k):
        """A candy pill in the top-left corner; k = 0..1 slide-in amount."""
        if k <= 0:
            return
        f = QFont("Nunito")
        f.setPixelSize(30)
        f.setWeight(QFont.Black)
        fs = QFont("Nunito")
        fs.setPixelSize(19)
        fs.setWeight(QFont.Bold)
        from PySide6.QtGui import QFontMetrics
        w = max(QFontMetrics(f).horizontalAdvance(label), QFontMetrics(fs).horizontalAdvance(sub)) + 64
        h = 92 if sub else 64
        x = lerp(-w - 20, 40, back_out(k, 1.2))
        r = QRectF(x, 40, w, h)
        path = QPainterPath()
        path.addRoundedRect(r, 26, 26)
        p.save()
        p.setOpacity(min(1, k * 2))
        for i in range(8):  # soft glow
            g = QPainterPath()
            g.addRoundedRect(r.adjusted(-i * 2, -i * 2 + 6, i * 2, i * 2 + 6), 26 + i * 2, 26 + i * 2)
            p.fillPath(g, QColor(42, 10, 36, 14))
        grad = QLinearGradient(r.topLeft(), r.topRight())
        grad.setColorAt(0, QColor("#ff8fc8"))
        grad.setColorAt(1, QColor("#c7a2ff"))
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(255, 255, 255, 120), 2))
        p.drawPath(path)
        self.text(p, QRectF(r.x() + 32, r.y() + 10, w, 44), label, 30, "#2a0c22", QFont.Black, Qt.AlignLeft | Qt.AlignVCenter)
        if sub:
            self.text(p, QRectF(r.x() + 32, r.y() + 50, w, 30), sub, 19, "#4a1640", QFont.Bold, Qt.AlignLeft | Qt.AlignVCenter)
        p.restore()

    def cursor(self, p, x, y, pressed=False):
        path = QPainterPath()
        pts = [(0, 0), (0, 26), (7, 20), (12, 31), (17, 29), (12, 18), (21, 18)]
        path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
        path.closeSubpath()
        p.save()
        p.translate(x, y)
        s = 0.88 if pressed else 1.0
        p.scale(s, s)
        p.translate(2, 3)
        p.fillPath(path, QColor(42, 10, 36, 70))
        p.translate(-2, -3)
        p.fillPath(path, QColor("#ffffff"))
        p.setPen(QPen(QColor("#e8438f"), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)
        p.restore()

    # a frameless app window (uwu-term, VS Code): rounded, with a soft shadow
    def app_window(self, p, img, rect, radius=12, alpha=1.0, scale=1.0):
        p.save()
        p.setOpacity(alpha)
        c = rect.center()
        p.translate(c)
        p.scale(scale, scale)
        p.translate(-c)
        for i in range(14):
            g = QPainterPath()
            g.addRoundedRect(rect.adjusted(-i * 2.2, -i * 2.2 + 10, i * 2.2, i * 2.2 + 14), radius + i * 2, radius + i * 2)
            p.fillPath(g, QColor(30, 6, 26, 9))
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path)
        p.drawImage(rect, img)
        p.restore()

    # a window with the uwu KWin decoration around it (Firefox, Konsole)
    def deco_window(self, p, variant, img, rect, title, active=True, alpha=1.0, scale=1.0):
        sc = self.scene(variant)
        p.save()
        p.setOpacity(alpha)
        c = rect.center()
        p.translate(c)
        p.scale(scale, scale)
        p.translate(-c)
        sc.p = p
        rc = sc.rc["Layout"]
        P = [int(rc[k]) for k in ("PaddingLeft", "PaddingTop", "PaddingRight", "PaddingBottom")]
        side = int(rc["BorderLeft"])
        top = int(rc["TitleEdgeTop"]) + int(rc["TitleHeight"]) + int(rc["TitleEdgeBottom"])
        deco = QRectF(rect.x() - side - P[0], rect.y() - top - P[1], rect.width() + 2 * side + P[0] + P[2],
                      rect.height() + top + side + P[1] + P[3])
        sc.deco.frame(p, deco, "decoration" if active else "decoration-inactive")
        ty = rect.y() - top + int(rc["TitleEdgeTop"])
        sc.text(rect.x(), ty, title, 14, sc.c["Text"] if active else sc.c["Inactive"], QFont.Bold, Qt.AlignCenter,
                rect.width(), int(rc["TitleHeight"]))
        bx = rect.right() - 8
        for i, b in enumerate(("close", "maximize", "minimize")):
            bx -= 24 + (4 if i else 0)
            sc.buttons[b].draw(p, f"{'active' if active else 'inactive'}-center", QRectF(bx, ty + 1, 24, 24))
        sc.icon(rect.x() + 8, ty + 3, 20, "#c7a2ff", "✿", 0.35)
        p.drawImage(rect, img)
        p.restore()

    # the panel with whatever windows are open
    def panel(self, p, variant, tasks, active=None, hover=None, launcher_hover=False, slide=1.0):
        key = ("panel", variant, tuple(tasks), active, hover, launcher_hover)
        if key not in self._layers:
            img = QImage(W, H, QImage.Format_ARGB32_Premultiplied)
            img.fill(0)
            q = QPainter(img)
            q.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
            sc = self.scene(variant)
            sc.p = q
            c = sc.c
            th, gap = 50, 8
            rect = QRectF(gap, H - th - gap, W - 2 * gap, th)
            bg = sc.svg["widgets/panel-background"]
            bg.shadow(q, rect)
            bg.frame(q, rect)
            ml, mt, mr, mb = bg.margins()
            inner = rect.adjusted(ml, mt, -mr, -mb)
            s = inner.height()
            lr = QRectF(inner.x(), inner.y(), s + 4, s)
            if launcher_hover:
                sc.svg["widgets/tasks"].frame(q, lr, "hover")
            self.logo.render(q, QRectF(lr.x() + 5, lr.y() + 4, s - 6, s - 8))
            x = lr.right() + 10
            tsvg = sc.svg["widgets/tasks"]
            for i, (name, col, glyph) in enumerate(tasks):
                r = QRectF(x, inner.y(), 176, inner.height())
                state = "focus" if name == active else ("hover" if name == hover else "normal")
                tsvg.frame(q, r, state)
                l, t, rr_, b = tsvg.margins(state)
                ic = r.height() - t - b - 4
                sc.icon(r.x() + l + 6, r.y() + t + 2, ic, col, glyph)
                sc.text(r.x() + l + ic + 14, r.y(), name, 14, c["Text"], QFont.Normal, Qt.AlignLeft | Qt.AlignVCenter, 140, r.height())
                x += 180
            cw = 90
            sc.text(inner.right() - cw, inner.y() - 2, "21:42", 16, c["Text"], QFont.Bold, Qt.AlignCenter, cw, inner.height() * 0.62)
            sc.text(inner.right() - cw, inner.y() + inner.height() * 0.5, "Sat 3 Oct", 11, c["Inactive"], QFont.Normal, Qt.AlignCenter, cw, inner.height() * 0.5)
            tx = inner.right() - cw - 8
            for g in ("♥", "♪", "☀" if variant == "night" else "☾", "✧"):
                tx -= 32
                sc.text(tx, inner.y(), g, 18, c["Text"], QFont.Normal, Qt.AlignCenter, 30, inner.height())
            q.end()
            self._layers[key] = img
        p.save()
        p.translate(0, (1 - slide) * 90)
        p.drawImage(0, 0, self._layers[key])
        p.restore()

    def launcher(self, p, variant, k):
        key = ("launcher", variant)
        if key not in self._layers:
            img = QImage(W, H, QImage.Format_ARGB32_Premultiplied)
            img.fill(0)
            q = QPainter(img)
            q.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
            sc = self.scene(variant)
            sc.p = q
            sc.launcher(QRectF(8, H - 58, W - 16, 50))
            q.end()
            self._layers[key] = img
        if k <= 0:
            return
        p.save()
        p.setOpacity(min(1, k * 1.5))
        origin = QPointF(30, H - 60)
        p.translate(origin)
        sc_ = lerp(0.9, 1.0, back_out(k, 1.1))
        p.scale(sc_, sc_)
        p.translate(-origin)
        p.drawImage(0, 0, self._layers[key])
        p.restore()

    def blurred(self, img, factor=14):
        small = img.scaled(img.width() // factor, img.height() // factor, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        return small.scaled(img.width(), img.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


# ─────────────────────────────── the story ───────────────────────────────
TERM_TASK = ("uwu-term", "#ff8fc8", "♡")
IDE_TASK = ("uwu IDE", "#c7a2ff", "✿")
WEB_TASK = ("Firefox", "#ffb36b", "☺")
TUI_TASK = ("Konsole", "#8ff5cf", "❯")

TERM_RECT = QRectF(140, 90, 1100, 680)
IDE_RECT = QRectF(560, 70, 1240, 775)
WEB_RECT = QRectF(330, 120, 1120, 700)
TUI_RECT = QRectF(760, 250, 980, 640)


class Show:
    def __init__(self, kit):
        self.k = kit
        self.clips = {}
        self.stills = {}
        self.segments = []  # (name, seconds, fn, crossfade)
        self.build()

    def clip(self, key, path, w, h, start=0.0):
        if key not in self.clips:
            self.clips[key] = (Clip(path, w, h, start), None)
        return self.clips[key][0]

    def still(self, path, w, h):
        key = (str(path), w, h)
        if key not in self.stills:
            self.stills[key] = QImage(str(path)).scaled(int(w), int(h), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        return self.stills[key]

    def seg(self, name, seconds, xfade=0.0):
        def deco(fn):
            self.segments.append((name, seconds, fn, xfade))
            return fn
        return deco

    def desktop(self, p, variant, time, petals=True):
        p.drawImage(0, 0, self.k.wall[variant])
        if petals:
            self.k.draw_petals(p, time)

    def build(self):
        k = self.k

        @self.seg("intro", 3.6)
        def intro(p, t, T):
            z = 1.06 - 0.04 * t / 3.6
            p.save()
            p.translate(W / 2, H / 2)
            p.scale(z, z)
            p.translate(-W / 2, -H / 2)
            p.drawImage(0, 0, k.wall["night"])
            p.restore()
            p.fillRect(QRectF(0, 0, W, H), QColor(20, 6, 26, 140))
            k.draw_petals(p, T)
            a = ease_out(t / 1.0)
            # bunny
            b = 150
            hop = abs(math.sin(t * 3.2)) * 26
            p.setOpacity(a)
            k.bunny["awake"].render(p, QRectF(W / 2 - b / 2, 250 - hop, b, b))
            # title with a pink → lavender fill
            f = QFont("Nunito")
            f.setPixelSize(170)
            f.setWeight(QFont.Black)
            path = QPainterPath()
            path.addText(0, 0, f, "uwu ♥")
            br = path.boundingRect()
            path.translate(W / 2 - br.width() / 2 - br.x(), 560)
            grad = QLinearGradient(QPointF(W / 2 - 300, 0), QPointF(W / 2 + 300, 0))
            grad.setColorAt(0, QColor("#ff8fc8"))
            grad.setColorAt(1, QColor("#c7a2ff"))
            p.save()
            p.translate(0, (1 - a) * 30)
            p.fillPath(path.translated(0, 8), QColor(42, 10, 36, 120))
            p.fillPath(path, QBrush(grad))
            p.restore()
            p.setOpacity(ease_out((t - 0.6) / 1.0))
            k.text(p, QRectF(0, 610, W, 60), "a kawaii desktop, from boot to lock screen", 40, "#ffeaf6", QFont.ExtraBold)
            p.setOpacity(ease_out((t - 1.2) / 1.0) * 0.85)
            k.text(p, QRectF(0, 680, W, 40), "KDE Plasma · uwu-term · VS Code · opencode web & TUI · lock screen", 26, "#d6a8c8", QFont.Bold)
            p.setOpacity(1)

        @self.seg("splash", 5.5, xfade=0.7)
        def splash(p, t, T):
            c = self.clip("splash", CLIPS / "q-splash.mp4", W, H)
            p.drawImage(0, 0, c.frame(int(t * FPS)))
            k.caption(p, "① splash screen", "the bunny hops while Plasma starts", ease_out((t - 0.5) / 0.6) - ease((t - 4.8) / 0.5))

        @self.seg("desktop", 3.8, xfade=0.9)
        def desktop(p, t, T):
            self.desktop(p, "night", T)
            k.panel(p, "night", [], slide=ease_out((t - 0.3) / 0.7))
            k.caption(p, "② Plasma theme", "candy panel · sakura wallpaper · night colours", ease_out((t - 0.8) / 0.6))
            mx, my = lerp(1300, 1000, ease(t / 3.8)), lerp(700, 640, ease(t / 3.8))
            k.cursor(p, mx, my)

        @self.seg("launcher", 4.6)
        def launcher(p, t, T):
            self.desktop(p, "night", T)
            hover_l = 0.9 < t < 3.9
            k.panel(p, "night", [], launcher_hover=hover_l)
            open_k = ease_out((t - 1.1) / 0.35) - ease((t - 3.7) / 0.3)
            k.launcher(p, "night", open_k)
            k.caption(p, "start menu", "pill search · candy highlights · dashed dividers", ease_out(t / 0.5))
            # cursor: to the start button, click, then down the app list, click uwu-term
            if t < 1.0:
                mx, my = lerp(1000, 34, ease(t / 1.0)), lerp(640, H - 32, ease(t / 1.0))
            elif t < 1.6:
                mx, my = 34, H - 32
            elif t < 3.0:
                q = ease((t - 1.6) / 1.4)
                mx, my = lerp(34, 330, q), lerp(H - 32, 515, q)
            else:
                q = ease((t - 3.0) / 0.5)
                mx, my = lerp(330, 300, q), lerp(515, 485, q)
            pressed = 1.0 < t < 1.15 or 3.55 < t < 3.7
            k.cursor(p, mx, my, pressed)

        @self.seg("term", 8.5)
        def term(p, t, T):
            self.desktop(p, "night", T)
            c = self.clip("term", SHOTS["term"], TERM_RECT.width(), TERM_RECT.height(), start=3.4)
            a = ease_out(t / 0.45)
            k.app_window(p, c.frame(int(t * FPS)), TERM_RECT, 18, a, lerp(0.92, 1, back_out(t / 0.5, 1.2)))
            k.panel(p, "night", [TERM_TASK], active="uwu-term")
            k.caption(p, "③ uwu-term", "a kawaii terminal: the bunny reacts to your commands", ease_out((t - 0.3) / 0.6))

        @self.seg("ide", 8.0)
        def ide(p, t, T):
            self.desktop(p, "night", T)
            p.drawImage(0, 0, self._term_still(T))
            c = self.clip("ide", SHOTS["ide"], IDE_RECT.width(), IDE_RECT.height(), start=2.5)
            k.app_window(p, c.frame(int(t * FPS)), IDE_RECT, 10, ease_out(t / 0.45), lerp(0.92, 1, back_out(t / 0.5, 1.2)))
            k.panel(p, "night", [TERM_TASK, IDE_TASK], active="uwu IDE")
            k.caption(p, "④ uwu IDE", "VS Code, made unrecognisably cute", ease_out((t - 0.3) / 0.6))

        @self.seg("web", 7.0)
        def web(p, t, T):
            self.desktop(p, "night", T)
            p.drawImage(0, 0, self._term_still(T))
            p.drawImage(0, 0, self._ide_still())
            c = self.clip("web", SHOTS["web"], WEB_RECT.width(), WEB_RECT.height(), start=0.5)
            k.deco_window(p, "night", c.frame(int(t * FPS)), WEB_RECT, "opencode ♡ Firefox", True,
                          ease_out(t / 0.45), lerp(0.92, 1, back_out(t / 0.5, 1.2)))
            k.panel(p, "night", [TERM_TASK, IDE_TASK, WEB_TASK], active="Firefox")
            k.caption(p, "⑤ opencode web", "uwu window title bar · candy buttons", ease_out((t - 0.3) / 0.6))

        @self.seg("tui", 4.6)
        def tui(p, t, T):
            self.desktop(p, "night", T)
            p.drawImage(0, 0, self._term_still(T))
            p.drawImage(0, 0, self._ide_still())
            p.drawImage(0, 0, self._web_still())
            img = self.still(ROOT / "opencode" / "tui" / "screenshots" / "tui-diff-dark.png", TUI_RECT.width(), TUI_RECT.height())
            k.deco_window(p, "night", img, TUI_RECT, "opencode ♡ Konsole", True, ease_out(t / 0.45), lerp(0.92, 1, back_out(t / 0.5, 1.2)))
            k.panel(p, "night", [TERM_TASK, IDE_TASK, WEB_TASK, TUI_TASK], active="Konsole",
                    hover="Firefox" if 2.6 < t < 3.6 else None)
            k.caption(p, "⑥ opencode TUI", "the same palette in the terminal", ease_out((t - 0.3) / 0.6))
            # cursor heads for the ☀ tray icon to switch to day
            q = ease((t - 2.2) / 2.2)
            k.cursor(p, lerp(1200, W - 8 - 6 - 90 - 8 - 32 * 3 + 12, q), lerp(820, H - 34, q), t > 4.45)

        @self.seg("day", 5.2)
        def day(p, t, T):
            # a circle of day light spreads out from the ☀ icon
            night = self._full("night", T)
            dayimg = self._full("day", T)
            p.drawImage(0, 0, night)
            cx, cy = W - 8 - 6 - 90 - 8 - 32 * 3 + 15, H - 34
            r = ease(t / 1.4) * 2300
            path = QPainterPath()
            path.addEllipse(QPointF(cx, cy), r, r)
            p.save()
            p.setClipPath(path)
            p.drawImage(0, 0, dayimg)
            p.restore()
            if r < 2300:
                p.setPen(QPen(QColor(255, 255, 255, 160), 6))
                p.drawEllipse(QPointF(cx, cy), r, r)
            k.draw_petals(p, T, 0.6)
            k.caption(p, "uwu day ☀", "one click: every colour follows", ease_out((t - 1.0) / 0.6))
            k.cursor(p, cx - 3, cy + 2, t < 0.15)

        @self.seg("rotate", 6.4)
        def rotate(p, t, T):
            dayimg = self._full("day", T, petals=False)
            p.fillRect(QRectF(0, 0, W, H), QColor("#2a1630"))
            bg = self._blurred_day()
            p.setOpacity(ease(t / 0.8))
            p.drawImage(0, 0, bg)
            p.setOpacity(1)
            # the landscape screen turns 90° and shrinks to fit…
            q = ease((t - 0.3) / 1.4)
            ang = 90 * q
            fit = lerp(1.0, H / W, q)
            p.save()
            p.translate(W / 2, H / 2)
            p.rotate(ang)
            p.scale(fit, fit)
            p.translate(-W / 2, -H / 2)
            frame = QPainterPath()
            frame.addRoundedRect(QRectF(0, 0, W, H), 30 * q, 30 * q)
            p.setClipPath(frame)
            p.drawImage(0, 0, dayimg)
            p.restore()
            # …and becomes a proper portrait desktop; then a second rotated screen slides in with the lock screen
            pw, ph = H * 1080 / 1920, H
            sa = ease_out((t - 3.0) / 0.8)
            portrait = QRectF(W / 2 - pw / 2 - (pw / 2 + 30) * sa, 0, pw, ph)
            pa = ease((t - 1.6) / 0.6)
            if pa > 0:
                p.setOpacity(pa)
                path = QPainterPath()
                path.addRoundedRect(portrait, 30, 30)
                p.save()
                p.setClipPath(path)
                p.drawImage(portrait, self._portrait("day"))
                p.restore()
                p.setOpacity(1)
            if sa > 0:
                lock = self.clip("lockp", CLIPS / "q-lock-portrait.mp4", 1080, 1920)
                fr = lock.frame(int(max(0, t - 3.0) * FPS))
                r2 = QRectF(lerp(W + 50, W / 2 + 30, sa), 0, pw, ph)
                path = QPainterPath()
                path.addRoundedRect(r2, 30, 30)
                p.save()
                p.setClipPath(path)
                p.drawImage(r2, fr)
                p.restore()
            k.caption(p, "⑦ monitor turned 90°", "portrait wallpaper · portrait lock screen", ease_out((t - 1.6) / 0.6))

        @self.seg("lockin", 1.6, xfade=0.8)
        def lockin(p, t, T):
            p.drawImage(0, 0, self._full("night", T))
            k.caption(p, "Meta + L", "", ease_out((t - 0.2) / 0.4))

        @self.seg("lock", 14.6, xfade=0.6)
        def lock(p, t, T):
            c = self.clip("lock", CLIPS / "q-lock.mp4", W, H)
            p.drawImage(0, 0, c.frame(int(t * FPS)))
            k.caption(p, "⑧ lock screen", "sleepy bunny · heart password · wrong one pouts", ease_out((t - 0.5) / 0.6) - ease((t - 13.6) / 0.4))

        @self.seg("unlock", 2.4, xfade=0.5)
        def unlock(p, t, T):
            img = self._full("night", T)
            p.drawImage(0, 0, img)
            k.caption(p, "welcome back ♡", "", ease_out((t - 0.2) / 0.4) - ease((t - 2.0) / 0.4))

        @self.seg("end", 5.6, xfade=0.9)
        def end(p, t, T):
            p.drawImage(0, 0, self._blurred_night())
            p.fillRect(QRectF(0, 0, W, H), QColor(20, 6, 26, 110))
            k.draw_petals(p, T)
            b = 130
            hop = abs(math.sin(t * 3.0)) * 22
            k.bunny["love"].render(p, QRectF(W / 2 - b / 2, 170 - hop, b, b))
            a = ease_out(t / 0.8)
            p.setOpacity(a)
            k.text(p, QRectF(0, 310, W, 150), "uwu ♥", 130, "#ff8fc8")
            items = ["opencode web", "opencode TUI", "uwu IDE", "uwu-term", "Plasma theme", "lock screen", "splash", "wallpaper"]
            f = QFont("Nunito")
            f.setPixelSize(26)
            f.setWeight(QFont.ExtraBold)
            from PySide6.QtGui import QFontMetrics
            fm = QFontMetrics(f)
            widths = [fm.horizontalAdvance(s) + 48 for s in items]
            rows = [items[:4], items[4:]]
            y = 520
            idx = 0
            for row in rows:
                ws = [widths[items.index(s)] for s in row]
                total = sum(ws) + 18 * (len(row) - 1)
                x = W / 2 - total / 2
                for s, w_ in zip(row, ws):
                    ka = ease_out((t - 0.5 - idx * 0.12) / 0.5)
                    p.setOpacity(ka)
                    r = QRectF(x, y + (1 - ka) * 20, w_, 56)
                    path = QPainterPath()
                    path.addRoundedRect(r, 28, 28)
                    p.fillPath(path, QColor(255, 143, 200, 50))
                    p.setPen(QPen(QColor("#ff8fc8"), 2))
                    p.drawPath(path)
                    k.text(p, r, s, 26, "#ffeaf6", QFont.ExtraBold)
                    x += w_ + 18
                    idx += 1
                y += 76
            p.setOpacity(ease_out((t - 1.6) / 0.8))
            k.text(p, QRectF(0, 720, W, 50), "github.com/folkedevvy/opencode-web-uwu", 30, "#d6a8c8", QFont.Bold)
            p.setOpacity(1)
            p.fillRect(QRectF(0, 0, W, H), QColor(0, 0, 0, int(255 * ease((t - 4.8) / 0.8))))

    # ── cached stills of earlier scenes (windows stay open in the background) ──
    def _layer(self, key, draw):
        if key not in self.k._layers:
            img = QImage(W, H, QImage.Format_ARGB32_Premultiplied)
            img.fill(0)
            q = QPainter(img)
            q.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
            draw(q)
            q.end()
            self.k._layers[key] = img
        return self.k._layers[key]

    def _term_still(self, T=0):
        def d(q):
            img = Clip(SHOTS["term"], TERM_RECT.width(), TERM_RECT.height(), start=11.6).frame(0)
            self.k.app_window(q, img, TERM_RECT, 18)
        return self._layer("term-still", d)

    def _ide_still(self):
        def d(q):
            img = Clip(SHOTS["ide"], IDE_RECT.width(), IDE_RECT.height(), start=10.4).frame(0)
            self.k.app_window(q, img, IDE_RECT, 10)
        return self._layer("ide-still", d)

    def _web_still(self):
        def d(q):
            img = Clip(SHOTS["web"], WEB_RECT.width(), WEB_RECT.height(), start=7.4).frame(0)
            self.k.deco_window(q, "night", img, WEB_RECT, "opencode ♡ Firefox", False)
        return self._layer("web-still", d)

    def _windows(self, variant):
        def d(q):
            if variant == "night":
                q.drawImage(0, 0, self._term_still())
                q.drawImage(0, 0, self._ide_still())
                q.drawImage(0, 0, self._web_still())
                img = self.still(ROOT / "opencode" / "tui" / "screenshots" / "tui-diff-dark.png", TUI_RECT.width(), TUI_RECT.height())
                self.k.deco_window(q, "night", img, TUI_RECT, "opencode ♡ Konsole", True)
            else:
                self.k.app_window(q, self.still(ROOT / "terminal" / "uwu-term" / "screenshots" / "light.png", TERM_RECT.width(), TERM_RECT.height()), TERM_RECT, 18)
                self.k.app_window(q, self.still(ROOT / "vscode" / "screenshots" / "uwu-ide-light.png", IDE_RECT.width(), IDE_RECT.height()), IDE_RECT, 10)
                self.k.deco_window(q, "day", self.still(ROOT / "opencode" / "web" / "screenshots" / "session-light.png", WEB_RECT.width(), WEB_RECT.height()), WEB_RECT, "opencode ♡ Firefox", False)
                img = self.still(ROOT / "opencode" / "tui" / "screenshots" / "tui-diff-light.png", TUI_RECT.width(), TUI_RECT.height())
                self.k.deco_window(q, "day", img, TUI_RECT, "opencode ♡ Konsole", True)
            self.k.panel(q, variant, [TERM_TASK, IDE_TASK, WEB_TASK, TUI_TASK], active="Konsole")
        return self._layer(f"windows-{variant}", d)

    def _full(self, variant, T, petals=True):
        img = QImage(W, H, QImage.Format_ARGB32_Premultiplied)
        q = QPainter(img)
        q.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        q.drawImage(0, 0, self.k.wall[variant])
        if petals:
            self.k.draw_petals(q, T)
        q.drawImage(0, 0, self._windows(variant))
        q.end()
        return img

    def _portrait(self, variant):
        key = f"portrait-{variant}"
        if key not in self.k._layers:
            sc = pv.Scene(variant, 1080, 1920)
            sc.render(str(CLIPS / f"{key}.png"))
            self.k._layers[key] = QImage(str(CLIPS / f"{key}.png"))
        return self.k._layers[key]

    def _blurred_day(self):
        if "blur-day" not in self.k._layers:
            self.k._layers["blur-day"] = self.k.blurred(self.k.wall["day"])
        return self.k._layers["blur-day"]

    def _blurred_night(self):
        if "blur-night" not in self.k._layers:
            self.k._layers["blur-night"] = self.k.blurred(self.k.wall["night"], 10)
        return self.k._layers["blur-night"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "uwu-showcase.mp4"))
    ap.add_argument("--preview-every", type=float, default=0, help="also save a PNG every N seconds")
    ap.add_argument("--only", default="", help="render only these segments (comma separated)")
    a = ap.parse_args()
    app = QGuiApplication(sys.argv)  # noqa: F841
    kit = Kit()
    show = Show(kit)
    segs = [s for s in show.segments if not a.only or s[0] in a.only.split(",")]
    total = sum(int(s[1] * FPS) for s in segs)
    print(f"{len(segs)} segments, {total / FPS:.1f}s, {total} frames")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    frame = QImage(W, H, QImage.Format_ARGB32)
    prev = None
    n = 0
    for name, secs, fn, xfade in segs:
        count = int(secs * FPS)
        for i in range(count):
            t = i / FPS
            T = n / FPS
            frame.fill(QColor("#000000"))
            p = QPainter(frame)
            p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
            fn(p, t, T)
            if prev is not None and t < xfade:
                p.setOpacity(1 - ease(t / xfade))
                p.drawImage(0, 0, prev)
                p.setOpacity(1)
            p.end()
            ff.stdin.write(bytes(frame.constBits()))
            if a.preview_every and n % int(a.preview_every * FPS) == 0:
                frame.save(str(CLIPS / f"preview-{n // FPS:03d}-{name}.png"))
            n += 1
        prev = frame.copy()
        print(f"  {name:9s} done ({n / FPS:.1f}s)", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
