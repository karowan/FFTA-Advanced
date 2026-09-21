# Native Doublecast ownership

## Controller evidence

Native `92784` receives the battle controller (`0200F4E8`) in r0/r8. Command33
is stored at+A6, the two selected spells at+AA/+AC, and the index at+AF.
At `95B18..95B60`, the controller selects the indexed spell/target and calls
`A8194`, which allocates the result container and invokes `A433C` at `A822A`.
These are separate transactions across controller ticks, not nested calls.
The index advances at `95D04`. Native checks at `95D12..95D4E` may cancel the
second cast when the actor cannot continue. Both normal completion and early
termination join `95D66`. The result pointers remain at+4C/+50 until later
native processing/free at `96072..96098`.

The composed hooks authenticate the real `95B60` caller, controller, wrapper,
actor and selected slot. A heap-owned continuation transfers frozen snapshots,
both extension banks, claims and cumulative HP loss between casts. Spellweave
commits at the outer finish;
Magic Shell's opportunity remains claimed across the pair. Queries cannot
modify the carried state. Native spell costs, targeting, damage and reaction
execution remain in their original constructors.

The existing pool's final16 padding bytes (`+2610..261F`) now own a lazily
allocated1,836-byte continuation, including up to64 complete unit records and
64 exact first-result wrapper references.
No persistent save field or additional fixed RAM address is used. Allocation
headers, pool ownership and current heap identity are validated; completion,
stale-owner replacement and manager/pool retirement release the continuation.
This does not enlarge the common pool or allocate anything at game startup.

## Initial verification selection (Mystic-only predecessor)

Changed behaviors: controller constructor/finish hooks, Mystic extension carry,
and optional battle-owner cleanup. Selected IDs:
`test-mystic-knight-doublecast`, `test-mystic-knight-shell`,
`test-battle-workspace`, `test-integration-relocations`, with their declared
native build/capture prerequisites. Static native branch scanning found no
conditional/unconditional branch into either replaced span. Full integration
is deferred. Fresh startup is unchanged because pool size/constructor and
allocation timing before a committed Doublecast are unchanged.

The deterministic Doublecast script executes actual controller call-site
slices, full native spell constructors/executors and the installed finish hook
using explicit captured ABI inputs. It does not inject accuracy, damage or
sequence outcomes. Both stack residues, hit/miss seeds, two costs, both damage
bonuses, Shell lifetime, cancellation and delayed-commit exclusions are tested.

Initial selected run `20260916T084008.253661Z` passed13/13. A targeted extension
now selects only `test-mystic-knight-doublecast-lifecycle` with verified reused
prerequisites: actual pool/manager teardown, cancelled MP payments, malformed
mixed categories and preserved original Doublecast eligibility. Native source
and candidate bytes are unchanged; this selection does not repeat the core
matrix, Shell or workspace suite.

The extension passed2/2 in `20260916T084222.500926Z`. A subsequent source review
identified scratch-register preservation at the mid-function completion hook:
native C95A8 leaves r3/r12 intact. The hook now preserves both and recreates
the original LR; a native-span ablation compares all registers, NZCV and the
phase write. Selected rerun: `test-mystic-knight-doublecast` and
`test-integration-relocations` with the changed-image prerequisite chain.
Other gameplay sources are unchanged, so Shell/workspace matrices are not
repeated for this assembly-only correction.

Final run `20260916T084408.356171Z` passed11/11 on
`8b1ffe992fa9731156ceed1f9de6bc998cdefd42`, with unchanged inputs and an
independently verified image hash. The focused script has1,258 assertions;
the final default includes the added lifetime and exact-ABI cases. Current
Mystic/workspace code is15,384 bytes; central code is32,056/32,768.

## Execution-time pair forecast

Candidate `1bf83980ac3d339e82d862c39148c18d29aa9bd7` includes the second selected
spell's eligible damage before Magic Shell's one threshold decision. Native
`A39F8` builds a temporary recipient object using the controller's second
coordinates. Its normal `B4A1C` area and `A3778/A3848` eligibility helpers remain
in control; excluded recipients do not contribute. The native continuation
predicates at `95D12..95D4E` and actual remaining MP/native `12ED98` cost gate
that contribution. Only positive magical HP damage contributes, including when
the first spell's element is immune or absorbed. Healing/status-only spells
do not create a hypothetical HP hit. Existing flags still permit one decision.

The query preserves native `0200F390..0200F423` and RNG. Native recipient
scratch is a `2C4`-byte object plus `1000`-byte area buffer allocated/freed on
the normal heap. A new stack-local snapshot initially overflowed into native
IWRAM code; the fix borrows an unused existing result-bank slot with the same
live-stack-token authentication as native result scopes. No buffer persists
between queries; no pool or save-layout growth. The acceptance checks compare
IWRAM code bytes and verify retirement of all borrowed bank slots.

