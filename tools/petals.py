#!/usr/bin/env python3
"""Sakura petal tiles shared by the asset generators.

static_tile() draws a still picture of scattered, tumbled petals that tiles
seamlessly. uwu-term slides a layer of these with a compositor-only CSS
transform animation, which is nearly free to draw (see #frame::before in
terminal/uwu-term/renderer/style.css). tools/kawaii_assets.py embeds them and
tools/lockscreen_assets.py reuses the palette. This file has no output of its own.
"""
import random
import urllib.parse

# A sakura petal: rounded teardrop with the little notch at the tip.
PETAL = (
    "M0 -7 C1.5 -10 5 -11.5 6.5 -8.5 C8.8 -4 6.5 4 0 11.5 "
    "C-6.5 4 -8.8 -4 -6.5 -8.5 C-5 -11.5 -1.5 -10 0 -7 Z"
)
# a faint lighter crease down the middle sells the "petal" read at small sizes
VEIN = "M0 -5 C.6 0 .4 5 0 9"


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

# Still layers (near, far) as (data URL, tile width, tile height). The sizes divide
# 1000px: the CSS slides the layer down by exactly 1000px per loop, so it wraps seamlessly.
STATIC_LAYERS = [
    # near: bigger, brighter
    (static_tile(42, 1000, 1000, 9, (1.3, 1.9), PINKS, .92), 1000, 1000),
    # far: small and pale
    (static_tile(7, 500, 500, 7, (.7, 1.0), PINKS, .6), 500, 500),
]
