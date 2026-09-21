# Sprite-based badge revisions and portrait eyes

The user rejected all round-two equipment badges and preferred the original
sprite-derived batch. The Human Dark Knight portrait read as three eyes; the
Viera Mystic Knight's far eye also needed correction. No approval of other
surfaces is inferred from these comments.

[Complete round-three page](../build/art/job-art-approval-v3-2026-09-20/index.html)
shows first-batch badges beside ten new model-generated edits, plus clean
original same-race icon references. Both eligible and ineligible native colors
and native-size strips remain available. The two portraits received targeted
eye edits; the previous portrait versions are displayed for comparison.
All original animation/keyframe groups, screenshots and inventory remain.
Use Codex integrated browser annotations; no page annotation system was added.

## Changed process

The round-two icon references were equipment-screen crops, some with the native
dim/stippled appearance. This round uses the clean indexed icons previously
decoded by [the native UI exporter](../scripts/export-native-ui-reference.py),
cropped to the fixed head window. The first sprite-based badge is the edit target.
Four clean original icons guide anatomy, eye shapes and pixel density; the
existing native color swatch is another input. No original job is repainted
into the new class. Each edited icon has its own imagegen call.

Each output is sampled directly to 16x14 once, with no bounding-box fit or manual
pixel repair. Portrait edits similarly sample directly to 48x56. Palette mapping
uses only the unchanged native palettes already recorded in round two. Label and
frame pixels outside the badge head window are preserved exactly. No palette
bank, ROM, runtime route or player save is changed.

The Moogle attempts needed additional costume references: the first Chemist
adopted a reference job's blue star cap, and the Bard lost its feather. Both were
regenerated with the approved concepts. A further Chemist attempt strengthened
the pale face outline after native-size inspection. These remain candidates;
especially at 16x14, a larger generated image is not proof of better definition.
The first batch remains directly available for comparison and fallback.

## Reproduce and inspect

- [Preparation and conversion](../scripts/revise-ui-art-round3.py): `prepare`
  creates immutable inputs; `ingest` consumes preserved generated paths.
- [Complete page builder](../scripts/build-art-approval-round3.py)
- [Page template](../scripts/art-approval-round3.html.txt)
- [Initial prompts and reference hashes](../src/art/native-ui-review/round3/plan.json)
- [Final prompts, references and output hashes](../src/art/native-ui-review/round3/results.json)
- [Rejected attempt records](../src/art/native-ui-review/round3/rejected-attempts.json)
- [Review provenance](../build/art/job-art-approval-v3-2026-09-20/revision-proof.json)

Use built-in `image_gen.imagegen`, one call per asset, with each preserved prompt
and exact reference list. Model version and seed are tool-managed, not exposed.
Generated-path records can carry a revision prompt/reference list and versioned
raw filename; preserve the original plan and rejected outputs. Raw generated
images and compiled review files remain ignored. Run ingest, then the page
builder. Do not integrate these proposals before user review.

Verification passed for all twelve revised native dimensions and palette-index
bounds, exact native palette colors, reference hashes, unchanged badge pixels
outside the head window, and all page image paths. The complete 675-pose,
796-sequence, 3025-draw, 1116-control, 884-empty-slot inventory equals round one.
The extracted page JavaScript passes Node syntax checking. Native comparison
images were visually inspected. Browser layout was not rechecked because local
file navigation was previously blocked; no alternate route was used. This is
review-only work, so no game builds or runtime test runs were required.
