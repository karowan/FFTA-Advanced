# Recovery, pub access and sorted deployment

Candidate `687ed5d48494dcb46d8b70612680ede56d5dec86` passes the three remaining
non-Morpher vanilla+ player paths below. No game code or ROM changed.

## Two paid quest-item recoveries

Run `20260917T062103.530712Z` passes57 assertions in16.5 seconds. One continuous
controller-input timeline starts from explicitly declared original Elda's Cup
source completion,5,000 gil, level50 Ford and64 different held quest items
excluding the Cup. It does not claim to have played that original source quest.

The actual pub charges300 gil and assigns Ford. Ordinary world travel advances
the five native dispatch days. The player rejects the replacement at the full-bag
dialog: every existing item survives, no extra fee/refund occurs, and the earned
entitlement remains. Ordinary travel clears the one-day cooldown. The pub then
charges another300 gil for a second dispatch. After another five days, actual
reward menus replace only the selected first inventory slot with one Cup.

Both returns preserve equipment/extra AP and all original/source/use/service
completion flags. Holding the replacement suppresses another recovery. Normal
Save and fresh SRAM-only Continue retain exact clan/AP, equipment, gil, quest
items and gift receipts. Final gil is4,400; final SRAM SHA1 is
`ff114a7123df8bc17c7393c441c522324205f4b2`. The seed remains unchanged.

Private artifacts are under
`quest-recovery-cycle-20260917T062104.316370Z/report.json` beside the candidate.
Every completed phase has state/RAM/SRAM hashes for authenticated continuation.
No results, timers, rewards or success flags are written after preparation.
Inherited test wording called the fee Cyril's; the actual pub is Sprohm. The
committed wording now says town-adjusted fee. This text-only correction and a
capture-label correction do not change inputs or warrant replay.

This completes the second-payment/full-bag obligation in A01/V05. Retain the
all64-route entitlement/lifecycle matrix and original refund evidence.
Campaign milestone coverage remains V06; the source progression portion of
A01 stays open there rather than being inferred from this declared setup.

## All pub options remain available

Run `20260917T062840.810877Z` passes18 assertions in3.2 seconds using the above
authenticated first-payment checkpoint. The installed native dispatch prefix
maps the four displayed indices to original actions1/0/2/3. The only emulated
instruction in that detached check is ARM7's standalone BL suffix; the actual
menu playback uses mGBA and the unchanged candidate.

Fixed inputs open Missions, Rumors and Quit Mission, cancel safely, and use
Leave to exit the pub. Missions constructs a bounded actual offer list. Each
case preserves clan/AP/equipment, gil, quest items and Ford's active assignment.
Root inspected the rendered rumor list, the active Cup dispatch under Quit
Mission, and the town menu after Leave. This proves access/cancellation, not an
additional actual mission-abort payment/refund scenario; the native cancellation
matrix remains its separate evidence.

Report: `pub-options-20260917T062841.573832Z/report.json`.

## Sorting survives actual deployment

The same run passes27 assertions in7.7 seconds. It reuses the current native
Herb Picking acceptance capture and declares distinctive extra AP/preferences
before sorting. Native Select input still refuses Marche/Montblanc, swaps Ford
and Jona's complete generic records, and moves their extra AP/preferences exactly.
The accepted mission queue is unchanged.

World travel, mission entry, deployment-square/facing selection and battle
construction then execute through normal inputs. Exactly six original party
members deploy once. All six retain identity/name, race, job, equipment and
racial AP; all extra AP/preferences and equipment inventory remain exact. The
native command menu becomes ready. Root inspected Jona deployed as the third
member, confirming that the sorted identity reaches the visible deployment UI.

Report: `sorted-deployment-20260917T062844.829205Z/report.json`.
This fills the specific deployment gap; the earlier dispatched sorting and
normal cold-save cases remain reusable. It does not claim every special story
scene was played. Morpher visuals remain the outstanding V05 subtask.

## Reproduction

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only` with
`test-quest-recovery-cycle`, `test-pub-options-cached`, or
`test-sorted-deployment-cached`. `test-quest-recovery-cycle-resume` retains passed
phases. The pub consumer authenticates the existing successful recovery report
instead of replaying its producer. All tests use exact read-only assembly
verification; none builds the ROM or runs unrelated combat suites.

The first menu/deployment run `20260917T062803.863237Z` failed before gameplay
because the imported ARM class's default stack constant was declared too late.
Both initializations were corrected together and only those two checks reran.
The failed reports remain retained. ROMs, saves and raw artifacts remain ignored.
