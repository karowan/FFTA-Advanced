# Scoped ARM copy costs and unrolled-copy trial

September18 local / September19 UTC. Full engineering remains required; only
artwork content is deferred. E01-E05 remain open. Private unrolled candidate
`0cca349466176f5abeac12b5ab28292cc45e9b95` is not accepted or installed.
Action5a14e6c7, defaultfa3d12b4 and installed7507ca5c are unchanged. All runners
are terminal. No player-save changes, launches, agents or publication.

## Root-cause refinement

The established regression is added per-interrupt composition work reducing
native foreground time, not lost held inputs. It is not proven unsolvable.
The previous inclusive profiler could not separate ARM copy from execution.
`scripts/art_scoped_costs.py` now authenticates every byte of the standard
144-byte wrapper and each leaf hash, then observes unconditional ARM boundary
instructions through a private host dispatch table. The ROM and emulated CPU,
memory and timing are unchanged. Native conditional-instruction failures do not
reach this table; these sites deliberately use unconditional instructions only.

Pinned core DLL remainsb7008c1a834fef42c9c2b66594855f63924d419fb33af2863e86b1a032d03560.
Its ARMRunLoop reads table reference RVA2A7470 at35CC0 and indexes the4096-entry
table by `((opcode >> 16) & 0xff0) | ((opcode >> 4) & 15)` before35CF7's call.
ARM observation PC is register15 minus8. Host code, table pointer and all handler
ranges are checked. Original handlers execute exactly once, and context exit
restores both ARM and Thumb tables. The local pinned source under
`tools/mgba-trace-source/e31759b/src/arm/arm.c` corroborates this dispatch.

`test-art-scoped-copy-costs`, runner20260919T041240.651620Z, passes31227 checks.
Report: `build/art/native-frame-events/20260919T041241.334001Z/report.json`.
SHA256: `9afa9c422a2f7aba6ec15e1eaaa1acd37fbdcb43d73344b6580703ad7777dd89`.
It reuses e1a87ecd's retained ready state013433.783581Z, both fixed arrival
offsets and both active/bypass branches. All1024 complete state/frame pairs
match ordinary execution. Every actual copied execution target matches the
entire ROM leaf, with exact stack, return address and copied size. Each active
action has128 owner and128 publication copies/executions. No ROM fallback is
exercised in these scenarios; shared return-only arrivals are explicitly excluded.
The observer currently supports standard looped ARM wrappers only, not the new
unrolled layout or compact Thumb variant.

Mean scanlines at offset0 (1232 GBA cycles per line):

| Routine / phase | Move | Cancel |
| --- | ---: | ---: |
| Fused owners: allocation/copy |1.8353|1.8338|
| Fused owners: actual leaf branch through return |2.5566|2.6899|
| Publish: allocation/copy |0.6799|0.6793|
| Publish: actual leaf branch through return |1.5506|1.5441|

Offset4 is similar. These phases are nested within the older inclusive wrapper
measurements; never add them twice. About2.51 lines per interrupt copy1136 bytes
of executable code (832+304), before useful leaf execution.

## Implementation and bounded correctness

Optional `unrolled_copy=True` / `--unrolled-copy` replaces the ROM copy loop with
exactly size/16 adjacent LDM/STM pairs. This removes branch/refill and counter
work. It uses the same scratch registers, saved registers, temporary allocation,
512-byte interrupt reserve, minimum stack checks and ROM fallback. No persistent
code cache or writer-lifetime assumption is introduced. Compiled leaf bytes,
stack sizes, minimum SP and SHA256 metadata match the previous scalar leaves.
The wrapper code grows1080 bytes in the existing ROM reservation (stage252152).
The state remains11316 bytes in the existing12KiB reservation.

The option requires private fused ARM composition and rejects compact leaves.
The connected build includes the mandatory final action-completion stage (six
Moogle land descriptors). The isolated selector is
`build/art/performance/unrolled-copy/current.json`; existing selectors are restored.
Default installed-palette rebuild remains byte-exact. This does not claim a
clean final release rebuild or all gameplay acceptance for this private trial.

All following IDs used the declared native-art plan through Test Expansion.ps1:

| Runner20260919T | Test/result | Child report under build/art |
| --- | --- | --- |
|041448.046326Z|unrolled-owners17068 pass|palette-owners/20260919T041448.746435Z/report.json|
|same|unrolled-plan488 pass|frame-high-slots/20260919T041450.842016Z/report.json|
|same|unrolled-build8 pass|performance/unrolled-copy/20260919T041451.687823Z/report.json|
|same|unrolled-consumers launch failed; entry skipped|test plan mistakenly named a nonexistent script; log retained|
|041534.626039Z|corrected unrolled-consumers244 pass|fused-consumers/20260919T041535.366443Z/report.json|
|same|unrolled-entry fails raw paired ready palette-shadow equality|live-palette/battle/20260919T041536.241917Z/failed.json|
|041629.517268Z|unrolled-frame-events31105 pass|native-frame-events/20260919T041630.187456Z/report.json|
|041729.440986Z|unrolled-phase-evidence6226 pass|native-phase-evidence/20260919T041730.320158Z/report.json|
|same|unrolled-response-budget six metrics fail|response-budget/20260919T041730.792383Z/failed.json|

Full IDs use `test-art-` prefix. Ownership tests include native producer counter
matrix, actual output equivalence, both alignments and deep/external fallback.
High-slot tests cover20 histories, exhaustion, clipped/affine/mosaic/invalid
8bpp objects, native resident-memory fences and actual scoped/fallback execution.
Some malformed-counter tests exercise the previous generic/native entries, not
all fused-entry negatives; retain that limitation. Complete consumer comparison
includes simultaneous same-class split histories and highlight fallback.
The entry script's later assertions remain skipped. Independent phase evidence
proves native rotation/DMA phase behavior in its recorded windows, not every
entry assertion or complete campaign correctness.

Trace SHA256:
`178925a3bbcb8bf0a81343de76ec435ca9a257082a2235f36c603a355672b125`.

| Offset | Action | Active start/end/duration | Same-ROM bypass |
| ---: | --- | --- | --- |
|0|Move|24/71/47|24/70/46|
|4|Move|25/72/47|24/71/47|
|0|Cancel|31/31/0|29/29/0|
|4|Cancel|30/30/0|30/30/0|

Mean compositor15.84/15.93 lines Move and14.70/14.65 cancel; peak31.04.
The prior looped means17.06/17.07 and15.82/15.66 were higher. At offset0,
owner wrapper falls4.51->3.75 lines on Move and4.64->3.88 cancel; publish falls
2.35->2.08 and2.34->2.07. These savings do not waive the six failing response
metrics. Ready-state onset phases differ, so absolute onset across candidates
is not a causal comparison; each response verdict uses its own same-ROM bypass.

## Next work

Copy cost is now measured and the safe unroll trial yields real cycle savings,
but copy optimization alone is insufficient. Do not promote it. Target actual
owner/publication execution or planner cost using the retained inclusive trace.
At offset0 plan_inputs is3.336 lines Move/2.106 cancel, with24/10 bank-span calls
(mean9.87/9.72 lines each). Remaining calls occur every frame. Preserve complete
current-input validation and avoid rejected prior-frame cache assumptions.
Continue other action/effect/UI, maximum-capacity and full-game/release gates;
no prior passing job implementation should be restarted.
