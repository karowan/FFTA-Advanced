# Dark Knight implementation handoff

Branch `jobs/dark-knight`, isolated checkout `.worktrees/dark-knight`.
This is an implementation checkpoint, **not complete Dark Knight acceptance**.
The root coordinator will finish integration and all subsequent work alone.
No player save or visible game session was used. All ROMs, captures, object files
and emulator/compiler binaries remain local ignored assets.

## Verified boundary

Last accepted job source: `528ba47`. Its candidate is
`80ef51a56201086805c633c8aa44e218bdb80b3f`, composed over saved-state candidate
`02d4fee3f935e410e2c88d1d41ce91f7ff03fcbf` and Samurai
`7bd9b8b51c67769e16c5a896c6a31f0f3b4c9d5e`.

- `20260915T051632.757302Z`: eight steps passed, including shared action context
  2,777 native checks and both-race Unholy menu/cancel/payment/cold-save replay.
- `20260915T052002.828844Z`: ten steps passed, including Dark Mind/Blood Edge
  regression, 512 sword-rider native cases, query purity/help and both-race
  Crushing Blow replay. Each sword replay uses 128 fixed native-entry seeds.
- Exact-entry RNG seeding and the observed A822E return replaced an invalid
  extra menu-confirmation input. These tests do not inject outcomes.

Current batch is separately unaccepted. Translation-unit compilation passed
`20260915T055859.543740Z` after the final source edits. Consolidated build attempt
`20260915T055633.283131Z` reproduced the shared bases but stopped at missing
`ffta_action_unit_at`, because the reaction-queue prerequisite is not adopted.
There is no successfully linked current-batch ROM hash to claim.

## Lesson coverage

| Lessons | Current implementation and evidence |
|---|---|
| A1 Blood Edge356 | Accepted physical Dark coefficient, primary-sword gate, paid HP, native execution and both races' menu/cold-save coverage. |
| A2 Sanguine357 / A3 Infernal358 / C1 combo129 | Existing foundation retained; whole-job laws/AI/cross-class/copy acceptance remains. |
| A4 Dark Mind359 | Accepted native Shell plus capped self-heal, weapon-free, Silenced use, native execution/menu/cold-save. |
| A5 Last Resort360 | Batch: strike/self mode, after-paid completion buff even on miss, indivisible saved T2 state, one-product factors, cleanup and icon. Not yet accepted. |
| A6 Crushing361 / A8 Unholy363 | Accepted native physical damage then actual-HP-gated Stop/Slow; costs, accuracy/query guards and both-race replay. |
| A7 Abyssal362 | Not implemented. Needs proven prospective origin-to-magnitude bridge for line falloff; do not use stale F6/F7 or resolve live actor by identity. |
| A9 TBN364 | Batch: ally/self action, additive HP/MP payment, exact caster token, saved ward, cleanup/icon and whole-action reduction. Zero-rounded damage consumption remains unresolved. |
| S1 Desperation130 | Batch: action-start equipment, post-cost threshold35%, native/custom physical and magic one-product factors, MP/reaction exclusions. Deterministic threshold/rounding test authored, not accepted. |
| S2 Bloodcasting131 | Batch: native computed MP lookup converted to2HP, additive DRK sacrifice, nonlethal admission and payment. Multiple subcasts and native staged self-cost aggregate reservation remain unresolved. |
| R1 Dark Ward130 / R2 Vengeful131 | Batch consumers and hidden native result actions433/434 authored. Depend on Chemist's independently accepted queue release; no invisible direct HP/Shell completion write. |

Existing job/equipment/AP/acquisition records are retained for both races.
Allocated lesson records do not establish complete behavior, laws or AI.
The help bank adds descriptions for the six implemented action rows and four
support/reaction rows; old text and routes are preserved by the native text test.

## Merge contract

