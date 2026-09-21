# Native color operations and compositor isolation — September 18, 2026

Follow-up to `0f2bda3`. Current private candidate is
`6fa4fd9c048583f3eae27d5b6b45f0c9b7ec93df`, resolved through
`build/art/live-palette/poc.json`. ROM stage157052 bytes; transient state remains
8096 bytes in the existing8KiB reservation. The status shortcut is preserved.
No player, package, launcher or running-session change. Built-in imagegen only;
final sprite refinement remains deferred. All G gates remain open.

## Four previously unsupported native targets now follow generated colors

The custom palette now follows these original setters:

| Native entry | Operation | Generated target |
| --- | --- | --- |
| 08147B28 | Weighted grayscale | Original pure routine081477DC on each current generated color. |
| 08147BA4 | Preset tint | Original081483EC with native coefficients294,273,204. |
| 08147C2C | Six-argument RGB multiplier | Original081483EC with all three caller coefficients. |
| 08147CC0 | Six-argument solid color | Exact native16-bit channel packing. |

Targets start from the current generated fade colors, so a new operation can
interrupt an existing fade correctly. The established native-progress binding
then supplies the original integer interpolation and completion behavior.
Native palette shadows and effect tasks still come from the original functions.
All argument truncation follows the original setters. No new RAM, palette slot,
save field or job ID was added.

The six-argument entry veneers preserve r3 and the two caller-stack arguments.
Their trampolines reproduce every displaced prologue instruction and continue at
147C3D/147CD1. Three-argument grayscale/tint preserve their original high-register
prologues. Builder assertions authenticate all displaced bytes against the
pinned parent. `art-palette-binding.c` uses the game routines directly instead
of approximating their color arithmetic.

Partial banks and durations above255 remain explicitly unsupported for custom
bindings. Unknown direct setup and unmatched explicit table targets are also
still reported. Supporting these four setters does not accept every native
color operation, reload, late entry or scene lifetime.

## Current candidate evidence

All runtime work used declared IDs and `Test Expansion.ps1`, with each purpose
announced before execution. No broad integration or campaign replay ran.

| ID | Runner | Checks | Report |
| --- | --- | ---: | --- |
| test-live-art-palette-native | 20260918T080851.487275Z | 1139 | build/art/live-palette/native/20260918T080852.097329Z/report.json |
| test-native-art-color-operations | 20260918T080851.487275Z | 6344 | build/art/color-operations/20260918T080854.695312Z/report.json |
| test-live-art-color-operations | 20260918T081113.949907Z | 782 | build/art/live-palette/fades/20260918T081114.564879Z/report.json |
| test-native-art-palette-binding | 20260918T081225.244450Z | 32 | build/art/palette-binding/20260918T081225.872254Z/report.json |

The component comparison executes each installed setter against the original
setter using identical retained input. A separate original-engine machine uses
generated colors as its native palette, independently producing exact custom
targets and every callback phase. Cases include both stack alignments,
durations0/1/8/17, black-fade interruption, coefficient/channel truncation and
limits, unowned ranges, partial-bank refusal and duration256 refusal. Complete
native palette/effect state, all generated target/tick colors, other owners and
EWRAM outside the reserved pages are checked.

The live sequence runs grayscale, baseline restore, preset tint, RGB multipliers,
solid color, interrupted RGB fade, grayscale interruption and final restoration.
It installs actual native setter inputs on paused-state clones and transfers
only authenticated native effect/private binding regions. The game then runs
its callbacks and palette DMA. Every sampled generated hardware color matches
the same native visible fade phase; every unowned hardware color and canonical
unit record matches the parent. Eight starts, seven completions, one interruption,
zero unsupported operations and exact generated baseline restoration are proven.
Screens `candidate-gray-11.png` and `candidate-restore-again-11.png` were visually
inspected: the character turns grayscale and returns to its prior colors. This
is technical effect review of an unaccepted draft, not final sprite acceptance.

The old binding test incorrectly required an obsolete menu capture's ROM hash
to equal every new candidate. It now uses the authenticated29453 ready state;
its source report failed phase equality, and is never relabeled as accepted.
The input has valid current-layout idle bindings. Grayscale is no longer the
unknown-operation example; direct unrecognized setup tests that boundary.
Partial/unowned/table target/fourth argument/task-address controls all pass.

## Identical-input compositor isolation on prior29453

`test-native-art-compose-isolation`, runner `20260918T080356.679697Z`, passes3900.
Report: `build/art/compose-isolation/20260918T080357.278422Z/report.json`.
It pins the prior29453 ROM and existing ready RAM/IWRAM/VRAM/palette/OAM hashes.
The control restores only the original eight-byte compositor entry. Both
machines receive exactly the same captured inputs and authenticated prior-overlay
restoration. Native08146864 derives all seven BG color phases. Fresh and skipped
palette DMA inputs and both stack alignments are exercised.

The actual installed compositor and original native compositor issue identical
DMA0 transfers. All unowned hardware colors and OAM bytes are exact; owned OAM
changes only palette selection and receives exact generated colors. Native
shadow, complete VRAM, IWRAM below call scratch and all EWRAM outside the owned
reservation remain exact. The DMA0 model is synchronous at the four original
completion sites already used by the ownership component test.

This distinguishes bounded compositor writes from palette-phase arrival, but
does not prove real VBlank timing or unchanged scheduler phase. The failed full
battle and response comparisons in `notes/native-status-iterator-cost.md` remain
failed. Do not normalize their phases or claim this component proves all scenes.
The3900-check report belongs to29453; this turn did not replay it merely because
the new unrelated setter hooks changed the ROM hash.

## Retained failures and next work

- Runner `20260918T080313.236428Z`: phase enumeration stopped after30 callback
  calls and observed only five phases. Native cadence is eight calls; extending
  the bounded observation to64 covers the complete seven-phase set. No ROM fix.
- Runner `20260918T081033.295197Z`: live baseline RGB setter failed the clone
  memory guard because its fifth/sixth input arguments at STACK..STACK+8 were
  omitted. The guard now requires exactly those supplied bytes, rather than
  allowing arbitrary writes; neither stack arguments nor clone scratch are
  transferred to the live game. Failure and captured baseline state remain.

Next handle authenticated palette reloads and late appearance during an active
effect, then remaining color operations and native scene/heap/stack/asset
consumers. Preserve the measured status improvement. Remaining response cost
and full-route palette-phase comparison still need their own evidence. Reuse
unchanged planner/ownership/variant and prior fade coverage; final assembled
acceptance, packaging and production artwork remain unfinished.
