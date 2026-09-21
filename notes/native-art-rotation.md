# Native rotation and literal color cycling

September18,2026; follows `4de6d4c`. Private candidate
`21f24d6f69d5864d28366ee1a515e72b84e2cf59` resolves via
`build/art/live-palette/poc.json`. Stage161196/state8096 bytes. No new persistent
state, save fields, package, launcher or player-session changes. Built-in imagegen
assets remain technical drafts; final artwork is deferred.

## Reachability changes the next action

`scripts/audit-native-art-effect-reachability.py` authenticates the source ROM and
scans all halfwords for Thumb BL targets and all bytes for exact32-bit addresses.
Report: `build/art/effect-reachability/20260918T094552.876905Z/report.json`.

| Native routine | Observed direct callers |
| --- | --- |
| Palette initialization1479DC | Boot00029E |
| Palette heap destruction147A2C | None |
| Rotation wrapper147FD8 | 01D458,01D468,0D41F2 |
| Literal cycling wrapper148034 | 0D4214 |
| Stream wrapper148084 | None |
| Frame-table wrapper1480C4 | None |

No exact stored pointers to those functions or their four constructors were
found. Constructors146FB8/147068/147124/1471E0 have only their respective wrapper
callers. Original dispatcher147288 indexes table089A5CF8 by task type:
1->148740,2->146864,4->146BB0,8->146C8C,16->146D38.

Disassembly confirms the two01D4xx rotation calls use background color ranges
A2..A8 and A9..AF. Script interpreter0D41xx supplies dynamic color ranges for
rotation and literal cycling. Those active consumers justify the two callbacks
implemented here. Initialization currently needs no extra hook: the actual boot
fixture already starts with cleared transient art state. Heap destruction and
the two unreferenced wrappers are lower priority pending concrete consumers.
This is a conservative static audit, **not proof of dynamic unreachability**;
computed addresses or unobserved runtime paths are still possible.

## Implementation

Authenticated hooks at146864 and146BB0 preserve their complete displaced
instructions, original task/heap operations, return continuation and register ABI.
Before the first callback, exact native palette references establish generated
history for the affected bank even when the character has not appeared yet.

Type2 rotates current colors plus fade targets, channel errors and deltas. This
allows it to run concurrently with a type1 fade, as the original constructor's
cancellation mask permits. The wrapper follows the real countdown and step-count
byte, preserving both directions and partial ranges. Type4 shifts current colors
and inserts the literal table value. Its original constructor cancels overlapping
fades; interpolation targets/errors are not shifted for this effect. Neither
effect invents fade-start/completion counts. Display colors still latch at the
native DMA boundary.

Supported rotations are contained within one16-color native bank; partial ranges
inside that bank work. A cross-bank operation preserves native execution but
explicitly increments the unsupported count for each overlapping generated
binding. It must not silently reinterpret another bank's color identity. This
remains an open support boundary, not a completed generic palette pipeline.

## Reproduction and evidence

Build with `scripts/build-live-art-palette.py`. Run the declared IDs through
`Test Expansion.ps1 -Plan scripts/native-art-test-plan.json -Only ...`, announcing
the exact IDs/purpose first. Do not edit inputs while a runner is live.

| Runner | Test ID | Checks | Private report under build/art |
| --- | --- | ---: | --- |
| 20260918T093748.589579Z | test-native-art-rotation | 38146 | rotation/20260918T093749.240791Z/report.json |
| 20260918T094440.098899Z | test-live-art-rotation | 1297 | live-palette/fades/20260918T094440.781162Z/report.json |
| 20260918T094440.098899Z | test-live-art-palette-native | 1153 | live-palette/native/20260918T094448.077354Z/report.json |
| 20260918T094440.098899Z | test-native-art-palette-binding | 32 | See runner's003 log and linked report |

The ARMv4T component executes original constructors and the actual147288
dispatcher, comparing complete native effect state and an independent original
engine with generated colors as input. It covers both directions, delays1/3,
step counts1/3, normal-source palettes in banks0/9, both stack alignments,
partial/full bank ranges, initial discovery and concurrent fades. Target
permutation and later interpolation are checked; cross-bank ambiguity is a
declared refusal. It uses the retained authenticated075021 battle fixture.

The live test uses controlled constructors on a paused clone, guarded against
changes outside native palette/effect state and the art reservation. Clone stack
arguments remain isolated. Actual mGBA dispatcher/DMA playback covers both
directions, partial/full ranges, delay2/step3, two concurrent white fades and
literal cycling from an immutable original ROM table. Every owned hardware
sample agrees with the independent oracle at a matching native phase; unowned
colors and units match the paired original build. Final baseline restoration
finishes with three starts/completions and zero refusals. The source save remains
unchanged. The native check rebuilt byte-exact and authenticated both new hooks.

Visually inspected `candidate-rotation-rotate11-8.png`; the deliberate rotating
white fade is present with unchanged native menu lettering. This does not accept
the draft character's aesthetics. No failed run occurred in this batch. Prior
cancellation, table-color, late-entry and reload evidence remains applicable.
No broad suite was justified.

## Remaining acceptance

Prioritize naturally triggered palette/script consumers and lifecycle transitions,
maximum mixed-class capacity, cross-bank mapping and the retained battle
timing/response failure. Require a concrete reachable caller before implementing
unreferenced teardown/stream/frame helpers. Other native asset consumers, all
class artwork, final visual approval and reproducible packaging remain open.
All G01–G04 gates remain open; this is technical integration progress only.
