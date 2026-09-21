# Full roster transactions and independent save slots

Candidate: `687ed5d48494dcb46d8b70612680ede56d5dec86`.
These passes change test coverage, not the shipping ROM. Native whole replacement
and removal are accepted across all24 slots. Both normal save slots independently
preserve full-clan profiles through fresh emulator loads. The later player-flow
pass below accepts away-member sorting and normal recruitment capacity behavior.
Ordinary mission recruitment has no full-clan replacement offer: the original
world controller skips candidate generation when every slot is occupied.
Do not invent a new replacement UI to satisfy the earlier mistaken test premise.

## Native roster transactions

`scripts/test-full-roster-replacement.py` authenticates the existing candidate's
battle capture, declares a full24-member clan, and lets native `080D241C`
generate Quin. It supplies the native replacement UI's normalized name index97,
join flag and selected pointers, then invokes the entire `08061F54` transaction.
No copy, clear, AP or acceptance result is mocked.

Every destination, replacement/removal, and both stack residues are exercised:
96 cases,7,296 assertions. Other units' native264-byte records,34-byte extended
AP and potion preferences remain unchanged. The selected slot clears old extra
AP, preference and job state; replacement commits Quin's identity and accepted
history and keeps24 occupied slots. Removal vacates exactly one slot and does
not accept the offered candidate. These are native commit tests, not proof of
the full recruitment controller, dismissal dialogue, or original unlocks.

Run `20260917T052540.448625Z`, step3, passed. Private report relative to the
candidate directory: `full-roster-replacement-20260917T052543.013420Z/report.json`.
The same run's save test failed during fixture creation; that does not invalidate
the independently completed roster test, which was not rerun.

## Two real saves and three cold loads

`scripts/test-independent-save-slots.py` starts with the unchanged early-town
SRAM, declares24 valid occupied records with distinct AP/preferences and two
different inventory/gil profiles. All subsequent saves/loads use fixed buttons
on the shipping ROM. It does not construct flash pages or checksums. These
declared profiles do not claim campaign recruitment or earned mastery.

Profile0 is saved to file1, cold-loaded, then changed to profile1 and saved to
file2. The final SRAM is loaded into three fresh emulator sessions in order
file1, file2, file1. All24 native unit records, all816 extended AP bytes,
24 preferences, inventory, Quin history and gil match the selected profile.
Normal loads reset the entire792-byte battle-only job bank. Saving preserves
the live battle-only bank until that ordinary load. The seed save is unchanged.

Final two-slot SRAM SHA1: `d132f6b55da081b880905bba99d4829aef055815`.
The accepted evidence is a chain of bounded phases, not a claim that every
earlier whole-script run passed:

- `20260917T052540.448625Z`: fixture setup rejected a Python bytearray at the
  ctypes write boundary. No gameplay assertions completed in the save script.
- `20260917T052603.280228Z`: first save/cold profile passed; a vertical slot
  input failed to change the horizontal selector and overwrote file1.
  Its immutable `profile-1` checkpoint was reused for the corrected save.
- `20260917T052711.387957Z`: file2 saved, but short cold-menu waits left a
  transition incomplete. The saved screenshots identify the actual menu.
- `20260917T052753.200847Z`: both saves and file1 cold checks passed. File2
  selected the wrong file because the native cursor remembers last-used file2
  and wraps horizontally. Fixed inputs now account for that initial selection.
  Ten assertions passed before that failure; the report remains failed.
- `20260917T052853.199416Z`: a cold-only resume attempted to equate fresh-core
  SRAM immediately after state loading with the explicit saved SRAM. That
  assumption is invalid; the failure capture also attempted a screenshot
  before a rendered frame. Neither was a shipping game failure.
- `20260917T052929.950271Z`: only remaining file2/file1 cold loads ran; all15
  assertions passed. It reads the previously written native SRAM directly,
  records its hash and the prior report hash, and supplies it only at cold boot.

The successful suffix report is
`independent-save-slots-20260917T052930.644905Z/report.json`; its predecessor is
`independent-save-slots-20260917T052753.890693Z/report.json`. Both are inside the
candidate directory. Captures, controller inputs, full profiles, failures,
state/RAM hashes and native SRAM remain private and ignored. No full integration
suite, combat replay, or game build was needed for this coverage-only pass.

