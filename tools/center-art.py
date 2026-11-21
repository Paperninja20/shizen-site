#!/usr/bin/env python3
"""Re-centre each sprite's ink inside its own PNG, on both axes.

The art is cropped from a larger painting, so the visible ink does not sit at
the centre of the file - coral-1 is 3.7% right of it, the koi 4.9%. Layout
centres the <img> BOX, which is exact (measured: artC == imgC for every item),
so an off-centre ink pulls the picture away from anything positioned on the
box. The ground shadow under each sprite is centred on the box, so the art
appeared to sit right of its own shadow - reported as the shadow being left
aligned.

Fixing it here rather than in CSS: a per-sprite nudge in the stylesheet would
have to be maintained for every new piece of art and re-derived whenever a
file is re-exported. Centring the source means everything downstream - the
shadow, the growth on hover, any future alignment - is simply correct.

The whole raster is shifted horizontally and the ink is re-measured after, so
a shift that would clip is caught rather than assumed. Dimensions do not
change; the vacated edge is transparent.

    python3 tools/center-art.py [--check]
"""
import os
import sys
import glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "assets", "img")
SKIP = {"washi-tile", "washi-overlay", "ripple-1"}   # textures, not sprites


def ink_bbox(im):
    return im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()


def offset_of(im):
    """How far the ink's centre sits from the file's centre, x and y."""
    b = ink_bbox(im)
    if b is None:
        return None, None, None
    w, h = im.size
    return ((b[0] + b[2]) / 2.0 - w / 2.0,
            (b[1] + b[3]) / 2.0 - h / 2.0, b)


def main():
    check = "--check" in sys.argv
    moved = 0
    print("%-26s %-10s %s" % ("file", "offset", "result"))

    for path in sorted(glob.glob(os.path.join(IMG, "*.png"))):
        name = os.path.basename(path)[:-4]
        if name in SKIP:
            continue

        im = Image.open(path).convert("RGBA")
        ox, oy, _ = offset_of(im)
        if ox is None:
            print("%-26s %-10s no ink" % (name, "-"))
            continue

        # BOTH axes. x alone was enough while the shadow only had to sit
        # under the art; growth on hover scales about the box centre, so an
        # ink that is low in its file - the betta is 20px low, the koi 16px -
        # walks downward as it enlarges instead of growing in place.
        sx, sy = -int(round(ox)), -int(round(oy))
        if sx == 0 and sy == 0:
            print("%-26s %-10s already centred" % (name, "0,0"))
            continue

        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.paste(im, (sx, sy))

        ax, ay, b2 = offset_of(out)
        w, h = im.size
        if b2 is None or b2[0] < 0 or b2[1] < 0 or b2[2] > w or b2[3] > h:
            print("%-26s %-10s SKIPPED - shifting would clip the ink"
                  % (name, "%+.0f,%+.0f" % (ox, oy)))
            continue

        after = "%+.1f,%+.1f" % (ax, ay)
        off = "%+.0f,%+.0f" % (ox, oy)

        if check:
            print("%-26s %-10s would move (then %s)" % (name, off, after))
            continue

        out.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(path, optimize=True)
        moved += 1
        print("%-26s %-10s centred (now %s)" % (name, off, after))

    if not check:
        print("\n%d sprite(s) re-centred" % moved)


if __name__ == "__main__":
    main()
