# Physician and Sapper integration

September 27, 2026. The user approved the anchored artwork and requested both
classes be connected end to end. The [design](../CHEMIST-PROGRESSION-SPEC.md)
and two JSON data files beside this document define jobs 126/127, twenty lessons
and ten teaching weapons. The abandoned September 26 data-only attempt is
superseded by this implementation. Intermediate ROMs remain labelled test-only;
only the authenticated package adapter can promote one to the local launcher.

## Reproduction

Use the authenticated accepted 0.7.4 parent, SHA-1
`dd20c5771418cf470594c3e79c6d197b3bae4848`, and the approved art inventory.
Run each stage to completion in order:

1. `node scripts/build-chemist-progression-data.mjs`
2. `python scripts/build-chemist-progression-art.py`
3. `python scripts/build-chemist-progression-menu.py`
4. `python scripts/compile-chemist-progression.py`
5. `python scripts/install-chemist-progression-probe.py`
6. `python scripts/build-chemist-progression-actions.py`
7. `node scripts/build-chemist-progression-help.mjs`
8. `Test Expansion.ps1 -Plan scripts/chemist-progression-test-plan.json -Suite chemist-progression`
9. `python scripts/package-chemist-progression.py --run <passed-run/report.json>`
10. `Test Expansion.ps1 -Plan scripts/mod-release-test-plan.json -Only test-mod-release`

The fixture-diagnostic step is outside the acceptance suite: an opt-in exception
investigation, not a passing check. Stage 9 checks all ten acceptance step IDs,
unchanged inputs, per-test ROM hashes and compiled source/header hashes, then
verifies deterministic BPS creation, exact clean-ROM roundtrip and wrong-source
rejection. Promotion is local; it does not upload, launch, or touch player saves.
Stable launchers retain the normal-save directory and ROM basename. Use normal
in-game saves when updating, not emulator savestates from a different ROM.

## Implemented consumers

- Both jobs: race wheel entries, prerequisites, native portraits, battle actors,
  animations, wheel figures, eligibility badges, primary/secondary command
  lists, all twenty AP lessons, help, support/reaction/combo selection and ten
  teaching weapons. Cyril shipments add two, then four, then four weapons.
- Physician: seven healing/preventive commands, Follow-up Care, Emergency
  Dressing and its combo. Native observers distinguish new ailments from old
  ailments and actual cures from harmless queries. Recovery executes through
  the existing queued action path, once per qualifying event.
- Sapper: seven commands, Spotter, Duck and Cover and its combo. Breach exposes
  Protect/Shell choice; Flash uses native Blind accuracy; Concussion uses legal
  knockback. Tripwire marks one empty tile, expires/replaces per caster, avoids
  mid-air crossings, executes native Lightning damage/Slow and stops lethal
  movement. AI avoids hostile traps. Springboard owns an ally route, rechecks
  occupancy/mobility, charges once and preserves the caster's Move budget.
- Timed Fuse uses an owned delayed controller and native hit-number/KO playback.
  It resolves the carrier's cross, including allies, with native element
  immunity/absorption. Movement, Remedy, KO and lifecycle cleanup cancel it.
  Delayed effects reuse existing native visuals; no bespoke explosion artwork
  or palette bank was introduced.
- Law forecasts and committed results retain native command elements and
  successful harmful-status receipts. Movement retains native route execution.
  AI uses actual ability admission/search and evaluated-unit state copies.

## Coordinated memory and save contract

Live job state is 27 bytes, preserving the prior 22 and adding five. Schema 3
packs each live record into 22 flash bytes (174 used bits, two zero padding
bits), retaining the existing 824-byte suspend envelope. Schemas 1/2 migrate
with the new fields zero. The canonical 36-unit bank ends at `0203F7DC`.

Inventory capacity is 470 items; its view ends at `0203FF58`. Copy, execution,
snapshot, AI, damage and fight roots live at `0203FF60..0203FF87`. All live,
equipment, AI, snapshot, reaction, sorting, save and restore consumers compile
together. Copy extras are 66 bytes; the full party list moves to +7290 and the
allocation to +9990. Battle Status in the accepted parent uses this full path.
The manager allocates +450 bytes with its header at +440; snapshots and command
selection allocations grow with their transported tails. Static layout asserts
and native allocation checks protect these boundaries. Transient route and
delayed-controller pointers never enter normal saves.

The code imports distant Thumb targets with ARM7TDMI-compatible stubs. Weak
callbacks are resolved explicitly. Component-local predecessor aliases must not
be silently rebound by merging symbol maps: the lifecycle chain is
Dark Knight -> Viking -> Chemist -> Bard -> Samurai, once each. A cold fixture
caught the recursive-alias failure that isolated effect tests did not.

## Artwork

