# Native palette scan performance and cycle diagnosis

September 17 local; continuation of commit `5733409`. **Technical integration
is incomplete.** Built-in imagegen remains the only requested artwork provider;
final sprite refinement is deferred. No player files, package, launcher, game
session, publication or artwork changed.

Current private candidate: `7e2b8b86dfe33ead7bb5bfbcf4631f1163a4326f`, resolved by
`build/art/live-palette/poc.json`. Parent remains `0fa7d1707e2d85fb2a8602f061b5eb4479ff3211`.
ROM stage uses 154436 bytes; persistent transient state remains 8060 bytes in
`0203D000..0203F000`. Only the unaccepted Dark Knight draft is enabled.

## Implemented performance changes

FFTA hides unused hardware objects with attributes `00A8,00F8,0000`, rather
than setting the disabled bit. This is an ordinary 8x8 object outside the
screen. The retained battle ready frame has 78 such trailing entries.
`object_count` verifies the exact three attributes and absent owner tag before
trimming that suffix. Disabled entries also trim; interior holes, later visible
objects, changed attributes and tagged objects remain checked. Full allocation
still reads all 128 entries, retaining its original bank0 demand and diagnostics.
Preferred bank0 falls back to full allocation.

The ARM pixel predicate now combines four exact byte comparisons before
branching. XOR against the wanted high nibble followed by the byte-less-than16
predicate handles all low nibbles, including subtraction borrows. Transparent
zero groups retain their shortcut. No approximate hash or stale-frame reuse.

The 160-byte position-independent leaf can run from temporary IWRAM stack
storage. The wrapper preserves its registers, copies the complete leaf including
literal pool, invokes it, then releases the image. It adds no persistent memory
reservation. After its 24-byte register push, SP must be between `03007024` and
`03008000`; this leaves the 160-byte image, 28-byte leaf stack and an additional
512 bytes above resident native code ending at `03006D68`. Deeper/non-IWRAM
stacks use the ROM leaf. The assembler rejects growth beyond 160 bytes.

Native IRQ dispatch at `03000FBC` switches to system mode before invoking the
callback; this was statically checked against retained original IWRAM. The
additional margin is conservative, **not proof of every nested-interrupt or
deep gameplay-stack lifetime**. Those remain acceptance work. Retained native
executable bytes `03006170..03006D68` match ROM `A38D24..A3991C` at available
battle snapshots; these snapshots do not cover every frame.

## Evidence on the final candidate

All runtime runs used `Test Expansion.ps1` and the declared native-art plan.
Exact IDs and purposes were announced before each run. This was targeted
palette work, not broad integration acceptance.

| Test ID | Runner | Result and component evidence |
| --- | --- | --- |
| test-art-palette-plan | 20260918T063200.387008Z | 47479 pass; `build/art/palette-plan/20260918T063200.977977Z/report.json` |
| test-live-art-palette-native | 20260918T063232.673856Z | 1128 pass; `build/art/live-palette/native/20260918T063233.266785Z/report.json` |
| test-live-art-palette-fades | same | 610 pass; `build/art/live-palette/fades/20260918T063235.596638Z/report.json` |
| test-live-art-palette-transitions | same | 2933 pass; `build/art/live-palette/transitions/20260918T063243.430264Z/report.json` |
| test-live-art-palette-battle-short-input | same | **FAIL**; `build/art/live-palette/battle/20260918T063251.084932Z/failed.json` |

Planner coverage includes all byte values/lanes in the relocated leaf, the prior
full-tile collision controls, exact sentinel rejection, late enabled entries,
unchanged native code fence and deep/non-IWRAM fallback. The native test rebuilds
the private ROM byte-for-byte. Prior ownership recording and native color-binding
primitive evidence remains applicable to those unchanged implementations.

The complete derived `trace-audit.json` beside the failed battle report covers
all 1205 paired samples, beyond the fail-fast shadow assertion:

- Generated colors exact, all overlays present, no allocation/ownership failure,
  canonical units and input schedule preserved, EWRAM fence intact.
- No scan/display wrap; maximum active display line 204.
- Movement: parent 123 frames, candidate 126 (previous checkpoint 135).
- Move starts at sample50 versus parent51; cancel at60 versus parent49.
- Every pair still differs in native shadow and unowned hardware colors.
  Unsupported variants count149 at ready and return; this is not accepted.

The native IWRAM guard now appears in the offline audit when retained snapshots
and the authenticated manifest are available. It reports exact snapshot paths,
hashes and scope. It does not manufacture per-frame stack coverage or turn a
failed trace into acceptance.

## Native cycle and portrait ownership findings

`test-native-battle-palette-cycle`, runner `20260918T060524.874801Z`, passes264
checks on retained original/4cf2dcb9 states. Report:
`build/art/native-battle-cycle/20260918T060525.459910Z/report.json`.
No campaign route or fixture was recreated. Actual callback `08146865` rotates
only the seven colors declared by each native task: BG162..168 and BG169..175.
All seven rotations occur. Idle at the command menu leaves the cycle list empty
and colors static. Eight-frame A opens Move: cycles resume at sample317 in the
parent versus324 in 4cf2dcb9. Both pause again at529 on cancel. OBJ418..424 stays
at one phase. **This proves native cycle behavior, not permission to normalize
away phase differences.** The OBJ copy's origin remains unresolved.

`test-native-battle-draw-trace`, runner `20260918T061628.557078Z`, passes7 checks.
Report: `build/art/native-battle-draw/20260918T061629.162856Z/report.json`.
One isolated native `08000460` draw call from authenticated parent RAM reaches
the Dark Knight layout `09DC21A4`. High-level renderer `0802D05C` calls priority
OAM renderer `08001CF0` at `0802D0A4`, with fixed tile base `0240`; inner renderer
is `080014C8`. This agrees with actual OBJ VRAM offset4800. The portrait loader
is `0802CE50/0802CE5C` with a queued descriptor, not the separate `080866EC`
HUD path. The latter uses CpuSet into `06014300` and must not be conflated.

These findings identify real consumers; they do **not** prove exclusive portrait
VRAM lifetime or justify reserving banks6..8 without scanning. Direct CpuSet
uploads exist, so queue-only invalidation is insufficient for a general cache.

## Retained failures and trials

- Cycle runner `20260918T060332.196109Z` passed its narrower idle/callback scope;
  its report remains, superseded only for Move/cancel observations.
- `0e9c1b00`: planner/disabled-bit trimming only. Runner `20260918T062037.318520Z`,
  battle `20260918T062047.818479Z`: still135 movement frames, max209; **FAIL**.
- `f6125ffe`: exact native sentinel trimming. Runner `20260918T062405.363377Z`,
  battle `20260918T062415.956620Z`:126 frames, max204; **FAIL**.
- Runner `20260918T062727.025200Z` stopped at assembler `.if` non-constant
  expression. Replaced by a bounded `.org`; failed compile log preserved.
- `78a3dbae`: initial scoped leaf, runner `20260918T062836.460381Z`, battle
  `20260918T062846.935628Z`:126 frames, max204; **FAIL**. Final7e2b8b86 adds512
  bytes of stack headroom and explicit deep-stack fallback coverage.

All previous failures remain intact. Each ROM trial was private; none was
promoted to the playable package.

## Next

Resolve remaining foreground processing/input delay and independently trace the
native OBJ418..424 palette copy. Keep phase semantics and timing acceptance
separate; do not waive one to hide the other. Finish simultaneous native-bank
variants, remaining native color operations and scene/heap/stack lifetimes.
Then complete the remaining asset consumers and reproducible technical package.
All G01-G04 gates remain open; final artwork is still deferred.
