# Native water transition proof, September17

Subsequent bounded coverage: notes/native-natural-water-proof.md adds original
map92 terrain through the existing encounter shell, without modifying water flags.
Its paired movement/cancel test passes7,889 checks. The older test described below
remains a synthetic Giza water-flag fixture; neither proves all-class water or the
original water map's campaign mission.

Current private candidate remains714f45eb9997ad39d11b13f92c35d5b0de1a0e7f.
No ROM edits were needed. Temporary imagegen poses remain transport assets.

## Actual paired movement

Declared test-generated-actions-water uses the existing authenticated world
seed, deployment and canonical Giza formation. Its one additional terrain
input sets flags bit2 on tile4,14; native movement calculates the submerged
height and chooses resource261. No live actor or resource pointer is written.
Native B cancels the move, returning Viking to1,14 and resource260. Both the
previous75029dea and current714f45eb complete these transitions with identical
owned gameplay hashes and retired action roots. Four generic bodies are sampled.

Runner221611.833257Z completes both scenarios, then fails its graphics oracle
on one queued land/water upload. Complete immutable captures/report are in
build/art/generated-actions/battle/20260917T221612.382005Z/. There are7,885
successful recorded assertions. Final retained acceptance is declared
test-generated-water-retained, runner20260917T221859.858589Z:40 checks pass,
reusing those completed scenarios. Report:
build/art/generated-actions/water-retained/20260917T221900.464725Z/report.json.

The retained verifier authenticates the failed report by SHA256, both ROMs,
captured VRAM and parsed actor metadata. At generated/cancel-move-40, the
land260 record has native deferred-transfer flag0x100000 while all512 bytes
still exactly match the preceding directly verified water261 frame. Eight
frames later the land upload is directly verified. The helper accepts only one
such hold within the same allocation and one explicit owned land/water pair.
It rejects modified pixels, wrong resource, tile, allocation, missing pending
flag and chaining from an unverified predecessor. The original failure remains.

Earlier221422.722451Z failed because the fixture used key512 instead of the
established native B mask1. It also exposed a single walking sequence rewind:
index/timer reset to0 while the entire previously verified upload and source
remain exact. The corrected helper allows only that bounded same-sequence hold.
This is distinct from the subsequent pending land/water resource swap.

## Limits and next work

This is a controlled water-flag terrain fixture. The displayed background is
still Giza, which has no natural water tiles. It is not acceptance of a natural
water map, every class's water playback, all commands, auxiliary graphics,
custom actor palettes or finished animations. All20 native resources' existing
26,640 format/widget/rebuild checks and the8,131 actual Move/Fight checks remain
applicable because ROM bytes are unchanged. G01-G04 remain open.

Native terrain lookup uses global02007f10, grid pointer+4, width byte+8;
each tile is(height,flags). Native0801cc38 subtracts1 from a water tile's height
for an ordinary walking unit. The wrapper appearance selector calls08022268
for water,08022238 for land; their getters080cb750/080cb714 preserve16-bit IDs.
Unit byteFD=2 permits the walking water appearance. Wrapper+34 is its resource,
+44 is its body object. Preserve these distinctions in future fixtures.

Older all-class Combo reports survive under candidate687ed5d4/combo-ui, but
their referenced turn-ready.state files and frozen.gba are no longer present.
Do not call those files reusable live fixtures or rerun full Combo acceptance
merely to recover them. Reuse the established scenario procedures and the new
paired water-ready snapshots for bounded affected graphics tests where valid.

Next: remaining weapon/action families and independent palette/equipment/effect/
status consumers, then assembled technical packaging. Latest user direction
defers final art refinement until this technical pipeline works end to end.
No external model, council, publication, game launch or player-save change.
