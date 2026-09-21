# Samurai native-scale revision study - September17, 2026

**Subsequent correction:** see `samurai-three-pose-transport.md`. Original FFTA
idle steps through three poses; the fixed-feet/breathing premise used below was
incorrect. Keep measured differences as observations, not automatic rejection
evidence. Costume/view continuity still needs review. The newer bounded import
does not replace the packaged preview or accept final artwork.

The prior goal turn delivered the expanded technical preview. This continuation
uses built-in imagegen only to investigate the still-rejected final sprite
quality. It does not replace packaged artwork or close an animation gate.

## Inputs and method

`src/art/imagegen/samurai-native-study.json` records all three exact prompts,
generated source paths/hashes and review decisions. The tool's specific model
name was not exposed; it is recorded as the built-in default, not invented.
Sources remain private under `build/art/imagegen/samurai/native-scale-study/`.

Original human resources0/2/4/6 were extracted from authenticated native tile/OAM
records solely as proportion and pixel-density references. The first three
idle figures measure16x27 opaque pixels; resource6 is16x29. This explains why
the previous wide, nearly square generated design looked unlike the originals.
No original character served as a painted-over base.

Imagegen created a new narrow red-armored Samurai, then corrected the eye/crest
using its converted image as an edit reference, then produced two front and two
back idle frames. All outputs are1254x1254 despite the initial1024x1024 request.
They also fail the exact requested logical grid. Do not label them native-ready
merely because they contain large square shapes.

`scripts/review-samurai-native-study.py` reproduces reference extraction and five
existing-converter configurations. It authenticates each original/generated
source, applies the actual Samurai palette419d80, produces indexed native-size
comparisons and measures idle-pair changes. It never draws character pixels.
There are no game executions, ROM changes or new runtime fixtures in this study.

## Findings

- First native-v1: the27px conversion improves human proportions, but loses the
  eye and crescent. Box averaging merges costume detail; nearest is preferable.
- Native-v2: the eye correction survives, but the14px-wide27px-tall conversion
  still loses the crescent gap.
- Idle-v5 at maximum27px: converted widths15px and heights26/27px; crest remains
  weak. At maximum30px, widths17px and heights29/30px retain both the eye and
  the crescent gap. This is a promising silhouette/face direction, not final art.
- **Idle-v5 consistency is rejected.** Front pair differs86 indexed pixels,
  including4 in the bottom five rows. Back pair differs190 pixels, including6
  in those foot rows; armor/boot shapes shift beyond a subtle breathing motion.
  Counts are observations, not an automatic aesthetic acceptance threshold.

Review artifacts:

- `build/art/imagegen/samurai/native-scale-study/review-comparison.png`:
  columns are original Soldier, original Paladin, packaged temporary Samurai,
  v5 front and v5 back; all enlarged with nearest-neighbor after native conversion.
- `build/art/imagegen/samurai/native-scale-study/v5-h30/native-palette-review.png`:
  all four candidate idle poses in the actual native palette.
- `build/art/imagegen/samurai/native-scale-study/review.json`: authenticated
  reference/conversion metadata and exact continuity measurements.

Next, fix the phase-to-phase costume/foot drift through imagegen before extending
to a walk or attack sheet. Review both directions at native size, preserving
anatomical sheath side and silhouette. Do not solve the mismatch by claiming
repeated idle poses are completed animation or by hand-drawing replacement pixels.

The playable a6d883b5 preview, production catalog and existing player files remain
unchanged. G01-G04 remain open. No runtime suite was rerun for an uninstalled
art study; source syntax, asset hashes and conversion reproduction were checked.
