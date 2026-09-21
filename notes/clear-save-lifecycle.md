# Native clear-save checkpoint

Follow-up: [ending-continuation.md](ending-continuation.md) verifies the retained
dialog endpoint through native reset to title and same-core Continue, plus two
postgame mission listings. Native state0x106 deliberately resets; it does not
return to the synthetic parent. The historical observations below remain valid,
but the parent-byte assertion is not the correct oracle for that branch.
Actual final scenes/credits and their connection to this task remain open.

September 17, 2026. The shipping candidate remains
`1b070824a8dad4995434eee3ab40fa08187a6120`. No game implementation changed.

## Accepted scope

`test-clear-save-lifecycle` passes 12 assertions in common-runner run
`20260917T091907.993516Z`; assembly verification and the 9.2-second consumer
both pass. Only those two declared steps ran.

The deterministic script starts with the ordinary early-town save, declares a
24-member test profile, and saves it through native controller input. The
profile contains distinct ordinary/extended AP, preferences, inventory and gil.
These are test inputs, not claims of earned AP or campaign recruitment.

A private instrumented image starts the original ending-save task inside an
active New Game story scene. It retains the previously written SRAM and
restores that save's selected-slot input. The original task reads the selected
slot, prepares cleared state, writes flash, displays Save complete and advances
after dismissal. A fresh core running the unmodified candidate loads that flash
through Continue. Cleared-game flag 54 is present, all compared profile bytes
match, and battle-only expansion state is reset. The original source save is
unchanged. Root inspected the save-complete and cold world captures; the final
cold capture hashes match the earlier inspected capture exactly.

This proves the save transaction and cold-load portion of V06. It does not
prove the final battle, credits, complete ending scene, return to its real
parent task, or postgame mission consumers from this newly cleared save.
The retained task observer ends at state 0x106; its synthetic parent's byte 6
does not become 1. Keep that return path open instead of treating dialog
dismissal as complete ending-scene acceptance.

## Native path and instrumentation

- Flag reader: `0x080C9540`; arbitrary-state flag reader/setter:
  `0x080C95D8` / `0x080C960C`.
- Clear-save preparation: `0x0812C170`, sets flag 54 in staging state
  `0x02003CB0`, not the active game's live flag bank.
- Ending controller: `0x0812C2B8`; constructor: `0x0812C510`.
  Native flash read/write: `0x0813B480` / `0x0813B0D4`.
- The script verifies the original reader, arbitrary-state flag helpers and
  ending controller region against the authenticated clean USA ROM.
- A private flag-reader shim calls the constructor once, then delegates the
  original reader to its byte-for-byte copy. A callback wrapper observes the
  original controller. Both occupy authenticated unused ROM tail space.
  The shipping image is never modified. Cold loading uses that shipping image.
- The event-task scheduler must be active. An idle world menu does not provide
  the scene context needed to execute this task. The ordinary Save UI also
  remains on its slot selector; four B presses return to the world.

## Evidence and reproduction

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-clear-save-lifecycle
```

Private artifacts are under the candidate's directory selected by
`build/expansion/probes/integrated-jobs/current.json`, in
`clear-save-20260917T091908.745148Z/`. The report preserves exact input sequence,
captures, profile bytes, ROM/source hashes and pass/fail result; compiler logs,
script snapshot and SRAM files are retained beside it and ignored by Git.

| Artifact | SHA-1 |
| --- | --- |
| Final report | `caeea467c2af4b202ece2a4716335720c5129e23` |
| Test source | `5588ecf26c9c884995455854aa5e8bae4e17e6bc` |
| Imported profile/owned helper source | `ef19fba1d12153b06e6c17954429a1e09810f739` |
| Private instrumented image | `634d203810e720fdec1ee474bf985c55e8104f09` |
| Original early-town SRAM | `b0199e7490f7c22f84512825a4a1bde08d3b3eec` |
| Native ordinary save before clear | `5ba126d8cb06a7389ad8286fae9a73e884a380f2` |
| Native cleared SRAM | `7171fd22d6e76a094375d12eca8c45441b6881c4` |
| Cold cleared EWRAM | `cac916307e21047016b4ff117c1c0889d8924ece` |
| Cold cleared state | `989529f628276d5403fa49db6ebf9a7371e5bb6e` |

Earlier failures remain failed: 085343 left the save selector active; 085419,
085456 and 091048 lacked an active event scheduler (the observer distinguished
constructor invocation from actual task execution). Run 091205 passed the
nine-assertion save/cold prefix. Run `20260917T091819.018635Z` failed the newly
added synthetic-parent completion assertion. The final test explicitly narrows
its assertion to observed dialog dismissal/transition and retains full parent
return as a campaign gap. None of these results establishes a shipping defect.

Do not rerun this prefix just to update documentation. For an actual ending
consumer, authenticate and reuse its retained cleared SRAM where applicable.
