#!/usr/bin/env python3
"""Do the mode clips show the plugin window's own edge?

Both recordings carry a dark column at x=0 and x=1279 - about (104,103,98)
against washi at (228,221,211) - which is the plugin window's vertical border
caught in the capture. Top and bottom are clean; it is only the sides.

There is no ffmpeg or PyObjC here to re-crop the files, so .mode-media's
aspect-ratio is set a shade narrower than the clips and object-fit: cover
trims the excess evenly off both sides. 1264/652 against the clips' 1280/652
takes 8 native px a side, six times the 1.33px line.

This renders the poster under the REAL stylesheet and samples the painted
edge, because "the arithmetic says the crop is enough" and "the browser
paints no dark pixel" are different claims and only the second one matters.

    python3 check-mode-clip-edges.py shizen
    python3 check-mode-clip-edges.py nagare

At 1264/652 it reports none; put the box back to the clips' own 1280/652 and
it reports 2 a side, which is how it was checked.
"""
import os, re, subprocess, tempfile, sys
from PIL import Image
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = open('shizen/index.html', encoding='utf-8').read()
css = "\n".join(re.findall(r"<style>(.*?)</style>", src, re.S))
page = """<style>%s
 html,body{margin:0;background:#FF00FF} .wrap{width:520px;padding:20px}
</style><body><div class="wrap">
<video class="mode-media" poster="assets/video/%s-mode-poster.jpg"></video>
</div></body>""" % (css, sys.argv[1])
fd, path = tempfile.mkstemp(suffix=".html", dir="."); os.write(fd, page.encode()); os.close(fd)
shot = "/tmp/claude-501/e.png"
try:
    subprocess.run([CHROME,"--headless","--disable-gpu","--screenshot="+shot,
                    "--window-size=600,360","file://"+os.path.abspath(path)],
                   capture_output=True, timeout=90)
finally: os.unlink(path)
im = Image.open(shot).convert("RGB"); w,h = im.size
mg = lambda p: p[0]>200 and p[1]<80 and p[2]>200
ys=[y for y in range(h) if any(not mg(im.getpixel((x,y))) for x in range(w))]
y=(min(ys)+max(ys))//2
xs=[x for x in range(w) if not mg(im.getpixel((x,y)))]
l,r=min(xs),max(xs)
edge=[im.getpixel((l+i,y)) for i in range(3)]+[im.getpixel((r-i,y)) for i in range(3)]
dark=[p for p in edge if sum(p)/3<170]
print("    %-8s dark edge pixels: %d  %s" % (sys.argv[1], len(dark), dark[:2]))
