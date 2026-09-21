# Native palette constraint and rejected color conversion

## Latest user direction

Update: both approved human bases have now been propagated and the Samurai
tested in-game. See [the verified human checkpoint](native-human-integration-2026-09-20.md)
for all 132 human poses, exact backup preservation and six in-game screenshots.
The later sections below preserve the historical color-review sequence.

The user wants brighter colors and better contrast to match the original jobs.
The user explicitly approved Human Dark Knight v1 in native colors: "dark knight
in native, no notes". Preserve that exact native PNG; its approval and hash are
recorded in the source receipt. Samurai v4's face and hands were too red.
The user has now selected the exact Samurai `Palette1 - neutral` backup with
the muted scarf as the approved native base. Stop scarf variants. Its PNG hash
is `2fbe4a56e9b68e9a919cf8b6eb9cc76e4ae7b5aaafee5cf711b72ef63178b76b`.
This restores the entire selected backup, including its original face, rather
than mixing features from the later generated trials. Both human native bases
are approved; this does not claim completed animation propagation.
Current comparison: `build/art/native-color-study-2026-09-20/base-review.html`.

The exact `human-samurai/palette-1-neutral.png` comparison, previously a conditional
fallback, is now explicitly approved. Its preserved copy and SHA256 are recorded
under `nativeConversions` in `src/art/race-study/native-color-study-v1.json`.
Reproduce its existing `neutral` conversion from the original approved source;
do not introduce a new color-transfer approximation or regenerate this base.

The approved native Dark Knight has since been propagated into an isolated
66-pose battle-art candidate, with passing Fight/Combo/water playback and intact
in-game screenshots. See [the exact checkpoint](native-color-transfer-2026-09-20.md).
The remaining classes and final combined build are still unfinished.

The user explicitly requires the game's existing native palette system. Runtime
palette ownership/remapping and extra custom banks are retired. Two experimental
scanner optimizations were slower and have been abandoned; their uncommitted
source was archived under ignored `build/art/rejected-palette-trials-2026-09-20/`.
The engine scanner source was restored to the preceding committed version.

## Native build checkpoint — functional, visually rejected

Starting directly from accepted engineering
`a28b624bb13c8f2f2597a4d4bd3999b17c234b99`, the reviewed poses were imported directly
into existing native palettes. Combined candidate:
`e11b2603b93f7b74cbe497291af22cd9a3f9f468`, manifest
`build/art/reviewed-integration/native-complete-candidate.json`.

All675 source poses,3025 drawing records and1116 control records remain. The
20 land/water resources retain all native animation durations and commands.
Miniatures use the native archive and shared menu palettes without any upload
or palette hook. Portraits use the existing native47-opaque-color archive format.
Badges use unchanged native palettes. No new executable code or RAM reservation
is introduced. The complete contract check verifies all other ROM bytes equal
accepted engineering, including palette tables, class/side selectors and native
graphics entry points.

Terminal runner `20260920T164234.764495Z` passed native contract2805, cold entry38,
all-ten menus815, all1592 mode transitions7184, and action-import26921 checks.
Runner `20260920T164431.827300Z` passed all-ten Fight playback, capacity18016 and
native save/Continue21 checks. Capacity uses the declared formation324 encounter
fixture; ten bodies are allocated among13 actors, and nine appear in its sampled
viewport. All ten have individual Fight/menu screenshots.

Thundaga plus repeated Status passed5995 checks in
`build/art/capacity-action/20260920T164946.561171Z/report.json`.
Native Dark Knight Combo test adaptation remains unfinished: retained failed
runs164945,165102,165203 and165307 exposed stale custom-observer assumptions,
offscreen-jump assumptions, then a composition snapshot used after its observed
window. No game code was changed for these test failures. The remaining water
and Bard Combo cases in those stopped runs did not execute. Resume only after
the artwork direction is resolved; do not label these cases passing.

The native preview was installed separately under
`saves/reviewed-native-art-2026-09-20/`; nine existing files were preserved. Its
launcher ValidateOnly passed, but the new native desktop game was **not launched**.
The user then rejected its colors in the22-image gallery. This is not a completed
art delivery, production approval, or a new campaign acceptance. Existing games
and saves remain untouched.

## Color investigation

