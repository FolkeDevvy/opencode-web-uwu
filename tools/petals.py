#!/usr/bin/env python3
"""Generate the falling-sakura SVG tiles used by chrome/userContent.css.

Each tile is a self-animating SVG (SMIL): every petal falls exactly one tile
height per cycle and is drawn twice (at y and y - H), so when the tile repeats
across the screen the petals flow over tile seams without popping. Sway,
spin and the 3D "flip" all use periods that divide the fall period, so the
loop is seamless too.

The wind lives inside the SVG as well: the whole layer slides sideways by a
whole number of tile widths per WIND cycle (petals are also drawn at x - k*W),
with an ease-in-out spline for calm -> gust -> calm. Doing it here instead of
animating CSS background-position matters: browsers re-rasterise huge
repeating SVG backgrounds when their position animates, which made the
petals visibly hitch every second or so.

The opencode web theme no longer uses these animated tiles: SMIL animation
inside a CSS background makes Firefox re-rasterise the whole layer on the
main thread every frame, which made the page crawl. It uses static_tile()
instead: still pictures of petals, moved by compositor-only CSS transform
animations (see the petals section of userContent.css). VS Code keeps the
animated tiles.

    python3 tools/petals.py   # rewrites the PETALS block in userContent.css
                              # and vscode/uwu-code/petals.js
"""
import random
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "opencode" / "web" / "chrome" / "userContent.css"
VSCODE = ROOT / "vscode" / "uwu-code" / "petals.js"

WIND = 26  # seconds per calm -> gust -> calm cycle (lower = windier)

# A sakura petal: rounded teardrop with the little notch at the tip.
PETAL = (
    "M0 -7 C1.5 -10 5 -11.5 6.5 -8.5 C8.8 -4 6.5 4 0 11.5 "
    "C-6.5 4 -8.8 -4 -6.5 -8.5 C-5 -11.5 -1.5 -10 0 -7 Z"
)
# a faint lighter crease down the middle sells the "petal" read at small sizes
VEIN = "M0 -5 C.6 0 .4 5 0 9"


def tile(seed, w, h, count, scale, period, colors, opacity, blur=0, wind_tiles=1, soft=False):
    """soft=True fakes the out-of-focus look with a gradient that fades to
    transparent at the edges instead of an SVG blur filter, which is far
    cheaper to re-rasterise every frame (used for the VS Code editor)."""
    rnd = random.Random(seed)
    if soft:
        defs = [
            f'<radialGradient id="g{i}" cx=".5" cy=".55" r=".62">'
            f'<stop offset="0" stop-color="{inner}"/><stop offset=".5" stop-color="{outer}" stop-opacity=".85"/>'
            f'<stop offset="1" stop-color="{outer}" stop-opacity="0"/></radialGradient>'
            for i, (inner, outer) in enumerate(colors)
        ]
    else:
        defs = [
            f'<radialGradient id="g{i}" cx=".5" cy=".7" r=".8">'
            f'<stop offset="0" stop-color="{inner}"/><stop offset="1" stop-color="{outer}"/>'
            "</radialGradient>"
            for i, (inner, outer) in enumerate(colors)
        ]
    if blur:
        defs.append(
            f'<filter id="b" x="-60%" y="-60%" width="220%" height="220%">'
            f'<feGaussianBlur stdDeviation="{blur}"/></filter>'
        )
    vein = "" if soft else (
        f'<path d="{VEIN}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width=".9" stroke-linecap="round"/>'
    )
    defs.append(f'<g id="p"><path d="{PETAL}"/>{vein}</g>')
    petals = []
    for n in range(count):
        # spread petals evenly across the tile, with jitter
        x = (n + 0.5) * w / count + rnd.uniform(-w / count / 3, w / count / 3)
        margin = 12 * scale[1] + 26  # keep big petals from being clipped at tile seams
        x = max(margin, min(w - margin, x))
        sway = rnd.uniform(14, 26)
        dur = rnd.uniform(*period)
        begin = -rnd.uniform(0, dur)
        s = rnd.uniform(*scale)
        g = rnd.randrange(len(colors))
        spin = rnd.choice([1, -1]) * 360
        spin_dur = dur / rnd.choice([2, 3, 4])
        flip_dur = dur / rnd.choice([4, 5, 6])
        # wavy path, one full tile tall, ends at the same x it started from
        q = h / 4
        path = (
            f"M{x:.1f} 0 C{x + sway:.1f} {q * .5:.1f} {x + sway:.1f} {q * 1.5:.1f} {x:.1f} {q * 2:.1f} "
            f"S{x - sway:.1f} {q * 3.5:.1f} {x:.1f} {h}"
        )
        filt = ' filter="url(#b)"' if blur else ""
        body = (
            f'<g transform="scale({s:.2f})"{filt}>'
            f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="{spin}" '
            f'dur="{spin_dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="1 1;1 .25;1 1" '
            f'dur="{flip_dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<use href="#p" fill="url(#g{g})"/></g></g></g>'
        )
        motion = (
            f"<g><animateMotion path=\"{path}\" dur=\"{dur:.2f}s\" begin=\"{begin:.2f}s\" repeatCount=\"indefinite\"/>"
            f"{body}<g transform=\"translate(0 {-h})\">{body}</g></g>"
        )
        # horizontal copies so the wind can carry petals across whole tiles seamlessly
        petals.append(motion + "".join(
            f'<g transform="translate({-k * w} 0)">{motion}</g>' for k in range(1, wind_tiles + 1)
        ))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<defs>{''.join(defs)}</defs><g opacity=\"{opacity}\">"
        f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{wind_tiles * w} 0" '
        f'keyTimes="0;1" calcMode="spline" keySplines=".45 0 .55 1" dur="{WIND}s" repeatCount="indefinite"/>'
        f"{''.join(petals)}</g></g></svg>"
    )
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/;,.-_()'\"") .replace('"', "'") + '")'


