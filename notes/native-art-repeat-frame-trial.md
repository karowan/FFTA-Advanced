# Repeated palette-demand trial: rejected for delivery

September18 Pacific; follows be19bff. E01–E05 remain open. Only final artwork
and authored animation frame content are deferred. Installed7507ca5c, default
palettefa3d12b4, immutable delivery indexes and player files remain unchanged.
All runs below are terminal. No art generation, agent, game launch or publication.

## Implementation and bounds

The private `repeat_frame=True` option is never enabled by default and cannot
publish a current player index. The latest candidate is
`183c641a3d5d13db97b66ccf891843f4bd04f289`, resolved privately through
`build/art/performance/repeat-frame/current.json`. It combines the earlier exact
ARM scans with928 bytes inside the existing12KiB reservation; live size12244,
28 bytes before the independent battle-menu root. No heap endpoint moves.

Unlike the first trial below, current source authenticates native ownership on
every composition. A normalized key includes custom class/native-bank identities,
native4bpp bank demands and all consumed8bpp geometry. Disabled objects have a
distinct key;4bpp position/animation tile changes do not change palette demand.
History mappings and the complete prior plan must match. Every consumed8bpp byte
is compared with the existing exact pixel cache, with no writer assumptions,
approximate hashes or pixel-cache overwrite. More than32 consumed tiles, missing
cache validity or cache alias mismatch falls back to full planning.

Current native colors are backed up and current displayed custom colors applied
on every hit. Native palette-DMA latching remains before lookup. Split histories
map newly authenticated class tags to history slots; identity mapping avoids a
redundant tag walk. A capture may reuse its tile-index list only after comparing
every8bpp geometry key; its bytes are revalidated after full planning. Heap reset
clears validity/counters. Rendering need not invalidate a producer epoch because
the current ownership and consumed inputs are reauthenticated instead.

The640-byte position-independent ARM probe uses scoped IWRAM above the native
resident-code fence, with40 bytes leaf stack and512 bytes interrupt reserve.
Post-wrapper SP must be03007210..03008000; deep/external stacks use the same ROM
leaf. Source is retained for reproduction, not accepted implementation selection.

## Trials and measured rejection

All private paths below are under build/art. All runner timestamps have prefix
20260919T. Three candidates were measured on their own fresh native captures;
no serialized actor state was loaded on a different ROM.

| Candidate | Reuse design | Move durations active/control, offsets0/4 | Cancel active/control |
|---|---|---|---|
|f90475f290d1f0d90313e6efac0b083d2a913076|Whole OAM plus render/reset invalidation|53/47,53/48|31/28,30/29|
|69856f6a63532baaf90ce508ce7af5cc8ca75a3a|Fresh ownership plus normalized demand|53/47,54/47|32/29,30/29|
|183c641a3d5d13db97b66ccf891843f4bd04f289|Identity-tag shortcut and unchanged-footprint reuse|48/47,49/46|30/28,32/28|

First trial: runner001544.599242Z passes component8428/build8;001717.599401Z
passes isolation4040/profile296/entry. Trace001918.816022Z passes5187 observer
checks, but only3–4 Move and13–15 cancel hits among127 transitions. Mean
composition30–33scanlines. Its entry passing does not accept performance.

Second trial: runner002445.387166Z passes component14250/build8/entry. Due to
plan ordering, its isolation/profile steps preceded the rebuild and still
tested f90475f2. Their coverage is not reassigned to69856f6a. Order was corrected.
Runner002620.725910Z then passes correct-candidate isolation4040/profile296 and
trace5187. Trace002622.092980Z has113 Move/116 cancel hits among127 transitions;
yet composition26–27scanlines and the timing above still fail. Source review
identified redundant full tag walks and repeated footprint construction.

Latest trial: runner002940.785889Z stops at a component expectation failure.
The fixture incorrectly required a disabled object's owner tag to affect demand.
The full planner ignores disabled objects. The corrected case explicitly compares
the full and reused outputs; this is not a waived engine failure. Later steps
were skipped in that failed run. Runner003036.221096Z passes:

- component14279: repeat-frame-contract/20260919T003036.931336Z/report.json.
  Every OAM attribute bit, every consumed pixel byte, history/plan changes,
  fresh colors/backups, caller ABI/stack/fences, full-planner equivalence for
  accepted mutations, clipped/flipped/mosaic/disabled footprints,33rd-tile
  fallback and high-history remapping are covered.
- build8: performance/repeat-frame/20260919T003040.167159Z/report.json;
  defaults reproducefa3d12b4 and existing source/delivery indexes are restored.
- isolation4040/profile296: compose-isolation/20260919T003052.519215Z/report.json
  and20260919T003052.844570Z/report.json. All seven native phases, fresh/skipped
  palette DMA and both stack alignments pass bounded write/output isolation.
  Profile cold23065/repeat9412 instructions; skipped-DMA22813/9160.
- Entry FAILS paired native shadow at ready; retained capture:
  live-palette/battle/20260919T003053.098031Z/failed.json. Later assertions skipped.

Initial latest trace003154.915809Z passes5187 observer checks. Its independent
repeat audit checked bytes of the recorded tile list but did not independently
prove that the list was complete. That limitation is retained. The strengthened
observer rebuilds the entire ordered footprint and native ownership from current
inputs and requires coverage fields on every fast entry. Corrected runner
003449.016885Z passes5203:
`native-frame-events/20260919T003449.711213Z/report.json`, SHA256
6ebe2fe3b64c1a7314e073d97da2030d32b4f503542e8e1df5794860abf8f456.
All1024 complete native states/framebuffers match ordinary emulation. The
timings are unchanged. This remains observer correctness, not acceptance.

Latest hot calls average20.1–20.8scanlines; misses38.3–41.1, peak62.78. There
are114 actual Move hits and117 cancel hits per128-frame window. Actual call
stacks are well above the scoped-code threshold, so deep-stack ROM fallback
does not explain the result. High hit rate does not solve the deadline cost.

## Hard VBlank failure and formal response gate

`test-art-repeat-v3-phase-evidence`, runner003542.308130Z, FAILS at
active/offset0/Move frame107. Composition starts at line164, returns227, and
native display return wraps to line0. Offset4/Move frame109 starts166 and
returns1/display2. Both cross VBlank; this is not merely a phase mismatch.
Report: native-phase-evidence/20260919T003543.016630Z/failed.json.
The response step was skipped after that failure.

Separate runner003613.250683Z executes `test-art-repeat-v3-response-budget`:
13 authentication/coverage checks pass, nine response metrics FAIL. Report:
response-budget/20260919T003613.899480Z/failed.json. Move starts+1 at offset0;
duration+1/+3, cancel+2/+4 at offsets0/4. No threshold or original failure was
relaxed. Candidate183c641a must not be installed or packaged.

## Next boundary

Do not continue generic whole-frame caching or accept average/instruction counts.
Both the hot path and rare misses still cost too much; misses now cross VBlank.
The simpler prior exact-scanner473a6938 remains unaccepted too, but avoids this
trial's new miss overhead and has passing bounded VBlank evidence. Prefer a
substantive reduction of unconditional composition work and maximum cost, using
the retained native scheduler/graphics observations. Any scheduling change needs
proof of input lifetimes across native uploads; queue-only invalidation remains
insufficient. Capacity, native action consumers and full-game final acceptance
are still required. No E gate is checked by this trial.
