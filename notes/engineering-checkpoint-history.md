# Engineering checkpoint history

Historical status entries; see IMPLEMENTATION-STATUS.md for the current state.

## Current expansion engineering build

The previously accepted assembled candidate is
`d1565a7ee341621e58bd2bb791b065144fe51aec`. It adds Fell Cleave, its Exposed
drawback, native remedy/expiry/save handling, and the expansion status-icon
display. All91 declared implemented-feature regression steps pass on this exact
ROM across resumed deterministic runs. `build/expansion/d156-regression-coverage.json`
records each step's passing log, verifies unchanged application inputs, and
checks the current test entrypoints. This is split-run coverage, not one
uninterrupted run or completion of the expansion. The accepted snapshot is
under `build/expansion/accepted/d1565a7ee341621e58bd2bb791b065144fe51aec`.

The candidate contains10 enabled new actions,2 supports and8 combos. The
approved85 actions and36 support/reaction lessons are not yet all implemented.
All testing now runs as deterministic local scripts, with fixed scenarios and
retained reports. No agents run or monitor tests. See `TESTING.md`,
`notes/fell-cleave-integration-review.md` and `STATUS-EFFECTS.md`.

Private Samurai candidate `41c51aa1f597b1bb6419166ccca3ddaa91597176`, based on
the accepted d156 build, implements Ashura, Osafune, Guarding Draw,
Kiku-ichimonji, Murasame and Kiyomori. Its complete twelve-step Samurai suite
passes in one uninterrupted run with unchanged inputs:
`build/expansion/test-runs/20260914T231932.500064Z/report.json`.
Native execution, lifecycle, law, actual hit/miss, immediate Counter,
Silence/Reflect, allied cross targeting and cold-save checks pass. This adds
six privately tested actions; the assembled build's count above remains ten.
Wind Draw, Moon Blossom, Higanbana and the Samurai supports/reactions are
still open. See `notes/samurai-restoration-review.md` and
`notes/samurai-integration-review.md` for exact evidence and remaining work.

Subsequent private candidate `f71fceb6a7d6d183cd1fcb8de4513f6e18376320` adds
Wind Draw. Focused native geometry, all-direction actual battle, obstruction,
ally exclusion, damage, cold-save and law checks pass. This brings the private
implementation to seven Samurai actions; it has not received a complete
seven-action suite or main integration. See `notes/samurai-wind-review.md`.
Private candidate `e6e2ba03b53a4df80a8a4c17f96af490d28eb3ff` then adds
Moon Blossom. All seventeen Samurai steps pass in one uninterrupted run with
unchanged inputs: `build/expansion/test-runs/20260914T234811.104349Z/report.json`.
The tests include actual cross attacks, misses, Damage-to-MP interception,
one Regen grant per action, native status compatibility/cleanup, laws and cold
resume. These eight Samurai actions remain private; Higanbana and Samurai
supports/reactions remain unimplemented.

Follow-up candidate `46a0d51567965ae0136e4c0a0f01d16ab87d2540` corrects Murasame
to reject undead allies as the approved shared restoration rule requires.
Its six-step focused restoration run passes, including an exhaustive packed
state formula check, undead eligibility/direct-execution cases and the actual
battle replay: `build/expansion/test-runs/20260914T235536.833910Z/report.json`.
This latest candidate has focused correction coverage, not a repeated full
Samurai regression. See `notes/samurai-moon-review.md`.

Higanbana's pending record layer has a separate isolated ARM-code fixture.
Its deterministic test passes491161 assertions for the stored pulse schedule,
replacement, exact canonical/staging owners, migration and roster swapping.
No Higanbana action or wound copy/turn-end hook is enabled by that fixture.
See `notes/blade-wound-storage-plan.md` for evidence and remaining integration.

New assembled candidate `ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7` integrates
the wound record into canonical/staging storage, roster sorting/clears,
manager/selection/party/snapshot copies and evaluated law/preview units.
Focused native copying, allocation, law evaluation and persistence checks pass;
actual normal save/load, sorting, battle preview/cancel, suspend/cold resume
and ordinary battle lifecycle checks also pass. All91 declared regression
steps now have passing evidence across resumed deterministic runs on this
exact ROM, with unchanged application inputs. The reconciliation report is
`build/expansion/ba1c-regression-coverage.json`; the accepted ROM, engine,
sources and scripts are under
`build/expansion/accepted/ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`.
This is split-run coverage, not a single uninterrupted run.
It still has ten enabled new actions; Higanbana application/pulses are not yet
enabled, and the eight-action Samurai candidate remains a separate build over
the older accepted base. See `notes/blade-wound-storage-integration.md`.

