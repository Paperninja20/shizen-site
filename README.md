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
5. **The five demo tracks.** The "Hear the pond" section expects
   `assets/audio/demo-1.mp3` through `demo-5.mp3`. Until they exist the
   players render but will not play. Every one carries `preload="none"` on
   purpose - five audio files fetched before anyone presses anything would
   dwarf the rest of the page, which is under a megabyte in total. The track
   names and one-line notes are in `index.html`; change them to match
   whatever you actually record.
6. ~~**The two mode recordings.**~~ Done - `assets/video/shizen-mode.mp4`
   and `nagare-mode.mp4`, 960x696, with a still from each as the poster so
   the cards are not black rectangles before play.

   Both carry `preload="none"`: 18MB of video fetched before anyone pressed
   play would be eighteen times the rest of the page.

   To replace one: the sources are H.264 `.mov` screen captures, converted
   with the macOS built-in (no ffmpeg needed) -

   ```sh
   avconvert --source IN.mov --output out.mp4 --preset Preset640x480 --replace
   qlmanage -t -s 960 -o /tmp out.mp4     # a still, for the poster
   ```

   The presets fit WITHIN their box preserving aspect, so a near-16:9 source
   lands at 640x360-ish. `Preset960x540` was tried and is twice the size for
   a difference nothing can see on a card that renders 440px wide.

   `.mode-media` is `aspect-ratio: 16 / 9` with `object-fit: cover`, NOT an
   exact per-clip ratio: the two clips were cropped separately and differ by
   1.1% (640x360 against 640x364). `cover` takes that one percent off the
   taller one invisibly; `contain` would show it as thin bars on one card and
   not the other.
7. ~~**Open Graph image.**~~ Done - `assets/img/og-card.png`, 1200×630, is
   what a pasted link renders as in Discord, X or iMessage. Composed from the
   site's own artwork and the omake wordmark outlines, so it needs no font and
   stays licence-clean.

   To change it: edit `tools/og-card.html`, then

   ```sh
   site/tools/make-og-card.sh        # render + quantise + install
   python3 site/tools/check-og-card.py   # prove the margin still holds
   ```

   **The filename is versioned (`og-card-v3.png`) on purpose.** Discord, X and
   iMessage cache the card on their own proxies keyed by that URL, for days -
   replacing the bytes at a fixed name leaves everyone looking at the old
   picture with no way to tell it is stale. When the artwork changes, bump the
   `-vN` in both the filename and `og:image`, and in `tools/make-og-card.sh`.

   The checker enforces a 15px border with no art in it, and that nothing is
   cropped. It measures rather than trusts the CSS: the card is rendered twice,
   once with `img.art` hidden, and the difference IS the art wherever it
   actually landed - a sprite's visible ink is smaller than its box by an
   amount that differs per file, so the arithmetic cannot tell you.
   `og:image` and `og:url` are absolute and name the live host - update both
   when a real domain is pointed at the page.
8. **A real screenshot.** The hero currently composes the plugin's own
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

**Live at https://paperninja20.github.io/shizen-site/**

To publish a change:

```sh
site/tools/publish.sh "what changed"
```

That mirrors `site/` into the public `Paperninja20/shizen-site` repo, which
GitHub Pages serves. It rsyncs with `--delete`, so a file removed here is
removed from the live page too.

### Why a second repo

The plugin repo is PRIVATE, and GitHub Pages will not serve a private repo on
a free plan. The two alternatives were making the plugin source public to
obtain a landing page - a bad trade for something being sold - or paying for
a plan to host one static page. So only `site/` is mirrored, and the source
stays private.

`site/tools` is deliberately NOT mirrored. `make-type.py` reads the licensed
omake font out of the plugin tree, and that licence forbids redistributing
the font data; publishing a script that points straight at it invites exactly
that. Regenerate type in this repo, then publish.

### A real domain

When one is pointed at the page, update **`og:url`** and **`og:image`** in
`index.html` - both are absolute, because link unfurlers do not resolve a
relative URL, and both currently name the github.io host.

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
