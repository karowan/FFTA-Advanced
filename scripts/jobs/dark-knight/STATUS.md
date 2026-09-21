# Dark Knight implementation branch

This is the historical branch handoff. All implementation agents have finished.
Root's current integrated implementation and remaining acceptance are recorded
in `IMPLEMENTATION-STATE.md`, `notes/dark-knight-reactions.md` and
`notes/abyssal-blade.md`. In particular, Last Resort, TBN, the four R/S effects
and Abyssal Blade now have implementations newer than the branch account below;
compound Bloodcasting and full end-to-end job acceptance are still pending.

The complete fourteen-lesson job remains in progress on jobs/dark-knight.
Current shared checkpoint ce83f72 adds authenticated reaction permission and
actual-HP observation after the owned saved-state release439e55a. DRK source
currently adds Blood Edge, Dark Mind, Crushing Blow and Unholy Sacrifice to
the earlier Sanguine Sword/Infernal Strike/Abyss Combo foundation. Last Resort,
Abyssal Blade, The Blackest Night and the four supports/reactions remain pending;
full laws/AI/cross-class acceptance remains pending for the whole job.

Dark Mind uses native Shell stage45 and healing stage90, self selection3 with
one-tile area1. The custom admission is weapon-free, self-only, living and
unconfused; its healing amount is min(floor(maxHP/5),100,missingHP). The native
action commits8MP once and retains ordinary status compatibility, Shell
duration, Silence independence and no Reflect/Return Magic/Doublecast. Its
description is assigned to both racial lesson records.

The builder reads the exact hashed private Samurai input, imports its two
existing descriptor callbacks, and compiles a small DRK layer at ROM offset
0x1200000. It asserts erased bytes before allocation. Text lives in
0x1230000..0x1240000. No persistent or transient RAM is allocated. The only
shared dispatch replacements are descriptor eligibility8 (0x3a8624) and
healing magnitude25 (0x3a875c); other actions call the imported prior callbacks.

Candidate f3965cb1d663443dec600c32cbd3b9f45a1c15f8 has:

- Run20260915T035804.822249Z:2944 native checks pass, including independent
  cap/rounding cases, all461 primary item IDs, both racial jobs and other
  legal jobs, preserved callback results, actual executor HP/MP/Shell/timers.
  Its first in-game test failed because the script had not used Move and
  therefore incorrectly expected Act to end the turn automatically.
- Run20260915T035912.229302Z:fixed native Move/Act inputs,40 actual mGBA
  checks pass. Both Human and Bangaa select/cancel/execute Dark Mind through
  the ordinary UI;50/200HP becomes90HP and50MP becomes42MP, native Shell
  appears, AP/inventory remain intact, and native Save Now/cold resume retains
  resources/status. The engine/ROM did not change between these two runs.

Reports and full logs/captures remain ignored under build/expansion. No ROM,
save, native dump or generated build belongs in the branch.

Outstanding: explicit native help decoder coverage, complete laws/AI/status
edge coverage, all other lessons, Bloodcasting cost consumers/multiple
subcasts, native sacrifice payment, Desperation, both new reactions, and the
root-provided owned status extension for Last Resort and The Blackest Night.
Dark Mind's passing focused tests are not full-job acceptance.

Requested shared state: four bytes per owned unit. Byte0 Last Resort T2/phase;
byte1 Blackest Night source token(0none,1..36canonical); byte2 active ward;
byte3 reserved. Caster-linked expiry requires exact copy-propagated source
tokens. Root owns the save/copy allocation contract; no bytes are borrowed.

## Blood Edge checkpoint

Candidate4120ec999e42fcb890dbf8bcf19ec5e795222280 adds DRK-A1/action356:
1.50P Dark, primary sword/greatsword/broadsword, r1/h2, no weapon proc or
drain, native accuracy, ceil(maxHP/10) paid once even on miss, leaving1HP.
Its native usability predicate and committed payment gate both reject an
unaffordable sacrifice. The new physical finalizer composes Exposed/Poise/
Blade Ward with one division. The native later stage explicitly excludes356
from applying these factors again; a failing rounding test caught that defect.
Its law weapon list includes only the primary, and explicit evaluated Move
coordinates own range/height admission. Two racial descriptions decode in
native help with at most3lines/27characters each.

- Run20260915T040710.716683Z:Dark Mind2944 native checks and40 in-game
  checks pass on this candidate. Blood Edge native tests pass; its first
  in-game oracle incorrectly demanded that fixed seed3 hit in both races.
  The Human case legitimately missed and paid its sacrifice correctly.
- Run20260915T040853.052251Z:Blood Edge120 actual mGBA checks pass,
  including fixed seeds0..7 with native-P comparison in both racial jobs,
  ordinary menu/cancel, sacrifice/payment and native cold suspend resume.
- Run20260915T041119.449306Z:1845 Blood Edge native checks pass,
  including450 geometry cases and complete native executor preservation for
  all366 previously enabled/original action IDs.3476 native help checks pass,
  preserving all previous help and verifying both racial new descriptions.

