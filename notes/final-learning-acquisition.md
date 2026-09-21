# Current-build learning and acquisition acceptance

Candidate `687ed5d48494dcb46d8b70612680ede56d5dec86` passes the complete
equipment-learning association matrix, all ten native job menu/save flows,
approved teaching-stock combinations, prices and purchase commits, and an
actual opening shop/equipment/cold-save flow. No shipping game code changed.

This closes V03's mechanics, data and menu acceptance on the assembled candidate.
It does not claim campaign earning of every story flag; V06 and final R02 remain
open. No reward source, shortcut, prerequisite or free mastery was added.

## Complete learning matrix

`test-integrated-learning.py` authenticates the current ROM and existing native
IWRAM capture. All85 teaching weapons,129 lessons and158 racial lesson records
run through both stack alignments:316 cases,6,639 assertions. Each starts with
zero AP and one owned teacher on its legal job. The complete native equipment
setter grants equipment-only usability; removal removes that usability.

The installed results block awards AP to just below the independent approved
cost. Removal preserves earned progress; re-equipping and one more AP unit
reaches mastery and emits the correct racial notification index. Removal now
retains usability. Further AP produces no duplicate notification or overflow.
Inventory, job and race remain intact. Award quantities are declared inputs,
not injected mastery results or claims of campaign rewards.

The actual results block `08049032..080490A6` executes its cost, decision, write
and notification logic. This does not draw129 individual results popups. Native
readable lesson help retains its separate installed-help audit.

Run `20260917T054954.530321Z`, step2, passes. Private report under the candidate:
`integrated-learning-20260917T054955.279322Z/report.json`.

## Every job through native menus and saves

The same run's step3 passes jobs116..125 on the current image.
`test-all-new-jobs-in-game.py --integrated` authenticates its candidate capture
and no longer executes an unrelated inventory stress suite when importing an
ARM helper. Historical probe/frozen modes remain available. The integrated
mode never overlays a bootstrap binary onto the assembled image.

It verifies job-wheel paging, selection, cancellation/confirmation, identity,
race, AP counts, legal equipment cleanup, unchanged inventory/AP, reopening,
normal save, exact full-unit cold load, and selection of the other new same-race
secondary command. All seven donor appearance selectors for each job and1,024
native command-label cases are checked. UI fixtures declare mastery; the
independent learning matrix above verifies how it is earned.

Reports/screenshots: `all-new-jobs-ui/<candidate SHA1>/`. Root inspected the
Samurai/Dark Arts labels, Geomancer wheel and Mystic Knight/Spellblade/Dance
labels. Native donor sprites and readable labels are intact. These are menu/save
checks, not substitutes for job-specific battle playback.

## Stock, prices and checkout

`test-integrated-acquisition.py` imports only the independent stock oracle from
`test-acquisition-gates.py`. It skips that legacy module's other suites and
never injects its bootstrap engine. The optional candidate parameter preserves
legacy callers. Installed native consumers are compared with the clean-ROM
stock control and approved acquisition ledger.

Run `20260917T055300.961780Z` passes:

- 2,160 stock combinations: five towns, six tabs, three original shop tiers,
  three territory counts and all eight combinations of completion gates7/13/19.
  Original rows remain exact; additions obey town/tab/stage, without duplicates
  or overflow. Largest list182 remains below the byte count limit.
- 1,275 prices:85 items, five towns, three clan ranks. Original sell floors and
  applicable town/clan discounts remain intact.
- 170 native checkout commits:85 IDs with quantities1/3. Exactly the intended
  equipment count changes, gil is deducted once, and all120 quest-inventory
  bytes remain unchanged.
- 2,131 installed-design checks:129 lessons,158 racial records,85 equipment
  records and ten job profiles match the approved0.7 specification.

Flags are declared inputs. Earlier native completion/save evidence establishes
their semantics; earning them through campaign progression remains V06.
Acquisition report: `integrated-acquisition-20260917T055301.690641Z/report.json`.
Static report: `build/reports/installed-design.json`.

## Actual opening purchase and teaching interface

Run `20260917T055349.846222Z` passes
`test-new-equipment-in-game.py --integrated`. Native Sprohm opening stock has
exactly the six approved added weapons and excludes the later axe. Fixed player
inputs buy Recruit Axe453 for300gil, equip it, obtain its Human extension
lesson, save and cold-load exact gear/inventory/gil/AP. Native removal cases at
zero/90/100AP retain usability only at mastery.

The seed is unchanged. Its disposable offhand is explicitly cleared for the
approved two-handed axe; separate legality tests retain shield/Monkey Grip
rejection. The final integrated report wording removes obsolete historical
battle/learning TODOs. That metadata edit changes no assertion or input and did
not warrant replaying the successful runtime.

## Reproduce only affected portions

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only` with:

- `test-integrated-learning-cached`
- `test-integrated-job-menus-cached`
- `test-integrated-acquisition-cached`
- `audit-installed-design-cached`
- `test-integrated-opening-teaching`

These use read-only assembly verification and exact existing captures where
needed. This was the targeted V03 acceptance gate, not a per-commit full suite.
All selected runs passed. Raw reports, ROMs, saves and tools remain ignored.
