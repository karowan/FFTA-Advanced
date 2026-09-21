# Blade Wound storage integration

September14,2026. Assembled candidate
`ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7` extends the accepted d156 build's
saved and copied unit state. Higanbana application, immunity, turn-end damage,
remedy/lifecycle cleanup and display are not enabled by this change.

Canonical24 party/12 enemy records use72 reserved bytes at1EBC..1F04.
The original format1 migration zeroes that reserve; existing format1 imports
preserve it. No save block enlargement or native AP-byte reuse is involved.
Roster swaps and whole-unit clears carry/clear the correct two bytes. Partial
unit writes preserve them, and unknown sources clear a known destination.

Owned copy tails grow from36 to38 bytes. Snapshot allocation is1014, manager400,
selection3828 and party7268. Actual native constructors and allocation-size
checks pass, including native snapshot sorting and nested rollback. Evaluated
unit containers remain276 bytes by assigning two former reserved bytes.
Those unaligned bytes use byte access. Exact stack/heap tags govern ownership;
copying native character identity cannot claim another unit's wound.

`build/expansion/test-runs/20260915T000548.242998Z/report.json` passes all five
selected steps with unchanged inputs: persistence engine, generic native copy
entrypoints, evaluated units, native copy constructors and exhaustive wound
record arithmetic. Distinct wound values follow every source/destination pair
alongside AP/preferences/packed state; whole-RAM comparisons check isolation.
Actual native law evaluation copies both actor and target wounds independently
across every original action and retains native law results/RNG behavior.

`build/expansion/test-runs/20260915T000649.849510Z/report.json` passes four
selected steps with unchanged inputs. Actual normal SRAM save and cold load,
native party sorting, battle Fight preview/cancel, Save Now and cold Resume
Battle preserve all108 state bytes. Every unit has a distinct nonzero wound
record in the save fixture. AP/preferences and memory guards remain intact.
The ordinary battle lifecycle replay also passes on the rebuilt ROM.

The first focused attempt failed because the old persistence oracle expected
the newly assigned wound bytes to stay in place during roster sorting. The
oracle now expects the approved per-unit state to follow the sorted unit,
and checks the entire state block after both swap and clear. The production
sorting behavior was not weakened to satisfy the old expectation.

All91 declared implemented-feature steps now have passing evidence on this
candidate across the resumed runs below. The deterministic reconciliation
`build/expansion/ba1c-regression-coverage.json` verifies unchanged application
inputs, exact commands, current test entrypoints and their changed consumers.
The accepted ROM, engine, source and script snapshot is under
`build/expansion/accepted/ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`.
The older accepted d156 snapshot and player launcher remain available.
This is not a completed mod or one uninterrupted regression run.

## Full regression reconciliation

The91-step run `20260915T000819.824063Z` passed its first56 steps and stopped
at the unit-sidecar clear test. Its old whole-state oracle omitted the new
wound clear. That test now includes the expected two-byte clear and all12
canonical enemy slots. The unchanged ROM resumed in `20260915T001446.194845Z`;
the corrected test and the subsequent job, battle, axe, physical-rider and
Executioner replays passed.

The arc fixture then rejected an obsolete fixed wrapper address. Its placement
setup now obtains the native battle-list wrappers through99CDC on a detached
emulator clone, validates the returned identities and bounds, and only uses
those addresses to place fixture units. No returned scratch data or target
list is written into gameplay. The complete arc replay passes in the next
resume, `20260915T002254.895057Z`.
The production ROM remains ba1c33ea throughout these test-only corrections.
`build/expansion/verify-ba1c-coverage.py` subsequently succeeded against all five
reports and the current files, yielding the91-step coverage report above.

The mobility fixture had the same fixed-wrapper issue. It now reuses only the
native enumerator function from the arc test, and its full movement/cancel/
cold-resume test passes in `20260915T003316.119991Z`. Grace's save test then
needed a bounded wait for the native turn menu and a save comparison spanning
the whole confirmation sequence. Its complete combat/cold-save replay passes
in `20260915T003534.085675Z`, along with all remaining Quin/Fell/status checks.
No production change was needed for these four test-fixture corrections.

Private Samurai UI fixtures still contain fixed wrapper addresses; rebase them
through native enumeration before claiming acceptance on the new allocation
layout. The Samurai candidate over d156 retains its historical evidence.
