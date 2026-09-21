# Shared action context implementation contract

Implementation owner: `jobs/dark-knight`, separate shared-prerequisite commit.
This contract extends the existing Poise/Blade Ward exact-pointer snapshot.
It does not complete Dark Knight, Viking or Chemist by itself.

## Build and repeatable checks

Use the isolated worktree's copied private assets. `build-samurai-probe.py`
starts with accepted ROM `ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`
and its matching frozen engine binary; it does not rebuild that accepted
engine from newer sources. It compiles the context in the private Samurai
reservation. Current context candidate is
`967a24ed3eed6da3b01438fa9d795e2033414bdc`.

```
.\Test Expansion.ps1 -Suite samurai -Only test-action-context,test-samurai-native,test-poise-native,test-blade-ward-native,test-blade-ward-executor
.\Test Expansion.ps1 -Suite samurai -Only test-samurai-in-game,test-poise-counter-in-game,test-poise-mp-in-game,test-blade-ward-in-game
```

Final 13-step acceptance passed in run `20260915T044135.796748Z`, including
native all-action preservation, Poise/Ward arithmetic/copies/counters, fixed
Samurai menus/cancel/execution/cold save, native MP interception, Blade Ward,
and the 2484-check action-context matrix. `test-action-context.py` constructs
explicitly labeled isolated API fixtures and separately observes complete native
execution with read-only hooks. Cases cover Fight, magic, Iaido, actual HP loss,
Damage-to-MP, counters, misses, payment, two held weapons and exact native result
object lifetime. It never injects an expected effect during execution. Detailed
observations and test-source hash are saved next to the exact candidate ROM as
`action-context.json`.

Earlier native regression passed in `20260915T043214.728483Z`; the 816-byte
pre-result-accessor candidate passed immutable replay run `20260915T043804.654192Z`.
The preceding run043436 had all individual checks pass but was correctly rejected
by the runner because its plan was reformatted during execution. Its replacement
and final acceptance above had immutable inputs throughout.

All declared runner reports and complete logs remain ignored local artifacts.

## Stack ownership and layout

Root integration now has an optional external bank for fresh native result
scopes. The payload below stays820 bytes. Each of eight824-byte slots adds a
four-byte pointer to an exact live stack token whose value must equal that
slot's frame address. A slot is not valid merely because its header looks
correct. The owner token must remain aligned and within the current live
IWRAM stack. Parent traversal, copied-unit cleanup and extra-flag ownership
use the same validation. End clears the frame, then releases its token.

The root bank is0203CE40..E7FF and is excluded from all three native heaps.
Its purpose is to remove the large nested result local from the stack after
real Counter exposed renderer-code overwrite. Primary snapshots and standalone
overlays retain their existing stack path. Native result objects are still
processed by the original engine; no reaction result is substituted. Acceptance
of this correction is recorded separately in `remaining-state-capacity.md`.

The existing root at `0203FF48` remains four transient bytes. No new persistent
RAM or save bytes are allocated. An action owns an 820-byte stack frame,
cleared on close; this replaces the prior 532-byte frame. Test guards explicitly
initialize both existing transient roots `0203FF44..0203FF4B` to zero.
A pre-allocation fixture filled the newer root with D7; expecting that invalid
pointer to survive a full action was an obsolete test assumption, now fixed.

| Offset | Field |
| --- | --- |
| 0, 4, 8 | magic, exact self pointer, previous frame |
| 12, 16 | record count, native reactions-enabled flag |
| 20..787 | 64 records: exact pointer u32, frozen flags u32, HP loss u16, claims u16 |
| 788, 792, 796, 800 | action ID, origin, category, phase |
| 804 | actual paid-event count |
| 808, 810, 812 | post-cost HP u16, MP u16, exact actor pointer |
| 816 | exact native result-object pointer; only exposed during RESULT |

Every native battle transaction opens a scope, even with no Poise/Ward.
Queries open if inherited context or a declared provider needs one. Explicit
copy observers propagate flags and independent loss/claim values. Closing
an evaluated copy or freeing its owning allocation removes that alias.
Queries inherit action metadata but have QUERY phase and cannot claim or
accumulate committed loss. Unknown pointers never substitute a live unit.

## Provenance and events

`ffta_action_started(actor, action, origin, category)` records an authenticated
executor action before native effects. Categories are explicit flags and remain
UNCLASSIFIED until a provider establishes them. There is no guessed blanket
physical/magical classification.

At native result entry `A23B8`, the wrapper preserves the actual caller LR as a
ninth C argument. The authenticated caller returns are `080A4857` and
`080A4A9F`. Both retain the original primary actor wrapper in argument 1.
Comparing it with the exact actor wrapper in the result object distinguishes
NATIVE_PRIMARY from NATIVE_REACTION. The incoming `r3` reaction-enable argument
is independent; it is not used to infer origin. Unknown callers are QUERY.
Native Counter tests observe separate reacting-actor scopes and disabled
further reactions. Their HP loss does not enter the initiating attack's totals.

Weak `ffta_additional_action_event(actor, action, event)` receives:

| Event | Phase | Meaning |
| --- | --- | --- |
| 0 | EXECUTING | action-start snapshot established |
| 1 | EXECUTING | actual native payment succeeded; post-cost HP/MP captured |
| 2 | RESULT | one native result object completed, before scope restoration |
| 3 | COMPLETING | native primary A433C transaction completed |

