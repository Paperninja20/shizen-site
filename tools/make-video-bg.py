#!/usr/bin/env python3
"""Render the site's own washi sheet as a flat image, for use as a video bed.

The page builds it from three things: --paper-page, four percentage-placed
watercolour blooms, and washi-tile.png multiplied on top at HALF strength.
All four are read out of index.html here rather than retyped, so this cannot
drift from the site - and it has drifted twice already, once when the page
got its own lighter token and once when the grain was halved.

Two variants, because "the washi background" can mean either:
  <name>.png        the sheet as the page shows it, blooms included
  <name>-flat.png   paper and grain only, for busier footage

Usage: make-video-bg.py [WIDTH HEIGHT] [--out DIR]
"""
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('-')]
    W, H = (int(a[0]), int(a[1])) if len(a) >= 2 else (1920, 1080)
    out = os.path.expanduser(sys.argv[sys.argv.index('--out')+1]) if '--out' in sys.argv \
          else os.path.expanduser('~/Desktop')

    src = open(os.path.join(SITE, 'shizen', 'index.html'), encoding='utf-8').read()

    scene = re.search(r'--paper-page:\s*(#[0-9a-fA-F]+);', src).group(1)
    body = re.search(r'\n  background-color: var\(--paper-page\);\n'
                     r'  background-image:\n(.*?);\n', src, re.S).group(1)
    blooms = body.strip().rstrip(',')
    tile = re.search(r'background-image: url\("([^"]+)"\);\s*\n\s*background-size: (\d+)px',
                     src)
    tile_url, tile_px = tile.group(1), tile.group(2)
    grain = re.search(r'body::before \{.*?opacity:\s*([0-9.]+);', src, re.S)
    grain_op = grain.group(1) if grain else "1"
    print("page %s / %d blooms / tile %s @%spx / grain opacity %s"
          % (scene, blooms.count('radial-gradient'), tile_url, tile_px, grain_op))

    page = """<style>
html,body{margin:0;padding:0;width:%dpx;height:%dpx;overflow:hidden}
body{background-color:%s;%s}
body::before{content:"";position:absolute;inset:0;
  background-image:url("%s");background-size:%spx %spx;
  opacity:%s;mix-blend-mode:multiply;pointer-events:none}
</style>""" % (W, H, scene,
               ("background-image:\n" + blooms + ";") if not FLAT else "",
               tile_url, tile_px, tile_px, grain_op)
    return page, W, H, out, scene

FLAT = False
for variant, flat in (("", False), ("-flat", True)):
    globals()['FLAT'] = flat
    page, W, H, out, scene = main()
    # the probe has to live in the site dir so assets/ resolves
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=SITE); os.write(fd, page.encode()); os.close(fd)
    png = os.path.join(out, "shizen-bg-%dx%d%s.png" % (W, H, variant))
    try:
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1",
                        "--window-size=%d,%d" % (W, H), "--virtual-time-budget=6000",
                        "--screenshot=" + png, "file://" + tmp],
                       capture_output=True, timeout=120)
    finally:
        os.unlink(tmp)
    print("  ->", png)
