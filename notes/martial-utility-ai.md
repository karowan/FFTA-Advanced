# Martial utility AI

Updated September 16, 2026 Pacific. This closes the defects below, not the
whole A06 audit or final expansion acceptance.

Current candidate: `8b31d4918e8bdf2c161e4adbbc102dd6637e3e7d`, shared base
`b26778520203359c3b129bcc025b92dd0e4c01f1`.

## Implemented behavior

Both native recipient-row and area-score consumers now value the remaining
benefits of these six commands. Empty utility rows are cleared, including
residual native values on Petrified recipients. These are planning weights;
the approved effect strengths, durations, costs and execution remain intact.

| Command | Useful benefit, before recipient sign |
| --- | --- |
| Murasame | Twice actual capped HP restoration |
| Kiyomori | 20 each for missing Protect and Shell |
| Dark Mind | Twice actual capped self healing, plus 20 for missing Shell |
| Last Resort, self | 20 if its owned buff is absent; zero for a refresh |
| The Blackest Night | 20 if its owned ward is absent |
| War Cry | 20 if its owned resilience is absent, plus 20 each for present Blind, Silence and Confuse |

Healing uses the small execution formula, including Centered, Recuperation,
Composure, fractional bases and missing-HP caps. It does not nest a second
full native forecast inside placement. The test explicitly respects the one
Support slot: self Dark Mind cannot combine Recuperation and Composure.

Last Resort's hostile row previously subtracted its actor buff as though it
benefited the enemy. Remove the native Sure status-stage subtraction and add
20 only for a new actor buff, retaining the original native strike/hit value.
The area scorer already excluded that false recipient benefit. The independent
control removes only the buff descriptor in private emulator memory and runs
the original native row and score functions. Production bytes are restored.

War Cry now has native selector11 (self allowed). C241C otherwise drops its
self AI row even though execution's self-centered cross already includes the
caster. Its existing Silence bypass remains.

Pure custom buffs use a single beneficial-status category in AI rows; their
real descriptors remain unchanged. Native C35D6 now recognizes useful self
Last Resort, TBN and War Cry after the original common restrictions and row
willingness check. Their own state determines usefulness. They no longer
inherit Protect's unrelated existing-status test or its additional random
10% self / 50% ally heuristic. Original statuses, Kiyomori and every other
command retain the original filter. Discovery and row consideration
probabilities are not inflated.

The inline hook preserves the native frame and live registers at both stack
alignments. No RAM reservation, save schema or new allocation is introduced.
All movement/placement coroutines are still native. An initially proposed
replacement search was discarded after testing the real constructor proved
it unnecessary.

## Deterministic evidence

Run runtime checks only through `Test Expansion.ps1` with the integration plan.
Each report lives under `build/expansion/test-runs/<timestamp>/`; observations
live beneath the exact candidate directory. Raw logs, captures and ROMs stay
ignored. Every abbreviated timestamp below has the `20260917T` prefix.

- `013902.515032Z`: assembly, one exact capture, 2,470 recipient assertions
  across 264 cases, and 411 placement assertions across 66 cases pass. Its last
  filter harness step failed because its own state-reading helper overwrote
  registers before the inline call. The source hook did not cause that error.
- `014018.451754Z`: corrected filter harness passes 2,076 assertions across
  96 cases. It checks real continuations, live registers, both stack alignments,
  query purity, existing Protect versus missing custom benefits, redundant and
  invalid cases, and exact original fallback for unrelated actions.
- `014038.266495Z`: 64 assertions over three actual autonomous casts pass:
  Last Resort seed 5, TBN seed `0x12345678`, and Silenced War Cry seed 5. Native
  effects, exact MP/HP payment, self mode, renderer code and handoff pass.
- `014221.458945Z`: Kiyomori's bounded seed sweep passes 35 assertions.
  Seed`0xdeadbeef` completes without casting; seed `0x87654321` casts and grants
  Protect and Shell to the caster, pays 10 MP and returns control. The sweep
  stops there. Future ordinary runs pin the successful input rather than
  repeating discovery. Its negative first case remains in the report.
- Retain the successful Dark Mind case from `012810.436656Z`, candidate
  `674ebdd2add216e470cde12eefbeadfc20cfc294`: actual self Shell, 100 HP recovery,
  8 MP cost, renderer preservation and handoff. That overall report failed
  for other commands and is not relabeled as passing. Later code changes
  affect the three custom-ward filters, not Dark Mind's tested behavior.

The current native checks total 4,957 assertions. Current playback contributes
99 assertions across four positive casts and one no-cast control; the retained
Dark Mind case is separate evidence. This is not a single five-cast current-ROM
run or full integration pass.

Reproduce the native group with:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only @('test-martial-utility-filter')
```

For a matching assembled image, use `test-martial-utility-ai-cached`,
`test-martial-utility-search-cached` or `test-martial-utility-filter-cached`.
`test-martial-custom-ward-turns-cached` and
`test-martial-kiyomori-turn-cached` replay the corresponding fixed subsets.
`test-martial-utility-turns-cached` declares all five fixed positive scenarios
for a later assembled acceptance gate. Preserve applicable evidence instead of
rerunning the whole group for a documentation edit.

## Diagnostic history and limits

The initial `010702.350834Z` audit exposed redundant scores. The subsequent
matrix and compiler failures remain in their reports. Placement originally
guessed a callback and guarded a region containing its own artificial test
stack. Corrected tests use actual C01D0 construction, its returned callback,
and the low-stack arithmetic guard. The real playback separately guards the
renderer. A published beneficiary coordinate alone is not proof of an
executed area center. Native search control `012508.355845Z` showed all 66
placement scenarios already work with the original coroutines.

Pinned native traces `012944.806235Z` distinguish command discovery from the
later application filter. The diagnostic script intentionally requires its
recorded 674ebdd candidate and captures and is not a release test. Initial Kiyomori
seeds 0..31 failed discovery (`013050.912737Z`); a wider seed diagnostic found
admission at `0x12345678` (`013208.907190Z`). Admission alone did not establish
a cast: the later native Protect/Shell heuristics remain. The final bounded
playback sweep supplied actual positive evidence without changing them.

The intermediate 89a29c candidate only normalized custom kinds. Its
`013356.383782Z` playback still failed; the final custom-state filter addresses
the distinct native Protect policy problem. Keep both failed reports.

No full integration, cold save or campaign replay was run for this group.
A06 remains open for medicine, further ordinary attack/status decisions,
broader hostile Last Resort weapon/support combinations and shared-support
interactions. Murasame has this group's native row/placement evidence and
retained execution coverage, not a new autonomous turn in this playback set.
Final mixed-job, campaign, acquisition and release acceptance remain on the
maintained checklist.
