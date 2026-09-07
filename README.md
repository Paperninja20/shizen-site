# Shizen — landing page

A single static page. No build step, no dependencies, no framework: open
`index.html` and what you see is what deploys.

```
site/
  index.html        the whole page, styles inline
  assets/img/       artwork, lifted from the plugin and quantised for the web
  README.md         this file
```

## Before it goes live

Everything below is marked `TODO` in `index.html`. Search for it.

1. ~~**Price.**~~ Set to `$49.99`, matching the variant. It appears in three
   places — the hero button, the buy card heading, and the buy-card button —
   and all three have to move together, or the overlay opens at a different
   number than the one that was clicked.
2. ~~**Lemon Squeezy store and variant.**~~ Done - both buttons point at
   `jayubeats.lemonsqueezy.com/checkout/buy/b5286d77-...?embed=1&media=0`.
   `?embed=1` plus `lemon.js` is what makes it an overlay rather than a
   navigation; if you ever swap the link, keep that parameter.
3. ~~**Support email**~~ Done - `prodjayu@gmail.com` in the footer.
4. **Demo video.** Replace the dashed `.demo-frame` placeholder with the
   iframe commented directly above it.
5. **The two mode recordings.** Each `.mode-media.is-empty` box in the Two
   modes section is a slot; the markup to drop in is commented above it.
   Prefer a muted, looping, inline `<video>` over a GIF - an equivalent MP4
   is roughly a tenth the size, and a GIF of a whole plugin window runs to
   tens of megabytes. Drop the `is-empty` class when you do. The boxes are
   sized `11 / 8` for the plugin window; change `aspect-ratio` on
   `.mode-media` if you record the pond alone.
6. **Open Graph image.** `assets/img/og-card.png`, 1200×630, is what appears
   when the link is pasted into Discord, X or iMessage. Not yet made. Also
   set `og:image` to an absolute URL once the domain exists — relative URLs
   do not resolve in most link unfurlers.
7. **A real screenshot.** The hero currently composes the plugin's own
   sprites into a pond, which looks right but is not the product. One honest
   screenshot of the actual window will sell it better than the composition.

## Checkout

Lemon Squeezy is the payment layer only; the page is entirely ours. The
integration is two things and nothing else:

- `lemon.js`, loaded once at the bottom of the page.
- Any `<a class="lemonsqueezy-button" href="...?embed=1">`.

That opens the checkout as an overlay on top of the page instead of
navigating away. Lemon Squeezy is a Merchant of Record, which is the reason
to use them: they take on the VAT and sales-tax liability, host the download
and issue licence keys. The trade is that the card form has to be theirs —
you cannot collect card details in your own markup.

Because the whole integration is one `<a>` tag, moving to Paddle (the
closest equivalent Merchant of Record) is a one-line change. Nothing about
the page's design depends on the processor.

## The typeface

The page is set in the plugin's own **omake** by rttiipp — but as **outlines**,
never as a webfont.

That licence grants commercial use freely, and *separately* forbids
`フォントデータの複製・改変・改造・二次配布・二次販売` — copying, modifying and
redistributing the font **data**. Those are two different permissions, and a
webfont runs into the second one: `@font-face` sends `omakebold.woff2` to
every visitor's browser regardless of how the page is monetised, so the
commercial grant is not the clause it answers to. A non-commercial blog would
hit exactly the same prohibition.

Text converted to paths is derived **artwork**, not font data — the same
footing any logo drawn in a licensed face stands on, and squarely the "use"
the licence does grant. So the wordmark and every `h1`/`h2` are genuine
omake, and no font file is served.

Three things fall out of it:

