# Generated color history before first appearance — September 18, 2026

Follow-up to `01bcf17`. Current private candidate
`af008a20544506ce12a7383c9af7b3095be67fb7` resolves through
`build/art/live-palette/poc.json`; stage157900 bytes, transient state8096 unchanged.
No package, launcher, player save or running-session change. Built-in imagegen
only; final sprite refinement remains deferred. G01–G04 remain open.

## Behavior

Supported effect setters now establish generated-color history before an actor
first emits OAM. Pretracking accepts only an exact authenticated normal or
native19/32 dim palette, only enabled custom classes and complete affected banks.
It uses empty existing slots, never invents a starting palette and never evicts
another history. It writes no OAM or hardware palette by itself.

Each tracked palette then follows the same native task, callback and integer
interpolation as an already visible character. A later first appearance reuses
that history, including after the effect completes. Temporarily absent active
or completed transformed bindings are protected from slot reassignment. Baseline
history is disposable; unknown prehistory and exhausted capacity remain explicit
appearance failures. Ten slots do not establish all-class maximum capacity.

The saved displayed-color phase now follows native palette DMA even when no
custom actor emits OAM; skipped DMA preserves the prior phase. New nonidentity
slots receive the source class's baseline immediately, before any tick or DMA.
This avoids inheriting another class's reset colors from the slot number.

## Evidence

Final runner `20260918T085706.102667Z`, currentaf008:

| Test ID | Checks | Coverage |
| --- | --- | --- |
| test-native-art-late-entry |2426|ARMv4T installed black/white/gray/tint/RGB/solid/explicit-restore setters, exact original-engine generated/native continuation, normal/dim, appearance at0/3/17 callbacks, both stack alignments, history retention, bounded ten-slot capacity/eleventh refusal, unknown prehistory rejection, alternate-slot initial latch and absent fresh/skipped DMA. |
| test-live-art-palette-late-entry |727|Actual mGBA callbacks and hardware after controlled native draw-enable hide/reveal, black/RGB effects active/completed before first ownership, paired native/unowned colors and canonical units. |
| test-live-art-palette-native |1140|Byte-exact rebuild and existing authenticated native installation/reservation checks. |

Final reports:
`build/art/late-entry/20260918T085713.920191Z/report.json`,
`build/art/live-palette/fades/20260918T085706.775650Z/report.json`, and
`build/art/live-palette/native/20260918T085717.042694Z/report.json`.

Live first-appearance procedure authenticates the original21754 draw gate,
clears only actor flag0x40, waits for both queued OAM buffers to leave hardware,
and calls the owned-state initializer on a paused clone. It transfers only the
verified private reservation. It starts the installed native effect with the
existing clone-input guard, waits while drawing is disabled, then restores0x40.
Actual callbacks, composition and hardware display execute in mGBA. This is a
controlled lifetime experiment, not a naturally triggered campaign scene change.

Prior candidate74c07bac7f6a39585c5c29c0b57aa598dc671288 has applicable direct
regression evidence in runner `20260918T085453.306367Z`:
component color operations6344, live color operations791, live reload699,
actual deployment variants587 (including65 consecutive normal/dim observations).
The latter reports are respectively under color-operations/20260918T085530.650043Z,
live-palette/fades/20260918T085523.301131Z, fades/20260918T085516.519950Z and
live-palette/battle/20260918T085457.137049Z. Their behavior is unchanged by the
final alternate-slot baseline initialization. Compiled variant contract23 and
native rebuild1140 also passed in runner20260918T084948.784675Z. Reuse this
evidence within its scope; no broad regression was justified.

## Retained failure and review correction

The first live run, runner20260918T085203.063714Z, failed the old assertion that
Dark Knight always used binding slot1. Its exact retained state instead had
normal class/bank key16 in slot0 and earlier pretracked key20 in slot1, active
mask4, tags0/255, counters3/3/0 and all four refusal counters0. This was a test
identity assumption, not a hidden pass. Failed artifacts remain at
`build/art/live-palette/fades/20260918T085203.725733Z/`.

Fade and battle observation helpers now resolve the recorded class/bank identity
and per-object tag. Effect counters are compared against captured startup counts
because naturally occurring effects can now be tracked before the tested menu.
The corrected live run passed727 on74c07 in20260918T085308.323477Z.
Its first RGB-active screenshot was visually inspected; the draft remains
unaccepted artwork. Review then found the alternate-slot initial-latch case,
fixed in af008 and covered by the final new assertions and actual playback.

Remaining: arbitrary unknown/partial prior palettes, unsupported native effects
and copy mechanisms, all-class/mixed-variant capacity, naturally triggered scene
transitions and heap/stack lifetimes, all remaining assets, phase/response gates,
final art and reproducible playable packaging. Previous battle timing/phase
failures remain open; this turn did not repeat or waive them.