Shared hook additions requiring deliberate root integration:
physical final1300E2, weapon drain130654, weapon proc130688, paidA45C6,
element12F8A4, usability133E18, final native stage131B4A, law weapons13467A,
geometryA0014 and magnitude descriptor30. Generated physical source from
the local Samurai build is recompiled into the DRK reservation with explicit
imports; the accepted main binary is never rebuilt or replaced.

Remaining Blood Edge-specific acceptance: AI's separate evaluated cost
debitC11A8..C11B8 and associated scoring consumers must incorporate HP
costs, complete native law predicates and immunity/absorption/retaliation
edges. Only focused native element/primary-weapon law contracts have passed.
Do not treat this checkpoint as full-job or complete AI/law acceptance.

## Shared action-context prerequisite released eff9489

Branch jobs/dark-knight; DRK checkpoint7fcfa17; shared prerequisite eff9489
is a separate source-only commit for root and other job worktrees to import.
See notes/action-context-contract.md for the complete reproducible contract.
Final shared candidate967a24ed3eed6da3b01438fa9d795e2033414bdc; immutable
13-step run20260915T044135.796748Z passed, including2484 context checks,
native all-action/Poise/Ward and fixed game menus/cancel/combat/cold save.
Expanded scope820bytes remains stack-owned
under the existing0203FF48 root; no new persistent allocation. New native
HP-writer hookA2210 captures Fight as well as descriptor-driven actions;
A315A alone was proven insufficient by the new deterministic test.
Native result origin uses authenticated caller and exact actor wrappers,
not the incoming reactions-disabled flag. Whole voluntary Doublecast grouping
and Composure movement eligibility are explicitly unproven.

Commands:
.\Test Expansion.ps1 -Suite samurai -Only test-action-context,test-samurai-native,test-poise-native,test-blade-ward-native,test-blade-ward-executor
.\Test Expansion.ps1 -Suite samurai -Only test-samurai-in-game,test-poise-counter-in-game,test-poise-mp-in-game,test-blade-ward-in-game

Root reservations confirmed: DRK applications97LastResort/98TBN,
descriptors213CrushingStop/214UnholySlow/216LastResort/217TBN,
visible status keys28LastResort/29TBN, persistent job-state bytes0..3.
No new DRK status sprite has yet been installed. Root owns save/copy bank.

Correction to the preceding Blood Edge AI gap: native C1192 guards C11A8
with selector19 (Doublecast eligibility); Blood Edge is not eligible, so that
specific debit path is not a missing Blood Edge cost. It remains relevant to
future Bloodcasting multiple-subcast work. Full AI acceptance remains pending.

The shared interface also exposes the exact native result object only during
RESULT and four padded optional dispatcher stubs for isolated overlay linking.
Next prerequisite adoption: root77efe09 and portability fixd80bb14; root is
adding roster-token remapping and strict same-owner peer enumeration. DRK
feature work remains incomplete; do not count common-context tests as lessons.

## Shared saved-state adoption

Adopted root77efe09 as029ca41 and2eb9e52 asfd5f19f; the latter includes
portable fresh-fixture tests. Combined context820+job-state candidate
739ef5a7a7ccdb9f558c62ade6d9f47a249e54a2 passed all seven job-state steps
in run20260915T044726.384792Z, including native copying, cold save and roster
remapping. Read transport notes for strict owner-local peer enumeration.
The DRK builder now composes this state layer and imports ffta_action_paid.
Fresh DRK fixtures reserve heap end0203F400 and capture nativeA433C entry
using the deterministic Viking script4bbad8c adapted to the DRK path.
Old accepted-main executor heaps are no longer used by DRK feature tests.
Current commands: Test Expansion.ps1 -Suite job-state, then the declared
scripts/jobs/dark-knight/test-plan.json focused native and in-game steps.
Feature acceptance on the newly composed DRK ROM remains pending.

Combined DRK candidatecd3556ec7049dd24b098f0763756170c8a7b1753 passed all ten selected steps in
run20260915T045014.966913Z: fresh3F400 battle/executor, Dark Mind/Blood Edge
native checks, both-race fixed menus/cancel/combat/cold-save replay, and help.
This establishes the prior two added actions on the new shared prerequisites.
Next: Crushing Blow, Abyssal Blade and Unholy Sacrifice with actual-HP-gated
Stop/Slow riders, sword/geometry/cost laws and deterministic native/gameplay tests.

## Crushing Blow and Unholy Sacrifice prototype

New action records361/363, native descriptors213Stop/214Slow, primary-sword
physical coefficients1.15/1.75, Unholy20%maxHP+14MP, self-cross friendly fire
with self exclusion, costs/element/primary-weapon law callbacks and help are
authored. Native512fixed executor scenarios passed at050333.401082Z, including
bothracialactors, misses, MP-only interception, and actual-HP-gated riders.
Preview prediction now restores native global0x34context AND RNG; a full-RAM
query test exposed and verified that fix. Original action executor comparison
normalizes only the documented global descriptor pointer, verifies its exact
index/bytes, then compares all remaining EWRAM. Native half-S26 is retained,
including its forced100 special-status interception behavior. Fixed in-game
acceptance for both new abilities is now being exercised; not accepted yet.

