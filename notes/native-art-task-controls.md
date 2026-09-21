# Native palette cancellation and task controls

September 18, 2026; follows `2fb261e`. Private candidate
`debb7445d019137eb3a4ffddc9b6b32f3046ed11` resolves through
`build/art/live-palette/poc.json`. Stage159948 bytes; transient state8096 bytes
within the existing8KiB reservation. No installed package, save, launcher or
player session changes. Built-in imagegen only; production sprite refinement
remains deferred while technical integration is completed.

## Authenticated native behavior

- `08146DC8(first,last,typeMask)` truncates arguments to16 bits. It considers
  active state1 tasks whose type is contained in the mask. Fully covered tasks
  are deleted. Overlap at an end trims that end. A cancellation strictly inside
  a task deletes the whole task because the native operation cannot split it.
  Paused state2 tasks are not selected.
- `08148498(handle)` removes a supplied task. `08148540()` removes all tasks.
  Both return their caller's continuation in r0 as an incidental native ABI
  behavior; the wrappers preserve it.
- `081484CC(handle)` collects a completed task and returns0; active or paused
  tasks return their handle. Null returns0. It does not force completion.
- `08148518/0814852C` pause/resume one task; `08148588/081485AC` pause/resume all.
  These original functions need no replacement. The real dispatcher stops
  callbacks while paused, so generated interpolation also stops.
- **Correction to the preceding checkpoint:** `08148738/0814873C` are identity
  functions (`BX LR`), not global task selectors. The builder authenticates
  both bodies. The deletion trampoline omits the displaced identity call while
  reproducing its register result and stack behavior.

Four authenticated entry hooks preserve the original list/heap operations.
Deletion retires attached generated handles. Cancellation scans surviving
handles and retires bindings wholly outside the shortened range. The native
callback passes its current first/last colors to the generated fade step.
Only the intersecting colors and interpolation errors advance; excluded colors
remain frozen even on the final step. Native transparent-index skipping remains
unchanged. No additional persistent state or save schema is introduced.

## Reproduction and acceptance

Build the private candidate with `scripts/build-live-art-palette.py`. Run the
following declared IDs through `Test Expansion.ps1`, with
`-Plan scripts/native-art-test-plan.json -Only` and the selected ID list. Announce
purpose/IDs before runtime. Do not edit inputs while a run remains live.

Runner `20260918T092713.995873Z`, all passed:

| Test ID | Checks | Private report under build/art |
| --- | ---: | --- |
| test-native-art-task-controls | 40352 | task-controls/20260918T092714.705829Z/report.json |
| test-native-art-palette-binding | 32 | palette-binding/20260918T092731.947456Z/report.json |
| test-native-art-fade-contract | 7284 | palette-fade/20260918T092732.222273Z/report.json |

The new component uses the retained authenticated battle RAM/IWRAM fixture
from `20260918T075021.733381Z`. It runs the installed and original ARMv4T code
on TI925T, with a separate original-engine oracle receiving generated colors.
Its432 cases cover18 controls, native banks0/9, both stack alignments, cancellation
after0/4/16 ticks and transparent-index flags. Two-bank ranges verify one bank
can stop while another continues. Every callback compares native palette/task/
heap state, generated colors, contiguous display storage and outside gameplay
RAM. New white fades verify task-slot reuse and nested setup cancellation.
Callbacks are explicitly driven here; this is not scheduler evidence.

Runner `20260918T092946.003326Z`, all passed:

| Test ID | Checks | Private report under build/art |
| --- | ---: | --- |
| test-live-art-task-controls | 2013 | live-palette/fades/20260918T092946.644608Z/report.json |
| test-live-art-palette-native | 1151 | live-palette/native/20260918T092954.973337Z/report.json |

The live mode applies actual control commands on paused-state clones, copying
back only declared native palette/effect and private art state. Actual mGBA
callbacks and DMA then run. Ten scenarios cover cancellation, partial trims,
middle removal, direct/all deletion, active/completed collection and single/all
pause-resume. Paused colors, targets, errors and remaining duration are checked.
All controlled hardware samples match the independent original-engine oracle
at the native display phase, with paired native/unowned colors and units intact.
Final restore confirms eleven starts, seven completions, four cancellations and
no refusals. Source save bytes remain unchanged. Native acceptance rebuilt the
candidate byte-exact and authenticated the four additional patches.

Visually inspected `candidate-control-lower-21.png`: the intentionally partially
cancelled black fade renders in the expected menu with legible unchanged native
labels. It is a technical effect proof, not approval of the draft character art.
No failed run occurred in this batch. Prior timing/phase failures remain open.
Applicable table-color/late-entry/reload evidence from preceding checkpoints is
reused; no broad suite was justified for these bounded controls.

## Remaining work

Inspect native palette heap destruction `08147A2C` and separate constructors
`08146FB8/08147068/08147124/081471E0`, including their callbacks, rotation and
copy consumers. Prove naturally triggered scene/heap/stack lifetimes and maximum
mixed-class capacity. Existing battle timing/response failures, arbitrary
transformed source-table identity, remaining asset consumers, final art and
packaging remain open. None of G01–G04 is closed by this checkpoint.
