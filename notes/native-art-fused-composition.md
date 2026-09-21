# Same-call fused demands: correct, still not response acceptance

September18 local / September19 UTC. Full engineering is required; only artwork
and authored animation-frame content may remain placeholders. Private candidate
`e1a87ecde67f265f666d3ab9d7e50ba401370633` is not installed or accepted. E01–E05
remain open. No player saves, launches, agents or publication. All runners terminal.

## Implementation

This builds on native producer candidatea42c04e1. After authenticated native12BC
composition, the new scoped ARM leaf authenticates current custom ownership and
classifies current OAM in one traversal. A140-byte stack structure contains the
unowned4bpp bank mask, requested classes and ordered8bpp object indices. The
actual current history mapper updates tags and replaces the requested mask with
history IDs before the palette consumer. Nothing is retained across invocations.

The unchanged exact pixel planner still reads all required current8bpp bytes,
preserves clipping and palette-exhaustion refusal, and publishes only after a
valid plan. Preferred-bank validation remains. Invalid object geometry marks the
prepared demands invalid. Native targeting can filter ownership after recording,
so nonzero native_highlight takes the previous native-owner/prefix-planner path.
Generic ownership and palette interfaces remain available with their checks.

`fused_compose=True` requires native producer ownership, native prefix proof,
scoped leaves, ARM OAM classification and fast bank scan. It is a private builder
option. The all-ten-class build has20 history slots, unchanged11316-byte live
state and12KiB RAM reservation. The stage uses251072bytes. Defaultfa3d12b4 is
byte-exact; installed7507ca5c and all source/index manifests are restored.

The fused leaf occupies832bytes, uses72bytes of stack, and requires post-save
SP030072F0 for the temporary-IWRAM path. Its wrapper preserves512 interrupt
bytes above resident native code ending03006D68; deep/external stack calls take
the ROM fallback. Generic ownership and publication leaves remain unchanged.

## Evidence and explicit failures

All IDs were announced and run through Test Expansion.ps1 using
scripts/native-art-test-plan.json. Paths below are under build/art; timestamps
have20260919T prefix. Failed reports and raw logs are preserved.

- Runner013417.290905Z: `test-art-fused-owners` passes17068 checks at
  palette-owners/013417.925678Z/report.json. Actual native composition plus the
 756-count matrix checks fresh owner tags/banks and independently reconstructs
  prepared demands, including affine sentinel tails, alignment and fallbacks.
  Some malformed-counter atomic tests still exercise the prior native/generic
  entries; do not claim exhaustive new fused-entry negative coverage from them.
- Same runner: `test-art-fused-plan` passes488 at
  frame-high-slots/013420.120486Z/report.json. Differential20-history allocation,
  IDs10–19, invalid IDs, exhaustion,128-entry frames, disabled objects, clipped,
  affine/mosaic and out-of-range8bpp cases match the original full planner across
  fresh/warm plans and scoped/ROM stacks, with memory fences and actual PCs.
- Same runner: private build8 and isolated profile292 pass. Profile:
  compose-isolation/013433.555582Z/report.json. `test-art-fused-entry` fails the
  raw paired native-shadow snapshot at live-palette/battle/013433.783581Z/failed.json.
  Later assertions in that entry script remain skipped, not retroactively passed.
- Runner014002.370117Z: `test-art-fused-frame-events` passes31131 at
  native-frame-events/014003.037219Z/report.json. All1024 observed complete native
  states/framebuffers equal ordinary emulation. All512 actual ownership calls
  independently prove the full copied main span and exact current tags. At each
  fused application, bounded dynamic reads capture the actual stack demands,
  fifth count argument and frame descriptor before the consumer instruction.
  The observer independently classifies current OAM/mapped tags and checks the
  complete omitted sentinel tail. No emulated writes or timing normalization.
- Runner014123.842953Z: `test-art-fused-phase-evidence` passes6226 at
  native-phase-evidence/014124.669740Z/report.json. Original native rotations
  account for the observed shadow phases; native DMA/background preservation
  and measured VBlank deadlines pass. `test-art-fused-response-budget` fails
  six metrics, with13 authentication/coverage checks passing, at
  response-budget/014125.183881Z/failed.json.
- Runner014418.022318Z: initial `test-art-fused-consumers` passes240. Its supposed
  split case only moved a unique class to bank9, so that result proves acquisition
  and fallback, not simultaneous split demands. The corrected run014519.070708Z
  passes244 at fused-consumers/014519.786187Z/report.json. All24 cases compare
  full OAM/palettes/VRAM, live state and unrelated game memory againsta42c04e1.
  Fresh/skipped DMA, both stack alignments, highlight off/on, partial/full bank9
  takeover and actual same-class simultaneous history requests are covered.
  Observed PCs prove the fused route, prior highlight route and all-highlighted
  early exit. This uses retained raw inputs with controlled attribute/owner
  variations and synchronous DMA; it is not live targeting UI/action acceptance.

Immutable trace SHA256:
`778dac874761ddb3fa7377f44cbc56f69791ce202c9b472037a3503bc575462d`.

| Offset | Action | Active start/end/duration | Bypass start/end/duration |
| --- | --- | --- | --- |
|0|Move|24 /71 /47|23 /70 /47|
|4|Move|23 /70 /47|23 /70 /47|
|0|Cancel|31 /31 /0|30 /30 /0|
|4|Cancel|29 /29 /0|28 /28 /0|

Mean composition is17.06/17.07scanlines for Move and15.82/15.66 for cancel;
minimum13.09, peak32.07. The fused owner/classifier itself costs4.56–4.69lines.
Palette planning/publication costs4.51–6.01 inclusive; publication alone2.34–2.35.
These modest savings do not solve the one-frame response gaps. Compare against
each candidate's own same-ROM control; absolute onset phases differ between
ready captures. No input-offset cherry-picking, averaging or waiver is allowed.

## Next engineering work

E01 remains an added per-interrupt work problem. Combining passes saved little:
classification moved into the ownership leaf, whose cost increased accordingly.
Next inspect the compiled leaf's repeated halfword/byte reads and large copied
code footprint. Native OAM and owner records are aligned and each record is8bytes;
two validated word reads may replace repeated field loads without dropping any
current-input check. Establish that alignment contract and measure real inclusive
cycles if implementing it; instruction counts alone are insufficient. This is
proposed work, not an implemented or accepted optimization.

Do not retry generic prior-frame caches or move work out of VBlank without
proving all input lifetimes. Continue all E02–E05 gates after performance work,
reusing applicable historical full campaign/save/release evidence on1b070824.
This checkpoint neither completes the game nor changes the installed package.
