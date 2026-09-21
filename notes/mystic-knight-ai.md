# Mystic native AI integration

September 16, 2026. Current bounded candidate:
`0768c96b3e1f22977120387507261262ef3dff6e`.
Fight values, Spellbreak choice/damage admission and autonomous self preparation
have targeted evidence. I05 remains open for tactical command preferences,
Break/Flare selection and mixed-area choice coverage. Earlier checkpoints below
retain the tested scope and hashes for sibling paths.

## Fight values

Both native score BDECC and row C2618 add admitted Poison/Sleep/Silence/Slow
value, alongside the resource values documented in `mystic-knight-resources.md`.
An owned simulation follows the ordinary successful, average-damage branch and
uses the native S accuracy as value, matching native C257C's status contribution.
AI ranking does not borrow the optimistic preceding-miss/minimum-damage policy
used for a law warning. Existing ailments have no new value unless damage
removed them first (notably Sleep). Actual native prevention/application masks
exclude Astra, Immunity, Inoculated, zero HP loss, MP redirection and defeated
recipients. Slow retains its native whitelist exception. Queries preserve
units, owned job data, RNG and executable code.

## Spellbreak

One native action row considers all 21 eligible buff choices. Each candidate
uses native hit chance, damage after that exact removal, and law metadata.
Removal adds 20 value points scaled by native hit chance; damage supplies the
remaining preference, and ties use stable menu order. This is AI ranking only:
it changes neither damage, accuracy, costs nor which statuses are removable.
Missing buffs, friendly targets, Silence, inappropriate weapons and dead
targets produce no candidate. A stale selected buff never switches to another.

The synchronous choice is owned by the exact actor/action. After native
selection it can be recovered only from a matching completed decision, current
AI actor, action and operand. This preserves the choice during movement and
native target/damage queries without lending a player or copied actor a stale
selection. The original action-count allocation and native movement search
remain intact. No persistent choice or new saved state is introduced.

## Storage

The central code reservation had no room for further shared wrapper growth.
`ai-choice.c` and the new `mystic-knight-ai.c` now link inside the already
reserved Mystic region. Existing symbol-resolved hooks continue to reach the
same interfaces. No other job IDs, reservations or RAM state move.

Mystic command query snapshots borrow the existing authenticated result bank,
as Fight queries already do. Dispatch occurs in the existing native preview
wrapper, keeping the original real-result call depth and publication path.
An extra dispatch frame at real execution was enough to overwrite the last
16 bytes of renderer code in the actual unlearned/Fight control. That failed
case was retained, the extra frame removed, and the same flow now passes its
full renderer guard. Static compilation and shallow native calls alone could
not establish this transport/lifetime property.

## Deterministic evidence

Selected native checks: `test-mystic-knight-ai`, `test-ai-choice`,
`test-geomancer-ai`, `test-mystic-knight-commands` and
`test-mystic-knight-resources`, with the declared prerequisites. Only affected
checks were repeated after corrections; no full integration suite was used.
Full-turn check: `test-mystic-knight-choice-ai` (or its strict cached variant).

- Build-only runs 20260916T111432.734131Z and 111543.915361Z exposed central
  code capacity. Helpers/shared wrapper were placed in the existing reservation.
- 20260916T111709.577289Z passed 12/13 steps, including Dancer/native choice,
  Geomancer search and resource consumers; deeper Spellbreak query stack failed.
- 20260916T111851.431604Z passed 12/12: 1,359 new AI assertions, 2,383 command
  assertions and 12,652 resource assertions after bank-backed command queries.
- Cached 20260916T111942.332648Z completed the first four full-turn scenarios
  but failed the final unlearned/Fight renderer guard. No failure was waived.
- Final 20260916T112100.394984Z passed 11/11 selected steps on the candidate
  above: 1,359 AI assertions and 71 full-turn assertions. The final correction
  only changed query dispatch to preserve real-result depth. Retain earlier
  sibling native evidence rather than repeating unrelated passed matrices.

The new native matrix covers four Fight status riders, eight conditions, two
weapon arrangements and two stack alignments; all 21 Spellbreak choices;
84 native chosen casts; invalid targets and exact published-choice admission.
The five full turns use seeds 0/3/18 with Protect and seed 3 for no-buff and
unlearned controls. All three learned runs choose Spellbreak/Protect, move from
(0,14) to (0,15), pay 10 MP once and return the turn; seeds 3/18 remove Protect.
Seed 0's miss is retained. Both controls choose Fight. Inputs declare mastery,
equipment, allegiance, formation, native Protect with its three-turn timer,
and RNG seed; no selected action, option, route, score, hit or outcome is injected.

