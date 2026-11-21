"""Integrated loudness, ITU-R BS.1770-4, in pure Python."""
import wave, struct, math, array

def read_wav(path):
    w = wave.open(path, 'rb')
    ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    raw = w.readframes(n); w.close()
    assert sw == 2, "expected 16-bit"
    a = array.array('h'); a.frombytes(raw)
    return ch, sr, a

def biquad(x, b0, b1, b2, a1, a2):
    """In-place-ish direct form I over a list of floats."""
    y = [0.0]*len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, xv in enumerate(x):
        yv = b0*xv + b1*x1 + b2*x2 - a1*y1 - a2*y2
        y[i] = yv
        x2, x1 = x1, xv
        y2, y1 = y1, yv
    return y

def k_weight(x, sr):
    # BS.1770 stage 1: high shelf (+4 dB above ~1.5 kHz), coefficients for 48k
    # rescaled to sr by matching the pole/zero frequencies.
    # Shelf
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi*f0/sr); Vh = 10**(G/20); Vb = Vh**0.4996667741545416
    a0 = 1 + K/Q + K*K
    b = [(Vh + Vb*K/Q + K*K)/a0, 2*(K*K - Vh)/a0, (Vh - Vb*K/Q + K*K)/a0]
    a = [1.0, 2*(K*K - 1)/a0, (1 - K/Q + K*K)/a0]
    x = biquad(x, b[0], b[1], b[2], a[1], a[2])
    # Stage 2: high pass at ~38 Hz
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = math.tan(math.pi*f0/sr)
    a0 = 1 + K/Q + K*K
    b = [1/a0, -2/a0, 1/a0]
    a = [1.0, 2*(K*K - 1)/a0, (1 - K/Q + K*K)/a0]
    return biquad(x, b[0], b[1], b[2], a[1], a[2])

def integrated_lufs(path):
    ch, sr, a = read_wav(path)
    chans = []
    for c in range(ch):
        chans.append([a[i]/32768.0 for i in range(c, len(a), ch)])
    peak = max(max(abs(v) for v in c) for c in chans)
    weighted = [k_weight(c, sr) for c in chans]

    blk = int(0.400*sr); hop = int(0.100*sr)
    powers = []
    n = len(weighted[0])
    for s in range(0, max(0, n - blk + 1), hop):
        z = 0.0
        for c in weighted:
            acc = 0.0
            for i in range(s, s+blk): acc += c[i]*c[i]
            z += acc/blk
        powers.append(z)
    if not powers: return None, peak

    def L(z): return -0.691 + 10*math.log10(z) if z > 0 else -999.0
    # absolute gate
    kept = [z for z in powers if L(z) > -70.0]
    if not kept: return None, peak
    # relative gate
    thr = L(sum(kept)/len(kept)) - 10.0
    kept2 = [z for z in kept if L(z) > thr]
    if not kept2: kept2 = kept
    return L(sum(kept2)/len(kept2)), peak
