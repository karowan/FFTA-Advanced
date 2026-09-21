# Samurai walking material-color review

[Complete round-eight review](../build/art/job-art-approval-v8-2026-09-20/index.html).
User feedback identified inconsistent colors across the front walk and an exposed
skin-colored left sleeve in rear pose p005. The inconsistencies exist in the
generated RGB drawings; neutral nearest-color conversion amplifies them within
the limited native palette. Sharing a palette alone does not fix material drift.

Four step poses are revised: p000, p002, p003 and p005. Accepted neutral p001 and
p004 are retained unchanged. These poses occur only in Samurai land walk slots
0 and 1. No other action artwork is represented as newly approved or corrected.
The full page keeps all jobs, portraits, icons, animation sequences and keyframes,
with existing zoom controls and Codex browser annotations.

## Reproducible method

[Preparation, conversion and review builder](../scripts/revise-samurai-walk-colors.py).
Use `prepare` only for a fresh plan. Final conversion uses `ingest-individual`;
`ingest` alone reproduces the rejected combined-sheet experiment. Then run
`build` and Node syntax checking on the new review's page-script.js.

The combined-sheet generation moved internal details and was rejected. Four
separate built-in imagegen edits use each original native step as the target,
the accepted same-facing neutral as color reference, original Samurai concept
for material identity, and existing native palette swatches. The p005 helmet
gets a further focused edit to remove pale highlights from lacquered armor.
Exact prompts, references, raw outputs and failed receipts remain preserved.
Model version and seed are tool-managed.

The generated p002/p003 drawings shifted up by one logical pixel. Their explicit
one-pixel downward registration restores the original positions; it is the best
unchanged-index match among shifts of at most two pixels. This is translation,
not inferred silhouette scaling or newly authored pixels. Quantize to the exact
existing selector-1 colors, checked against the clean ROM. Preserve the original
alpha footprint/contact shadow so only opaque pixel colors can change. This
does not assert that every interior cluster is identical: model-produced color
changes are reviewed separately.

Native review previews retain their original 64x64 canvas and verified body
offset (16,12). Ally and enemy previews use the same new indices with their
existing respective native palettes. No palette banks, class selectors or
runtime allocation/remapping systems change.

## Scope and verification

The new walking images are **proposals, not game imports**. Existing screenshots
still show the earlier assembled ROM. Review data labels the four overridden
poses and retains each original game-tile hash separately. No ROM build or
runtime test is warranted before this visual review is resolved.

Checks cover source/reference hashes, native palette identity, original alpha
footprints, unchanged neutral poses, exact four-pose replacement scope, unchanged
sequence/control records, all other art paths, asset links and page JavaScript
syntax. The page retains 675 total poses and 796 sequences. Native-size contact
sheets and enlarged before/after frames are inspected; these checks cannot
establish user visual approval. Live browser layout QA remains unavailable after
the earlier local-file navigation restriction; no alternate route is attempted.

Final changed-pixel counts are 22 / 48 / 53 / 78 for p000 / p002 / p003 / p005.
In the diagnostic marked-arm region `(7,16,14,22)`, pale indices decrease from
8 to 3 while dark/red sleeve indices increase. This bounds the reported local
correction; it is not proof of semantic color consistency for every action.

Source receipts: [plan](../src/art/native-ui-review/round8/plan.json),
[individual prompts](../src/art/native-ui-review/round8/individual-plan.json),
[final generation paths](../src/art/native-ui-review/round8/individual-paths.json),
[conversion results](../src/art/native-ui-review/round8/results.json),
[review verification](../src/art/native-ui-review/round8/verification.json).
Raw art, ROMs, screenshots and review builds remain ignored.
