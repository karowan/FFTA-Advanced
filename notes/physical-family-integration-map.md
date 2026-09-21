# Reusable physical-action integration map

Read-only council map against current canonical `JOB-CLASS-SPECIFICATION.md`, generated registry and clean native ROM. This is an implementation plan, not a declaration that allocated lessons work. Generated macros must supply IDs; original0..346 remain unchanged.

## Shared core rather than one engine hook per lesson

Use one const definition table with explicit enabled entries. Each definition supplies primary weapon mask, allegiance policy, coefficient numerator/denominator, element policy (primary/none/fixed), target geometry, cost policy and typed before/after events. Do not infer mechanics from job or name. Existing native descriptor3F is the common physical damage path; existing shared wrappers can look up this table and immediately delegate for absent entries.

The current Chop hooks already provide the common eligibility, primary selection, magnitude, final coefficient, restorative sign, native weapon-drain suppression and3E exclusion. Generalize their single-ID predicate to an enabled physical definition. Keep ordinary accuracy13112C ->12EF94 ->12C7F4 and outer131378 compatibility/reaction handling. Original action0/Fight remains outside this table; no new offhand, crit or Doublecast paths. Classification and Spellweave sequencing must be separate fields; future Spellblade strikes are physical damage but sequence Magic.

Important element pitfall: native12F8A4(actor,action,item) reads action+02; zero falls back to the primary item element if action+05 is nonzero. **Do not encode non-elemental Samurai/DRK by setting +02=0 alone.** Keeping weapon-associated physical mode1 while forcing no element requires an explicit per-definition element policy at this helper or its audited formula call. Setting weapon mode0 instead also changes native physical scaling and is not an equivalent fix. Fixed Wind/Dark can use verified native element IDs in +02 after checking native spell records; weapon element retains0/mode1.

Native12FE38 computes attack via12FD44 and effective defense via12FDDC, each capped999, before12FE28 at12FEB0. Armor Splitter and Flare need a definition-aware effective-defense operation before this subtraction. Multiplying final P cannot emulate75% WDef. A narrow hook around12FEA8..12FEB0 is a candidate after exact instruction-span/ABI verification; do not directly rewrite a copied or live unit's WDef. Keep ordinary supports and Protect in the native input path. One final rational product at1300E2 prevents premature rounding across coefficient/Centered/other bonuses.

## Canonical martial rows

| Family | Rows | Additional primitive beyond common physical core |
| --- | --- | --- |
| Axe basic/reach | Chop424, Tomahawk425 | 11/10 and9/10; Tomahawk4MP, fixedr4/height3 and explicit LOS |
| Axe area | Overpower426, Reaping Arc429 | one selected frontal arc, three recipients, friendly fire, per-recipient A,9/10 or11/10; pay once |
| Axe defense | Shatter Guard427, Armor Splitter428 | successful-hit Protect removal BEFORE P;75% effective WDef for one hit, respectively |
| Axe finisher | Executioner430, Fell Cleave431 | snapshot targetHP<=half for18/10 and final+20pp cap95 (otherwise11/10); Exposed before hit even on miss, respectively |
| Samurai basic/reach | Ashura347, Osafune349, Guarding Draw352, Kiku-ichimonji353 | non-elemental primary katana;110/100,85/100,100/100,145/100; positive-damage Centered, capped MP removal, after-attempt Protect, Centered consumption/scaling as specified |
| Samurai area | Wind Draw348, Moon Blossom354 | cardinal line3/Wind/1P or self-cross/enemies/non-elemental135/100; Centered once for whole action; Moon Regen once after any positive recipient |
| Samurai wound | Higanbana355 |80/100 initial; pre-bonus P snapshot; two scheduled removable wound pulses, not repeated attacks |
| Dark sword core | Blood Edge356, Sanguine Sword357, Infernal Strike358, Crushing Blow361 | sword/greatsword/broadsword mask; Dark150/100 + HP cost; non-elemental95/100 actual HP drain; non-elemental75/100 actual MP siphon; weapon115/100 then separate half-S Stop |
| Dark area | Abyssal Blade362, Unholy Sacrifice363 | line3 any/falloff140/125/110 or self-cross any excluding self175/100 Dark; atomic HP+MP cost once; Slow half-S per positively damaged recipient for latter |
| Dark stance strike | Last Resort360 | self Sure orr1 enemy A with any damaging primary;1P then linked status even on miss; buff cannot boost initial strike; Healer strike forbidden |
| Viking theft strikes | Strong-Arm367, Pillage370 | axe85/100 or1P; independent original theft transaction BEFORE damage calculation, even if damage misses; original loot restrictions and own theft accuracy |