`test-mystic-knight-doublecast-shell` passed 2,975 assertions in selected run
`20260916T090133.174042Z` (10/10 including prerequisites). Controls execute
ordinary Shell and full native casts: both stack residues, fixed hit/miss
seeds, same/different/edge targets, exact combined threshold boundaries,
stronger/mixed original magic, immunity/absorption and insufficient second MP.
Shared single-action Shell and continuation tests passed in preceding 12/12
run `20260916T085905.381392Z`; only pair checks were repeated for the final
nullified-first-element correction. Test-only follow-ups can select
`test-mystic-knight-doublecast-shell-cached` after strict prerequisite reuse.

## Shared snapshot and reaction aggregation

The second subcast imports full frozen state before job start handlers. Native
per-result interception/redirect markers reset; Attunement resets only its
per-subcast price/refund markers as required by the specification. TBN/Poise,
Dark Ward mitigation and one-shot claims persist across the pair. Recovery and
retaliation use accumulated actual HP loss and require survival of the completed
action. Auto-Cureall shares its claim/item across both status applications.

Queue exhaustion defers new reactions while the native caster status predicates
and remaining MP allow the second cast. Otherwise it resolves the partial
action immediately. First-only targets use exact wrappers retained from native
first-result rows; there is no coordinate or live-roster fallback. Empty second
casts bind their actual native queue frame at the installed assembly entry,
so they still flush carried reactions even without an A23B8 result callback.
All queue arena/capacity/known-unit/frame guards remain in force.

Candidate `c1fee872002c58941114f2d80aae2073ce910244` passed existing queue ABI,
Mystic continuation and pair-Shell checks in `20260916T091435.519188Z`. The new
reaction script initially had two invalid controls (unmitigated Dark Ward and
enemy-owned inventory). Corrected controls and added lifecycle cases passed
1,649 assertions in cached run `20260916T092033.285820Z` (2/2), without native
source/image changes. Seven queued reactions plus Auto-Cureall cover same and
first-only targets, both stack residues, fixed seeds, real inventory debit,
whole-pair survival, insufficient second MP and natural caster KO. Native
constructors generate damage, status, queued objects and costs. This does not
substitute for frame-driven controller/animation acceptance.

## Frame-driven player flow

`test-doublecast-playback` selects original Red Magic/Doublecast/Fire using
fixed button sequences on a real Viera turn, with a real Bangaa recipient.
Declared mastery, stats, allegiance and formation are fixture inputs; the
native controller chooses targets, constructs both spells, renders queued
recovery, reaches its facing prompt and advances to another unit's menu.
The recorder only fixes the declared RNG seed and copies results.

Initial run `20260916T092853.524112Z` passed 10/10 including prerequisites.
Expanded cached run `20260916T093237.538737Z` passed 2/2 and 306 assertions on
the same `c1fee872002c58941114f2d80aae2073ce910244` image: twelve scenarios,
reaction-disabled controls, Spellweave enabled/disabled, same and first-only
targets, and hit/miss seeds. It checks two costs, frozen then committed sequence,
one cumulative Absorb recovery after the pair, continuation retirement,
unchanged AP/inventory and exact native renderer bytes `03006170..03006D67`.
Playback terminates at the native facing phase rather than a fixed excess wait.
The earlier expanded attempt selected an empty second area the player UI
would not confirm; its fixture now selects another occupied area. No game
source change was needed. Frame changes do not certify every frame/banner.

The interruption-only follow-up `20260916T093642.303229Z` passed 2/2 with
73 assertions across four additional player flows. Before confirmation, the
caster has 1 HP and targets her own tile with the first Fire. Native damage
KOs her, the controller cancels the second cast without charging its cost,
the surviving defender's pending Absorb recovery resolves exactly once, and
rendering advances to another unit's menu. The continuation retires normally.
Enabled/disabled controls and fixed seeds 3/18 require actual positive damage;
no KO, action result or completion state is injected. The cached selection
`test-doublecast-interruption-cached` skips the already-passed twelve flows.
The ordinary playback step now includes both sections for final acceptance.

I03's shared ownership implementation is complete with this scoped native
evidence. The combined player-menu Shell path and five whole Shell pair flows
now pass on83d8d026e0bdf76ca1a1265d1da218eef54b8ad9; see
`notes/mystic-knight-shell.md` for the native selection contract, numbers and
stack correction. The later020d043ebca6208365faf874e938d6deca697dd3 checkpoint
also closes I02's mixed-heal/buff and actual cancellation/re-entry audit;
see that same evidence note. Final assembled presentation/regression remain
V01/R02.
Other reaction visuals remain covered by their individual playback scenarios
and eventual assembled acceptance, not by the Absorb scenario alone.
The forecast uses currently known
eligibility, not a simulation of future random misses or reaction interrupts.
I02 is complete within its bounded contract; this does not claim release or campaign acceptance.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-knight-doublecast,test-integration-relocations
# Only after verifying an unchanged built image/capture baseline:
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-knight-doublecast-lifecycle
```