`scripts/study-reviewed-native-color.py` compares RGB555 nearest distance,
perceptual Oklab distance and an added neutral-chroma penalty for all ten bases
against all three native shared palettes. Sources and alpha geometry are
unchanged. Oklab conversion follows the author's
[published matrices](https://bottosson.github.io/posts/oklab/).
The neutral penalty is an experiment, not a proven perceptual improvement.

The comparisons show that changing the distance function alone has little
effect on the largest costume shifts. Palette0 provides blue/green/teal ramps;
palette1 provides strong reds and purple ramps; palette2 provides gold/green
ramps. All have common dark/cream/warm accents. A sprite cannot independently
select arbitrary colors from all three at once under the current body contract.

**Palette selection is not restricted by race.** In the original clean ROM,
human jobs6,7 and11 already use ally selector1, while jobs2–5 use selector0.
Selectors are the low/high nibbles of class-record byte11 (ally/enemy). Palette1
contains native reds `#BD0808` and `#EE4139`. The rust/brown Samurai trial used
palette0 to preserve teal; the user correctly challenged that tradeoff. The next
Samurai trial uses palette1, retaining red armor and adapting the scarf to a
muted neutral tone. This is a design comparison, not approved costume revision.

## Imagegen trials and next checkpoint

Private outputs: `build/art/native-color-study-2026-09-20/`. Source receipts:
`src/art/race-study/native-color-study-v1.json`.

- Samurai v1: source + palette0 + full concept. Rejected: generation increased
  detail and changed proportions; it did not enforce the requested palette.
- Samurai v2: short recoloring prompt, source + palette0. Still rust/brown; not
  a satisfactory replacement for the defining red armor.
- Human Dark Knight v1: source + palette0, deliberately dark armor/gold/blue.
  Native32px base explicitly approved by the user; not propagated.
- Samurai v3: source + palette1 + user's native red-costume example. Exact
  conversion retains strong red armor; scarf becomes muted gray/purple.
  The user liked this design except possibly the scarf color.
- Samurai v4: targeted imagegen edit of v3, ivory scarf; all other features
  requested unchanged. User rejected the red appearance of face and hands.
- Samurai v5: imagegen edit of v4 requesting cream face and hands with sparse
  peach shading. A red patch appeared below the chin; retained as superseded.
- Samurai v6: imagegen edit of v5 correcting that patch to cream neck skin.
  User rejected cream skin blending with the ivory scarf. Compared with v4,
  the alpha silhouette and eye pixels are unchanged. There are32 changed indexed
  pixels, including incidental shifts among existing red/gold costume colors;
  this is not a claim that generation preserved every unrelated pixel.
- Samurai v7: original human skin references from clean-ROM jobs2/3/7 were
  included with v4 in imagegen. The face and hands use the original ochre
  ramp, native indices5/6/7. User rejected the remaining ivory scarf.
- Samurai v8: violet scarf with lavender highlights. User rejected the color
  pairing; retain its prompt/output as failed evidence.
- Samurai v9: user-selected yellow scarf, cream highlights and orange shadows,
  generated from v7. Exact native palette1 conversion has the same silhouette
  and face pixels as v7;36 indexed pixels changed overall. User subsequently
  chose the original muted-scarf backup instead; v9 is retained as rejected.

`scripts/prepare-native-human-skin-reference.py` reproduces the original human
reference board from authenticated ROM tiles, OAM and each job's palette selector.
It reproduces the exact reference PNG hash used by v7. Native skin colors are
shared warm ramp entries, not the pink costume-ramp entry10 or cream alone.
The live baseline references use table0x419d60; the script also shows the native
0x41a860 reference bank separately without substituting it for live colors.

For v9, use the saved built-in imagegen prompt/references in its source receipt,
then `scripts/convert-native-palette-study-output.py --source <saved-generation>
--slug human-samurai --version v9 --palette 1 --prompt
build/art/native-color-study-2026-09-20/samurai-generation-v9.json`.
Review `build/art/native-color-study-2026-09-20/samurai-yellow-scarf-v9.html`.
All generation/reference hashes, fallback bytes and review-page links passed.
No game assets were changed during the scarf review.

Skin-review verification: generated/output hashes and every local review-page
link passed; native conversion asserts the unchanged palette and indices0–15.
No game assets were replaced and no runtime tests were needed for this review.

`scripts/convert-native-palette-study-output.py` performs uniform nearest-neighbor
sampling to32x32, alpha threshold128, then exact native-index mapping. Every
opaque pixel is1–15 and the palette is byte-derived from the clean ROM. This
does not claim imagegen obeyed the palette exactly or preserved every source
pixel. Inspect the converted result, not just the large generation.

Do not generate675 replacement poses from these drafts. First settle native
palette choice and a convincing base for each design. Then carry the fixed
color mapping/approved regenerated base through every frame, including rear,
water, attack, casting, hurt, KO and other existing native modes. The integration
goal remains active; user review of the base colors is the current checkpoint.