These are24 physical rows in SAM/DRK/VIK/axe, but only Chop is currently accepted end to end. Kiku's direct damage may share the simple coefficient path, yet it cannot be declared complete until Centered works. None of the theft/cost/status rows is an honest complete implementation if only its damage coefficient exists.

Other clear reuse candidates: Dancer Sword Dance408 is actual primary knife/rapier160/100; Dancer Pdance actions require their separate virtual-weapon baseline and must not silently call ordinary primary P. Mystic Knight strike modes410..421 can reuse the core only after dual self/strike selection, persistent enchantment and Magic sequencing are implemented. Break Blade423 is S/Petrify with no HP damage; Arcane Release422 uses magic and cannot be put into the physical magnitude family. Viking Thunder/Stormcall/Thundaga/Tsunami likewise use the separate M formula.

## Verified native geometry donors and gaps

`scripts/probe-physical-native-area.py` runs actual clean native A0254 and B4A1C using the real map grid. B4A1C descriptor has unit+0, actorXY+4/+5, selected centerXY+6/+7, action+8,item+A. Its mode argument2=1 builds affected area and argument1 selects cardinal direction. Native output records are4 bytes; caller must supply enough room and retain guard checks.

At center6,6, all four directions:

- Wild Swing113, Whirlwind102 and Saint Cross92 yield exactly four orthogonal neighbors, exclude center. Wild Swing is mode1 physical and useful as a self-cross damage donor.
- Sonic Boom180 yields center plus four orthogonal neighbors: a true five-cell cross, range4, mode1 physical. Useful mechanics donor for cross geometry, not automatic enemy/ally filtering or approved animation.
- Earth Render103 yields a selected cardinal ray to map edge. It is NOT an already bounded line3 and uses mode0/power34, so do not copy its damage record for weapon P. Bounded line3 needs explicit length/height/impassable-stop policy.
- A0254 alone returns a broad geometric membership bound (e.g. radius4 for Wild Swing), not the final affected tile set. Testing only this function would incorrectly report41 targets. Test the real list builder and execution recipient list.

Frontal arc is not Wild Swing: center-front and the two diagonals in the selected facing must be generated explicitly and rotate correctly. A single area-list/geometry extension can serve both axe arcs and the two line3 techniques. Keep per-recipient enemy/any filtering separate from tile geometry. Use evaluated explicit coordinates for Move/AI/copies, not unitF6/F7. Native range donor147 and projectile LOS gap are detailed in `tomahawk-integration-review.md`.

No status-before-damage or custom area hook is installed by this note. Native area probes:605 raw membership executions and20 complete area lists, with guarded outputs, recorded in `physical-native-area.json`; these are geometry tests, not full attacks.

## Minimal lifecycle interfaces that prevent incorrect timing

Three events suffice conceptually, but their exact committed native hook sites require trace tests before installation:

1. **Action commitment, once:** validate all resources and target form; capture explicit coordinates, cost, selected status/theft type, pre-action status snapshots, whole-action Centered/Fury. Pay once; apply Fell Cleave Exposed before rolls; never mutate from repeated preview/AI queries.
2. **Recipient successful-hit boundary:** after A and preventing interceptions but before P, Shatter Guard/Spellbreak remove the selected status and calculate against remaining defenses. This cannot live in the unconditional magnitude callback unless it operates on isolated prediction copies and the committed path applies it once. Strong-Arm/Pillage are a different before-damage event with an independent theft roll; damage miss must not suppress it. Recompute damage after stolen equipment changes defenses.
3. **Recipient resource application / action completion:** capture actual HP removed after redirect/interception/overkill cap. Use actual positive HP removed for drain/MP riders; never use displayed P. Apply positive-damage status riders only then. After-attempt self buffs apply even on miss once; aggregate-any-positive Regen applies once after all recipients; expire/consume whole-action charges once. Preserve undead reversal and restorative prohibition.

Do not reuse13388C postprocessor as a presumed pre-damage hook: it is an application/postprocessing path and includes the native weapon3E call133954. Descriptor application13215C being noop does not mean outer HP effects are absent. Eligibility target is context+4, while actual receiver in application can be context+8; redirected/reflected/law copies must use the phase-appropriate pointer.

The concrete next safe implementation is the shared physical definition lookup with original fallback, Tomahawk range/LOS and a single extra coefficient. Then build one before-hit transaction and one bounded area policy with native preview/commit evidence before enabling their dependent rows. No per-lesson duplicate formulas, no hidden native substitutions, and no blanket enabling of inert registry rows.
