# Battle Status allocation — September 18, 2026

Follow-up to a2c8b5c. Current private connected ROM is
`4a7d55ce09cd4a40965a0bb97de2701d276789c5`, resolved through
`build/art/connected/current.json`. Palette parent is
`5eff9a7044165dd639d47163b44e8f315a722ddd`,
`build/art/live-palette/status-current.json`. Stage245932; palette state11312
and its0203C000..0203F000 reservation are unchanged. No playable package,
launcher, player save, running game or publication changed. G01-G04 stay open.
Built-in imagegen only; final sprite refinement remains deferred.

## Actual memory improvement

The read-only battle Status scene had inherited the full460-item inventory
list tail even though its two panels show equipment/abilities and inspection
help. This added0x2700 (9,984) bytes to an already large context. The native
context's original list area is at+0x4340, ending at+0x5AC0; the expansion
AP/status/job-copy tail ends at+0x7280 and must remain allocated.

Only the authenticated Status entry at08070688 marks a fresh borrowed battle
heap as read-only. Native context allocation at08071138 then requests0x7280
instead of0x9980. Pointer binding at080711CC selects context+0x4340 for that
owned lifetime; all other contexts retain+0x7280 and the full0x9980 allocation.
Mode1 alone is deliberately insufficient: world menus also use that mode.
Other native constructor callers at08070A74,08070CE8 and08070E30 retain their
full allocation. Their reachability and capacity remain follow-up coverage.

The existing16-byte ownership record gains no storage. Magic50485232 marks
the read-only lifetime, versus50485231 for the ordinary borrowed parent.
Both variants retain exact root/caller guards, constructor/destructor counts,
reset and parent retirement. A second parent claim is rejected. All existing
native child allocations and the AP/status/job-copy area remain intact.
The original native Status constructor, display, input, help and destructor
continue to execute. No font, art, player format or item capacity changed.

Actual mixed-battle heap measurements:

| Point | Free bytes | Largest free block |
| --- | ---: | ---: |
| Ready |54,632|41,640|
| Status open |11,052|8,776|
| Equipment help |11,052|8,776|
| Ability help |11,052|8,776|
| Returned to battle |54,632|41,640|

The previous Status allocation left1,068 free. The component test additionally
holds an8,192-byte allocation from the actual native allocator before entering
Status; the compact context still constructs with2,848 free bytes. Its held
payload and all preexisting allocations remain exact, and teardown restores
the original free-list topology. This is a controlled pressure case, not proof
of every larger encounter, effect or nested menu lifetime.
The retained component report's scope still says full-width list ownership;
its observations record the compact and pressure cases. Current source corrects
that reporting text without rerunning the unchanged behavior.

## Consumer investigation and retained harness errors

All investigation starts from exact7b966543 captures, never from stale actor
pointers loaded into a relocated ROM. Original code identifies the Status
scene070604, its scheduler03002730, and input callback0807F7B4. Equipment's
ordinary state is3 and inspection state19h; Abilities uses0Fh/1Bh. Help uses1Ch.
Right/Left switch the two panels; Select opens an inspection cursor; A opens
the selected help. A outside inspection closes Status. The large tail remains
all-zero in the inspected panel/help captures.

`test-art-status-pages` first reported59 checks in runner182740.099462Z,
child `build/art/status-pages/20260918T182740.731257Z/report.json`. Visual review
**rejects its claimed page/active-context evidence**: the shoulder button did
not switch panels and A exited. It checked a stale global pointer, not live
ownership. Retain that report and images; it does not justify an allocation
change. Corrected checks require the copy owner, borrowed-lifetime record and
allocated native block, plus directional page input.

- Corrected panel navigation:74 checks, runner182845.466402Z,
  `build/art/status-pages/20260918T182846.080513Z/report.json`.
- Select/cursor navigation:51 checks, runner183136.705131Z,
  `build/art/status-pages/20260918T183137.379119Z/report.json`.
- Both panels, six cursor positions and A-help:213 checks, runner183255.459126Z,
  `build/art/status-pages/20260918T183256.057498Z/report.json`.