## Reaction observer and sword replay milestone

Shared source-only commit ce83f72 passed2777 action-context native checks on
Samurai7bd9b8b51c67769e16c5a896c6a31f0f3b4c9d5e. No saved or stack schema change.
DRK candidate80ef51a56201086805c633c8aa44e218bdb80b3f passed the combined
8-step run20260915T051632.757302Z. Unholy Sacrifice now passes both-race
menu/preview/cancel/payment/cold-save and128 fixed native-entry seed cases.
The first replay failure was a TEST routing error: self-centered targeting
needs one fewer confirmation input, and the old confirmation checkpoint was
already post-commit (60HP/36MP vs100HP/50MP). The new test explicitly asserts
unspent resources at confirmation. It seeds at nativeA433C entry and stops at
its observedA822E return, adapted from root36ffd2b; it never injects outcomes.
The earlier cached-preview inference was not the cause. Eight seeds lacked
Slow success in the actual fixture; the declared64-seed set per race provides
positive damage, native misses and successful Slow coverage.

Native sword riders and Crushing Blow's updated replay are being rerun on the
new common-API candidate before committing the job-specific milestone.
Reproduce: Test Expansion.ps1 -Plan scripts/jobs/dark-knight/test-plan.json
-Suite dark-knight -Only test-action-context,test-unholy-sacrifice-in-game.
Upcoming snapshot reservations:22 LastResort,23 TBNactive,24 TBNcurrent-action
consumption latch. Queries must never claim24. Root reserves15Composure and
Viking16..21; Chemist action-claim masks1/2/4 are distinct from snapshot flags.

Milestone acceptance: run20260915T052002.828844Z passed all ten selected
steps on80ef51a56201086805c633c8aa44e218bdb80b3f: both previous new actions'
native tests, all512 sword-rider executor cases, full query purity/help checks,
and bothracial Crushing Blow menu/cancel/payment/cold-save replay with128
fixed native-entry seed cases. Together with051632, both new sword arts have
actual gameplay coverage. Full laws/AI, LastResort/Abyssal/TBN and four
support/reactions remain outstanding. No ROM/private assets enter Git.

## Desperation prototype after528ba47

Shared denominator2 outgoing factor is authored at the same sole final
division as native Exposed/Poise/Ward for custom physical, native physical
and native magical damage. Frozen support bit13 and post-payment activebit14
are cross-job native support lookup. Pure queries predict explicit DRK HP
costs without paying; actual native MP interception keeps MP magnitude neutral.
Native threshold/magic/sword/drain/MP tests are authored and running. No
Desperation completion claim yet; UI/AP/cross-class/legal command and excluded
reaction/fixed/item paths require independent acceptance.

## Batch implementation directive

User/root now require one coherent remaining-kit sweep before consolidated
acceptance. No test-after-every-edit cadence. Current tests are stopped; the
Desperation failure was an uninstalled optional-provider binding (the builder
text anchor failed to match); direct native support lookup/provider passed.
That binding now has an exact asserted insertion. The batch covers LastResort,
Abyssal Blade, TBN, Desperation, Bloodcasting, DarkWard and VengefulPulse plus
UI/law/AI/copy integration. Native reaction output insertion is coordinated
with Chemist; prospective-coordinate provenance and multi-subcast payment
remain explicit engineering prerequisites, never replaced with guessed data.
Compilation and focused blocking diagnosis only until the batch is assembled.

## Source handoff checkpoint after528ba47

Current branch: jobs/dark-knight. Last accepted job commit528ba47 remains the
fallback; this new batch is explicitly UNACCEPTED. Read HANDOFF.md for the
complete14-lesson matrix, native hook/state/table contracts and remaining work.
All C/assembly translation units compiled in055859.543740Z after final batch
edits. This proves compilation only. Consolidated build055633.283131Z rebuilt
SAM7bd9 and saved-state02d4, then stopped at the missing shared queue getter
ffta_action_unit_at. No queue stubs, fabricated native results or successfully
linked new-batch ROM were published. Chemist owns the pending shared release.

Authored this batch: LR/TBN state/action/icon integration, Desperation factors,
Bloodcasting single-component pricing, DarkWard/Vengeful native queue consumers,
436-row global action table with hidden433/434, extended description bank,
fixed native payment/lifecycle and threshold/rounding test plans. Root approved
queue claims512/1024. All tests are deterministic scripts in this checkout.

Definite gaps: Abyssal not implemented; compounded/subcast/native staged HP
cost upfront reservation; TBN eligibility when final damage rounds to zero;
reaction native animation/payload acceptance; full new status laws/AI/query,
UI/AP/copy/save/acquisition and combined cross-job regression. Parent/user asks
for the current agents to hand off and stop; root finishes these solo. Never
merge this checkpoint as a completed or accepted whole Dark Knight job.

Reproduce compilation:
Test Expansion.ps1 -Plan scripts/jobs/dark-knight/test-plan.json
-Suite dark-knight -Only compile-dark-knight-batch
Reproduce pending consolidation after queue adoption: commands in HANDOFF.md.
