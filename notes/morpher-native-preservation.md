# Morpher native preservation

Accepted candidate: `687ed5d48494dcb46d8b70612680ede56d5dec86`.
This checkpoint changes test sources and documentation, not the game image.
V05's remaining Morpher scope is accepted for the cases below. Full campaign
coverage, arbitrary animation combinations and release acceptance are separate.

## Fixture and scope

`prepare-morpher-fixture.py` constructs one reusable battle through ordinary
Giza travel and deployment. The original Nu Mou keeps its identity/race, with
Morpher and secondary Black Magic declared before battle construction. Nine
mastered Soul abilities and the captured bank are controlled inputs. The original
Capture application creates each captured record/Soul on an isolated clone;
this is fixture setup, not a claim of actual Capture gameplay. Native equipment
setup equips each Soul before its case. No morph flag, hit, result, sprite or
post-input movement output is supplied by the test.

`test-morpher-player.py` executes all nine transformations through native menus.
It compares all48 unit selectors per form against the clean game: only the four
appearance selectors may select monster animations. Identity, native gameplay
selectors, equipment, mastery, bank and inventory remain intact; the renderer's
IWRAM code remains equal to ROM. Root reviewed all nine resulting form captures.
The native affiliation palette is retained; no new monster artwork is required.

`test-morpher-lifecycle.py` consumes those hashed transformed states. All nine
forms move through the native board/wrapper/facing/coordinate commit path, take
ordinary enemy damage (500HP becomes491 or492 before the next Morpher turn),
and execute a native monster ability. Eight manually Unmorph and restore the
ordinary Morpher; Bomb executes Blowup, reaches0HP, clears the form and passes
control normally. All36 phase checkpoints are preserved. This is bounded
playback plus selector/code integrity, not an exhaustive review of every frame
of every monster skill, terrain or palette combination.

| Form | Exercised original action | ID |
| --- | --- | --- |
| Goblin | Goblin Punch | 266 |
| Flan | Acid | 269 |
| Bomb | Blowup | 271 |
| Dragon | Mighty Guard | 274 |
| Lamia | Night | 277 |
| Bug | LV3 Def-less | 282 |
| Panther | Poison Claw | 293 |
| Malboro | Bad Breath | 297 |
| Floateye | Stare | 300 |

Root's read-only comparison confirms all nine installed28-byte action records
are identical to their clean originals. Morphed units use their monster command
set; ordinary Fight/secondary Black Magic are not the commands offered while
morphed. The fixture's Black Magic assignment is not a claim to override this.

`test-morpher-exit.py` accepts all nine live forms plus the actual Blowup KO.
EnemyHP zero is declared at each exit scenario's start. The game handles Wait,
victory/ending/results and clears the morph, retaining identity, Soul equipment
and all captured records. This does not claim the enemies were defeated by a
played campaign battle. Nine cases end at native mandatory territory placement;
that screen is explicitly not the ordinary freely available system menu.
The KO continuation places the awarded Lutia Pass through native cursor/input,
then performs a normal save and fresh SRAM-only Continue on the shipping ROM.
The full clan, inventory/extraAP and captured bank survive byte-for-byte with no
stale morph. Root reviewed the cold world-map capture.

## Evidence and reproduction

Private artifacts are under the candidate directory named above. Successful
reports (including authenticated retained phases/cases):

- `morpher-player-20260917T065215.753262Z/report.json`, SHA1 `c063d51b7c1c10fe7f4859ec4647e0d7ce654f23`.
- `morpher-lifecycle-20260917T070212.720631Z/report.json`, SHA1 `be3a5ca1046cb31de6f6509a3c11bd891d1b9b80`.
- `morpher-exit-20260917T070952.400965Z/report.json`, SHA1 `6997df0e2b5b59c04cb3cc4c5bbbb5a36fb19f2b`.

Passing transformation continuation: `20260917T065215.047982Z` (17.2s).
Passing lifecycle continuation: `20260917T070212.012288Z` (93.2s).
Exit run `20260917T070549.649296Z` retains nine passing form exits;
`20260917T070951.681623Z` completes the KO/placement/save continuation (10.8s).
Counters in resumed reports include earlier attempted checks; case/phase coverage,
not their aggregate counter, is the acceptance claim. The first lifecycle report
inherited its helper's scope paragraph; the source now keeps its own scope. That
text-only correction did not warrant replaying passing gameplay.

Fresh reproduction, in order (each consumer authenticates its producer rather
than executing it again):

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-morpher-player
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-morpher-lifecycle
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-morpher-exit
```

Each consumer also has a `-resume` test ID for unfinished cases/phases. The fixture
cache authenticates its source inputs and outputs. These are targeted V05 tests;
no full integration run is justified by this source/documentation checkpoint.

Earlier failures remain recorded. They exposed test premises rather than a game
regression: ctypes needs immutable bytes; the fifth native Unmorph row shifts
Wait/Status8px left/16px up; coordinates commit after facing; moving in place
cancels Move; native monster commands replace Fight/secondary; Blowup KO skips
facing; Night can make the same actor the next ready unit; and mandatory Lutia
placement blocks Save. Completed transformations/families were retained while
correcting those boundaries. No shipping logic was changed to satisfy a test.