## Reproduce

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only` with:

- `test-full-roster-replacement-cached` for the96 native commit cases.
- `test-independent-save-slots-cached` for the complete corrected save flow.
- `test-independent-save-slots-resume` for a retained `profile-1` checkpoint.
- `test-independent-save-slots-cold-resume` for remaining cold loads after an
  earlier run has completed both saves and the first file1 cold check.

Resume selectors verify candidate/seed/report/checkpoint provenance and retain
the original failed reports. The native SRAM suffix additionally records its
exact input hash; it does not claim that RAM-only state bytes prove flash bytes.
Use an existing exact-ROM fixture for native commits; rebuild its declared
preparation only if it is absent or fails authentication.

## Sorting an actually dispatched member

`scripts/test-sorted-dispatch.py` reuses the paid-recovery helpers but runs only
one continuous acceptance/return. It declares distinctive AP/preferences before
paying the actual Cyril15000gil fee and assigning Ford to the20-day Materia Blade
recovery. In the native party screen, Select on Marche and Montblanc changes
neither story unit nor extra data. Select swaps away Ford from slot2 to slot3.
All264 unit bytes,34 extended AP bytes, potion preference and assignment move
together; the native dispatch queue stays exact. The displaced generic member
does not acquire Ford's assignment.

Actual world travel exhausts the original20 days. The native return clears
Ford's new slot, leaves the displaced member unassigned, awards one blade and
charges no extra fee. Normal Save/fresh Continue retains all24 unit records,
inventory, extended AP and preferences. Final gil35000 and one blade reflect
one actual payment/return. Root inspected the party screenshot: Ford is shown
at No.4 with the native Mission label; Marche/Montblanc remain No.1/No.2.

Run `20260917T053428.753715Z` passes51 assertions. Private report:
`sorted-dispatch-20260917T053429.466668Z/report.json`.
Cold SRAM SHA1: `7e028ff007b49cd749ddacbf48dbe518c01f690a`.
Reproduce with `test-sorted-dispatch-cached`; `test-sorted-dispatch-resume`
continues only unfinished phases from recorded checkpoints. Deployment after
sorting remains with V05; this test ends on the world map.

## Ordinary recruitment at capacity and after a vacancy

`scripts/test-full-clan-recruitment.py` declares a results fixture by letting
native Herb Picking end after setting enemy HP to zero, then installing a
native-generated Mythril Rush accepted reward record, its prerequisite flag,
and24 occupied records. This is not a Mythril battle/campaign completion claim.

The whole native vacancy scan `0803600C` returns zero for the full clan. The
original world controller at `080488A0..080488AC` branches away before its
candidate call at `080488E8`; it requires the scan's nonzero free-slot pointer.
An independent native candidate call still produces Quin, establishing that
capacity, not lost character eligibility, explains the missing offer. Actual
results playback grants no recruit or accepted-history bit, preserves every
non-AP unit byte and all extra AP/preferences, and retains Silvril. Closing the
result also awards ordinary equipment AP; those native AP bytes are recorded
but are not misclassified as unwanted ownership changes.

The paired scenario restores the authenticated result checkpoint with one
declared vacancy in slot2. It does not simulate a player dismissal. The native
vacancy scan finds exactly `02000290`. With fixed controller-boundary RNG seed2,
the game renders Quin's offer. Actual Yes acceptance fills slot2, preserves the
other23 complete native records against the full-case reward output, retains
all other extra AP/preferences and the original reward, and commits history.
Fresh normal Save/Continue preserves all24 records, AP, preferences and history.
Root inspected the native Quin offer and returned world scene. No recruitment
or capacity code changed.

The accepted phase chain ends in run `20260917T054114.146509Z`,73 recorded
assertions, with report `full-clan-recruitment-20260917T054114.907138Z/report.json`.
Cold SRAM SHA1: `6212a5c25dcd24254c27b381877624e455e90a30`.
Earlier reports remain failed:

- `20260917T053657.545346Z` and `20260917T053811.884663Z` incorrectly expected a
  full-clan offer. Native code inspection corrected that premise.
- `20260917T054007.503070Z` correctly observed refusal but incorrectly expected
  result closure not to award native equipment AP. Ownership comparisons now
  isolate that reward and compare every other byte.
- `20260917T054056.386634Z` completed full-capacity and vacancy checks; seed0
  was a normal failed offer at the controller boundary. The previously known
  controller witness seed2 succeeds. Only the unfinished offer/accept/save
  suffix reran; the ending, full-capacity branch and vacancy preparation did not.

Use `test-full-clan-recruitment-cached` for full reproduction or
`test-full-clan-recruitment-resume` for unfinished phases. Checkpoints retain
state, RAM and separate SRAM hashes. Final label/provenance cleanup changes no
inputs or game behavior, so accepted runtime evidence is retained.

V02's named storage/ownership boundaries are now covered alongside its retained
job-specific cold/expiry/copy proofs. Sorted deployment subsequently passes27
checks in [`vanillaplus-final-paths.md`](vanillaplus-final-paths.md). Shara's
complete scene remains V06, and assembled final acceptance remains R02. These
ordinary recruitment checks do not establish every special scene's controller.
