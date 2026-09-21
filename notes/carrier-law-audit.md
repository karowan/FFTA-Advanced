# Remaining carrier-law audit

September16,2026. Item/weapon classification accepted within the scope below
on candidate `1427bd3de8bf54c7b0803c624bb33c8f1fc60683`. Earlier elemental
corrections used `3255000cfb2293c08a753c259239617c27fbd2d7`. I09 remains open.
The initial read-only audit used9ac4fa5b.

The approved specification requires new commands to obey relevant element,
item, theft, healing, equipment and mapped command restrictions. Audit each
native selector and its actual caller operands before extending the law hook.
The new harmful-status predictor/receipt is accepted separately in
`custom-status-laws.md`.

## Elemental corrections

Native kind2 at1344EC..13451A reads selector1 of the action record via CCD50.
It does not call the runtime element routine12F8A4. Before this change the law
hook overrode this category only for enchanted Fight, action0. The following
corrections are now installed:

- Mystic commands410..420 now contain the correct static element, matching
  `ffta_myk_element` for their identity. The ordinary selector handles both
  self enchantment and hostile strikes without a special law exception.
- Release422 preserves its frozen element in the authenticated per-object law
  receipt. Consuming or replacing the live enchantment cannot rewrite it.
  Flare explicitly records a non-elemental cast.
- Gaia381 retains its static Wind default but predicts selected elements
  through the authenticated existing player/AI choice and movement scope.
  Its receipt records the actual native object+18 choice before execution.

Static record observations were read from the assembled action table at
ROM11E8000. Actual damage already used the dynamic element hooks; these changes
close the corresponding law-classification gap.

## Caller and ownership constraints

The eight-argument native law evaluator1343C8 receives actor,target,action,
item-used boolean,movement,damage,mask,law. Its fourth argument is not a choice
or equipment ID. Late ordinary-command135072 passes zero there; native
Item134C52 passes action0 and boolean1. Do not overload that boolean to carry
Gaia's selected element or an enchanted weapon.

The native result object uses action at16 and its extra operand at18; actual
Gaia executions verify that field equals the selected element. Late queries
authenticate the exact action, container, actor, recipient and mask address.
The existing14 kind bytes store command elements with high bit80 set, including
element0, while Fight retains its original untagged kinds. No allocation or
save schema changes. The exact result wrapper binds before and after native
execution; Release reads frozen snapshot flags at both points. The late native
caller retains its original hit/target gates. Element classification does not
pretend to be proof of a newly applied status.

## Deterministic acceptance

| Run (UTC) | Selected checks | Result |
|---|---|---|
| `20260916T152350.996183Z` | Required build/native prerequisites; `test-carrier-element-laws`; shared Mystic commands, Fight laws and custom-status laws |13/13 steps passed;27,578 new elemental assertions |
| `20260916T152618.664081Z` | `test-carrier-element-law-playback-cached` and verified prerequisite reuse |144 assertions across12 actual menu-to-Judge casts |

The core matrix executes all11 fixed commands in self and hostile modes at
seeds0/3/18, plus all5 Gaia elements and all5 legal Release fuels at
seeds0/1/3/18. Queries use both stack residues and eight elemental rule values.
Actual native receipts retain the original element after live-state changes;
copied masks, wrong recipients and retired containers cannot borrow it.
Native late wrapper135750 and20 real AI score rows consume the same rules.
Tests protect live state, RNG, owned receipts, query roots and executable IWRAM.

Playback uses real learned command menus and native movement/selection:
self/hostile Fireblade, Fire/Flare Release and Fire/Ice Gaia, each under
matching/nonmatching elemental rules. A declared all-material Giza tile is a
test input, shared with the existing Geomancy fixture. It does not replace
selection, execution, hit results, rendering or law evaluation. All12 casts
reach the actual late Judge query; fuel consumption and renderer guards pass.
Both runs passed on their first execution. Root reviewed source ownership,
native caller operands and scope before accepting the batch. No full-suite,
cold-save or campaign replay was performed.

## Item, weapon and HP/MP classification

Native kind4 at13456E tests the Item-use boolean, so recipe commands383..392
previously escaped it despite consuming inventory. The new selector identifies
those commands as item use without changing their action identity or abusing
the native fourth argument. Ordinary actions0..346 preserve the native boolean.
Movement stays exempt; native actor KO/Petrify and late hit gates stay intact.