The last report's historical scope text predates its12-case extension; its
input/capture records identify the actual cases. Current source emits the
correct scope text. This reporting-only correction did not rerun gameplay.
Images were inspected: two distinct panels, actual item help and class/body
graphics remain visible. Draft visuals are not production-art acceptance.

Initial compile `compile/20260918T183700.069817Z/compile.log` rejected low-register
Thumb `mov` instructions; corrected to ARM7TDMI `movs` before runtime.

Four live UI failures remain intact, all under `build/art/owned-menu/battle/`:

| Runner | Child directory | Actual reason |
| --- | --- | --- |
|184052.125859Z|20260918T184052.812394Z|Two B presses left the long equipment help's inspection cursor active; return anchor correctly failed.|
|184203.493841Z|20260918T184204.132116Z|Three fixed B presses were too many for shorter ability help and exited Status before the page-state check.|
|184311.992772Z|20260918T184312.734788Z|Bounded exit guard omitted native ability inspection state1Bh.|
|184357.002527Z|20260918T184357.696116Z|Guard assumed both ordinary panels use state3; Abilities actually uses0Fh.|

Original disassembly and earlier retained page snapshots confirm the distinct
states. The final test checks each panel before entering inspection, allows
only its exact cursor state or help1Ch, and presses B at most three times,
stopping when that panel's ordinary state returns. It does not accept arbitrary
states or retry until a screenshot happens to match. Final observed exit states
are[1Ch,1Ch,19h] then ordinary3, and[1Ch,1Bh,0Fh].

## Final verification

All dates below are20260918. Exact IDs and purposes were announced; every runner
is terminal. Tests used the declared native-art plan through Test Expansion.

| ID | Checks | Runner | Report/location |
| --- | ---: | --- | --- |
|test-art-compact-status-lifecycle|152|183730.049936Z|`build/art/owned-menu/shared-native/20260918T183730.681426Z/report.json`|
|test-art-compact-status-native|9814|same|`build/art/live-palette/native/20260918T183730.887186Z/report.json`|
|test-art-compact-status-mixed-entry|632|183918.953096Z|`build/art/live-palette/battle/20260918T183919.610099Z/observed.json`|
|test-art-owned-menu-bounds|80|same|`build/art/owned-menu/native/20260918T183938.511369Z/report.json`|
|test-art-owned-menu-preference-ui|24|same|Runner's003 log and candidate's`potion-menu-20260918T183938810375Z`|
|test-connected-art-equipment-ui|30|same|`build/art/generated-equipment/tests/20260918T183948.679762Z/report.json`|
|test-connected-art-native|3981|same|`build/art/connected/native/20260918T184004.316839Z/report.json`|
|test-art-compact-status-battle-ui|38|184454.013067Z|`build/art/owned-menu/battle/20260918T184454.647504Z/report.json`|

The final actual Status test starts from the fresh exact4a7d55ce battle capture.
It verifies the smaller allocated context, original in-context list, ownership,
both equipment/ability help panels, native teardown, restored actors/class
palettes and unchanged roster/inventory/AP. Root inspected Status, Item help
and the returned Move menu. World-mode allocation/full460-row fences and both
racial Auto-Potion preference flows remain verified separately. The connected
build reconstructs byte-exact; no broad integration/campaign replay was needed.

Root implementation review checked all three Thumb continuations, preserved
callee registers/stack alignment, original mode1 allocator fallback, exact
ownership marking, pointer bounds, copy tail and release guards. Native0x4340
storage is restored only for the real read-only entry; no full inventory list
is assigned this smaller capacity. This closes the identified Status headroom
defect, not maximum scene capacity or the remaining artwork/release gates.

## Reproduce and continue

Build the palette with the existing20-history/all-class/workspace/provisional/
fast-rotation/owned-menu/shared-heap/compact-keyboard flags plus
`--compact-battle-status`. Then build-connected-art.py with explicit
`--source build/art/live-palette/status-current.json`. Never use a mutable old
palette index as an implicit parent. Keep the earlier d9acd723 checkpoint and
its evidence within their original scopes; no prior failure is relabeled.

Remaining: measured compositor/input delay and native phase analysis;
concrete larger-scene/effect capacity; remaining natural action/effect consumers;
assembled acceptance and reproducible technical delivery. Actual animation/art
refinement remains deferred by the user, and all G gates remain open.
