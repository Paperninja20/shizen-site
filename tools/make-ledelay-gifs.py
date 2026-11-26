"""Make the two dribble loops on the LeDELAY page's BASIC / DEEP cards from the plugin's own UI.

    python3 tools/make-ledelay-gifs.py [path/to/LeDELAY]      (default ~/Developer/LeDELAY)

Writes assets/ledelay/basic-dribble.gif and deep-dribble.gif.

HOW
    tools/uigif.swift is uiprobe with a frame loop: load the plugin page offscreen, run a setup
    script, then n times run a step script and snapshot. rAF never fires offscreen, so the step
    is the page's own loop(now) with a clock stepped 40ms at a time; the GIFs keep every other
    frame (12.5 fps, 80ms), which is plenty for a bounce and halves the size.

    BASIC: Single, 1/4, feedback 100 (so the bounce never fades), one bar at 120 BPM = 4 bounces,
    and the ball's V alternates sides each bounce, so 2 seconds loops exactly.
    DEEP: Ping-Pong with the handles below dealt to the two balls by pan, LeLOOP at one bar,
    feedback 100. The left ball's V side takes two bars to come round, so that loop is 4 seconds.
    Flutter is 0: the spin isn't periodic with the bar and would show at the seam. Both loops
    are verified seamless (frame n == frame 0) when the pre-roll is long enough for the eased
    crouch / hold / glide to settle, which is what the pre-roll seconds below are for.

    The crop is the court around him in the 2x snapshot; the shared palette comes from a mosaic
    of ten frames so the colours don't jump between frames.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "ledelay")
LEDELAY = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Developer/LeDELAY"))
UI = os.path.join(LEDELAY, "ui", "index.html")
preset = json.load(open(os.path.join(LEDELAY, "presets", "02-alley-oop.json")))

FPS, KEEP, W = 25, 2, 420                    # captured fps, every KEEP-th frame kept, GIF width
BOX = (720, 215, 1570, 1070)                 # the court around him, in the 2x snapshot
DT = 1000 / FPS
work = tempfile.mkdtemp(prefix="ledelay-gifs.")
harness = os.path.join(work, "uigif")
subprocess.run(["xcrun", "swiftc", "-O", "-o", harness, os.path.join(HERE, "uigif.swift")], check=True)

def setup_js(params, ui, preroll_s):
    return f"""
    const pj={json.dumps(preset)};
    Object.assign(P,pj.params); Object.assign(P,{json.dumps(params)});
    Host.applyUiState(Object.assign({{}},pj.ui,{json.dumps(ui)})); presetName=pj.name; updatePresetChip(); render();
    document.getAnimations().forEach(a=>{{ try{{a.finish()}}catch(e){{}} }});
    window.__t=performance.now(); last=window.__t; dribble();
    for(let i=0;i<{int(preroll_s*FPS)};i++){{ window.__t+={DT}; loop(window.__t); }}
    'clock '+clock.toFixed(3);
    """
STEP = f"window.__t+={DT}; loop(window.__t); clock.toFixed(3);"

pp = lambda s, l, pan: {"s": s, "l": l, "pan": pan}
SCENES = {
    "basic": (setup_js({"bag": "BASIC", "mode": "Single", "sync": "1/4", "feedback": 100, "era": "2020s", "wow": 10, "flutter": 0}, {}, 4.0), 2.0),
    "deep":  (setup_js({"bag": "DEEP", "mode": "Ping-Pong", "feedback": 100, "era": "2020s", "wow": 10, "flutter": 0},
                       {"lanes": [[pp(0, .9, -60), pp(3, .7, 60), pp(4, .9, -60), pp(6, .8, 60), pp(8, .6, -60),
                                   pp(9, .9, 60), pp(10, .8, -60), pp(11, .5, -60), pp(12, .7, 60), pp(14, .9, -60)], []],
                        "loopOn": True, "loopAt": 16}, 8.28), 4.0),
}

for name, (js, seconds) in SCENES.items():
    d = os.path.join(work, name); os.makedirs(d)
    setup = os.path.join(work, name + ".setup.js"); open(setup, "w").write(js)
    step = os.path.join(work, "step.js"); open(step, "w").write(STEP)
    n = int(seconds * FPS)
    subprocess.run([harness, UI, setup, step, d, str(n + 1), "1072", "652", "1", "1.5"], check=True, stdout=subprocess.DEVNULL)
    H = round(W * (BOX[3] - BOX[1]) / (BOX[2] - BOX[0]))
    frames = [Image.open(os.path.join(d, f"f{i:03d}.png")).convert("RGB").crop(BOX).resize((W, H), Image.LANCZOS) for i in range(0, n + 1, KEEP)]
    seam = max(max(px) for px in ImageChops.difference(frames[0], frames[-1]).getdata())   # the eased states settle to sub-pixel, not to zero
    if seam > 24: print(f"warning: {name} does not loop cleanly (frame {n} vs frame 0: max channel diff {seam})")
    frames = frames[:-1]
    mosaic = Image.new("RGB", (W * 5, H * 2))
    for i, f in enumerate(frames[::max(1, len(frames) // 10)][:10]): mosaic.paste(f, ((i % 5) * W, (i // 5) * H))
    pal = mosaic.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out = os.path.join(OUT, f"{name}-dribble.gif")
    q[0].save(out, save_all=True, append_images=q[1:], duration=int(DT * KEEP), loop=0, optimize=True, disposal=1)
    print(f"{name}-dribble.gif  {len(q)} frames  {os.path.getsize(out) // 1024} KB  {W}x{H}")
