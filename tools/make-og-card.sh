#!/usr/bin/env bash
# Render the Open Graph card from tools/og-card.html and install it.
#
# Kept as a script because the card is generated, not drawn: the wordmark and
# tagline are the same omake outlines the page uses, so a change to either has
# to flow through here rather than being re-drawn by hand.
#
#   tools/make-og-card.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE="$(dirname "$HERE")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

WORK="$(mktemp -d /tmp/ogcard.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

cp -r "$SITE/assets" "$WORK/"
cp "$HERE/og-card.html" "$WORK/card.html"

"$CHROME" --headless --disable-gpu --hide-scrollbars \
          --window-size=1200,630 --virtual-time-budget=6000 \
          --screenshot="$WORK/og-card.png" "file://$WORK/card.html" 2>/dev/null

# Must match the versioned filename in index.html's og:image.
DEST="$SITE/assets/img/og-card-v3.png"

# REFUSE to clobber a card this script did not make.
#
# The live card is decorated by hand from the bare plate this generates.
# Running this without thinking would replace that artwork with the plate,
# and the only copy might be the one it just destroyed. So: generate,
# compare, and stop unless --force says otherwise.
if [ -f "$DEST" ] && ! cmp -s "$WORK/og-card.png" "$DEST"; then
    if [ "${1:-}" != "--force" ]; then
        echo "  REFUSING: $DEST differs from the generated plate."
        echo "  It is almost certainly the hand-decorated card, and"
        echo "  regenerating would throw that away."
        echo
        echo "  If you really mean to replace the artwork:"
        echo "      tools/make-og-card.sh --force"
        exit 1
    fi
    echo "  --force given: replacing the existing card"
fi

# Quantised like the rest of the artwork - watercolour takes a 256-colour
# palette without a visible difference, and this is ~4x smaller for it.
python3 - "$WORK/og-card.png" "$DEST" <<'PY'
import sys, os
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
before = os.path.getsize(src)
# Quantise only when it costs nothing. Flat paper and type take a
# 256-colour palette invisibly; hand-painted watercolour does not - measured
# at 48KB saved against a worst-case 51-level shift, which is banding.
from PIL import ImageChops, ImageStat
im = Image.open(src).convert("RGB")
q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE).convert("RGB")
worst = ImageStat.Stat(ImageChops.difference(im, q).convert("L")).extrema[0][1]
if worst <= 12:
    q.save(dst, optimize=True)
    print("  og-card.png  %dKB -> %dKB (quantised, worst %d levels)"
          % (before // 1024, os.path.getsize(dst) // 1024, worst))
else:
    im.save(dst, optimize=True)
    print("  og-card.png  %dKB (left as-is, quantising would shift %d levels)"
          % (os.path.getsize(dst) // 1024, worst))
PY

echo "  written: $DEST"
echo "  now run: python3 tools/check-og-card.py"
