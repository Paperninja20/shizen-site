#!/usr/bin/env python3
"""Prove the OG card layout keeps its two rules, instead of eyeballing them.

Note this measures tools/og-card.html - the generated PLATE - not whatever is
currently installed as assets/img/og-card-vN.png, which may be hand-decorated.

    1. a 15px border with NO art in it
    2. nothing cropped - every sprite fully inside the frame

Both are the same measurement. The card is rendered twice, once normally and
once with `img.art` hidden, and the two are differenced: what changed IS the
art, wherever it actually landed. The text is present in both renders, so it
cancels out and never has to be reasoned about.

A single bounding box then answers both questions. Art intruding on the
margin starts inside the band; art running off the edge starts at 0. CSS
arithmetic cannot tell you either, because a sprite's visible ink is smaller
than its box by an amount that differs per file.

    python3 tools/check-og-card.py
"""
import os
import subprocess
import sys
import tempfile
from PIL import Image, ImageChops

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
W, H, MARGIN = 1200, 630, 15


def render(html_path, out_path):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=%d,%d" % (W, H), "--virtual-time-budget=6000",
                    "--screenshot=" + out_path, "file://" + html_path],
                   capture_output=True, timeout=90)


def main():
    work = tempfile.mkdtemp(prefix="ogcheck.")
    subprocess.run(["cp", "-r", os.path.join(SITE, "assets"), work], check=True)

    src = open(os.path.join(HERE, "og-card.html"), encoding="utf-8").read()
    a = os.path.join(work, "with.html")
    b = os.path.join(work, "without.html")
    open(a, "w", encoding="utf-8").write(src)
    # Hide EVERY foreground layer, not just art. The card is bare paper plus
    # text now, so a checker that only looked for `img.art` would find nothing
    # and report a pass over an empty measurement. This way the bounding box
    # covers whatever is on the paper - text today, decorated art later.
    open(b, "w", encoding="utf-8").write(
        src.replace("</style>",
                    ".plate, img.art { visibility: hidden; }</style>"))

    render(a, os.path.join(work, "with.png"))
    render(b, os.path.join(work, "without.png"))

    ia = Image.open(os.path.join(work, "with.png")).convert("RGB")
    ib = Image.open(os.path.join(work, "without.png")).convert("RGB")
    if ia.size != (W, H):
        print("FAIL  card is %dx%d, expected %dx%d" % (ia.size + (W, H)))
        return 1

    # >8 rather than >0: PNG quantisation and antialiasing leave a dusting of
    # 1-2 level differences that are not art.
    diff = ImageChops.difference(ia, ib).convert("L").point(
        lambda v: 255 if v > 8 else 0)
    box = diff.getbbox()

    if box is None:
        print("FAIL  nothing on the paper - the two renders are identical")
        return 1

    x0, y0, x1, y1 = box
    lo, hi_x, hi_y = MARGIN, W - MARGIN, H - MARGIN
    ok = x0 >= lo and y0 >= lo and x1 <= hi_x and y1 <= hi_y

    print("  card            %dx%d" % ia.size)
    print("  content extent  x %d..%d   y %d..%d" % (x0, x1, y0, y1))
    print("  safe area       x %d..%d   y %d..%d" % (lo, hi_x, lo, hi_y))
    print("  clearance       left %d  right %d  top %d  bottom %d"
          % (x0, W - x1, y0, H - y1))
    print()
    print("  %s" % ("PASS - everything inside the 15px margin, nothing cropped"
                    if ok else
                    "FAIL - content reaches outside the safe area"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
