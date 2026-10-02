#!/usr/bin/env python3
"""Generate the falling-sakura SVG tiles used by chrome/userContent.css.

Each tile is a self-animating SVG (SMIL): every petal falls exactly one tile
height per cycle and is drawn twice (at y and y - H), so when the tile repeats
across the screen the petals flow over tile seams without popping. Sway,
spin and the 3D "flip" all use periods that divide the fall period, so the
loop is seamless too.

    python3 tools/petals.py          # rewrites the PETALS block in userContent.css
"""
import random
import re
import urllib.parse
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "chrome" / "userContent.css"

# A sakura petal: rounded teardrop with the little notch at the tip.
PETAL = (
    "M0 -7 C1.5 -10 5 -11.5 6.5 -8.5 C8.8 -4 6.5 4 0 11.5 "
    "C-6.5 4 -8.8 -4 -6.5 -8.5 C-5 -11.5 -1.5 -10 0 -7 Z"
)
# a faint lighter crease down the middle sells the "petal" read at small sizes
VEIN = "M0 -5 C.6 0 .4 5 0 9"


def tile(seed, w, h, count, scale, period, colors, opacity):
    rnd = random.Random(seed)
    defs = [
        f'<radialGradient id="g{i}" cx=".5" cy=".7" r=".8">'
        f'<stop offset="0" stop-color="{inner}"/><stop offset="1" stop-color="{outer}"/>'
        "</radialGradient>"
        for i, (inner, outer) in enumerate(colors)
    ]
    defs.append(
        f'<g id="p"><path d="{PETAL}"/>'
        f'<path d="{VEIN}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width=".9" stroke-linecap="round"/></g>'
    )
    petals = []
    for n in range(count):
        # spread petals evenly across the tile, with jitter
        x = (n + 0.5) * w / count + rnd.uniform(-w / count / 3, w / count / 3)
        x = max(30, min(w - 30, x))
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
        body = (
            f'<g transform="scale({s:.2f})">'
            f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="{spin}" '
            f'dur="{spin_dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="1 1;1 .25;1 1" '
            f'dur="{flip_dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<use href="#p" fill="url(#g{g})"/></g></g></g>'
        )
        petals.append(
            f"<g><animateMotion path=\"{path}\" dur=\"{dur:.2f}s\" begin=\"{begin:.2f}s\" repeatCount=\"indefinite\"/>"
            f"{body}<g transform=\"translate(0 {-h})\">{body}</g></g>"
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<defs>{''.join(defs)}</defs><g opacity=\"{opacity}\">{''.join(petals)}</g></svg>"
    )
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/;,.-_()'\"") .replace('"', "'") + '")'


PINKS = [("#ffe6f1", "#ff8fc2"), ("#ffd4e7", "#f9679f"), ("#fff0f6", "#ffa9cf"), ("#ffc9e0", "#ef5d97")]

LAYERS = {
    # far: small, pale, slow
    "--uwu-petals-far": tile(7, 610, 700, 10, (.7, 1.0), (16, 24), PINKS, .6),
    # near: bigger, brighter, a bit quicker
    "--uwu-petals-near": tile(42, 1010, 900, 7, (1.3, 1.9), (10, 15), PINKS, .92),
}


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


if __name__ == "__main__":
    main()
