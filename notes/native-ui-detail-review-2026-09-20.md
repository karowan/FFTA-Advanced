# Targeted native UI review, round five

[Complete review page](../build/art/job-art-approval-v5-2026-09-20/index.html).
Five proposals change from round four: the Human Dark Knight portrait and badge,
Human Samurai badge, Viera Dancer badge and Viera Mystic Knight badge. Fifteen
other portrait/head surfaces are byte-identical. The page retains every job,
animation, ordered keyframe, original reference and preceding in-game screenshot.
Before/after cards are at the top. Annotation uses Codex browser comments only.
These proposals await user approval and are **not imported into the game**.

## Changes and conversion decisions

- Dark Knight portrait: imagegen edited the eyes using the original FFT reference.
  Point sampling again made the two shapes unequal. Area sampling to the same
  48x56 grid retains similar rounded golden vertical eyes. The native palette is
  still original human job 10, index 16. No eye pixels were hand-painted.
- Dark Knight badge: regenerated frontal helmet. The second generation still
  placed eyes at columns 5 and 9. Fixed horizontal nearest-neighbor registration
  `[4/3,0,-4.5,0,1,0]` maps them onto required columns 7 and 10, rows 7 and 8.
  This is a documented technical placement/scale adjustment, not a generated
  bounding-box fit or code-drawn/mirrored helmet. Gold trim/shading and trailing
  blue cloth are not asserted to be pixel-symmetric. Visual acceptance remains
  separate from the passing eye-coordinate check.
- Samurai badge: model narrowed the red helmet and retained the gold crescent.
  The same 19 original Human facial pixels are restored during conversion.
- Dancer badge: short white bob, gold hoop and wine-colored collar. Opaque black
  letterboxing required an explicitly inspected strip crop, recorded in receipts.
- Mystic Knight badge: long white hair, angular gold temple piece with a red gem,
  and dark collar. The first ornament was too small after sampling; a second
  model edit enlarged it. Both Viera retain the same 37 native facial anchors.

All colors come from existing native palettes. Artwork is model-generated;
code performs sampling, registration, native conversion and extraction of shared
original face pixels. No custom palette bank or runtime routing changes.

## Reproduction

Use [round-five preparation/conversion](../scripts/revise-ui-art-round5.py) and
[review builder](../scripts/build-art-approval-round5.py). The builder reuses
the round-four converter, template and deterministic verifier. Defaults still
reproduce round four. Source records are frozen under
[round5](../src/art/native-ui-review/round5/results.json); raw generated images,
native references and rejected attempts remain ignored under
`build/art/ui-detail-v5-2026-09-20/` and previous review folders.

With those private inputs present, restore the preserved `plan.json` and
`generated-paths.json` to the round-five build folder. Run:

```text
python scripts/revise-ui-art-round5.py ingest
python scripts/build-art-approval-round5.py
node --check build/art/job-art-approval-v5-2026-09-20/page-script.js
```

The prepare action creates a fresh initial plan and refuses to overwrite one.
Final retry prompts, reference hashes, strip bounds, sampling and registration
are recorded in generated-paths and results; replaying only the initial plan
does not reproduce the final revisions. Imagegen model version/seed are managed
by the tool and unavailable. Each generation is one asset, with raw output
preserved. The full review merges five new results with seven round-four results;
the other eight portraits remain from earlier approved-for-review generations.

## Verification and limits

Passed: raw/reference/output hashes; twelve merged asset dimensions and exact
native palette membership; shared facial pixels; closed-helmet eye coordinates;
unchanged native frame and lettering indices; 1,716 linked review assets;
unchanged 675 poses, 796 sequences, 3,025 drawing records, 1,116 controls and
884 unused slots. Fifteen unaffected portrait/head images match round four
byte-for-byte. Page JavaScript syntax passed. Native converted candidates were
visually inspected at integer magnification.

No game build or runtime test is warranted for this offline review-only change.
Screenshots still show assembled build `316a40524b960c49ad7213ac4b0bea539bfa9513`.
Live browser layout QA remains unavailable after the earlier local-file
navigation restriction; no alternate route was used. Anchor checks do not
establish artistic approval, perfect symmetry or full animation acceptance.
