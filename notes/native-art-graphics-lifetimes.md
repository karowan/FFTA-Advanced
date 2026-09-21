# Graphics lifetimes and remaining compositor cost

September18,2026. FULL engineering remains the goal; only artwork and authored
frame content are deferred. E01–E05 remain open. Neither candidate below is
installed or accepted. Default palette rebuild is still exactfa3d12b4;
installed7507ca5c, player saves and immutable delivery indexes are unchanged.

## Observed native inputs

`art_graphics_trace.py` extends the pinned native host observer, keeping complete
native-state/framebuffer equivalence checks. It snapshots full native OAM and
32KiB OBJ at08001480, after native composition but before our overlay. Exact
bytes decide equality. Visible8bpp footprints follow clipping/flips, with
conservative affine/mosaic coverage. Thumb STR/STRH and queued DMA destinations
are recorded; original handlers run exactly once.

Installed baseline observation passes1071, runner230941.242611Z, report
native-frame-events/20260918T230941.947642Z/report.json. Each128-frame window has
124 unchanged visible8bpp snapshots for Move and127 for cancel. Every changed
64-byte OBJ tile overlaps an observed immediate queued DMA at08000828. This
does not prove every changed byte had that producer or cover other scenes,
ARM/BIOS transfers, STM/byte stores, or deferred DMA. The skipped-palette flag
alone remains insufficient for reuse. Known direct CpuSet06014300 from080866EC
remains relevant; see native-palette-scan-performance.md.

## Queue-only cache prototype: not a general solution

Private connected2244dce2ffb73bafad190a9bcad7334b00d7a1b2, palette5788d684.
Opt-in `dma_tile_cache=True` reuses the existing2124-byte cache for512 tile
masks and valid bits. A hook before native queued DMA invalidates overlapping
tiles. Delayed/repeating transfers disable reuse until reset; uncached exact
reads remain available. Full and preferred planning use the cache. No new
memory reservation, player data or art changes.

Contract1169/build8 pass, runner232733.256935Z; component report
dirty-cache/20260918T232733.913783Z/report.json. Tests cover all512 tile identities,
read-free warm hits, boundaries, DMA widths/modes, blocked reuse, preferred-bank
conflicts and the native hook on all four channels/both stack alignments.
Registers includingr12/LR, CPSR after the next native flag-setting ADD, IO and
noncache EWRAM match. Retained initial failures:232613.923878Z assembler MOV
syntax;232651.157984Z harness set banked SP before CPU mode. Both corrected.

Entry232809.558912Z fails paired native shadow at ready; capture at
live-palette/battle/20260918T232810.271883Z. Frame observation232939.578530Z
passes5175 but attached the optional cache audit to the wrong observer instance.
It proves observation, NOT cache validation. Corrected runner233159.800600Z
passes5191 and explicitly requires the audit at all1024 graphics boundaries.
It checks every cached mask against current pixels, including15,976 active
tile checks. Report native-frame-events/20260918T233200.559927Z/report.json:
SHA25659285dad8e4a3b3ce9c5f8cffc91203cc16c770b6319dc150f99cf5533ca7d94.

Actual Move is50 versus47frames; cancel30/31 versus29/29. Composition still
averages29.08–30.18scanlines. Independent phase6226 passes in233621.952499Z;
response-budget fails nine metrics,13 authentication checks passing. Reports:
native-phase-evidence/20260918T233630.715308Z/report.json and
response-budget/20260918T233631.090094Z/failed.json. This does not fix timing or
complete writer coverage. Do not promote this option.

## Exact current-OAM traversal candidate

Private connectedefd70a3d92d93d23291cee5d4d1d8f783c44fc16 uses
`fast_oam_plan=True`, independently of dirty tracking. Four exact native empty
entries are folded while preserving bank0 demand, owner checks and affine
words. Full planning avoids a redundant scalar tail scan; application already
skips unowned tags in groups. All current bytes are still checked.

Runner233442.448608Z: planner48449/build8/profile292 pass; entry fails paired
native shadow at ready. The later requested DMA phase step did NOT run after
that failure; it subsequently ran in233621.952499Z. Component evidence:
palette-plan/20260918T233443.112584Z/report.json. Profile:
compose-isolation/20260918T233457.591588Z/report.json totals15,091 instructions
versus17,928 in the retained matching default profile, roughly16% less work.

Fresh capture live-palette/battle/20260918T233457.836769Z feeds observation
233621.952499Z, passing5175. Trace:
native-frame-events/20260918T233622.626937Z/report.json,
SHA256b43fddc7fe2c2a415bd4ab7343c1f955ce507ae5a9f3d080d2e8c91d76c7cbd9.
Mean composition23.64–25.19scanlines, versus about2.8 without overlay. Move
starts25 versus24; durations46/47 versus47/47; cancel31/32 versus30/30.
Response gate fails seven metrics. Phase6226 passes. Runner233836.216751Z:
native-phase-evidence/20260918T233836.923343Z/report.json and
response-budget/20260918T233837.245122Z/failed.json. This measurable saving
still does not fix performance. No threshold was loosened. Independent phase
proofs do not silently pass original entry failures or their skipped assertions.

## Reproduction and next work

Evidence paths above are underbuild/art; runner timestamps underbuild/expansion/
test-runs have prefix20260918T. All enclosing runners are terminal. Use declared
`test-art-dma-cache-*` and `test-art-oam-plan-*` IDs. Immutable frame/phase/
response IDs pin actual candidates. `summarize-art-graphics-inputs.py` and
`summarize-art-frame-events.py` are read-only summaries, not runtime/acceptance.
No broad suite ran. All failures remain; no agents, art, launch or publication.

Avoiding pixel rescans alone has not removed the delay. Continue from measured
total compositor cost, including ownership/variant preparation and full OAM/
palette planning. Keep exact grouped-OAM savings as an optional input to a
substantive next change; do not repeat passed checks without changed behavior.
A queue-only cache cannot ship without complete writer/lifetime coverage.
Reuse applicable previous action/campaign/save evidence; E02–E05 still apply.
