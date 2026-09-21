# Persistent Fight: execution and damage-forecast checkpoints

This accepts a bounded portion of checklist I01. Actual native primary Fight
now uses the prepared element (Fire, Ice, Lightning or Holy), or neutral for
the other enchantments. Flare uses 75% of capped effective WDef. Drain and
Osmose use actual HP removed, their approved caps and undead reversal.

Poison/Sleep/Silence/Slow riders and ordinary weapon-effect replacement now
also execute. Native player/AI HP damage forecasts are now connected. Remaining
AI effect scoring, recovery prediction and healing/MP law reporting remain.
Status-law prediction and committed elemental/status reporting have separate
bounded acceptance below. This is not complete Spellblade or release acceptance.

## Verified primary-weapon ownership

Native A433C supplies its exact frame to the A23B8 result wrapper at caller
A4856. Frame+34 is the actual weapon iteration; frame+38 is its count. Both
the original action (frame+28) and result action (object+10) must be Fight.
The original wrapper at frame+24 must match the supplied wrapper and object.
Queued reactions, unidentified callers and other actions cannot bind fuel.

Iteration zero is **not necessarily equipment primary**. Native12F0D8 calls
12E55C, which gets the equipment-order pair through 12E4F4, then stably sorts
the pair by weapon attack (item selector10). The stronger offhand can execute
first. Equal weapons retain equipment order. The implementation maps the
equipment primary onto that sorted iteration, then also checks the actual
object's weapon. Identical item IDs alone never establish hand identity.
The approved image's item attacks range from 0 to 87; the native signed-byte
comparison and the implementation's nonnegative comparison agree throughout
this entire content range. Reaudit sorting if future content exceeds 127.

`diagnose-mystic-fight-carriers.py` observed 48 native casts and passed 610
checks on the prior accepted 3aa5cd image. It covers one weapon, equal weapons,
different weapons in both orders and actual formula/object correspondence.
These two-weapon fixtures test engine component ownership, not menu legality
for equipping a particular race/job with those weapons.

## Execution and lifetime

`action-snapshot.c` supplies only a freshly authenticated frame to the optional
`ffta_additional_native_result` provider. The integrated provider binds a
24-byte stack scope through the transient cell 0203F730..0203F733, outside the
saved job bank. Spellbreak's separate 0203F72C cell is unchanged. Every return
restores the previous pointer; an ineligible nested result shadows the scope.
There is no saved-layout change or battle heap expansion.

Native Fight's damage routine also enters read-only nested snapshot scopes.
`ffta_action_in_result` authenticates their exact actor/action and live result
ancestor. It does not grant a query mutation privileges. This lets native
formula evaluation use the bound primary element and Flare defense input while
keeping unrelated queries, copies with different actors and reactions inert.
The elemental hook falls through to the existing dispatcher for other actions.
Flare changes the native scalar after the normal effective-defense cap; original
accuracy, criticals, variance, affinity, damage modifiers and clamps remain.

Only the verified direct Fight HP writer (native return A2B8B) calls the
resource handler. It locates the exact recipient row of the current object
and reuses the command resource equations. Misses, absorbed hits, overkill,
displacement, redirected MP damage and the second weapon cannot manufacture
recovery. Drain accumulates the native actor HP result; Osmose updates bounded
MP and the native recipient result row. One action claim prevents duplicates.

## Status, prevention and weapon effects

The direct HP writer records the exact recipient only after positive HP loss.
The status hook at native A2DCC consumes that pending recipient after the
original damage-sensitive status cleanup, before native refresh 131C58.
Applying Sleep earlier would let the same hit immediately wake its new status.
Miss, absorption, zero damage, redirected MP damage and lethal hits do not
create a surviving-target rider. Native friendly fire remains applicable.

The synchronous rider saves/restores the 52-byte global effect context and
runs native eligibility, S accuracy, player-side adjustment, RNG and application
for descriptors125/97/111/104. Native compatibility, Astra, Inoculated,
Immunity, timers and Chemist prevention therefore remain in control. Slow is
outside the native Cureall/Immunity whitelist. Sleep uses S/2, except that
Astra's guaranteed admission must stay guaranteed to consume its interception;
this correction also applies to the immediate Sleep command. No roll or outcome
is injected into shipping execution.

