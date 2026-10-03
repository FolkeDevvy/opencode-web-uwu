#!/usr/bin/env python3
"""Draw the uwu lock screen's artwork (kde/lockscreen/lockscreen/assets).

* the mochi bunny from the uwu IDE / uwu-term, in four moods:
  sleepy (idle), awake (typing), sad (wrong password) and love (unlocking)
* sakura petal sprites for the Qt particle system: crisp ones for the
  falling layer, and big pre-blurred ones that drift past in front
* the uwu logo

Needs Pillow.  Run from anywhere: python3 tools/lockscreen_assets.py
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from kawaii_assets import LOGO, svg
from petals import PINKS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "kde" / "lockscreen" / "lockscreen" / "assets"

# ─────────────────────────────── the bunny ───────────────────────────────
BODY = (
    '<defs><radialGradient id="b" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff"/>'
    '<stop offset="1" stop-color="#ffe0ef"/></radialGradient></defs>'
    '<ellipse cx="60" cy="112" rx="34" ry="6" fill="#ff8fc8" opacity=".25"/>'
    '<path d="M38 40C30 14 36 2 44 4s10 18 6 34M82 40c8-26 2-38-6-36s-10 18-6 34" fill="url(#b)" stroke="#ff8fc8" stroke-width="3"/>'
    '<path d="M42 30c-3-12-1-19 3-19M78 30c3-12 1-19-3-19" stroke="#ffb3d9" stroke-width="4" stroke-linecap="round" fill="none"/>'
    '<ellipse cx="60" cy="74" rx="44" ry="38" fill="url(#b)" stroke="#ff8fc8" stroke-width="3"/>'
    '<ellipse cx="38" cy="82" rx="7" ry="4.5" fill="#ff9fcf" opacity=".7"/>'
    '<ellipse cx="82" cy="82" rx="7" ry="4.5" fill="#ff9fcf" opacity=".7"/>'
)
INK = 'stroke="#57264c" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" fill="none"'
SPARKLE = '<path d="M86 38l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" fill="#ffe59a"/>'


def heart(x, y, s, fill):
    return (f'<path transform="translate({x} {y}) scale({s})" fill="{fill}" '
            'd="M0 3C-1.5 0-6-1-6 2.5c0 2.6 3 4.6 6 7 3-2.4 6-4.4 6-7C6-1 1.5 0 0 3z"/>')


MOODS = {
    # ^ ^ happy eyes + little smile (same face as the IDE mascot)
    "awake": '<path d="M44 70c2-4 8-4 10 0M66 70c2-4 8-4 10 0" ' + INK + '/>'
             '<path d="M55 80c2 3 8 3 10 0" ' + INK + '/>' + SPARKLE,
    # u u closed eyes, tiny mouth, and a floating zzz
    "sleepy": '<path d="M44 71c2 3 8 3 10 0M66 71c2 3 8 3 10 0" ' + INK + '/>'
              '<ellipse cx="60" cy="82" rx="2.6" ry="2" fill="#57264c"/>'
              '<text x="88" y="40" font-family="sans-serif" font-weight="900" font-size="15" fill="#c7a2ff">z</text>'
              '<text x="99" y="28" font-family="sans-serif" font-weight="900" font-size="11" fill="#c7a2ff" opacity=".8">z</text>'
              '<text x="107" y="18" font-family="sans-serif" font-weight="900" font-size="8" fill="#c7a2ff" opacity=".6">z</text>',
    # > < squeezed eyes, wobbly frown and a tear
    "sad": '<path d="M44 66l9 4-9 4M76 66l-9 4 9 4" ' + INK + '/>'
           '<path d="M54 84c2-3 4-3 6 0s4 3 6 0" ' + INK + '/>'
           '<path d="M42 77c-2 4-3 7-1 9s5 0 4-3c-.5-2-1.6-4-3-6z" fill="#9fd8ff" stroke="#6fb8f0" stroke-width="1"/>',
    # heart eyes, open smile, floating hearts
    "love": heart(49, 64, 1.25, "#ff5fae") + heart(71, 64, 1.25, "#ff5fae")
            + '<path d="M53 79c2 6 12 6 14 0z" fill="#57264c"/><path d="M56 82c2 2 6 2 8 0" stroke="#ff8fc8" stroke-width="2" fill="none" stroke-linecap="round"/>'
            + heart(96, 30, 1.3, "#ff8fc8") + heart(18, 36, 1, "#c7a2ff") + heart(104, 52, .8, "#ffb3d9"),
}


def mascot(mood):
    return svg(BODY + MOODS[mood], size=120)


# ─────────────────────────────── petal sprites ───────────────────────────────
# the same teardrop-with-a-notch petal as tools/petals.py, as cubic beziers
SEGMENTS = [
    ((0, -7), (1.5, -10), (5, -11.5), (6.5, -8.5)),
    ((6.5, -8.5), (8.8, -4), (6.5, 4), (0, 11.5)),
    ((0, 11.5), (-6.5, 4), (-8.8, -4), (-6.5, -8.5)),
    ((-6.5, -8.5), (-5, -11.5), (-1.5, -10), (0, -7)),
]


def bezier(p0, p1, p2, p3, n=24):
    for i in range(n):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        yield (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def outline(scale, cx, cy):
    return [(cx + x * scale, cy + y * scale) for seg in SEGMENTS for x, y in bezier(*seg)]


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def petal(size, light, deep, blur=0.0, pad=0):
    """A petal filling `size` px, shaded from a light centre to a deeper edge."""
    ss = 4  # supersample
    full = (size + 2 * pad) * ss
    # transparent pixels carry the petal colour, so blurring/scaling never adds a dark fringe
    img = Image.new("RGBA", (full, full), hex_rgb(deep) + (0,))
    scale = size * ss / 24.0
    c = full / 2
    shape = Image.new("L", (full, full), 0)
    ImageDraw.Draw(shape).polygon(outline(scale, c, c + scale * .3), fill=255)
    # radial-ish shading: blend deep -> light towards the upper middle
    grad = Image.new("RGBA", (full, full))
    gl, gd = hex_rgb(light), hex_rgb(deep)
    px = grad.load()
    for y in range(full):
        for x in range(full):
            d = min(1.0, math.hypot((x - c) / (full * .42), (y - c * .8) / (full * .5)))
            t = d ** 1.4
            px[x, y] = tuple(round(gl[i] * (1 - t) + gd[i] * t) for i in range(3)) + (255,)
    img.paste(grad, (0, 0), shape)
    # the faint lighter crease down the middle
    vein = [(c + x * scale, c + scale * .3 + y * scale) for x, y in bezier((0, -5), (.6, 0), (.4, 5), (0, 9))]
    crease = Image.new("RGBA", img.size, (255, 255, 255, 0))
    ImageDraw.Draw(crease).line(vein, fill=(255, 255, 255, 120), width=max(1, round(scale * .45)))
    crease.putalpha(Image.composite(crease.getchannel("A"), Image.new("L", img.size, 0), shape))
    img = Image.alpha_composite(img, crease)
    img = img.resize((size + 2 * pad, size + 2 * pad), Image.LANCZOS)
    if blur:
        img = blur_premultiplied(img, blur)
    return img


def blur_premultiplied(img, radius):
    """Gaussian blur that doesn't pull dark fringes in from transparent pixels."""
    r, g, b, a = img.split()
    # multiply colour by alpha, blur everything, then divide back out
    pre = [ImageChops.multiply(ch, a) for ch in (r, g, b)]
    pre = [ch.filter(ImageFilter.GaussianBlur(radius)) for ch in pre]
    a2 = a.filter(ImageFilter.GaussianBlur(radius))
    out = []
    for ch in pre:
        out.append(Image.frombytes("L", img.size, bytes(
            min(255, round(c * 255 / al)) if al else 0 for c, al in zip(ch.tobytes(), a2.tobytes()))))
    return Image.merge("RGBA", (*out, a2))


