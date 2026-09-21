# Motion refinement and Dark Knight palette evidence

September 17, 2026 local. Prior b57e51d was progress: smaller generated Samurai
artwork and exact private runtime evidence. This continuation produces three
built-in-imagegen source sheets and reviews their native conversions. No ROM,
import selection, package, launcher, player save or running game changed. No
runtime tests were warranted for these uninstalled art studies; existing passing
evidence remains applicable to its original candidates. All G gates stay open.

## Samurai motion

Exact prompts, source/reference hashes, tool-output paths and review findings:
`src/art/imagegen/samurai-march-v5.json` and `samurai-march-v6.json`.
Both outputs are 1536x1024, six cells, generated from the new red Samurai design.
The authenticated original Ninja sequence is a motion reference only; its pixels
are not copied into the new character.

v5 improves lifted-leg visibility but FAILS the third column: the supporting
front boot disappears and the back view repeats the same lead leg. v6 edits
those two poses and shows both boots and opposite lifted legs in source and
native conversion. Conversion uses 3 columns, 2 rows, height27, nearest sampling,
and direct native palette0x419d80. Native bounds are17x27,17x27,18x26,
17x27,17x26,17x26. The face/helmet shifts and minor costume drift remain
unaccepted. Do not conflate successful gait reversal with final art acceptance.

v6 source SHA-256:
`f9e0b2071693f38cb856538377d75b412907b6c7c3d7d70c20ad35f8e32e0a47`.
`scripts/review-samurai-motion.py` authenticates source/reference/converted tile
hashes and creates these private review artifacts under
`build/art/imagegen/samurai/native-scale-study/`:

- `march-v6-motion.gif`: original motion at left, generated Samurai at right;
  front above/back below. Sequence A/B/C/B. GIF delays270/130/270/130ms
  approximate the native16/8/16/8 ticks at60Hz to GIF's10ms granularity.
- `march-v6-motion-phases.png`: all four comparison phases; visually inspected.
- `march-v6-motion-review.json`: source hashes, sizes, timing and descriptive
  brown lower-leg pixels. Sheath pixels can share that color; samples do not
  automatically prove gait acceptance. The composited loop is not a game capture.

Only conversion/compositing is coded; all new character pixels came from imagegen.
The last runtime-tested Samurai remains v4 on private0fa7d170. Neither v5 nor v6
is imported or production accepted.

## Human Dark Knight

The older large concept sheet was simplified into a six-pose imagegen sheet.
Exact prompt/provenance: `src/art/imagegen/human-dark-knight-march-v2.json`.
Private source: `build/art/imagegen/human-dark-knight/march-v2.png`.
Native sizes are16-17 pixels wide and26-27 tall. Source still FAILS motion/costume
continuity: the middle back pose swaps the cape's shoulder, and the final front
phase repeats the first lead foot. No production acceptance or import.

The existing class manifest selects native palette0x419d60 for job117. Comparing
two conversions of this SAME source with the SAME crop/scale/sampling isolates
a substantial color limitation:

| Conversion | Source-color mean squared RGB error | Visual finding |
| --- | --- | --- |
| Exact assigned native palette | 758.4932 | Violet armor becomes green; burgundy cape becomes brown |
| Generated15-color palette | 139.7721 | Violet steel and burgundy cape retained much better |

Inspected both `native-review.png` files under
`build/art/imagegen/human-dark-knight/march-v2-native/` and
`build/art/imagegen/human-dark-knight/march-v2-own-palette/`. The latter is a
conversion comparison, NOT proof the game can allocate/display that palette.
Error describes the color mapping only, not silhouette quality or full fidelity.

Reproduce with `scripts/convert-generated-sprites.py`, source path above,
`--columns 3 --rows 2 --height 27 --resampling nearest`; add
`--native-palette-offset 0x419d60` for the native case and omit it for the
independent comparison. Output to the two named private folders. Prompt record
pins source/reference hashes, palette hashes, settings and measurements.

## Next implementation priority

Independent actor palette allocation is an existing open requirement, now tied
to a concrete rejected color conversion. More artwork generation alone cannot
correct this native palette mismatch. Reuse the earlier audit in
`notes/assembled-art-technical-delivery.md`, rather than treating a new palette
ID as a finished allocation implementation.

Current static reinspection of the clean ROM confirms native0802292C calls
080CBA3C with index0 and copies512 bytes at08022990, then calls080CBA84 and
copies512 bytes again at080229A6. These are bulk16-palette paths. CBA3C selects
the normal/color-mode source tables. This reinspection is static evidence only;
no new free-bank or lifetime claim is established.

Next trace actual palette ownership/load/update across battle and menu consumers,
then implement bounded allocation/remapping with explicit coexistence evidence
for original actors, weapons, effects and UI. Preserve original source palettes;
do not overwrite a shared bank merely to make the Dark Knight look correct.
Motion/face/costume corrections can reuse the saved imagegen sources once the
palette contract is real. The packaged technical preview a6d883b5 stays unchanged.