Latest private Samurai candidate `d7d6e31967d9a4627c08542d96f059bb499fb03e`
rebases the Samurai work onto ba1c and implements Higanbana's initial hit,
scoped native-P snapshot, two end-turn pulses and broad-remedy/lifecycle cleanup.
Focused deterministic execution and lifecycle checks pass, as do actual
Higanbana menu/preview/cancel/commit, Wait, two-pulse and lethal-cleanup scenarios.
Native suspend and fresh cold resume preserve the one remaining pulse.
Full Samurai acceptance, Wound UI/laws and the broader expansion remain open.
See `notes/samurai-wound-review.md` for exact hashes, evidence and limitations.


## Earlier integration entries

The last complete `Build Engine.ps1` regression run passed on combat SHA-1
`ad1767f8b4c78276e711d7e89e669f6b0b272097`. It includes all ten new job menus,
native equipment/AP/save lifecycles, seven axe actions, eight combo profiles,
all 39 permitted weapon-family gameplay cases, and scoped temporary state.
Its retained log is `build/expansion/full-suite-ad1767f8.log`. It also includes
Sanguine Sword, Infernal Strike, Light Foot, Grace, recruitment prerequisite
counting, and the Quin acceptance-history safeguard. The separate deterministic
Quin suite passed all four steps on the same ROM, including fresh fixture
generation and actual normal/suspend save imports. Its retained report is
`build/expansion/test-runs/20260914T210535.570443Z/report.json`.

Subsequent combat build `5b90d5fb623457405d96948e33df623b342da14c` adds
Tomahawk's range-four physical attack and explicit terrain line of sight, plus
the eight named native combo profiles and their primary-weapon restrictions.
Native arithmetic, proc exclusion, geometry, and combo component tests pass.
Tomahawk's actual player-selected hit/miss/cancel test passes with exactly four
MP paid on execution, no payment on cancellation, and no axe consumption.
Tomahawk's turn completion and native suspend/cold reload pass. Its physical
projectile is visually verified; the fix preserves native equipment and quest
icons. Combo tests cover initiation, actual participation against named native
donor controls, and cold saves. They exposed knife-animation hangs for Nu Mou
Chemist and Viera Dancer; both scoped pose fixes passed gameplay verification.

Previously accepted combat `69a844aee6a536f29e2b00959acce62de1658e27` enables seven axe
actions: Chop, Tomahawk, Overpower, Shatter Guard, Armor Splitter, Reaping
Arc and Executioner. Shatter and Armor Splitter passed 340 fresh gameplay
checks on their earlier integration. Executioner passed 300 fresh gameplay
checks on `d658e596e13febd725a0c312c204f844d2b92e62`, including its actual
displayed hit chance, execution-time HP threshold and cold save/resume.

The current build fixes arc direction through target selection, pre-attack
rotation and action construction, and carries the AI's chosen direction.
All thirteen gameplay direction cases now select the intended recipients,
including invalid center tiles. The current build passed 846 fresh arc
battle/save checks and the council's native AI direction and hook comparisons.
The whole regression suite has passed on that revision. Scoped Exposed storage
now covers saved units and temporary law/preview copies; its actual damage
and expiry rules are not yet installed. Both Chemist and Dancer knife pose
fixes are integrated; all 39 weapon-family gameplay cases passed on d658.

Combat `1587503e86d1fc9285ebb70ab6f04c01c40fe00e` additionally integrates
Sanguine Sword, Infernal Strike and Light Foot. Their current native and
fresh battle tests pass: both racial Dark Knights, hit/miss and cancellation,
overkill/empty MP/undead reversal, external-job movement and cold saves.
The current composition has nineteen implemented lesson descriptions with
native decoding and original/equipment routing tests. Grace now passes the
composed native and actual-game suites, including all four facing directions
against an independent accuracy-table control.

**The 129-lesson expansion remains unfinished.** Nine integrated custom
actions and two supports have passed targeted battle lifecycle tests. The
other 76 actions and 34 supports/reactions still need completed integration.
All eight combo profiles and the expanded weapon-family suite pass.
Custom status/turn effects, synergies, law integration, remaining
vanilla+ safeguards, and final packaging remain required. Allocated or
learnable lesson records are not evidence that their effects work.

Source edits for Fell Cleave/Exposed and private Samurai work are pending
composition and further verification. They are not part of the accepted ROM
above. The new deterministic runner replaces agent-operated test execution;
the final council review remains separate from running the tests.

Detailed findings and continuation notes are in
[expansion engineering](expansion-engineering.md), with individual council
reports beside it. The foundation status below describes the launcher build,
not these newer disposable test ROMs.
