# Samurai support-pose draft and native assignments

September 18, 2026. Follow-up to `10fbf46`. Built-in imagegen only; no external
provider, new agents, publication, visible game launch or player-save changes.
The installed technical preview remains `7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b`.

## Generated source and visual review

`src/art/imagegen/samurai-support-v1.json` retains the exact prompt, model/tool
description, source path/hash and both reference identities. The 1983x793 PNG
contains ten cells: neutral, raised arms, recoil, kneeling and fallen, each
front/back. The generated red Samurai v7 is the character reference. Original
resource4 is a pose/scale reference only; its pixels never enter the new art.
The native-pose contact sheet is reproducible with `review-samurai-support.py`.

Source SHA256: `b90e9ce8420ee23b07d8e278bcd0ef347e8bc59eff2a890474a4e190e1f4cac3`.
Private source: `build/art/imagegen/samurai/action-study/samurai-support-v1.png`.
Conversion: same directory, `support-v1-own/`. Five columns, two rows, common
height27 scaling, nearest sampling, alpha>=128 and the exact v7 class palette:
`f2a1d15c882bf57fa90d88f3927f251a66bb6001a49382a5fe2e2dbf433d3d7c`.
The new authenticated `--palette-file`/`--palette-sha256` options preserve color
indices across action sheets. The existing conversion manifest's historical
`native-palette` name means supplied palette mapping here, not original colors.

Only the eight support poses are imported from this sheet. Existing v7 neutral
front/back frames remain authoritative; the two new neutral drawings are scale
and identity references. Common scaling preserves shorter wounded/fallen bodies:
front raised20x27, recoil18x24, kneel21x19, fallen28x13; back raised20x26,
recoil19x23, kneel21x19, fallen28x15. Exact white eye pixels remain in front
raised/recoil, with one white pixel in front kneel. A dark preview background
must not be used to infer a missing indexed feature.

Root reviewed source and `support-v1-comparison.png` against native originals
at equal game scale and baseline. It shows original front, generated front,
original back, generated back. This is a composited comparison, not a screenshot.
Head angles in the back support poses expose more side face than the march;
that continuity difference is still open. These are private drafts, not accepted
production art. Review labels are annotations, not game typography.

## Import

`live_action_plan.py` authenticates the clean ROM and exact native tile/OAM pose
identity, then substitutes the declared generated cell everywhere that original
pose occurs. It verifies original descriptor metadata, null slots, frame count,
commands and timing against the retained transport before mapping. Assets must
share the class's exact palette and match source, conversion, indexed image and
binary tile hashes. Missing/duplicate/unused/foreign assignments fail explicitly.

`samurai-support-v1-plan.json` maps eight support and two v7 neutral pose keys.
The live palette override selects this plan by hash. It changes104 frame entries
in40 land slots, including both facings of recoil4/5, kneel6/7, fallen10/11 and
raised arms in30/31 and other consumers. It also fixes neutral return frames in
the affected sequences. Unmapped frames keep the previous temporary transport.
Native control timing is preserved even where the same body pose appears in
multiple animation families. This is deliberately partial coverage.

Private connected candidate: `5fe7c35d4b4a89e71f3cdc059e5bff75e747ee33`.
Palette stage: `edd40194f6f957f43e5310ee60a8547ea0d1d844`.
Resolve from `build/art/refinement/samurai-support-v1/current.json`;
full manifest is `build/art/generated-effect/5fe7c35d4b4a89e71f3cdc059e5bff75e747ee33/samurai-support-v1-preview.json`.
It is not packaged or installed. The compiled engine and every class palette
are byte-exact to v7. Other class pixels, water, unmatched poses and timing stay
unchanged. The current palette reservation has9,568 bytes left (252,576 used of
262,144); future larger action sets require explicit authenticated data-space
planning. Do not silently overflow or claim capacity for all remaining art.

## Evidence and limits

Declared runner `20260918T220819.115568Z` is terminal/passed:

- `test-samurai-support-build`:12,661 checks; private construction, unchanged
  engine/palettes, original frame timing, all unrelated pixels/alignment and
  installed/source index preservation. Report:
  `build/art/refinement/samurai-support-v1/20260918T220819.790607Z/report.json`.
- `test-samurai-support-native`:797 checks; actual ARMv4T native widget creation,
  every mapped mode/facing and native phase setter resolve the exact generated
  tiles within16-tile layouts. All104 original occurrences in40 slots reconcile
  independently with the extracted native resource. Eight invalid-input cases
  are rejected. Report:
  `build/art/refinement/samurai-support-native/20260918T220828.820228Z/report.json`.

A final source-normalization rebuild (runner `20260918T221348.663399Z`)
passes12,662 checks and proves the exact same connected ROM. The tracked action
plan/override use canonical LF bytes so Git checkout preserves their hashes.
Report: `build/art/refinement/samurai-support-v1/20260918T221349.298407Z/report.json`.
Only source formatting/provenance and an exact-ROM assertion changed; the native
797-check result is reused because all emitted bytes and pose assignments match.

The native check uses authenticated retained RAM as an isolated allocator
context; it does not run live battle actions or prove VRAM upload. No new live
casting/hit/KO gameplay acceptance follows from native setters. Previous v7
march and mixed-entry evidence remains applicable to unchanged art/engine
behavior, but it is not an exact-new-candidate action playback report.

`review-samurai-support.py` separately reproduces every converted4bpp frame and
palette byte and verifies all104 imported opaque baselines against the original
native pose. It writes `support-v1-review.json` and two comparison images.
No runtime failures occurred in this checkpoint. Initial exploratory shell
lookups used nonexistent test filenames; the declared plan supplied the correct
paths. An initial private reference composition used an incorrect P-mode mask;
it was corrected and inspected before generation. The committed review script
uses index-based alpha and reproduces the actual imagegen reference hash.

Next: actual Samurai attack/body poses and separate held-weapon coordination,
remaining action/water families, consistent menus/portraits, then the other nine
racial jobs. Plan space before expanding the payload. Keep partial art coverage,
live playback and production acceptance separate. G01-G04 remain open.
