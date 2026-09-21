# Native scheduling and input-arrival experiment — September 18

Follow-up to fb3889c. Production source and current connected candidate
`d9acd7234186a77561a2fb4ee91fdae2197c197d` are unchanged. This is a bounded
diagnostic checkpoint, not timing acceptance or a completed graphics release.
Built-in imagegen only; final sprite refinement remains deferred.

## Evidence

Declared `test-art-scheduler-phase` passes109 checks in terminal runner
`20260918T181759.118342Z`. Report:
`build/art/scheduler-phase/20260918T181759.744247Z/report.json`, SHA256
`00aaadc2664514551401fd1e01aa745381e5da4955bb29526ecaa67fac70e8ed`.

It starts each of12 cases from the exact authenticated mixed-battle ready
capture `20260918T171708.832178Z`, ROM7b966543. Initial RAM/IWRAM and the CPU
wait point0800042A must match. All serialized actor pointers belong to that ROM.
The current d9acd723 ROM is authenticated separately: its sole difference is
the US keyboard allocation byte12A15E, C6→42. No cross-ROM state is loaded.

Each pair uses identical existing navigation and eight-frame A/B presses,
with600 subsequent video-frame observations per action. The only input
variation is0..5 extra zero-input frames immediately before Move. A private
control restores only the eight original bytes at compositor entry080012BC.
It intentionally lacks custom palette composition and is not a delivery ROM.

| Extra idle frames | Active Move start/end/duration | Bypass Move start/end/duration | Active/bypass cancel start |
| ---: | --- | --- | --- |
|0|16 /63 /47|15 /62 /47|27 /22|
|1|16 /64 /48|15 /62 /47|26 /23|
|2|16 /64 /48|15 /62 /47|25 /23|
|3|16 /64 /48|15 /61 /46|25 /23|
|4|16 /64 /48|16 /62 /46|24 /23|
|5|16 /66 /50|15 /61 /46|24 /22|

All12 cases traverse the same ordered logical positions, reach the same final
Move/cancel coordinates and preserve canonical roster/inventory/AP bytes.
Absolute native color-phase sequences vary even within the unchanged bypass
control (five distinct Move traces and four cancel traces). This establishes
an input-arrival contribution; it does not attribute every earlier mismatch
to scheduling or authorize normalizing failed comparisons into passes.

The custom compositor still has a measurable cost across these offsets:
0..4 additional moving frames and1..5 additional cancel-response frames.
Its sampled03000E10 flag is nonzero78..80 times during Move, versus26 for the
control. These are frame-boundary observations, not a count of executed DMA
skips or proof of a particular interrupt overrun. Per-frame input words,
native frame counter, cycle head/colors, positions and palette profile remain
in the report. No threshold was weakened and the timing gate remains open.

The historical report's `controlPatch` field contains the builder's original
installation record (original→hook); the actual control operation was its
reverse. The script now writes before=hook, after=original and prints compact
timing summaries. These are reporting-only corrections after the completed
run, not replayed runtime evidence. The original immutable report is retained.

## Native control-flow review

Static Thumb disassembly of the authenticated current ROM agrees with the
earlier `native-palette-composition-cost.md` leads:

- Foreground080003A2 tests byte03000EA9. The interrupt-enabled path waits at
 080003D4 on03000E10 before the03F0 clear/update/draw path. The alternate path
 clears03000E10 at040C..0416 and waits at0418..0428 before calling0460.
- Draw08000460 resets/prepares object buffers, dispatches080069F4 with context
 03000E10 and mode3, toggles main/UI write banks through01CD0/01CE0, reads
 KEYINPUT and calls native input polling0800221C.
- VBlank080004B0 invokes begin006D0, queued DMA007C8 and scheduler groups0438.
 It conditionally calls00718/147A44 when03000E10 is zero, always composes at
 012BC, runs end00788, conditionally calls147288, then sets03000E10 to1.
- Dispatcher080069F4 distinguishes ordinary index traversal from callback
 selection/disabled states in context byte+5. A sampled03000E10 value alone
 is insufficient to infer all callbacks or foreground progress.

This review identifies where to measure; no native scheduler, input cadence,
DMA ordering or palette callback has been changed. Moving preparation before
VBlank would require proof that its OAM, VRAM, ownership and palette inputs are
still valid after intervening native writes; existing queue hooks alone do not
cover direct CpuSet uploads. Do not implement speculative stale-frame reuse.

## Heap evidence and next concrete work

Read-only parsing of the20 authenticated water/land endpoint RAM files pinned
in `native-art-all-class-water-evidence.json` finds the same heap topology in
every capture:11 blocks,54,632 free bytes,41,640 largest block, end0203C000.
This agrees with the mixed battle before Status. Those are the same12-actor
encounter shell on original map92; they do not add larger-encounter acceptance.
No water playback was repeated.

The live Status constructor still leaves1,068 free bytes after its native
children allocate. Its context grows7280→9980 solely for the full2700-byte
list tail. Native mode1 uses a2800-byte secondary buffer; mode0 uses3800.
The original list region4340..5AC0 is smaller than the full460-item list.
Do not shrink or reuse it without proving which lists battle Status can reach.

Next bounded memory investigation: trace the read-only battle Status page/list
consumers separately from editable world party/inventory and Auto-Potion.
Determine whether the large item-list tail can be restricted to editable
contexts, while preserving the native AP/status/job-copy tail and all list
bounds. Prove reachability and ownership before adding such a mode-dependent
allocation. Existing passing world460-row/preference/UI evidence is reusable
only where those paths remain unchanged. Larger battle/effect capacity,
remaining natural consumers, assembled acceptance and delivery remain open.

No package, installed preview, player save, running game or publication changed.
No new council/agent or broad integration suite was used. G01-G04 remain open.
