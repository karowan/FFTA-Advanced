# Approved native Dark Knight color transfer

The native Human Dark Knight base is user-approved, keyed by PNG SHA256
`df111ab83c90de87948abb7aaf73e16a80de2b5dd6ebefba35ea518309cf3eed`.
Its original and regenerated bases have99.90% alpha-grid agreement. That permits
a color-only calibration from aligned opaque source pixels to approved native
indices. This is offline conversion into palette0, not new palette allocation,
runtime remapping, hand-painted pixels, or a new drawing system.

## Reproduction and review

`scripts/study-approved-native-transfer.py --job 117 --select 5` authenticates the
original source and approved native PNG, compares1/5/9 nearest reference colors
in Oklab, and writes all66 Dark Knight poses. A weighted vote selects existing
native indices only. The same RGB maps consistently across all converted poses.
All pose silhouettes are preserved. Where a pose uses the original neutral base,
the exact user-approved replacement PNG is inserted instead of re-converting it.

The primary agent inspected all66 source, direct-conversion, five-neighbor and
nine-neighbor poses. The five-neighbor result preserves dark armor, brighter gold
and blue cloth more faithfully than the rejected direct conversion. This is an
integration pilot, not user approval of every derived frame. Aligned reference
colors are not semantic material labels; inspect future races independently.

Run the eight declared steps in `scripts/native-color-transfer-test-plan.json`
through `Test Expansion.ps1 -Plan scripts/native-color-transfer-test-plan.json
-Suite native-color-transfer`. The source catalog is unchanged. The importer
uses a separate conversion manifest and writes a separate candidate. It archives
the recipe and every actual imported PNG by hash.

Render the review with `scripts/build-native-color-transfer-review.py --run
build/expansion/test-runs/20260920T172357.910115Z/report.json`.
Private gallery: `build/art/native-color-transfer-2026-09-20/index.html`.
Six screenshots are copied byte-for-byte from the test runs, without retouching.

## Verified checkpoint

Candidate ROM: `bee412823471003eb42b4f7cbf0f65bc81a095a2`.
Candidate manifest:
`build/art/native-color-transfer-2026-09-20/dark-knight-candidate.json`.
All eight selected steps passed in runner `20260920T172357.910115Z`, which exited
successfully with source inputs unchanged. This is targeted Dark Knight art
verification, not a full integration-suite run.

- Native conversion contract:20722 checks; all66 poses, exact approved base,
  cross-frame RGB/index consistency, unchanged native palettes and actual ROM
  tiles. Report under `build/art/native-color-transfer-2026-09-20/checks/20260920T172418.652464Z/`.
- Full animation import:26921 checks, preserving675 poses,3025 draw records and
 1116 controls. No action slots replaced with idle stand-ins.
- Own-ROM cold entry:38 checks;
  `build/art/reviewed-integration/runtime/20260920T172421.520145Z/report.json`.
- Move/Fight/next turn:6141 checks,608 sampled action frames,24 damage;
  `build/art/class-fight/20260920T172433.414499Z/report.json`.
- Move/Combo/next turn:18242 checks,608 sampled action frames,24 damage and a
  single3-JP debit; `build/art/class-combo/20260920T172450.470608Z/report.json`.
- Natural water entry/cancel:1270 checks;
  `build/art/reviewed-integration/water/20260920T172508.045092Z/report.json`.

The stale Combo-observation bug is fixed: composition events are retained for
the report, but are not compared against later hardware after tracing ends.
The current native Dark Knight Combo and water cases pass on this candidate;
the previous failed evidence remains intact. Other unrun native cases are not
implicitly passing.

No launcher or installed preview was changed. Tests used disposable own-ROM
checkpoints and verified their source saves unchanged. The other nine classes
still use their previous conversions in this pilot, and menus/portraits retain
the engineering parent's assets. Remaining work: settle Samurai skin, complete
the other native bases, apply/review colors through every pose, assemble all
graphics consumers, verify the final combination, and deliver the running game.