Approval is authenticated by
`src/art/new-job-review/chemist-integration-approval-2026-09-27.json`.
There are 148 distinct drawings: 68 Physician, 80 Sapper. All 150 populated
sequences retain native timing/control records. Fixed 64x64 canvases use
origin (32,56), with 32x40 native actor layouts and existing palettes. Import
checks exact indexed pixels after native layout reconstruction. Portrait and
wheel archives append approved entries while preserving every older decoded
entry. Original ROM assets, reference worksheets and generated builds remain
private and ignored.

## Acceptance scope

Final assembly is a substantial milestone because the live state/copy ABI and
both delayed/movement lifetimes changed. Run the entire declared new-job suite
against the final help-stage candidate, including the mixed original/new-class
battle and cold Suspend/Resume. Earlier legacy plans pin older parents and do
not establish acceptance for this ROM merely by passing; their unaffected
evidence is retained rather than rerunning them against the wrong image.

The eleven gates cover codec migration/corruption, native healing/damage/payment,
Flash/Triage/Spotter matrices, lifecycle callbacks, cold mission entry, Fuse and
trap playback including lethal/immune cases, six paid movement flows, AI
admission/trap targeting/avoidance/ally search, cold SRAM Resume, actual
world/battle menu allocation/copy/return, all lessons/unlocks/shop tiers and
native element/harmful law receipts. Each run preserves fixed inputs, complete
logs, ROM identity and failure captures under ignored build output.
The status-record gate checks every historical accessor across all 36 canonical
slots, movement-only records, real Last Resort icons and canonical field dispatch.

This is a first playable balance pass. These checks do not represent a whole
campaign playthrough, every law/Judge animation, or exhaustive combinations of
all old and new abilities. Any such claim needs its own declared scenario.

## Accepted local build

### September 27 status-record regression

The player's captured battle exposed a gap in the 0.7.5 gate: retained older
accessors still used a 22-byte stride against the new 27-byte live records.
Montblanc's movement-only record consequently produced native status IDs 40/42
through old Geomancer queries. The installer had redirected only the newest
symbol entry. Capture and old diagnostic evidence are preserved under ignored
`build/expansion/bugs/2026-09-27-white-monk/`; no player save was modified.

The repair redirects every authenticated retained entry and recompiles the
direct Geomancer cohort traversal. Replacing its entry also bypassed an existing
fast dispatcher in the first repair candidate. The original eight-frame Move
test exposed missed input sampling. A diagnostic 32-frame press confirmed the
delay; it is not the acceptance input. The final source retains the canonical
fast path, now checked through every historical field entry. The test also needs
60 no-input frames after its artificial team/HP edits for native menu refresh;
settling before those edits did not help. It asserts unchanged starting HP,
position and trap timer after settling, then uses the original eight-frame inputs
and unchanged damage, consumption and movement expectations.

Final assembled acceptance requires all eleven `chemist-progression` IDs on the
repaired candidate plus `cp-user-status-regression` on the captured battle.
This full-gate rerun is justified by the demonstrated cross-class record-layout
regression: old and new status, movement, copies, AI and suspend consumers all
share these entries. Prior 0.7.5 checks remain historical evidence, not proof that
its shared status layout was correct. Cached visual indicators in an old emulator
state are not repaired by changing query results; update through a normal save.

Local 0.7.6 is packaged with game SHA-1
`b7d011755c998e23935a53d416bea252fef356ef` and ZIP SHA-256
`1df63f188737a60cdba6c3639069d6204e5891756e4a71dcdeba3de4c79db138`.
All eleven gates passed with unchanged inputs in
`build/expansion/test-runs/20260927T222305.555070Z/report.json`.
The captured battle's status regression passed in `20260927T222512.014113Z`;
32 packaging/launcher checks passed in `20260927T222554.831905Z` with detailed
receipt `build/release-tests/20260927T222555.685023Z/report.json`.
Default-off Geomancer syntax checks also passed. No remote publication, player
save modification or running-game restart occurred. The captured diagnostic
state is later than the supplied attack-preview screenshot, so this evidence
does not establish that screenshot's missing target name/portrait is repaired.

### Historical 0.7.5 gate

All ten gates passed on SHA-1 `3cefd6479739d7bb24a1fb4cde36b06f8bbebd98`
in `build/expansion/test-runs/20260927T194549.078118Z/report.json`, with unchanged
inputs. The local 0.7.5 package has SHA-256
`a7bb4856cd8af71f2950661a2db3278cdc1d0d5de1ea51dfbcb0ff09e853cf15`.
`Play Mod.cmd` and `Play New Sprites.cmd` resolve that package. No remote release
was uploaded and no game process or player save was changed.

Package/launcher verification passed 32 checks in
`build/expansion/test-runs/20260927T194832.537737Z/report.json`, with detailed
receipt `build/release-tests/20260927T194833.569729Z/report.json`. Both launchers
validated the same ROM and save override; all protected player files remained
byte-identical. All 55 coordinated C modules also passed default-off syntax
checks with the corresponding original 460-item registry. Using the expanded
470-item registry with default-off memory roots correctly fails the inventory
overlap assertion; do not mix those two build configurations.