Event 2 may occur repeatedly for a primary action with multiple weapons.
Event 3 observes completion; reactions needing native presentation use the
queue-completion provider before the transaction's arena is freed.
A queued Counter receives event 2 and then its independent scope is retired.
Fight skips native MP payment, so paid count remains zero; it does not emit a
fictional payment event. The explicit cost observer runs after the real native
MP write at `A45C6..A45D4`. Job HP costs must complete before that notification.

**Scope limit:** A433C is one native transaction, not the outer Doublecast
boundary. The integrated controller continuation in
`notes/mystic-knight-doublecast.md` carries frozen snapshots, both extension
banks, claims and accumulated HP loss across its two transactions. It defers
new queued reactions until the completed pair (or completed partial action)
and commits Spellweave once at the native controller join. It does not leave
an active stack snapshot between ticks or serialize transient ownership.
NATIVE_PRIMARY is not proof of a
player-controlled action, own-turn eligibility, or no voluntary movement.
No Composure eligibility is guessed here.

## Shared providers, flags and claims

`ffta_additional_snapshot_flags(unit)` may supply only declared job bits.
The existing `ffta_additional_beneficial(unit)` composes custom positive
statuses into Poise. Do not return Poise's low bit through the job-mask provider.
At merge root must compose job functions behind these dispatchers instead of
linking several competing definitions of one weak hook.

| Bits | Owner |
| --- | --- |
| 0..8 | existing Poise, actor role, native reaction, Ward, side and Charm |
| 9 | qualifying harmful status snapshot |
| 10 | Viking Opportunist |
| 11, 12 | Chemist Auto-Cureall and Auto-Potion start eligibility |
| 13, 14 | Dark Knight Desperation equipped and threshold-active |

`ffta_action_set_actor_flags(mask,value)` can update only job bits, after an
actual paid event and only in EXECUTING phase. This supports post-sacrifice
Desperation thresholds without changing frozen recipient eligibility.
`ffta_action_unit_flags(unit)` reads the exact action snapshot.

Claims are separate 16-bit per-recipient latches: bit 0 Auto-Cureall,
bit 1 Auto-Potion. `ffta_action_claim` succeeds only for a known recipient and
known origin in RESULT or COMPLETING phase, once per requested bit. It does
not consume inventory itself. A caller must claim only after its own successful
item consumption and earlier-priority interception checks. Query copies cannot
claim live stock. `ffta_action_claimed` is a read-only query.

## Actual HP loss observer

The installed shared hook is `A2210..A221C`, the native HP writer. Its exact
original prologue and native `C8280` call are preserved before continuation at
`A221D`. Wrapping only the earlier custom-rider site `A315A` misses Fight; the
focused native tests caught this and motivated the shared-writer hook.

`ffta_action_hp_apply` reads HP before/after the original native writer and
calls `ffta_action_note_hp_loss`. The recorder admits only an authenticated
RESULT scope and known non-actor recipient. Positive loss accumulates with
u16 saturation; healing, unchanged HP, self-target/cost and queries add zero.
Damage-to-MP therefore adds zero regardless of the displayed magnitude.
`ffta_action_hp_lost(unit)` returns the aggregate for that exact record.

This is an actual-loss measurement, not a complete eligibility policy. Consumers
must still exclude reflected actions, fixed/percentage effects, items, combos,
DoT and other ineligible categories at a proven action/stage boundary. It is
not safe to infer these categories merely from a positive loss value.

## Integration

Cherry-pick this shared source commit before adding job-specific consumers.
Preserve each job's source reservation and compose providers in root. The root
save/copy extension enlarges evaluated records from 276 to 296 bytes; it remains
a separate prerequisite and needs its own merge acceptance. The context has no
private saved state and must consume that extension through its public accessors.
Rebuild the private candidate and run focused native plus fixed in-game checks;
root then owns assembled regression and full merge acceptance.

## Rebindable optional dispatcher stubs

The four weak optional dispatchers have explicit 16-byte zero-return defaults
in action-snapshot.s. Their addresses are present in the private build manifest.
A job overlay may replace a verified stub with its own dispatcher without
rebuilding accepted main. Root must compose several job providers deliberately.
`ffta_action_result_object()` exposes the exact native object only during RESULT,
for consumers that establish selected-center geometry from its native layout.
It returns NULL during queries and completion; no native center offset is guessed.

## Native reaction permission

`ffta_action_reactions_enabled()` reads the independent native result permission
only during an authenticated RESULT scope. It returns zero for unknown calls,
queries, EXECUTING, COMPLETING and absent scopes. The restored event3 flag must
not authorize reactions. Consumers that act at event3 must retain their own
recipient-specific admission from the native result/HP event; cumulative loss
alone cannot prove every component admitted reactions. No layout change.

A fifth padded weak provider, `ffta_additional_hp_loss(unit,before,after)`,
runs after positive actual HP loss is recorded and while the authenticated
RESULT scope and native reaction permission remain active. Costs, healing,
unknown calls, queries and actor-self loss do not call it. It reports actual
HP values rather than the saturating cumulative counter. Category/origin and
recipient eligibility remain the consumer's responsibility.

The permission/HP observer followup passes 2777 native checks on
Samurai candidate `7bd9b8b51c67769e16c5a896c6a31f0f3b4c9d5e` in immutable run
`20260915T051632.757302Z`. Reproduce with
`Test Expansion.ps1 -Suite samurai -Only test-action-context`.


## Native queue extension

See `notes/native-reaction-queue.md` for the accepted transport contract,
4073 context/2339 queue checks, packed low8 permission isolation, exact native
frame binding and optional queue-completion provider. The820-byte layout remains;
the private RESULT pointer word retains a bound frame only while EXECUTING and
is never exposed as a native result object by the public getter in that phase.
