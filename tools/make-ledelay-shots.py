#!/usr/bin/env python3
"""Stills of the real LeDELAY UI, for the product page and the menu tile.

The pictures on /ledelay/ are not mock-ups: they are the plugin's own
ui/index.html, loaded in an offscreen WKWebView (tools/uiprobe.swift), with a
factory preset injected and the court driven a few frames into a dribble, then
snapshotted at 2x. Nothing here is drawn by hand, so a change to the plugin's
art is a re-run away from the page.

    python3 tools/make-ledelay-shots.py [path/to/LeDELAY]

The LeDELAY repo defaults to ~/Developer/LeDELAY. Needs Xcode's swiftc (to
build the harness once, into a temp dir) and Pillow.

What it makes, under assets/ledelay/:
    hero.jpg         the whole screen, preset Alley-Oop, the 2020s jersey (1600 wide)
    tile.jpg         a 16:10 crop of the same, for the channel menu (1100 wide)
    og-card-v1.png   the 1200x630 share card, from tools/og-card-ledelay.html

HOW THE SNAPSHOT IS TAKEN
    rAF never fires in an offscreen view, so the court is painted by calling
    the page's own loop(now) with a hand-rolled clock: dribble() is the HIT,
    then 46 frames of 16ms put the ball in his hand. CSS animations do not
    advance either, which left the LeHANDLES bar off-screen (it slides in),
    so every animation is finish()ed before the shot.

    The TV bezel is found by scanning the middle row and column for the
    first near-black pixel; the crops are measured from that frame rather
    than from the window, so a change to the page's margins cannot move them.

JPEG, not PNG: the court carries a vignette and scanlines that a 256-colour
quantise bands on. q86 is 132KB for the hero; the PNG was 1.1MB.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "assets", "ledelay")
LEDELAY = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Developer/LeDELAY"))
UI = os.path.join(LEDELAY, "ui", "index.html")
PRESET = os.path.join(LEDELAY, "presets", "02-alley-oop.json")
W, H = 1072, 652                       # the plugin's base size (PluginEditor.cpp)

work = tempfile.mkdtemp(prefix="ledelay-shots.")
harness = os.path.join(work, "uiprobe")
subprocess.run(["xcrun", "swiftc", "-O", "-o", harness, os.path.join(HERE, "uiprobe.swift")], check=True)

def snap(html, js, out, w, h, wait=1.5):
    probe = os.path.join(work, "probe.js")
    open(probe, "w").write(js)
    subprocess.run([harness, html, probe, out, str(w), str(h), "1", str(wait)], check=True,
                   stdout=subprocess.DEVNULL)
    return Image.open(out).convert("RGB")

preset = json.load(open(PRESET))
def court_js(era, frames=46):
    return f"""
    const pj={json.dumps(preset)};
    Object.assign(P,pj.params); P.era="{era}"; Host.applyUiState(pj.ui); presetName=pj.name; updatePresetChip(); render();
    dribble(); let t=performance.now(); last=t; for(let i=0;i<{frames};i++){{ t+=16; loop(t); }}
    document.getAnimations().forEach(a=>{{ try{{a.finish()}}catch(e){{}} }});
    for(let i=0;i<2;i++){{ t+=16; loop(t); }}
    'ok';
    """

def frame(im):
    px = im.load(); w, h = im.size
    dark = lambda p: max(p) < 22
    y = h // 2; x0 = next(x for x in range(w) if dark(px[x, y])); x1 = next(x for x in range(w - 1, 0, -1) if dark(px[x, y]))
    x = w // 2; y0 = next(y for y in range(h) if dark(px[x, y])); y1 = next(y for y in range(h - 1, 0, -1) if dark(px[x, y]))
    return (x0, y0, x1 + 1, y1 + 1)

def fit(im, width):
    return im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)

os.makedirs(OUT, exist_ok=True)
# One era is enough for the page as it stands; court_js takes any of the
# three, which is how the era portraits were made when the page had them.
shot = snap(UI, court_js("2020s"), os.path.join(work, "2020s.png"), W, H)
hero = shot.crop(frame(shot))
fit(hero, 1600).save(os.path.join(OUT, "hero.jpg"), quality=86, optimize=True, progressive=True)
w, h = hero.size; th = round(w * 10 / 16); y0 = (h - th) // 2
fit(hero.crop((0, y0, w, y0 + th)), 1100).save(os.path.join(OUT, "tile.jpg"), quality=84, optimize=True)

# the share card, from the hero just written
card = snap(os.path.join(HERE, "og-card-ledelay.html"), "document.fonts.status", os.path.join(work, "og.png"), 1200, 630, wait=2)
card = card.resize((1200, 630), Image.LANCZOS).quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
card.save(os.path.join(OUT, "og-card-v1.png"), optimize=True)

for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if os.path.isfile(p): print(f"{f:18} {os.path.getsize(p) // 1024:5d} KB")
