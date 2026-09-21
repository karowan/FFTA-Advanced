# Chop hostility, weapon effects, and geometry council review

**Migration recheck:** native Blank Card346 was discovered during the subsequent table-domain audit, moving custom actions up one and Chop423→424. The same eligibility suite now derives Chop from the combat manifest and covers all347 original actions. **21,883 checks pass** on combat `9f773e96fa6f98ceb9fc443ee96c56a8a64c4adc`, engine `58c534a82d297fdebcf2db8c156b0000b167045c`. The detailed423-era evidence below remains tied to its recorded historical hash; targeting/geometry contracts are unchanged. See `relocated-table-domain-review.md` for the preserved Blank Card regression and complete rebuilt acceptance.

The installed eligibility callback passes the independent tests after removing its stored-coordinate check. The original descriptor callback has no evaluated movement coordinates; range belongs to the native target-geometry layer. This corrects a real Move-preview failure observed by the parent, rather than weakening a required game rule.

Reviewed build: combat `dc02c7b68c950a503441735b1a0d168c847784cd`, input `f47cf7c35f3b47e2e16204d98f9075d9d1c1f93b`, engine `7b954b8185755f6794d910c9137d4e2f472dc241`. Tests freeze the current ROM, input, manifest and matching symbols into `build/expansion/probes/chop-eligibility-council/<hash>/`; they reject inconsistent current build artifacts. No engine files or user games/saves were modified by this review.

## Native allegiance contract

All addresses below are full GBA addresses unless a leading `0x08` is omitted for readability.

| Native function | Contract |
| --- | --- |
| `080C8240(unit)` | Boolean base enemy flag: `u16(unit+28) & 8000`. Null returns zero. |
| `080CDB54(unit)` | Boolean Confusion: `unit[EB] & 10`. |
| `080CDB6C(unit)` | Boolean Charm: `unit[EB] & 20`. |
| `080CE124(unit,value)` | Sets/clears only the Charm bit at EB. Does not change base side. |
| `080CE468(unit,value)` | Stores Charm duration byte at E2. |

Native AI's block `080C1ED2..080C1F12` begins with the actor's base side. If the actor is confused it substitutes RNG parity; if the actor is charmed it then XORs the selected side with one. The target's Charm is not applied to the base-side target lists. The independent test executes this exact instruction block, including its real getters, for all sixteen base-side/Charm/Confusion/RNG-bit combinations. Only the RNG provider is controlled in these Confusion demonstrations.

Consequently Chop's deterministic custom predicate is:

```
actor and target exist; actor != target; target HP != 0;
actor is not confused;
(baseEnemy(actor) XOR charmed(actor)) != baseEnemy(target);
first equipped weapon is an axe.
```

Do not XOR target Charm, borrow a live owner's faction, or call RNG during eligibility. Confusion normally forces Fight; failing closed on a direct confused custom-action invocation avoids a random preview result. This policy affects Chop only. In particular native ally-only callback `08130A58` compares base sides without this AI Charm adjustment; it must not be globally replaced.

Native Charm application `08133540` sets receiver Charm through CE124 and duration three through CE468 outside preview mode. This application context's receiver is word +8, while the eligibility context's target is word +4. Do not conflate those fields when instrumenting reflected or redirected application.

## Control owns a command relationship, not a changed target faction

Beastmaster actions189–201 select native application `0813363C`. Outside preview (`context+26 & 10`), it calls `CE2F0(actor,1)` and `CE488(actor,receiver[104])`. These store the controller's ED bit08 and E6 controlled-unit battle ID. The controlled receiver is unchanged. `CDCA4` reads the controller bit; `CE410` reads E6.

Native `080970E8(manager,unit)` resolves a controller by scanning battle wrappers, requiring a controller flag, matching its stored E6 against `unit[104]`, and native can-act eligibility. It returns the qualifying wrapper with the smallest signed wrapper+5C value. This is command routing, not proof of a permanent faction flip. Chop must not silently substitute a controller's faction or locate the live roster owner of an evaluated copy.

`scripts/probe-chop-hostility-procs.py` executes native CE124 and the getters for all256 initial EB values, both set/clear values and both base sides. It also executes the real Control application for four target IDs, both sides, preview/commit and both stack residues. Exact actor/target/context snapshots establish the ownership and preview behavior above: **4,265 checks pass**, including item-help checks below.

## Geometry and the Move-preview fix

The parent reproduced an actor that had moved visually to (4,14) while the unit record still contained (2,13). Target highlighting correctly used the moved location. Reading actor F6/F7 again inside the descriptor predicate rejected the highlighted adjacent target. The callback provides unit pointers/action, not the evaluated coordinate pair; a global lookup would also break copied simulations.

The correct native boundary is already present:

1. `080B4A1C` generates target tiles from a geometry descriptor: unit pointer+0, evaluated X/Y bytes+4/+5, action halfword+8, item halfword+A. It does not need the unit's stored coordinates for this origin.
2. Its shape branches use `080B4678` / `080B479C`, which call `080A0014(unit,actorX,actorY,targetX, targetY,action,item,mode)`.
3. Rush/Chop selector4 bit80 selects weapon geometry `0809FEF0(unit,actorX,actorY,targetX, targetY,item,mode)`.
4. Ordinary axe geometry calls `0812E1A8(unit,actorX,actorY,targetX, targetY,item,flags=1)`. This reads actual tile heights using `0801CC18(x,y)`.

