# Connected native ending scenes

## Selected verification

`test-campaign-ending-scenes` and its prerequisite
`verify-integrated-assembly-prerequisites` exercise the original transitions
from scene101 through scenes102,104,105, credits, the actual ending-save
opcode, reset/Continue and a cold load on the unmodified current candidate.
The initial queued scene is explicitly replaced once by101 from an authenticated disposable
ordinary save; final-battle victory and natural eligibility for scene101 are
outside this test. Native script ranges are compared with the clean image.
Instrumentation observes original callbacks and injects only the declared
initial scene queue. Fixed inputs and a bounded frame count drive playback.
No clear result is injected. Existing clear-save/postgame evidence is reused.

Before that runtime selection, `build-integrated-jobs` refreshes provenance
after the user-approved resource guard, pruning and emulator cleanup changes.
Its six declared assembly steps are build-samurai-private,
build-job-state-private, build-chemist, build-dark-knight, build-viking and
build-integrated-jobs. This is a source assembly check, not a broad gameplay
rerun; the candidate must retain SHA1
`1b070824a8dad4995434eee3ab40fa08187a6120`.

The pruning dry run retained the current candidate, all plan-referenced
candidates and the latest reproducibility workspace; it selected zero files.
Resolved pruning roots were checked for containment and linked directories.

## Result and retained failures

Run `20260917T110458.392835Z` passes both selected steps. The ending consumer
takes32.3seconds and passes14 assertions. Native scenes execute in order
101,102,104,105, with19 credit instructions and exactly one original
ending-save instruction at `0x089B83CA`. Its real parent context is
`0x020163A4`; the native save controller reaches state0x106 and resets to
title. Same-core Continue and cold loading on the unmodified candidate preserve
the full24-slot expansion profile and clear flag54, retire transient expansion
records, and leave the cleared flash unchanged. The source save is unchanged.
Root visually checked the snowy-town scene, clear-save notice, title and cold
world captures. Existing loaded-clear postgame consumer checks remain applicable.

The private report is beside the candidate under
`ending-scenes-20260917T110459.056443Z/report.json`, SHA1
`13e138e2c9fc9ab977c4087afb71e293959bbd09`. Script SHA1 is
`e5cb244449f183ef3feb92c653df421faeea0c6a`; test-only image SHA1 is
`c577389f0f86b540ef6791f735e8ca19b2210c76`. The report records authenticated
producer data, helper hashes, every fixed input and capture hashes.

Run110153 failed before runtime: an unchanged-script assertion included unrelated
scenes with existing expansion edits. It was narrowed to the actual ending
scripts and lookup tables. Run110257 failed its115200-frame bound because
calling the scene queue from a flag reader let normal world event selection
replace that queued scene. Its traces show162,13,162, never101. Both failures
remain recorded. The corrected probe substitutes101 at the next native queue
call, executes the displaced PC-independent prologue, and delegates all later
calls unchanged. An early bound now rejects failure to enter the declared scene.

The assembly refresh run `20260917T110103.919228Z` passes all six steps and
reproduces the same candidate. Resource containment was active with no threshold
override. No shipping code or player save changed, and no broad suite ran.

## Limits and reproduction

The test replaces one initial scene selection. It does not prove natural entry
from final-battle victory, the preceding battle chain, earlier territory/story
connections or special recruitment. Thus A01/V06 and final R02 acceptance stay
open. Do not rerun the accepted chain just to regain context: authenticate its
report and captures and test the remaining entry path separately.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-campaign-ending-scenes
```