Native kind10 only reaches its weapon enumerator when action selector3 is
nonzero. That missed katana restoration/protection, enemy Last Resort and
Break Blade. Explicit weapon delivery now classifies all Iaido, sword Dark
Arts and enemy Last Resort, Strong Arm/Pillage, Sword Dance, Mystic blade
commands except Release, and Soldier/Gladiator axe techniques. It uses the
actual first weapon in equipment order, not native attack-strength sorting or
an unused offhand. Self Last Resort and weapon-free utility remain exempt.
This does not alter combat flags, equipment legality or damage calculation.

HP-law kinds11..14 consume signed recipient HP changes only. Medicine tests
verify exact native threshold comparisons for all ten recipes and their
selected ingredients, both races, full and depleted resources, remedies and
revivals. MP restoration does not become HP healing; full-health medicine still
counts as item use. Recipes debit each ingredient once, independently of law
queries. No fabricated damage or success flags are used.

| Run (UTC) | Scope | Result |
|---|---|---|
| `20260916T153827.916922Z` | Required build/native prerequisites; category matrix; direct elemental and custom-status consumers |12/12 selected steps pass;45,560 new assertions and56 actual recipe casts |
| `20260916T154033.891688Z` | Real Potion/Ether/Mist menus and late Judge reporting |Ten completed passing casts retained in completed.json; final empty-ground setup failed an incorrect confirmation assumption |
| `20260916T154249.216039Z` | Only the corrected empty-ground selection case, cached prerequisites |11 checks pass: no confirmation, execution or debit; returning cursor to self confirms normally |

The category matrix covers85 new actions, self/other modes, two weapon orders
and no weapon, both stack residues, plus1,388 ordinary Item-boolean controls.
Mixed-race weapon pairs are classifier inputs, not claims about legal loadouts.
Queries preserve actor/target records, owned statuses, stock, RNG and lower
IWRAM. The retained player flows cover Potion and Ether at low/full resources
and Healing Mist, each under Items and HP-healing rules. They execute the
ordinary learned menu, payment, renderer and real late Judge caller. No broad
suite or cold-save repeat. Root reviewed approved delivery rules and native
selector/caller gates before accepting this bounded batch.

The tested empty-ground selection does not reach payment. This is not a proof
that every forced executor or AI empty-area path is rejected; those remain an
explicit audit item if such a reachable path is found. Do not invent a result
recipient solely to force law reporting. Actual cards and persistent penalties
remain V06. Weapon classification has native selector coverage here; this batch
does not claim new rendered weapon-law casts or completed AI acceptance.

## Remaining audit

Complete mapped command/theft restrictions across the85 approved commands,
weapon-derived elemental classification, relevant native buff/status masks and
field placement with no recipients. In particular, the preceding elemental
batch covered fixed Mystic and dynamic Gaia/Release, not all weapon-elemental
arts. Audit ordinary support-triggered healing separately from primary command
healing; preserve native reaction exemptions where appropriate.

For each remaining category, retain native gates and test its actual AI or
committed Judge consumer. A changed image hash alone does not justify a full
suite, cold save or campaign playback. Final assembled acceptance owns complete
weapon-law playback and card penalties; do not close I09 from partial queries.

## Next-batch source evidence

Read-only audit afterc122011, on1427bd3d:

- Native kind1 calls133D78 to resolve the equipped command family. Installed
  `ffta_action_command` returns the actual new command ID; it does not map
  Reaving theft to original Steal. Original Steal is family23 (native law5
  contains kind1,value23). Pickpocket366, Strong Arm367 and Pillage370 need
  explicit theft-family treatment while retaining their own command identity.
  Axe additions should still resolve their existing Battle Tech/Spellblade
  Tech families through the normal native command lookup.
- Native kind3 uses CCD50 selectors12..15 (action flag bits1..4), independently
  of kind1. Do not infer these four groups from a donor's command name.
- Native element routine12F8A4 reads static action element, then item element
  (CA7A4 selector4) only if weapon mode is nonzero. Native law kind2 reads only
  static element. Actions361/362/367/370/408/424 have static0, weapon mode1;
  relevant weapon-derived law reporting therefore needs separate transport.
- Last Resort360 has both static0 and weapon mode0. Its physical reference
  passes the original action ID and primary weapon to12FE38. Audit actual
  elemental damage as well as the law before assuming only reporting is
  missing. Self mode is weapon-free and must remain distinct. Current source
  evidence is a concrete lead, not a newly executed damage comparison.
- Existing elemental test inputs are vanilla item13 (sword,Ice),60
  (greatsword,Ice),68 (broadsword,Lightning),91 (rapier,Fire). All new teaching
  axes are non-elemental; classifier stress inputs must not be described as
  ordinary obtainable elemental axes.

