# ARM object classification: measured but not accepted

September18 Pacific. E01 remains open. Installed7507ca5c and default palette
fa3d12b4 remain unchanged. Both options are private, opt-in and unshipped.

`art-oam-demands.s` classifies all current native objects before pixel scanning:
occupied4bpp banks, requested custom histories and ordered8bpp object indices.
It preserves exact shape/disable/owner checks, uses halfword reads for2-byte
aligned OAM and ignores unrelated affine words. The existing exact pixel
scanner handles each8bpp footprint. No persistent cache or RAM reservation is
added. Scratch is140 stack bytes. The320-byte position-independent ARM leaf
runs in scoped IWRAM when post-wrapper SP is030070D0..03008000, leaving512
interrupt bytes above resident code ending03006D68. Deeper/external stacks use
the identical ROM leaf. Tests check ABI, boundaries and actual execution region.

`arm_oam_scan=True` requires `fast_oam_plan=True`; the combined experiment also
uses exact-byte `fast_bank_scan=True`. Neither uses incomplete DMA tracking.
Default compilation still reproduces the original palette ROM byte for byte.

## Standalone classifier

Candidate318d374170124321e387b2c6f0d92bc4a4a4ed6f. Runner
20260918T235310.764829Z passes contract54123/build8/profile292, then fails
the paired native palette-shadow assertion at ready. Profile totals15394
fresh/15142 repeated instructions. Capture:
`build/art/live-palette/battle/20260918T235326.880805Z/failed.json`.
No actual movement-response acceptance was run for this candidate.

## Combined exact scans

Candidate473a69382a4c14d4cd2da6b1b372563e60d156f6. Runner
20260918T235523.752698Z passes contract67877/build8/profile292, then fails
the paired native palette shadow at ready. Reports under build/art:

- palette-plan/20260918T235524.505810Z/report.json
- performance/arm-full-scan/20260918T235527.734896Z/report.json
- compose-isolation/20260918T235539.864331Z/report.json
- live-palette/battle/20260918T235540.125748Z/failed.json

Fresh isolated instructions13889 versus17928 baseline; repeated13637.
The profile's historical `scoped IWRAM pixel scan` label includes both the
object-classification and pixel leaves. Instruction reduction is not acceptance.

`test-art-arm-full-frame-events` passes5175 in terminal runner
20260918T235635.086501Z. It verifies full native state/framebuffer equivalence
of observation and retains1024 frames. Trace:
`build/art/native-frame-events/20260918T235635.728346Z/report.json`, SHA256
ada9d5289ee109e4a2ddb63b234eb7b6dea4562daa79e49a7160443883ebf89a.

At both input offsets0/4, Move starts24 versus23 and ends72 versus70:
48 versus47 frames of movement. Cancel32 versus30 and31 versus29. Composition
means22.71–24.15 scanlines, versus roughly2.8 with overlay bypassed.

Terminal runner20260919T000201.061557Z reuses that authenticated trace:
`test-art-arm-full-phase-evidence` passes6226, report
`build/art/native-phase-evidence/20260919T000201.794591Z/report.json`.
`test-art-arm-full-response-budget` fails ten response metrics;13 input/
coverage checks pass. Report:
`build/art/response-budget/20260919T000202.099632Z/failed.json`.
This reconciles native color rotations only. Original entry failures and
assertions skipped after them remain explicit. Neither a timing waiver nor
promotion occurred. Continue substantive total-cost/lifetime work, not another
instruction-count-only acceptance claim. E02–E05 also remain open.