Caller- and primary-scope checks suppress native3D drain's formula and recovery
paths and native3E cleanup, preserving existing custom-technique fallbacks.
Other equipment properties and native3F restoration remain. A restorative sign
correction prevents enchant affinity absorption from turning healing into HP
damage or resource theft. Real Healer staff124 cannot be enchanted; a disposable
qualifying-weapon3F fixture covers the defensive interaction. Counter and the
other hand never acquire the primary scope. No save/schema change is involved.

## Deterministic verification

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite
mystic-fight` for the declared focused suite, and `-Suite combined` for assembled
acceptance. The carrier diagnosis has its own `mystic-fight-carriers` suite.
Keep the sources frozen until the runner terminates.

`test-mystic-knight-fight.py` uses 1,328 native casts and 3,622 assertions:

- Independent damage controls change only the original item element or target
  WDef; hit decisions, random samples and damage outcomes are never injected.
- All eleven preparation kinds, five affinity inputs and eight fixed seeds.
- Per-component controls for identical and attack-reversed dual weapons.
- Actual-loss recovery, overkill, missing HP/MP, zero target MP, allies, undead
  class flags and Zombie; real Counter attacks remain unenchanted.
- Scope restoration and rejected invalid/stale pointers remain read-only.

The first focused run (`20260916T055948.346133Z`, 15/16) found that damage
formulas entered a nested query and therefore lost access to the result-owned
scope. Resource handling already used the proper result. The fix authenticates
the query's result ancestor. Failure serialization was also changed to freeze
lists instead of retaining references to subsequently reused observation lists.
Runs `20260916T060214.671338Z` and `20260916T060447.046598Z` passed 16/16;
the latter adds the resource-boundary and native Counter cases.

Historical damage/recovery combined run `20260916T060545.691544Z`: **77/77**, inputs unchanged.
Candidate SHA1 `0967526b01d104dbb7070cc6c0f11ad4da6c1f7b`; shared prerequisite
`1baaac2eec17c436ec55e30f08bbbc429bee56d5`. An independent post-run file hash
matched. Central code is 31,960/32,768 bytes; Mystic/workspace code is 12,336
bytes. Existing playback, AI, saves, workspace and fresh opening all passed.

### Status/effect batch and consolidated acceptance

`test-mystic-knight-fight-status.py`, included in `mystic-fight` and `combined`,
adds **7,972 assertions / 3,118 native casts**. It checks four riders across
native prevention, friendly fire, lethality, zero damage, Damage-to-MP,
restorative equipment and a silenced actor. Its independent oracle executes
an immediate native S stage on the observed post-damage state. Read-only
observations do not replace native rolls, HP, statuses or result rows.

Coverage includes identical/reversed dual weapons, native Counter, stock and
Inoculated/Auto-Cureall combinations, explicit Astra consumption, all 52 actual
item-effect bytes in paired controls, all eleven restorative enchantments
across five affinities, and ordinary unenchanted3D/3E controls. The existing
3,622-assertion damage/resource suite and Spell Parry suite also pass.

Focused run chronology (UTC identifiers):

- `20260916T064101.323236Z` and `20260916T064345.046333Z`:16/17 each.
  Corrected fixture assumptions: low attack need not deal zero damage; a
  supposed Healer rapier used an AP byte as an effect; Slow is not Cureall immune.
  Zero damage now uses the native prevention flag and Healer uses actual staff124.
- `20260916T064635.118683Z`:17/17, image022051fd2c1eca6144fe0d7c3daa04da79c2409e;
  restorative sign protection and corrected fixtures.
- `20260916T064928.024980Z`:17/17, imagede3ac52f0a0265a21165ad68efd0ae9deb808309;
  friendly-fire policy and native Auto-Cureall coverage.
- `20260916T065056.967916Z`: deliberately interrupted during step20 after
  review found Astra/Sleep admission needed correction. Not acceptance evidence.
- `20260916T065303.005312Z`: full combined **77/78** on final image
  `33e8cb4b9717b735117016510438035838da0969`; inputs unchanged.
- `20260916T071333.775734Z`: affected **22/22** on that same game image;
  inputs unchanged. All 78 combined-plan step IDs now have passing evidence.

The lone full-run failure was the shared test recorder publishing ready/count
before its rows were copied. Passing Step/Counter's first frame saw zero row1;
the finished native Counter row was `[0,33567716,33555880,129,50,0,0]`, actor HP0,
with the proper origin. Publish the complete payload before count/ready and
wait for both in the consumer. Assertions were retained. This test-only fix
changed no game bytes. The original failed report remains in the private run
directory. This is full-suite plus affected-rerun evidence, not one78/78 run.

Reproduce the affected rerun with `Test Expansion.ps1 -Plan
scripts/integration-test-plan.json -Only test-integrated-reaction-playback,
test-dancer-choice-playback,test-passing-step-playback,test-passing-step-ai,
test-passing-step-counter,test-geomancer-playback` (one comma-separated list).
Reports/logs are under `build/expansion/test-runs/<run>/`; candidate-specific
status results are `mystic-knight-fight-status.json` beside the integrated ROM.
Current central code is32,008/32,768 bytes, Mystic/workspace13,176 and Geo AI1,408.
An independent post-run hash matched the final image. The runner's top-level
ROM hash is the frozen foundation; use integrated manifests/logs for this image.

## Native damage forecasts

Final candidate `0be70587c636f5f9fea3896986b8ab632507e431` passes **79/79** in
`20260916T074143.381019Z`, inputs unchanged and independently rehashed. Shared
prerequisite and foundation are unchanged from the status checkpoint above.
Central code remains32,008/32,768 bytes; Mystic/workspace13,568; Geo AI1,408.
The earlier focused run `20260916T073749.021292Z` passed18/18 on
`79bc9609f27218383d9b576f64c03e96760ebadf`; the final batch adds stricter reaction
exclusion and wider deterministic property/law-query coverage.

The wrapper at130200 saves original r4–r7, LR and the two stack arguments before
opening the shared query snapshot. Recognized native callers are B572C (player
preview), BDF54 (AI score), C2364 (AI detail),12E7D8/12E974/12E9A4/12E9FE
(reaction eligibility) and1356E8 (law damage query). Their numerical forecasts
use the first power-sorted weapon; BDF54 also provides its actual r4 loop index.
Native UI construction B52E6 fills selection+EE with12F0D8's sorted pair.
C287C/C28AE supplies the first sorted weapon through C26EC/C2618/C2314 to the
AI detail calculation. The reaction evaluator12E6E0 uses12E55C's first sorted
weapon. These are explicit callers, not a general item-ID permission rule.

A shared helper maps this component to equipment-primary, preserving stable
order for identical weapons. If the stronger offhand is first, these original
first-weapon queries remain offhand queries and do not acquire the enchantment.
This preserves the native forecast's component scope; it does not introduce a
new aggregate dual-weapon display. Actual A2914/A2974 formula calls retain the
result-owned scope and still enchant primary when it executes second.

Query scopes have a null result object, require a live authenticated stack
owner, current query phase and exact actor/action, and restore the previous
pointer on return. Other/unknown queries shadow that scope. Native reaction
origins and foreign live result actors cannot gain primary enchantment fuel.
Element/neutral conversion, Flare effective defense,3D drain replacement and
3F restorative sign protection therefore use the same existing formula hooks.
No saved bytes, record IDs or permanent RAM were added; the stack scope stays24
bytes and bank0203F730..F733 remains a four-byte pointer.

`test-mystic-knight-fight-preview.py` is declared in both `mystic-fight` and
`combined`: **15,202 assertions /4,266 native calls**, zero failures. It calls
real B55CC, BDECC, C2618,12E6E0 and13569C entry points and observes their native
formula returns without modifying registers/results. The matrix covers all
11 enchantments, five affinities, four weapon pairs and both stack alignments;
paired controls change original item element and target defense. Further cases
cover ordinary drain and restorative weapons, unknown direct formula calls,
and unchanged live units, owned job state, RNG and retired scopes/snapshots.
Dual-weapon fixtures test engine ownership, not racial menu legality.

The native law query uses original damage-threshold law56; its observed damage
matches the independent control. This is not proof of actual elemental/status
law reporting. The suite also does not replace dedicated rendered-menu or full
Mystic AI-turn acceptance. Existing combined playback, AI, persistence, startup,
Fight execution/status and Parry tests all pass on the final image.

## Remaining integration

Elemental prediction and committed elemental/status Judge transport now have
bounded acceptance in `notes/mystic-knight-fight-laws.md`. The manager-owned
receipt preserves primary identity after reaction cleanup; actual native masks
supply success evidence. Ordinary-success status-law forecasts now have evidence
in `notes/mystic-knight-fight-prediction.md`. AI effect scoring, recovery
prediction and applicable healing/MP law outcomes remain. Card animation and persistent
penalties remain campaign verification. I01 stays open. Autonomous work has
resumed under the targeted-testing workflow in `PARALLEL-IMPLEMENTATION.md`.
