# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py"]
# ///
"""Draw the optional_dependencies logo: a package, asking if it is installed.

A package as a blue isometric cube, with a yellow badge carrying a question
mark: the check this library constructs. The shapes are vector, so the logo is
written as an SVG, sharp at any size; for a bitmap, name a .png and give its
size::

    uv run docs/_static/make_logo.py                     # favicon.svg
    uv run docs/_static/make_logo.py --size 2048 big.png
"""

import argparse
import math
from pathlib import Path

INK = "#1f2328"  # outlines and the question mark
# Python's blue and yellow, with a lighter and a darker blue for the cube's faces.
BLUE, BLUE_TOP, BLUE_SIDE = "#3776ab", "#5a93c8", "#2b5f8c"
YELLOW = "#ffd43b"

# In a 64-unit square. The cube: x and y of its top face's near corner, and its
# edge. The badge: its centre's x and y, and its radius.
CUBE = (32, 30, 18)
BADGE = (46, 44, 10)

SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="512" height="512">
  <g stroke="{ink}" stroke-width="2.4" stroke-linejoin="round">
    <polygon points="{top}" fill="{blue_top}"/>
    <polygon points="{left}" fill="{blue}"/>
    <polygon points="{right}" fill="{blue_side}"/>
  </g>
  <g transform="translate({bx:g} {by:g})">
    <circle r="{br:g}" fill="{yellow}" stroke="{ink}" stroke-width="2.2"/>
    <path d="M-3.6 -2.8C-3.6 -6.8 3.6 -6.8 3.6 -2.6C3.6 0.6 0 0.8 0 3.6" fill="none"
      stroke="{ink}" stroke-width="2.6" stroke-linecap="round"/>
    <circle cy="7.4" r="1.6" fill="{ink}"/>
  </g>
</svg>
"""


def faces() -> dict[str, str]:
    """Return the cube's three visible faces as SVG points."""
    x, y, s = CUBE
    h = s * math.sqrt(3) / 2  # half the cube's width
    corners = {
        "top": [(x, y - s), (x + h, y - s / 2), (x, y), (x - h, y - s / 2)],
        "left": [(x - h, y - s / 2), (x, y), (x, y + s), (x - h, y + s / 2)],
        "right": [(x, y), (x + h, y - s / 2), (x + h, y + s / 2), (x, y + s)],
    }
    return {
        face: " ".join(f"{px:.2f},{py:.2f}" for px, py in points)
        for face, points in corners.items()
    }


def svg() -> str:
    """Return the logo as SVG text."""
    bx, by, br = BADGE
    return SVG.format(
        ink=INK,
        blue=BLUE,
        blue_top=BLUE_TOP,
        blue_side=BLUE_SIDE,
        yellow=YELLOW,
        bx=bx,
        by=by,
        br=br,
        **faces(),
    )


def main() -> None:
    """Parse the command line and save the logo."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "out",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("favicon.svg"),
        help="output file, SVG or PNG by its extension (default: favicon.svg)",
    )
    parser.add_argument(
        "--size", type=int, default=512, help="pixels per side, for a PNG"
    )
    args = parser.parse_args()

    if args.out.suffix == ".svg":
        args.out.write_text(svg())
    else:
        import resvg_py  # noqa: PLC0415  # only a PNG needs a renderer

        png = resvg_py.svg_to_bytes(svg_string=svg(), width=args.size)
        args.out.write_bytes(bytes(png))


if __name__ == "__main__":
    main()
