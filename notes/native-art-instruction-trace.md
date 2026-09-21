# Native instruction observation — September 18, 2026

Follow-up to `87cc1d4`. The new host observer is verified against ordinary
emulation on 1,024 complete Move/cancel frames, without modifying the emulated
CPU, ROM or game memory. It establishes a reusable diagnostic, **not a timing
fix or expansion acceptance**. Current connected `4a7d55ce09cd4a40965a0bb97de2701d276789c5`
and palette `5eff9a7044165dd639d47163b44e8f315a722ddd` are unchanged. The installed
preview, player saves and session are unchanged. Built-in imagegen only; final
sprite refinement remains deferred. G01–G04 stay open.

## Observer and provenance

`scripts/mgba_instruction_trace.py` fails closed against the private core DLL
SHA256 `b7008c1a834fef42c9c2b66594855f63924d419fb33af2863e86b1a032d03560`
(`0.11-219-e31759b`). Host offsets are authenticated by its x64 machine code,
not assumed from the separate desktop mGBA version. Relevant upstream source:
[ARM execution](https://raw.githubusercontent.com/mgba-emu/mgba/e31759b/src/arm/arm.c),
[core interface](https://raw.githubusercontent.com/mgba-emu/mgba/e31759b/include/mgba/core/core.h),
[GBA core](https://raw.githubusercontent.com/mgba-emu/mgba/e31759b/src/gba/core.c),
[ARM layout](https://raw.githubusercontent.com/mgba-emu/mgba/e31759b/include/mgba/internal/arm/arm.h).
The inspected source copies are private under `tools/mgba-trace-source/e31759b/`.

The normal native runFrame/ARMRunLoop/event loop remains active. A private copy
of the 1,024-entry host Thumb handler table intercepts only opcode groups that
contain requested ROM addresses. Each callback observes the matching PC before
its instruction, then always calls the original native handler. No executable
instruction is patched. The eight-byte host table reference is temporarily
writable for replacement/restoration; original table entries are never changed.
Context exit restores the reference and checks the original table. It also
reports callback errors after restoration. This is specific to the pinned DLL,
not a general debugger ABI or a claim about every emulator build.

Authenticated RVAs: `retro_run=BF600`; core reference `2C8830`; mCore CPU/timing
pointers at `+0/+10`; runFrame slot `+500`; native saveState `+528`; frameCounter
`+560`. Native state is 397,312 bytes. ARMRunLoop reads the table reference at
`2A7530`, indexes by `opcode >> 6`, and dispatches through it. Thumb observation
PC is the already-advanced register15 minus4. CPU registers are checked against
the existing libretro serializer. Time is wrap-safe master32 plus relative CPU
cycles; do not rely on debugger-only global time. Frame length is280,896 cycles.

Observed game sites include input `0800221C`, foreground drawing `08000460`,
dispatcher `080069F4`, VBlank `080004B0`, composition `080012BC` and return
`080004DC`, native DMA decision `080004C8`, and foreground clear/return. Records
retain cycles, scanline, video/native frame, CPU registers, native flag and input
bytes. No busy-wait loop is logged per instruction.

## Evidence and retained failures

All runtime checks used the declared native-art plan through `Test Expansion.ps1`.
Every ID/purpose was announced. All runners below are terminal; dates20260918.

| Check / runner | Private child directory under build/art | Result |
| --- | --- | --- |
| step equivalence /191923.604791Z |instruction-trace/20260918T191924.261490Z|**Failed**: rejected single-step replacement crossed an extra IRQ boundary;39 native-state bytes differed in frame0.|
| dispatch equivalence /192335.645085Z |instruction-trace/20260918T192336.288696Z|40 checks,166 events;16 complete states/framebuffers equal, including held A.|
| native events /193028.111727Z |native-frame-events/20260918T193028.719910Z|**Failed**: action frame0 mismatch after mid-scene snapshot restoration.|
| restore diagnostic /193116.780270Z |native-frame-events/20260918T193117.484317Z|**Failed before observation**:12 serialized audio-state bytes changed when restoring the new action snapshot.|
| same-core replay /193203.300447Z |native-frame-events/20260918T193204.006916Z|**Failed before observation**: replay from retained seed in the advanced core still differed at150–151.|
| fresh-core native events /193254.895149Z |native-frame-events/20260918T193255.614632Z|1,069 checks;1,024 entire native states and complete framebuffers equal to ordinary execution.|

The rejected step implementation and mismatch states remain in the first private
directory. `ARMRun` services pending events differently from `ARMRunLoop`; the
replacement cannot be used for timing evidence. The later failures concern
restoration/replay before observation. Offset150 belongs to channel2's update
timestamp in the [native state layout](https://raw.githubusercontent.com/mgba-emu/mgba/e31759b/include/mgba/internal/gba/serialize.h).
Both successful action branches start in fresh cores, restore the same retained
seed and replay identical navigation. Their entire action-start native states
must match, and every subsequent state/frame must match. No bytes are masked,
normalized or waived. This bounds the observed equivalence to these scenarios;
it is not audio playback acceptance or a claim about arbitrary save restoration.

The current exact-ROM seed is `live-palette/battle/20260918T183919.610099Z`.
State/RAM/IWRAM SHA256 pins are in the test. Navigation remains four eight-frame
presses (A,Right,Right,Right), each followed by180 idle frames. Move and cancel
each hold their key8 frames then idle120. Extra pre-Move idle is0 or4, selected
from previously measured timing-sensitive offsets. The paired private control
restores only the original eight bytes at12BC; it omits custom composition and
is not a playable candidate. Canonical roster/inventory/AP and ordered logical
movement match. No new deployment fixture, player save or broad suite is used.
The successful raw report's `controlPatch` field contains the builder's original
hook record; the actual control restores its `before` bytes. The script now
reports that inverse restoration direction explicitly. This reporting-only
correction does not require replaying the accepted observation.

## What the trace establishes

Frames below start at zero with the first held-input video frame, **including
the eight press frames**. Earlier scheduler reports start after that press, and
used600 idle frames between actions; do not compare their absolute cancel
numbers as if the inputs were identical.

| Extra idle | Active Move start/end/duration | Bypass Move | Active/bypass cancel return |
| ---: | --- | --- | --- |
|0|24 /71 /47|23 /70 /47|32 /28|
|4|24 /72 /48|24 /70 /46|33 /28|

The first pressed input reaches the native poll within frame0 in every case
(active0.673–0.937 frame; bypass0.476–0.715). Thus these eight-frame inputs are
not lost or held outside the game for the entire response interval. This does
not establish single-frame tap behavior or every arrival phase.

Composition runs all128 observed frames per action. Its mean duration is
28.21–29.75 scanlines active versus2.756–2.793 bypass; active maximum49.33.
The active runs complete113 input polls during Move and103/105 during cancel,
versus117 and112 in the controls. Native palette-DMA skips are15 during Move and
23/25 during cancel, versus10/11 and16/17. The longest cancel inter-poll gap is
10.275/10.672 frames active versus8.911/9.114 bypass. Native foreground work
already spans interrupts in the control; custom composition consumes additional
time at each interrupt. The exact control supports a scheduling-cost explanation,
not a missing-input explanation. It does not isolate every contributing native
subroutine or make phase-dependent color differences acceptable.

Reproduce this summary without executing a game:

```powershell
python scripts/summarize-art-frame-events.py build/art/native-frame-events/20260918T193255.614632Z/report.json
```

## Next implementation boundary

Do not skip custom composition simply because native palette DMA was skipped:
the native compositor still rewrites OAM, and the earlier attempt caused flicker.
Do not move work outside VBlank without proving its input lifetimes. Investigate
reusing a previously validated mixed-class plan only when its actual OAM,
ownership, visible8bpp tile bytes, mapping mode and history-slot inputs are
unchanged. A candidate must still reapply the correct displayed palette phase
and preserve native backup/restore. Bound any cache inside existing reserved
memory; do not take back the repaired battle Status headroom. This is a proposed
next step, not an implemented or proven optimization.

Use the observer with exact candidate states to measure foreground progress and
response after such a substantial change. Reuse existing Status/world-menu and
other passing evidence where inputs remain applicable. Remaining gates include
timing/phase acceptance, larger encounter/effect capacity, remaining natural
graphics consumers, final assembled checks and reproducible playable delivery.