For ordinary melee including axe category31, native `12E336..12E352` requires Manhattan distance at most one. `9FEF0` separately rejects the same tile. The height branch `12E2C8` accepts `(targetHeight - actorHeight) + 3 <= 5` using an unsigned comparison, hence directional height difference **-3 through +2**, inclusive. F8 is facing, not tile height. Keep the donor's native rules rather than inventing a symmetrical absolute-height check.

Direct B4A1C callsites found: A3EC4, B59A0, B6904, BE2BE, BE63E, BE7F6, BE95C, BECD4, BEFF4, BF124, BF152, BF884, BFEBC, BFF32 and C0028. This shared target-list path includes the battle/AI candidate region. This bounded static trace is not an exhaustive proof that every law/application path invokes geometry immediately before every copied callback. A law simulation may legitimately evaluate an already selected target without rebuilding its range list. That is another reason not to invent a new position contract inside the effect callback.

`scripts/test-chop-eligibility.py` executes the real B4A1C shared list builder with deliberately stale actor (2,13) and evaluated origin (4,4), both normal and copied actor addresses. It checks the exact four adjacent tiles, removes the height-invalid neighbor, verifies output guards, and verifies the evaluated unit remains unchanged. Native A0014/9FEF0/12E1A8 tests cover distance0–3, height -8..+8, three weapons, invalid tiles and blocking flags. Only the map height/validity service functions are controlled. These are meaningful native boundary tests, not a rendered real-map or complete AI-turn test.

## Weapon status effects: important distinction

The apparent status tags on many original weapons are defensive immunities. Native compressed item-help decoding establishes:

| Item | Effect byte | Native help meaning |
| --- | --- | --- |
| Ancient Sword53 | 34 | null Petrify |
| Diamond Sword54 | 2B | null Slow |
| Hardedge55 | 32 | null Doom |
| Vigilante56 | 31 | null Confusion |
| Zankplus57 | 37 | null Poison |
| Master Sword58 | 35 | null KO |
| Oblige59 | 2C | null Charm |
| Iceprism60 | 36,02 | null Silence/Fire |
| Lurebreaker61 | 33 | null Sleep |
| White Staff121 | 3E | Removes doom from target |
| Cure Staff124 | 3F | Heals target's HP |

The repeatable native decoder stores both raw decoded bytes and searchable text in `chop-hostility-procs-tests.json`. Do not turn the defensive immunity scan into an on-hit suppression hook merely because its tags contain status names.

The bounded native code audit found these actual attack effects:

- `08130654` recognizes 3D drain. It affects the native physical formula at1300BC and ordinary action drain bookkeeping atA30AA; the separate Fight-region caller is A2B0C. A Chop-specific exclusion must cover formula and outer application bookkeeping while retaining Fight.
- `08130688(item,action,target)` recognizes only3E. It clears Doom through CDFE4/CE420. Its three direct callers are A2706, A2DC8 and133954, the last inside the ordinary13388C postprocessor. Returning early only for423 at this entry is the narrow exclusion; a magnitude-only change would miss the later postprocessor.
- `08130620` recognizes3F and drives the native healing sign reversal. Preserve the approved healing behavior and zero/absorb interactions independently of excluding drain/Doom removal.
- `0812ED04` is a read-only any-equipped-effect query. `0812ED58` reapplies equipment effects40/41 through general status-refresh logic; it is not an on-hit application and should remain intact.
- `0812D07C` scans item+1A..1C through12CB64 for status compatibility; the scan alone is not an application/proc. Equipment elemental modifiers likewise should remain intact.

No additional general weapon on-hit status executor was demonstrated in this bounded audit. This is not a proof that arbitrary future equipment effects are safe. Stage1/2 no-ops, retaining generic A-action execution, and narrow3D/3E exclusions are evidence-based; a speculative broad status hook is not. The engine council owns committed-action tests with synthetic effect-bearing axe records. Empty-effect ordinary axe donors cannot by themselves prove exclusion of3D/3E or other effects.

## Installed callback results and remaining acceptance

**21,867 checks pass** in `scripts/test-chop-eligibility.py` on the frozen combat hash above:

- All346 original action IDs through the installed descriptor pointer versus native130A94, both stack residues and dead/live/null target cases.
- All461 item IDs in all five equipment slots: primary weapon equals native ordered12E4F4; synthetic invalid IDs are skipped safely. First weapon, rather than strongest weapon, controls axe eligibility.
- Every axe, copied pointers, unrelated support data, all allegiance/Charm/Confusion combinations, null/self/dead targets, and 1,296 stored-coordinate invariance cases.
- Native effective actor-side block, native geometry, shared target-list outputs and guards.
- Hard failures for any eligibility RNG call, non-stack memory write, C-entry misalignment, preserved-register change or unbalanced stack.

These results do not certify combat damage, animations, complete AI decision-making or committed law bookkeeping. The parent is exercising the real battle and the engine council is checking formula/application effects. The earlier integration-review recipe saying a direct descriptor call must reject distance/height is superseded: rejection belongs at the explicit native geometry boundary.