All DRK writes are within ROM offsets `0x1200000..0x123ffff`, with erased-byte
checks. Code must end before `0x1228000`. The global action table moves to
`0x1228000`: 436 rows preserving all original432 and rebinding the17 known
native literals. Only hidden433/434 are filled locally; root must compose432/435.
Descriptors at `0x122c000` have220 rows: DRK213/214/216/217/219.
Applications97/98 and their masks move to `0x122c400`/`0x122cc00`.
Root must compose other jobs' banks, not overwrite them with this private bank.

Persistent DRK state owns only shared job-record bytes0..3:
byte0 is LR remaining1/2 plus application-turn skip4; byte1 TBN caster token1..36;
byte2 active0/1; byte3 reserved. Use `ffta_job_state/origin/peers` exclusively.
Missing same-owner peers do not imply expiration. Canonical roster token remap
already understands TBN source byte1. No private saved RAM is added.

Snapshot bits13/14 are Desperation;22 LR;23 TBN;24 reserved consumption latch;
27 DarkWard-ready;28 Vengeful-ready. Claims32 TBN,64 DarkWard,128 Vengeful,
512/1024 successful queue admission. Bit24 currently has no completed claim
implementation; do not mistake its reservation for the zero-rounding fix.
Status keys28/29 use tiles1E6..1E9. The dynamic tile pool moves to1F0 once.

Outgoing factor denominator8 combines Desperation3/2 and physical LR5/4.
Incoming denominator40 combines physical LR6/5, enemy TBN1/2 and magical
DarkWard3/4. Combine these with Poise/Ward/Exposed/Viking/Composure **before one
division**, not rounded sequential multipliers. Native actual MP redirection
keeps all HP-only factors neutral. The current local finalizer is generated
from the accepted Samurai source; root must compose overlapping finalizers.

Checked optional providers bind snapshot flags, beneficial status, paid/action
events, actual HP loss and reaction completion queue. Lifecycle wrappers compose
the prior Centered and Wound functions. Main/Samurai/saved-state call rebinding
is restricted to known code regions and reports every changed call/literal.

Shared queue API expected from Chemist: `ffta_action_unit_at`,
`ffta_action_reaction_kind/value`, `ffta_reaction_queue_append` and padded
`ffta_additional_reaction_queue`. Request kind130/action433 targets self Shell;
kind131/action434 carries immutable fixed damage. Original primary wrapper must
remain separate from self target. Vengeful checks actual completion positions
within Manhattan3; this is not prospective movement evaluation.

## Remaining acceptance work

1. Adopt the accepted shared queue source and rebuild the local shared base.
2. Run declared `test-dark-knight-batch-native`, `test-desperation-native`, old
   accepted action regressions and native help. Fix failures rather than waiving
   them; tests are authored but unaccepted until actual candidate execution.
3. Verify reactions through native output rows/animations, fixed payload,
   elemental immunity/absorption, surviving capability, no recursion, range,
   friendly/MP/DoT/cost exclusions and whole-action multi-target ordering.
4. Implement TBN pre-reduction positive payable admission when rounding becomes
   zero, covering Fight, custom/native magic/physical and pure preview isolation.
5. Implement Abyssal line geometry and proven evaluated-distance falloff.
6. Complete Bloodcasting multi-component upfront validation and native staged
   self-cost sums. Do not classify unsupported second components as free.
7. Complete beneficial law predicates, custom status native AI/query behavior,
   legal cross-class UI/AP/acquisition/equipment matrices, new status visuals,
   native save/cold-copy/reorder and full assembled regression.

Commands run from this worktree:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/jobs/dark-knight/test-plan.json -Suite dark-knight -Only compile-dark-knight-batch
& '.\Test Expansion.ps1' -Plan scripts/jobs/dark-knight/test-plan.json -Suite dark-knight -Only test-dark-knight-batch-native,test-desperation-native,test-dark-knight-help,test-sword-riders-native,test-dark-mind-native,test-blood-edge-native
```

Do not rebuild the accepted main engine from newer sources. Use the local
verified ba1c base and private builders. The test runner records source hashes,
input/output hashes, fixed scenarios and complete logs. Never alter source or
plans during a running test. Compile-only success is explicitly not ROM or
gameplay acceptance.