def write_petals():
    # crisp falling petals, one per palette pair
    for i, (light, deep) in enumerate(PINKS):
        petal(48, light, deep).save(OUT / f"petal-{i}.png", optimize=True)
    # big soft ones that drift past in front (bokeh)
    for i, (light, deep) in enumerate(PINKS[:3]):
        petal(120, light, deep, blur=9, pad=24).save(OUT / f"petal-blur-{i}.png", optimize=True)


def write_dots():
    # polka-dot tiles for the background (one dot per 56px tile, drawn small at runtime)
    for name, rgba in (("night", (255, 143, 200, 26)), ("day", (255, 95, 174, 38))):
        ss = 4
        tile = Image.new("RGBA", (56 * ss, 56 * ss), (0, 0, 0, 0))
        r = 3.2 * ss
        c = 28 * ss
        ImageDraw.Draw(tile).ellipse((c - r, c - r, c + r, c + r), fill=rgba)
        tile.resize((56, 56), Image.LANCZOS).save(OUT / f"dots-{name}.png")


def write_blobs():
    # soft round colour glows for the background (radial gradient, fully transparent edge)
    size = 256
    for name, hexc in (("pink", "#ff8fc8"), ("lav", "#c7a2ff"), ("mint", "#8ff5cf"), ("butter", "#ffe59a")):
        rgb = hex_rgb(hexc)
        img = Image.new("RGBA", (size, size))
        px = img.load()
        c = (size - 1) / 2
        for y in range(size):
            for x in range(size):
                d = min(1.0, math.hypot(x - c, y - c) / c)
                a = (1 - d) ** 2 * (3 - 2 * (1 - d)) if d < 1 else 0  # smooth falloff
                px[x, y] = rgb + (round(255 * a * (1 - d * .15)),)
        img.save(OUT / f"blob-{name}.png", optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mood in MOODS:
        (OUT / f"bunny-{mood}.svg").write_text(mascot(mood))
    (OUT / "logo.svg").write_text(LOGO)
    random.seed(7)
    write_petals()
    write_dots()
    write_blobs()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
