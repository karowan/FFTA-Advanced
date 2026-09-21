# Chop native integration review

2026-09-14. Read-only audit of clean USA ROM SHA-1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`, plus proposed `src/engine/axe-visual-hooks.s`. Addresses below are ROM offsets (add08000000 for CPU addresses). Disassembly evidence is saved as `build/expansion/probes/chop-*.txt`. No engine edits or gameplay acceptance are implied.

## Recommended minimum path

Keep Chop as action423, a normal A-ability, with one physical stage3F and no-op stages1/2. Preserve native eligibility dispatch, accuracy dispatch, signed magnitude dispatch and outer HP application. Add a new-ID eligibility branch and a new-ID magnitude wrapper that chooses the actual primary weapon. Apply the combined rational damage modifier before the existing signed cap at1300E2. Add a new-ID exclusion for weapon effect3E and explicitly exclude drain3D while retaining the approved healing interaction3F. The latter two are different native behaviors; one blanket weapon-effect toggle does not express this contract.

## Donor and eligibility

Rush112 record is:

`e4 01 00 0a 00 01 80 80 01 01 00 00 3f 4b 01 01 20 72 14 00 6d 00 a5 00 00 01 50 00`

Relevant fields: element0, MP0, weapon-associated mode1, native range bytes80/80/01/01/00, flags00147220, physical stage3F followed by knockback4B. Replace stage1 with no-op1 and retain stage2 no-op1. Descriptor3F is `[8,21,10,30]`: eligibility130A94, application13215C (`bx lr`), accuracy13112C, magnitude13189C. Copying the entire Rush effect vector incorrectly adds knockback. Copying its weapon-relative range without an axe check permits inappropriate equipment ranges.

**130A94 is only an alive-target check.** It loads context+4, calls C8280 and returns the inverse. C8280 means currentHP is zero. It does not check enemy allegiance, adjacency, height, weapon type or self-targeting. A safe action423 branch must reject null/same actor and target, retain the native alive check, verify a primary category31 axe, and require Manhattan distance1 using signed battle coordinates unit+F6/F7. Leave native donor height/geometry processing in place; a Manhattan check alone is not a replacement for map/height validation. Reject missing/offhand-only axe and illegal distant targets even when the caller directly invokes the callback.

C8240 reads unit+28 bit8000, the original enemy flag (also corroborated by the vendor unit-flag map: byte29 bit80 enemy,20 guest,10 judge). Comparing actor/target original enemy flags distinguishes the normal opposing sides and does not misclassify guests as enemies. **Charm/control allegiance needs an explicit native-behavior fixture before treating this base flag as the full effective-hostility contract.** Do not confuse unit+9 with team: it is level; nearby130AAC modulo10 comparisons are level targeting.

A new branch at eligibility callback entry130A94 can delegate every original action unchanged. Alternatively a private new descriptor may select a wrapper, but descriptor allocation must stay within the byte namespace. Do not globally alter original Rush eligibility.

## Primary weapon and accuracy

**Do not use12F0D8 as the primary-weapon getter.** It calls12E55C, obtains up to two weapons and sorts them by weapon attack at12E586–12E5AA. A stronger offhand can become result0. The order-preserving getter12F0CC calls12E4F4: it scans equipment selectors1D–21 in slot order, accepts native handedness1/2 and excludes shields/category20. It initializes and writes two halfwords, so its output buffer must be at least4 bytes. Valid game equipment limits it to two weapons; malformed five-weapon fixtures should not be fed an unguarded4-byte buffer. Directly scanning the five equipment slots with bounded storage is another safe implementation of the first weapon in equipment order.

Native verification on axe-visual SHA-1 `3d664d20c82b09a13aaa227057fc55a5e422d3f4`: all eight new axes453–460 are accepted by all four getters, with guard bytes and unit contents preserved. The two-weapon fixture `(Recruit Axe453, Barong52)` returns `(453,52)` through12E4F4/12F0CC and `(52,453)` through12E55C/12F0D8. **36 cases pass**; script and JSON are `build/expansion/probes/test-chop-weapon-getters.py` and `chop-weapon-getter-tests.json`. This is a getter-order fixture, not a claim that this two-weapon combination is legal equipment. There is no combat-getter category1–19 ceiling: it tests handedness1–2 and excludes category20.

For Chop, validate that first weapon's real category is31 and use that same item ID for magnitude. Do not validate one axe and compute with a context item selected by the native strongest-weapon helper. Primary sword plus offhand axe must fail. Primary weak axe plus stronger offhand must retain the axe's power, element and allowed healing behavior.

13112C calls12EF94(actor,target,0,0,stack0). That is the native attack-style accuracy path using actor/target positions and facing (F6/F7/F8), with normal native stat/status checks. Keep the outer131378 dispatcher too: it performs application compatibility/reaction checks and the native accuracy overrides. Returning a hard-coded hit percentage or directly running only the callback would omit those layers.

13189C passes mode0 for normal execution or mode2 when context+26 bit10 is set (preview). It never passes critical mode1. Thus stage3F does not acquire the formula's critical multiplier. Keep action423 distinct from Fight/action0 and do not redirect it into the specialized Fight executor. The Rush flags leave selector13/bit8 clear, so Chop is not selected by the native Doublecast-eligible scan. Those field observations do not substitute for a committed executor test proving one hit, no second/offhand strike, no critical result flag and no Fight-only triggers.

## Exact damage insertion and sign handling

13189C ->13079C ->12FE38(actor,target,action,item,0,mode,0). At **1300E2**, immediately before the final cap:

| Value | Native location |
| --- | --- |
| Signed, uncapped P | r5 |
| Actor | r8 |
| Target | word at original frameSP+18 |
| ActionID | r10 |
| ItemID | r9 |
| Formula mode (normal0, critical1, preview2) | original frameSP+20 |

r5 already includes the native offense/defense calculation, native weapon/action-power rounding, element/resistance, status/support/law interactions, variance where applicable, and native weapon sign changes. The existing cap is signed[-999,+999] at1300E2–1300F0. A narrow action423 branch can replace r5 with one combined rational result and then resume the original clamp. Preserve native frame offsets before pushing registers; retain SP/r4–r11 and dynamically align any C call to8 bytes. Reproduce every displaced clamp instruction and check continuation addresses against installed hook spans.

For Chop alone, scale signed P once by11/10, with the explicitly chosen signed-rounding convention (recommended truncate toward zero, preserving healing symmetry). Combine any approved new outgoing/incoming rational factors before that division rather than repeatedly rounding. Use a proven bounded intermediate or sufficiently wide arithmetic; do not multiply a value already clamped to999. Examples: P910 reaches1001 then caps999; P-910 reaches-1001 then caps-999; P0 stays0. The physical baseline's existing integer rounding remains part of P, not a reason to rewrite native defense math.

Native element handling at130022: resistance code0 gives1.5x,2 gives0,3 negates (absorb),4 halves, otherwise unchanged. Later target statusCDA4C can set0. These zeros must not become minimum-one damage when applying the new rational modifier. Negative P must not be cast unsigned, clamped to zero or converted to damage accidentally. Preview mode2 bypasses native variance; preserve that distinction and RNG-call count.

12F8A4 chooses explicit action element when nonzero; otherwise weapon element when action weapon-mode is nonzero. Element0/mode1 therefore gives the approved weapon element. Native 1300BA–1300E0 then checks weapon3D and3F effects. Effect3D can conditionally negate against certain targets and also drives outer drain bookkeeping; effect3F unconditionally negates the signed result. If both absorb and healing apply, the native two sign changes can produce positive damage. Preserve or deliberately document/test that native interaction; do not silently replace it with unconditional healing.

## Weapon effects: separate mechanisms

- **130688 is only effect3E.** It checks nonzero item and either action0 or action selector3 nonzero, scans item+1A/+1B/+1C for3E, then callsCDFE4(target,0) andCE420(target,0). It does not implement the entire weapon-status/proc system. Direct callers areA2706, A2DC8 and133954.
- The last caller is the ordinary13388C application postprocessor; a stage3F no-op application callback still reaches it. Excluding3E only while computing magnitude does not prevent this later mutation. A wrapper on130688 that immediately returns for action423 and executes the original body for every other action is a narrow, complete exclusion for this effect's observed paths.
- **130654 recognizes effect3D**, not3E. Formula1300BC uses it; outerA30AA–A30CC also detects it and updates actor/action-result HP drain bookkeeping when action is weapon-associated. The separate Fight-region callerA2B0C exists too. Suppressing3E alone still allows drain3D. Exclude3D for Chop both in its baseline/sign calculation and at the applicable outer drain path; do not globally disable the item effect for vanilla actions.
- **130620 recognizes effect3F**, the unconditional native healing sign reversal at1300D6–E0. Preserve this approved healing behavior separately. Zero stays zero even after reversal.
- Native12ED58 also reapplies equipment effects40/41 to units through a general equipment-state path; it is not evidence of an on-hit proc and should not be globally disabled to implement Chop's no-proc rule.

General on-hit status effects are not proven absent merely by blocking130688. Stage1/2 no-ops and avoiding specialized Fight execution remove obvious inheritance, but acceptance still requires instrumenting the committed action with weapons carrying each native effect byte and proving no new status, drain, second hit or extra application occurs. The current ordinary axe donor may have empty effect slots; such an item alone is an inadequate negative test. Use disposable ROM-mapped axe records for these fixtures, without changing approved acquisition data.

## Axe31 visual switch proposal

The proposed four shims in `axe-visual-hooks.s` correctly map only derived switch input31 to Barong category5. Each original switch accepts categories1–19 and otherwise falls back. Original item IDs, stored category fields and gameplay getter results must remain31.

| Hook span (end exclusive) | Continuation | Category5 result |
| --- | --- | --- |
|986DA–986E6|986E6, after reconstructing table address|Table986F0 entry4 ->9873C; sets local visual familyr5=1|
|A58A0–A58AC|A58AC|TableA58B4 entry4 ->A5900; sound7B|
|A7EDC–A7EE8|A7EE8|TableA7EF0 entry4 ->A7F3C; sound7B|
|B3C64–B3C70|B3C70, leaving indexr0 and baser1 for nativeADD|TableB3C7C entry4 ->B3D08; callbackAE7D9|

These continuations are outside their replaced spans. The shims restore savedr3 and reproduce native r0/r1 switch outputs. Category5's two sound arms have no further item-category condition. The actor arm replaces r5 with a visual-family number before its later family checks, so preserving the true category elsewhere does not make those checks see31. The selected heavy-blade effect callbackAE7D8–AF22C has no direct CA7A4 category lookup; it calls the actor animation dispatcher9836C, whose category switch is the first hook above. This is bounded static support for the proposal, not a rendered animation test. Original categories0,1–19,20–30,32–255 must retain their native case/fallback behavior, and type31 should match type5's selected callback/sound without changing the underlying record.

## Acceptance recipes

1. Run every original action/representative physical weapon through the intercepted callback/formula boundaries and compare registers, result, mutations and RNG calls byte-for-byte with the baseline. Verify both SP residues.
2. Chop eligibility at the complete native geometry/effect boundary: adjacent enemy succeeds; self/ally, dead target, distance0/2/diagonal, no weapon, sword-primary/axe-secondary and illegal height fail. **Follow-up correction:** do not test stored F6/F7 inside the descriptor callback; these can lag Move previews. Native B4A1C/A0014 carry evaluated coordinates separately and own range/height. See `chop-hostility-procs-review.md` for native Charm/control contracts, tested boundaries and evidence.
3. Hold primary axe constant and vary offhand power, element, status and healing effects. Damage and permitted interactions must remain primary-only, with exactly one committed hit.
4. Deterministic native-formula fixtures cover normal, weak, resist, null, absorb, healing3F, drain3D, native support modifiers and targetCDA4C. Capture r5 at1300E2; independently calculate the one rational result and final signed cap. Include small magnitudes, exact rounding boundaries and both cap signs.
5. Execute actual eligibility/accuracy/magnitude/application and committed HP bookkeeping, with stages1/2 confirmed no-op. Synthetic effect3E must not callCDFE4/CE420; effect3D must not heal the attacker; allowed3F and elemental absorb must retain their defined signed behavior. No direct writes to live owners from preview copies.
6. Differential-test all four visual switch categories and then render ordinary Fight and Chop with each new axe. This proves the switches select usable native assets and that the real item namespace remains unchanged.
