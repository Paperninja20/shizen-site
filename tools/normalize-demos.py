import sys, wave, array, math
sys.path.insert(0,'/tmp/claude-501')
from lufs import integrated_lufs

TARGET = -18.0
KNEE, CEIL = 0.85, 0.97          # soft knee, and the ceiling it asymptotes to

def process(path, out):
    lufs, _ = integrated_lufs(path)
    gain = 10 ** ((TARGET - lufs) / 20.0)

    w = wave.open(path,'rb'); ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
    a = array.array('h'); a.frombytes(w.readframes(n)); w.close()

    rng = CEIL - KNEE
    clipped = 0
    out_a = array.array('h', bytes(len(a)*2))
    for i, s in enumerate(a):
        v = (s/32768.0) * gain
        m = abs(v)
        if m > KNEE:
            m = KNEE + rng*math.tanh((m - KNEE)/rng)
            clipped += 1
            v = m if v >= 0 else -m
        q = int(round(v*32767))
        out_a[i] = 32767 if q > 32767 else (-32768 if q < -32768 else q)

    ow = wave.open(out,'wb'); ow.setnchannels(ch); ow.setsampwidth(2); ow.setframerate(sr)
    ow.writeframes(out_a.tobytes()); ow.close()
    return lufs, 20*math.log10(gain), clipped, len(a)

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    l, g, c, total = process(src, dst)
    print("  %-22s %6.2f LUFS  gain %+5.2f dB  softened %d/%d samples (%.3f%%)"
          % (src[:-4], l, g, c, total, 100.0*c/total))