Raw ROMs, instrumented fixtures, states, reports and logs stay ignored under
`build/expansion`. At this earlier checkpoint I05 still included self mode,
Release fuel/area coverage and remaining whole turns; the next section records
the subsequent work and its narrower remaining scope.
Persistent Fight implementation is complete within the documented contract;
final campaign Judge penalties remain V06 and assembled regression remains R02.

## Command query correction and self preparation

Candidate `c50b86715393fe8f36b125159f0b4a5a72f21947` additionally fixes
Spellbreak's native C48A4 admission. That caller constructs its query with
primary weapon 88 rather than selected buff 8. The earlier positive-score
assertion missed this: detailed score was only removal bonus 11, while the row
correctly scored 87. Query admission and damage now recover the exact choice
from the authenticated actor/action scope. Real execution retains its explicit
operand; no expired choice falls back to another buff. The new fixture requires
damage contribution and observes row/score 87/87 on the Protect scenario.

Self preparation previously inherited H damage's positive 100 hit contribution
and detailed score 55, making a harmless buff look harmful. The AI row and
score now use a small signed benefit (-20) only on a bare blade. Native hit and law flags remain intact. The self-only forecast row uses
native non-HP beneficial application category82; execution still uses the
Mystic descriptors and grants no Protect. Existing enchantments suppress
self preparation, including switching kinds, so unreachable enemies cannot
cause endless buff cycling. Attacks retain their normal enchantment changes;
player self refreshes and switches keep their original eligibility and costs.
No save schema, action IDs or persistent state change.

`test-mystic-knight-command-ai` covers 14 commands, ten conditions and two
stack alignments (280 scenarios, 1,462 assertions). It checks native row and
detailed score, byte guards, unit/job/RNG/code purity, valid/invalid Release
fuel, ally/self restrictions, Silence, weapon restrictions and no wasted
self refresh/switch. Run `20260916T113625.045762Z` passed 13/13 selected steps,
also retaining 1,359 AI assertions, 2,383 command assertions and five complete
Spellbreak/control turns (71 assertions). The preceding failed command matrix
and build-declaration failure are retained in the implementation checkpoint.

Native self-centered search BEAC8 excludes the actor from its recipient count
at BE6C2. A Mystic-only adapter now admits the native self candidate, checks
usability with command filter128 and the native movement map, then publishes
one self recipient at the current tile. It never supplies movement. Ordinary
self/area actions forward to the original prologue/continuation. Both stack
alignments and exact forwarded rejection are checked. The native matrix grew
to 2,056 assertions, adding 110 self-search conditions and forwarding controls.

Accepted coverage is the union of retained runs, not a claim that the whole
new playback file passed in one run:

- `20260916T113843.125544Z` completed 36 attack turns on c50b867: Sleep,
  Silence and Slow were chosen in nine turns; ordinary Fight won the others.
  Its later self failure was retained. These attack paths did not change.
- `20260916T114632.622520Z` passed the 2,056-check native matrix on 0768c96
  and sixteen remaining complete turns: all eleven self enchants, prepared
  Wait, Fire Release, Flare/Fight, no-fuel/Fight and bad-fuel/Fight. Its final
  allied-only control failed because its changed control bits did not change
  cached native faction membership. Prior captures remain under each named
  case in `mystic-knight-command-playback-ai` beside that candidate ROM.
- Corrected `20260916T114927.981372Z` passed 2/2 steps, 13 assertions and the
  allied-only Wait control on the same ROM: original factions, five opponents
  beyond range, nearby native allies and Immobilize. No production edit and
  no repetition of the sixteen passed cases.

This is 53 completed turns across retained and corrected evidence, including
Wait/Fight controls, not 53 custom casts. Break was not selected in the current
attack formation; Flare Release lost to Fight. Favorable/nonvacuous fixtures
for those choices and mixed enemy/ally area ranking remain explicitly open.
Player command modes and all21 exact removal choices retain the earlier native
execution coverage. Campaign Judge penalties and assembled release remain open.

Reproduce native coverage with `test-mystic-knight-command-ai`; full playback
with `test-mystic-knight-command-playback-ai`; use the `-cached` variants only
when prerequisite verification passes. The `-remaining` selection covers the
17 self/fuel cases; `test-mystic-knight-ai-allied-control` covers only the final
control. Playback output now has a unique timestamp directory, per-case
outcome records and completed-prefix logging on failure, so a narrow follow-up
cannot overwrite earlier summary evidence. Inputs remain fixed/deterministic.