def static_tile(seed, w, h, count, scale, colors, opacity, blur=0):
    """A still picture of petals, scattered and tumbled, that tiles seamlessly.

    Petals near an edge are drawn again on the opposite side, so they flow over
    tile seams. Nothing in here animates: the CSS slides the whole layer with a
    transform, which the compositor does without repainting anything. Blur is
    fine here, as it's only rasterised once.
    """
    rnd = random.Random(seed)
    defs = [
        f'<radialGradient id="g{i}" cx=".5" cy=".7" r=".8">'
        f'<stop offset="0" stop-color="{inner}"/><stop offset="1" stop-color="{outer}"/>'
        "</radialGradient>"
        for i, (inner, outer) in enumerate(colors)
    ]
    if blur:
        defs.append(
            f'<filter id="b" x="-60%" y="-60%" width="220%" height="220%">'
            f'<feGaussianBlur stdDeviation="{blur}"/></filter>'
        )
    vein = f'<path d="{VEIN}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width=".9" stroke-linecap="round"/>'
    defs.append(f'<g id="p"><path d="{PETAL}"/>{vein}</g>')
    # spread petals on a jittered grid so they never clump
    cols = max(1, round((count * w / h) ** 0.5))
    rows = max(1, -(-count // cols))
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    rnd.shuffle(cells)
    petals = []
    for c, r in cells[:count]:
        x = (c + rnd.uniform(0.15, 0.85)) * w / cols
        y = (r + rnd.uniform(0.15, 0.85)) * h / rows
        s = rnd.uniform(*scale)
        rot = rnd.uniform(0, 360)
        flip = rnd.uniform(0.35, 1.0)    # a petal seen edge-on, mid-tumble
        g = rnd.randrange(len(colors))
        filt = ' filter="url(#b)"' if blur else ""
        body = (f'<g transform="rotate({rot:.0f}) scale({s * flip:.2f} {s:.2f})"{filt}>'
                f'<use href="#p" fill="url(#g{g})"/></g>')
        reach = 14 * s + 3 * blur + 4
        for dx in (-w, 0, w):
            for dy in (-h, 0, h):
                px, py = x + dx, y + dy
                if -reach < px < w + reach and -reach < py < h + reach:
                    petals.append(f'<g transform="translate({px:.1f} {py:.1f})">{body}</g>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<defs>{''.join(defs)}</defs><g opacity=\"{opacity}\">{''.join(petals)}</g></svg>"
    )
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/;,.-_()'\"") .replace('"', "'") + '")'


PINKS = [("#ffe6f1", "#ff8fc2"), ("#ffd4e7", "#f9679f"), ("#fff0f6", "#ffa9cf"), ("#ffc9e0", "#ef5d97")]

# The web theme's layers. Tile sizes all divide 1000px: the CSS slides each layer
# down by exactly 1000px per loop, so every layer wraps seamlessly.
LAYERS = {
    # front: a few big, soft, out-of-focus petals
    "--uwu-petals-front": static_tile(99, 1000, 1000, 3, (3.4, 4.6), PINKS, .62, blur=1.1),
    # near: bigger, brighter
    "--uwu-petals-near": static_tile(42, 1000, 1000, 9, (1.3, 1.9), PINKS, .92),
    # far: small and pale
    "--uwu-petals-far": static_tile(7, 500, 500, 7, (.7, 1.0), PINKS, .6),
}

# background-image stacking order (first = on top) and tile sizes
ORDER = [("--uwu-petals-front", 1000, 1000), ("--uwu-petals-near", 1000, 1000), ("--uwu-petals-far", 500, 500)]


# The "classic" editor petals (uwu.petals.style = classic). The editor repaints
# these every frame on the CPU, so they get a front layer without the blur
# filter (same seed = same petals and motion).
# Smaller tiles are also much cheaper: the browser re-paints a whole tile every
# frame, so cost follows tile area. Same petal density, just repeated more.
VSCODE_LAYERS = [
    (tile(99, 840, 700, 2, (2.8, 3.6), (9, 12), PINKS, .58, wind_tiles=2, soft=True), 840, 700),
    (tile(42, 560, 520, 3, (1.3, 1.9), (10, 15), PINKS, .92, wind_tiles=2), 560, 520),
    (tile(7, 420, 480, 5, (.7, 1.0), (16, 24), PINKS, .6), 420, 480),
]


# Still pictures for VS Code and uwu-term (front, near, far), the same as the web
# theme's. They're nearly free to draw; motion comes from a compositor-only CSS
# animation that slides the whole layer by 1000px per loop (all sizes divide 1000).
STATIC_LAYERS = [
    (LAYERS["--uwu-petals-front"], 1000, 1000),
    (LAYERS["--uwu-petals-near"], 1000, 1000),
    (LAYERS["--uwu-petals-far"], 500, 500),
]


def write_vscode():
    import json
    pack = lambda ls: [{"url": url, "width": w, "height": h} for url, w, h in ls]
    VSCODE.parent.mkdir(parents=True, exist_ok=True)
    VSCODE.write_text(
        "// Generated by tools/petals.py. Do not edit by hand.\n"
        "// light: still sakura tiles (front, near, far), slid by a CSS animation; nearly free.\n"
        "// classic: self-animating SVG tiles (petals fall, spin and flip inside the image).\n"
        "//   Pretty, but the editor repaints them every frame, which costs a lot of CPU.\n"
        f"module.exports = {{\n light: {json.dumps(pack(STATIC_LAYERS), indent=1)},\n"
        f" classic: {json.dumps(pack(VSCODE_LAYERS), indent=1)},\n}};\n"
    )


def main():
    block = "\n".join(f"  {k}: {v} !important;" for k, v in LAYERS.items())
    css = CSS.read_text()
    css, n = re.subn(
        r"(PETALS:BEGIN \*/\n).*?(  /\* PETALS:END \*/)",
        lambda m: m.group(1) + block + "\n" + m.group(2),
        css,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("PETALS:BEGIN/END markers not found in userContent.css")
    CSS.write_text(css)
    print(f"wrote {len(block)} bytes of petals")
    write_vscode()
    print("wrote", VSCODE)


if __name__ == "__main__":
    main()
