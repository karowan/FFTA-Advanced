# Validated palette-bank reuse; battle acceptance still open

September 17 local / September 18 UTC. Previous checkpoint: `451278a`.
The retained private candidate is `4cf2dcb9f5e96bfc9928770eb929e36dcd2e5690`,
resolved by `build/art/live-palette/poc.json`. Its rebuild uses 154108 ROM bytes
and the unchanged 8060-byte state inside `0203D000..0203F000`.
Parent `0fa7d170` and packaged `a6d883b5` remain unchanged. No artwork, external
provider, game window, launcher or player-save change was made. All G gates remain
open. The user wants technical integration completed before final sprite work.

## Changes

The planner can reuse a previous single-owner bank only after validating the
current complete OAM frame. It rejects different owners, unsupported layouts,
native 4bpp conflicts and every potentially visible 8bpp pixel using that bank.
Bank zero with an 8bpp consumer and multiple custom owners use the full planner.
No palette or OAM writes happen before validation. The old occupied-bank field
remains the last full-plan diagnostic on reuse; it is not a fresh demand mask.
Heap reset invalidates the prior requested mask.

The 8bpp path scans contiguous visible source-tile rows. Entire off-screen tiles
can be excluded; partially visible tiles remain whole. Flips are accounted for;
affine and mosaic objects keep their complete source footprint. The bounded ARM
helper uses exact byte-bank comparison, with a whole-zero-group shortcut valid
only for nonzero proposed banks. It preserves callee-saved registers. Separating
this path keeps disabled/4bpp OAM handling small.

The ownership bridge now filters enabled jobs and collects original bank masks
while publishing authenticated tags. This removes a second 128-entry traversal.
The original complete-tag API remains available and is independently compared
with the filtered output. Original native OAM/source validation is retained.

Only banks about to be overwritten are backed up, after successful validation.
Restoration reads only those banks. Untouched entries in backup storage are not
current palette observations. The fade test now reads an untouched native bank
directly from hardware, and an overwritten native bank from its current backup.
This preserves the exact original interpolation oracle and phase requirement.

Battle input duration is explicitly selectable as 8 or 16 frames. The new
`test-live-art-palette-battle-short-input` declares eight-frame presses. The older
16-frame scenario remains available and is not responsiveness acceptance.

## Passing evidence for the retained candidate

All runtime used the declared plan and `Test Expansion.ps1`. No broad suite ran.

| Test ID | Runner | Checks | Component report under `build/art/` |
| --- | --- | ---: | --- |
| test-live-art-palette-native | 20260918T054010.186342Z | 1128 | live-palette/native/20260918T054010.788257Z/report.json |
| test-live-art-palette-transitions | 20260918T054010.186342Z | 2933 | live-palette/transitions/20260918T054013.241598Z/report.json |
| test-art-palette-owners | 20260918T054010.186342Z | 496 | palette-owners/20260918T054020.899584Z/report.json |
| test-art-palette-plan | 20260918T055144.534333Z | 32089 | palette-plan/20260918T055145.130850Z/report.json |
| test-live-art-palette-fades | 20260918T054245.823146Z | 610 | live-palette/fades/20260918T054246.448086Z/report.json |

Planner controls cover all 15 proposed nonzero banks, all 16 pixel banks and
every byte position in a 64-byte tile; exact backups; no-write refusals; clipping,
flips, affine/mosaic input; and changed pixels that require reallocation. Reused
original interpolation and queued-upload evidence remains scoped as before.
Transitions cover 571 paired frames; maximum observed display-enable line is 205.
After rejecting a slower trial, the builder reproduced byte-identical `4cf2dcb9`;
the applicable same-ROM runtime evidence was reused without another route replay.

## Battle is still failed

Runner `20260918T054245.823146Z`, component
`live-palette/battle/20260918T054254.715222Z/failed.json`, completes actual
deployment, three-cell Move and cancel with eight-frame presses and 8460 earlier
successful assertions. It then fails strict native-shadow equality at ready.
This is not full battle or responsiveness acceptance.

`scripts/audit-live-art-battle-trace.py` evaluates every retained paired sample,
including assertions that follow that first failure. Its derived
`trace-audit.json` pins both source evidence and analyzer hashes. It creates no
fixture and runs no emulator. The audit remains **failed**:

- All 1205 samples have an active generated overlay, exact latched generated
  hardware colors, intact reservation fence, matching canonical units and input
  schedule, no ownership/allocation failure and no scan/display wrap. Maximum
  display-enable line is 207. These are bounded observations, not overall success.
- All 1205 samples fail strict native-shadow and unowned-hardware equality.
  Differences are confined to native color indices 162..175 and 418..424.
  The old seven-color-cycle lead remains unresolved; no phase waiver was added.
- Move interpolates from frame 51 to 174 in the parent (123 frames), versus
  49 to 184 in the candidate (135 frames). This is approximately 9.8% slower.
- Cancel restores position at frame 49 in the parent and 61 in the candidate:
  a 12-frame response delay. It is a position restoration, not interpolated travel.
- The unsupported-binding counter is already 147 at ready and remains 147 on
  return. Earlier native-bank variants remain unfinished; the successful button
  sequence does not accept those entry consumers.

## Retained failures and rejected trials

All paths below are component directories under `build/art/`.

| Candidate | Runner | Evidence and result |
| --- | --- | --- |
| 8e8497d6 | 20260918T052929.210095Z | battle/20260918T052940.452284Z/failed.json: eight-frame deployment/Move/cancel reaches strict-shadow failure; motion still slower. Native/transition checks passed. |
| a77a72dc | 20260918T053536.826199Z | battle/20260918T053537.472565Z/failed.json: scalar tile-helper and selective backup trial still fails shadow comparison; 143 movement frames versus parent 123. |
| 4cf2dcb9 | 20260918T054135.367570Z | fades/20260918T054135.981710Z/failed.json: test incorrectly reads an untouched bank from the now-partial backup. Corrected observation passes the unchanged exact fade oracle. Runner stopped before battle. |
| 4cf2dcb9 | 20260918T054245.823146Z | battle/20260918T054254.715222Z/failed.json: current retained failure and complete audit above. |
| 3d3fb457 | 20260918T054743.419259Z | battle/20260918T054744.131188Z/failed.json: exact row-cache trial still takes 135 movement frames; maximum display line 216 versus retained 207. Removed. |

The rejected row-cache trial passed 32089 planner and 2933 transition checks in
runner `20260918T054610.004260Z`. Its steady menu sample improved slightly, but
maximum menu line rose to 211 and actual battle did not improve. The full-byte
row-comparison helper and reuse path were removed. The older full-planner tile
cache remains; it is separate from the rejected preferred-path row cache.

## Next work

Resolve the remaining battle execution cost and establish the actual native
color-cycle ownership/phase behavior. The current audit prevents the first palette
failure from hiding timing or restoration defects. Do not normalize native colors
merely because they resemble rotated tables. Any move of palette-demand work away
from each refresh needs authenticated graphics-write and OAM lifetime coverage.
Then finish variants, unsupported color operations, scene/heap capacity and the
remaining native asset consumers before promoting or packaging. Final sprites
remain deferred; use built-in imagegen when artwork creation resumes.
