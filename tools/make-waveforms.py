#!/usr/bin/env python3
"""Peak data for the demo waveforms, computed here rather than in the browser.

The players carry preload="none" on purpose - 2.3MB of audio fetched before
anyone presses anything would dwarf the page. Drawing a waveform client-side
means fetching and decoding the whole file, which throws that away. So the
peaks are computed once, here, and inlined into index.html as a few hundred
bytes per track: the waveform is on screen before a byte of audio is asked for.

Run against the NORMALIZED wavs, the same ones that get encoded to .m4a, so
the picture matches what plays.

    python3 make-waveforms.py "norm - Glitchy Texture.wav" ...
"""
import sys, wave, array, json, math

BARS = 96           # bars per track; sized for the two-column layout

def peaks(path, bars=BARS):
    w = wave.open(path, 'rb')
    ch, sw, n = w.getnchannels(), w.getsampwidth(), w.getnframes()
    assert sw == 2, "expected 16-bit"
    a = array.array('h'); a.frombytes(w.readframes(n)); w.close()

    frames = len(a) // ch
    out, step = [], frames / bars
    for b in range(bars):
        s = int(b * step); e = max(s + 1, int((b + 1) * step))
        hi = 0
        for i in range(s * ch, min(e * ch, len(a))):
            v = a[i]
            if v < 0: v = -v
            if v > hi: hi = v
        out.append(hi / 32768.0)

    # Scale so the loudest bar is 1.0. The files are already matched for
    # LOUDNESS; this is about the drawing filling its box, and a track whose
    # peak sits at 0.53 would otherwise render half-height and read as quiet
    # when it is not.
    top = max(out) or 1.0
    return [round(v / top, 3) for v in out]

if __name__ == "__main__":
    result = {}
    for i, p in enumerate(sys.argv[1:], start=1):
        result["demo-%d" % i] = peaks(p)
        print("  demo-%d  %s  %d bars" % (i, p, len(result["demo-%d" % i])), file=sys.stderr)
    print(json.dumps(result, separators=(',', ':')))
