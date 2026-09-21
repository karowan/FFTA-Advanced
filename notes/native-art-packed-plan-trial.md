# Direct current-demand palette planning: response still fails

September 18 Pacific / September 19 UTC. Full engineering remains required;
only artwork and artist-authored frame content are deferred. E01-E05 remain open.
Candidate `94770ae82551ba0bee8a535b80bb2446e0f1b087` is private and unaccepted.
Its selector is `build/art/performance/packed-plan/current.json`. No player-save,
installed package, action/default selector, launcher, agent or publication change.

## Implementation and exact scope

Optional `packed_plan=True` requires private fused composition and twenty history
slots. The trial builder combines it with the previously proved unrolled scoped
copies and the mandatory final action-completion stage. Default palette rebuild
still reproduces installed palette `fa3d12b4` byte for byte.

When freshly authenticated same-invocation demands contain no 8bpp consumers,
`plan_four` constructs the original full palette plan using five word stores for
the twenty bank entries. Allocation scans available banks monotonically instead
of restarting at bank zero for each history. All lower available banks have
already been allocated to earlier histories, so ordering is unchanged. Failure
remains atomic: no plan or hardware writes occur until every requested history
has a bank. Reserved fields and untouched structure padding match the original.

The existing single-owner preferred-bank validation runs first, preserving its
diagnostics and disabled-object behavior. Any 8bpp demand keeps the complete
existing pixel-scanning planner. Native highlights retain their existing separate
classification route. No demand, plan validity or pixel evidence is cached across
frames. Output uses the same native palette backup and scoped publication code.

The final ROM stage grows 192 bytes over `0cca3494` (252344 bytes used). The
11316-byte state, 12 KiB reservation, menu root and all scoped ARM leaf bytes,
stack sizes and minimum stack addresses remain identical. Metadata paths/compiler
commands differ because these are distinct builds; leaf records compare exactly.

## Correctness and retained failure

All checks use the declared native-art plan through `Test Expansion.ps1`.

| Runner, prefix 20260919T | Exact ID | Result / child report under build/art |
| --- | --- | --- |
| 045835.661065Z | test-art-packed-plan | Failed cache comparison; build/consumers/entry skipped |
| 045915.929253Z | test-art-packed-plan | 4744 pass; frame-high-slots/20260919T045916.682408Z/report.json |
| same | test-art-packed-build | 8 pass; performance/packed-plan/20260919T045917.771120Z/report.json |
| same | test-art-packed-consumers | 244 pass; fused-consumers/20260919T045932.214668Z/report.json |
| same | test-art-packed-entry | Failed raw ready palette-shadow equality; live-palette/battle/20260919T045933.050297Z/failed.json |
| 050030.614641Z | test-art-packed-frame-events | 31105 pass; native-frame-events/20260919T050031.263170Z/report.json |
| 050321.362693Z | test-art-packed-phase-evidence | 6226 pass; native-phase-evidence/20260919T050322.190575Z/report.json |
| same | test-art-packed-response-budget | Six metrics fail; response-budget/20260919T050322.679604Z/failed.json |

The first failure was in a newly strengthened test oracle, not ROM behavior.
The test added the complete 2124-byte pixel cache to output comparisons but
reused the first invocation's expected cache for a subsequent invocation with
an already valid preferred plan. The first full plan populates cache data;
preferred-plan reuse can leave the initial cache untouched. Case 12 therefore
failed on the second initial-plan variant. Each case now executes the original
reference planner from exactly the same initial plan/cache as the trial.
Complete cache equality is retained, not removed. The failed log remains intact.

The enlarged differential covers 36 deterministic native-bank masks (including
exhaustion, only one free bank, alternating masks and a fixed random sample),
four requested-history groups, IDs through 19, invalid ID 20, invalid custom
counts/mapping, omitted-tail bank zero, a full 128-object frame, disabled objects,
8bpp/affine/mosaic/clipped cases, both stack residues and deep/external fallback.
It compares full OAM, palette, plan including padding, backup fences and cache
against the original planner. This is a bounded matrix, not every possible mask.
The complete compositor differential also checks split histories, highlight
fallback, skipped-DMA phases and unrelated RAM against the original native bridge.

All 1024 complete emulated states and frames in the instruction-observation run
match ordinary execution. Its current demand validation and phase proof remain
separate from the entry failure and response gate. Later assertions in the entry
test are skipped; neither another green test nor timing improvement waives them.

Trace SHA256:
`9ef312213a76f874288b74396b6940a753253f27b22283dc5d6669894aa22fe1`.

## Measured result

| Input offset | Action | Active start/end/duration | Same-ROM bypass |
| ---: | --- | --- | --- |
| 0 | Move | 24/71/47 | 24/70/46 |
| 4 | Move | 25/72/47 | 24/71/47 |
| 0 | Cancel | 31/31/0 | 29/29/0 |
| 4 | Cancel | 30/30/0 | 30/30/0 |

These are the same failing response metrics as the unrolled-copy trial. Mean
composition drops to 15.512/15.603 scanlines for Move and 14.336/14.278 for cancel,
from about 15.84/15.93 and 14.70/14.65. Peak remains 31.071 lines. The modest
cycle saving is not a visible regression fix or acceptance.

Recorded current demands have zero 8bpp consumers on 104/103 of the 128 Move
frames and 118/119 cancel frames at offsets 0/4. Full `plan_inputs` runs on the
remaining 24/25 Move and 10/9 cancel frames. At offset 0, those full-plan calls
average 12.270 lines for Move and 12.124 for cancel; their nested exact bank-span
scan averages 9.868/9.719 lines. Do not add nested timings together. This isolates
the remaining expensive frames; the new path is actually exercised.

## Next work

Do not promote this candidate or waive the six response failures. Inspect the
exact 8bpp bank-span scanner's cached-byte comparisons, cache-miss scan/copy and
scoped copy on peak frames. Preserve complete current-byte verification and the
original transparent-index and clipping semantics. Avoid prior-frame validity
assumptions. The reusable scanner differential is `test-art-palette-plan.py`
with the explicit fast-bank-scan option; declare any new runtime selection first.

Continue current action/effect/UI, demanding native capacity, campaign/save and
final package acceptance without restarting passed job implementation. The
current action candidate remains `5a14e6c7`; installed `7507ca5c` is unchanged.
All runners and cleanup are terminal.
