# Chop geometry reconciliation

Canonical `JOB-CLASS-SPECIFICATION.md` line48 specifies melee height limit2. Native ordinary melee permits three tile-height units downward and two upward. Merely retaining Rush's geometry therefore permits one extra downward level and fails the approved symmetric rule.

New files `src/engine/combat-geometry.c` and `combat-geometry.s` add a narrow whole-entry wrapper at nativeA0014. The parent integrated and rebuilt them. **30,257 checks pass** in `scripts/test-chop-geometry.py` on combat `62c848bc42e92fd7652075b235c49347c6b23862`, engine `485c65b5985c7c104ccdfef4d80fc1b61a142fee`.

The wrapper forwards all eight native arguments, delegates the complete original geometry first, and changes only a successful Chop result whose two explicit evaluated map coordinates differ by more than two tile-height units. Every other action retains the native result. There is no global state, copied-owner lookup, unit F6/F7 check, RNG, or persistent write.

Native1CC18 reads the byte at `mapBase + 2*(y*mapWidth+x)` through02007F10. Native weapon and spell height comparisons use this returned byte directly. Therefore compare the same units; do not derive height from sprite Z/facing fields. Running native geometry first preserves bounds, terrain validity, impassable flags, shape and donor range behavior before these additional height reads.

## Installation contract

- Add the two files to the engine compile inputs.
- Add `(0xA0014,0xA0020,'ffta_combat_geometry_entry')` to the combat builder's existing save-r3 absolute-jump installer.
- Require the original12 bytes to match the clean ROM. The span displaces: `push {r4-r7,lr}; mov r7,r10; mov r6,r9; mov r5,r8; push {r5-r7}; sub sp,#24`.
- The native trampoline reproduces those instructions and resumes Thumb `080A0021` (instruction addressA0020), outside the hook span.
- The entry restores stub-saved r3. It saves r4–r7/LR and copies the four original stack arguments into a newly aligned outgoing argument area before calling C. All eight arguments and both SP residues need native verification.
- Keep the direct eligibility callback independent of stored unit coordinates; it correctly handles movement previews after the prior fix.

## Acceptance changes

Actual unwrapped9FEF0 should still accept native -3..+2. Installed A0014 and shared B4A1C should accept Chop only -2..+2, including moved/copy origins. Original Rush112 and all other original actions must retain the unmodified native result. Add target-height ±2/±3 boundaries, native invalid tiles, high-byte argument truncation, both stack residues, exact caller stack guards, no RNG, and unit-copy immutability.

These checks are now executed against the installed wrapper. The independent geometry suite constructs the actual native16×16 two-byte-per-tile map data and its02007F10 header. It does **not** stub height, validity, terrain, or geometry readers. All347 original actions match the unhooked native A0014 at three height differences and both SP residues (2,082 differential cases). Native and custom controls explicitly distinguish the -3 boundary. Both wrapper/C and native trampoline receive the exact original eight arguments; incoming stack data, lower guards, units and map remain unchanged. High argument bits obey native truncation, original impassable flags/bounds stay enforced, and any RNG call is a hard failure.

## Restorative effect risk

The canonical line44 also says Healer cannot become a damaging/draining attack. The native weapon-restoration effect3F unconditionally negates damage at1300E0. Elemental absorb already negates at13004A, so both together can become positive damage. The parent added a primary3F restorative-sign policy to the rebuilt custom final modifier and adjusted the preview hint; the engine council owns signed-effect verification. These geometry files do not change combat magnitude or reinterpret a nonexistent vanilla support name. Preserve zero, suppress custom drain3D separately, and verify3F with elemental absorb before accepting that rule.

## Shared melee family regression

The same installed eight-argument geometry contract now covers Chop424, Shatter427, Armor Break428, and Executioner430, with symmetric height2 and native weapon-derived range128. `test-chop-geometry.py` verifies all four actual native selector records (MP0/6/8/10 and3F/1/1/1 stages), copied/evaluated origins, truncation, map restrictions, both stack residues, unchanged caller data, and all347 original actions. On combat47f630ded93e0e386e7508c22bda988eaee83977 the39,846 checks passed. The separate eligibility test passed25,787 checks, including enemy-only single targets and friendly-fire426/429 arcs, primary-axe ordering, Confusion rejection, self/null/KO-target exclusions and original callback equivalence. Native arc list geometry remains covered by the parent-owned area test.
