#!/usr/bin/env python3
"""The rest of the uwu Plasma theme (kde/plasma/):

* wallpaper "uwu sakura": a blossoming branch, drifting petals and a soft
  moon (night) or sun (day). Plasma picks the image closest to each screen's
  size, so portrait (rotated) monitors get portrait art, and the dark images
  are used automatically with a dark colour scheme.
* splash screen (the bunny hops while Plasma starts)
* global themes "uwu night" and "uwu day", tying colours, Plasma style,
  window decoration, splash and wallpaper together

Needs Pillow. Uses the petal sprites and bunny from tools/lockscreen_assets.py.
"""
import json
import math
import random
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "kde" / "plasma"
LOCK_ASSETS = ROOT / "kde" / "lockscreen" / "lockscreen" / "assets"

SIZES = [(1920, 1080), (2560, 1440), (3840, 2160), (3440, 1440), (1080, 1920), (1440, 2560), (2160, 3840)]

THEMES = {
    "night": dict(sky=["#170a20", "#2a1236", "#4a1f4f"], glow=(255, 214, 236), glow_at=(0.78, 0.2), glow_a=110,
                  branch=(74, 36, 66), blossom=[(255, 196, 222), (255, 170, 208), (255, 222, 236)],
                  centre=(255, 120, 180), stars=True, haze=(255, 143, 200)),
    "day": dict(sky=["#ffeaf4", "#ffd9ec", "#eedcff"], glow=(255, 250, 235), glow_at=(0.8, 0.16), glow_a=170,
                branch=(150, 92, 112), blossom=[(255, 214, 232), (255, 186, 216), (255, 240, 247)],
                centre=(240, 96, 150), stars=False, haze=(255, 255, 255)),
}


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def sky(w, h, stops):
    cols = [hexrgb(c) for c in stops]
    col = Image.new("RGB", (1, h))
    px = col.load()
    for y in range(h):
        t = y / max(1, h - 1)
        seg = min(int(t * (len(cols) - 1)), len(cols) - 2)
        u = t * (len(cols) - 1) - seg
        a, b = cols[seg], cols[seg + 1]
        px[0, y] = tuple(round(a[i] + (b[i] - a[i]) * u) for i in range(3))
    return col.resize((w, h))


def radial(size, rgb, alpha):
    """A soft round glow, size x size."""
    small = 128
    g = Image.new("L", (small, small))
    px = g.load()
    c = (small - 1) / 2
    for y in range(small):
        for x in range(small):
            d = min(1.0, math.hypot(x - c, y - c) / c)
            px[x, y] = round(alpha * (1 - d) ** 2.2)
    g = g.resize((size, size), Image.BICUBIC)
    layer = Image.new("RGBA", (size, size), rgb + (0,))
    layer.putalpha(g)
    return layer


