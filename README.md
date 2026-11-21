# jayusounds.com

The whole site, served by GitHub Pages from this repo's `main` at the custom
domain in `CNAME`. Static pages: no build step, no dependencies, no framework.
Open the HTML and what you see is what deploys, a minute or so after a push.

**Two branches.** `main` is what is live. `dev` is the site as it is becoming:
the channel menu at the root, Shizen under `/shizen/`, LeDELAY under
`/ledelay/`. Until the day it goes live, `main` holds the Shizen-only page it
has shown since launch, so nothing below describes what jayusounds.com shows
today; it describes `dev`. `main` was put back to that page with a plain
commit rather than rewound, so going live is a tree copy, not a merge:

```sh
git checkout main
git read-tree -m -u dev        # main's files become dev's, deletions included
git commit -m "The new site goes live"
git push
```

To preview `dev`, serve the checkout from its root (`python3 -m http.server`
in it): the menu's `/shizen/` and `/ledelay/` links are root-relative and do
not resolve from a file:// open.

```
index.html            the channel menu - the homepage: one tile per product
shizen/index.html     Shizen, a generative sampler
ledelay/index.html    LeDELAY, a multi-tap delay
assets/img, audio, video, type     Shizen's artwork, demos, clips and headings
assets/ledelay/       LeDELAY's stills, share card and fonts
tools/                generators and checkers. Published too, but harmless
CNAME                 jayusounds.com - keep it; Pages reads the domain from here
```

**This repo IS the source now.** It began as a publish-only mirror of a
`site/` folder in the private Shizen plugin repo, pushed by a `publish.sh`
that rsync'd with `--delete`. That stopped on 20 Nov 2026 when LeDELAY, a
plugin from a different repo, needed a page here too: one site, one repo,
edited in place. The private repo keeps only `tools/make-type.py`, because it
reads the licensed omake font out of the plugin tree (see *The typeface*
under Shizen below); it writes into `assets/type/` here.

## The channel menu (`index.html`)

The homepage is a console-style menu: a neutral shell, and inside it a grid
of tiles where each product brings its own world. Two products take a 2x2
block each; the four small slots under them are empty on purpose and say so
once.

- The Shizen tile crossfades its share card with a clip of the plugin running
  and holds on the clip on hover.
- The LeDELAY tile is a still of the real plugin, `assets/ledelay/tile.jpg`.
  The hover script only animates a tile that carries a `.ch-clip`, so a still
  tile needs nothing from it.
- Links to the products are root-relative (`/shizen/`), which is right
  because the site is served from a custom-domain apex, not a Pages project
  path.
- The dock holds the Beats sheet (a BeatStars store in an iframe) and an
  About letter. **The About text is still the placeholder.**

## LeDELAY (`ledelay/index.html`)

Its own world: the plugin's arena palette, hardwood for one band, and the
plugin's own two faces.

**The pictures are the plugin.** `tools/make-ledelay-shots.py` loads the
plugin's `ui/index.html` (from `~/Developer/LeDELAY`, or the path you pass)
in an offscreen WebKit view, injects the Alley-Oop preset, drives the court
a few frames into a dribble, and snapshots it at 2x. It writes the hero, the
menu tile and the share card. Re-run it after any change to the plugin's
art; nothing is drawn by hand. (The page is deliberately short: hero, the
two bags, how the handles play, requirements, contact. The effects, era,
build-him and preset bands were written and cut on 20 Nov 2026; the era
portraits came out of the same script and can come back.) The harness is
`tools/uiprobe.swift`; the script builds it into a temp dir.

**Beaver Punch is served as a webfont.** Its author's terms: "100% free ...
for any personal or commercial purposes", forbidding only selling it,
modifying it or deriving a font from it. Serving the unmodified file does
none of those, so unlike the Shizen page the headings are live text. Saira
is SIL OFL; its licence ships beside it in `assets/ledelay/fonts/`.

**Before it goes on sale**, search the page for `TODO`:

1. The buy button. Both CTAs are a "Coming soon" placeholder. Swap in the
   Lemon Squeezy `<a class="btn btn-buy lemonsqueezy-button" href="...?embed=1&media=0">`
   the Shizen page uses, and put `lemon.js` back at the bottom. The price
   appears in the hero and in the Get it band - move both together.
2. The mailing-list endpoint, in `newsletter()` at the bottom. The form is
   hidden until one is pasted in.
3. The changelog, once there is a release. The requirements say Windows is
   "on the way": the Windows build is scripted but has not been run end to
   end yet.
4. Audio demos. There are none yet, so there is no "Hear it" band. The Shizen
   page's drawn-waveform players and `tools/make-waveforms.py` are ready for
   when there are.

The share card is `assets/ledelay/og-card-v1.png`, from
`tools/og-card-ledelay.html`. Versioned filename, same reason as Shizen's:
link unfurlers cache by URL. Bump the N in the filename, the page's
`og:image` and the script when the art changes.

The Echo King is a parody mascot. No real player's name, no team names or
logos, anywhere - team colours only. That rule is the plugin's and the page
keeps it.

## Shizen (`shizen/index.html`)

Shizen used to BE the site, at the root. `shizen/index.html` was a redirect
stub, put there so marketing could point at a stable address before a second
product existed - and its comment said exactly what would happen when one
did: the root becomes a menu, and every link that said "the root" and meant
"Shizen" quietly becomes a link to a product grid.

That moment arrived. The stub is gone and the real page lives there now.