- **Cheaper than the font.** 16 files, ~185 KB total, against 379 KB for the
  unsubsetted woff2 — and only the headings actually on screen are fetched.
  (Unsubsetted, because the same licence forbids `改変` and a subset is a
  modified font. That reasoning is already in the plugin's own CSS.)
- **The cmap stops mattering.** omake is missing `—`, `·` and `©` of the
  characters this page uses. Outlines do not consult a cmap, and everything
  still set as live text is Zen Kurenaido, which has all three.
- **Two files per heading.** An SVG cannot re-wrap, so each is emitted `wide`
  and `narrow` with different line breaks and `<picture>` chooses between
  them at 700px. Without that, a long heading on a phone would scale down to
  nothing rather than take another line.

Everything still set as live text — body copy, `h3`, the price, the FAQ
summaries — is **Zen Kurenaido** (SIL OFL, Google Fonts), the one live face
on the page.

### Keeping the changelog current

The Updates list in `index.html` is written by hand, but every entry came out
of `git log` rather than memory - the version each commit actually SET, read
back with:

    for c in $(git log --format=%h -60 -- plugins/Nagare/CMakeLists.txt); do
      v=$(git show "$c:plugins/Nagare/CMakeLists.txt" | grep -m1 'VERSION "' \
            | sed -E 's/.*VERSION "([^"]+)".*/\1/')
      echo "$v  $(git log -1 --format=%s $c)"
    done | awk '!seen[$1]++'

Only user-visible releases are listed. Most version bumps are signing, CI or
build work that nobody buying this needs to read, and listing them would bury
the few entries that matter.

### Changing a heading

Headings are images, so editing the text means regenerating:

```sh
python3 site/tools/make-type.py
```

Edit the `PIECES` table at the top of that script — it holds the wide lines,
the narrow lines, and the target pixel size for each. Then update the `<img
alt>` in `index.html` to match, since the alt text is what search engines and
screen readers actually read.

### One clause worth remembering

The same licence forbids `商標登録` — trademark registration of works made
using the font. If the omake wordmark ever becomes the brand, it cannot be
registered. A wordmark drawn in something you own would avoid that, even with
the rest of the page staying omake.

## Deploying

Any static host will take this folder as-is.

- **Cloudflare Pages** — connect the repo, set the build output directory to
  `site`, leave the build command empty.
- **Netlify** — same, publish directory `site`.
- **GitHub Pages** — needs the folder at the repo root or in `docs/`, so
  point an action at `site` rather than moving it.

Local preview:

```sh
cd site && python3 -m http.server 8000    # then open http://localhost:8000
```

## Page weight

The artwork came out of the plugin at 570×354 and totalled 2.5 MB. It is
downscaled to 420px wide and quantised to a 256-colour alpha palette, which
watercolour takes without a visible difference: **2.5 MB → 491 KB**. Anything
added later should get the same treatment. Everything below the fold is
`loading="lazy"`.

## What writing the requirements section turned up

Stating the requirements out loud is the first thing that forced exact
answers, and it found three facts about the product.

### The macOS build was Apple Silicon only — fixed

Nothing set `CMAKE_OSX_ARCHITECTURES`, so CMake built for the host machine
and every artefact — including the notarised `.pkg` — was `arm64` only, while
`CMAKE_OSX_DEPLOYMENT_TARGET` advertised `10.13`. An Intel buyer would have
got a plugin their host refuses to load.

Fixed in the root `CMakeLists.txt` (before `project()`, where the toolchain is
probed). Both slices now build, and each carries the right floor — 10.13 on
Intel, 11.0 on Apple Silicon, which is the lowest Apple Silicon allows:

```
$ lipo -archs .../Shizen.vst3/Contents/MacOS/Shizen
x86_64 arm64
```

Verified by running it, not by trusting `lipo`: pluginval is itself universal,
so under Rosetta it loads the Intel slice for real.

```
x86_64  VST3  SUCCESS      arm64  VST3  SUCCESS
x86_64  AU    SUCCESS      arm64  AU    SUCCESS
```

### Nothing ships a standalone

`release-macos.sh` builds and packages `Nagare_VST3` and `Nagare_AU` only, and
the Windows workflow builds `Nagare_VST3` alone. The standalone target exists
in the build tree but reaches no installer, so the page does not claim one.

If it should ship, that is a change to the release script (build the target,
`ditto` it to `/Applications`, sign it like the others) and to the Inno
Setup script on Windows — not a change to this page.

### No MP3 on Windows

`registerBasicFormats()` gives WAV, AIFF, FLAC and Ogg on both platforms.
`CoreAudioFormat` is registered on macOS only, which is where MP3, M4A and
CAF come from; `JUCE_USE_MP3AUDIOFORMAT` defaults to `0` and nothing turns it
on, and `JUCE_USE_WINDOWS_MEDIA_FORMAT` is not set either.

So a Windows buyer cannot drag an MP3 onto a fish, and the requirements
section says so. If that is not the intent, enabling one of those two flags
is the change — mind the licensing disclaimer JUCE attaches to the MP3
decoder.