def branch_layer(w, h, t, rnd, ss=2):
    """A blossoming sakura branch reaching in from the top-left corner."""
    W, H = w * ss, h * ss
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    unit = min(W, H)
    portrait = h > w
    clusters = []
    bark = t["branch"] + (255,)

    def grow(x, y, ang, length, width, depth):
        steps = max(6, int(length / (unit * 0.012)))
        px_, py_ = x, y
        bend = rnd.uniform(-0.35, 0.35)
        for i in range(1, steps + 1):
            a = ang + bend * (i / steps) + rnd.uniform(-0.05, 0.05)
            nx = px_ + math.cos(a) * length / steps
            ny = py_ + math.sin(a) * length / steps
            wd = max(unit * 0.0025, width * (1 - 0.45 * i / steps))
            d.line([(px_, py_), (nx, ny)], fill=bark, width=round(wd))
            d.ellipse((nx - wd / 2, ny - wd / 2, nx + wd / 2, ny + wd / 2), fill=bark)
            # blossoms all along the thinner branches
            if depth <= 3 and rnd.random() < 0.45:
                clusters.append((nx, ny, 0.8))
            px_, py_ = nx, ny
        clusters.append((px_, py_, 1.2))   # a full cluster at every tip
        if depth == 0:
            return
        for k in range(rnd.choice([2, 2, 3])):
            side = 1 if k % 2 == 0 else -1
            grow(px_, py_, a + side * rnd.uniform(0.3, 0.75), length * rnd.uniform(0.55, 0.75), width * 0.62, depth - 1)
        # little side twigs along the way
        if depth >= 2:
            for _ in range(2):
                f_ = rnd.uniform(0.3, 0.8)
                tx, ty = x + (px_ - x) * f_, y + (py_ - y) * f_
                grow(tx, ty, a + rnd.choice([-1, 1]) * rnd.uniform(0.6, 1.1), length * 0.35, width * 0.4, 0)

    if portrait:
        grow(-unit * 0.04, H * 0.04, math.radians(24), unit * 0.5, unit * 0.04, 4)
    else:
        grow(-unit * 0.04, unit * 0.06, math.radians(18), unit * 0.5, unit * 0.04, 4)

    def blossom(cx, cy, r):
        col = rnd.choice(t["blossom"])
        rot = rnd.uniform(0, math.tau)
        for i in range(5):
            a = rot + i * math.tau / 5
            px_, py_ = cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6
            d.ellipse((px_ - r * 0.52, py_ - r * 0.52, px_ + r * 0.52, py_ + r * 0.52), fill=col + (252,))
        d.ellipse((cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2), fill=t["centre"] + (255,))

    density = 0.6 if portrait else 1.0   # tall screens: the branch curls more, so keep it airy
    for (cx, cy, k) in clusters:
        if rnd.random() > density:
            continue
        for _ in range(int(rnd.uniform(2, 5) * k)):
            r = unit * rnd.uniform(0.009, 0.016) * k
            blossom(cx + rnd.uniform(-2.2, 2.2) * r, cy + rnd.uniform(-2.2, 2.2) * r, r)
    return layer.resize((w, h), Image.LANCZOS)


def moon(size, rgb):
    """A soft-edged moon (or sun) disc."""
    ss = 4
    m = Image.new("RGBA", (size * ss, size * ss), rgb + (0,))
    ImageDraw.Draw(m).ellipse((ss * 2, ss * 2, size * ss - ss * 2, size * ss - ss * 2), fill=rgb + (240,))
    return m.resize((size, size), Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(1, size / 60)))


def petal_sprites():
    return [Image.open(LOCK_ASSETS / f"petal-{i}.png").convert("RGBA") for i in range(4)], \
           [Image.open(LOCK_ASSETS / f"petal-blur-{i}.png").convert("RGBA") for i in range(3)]