**Anything already published that points at the bare domain now lands on the
menu, not on Shizen.** The trailer description, an Instagram bio and any
posted link are all in that category. They still work, they just cost a
click. Editable ones should be repointed at `/shizen/`; the rest resolve fine.
Ad links already carry `/shizen/?src=ig`, and the page itself turns that into
the discount code, so attribution is unaffected by the move.

Every asset reference inside `shizen/index.html` is `../assets/...`,
relative rather than absolute: on a custom domain the site root is `/`, but
served from a GitHub Pages project path it would be `/shizen-site/`, and an
absolute `/assets/` is right in only one of those.

### Checkout

Lemon Squeezy is the payment layer only; the page is entirely ours. The
integration is two things and nothing else:

- `lemon.js`, loaded once at the bottom of the page.
- Any `<a class="lemonsqueezy-button" href="...?embed=1">`.

That opens the checkout as an overlay instead of navigating away. Lemon
Squeezy is a Merchant of Record: they take on VAT and sales-tax liability,
host the download and issue licence keys. The trade is that the card form has
to be theirs. Moving to Paddle is a one-line change.

The price appears in three places - the hero button, the buy card heading and
the buy-card button - and all three have to move together.

### The typeface

The page is set in the plugin's own **omake** by rttiipp, but as **outlines**,
never as a webfont. That licence grants commercial use freely and separately
forbids `フォントデータの複製・改変・改造・二次配布・二次販売`: copying, modifying and
redistributing the font **data**. `@font-face` sends the font to every
visitor regardless of how the page is monetised, so the commercial grant is
not the clause it answers to. Text converted to paths is derived artwork, the
footing any logo drawn in a licensed face stands on. So the wordmark and every
`h1`/`h2` are genuine omake and no font file is served.

- 16 files, ~185 KB, against 379 KB for the unsubsetted woff2 (unsubsetted
  because a subset is a modified font).
- Each heading is emitted `wide` and `narrow` with different line breaks and
  `<picture>` chooses between them at 700px, because an SVG cannot re-wrap.
- Everything still set as live text is **Zen Kurenaido** (SIL OFL).

To change a heading, edit the `PIECES` table in `make-type.py` **in the
private plugin repo** (`site/tools/make-type.py`, the one file that stayed
there), run it, and it writes the SVGs into this repo's `assets/type/`. Then
update the `<img alt>` to match.

The same licence forbids `商標登録`, trademark registration of works made
using the font. If the omake wordmark ever becomes the brand, it cannot be
registered.

### The demos

Five `.m4a` files, 2.3MB in total, every one `preload="none"`. Drawn
waveforms rather than the native control: the peaks are computed offline by
`tools/make-waveforms.py` and inlined into the page, 96 bars a track. Re-run
it if the audio changes, against the NORMALIZED wavs.

They are matched to -18 LUFS, not to peak (`tools/normalize-demos.py`,
`tools/lufs.py`): as supplied the five spanned 7.84 LU, which is plainly
audible when stepping between players.

AAC in `.m4a`, not mp3: macOS decodes mp3 but cannot encode it, and there is
no ffmpeg here.

```sh
afconvert -f WAVE -d LEI16 IN.mp3 IN.wav      # only if the source is mp3
python3 tools/normalize-demos.py
afconvert -f m4af -d aac -b 192000 norm.wav demo-N.m4a
```

### The clips

`assets/video/shizen-mode.mp4` and `nagare-mode.mp4`, 1280x652, 8s each,
with a JPEG still as the poster. Converted from `.mov` screen captures with
the macOS built-in:

```sh
avconvert --source IN.mov --output out.mp4 --preset Preset1280x720 --duration 8 --replace
qlmanage -t -s 1280 -o /tmp out.mp4
sips -Z 960 /tmp/out.mp4.png --out p.png
sips -s format jpeg -s formatOptions 80 p.png --out poster.jpg
```

`.mode-media` is deliberately narrower than the clips so `object-fit: cover`
trims the plugin window's own dark edge. If you re-record, run
`python3 tools/check-mode-clip-edges.py shizen` (and `nagare`) from the repo
root: it renders the poster under the real stylesheet and samples the painted
edge.

The hero is `assets/video/hero-clip.mp4`, the actual plugin running, cropped
by a `transform: scale(1.012)` rather than by its box.

### The share card

`assets/img/og-card-v5.png`, 1200x630, composed from the site's own artwork
and the omake outlines. To change it: edit `tools/og-card.html`, then
`tools/make-og-card.sh` and `python3 tools/check-og-card.py`, which enforces
a 15px clear border by measuring rather than trusting the CSS. Bump the `-vN`
in the filename, in `og:image` and in the script.

### Keeping the changelog current

The Updates list is written by hand, but every entry came out of the plugin
repo's `git log` rather than memory. Only user-visible releases are listed.

## Deploying

Push to `main`. GitHub Pages builds it (the "legacy" Jekyll builder, so a
file or folder whose name starts with `_` is NOT served - handy for a local
probe, fatal for an asset). Check a build with:

```sh
gh api repos/Paperninja20/shizen-site/pages/builds/latest --jq '.status'
```

`CNAME` has to stay in the repo: it is what sets the custom domain, and
without it the site silently reverts to the github.io address.

## Page weight

Shizen's artwork came out of the plugin at 2.5MB and is quantised to a
256-colour palette: 491KB. LeDELAY's stills are JPEG, because the court's
vignette and scanlines band under a 256-colour quantise. Anything added
later should get the same care, and everything below the fold is
`loading="lazy"`.
