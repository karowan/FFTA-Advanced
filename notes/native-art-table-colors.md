# Explicit-source palette effects — September 18, 2026

Follow-up to `25346c3`. Current private candidate is
`98cfcfc8558ac58b4fb4f24d70ebf50ef2274257`, resolved through
`build/art/live-palette/poc.json`. Stage159444 bytes, state8096 unchanged.
No package, player save, launcher or running-session change. Built-in imagegen
only; final sprite refinement stays deferred. All G gates remain open.

## Two additional setters

-081474BC derives an exposure-style target from an explicit palette table. Its
  minimum-three channel floor applies to the target calculation only; neither
  the source table nor current interpolation colors are altered.
-08147E28 derives a weighted-mix target from an explicit palette table using
  the original08147830 conversion and native16-bit color/8-bit weights.

Both receive seven arguments. Authenticated16-byte entry stubs preserve the
table pointer and all three caller-stack parameters, reproduce the displaced
prologues and continue the original setters. The installed wrapper retains the
existing pre-effect ownership tracking and exact native callbacks.

Table mapping is shared with baseline restoration. A complete source bank must
equal the binding's authenticated native baseline (normal or dim), or be uniform.
Baseline sources map to the corresponding generated class and brightness; uniform
sources remain literal. Unknown palettes, partial banks and duration above255
explicitly refuse generated effects while preserving the original native call.
Table offsets use the actual first color, including ranges starting before the
owned bank. There is no guess based on average color or native palette index.

## Verification

All selected tests passed in runner `20260918T091447.854270Z` on current98cfc:

| Test ID | Checks | Evidence |
| --- | --- | --- |
|test-native-art-table-colors|17400|ARMv4T original/installed seven-argument execution. Normal bank0 and native-dim bank9, baseline/uniform source tables, five-color prefixes, argument truncation, both stack alignments, durations0/1/8/17, interruption, exact current-source preservation and targets/callbacks, full source-table immutability, outside gameplay memory and unknown/partial/unowned/duration boundaries. |
|test-live-art-table-colors|599|Actual mGBA callbacks/hardware for both table effects, black-fade interruption and final baseline restore; exact native/unowned palette and unit isolation, source bytes protected by clone input guard. |
|test-native-art-late-entry|4834|Expanded to all fourteen common-setup setters, normal/dim sources, appearance at0/3/17 callbacks, exact original-engine continuation and prior capacity/latch boundaries. |
|test-live-art-palette-native|1147|Authenticated patch points, byte-exact rebuild and existing reservation checks. |
|test-native-art-palette-binding|32|Shared table-mapping/restoration regression contract. |

Reports:
`build/art/table-colors/20260918T091448.549690Z/report.json`,
`build/art/live-palette/fades/20260918T091517.269395Z/report.json`,
`build/art/late-entry/20260918T091524.427604Z/report.json`,
`build/art/live-palette/native/20260918T091530.452861Z/report.json`, and
`build/art/palette-binding/20260918T091533.050562Z/report.json`.
The table-exposure midpoint screenshot was visually inspected. Artwork remains
an unaccepted transport draft. There was no failed run in this batch; earlier
rejected candidates and failures remain in their prior checkpoint notes.

The fourteen identified target setters sharing native146E54 setup are now hooked.
This is not a claim that all palette operations or scene lifetimes are complete.
Explicit arbitrary transformed source-table identities are still unsupported.
The controlled hardware experiment does not establish every natural trigger.

## Next lifetime work

Static original-code inspection confirms146DC8 can completely remove matching
tasks or shorten their color range at either end. The selection also filters by
task type. It calls native identity helper14873C and destructor148498
for full removal. A generated binding must retire when its task is removed and
must stop following any colors removed from a surviving task. Existing setup
invalidation covers replacement starts, not every standalone cancellation.

Correction after tracing both helper bodies:148738/14873C simply return the
supplied handle; the original checkpoint incorrectly called14873C a task
selector. The implemented controls and evidence are now documented in
`notes/native-art-task-controls.md`.

Analyze cancellation/task control and the separate146FB8/147068/147124/1471E0
constructors before adding hooks; retain exact native task-list/heap behavior.
Rotation/copy consumers, natural scene/heap/stack lifetimes, maximum mixed-class
capacity, remaining assets, timing/phase failures, final art and packaging remain
open. Prior unchanged reload/deployment/transition evidence remains reusable.
No broad suite, player save, installed build or game launch was involved.