def wallpaper(w, h, name, seed=3):
    t = THEMES[name]
    rnd = random.Random(seed + w * 7 + h)
    img = sky(w, h, t["sky"]).convert("RGBA")
    unit = min(w, h)
    # soft glows: the moon / sun, plus pastel haze
    g = radial(int(unit * 0.9), t["glow"], t["glow_a"])
    gx, gy = t["glow_at"]
    if h > w:
        gy = 0.12
    img.alpha_composite(g, (int(w * gx - g.width / 2), int(h * gy - g.height / 2)))
    disc = int(unit * 0.12)
    img.alpha_composite(moon(disc, t["glow"]), (int(w * gx - disc / 2), int(h * gy - disc / 2)))
    for (hx, hy, s, col) in [(0.15, 0.85, 1.1, (255, 143, 200)), (0.85, 0.9, 1.0, (199, 162, 255)), (0.5, 0.65, 0.8, t["haze"])]:
        hz = radial(int(unit * s), col, 60 if name == "night" else 90)
        img.alpha_composite(hz, (int(w * hx - hz.width / 2), int(h * hy - hz.height / 2)))
    # stars
    if t["stars"]:
        d = ImageDraw.Draw(img)
        for _ in range(int(w * h / 9000)):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.7)
            r = rnd.choice([0.6, 0.8, 1.0, 1.4]) * unit / 1080
            a = rnd.randint(60, 200)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 235, 245, a))
    # drifting petals: far (small, faint), the branch, then a few big soft ones in front
    crisp, soft = petal_sprites()
    for _ in range(int(w * h / 26000)):
        sp = rnd.choice(crisp)
        s = int(unit * rnd.uniform(0.008, 0.022))
        p = sp.resize((s, s), Image.LANCZOS).rotate(rnd.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        p.putalpha(p.getchannel("A").point(lambda v, k=rnd.uniform(0.35, 0.85): int(v * k)))
        img.alpha_composite(p, (int(rnd.uniform(0, w)), int(rnd.uniform(0, h))))
    br = branch_layer(w, h, t, rnd)
    shadow = br.filter(ImageFilter.GaussianBlur(unit / 220))
    sh = Image.new("RGBA", br.size, (40, 8, 30, 0))
    sh.putalpha(shadow.getchannel("A").point(lambda v: v // 3))
    img.alpha_composite(sh, (int(unit * 0.004), int(unit * 0.008)))
    img.alpha_composite(br)
    for _ in range(int(w * h / 900000) + 2):
        sp = rnd.choice(soft)
        s = int(unit * rnd.uniform(0.05, 0.1))
        p = sp.resize((s, s), Image.LANCZOS).rotate(rnd.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        p.putalpha(p.getchannel("A").point(lambda v: int(v * 0.55)))
        img.alpha_composite(p, (int(rnd.uniform(0.1, 0.95) * w), int(rnd.uniform(0.25, 0.95) * h)))
    return img.convert("RGB")


def write_wallpaper():
    d = OUT / "wallpapers" / "uwu-sakura"
    for sub in ("images", "images_dark"):
        (d / "contents" / sub).mkdir(parents=True, exist_ok=True)
    for (w, h) in SIZES:
        wallpaper(w, h, "day").save(d / "contents" / "images" / f"{w}x{h}.jpg", quality=90, optimize=True, progressive=True)
        wallpaper(w, h, "night").save(d / "contents" / "images_dark" / f"{w}x{h}.jpg", quality=90, optimize=True, progressive=True)
        print("  wallpaper", w, h)
    shot = Image.open(d / "contents" / "images_dark" / "1920x1080.jpg").resize((400, 225), Image.LANCZOS)
    shot.save(d / "contents" / "screenshot.png")
    (d / "metadata.json").write_text(json.dumps({
        "KPlugin": {
            "Authors": [{"Name": "uwu"}],
            "Id": "uwu-sakura",
            "License": "MIT",
            "Name": "uwu sakura",
        },
        "X-KDE-PlasmaImageWallpaper-AccentColor": "#ff8fc8",
    }, indent=4) + "\n")


# ─────────────────────────────── splash screen ───────────────────────────────
SPLASH_QML = r'''/*
    ♡ uwu splash screen: the bunny hops while Plasma starts.
    ksplashqml sets `stage` from 1 to 6 as startup progresses.
    Only plain QtQuick, so it loads on any Plasma 6.
*/
import QtQuick

Rectangle {
    id: root
    property int stage
    readonly property real u: Math.min(width, height) / 1080

    gradient: Gradient {
        GradientStop { position: 0; color: "@TOP@" }
        GradientStop { position: 0.55; color: "@MID@" }
        GradientStop { position: 1; color: "@BOTTOM@" }
    }

    FontLoader { id: nunito; source: "fonts/Nunito-900.ttf" }

    // drifting petals
    Repeater {
        model: 26
        Image {
            id: petal
            property real start: Math.random()
            property real t: start
            property real x0: Math.random() * root.width * 1.1 - root.width * 0.1
            property real sway: (20 + Math.random() * 40) * root.u
            property real phase: Math.random() * 6.28
            source: "images/petal-" + (index % 4) + ".png"
            width: (14 + Math.random() * 16) * root.u
            height: width
            opacity: 0.75 * Math.min(1, t * 10, (1 - t) * 10)
            x: x0 + t * 160 * root.u + Math.sin(t * 9 + phase) * sway
            y: -height + t * (root.height + 2 * height)
            rotation: t * 540 + phase * 50
            NumberAnimation on t {
                id: fall
                from: petal.start
                to: 1
                duration: (1 - petal.start) * 9000 + 1
                onFinished: { petal.start = 0; petal.x0 = Math.random() * root.width; fall.duration = 9000; fall.restart(); }
            }
        }
    }

    Item {
        id: content
        anchors.centerIn: parent
        width: 360 * root.u
        height: 330 * root.u
        opacity: 0
        Component.onCompleted: fadeIn.start()
        NumberAnimation on opacity { id: fadeIn; running: false; to: 1; duration: 600 }

        // the bunny, hopping
        Image {
            id: bunny
            source: root.stage >= 6 ? "images/bunny-love.svg" : "images/bunny-awake.svg"
            sourceSize.width: 256
            sourceSize.height: 256
            width: 170 * root.u
            height: width
            anchors.horizontalCenter: parent.horizontalCenter
            property real hop: 0
            y: 40 * root.u - hop * 34 * root.u
            SequentialAnimation on hop {
                loops: Animation.Infinite
                NumberAnimation { to: 1; duration: 320; easing.type: Easing.OutQuad }
                NumberAnimation { to: 0; duration: 420; easing.type: Easing.OutBounce }
                PauseAnimation { duration: 260 }
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 235 * root.u
            text: root.stage >= 6 ? "welcome back ♡" : "getting cozy…"
            color: "@TEXT@"
            font.family: nunito.status === FontLoader.Ready ? nunito.name : "sans-serif"
            font.weight: Font.Black
            font.pixelSize: 30 * root.u
        }

        // hearts fill up as Plasma starts
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 290 * root.u
            spacing: 10 * root.u
            Repeater {
                model: 6
                Text {
                    text: index < root.stage ? "♥" : "♡"
                    color: index < root.stage ? "#ff5fae" : "@MUTED@"
                    font.pixelSize: 26 * root.u
                    scale: index === root.stage - 1 ? 1.25 : 1
                    Behavior on scale { NumberAnimation { duration: 300; easing.type: Easing.OutBack } }
                }
            }
        }
    }

    onStageChanged: if (stage >= 6) outro.start()
    NumberAnimation { id: outro; target: content; property: "scale"; to: 1.08; duration: 400; easing.type: Easing.OutBack }
}
'''


def write_lnf(variant):
    night = variant == "night"
    pid = f"org.uwu.{variant}.desktop"
    d = OUT / "look-and-feel" / pid
    splash = d / "contents" / "splash"
    (splash / "images").mkdir(parents=True, exist_ok=True)
    (splash / "fonts").mkdir(parents=True, exist_ok=True)
    qml = SPLASH_QML
    for k, v in (dict(TOP="#170a20", MID="#2a1236", BOTTOM="#4a1f4f", TEXT="#ffeaf6", MUTED="#c79dbb") if night else
                 dict(TOP="#ffeaf4", MID="#ffd9ec", BOTTOM="#eedcff", TEXT="#57264c", MUTED="#c78fb0")).items():
        qml = qml.replace(f"@{k}@", v)
    (splash / "Splash.qml").write_text(qml)
    for f in ["bunny-awake.svg", "bunny-love.svg"] + [f"petal-{i}.png" for i in range(4)]:
        shutil.copy(LOCK_ASSETS / f, splash / "images" / f)
    fonts = LOCK_ASSETS.parent / "fonts"
    shutil.copy(fonts / "Nunito-900.ttf", splash / "fonts")
    shutil.copy(fonts / "OFL.txt", splash / "fonts")

    (d / "contents" / "defaults").write_text(f"""# ♡ uwu {variant}: what applying this global theme changes
[kdeglobals][General]
ColorScheme={'UwuNight' if night else 'UwuDay'}

[plasmarc][Theme]
name=uwu

[Wallpaper]
Image=uwu-sakura

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__uwu-{variant}

[ksplashrc][KSplash]
Engine=KSplashQML
Theme={pid}
""")
    (d / "metadata.json").write_text(json.dumps({
        "KPackageStructure": "Plasma/LookAndFeel",
        "KPlugin": {
            "Authors": [{"Name": "uwu"}],
            "Category": "",
            "Description": ("Strawberry-milk night" if night else "Sakura cream day")
                           + ": candy panels, pastel windows, sakura wallpaper and a hopping bunny ♡",
            "Id": pid,
            "License": "MIT",
            "Name": f"uwu {variant}",
            "Website": "https://github.com/folkedevvy/opencode-web-uwu",
        },
        "Keywords": "Desktop;Workspace;Appearance;Look and Feel;kawaii;uwu;sakura;pastel;",
    }, indent=4, ensure_ascii=False) + "\n")
    return d


def main():
    write_wallpaper()
    for v in ("night", "day"):
        print("wrote", write_lnf(v))


if __name__ == "__main__":
    main()