The next coherent correction should keep original command IDs, honor theft
independently of the following damage, and preserve any executed weapon-derived
element before reactions can alter gear. Reuse authenticated result ownership;
never infer late effects from an arbitrary copied mask. Declare the exact
native/AI/late consumers before its first runtime run. No additional runtime
was performed for this audit, and no gameplay source changed afterc122011.

## Weapon-derived elements, theft and Last Resort

Accepted bounded candidate `96ff816d6bad946c34f9c5e07e109b52ddce5e48`,
shared base `b26778520203359c3b129bcc025b92dd0e4c01f1`. The preceding
`f545cb2e7322ff1389693c461d23b9738f0431bb` differs only by the final
Last Resort self-target record correction and dependent private build bytes.

Fourteen weapon-elemental arts now use their actual primary element for native
law prediction and retain it in the existing authenticated result receipt for
late reporting:360..362,367,370,408,424..431. A non-elemental execution stays
non-elemental after gear changes. A second observation cannot overwrite the
original element; wrong recipients, copied masks and retired results fail.
Self Last Resort stays exempt. No saved state or workspace size changes.
Spellbreak421 was identified during final review as an additional required
consumer; it is explicitly still open rather than covered by this list.

Pickpocket, Strong Arm and Pillage additionally obey original Steal family23,
while keeping Reaving118, their real command IDs, AP and loot behavior. Native
successful-theft rows remain eligible for Judge reporting even if subsequent
physical damage misses. Other native command-family mappings remain unchanged.

The baseline damage audit155052 reproduced Last Resort dealing1HP regardless
of weapon affinity. Its weapon-free record sent the enemy formula through the
zero magical coefficient and no weapon element. The physical coefficient hook
now selects ordinary primary power only for360, and its element hook uses the
actual item operand. Both keep the original action ID and all existing cost,
status and support consumers. Native A0014 additionally required selector11
(flag bit0) for the approved self mode; the builder now sets it. Armed and
unarmed self use remains non-damaging and pays8MP once; prior Last Resort's
existing1.25 damage multiplier remains applicable to hostile use.

| Report UTC | Evidence |
|---|---|
|155529.251374Z|Eight build/capture steps passed; exact native comparison exposed the new owned axe receipt, not a gameplay regression.|
|155922.554700Z|Corrected exact64-byte receipt comparison passes; all other RAM, including rejected431, retains full comparison.155842 preserved the initial incorrect431 receipt expectation.|
|155942.494537Z|Six direct consumers pass:94,229 theft assertions plus Dark Knight, Dancer, Mystic commands, Fight laws and preceding elemental carriers. New element test exposed an incorrect prior-buff oracle.|
|160030.464914Z|Corrected10,558 element assertions pass onf545:42 non-elemental and36 elemental actual casts; both-race self/cost/primary-power cases.|
|160245.451270Z|14 actual native AI law rows pass; player self confirmation exposes the missing self-target bit.|
|160427.383244Z|All14 other real menu-to-Judge flows pass,166 assertions, including successful theft despite missed damage.|
|160847.494872Z|Final96ff build/native prerequisites and2,686 focused Last Resort assertions pass.|
|160929.381354Z|All12 Human/Bangaa armed/unarmed self and elemental enemy menu-to-Judge flows pass,146 assertions. AI selector failed only a missing sys import.|
|161028.951935Z|Corrected focused AI script passes18 assertions on two actual Last Resort rows; unchanged build/captures verified.|

All report prefixes are September16,2026 (`20260916T`). Fixed inputs, logs,
images, captures and ROM hashes remain private under the recorded reports.
The union of retained and focused evidence accepts this batch, not the entire
expansion. No full suite, cold-save or campaign repetition. Native card animation
and persistent penalties remain V06. Root reviewed hooks, caller operands,
exact receipt normalization and prerequisite provenance before this checkpoint.

## Spellbreak follow-up and remaining classification evidence

Candidate `a2a1958f9a5809a66e682cb38be7890f9010565e` adds421 to the same
weapon-element selector. No formula, cost, choice, effect or storage change.
This brings weapon-derived transport to15 arts. The active Spellblade
preparation is deliberately not used by Spellbreak damage or law reporting.

Run `20260916T161420.798218Z` passes the ten selected prerequisite/focused
steps and9,116 assertions:72 native casts (two legal rapiers, two selected
buffs, three seeds and three affinities), eight actual native AI rows, pure
queries, immutable receipts and native late wrapper reporting. Elemental
immunity still permits a successful selected-buff removal with zero damage;
foreign masks, wrong recipients and retired containers cannot borrow identity.
An existing Blizzard enchantment survives Fire-rapier and neutral-rapier casts.