## Tactical commands and completed I05 implementation

Accepted targeted candidate: `0cd1f531075e2125405c7f41a6356f7217bd4f6d`.
I05 is complete within its defined command/Fight decision scope. This does not
close campaign law penalties, the all-job interaction audit or release gates.

Bare-blade damaging strikes add a modest20 preparation value. Drain/Osmose
add their capped actual resource benefit/debit, including undead reversal and
Damage-to-MP rejection. Osmose accounts for native MP cost before estimating
missing MP; actual execution retains the shared post-payment plan. Native
prevention, weapon/Silence gates and all actual hit/cost/damage rules remain.
Damage-to-MP admission is isolated and restores both its temporary query
context and RNG. Original native public row/score routines still write their
normal query context; the custom forecasting helpers restore their own entry
context and never change live units, owned job state, RNG or renderer bytes.

Break Blade adds expected current HP neutralized to native Petrify value only
when actual native application on an owned target admits Petrify. Astra,
Immunity, Inoculated, prior Petrify, KO, allies, Silence and wrong weapons
produce no invented benefit. This changes AI value, not success probability.

The installed C2940 wrapper lets native sorting finish, then moves a better
Mystic strike/Break immediately ahead of Fight within that target's existing
complete20-byte records. Other target/ability order is retained. A native Fight
forecast sufficient for a free knockout keeps its preference. Row16 is left
unchanged: C2F6C uses it in sorting, but C359C also passes it to native random
willingness at12F1DC. The experimental override was removed after inspecting
both consumers. The native search, geometry, law flags, hit chance, command
transport, renderer and actual result executor remain responsible for play.
No new state, IDs, save schema or ROM reservation was introduced.

Acceptance is the union of these retained runs:

- `20260916T115446.483887Z`, earlier unchanged Release implementation0768c96:
  six full turns, Fire/Flare/mixed ally-area at seeds0/3. Every case selected
  Release, paid once, consumed fuel and damaged enemies. The nearby native
  ally was spared in the mixed cases. Its later Break failure is retained.
- `20260916T115950.419626Z`: existing2,056 command/self-search checks and
 12,652 shared resource/execution checks passed. Later failures isolated the
  new AI query's RNG mutation and inadequate ordering; both were corrected.
- `20260916T122008.007024Z`, final0cd1f531:1,882 native checks and both complete
  Break turns passed (30 assertions). Favorable Break was selected; Astra
  opponents caused Fight. All eleven utility strikes then completed with
  actual enemy damage, enchantment, single payment, rendering and handoff.
  Their per-case outcomes and completed prefix are retained under
  `mystic-knight-command-playback-ai-20260916T122049.239776Z`.
  The later low-health Drain input chose valid self preparation; that result
  remains recorded and is not counted as attack/recovery acceptance.
- `20260916T122325.972921Z`, same0cd1f531: the two attack-recovery scenarios
  pass (39 assertions), with Drain at700/999 HP and Osmose at fullHP/lowMP.
  Both perform enemy damage and actual resource gain. An unrelated new native
  sort assertion compared incidental void-return addresses and failed.
- `20260916T122406.818596Z`, same0cd1f531: final1,890 native assertions pass.
  This includes262 tactical inputs, exact resource/preparation arithmetic,
  native prevention, context/state/RNG purity, intact willingness,16 exact
  ordering controls and byte-exact forwarding of ordinary native sorts on
  both stack alignments. Native void-return R0 is not contractual; the harness
  still verifies SP and all callee-preserved registers.

Thus this increment adds21 accepted complete turns (six Release, two Break,
11 strikes, two recovery), retaining the earlier self/fuel/Spellbreak evidence.
It is not a claim that any failed combined report passed, or that every AI
situation is optimal. Critical-health native strategy can prefer self
preparation. The original low-HP opponent also exposed native free-Fight
behavior; normalizing all five opponents alone did not fix command preference.
A bounded native replay helped locate the later ordering/admission consumers;
its first variants omitted required native initialization and are diagnostics,
not acceptance. Full chronology is in `IMPLEMENTATION-STATE.md`.

Reproduce with `test-mystic-knight-tactical-values`,
`test-mystic-knight-ai-utility`, and `test-mystic-knight-ai-tactics`.
Use declared cached variants only after strict prerequisite verification.
`test-mystic-knight-ai-break-cached` and
`test-mystic-knight-ai-recovery-cached` isolate the corresponding corrections.
`trace-mystic-knight-ai-cached` reads a specifically retained private capture
and replays planning only; it does not create a fixture or certify a turn.
