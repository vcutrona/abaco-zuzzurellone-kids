#!/usr/bin/env python3
"""Generate the game's icons: the green A cube and the purple Z cube of the logo.

Writes icons/icon.svg (app icon source), updates the inline SVG favicon in index.html
and renders the PNG icons (192, 512 and the 180px apple-touch-icon) with rsvg-convert.

The letters become SVG paths taken from Baloo 2 ExtraBold, so the icons look the same
where the font isn't available. The font must be a .ttf or .woff file: the .woff2 files
in fonts/ need the brotli module, which fontTools only uses if it is installed.

Usage:
    pip install fonttools
    python3 tools/make-icons.py path/to/baloo-2-latin-800-normal.woff

The .woff is in the @fontsource/baloo-2 npm package (files/baloo-2-latin-800-normal.woff).
"""
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
PNGS = [("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)]


def glyph_path(glyphs, cmap, upm, ch, cx, cy, size):
    """SVG path of `ch` at font size `size`, centred on (cx, cy)."""
    g = glyphs[cmap[ord(ch)]]
    bounds = BoundsPen(glyphs)
    g.draw(bounds)
    x0, y0, x1, y1 = bounds.bounds
    s = size / upm
    tx = cx - (x0 + x1) / 2 * s
    ty = cy + (y0 + y1) / 2 * s  # SVG y goes down, font y goes up
    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    g.draw(TransformPen(pen, (s, 0, 0, -s, tx, ty)))
    return pen.getCommands()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    font = TTFont(sys.argv[1])
    glyphs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm

    def cube(ch, x, y, w, rot, fill, shade, size, shadow):
        cx, cy = x + w / 2, y + w / 2
        r = round(w * .18)
        out = f'<g transform="rotate({rot} {cx} {cy})">'
        if shadow:
            out += f'<rect x="{x}" y="{y + shadow}" width="{w}" height="{w}" rx="{r}" fill="{shade}"/>'
        out += f'<rect x="{x}" y="{y}" width="{w}" height="{w}" rx="{r}" fill="{fill}"/>'
        out += f'<path d="{glyph_path(glyphs, cmap, upm, ch, cx, cy, size)}" fill="#fff"/></g>'
        return out

    # App icon: full-bleed light blue background, the cubes inside the maskable safe zone
    icon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="#E3F2FF"/>'
            '<g transform="translate(256 256) scale(.9) translate(-256 -256)">'
            + cube("A", 96, 134, 168, -8, "#12B5A5", "#0B8478", 160, 12)
            + cube("Z", 248, 216, 168, 7, "#8E5CF6", "#6A3FD0", 160, 12)
            + '</g></svg>\n')
    (ROOT / "icons/icon.svg").write_text(icon)

    # Favicon: transparent background, bigger cubes and no shadow, since it is tiny
    favicon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
               + cube("A", 20, 40, 250, -8, "#12B5A5", None, 230, 0)
               + cube("Z", 242, 222, 250, 7, "#8E5CF6", None, 230, 0)
               + '</svg>')
    uri = ("data:image/svg+xml," + urllib.parse.quote(favicon, safe=" =:/.,-'()")).replace('"', "'")
    page = ROOT / "index.html"
    html, n = re.subn(r'<link rel="icon" type="image/svg\+xml" href="[^"]*">',
                      lambda _: f'<link rel="icon" type="image/svg+xml" href="{uri}">', page.read_text())
    if n != 1:
        sys.exit("index.html: the favicon <link> was not found exactly once")
    page.write_text(html)

    if not shutil.which("rsvg-convert"):
        sys.exit("icons/icon.svg and the favicon are updated, but rsvg-convert is missing: render the PNGs from icons/icon.svg yourself")
    for name, size in PNGS:
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(ROOT / "icons" / name), str(ROOT / "icons/icon.svg")], check=True)
    print("Updated icons/icon.svg, the favicon in index.html and", ", ".join(n for n, _ in PNGS))


if __name__ == "__main__":
    main()