Run `20260916T161555.622254Z` passes112 assertions across eight actual
menu-to-Judge casts: Shell/Protect choices, Fire/neutral rapiers and matching/
nonmatching laws. Retained failure161505 occurred before execution: the test
assumed the cursor started on disabled row1, but native selection starts at
first usable Shell7. The retained screenshot showed Inoculated13. Only the
fixed scroll offset changed; selected action/choice remain explicitly checked.
The corrected test reused hash-verified preparation and did not rebuild or
repeat the direct matrix. Earlier carrier/consumer evidence remains retained.

Read-only next-scope audit: native kind3 reads action selectors12..15, bits1..4
of the word at record+16. All347 vanilla and85 new action records have those
four bits clear. Preserve this existing behavior; do not invent a group from
a donor name. Native kind1 handles actual original command families separately.
Rule-bank kinds15/16 provide specific native statuses and the harmful group,
not a general beneficial-status rule. Native Shell24 and Protect25 still need
actual publication checks for the relevant composite new buffs. Placed fields
use paid action completion even with zero recipients (`ffta_geo_field_action`);
the empty-result reporting boundary still needs its own source/caller audit.
No game change or runtime acceptance is inferred from these static findings.

## Composite buffs and field boundary acceptance

Final bounded I09 candidate `5a01c78e45a32768a7568617a931c50a7b5300f3`.
The audit162050 executes60 composite/custom beneficial casts. Every actual
native result mask, including Earthen Ward, is already correct. Its only eight
failures are Dark Mind/Shell and Hide/Invisible predictions: native1347D0..134812
allocates separate actor and recipient copies for the same source. Pointer-only
self checks incorrectly rejected them. No descriptor-mask change was justified.

`unit-query.h` recognizes the same authenticated source origin only when the
context is explicitly a query. It admits registered copies but rejects unrelated
sources and unregistered byte copies. Actual execution still requires exact
pointer identity. Dark Mind admission/healing and Hide admission now use this
helper; no status effect, save schema or allocation changes. Silence remains
allowed for these two actions; Disable and KO retain their admission behavior.

| Full report UTC | Accepted scope |
|---|---|
|20260916T162306.091905Z|12 selected steps pass, including native925 assertions, Bard903, existing Dark Knight batch and4,888 new buff/ownership assertions.|
|20260916T162614.541935Z|Cached prerequisites plus all three caller tests pass:36 assertions/six actual AI rows,182 assertions/14 racial buff menu casts,124 assertions/eight field menu casts.|

The60-cast matrix covers Kiyomori, Dark Mind, Last Resort, TBN, War Cry,
Updraft, Earthen Ward, Inoculation, Guarding Draught, Battle Chant, Magickal
Refrain, Angelsong, Hide, Nameless Song and self Fire Spellblade, at two seeds
with fresh/refresh native statuses. Native Shell24, Protect25, Regen3 and
Invisible12 predictions and late masks agree with execution. Custom buffs have
no false native-status or harmful-group identity. An independent read of all60
retained complete status/result masks exactly matches these native sets. The
96-input copy matrix also verifies query/execution mode, self/foreign/raw-copy
identity, health/Disable/Silence and live state/RNG/executable-memory purity.

Actual player cases include both Dark Mind races, Hide, Earthen Ward, both
Guarding Draught races and Nameless Song. The installed native AI routine
produces correct self-buff law flags for both Dark Mind races and Hide. Some
specific status values (for example Invisible12) use a test-only rule record;
this proves evaluator transport without introducing a new campaign law.

Occupied Rime reports its Ice element through the actual Judge. Empty Rime and
Refuge still spend12MP once and create the correct field at the chosen center,
with zero recipient rows and normal return to player control. Native135004..
135022 skips absent/missed/unsuccessful result recipients before its late query;
the expansion preserves that gate. Occupied Refuge has no invented Protect or
harmful-status violation. Persistent field placement is not a unit ailment.
These controls do not claim to show persistent field outlines: I07 remains open.

Root reviewed the exact identity change, native caller gates, pure queries and
retained evidence. I09's implementation/classification scope is now closed by
the union of its declared targeted reports, not a single broad suite. V06 still
owns actual card animation, penalties and campaign rule rotation; final assembled
acceptance must verify the combined release. No full suite/cold-save repetition.
