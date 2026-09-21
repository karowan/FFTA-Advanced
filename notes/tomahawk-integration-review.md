# Tomahawk native integration review

Status: bounded native audit; no Tomahawk action or engine code installed by this review. Chop geometry remains accepted at combat `62c848bc42e92fd7652075b235c49347c6b23862` (30,257 geometry checks; 21,883 eligibility checks).

## Donor and exact fields

Use original **Nighthawk147**, rather than Mog Lance134, as the candidate fixed-range physical donor. Native147 is range4;134 is range3. Both have physical effect3F, followed by three noop1 stages. Unlike Rush112, neither has knockback4B to remove. This is a mechanics donor; its visual suitability still needs a real Human Soldier animation test.

Nighthawk's original28 bytes are `6c01001400010400010100003f010101207214009000c80000015000`. Native CCD50 verifies these fields:

| Field | Original147 | Tomahawk425 contract |
| --- | --- | --- |
| +00 u16 name | 364 | generated SLD-AX-A2 name885 |
| +02 element, selector1 | 0 | 0: primary weapon element with +05=1 |
| +04 MP, selector2 | 0 | 4 |
| +05 weapon scaling mode, selector3 | 1 | retain1 |
| +06 range, selector4 | 4 | retain4; do not set bit80 |
| +07 height, selector5 | 0, uncapped | 3 for symmetric single-target height3 |
| +08/+09/+0A | 1/1/0 | retain native single-target shape pending executor test |
| +0C..0F effects | 3F/01/01/01 | retain |
| +10 flags | 00147220 | same as Rush, ordinary martial physical donor |
| +14 u16 animation, selector32 | 144 | native Nighthawk animation candidate |
| +16 u16 independent preview message | 200 | clear to0: Tomahawk has no secondary-effect message |
| +18..1B | 00/01/50/00 | preserve unless a separately verified requirement applies |

Native selector32 -> +14 is proven by CCD50. Ordinary action animation dispatcher A681E/A6822 obtains it and A6988..A6990 calls D3508(animation,action-context,0). D3508 indexes the eight-byte native animation table3947D8 at `(animation-1)*8`. ID144 selects callback **080FC801**, allocation58, table row394C50 `01c80f085800ff7f`. This callback is a multi-frame native effect state machine, not the physical damage handler. The callback reads action context and schedules native effect resources39D420/39D464 and4F6BC8. A correct pointer is not proof that the effect looks like a thrown axe on Soldier; render it before acceptance. Do not treat +16 as a second animation number.

Physical descriptor3F's quartet is [8,21,10,30]. It selects native130A94 eligibility,13215C noop application,13112C ordinary attack accuracy and13189C physical magnitude. New eligibility must use primary axe, living enemy, native actor Charm/base target side, deterministic Confusion rejection, and no stored-unit coordinate predicate. Share the proven Chop magnitude/primary/proc rules and use9/10 in the final combined multiplier phase. Keep original action147 and all347 originals unchanged.

## Line of sight is NOT supplied by this donor

`scripts/probe-tomahawk-geometry.py` executes clean native A0014 against actual native map headers and a16x16 two-byte grid. No geometry/map reader is mocked. **315 cases pass** for donors134/147/148 over distance3/4/5, target height differences -10/-4/-3/0/3/4/10, and intervening terrain flags0/1/8/9/255. Intermediate obstacle tiles have height255. Mog Lance returns true through range3; Nighthawk and Throw through range4; none has a height cap. A memory-read hook proves **none reads an intervening tile**. Results: `build/expansion/probes/tomahawk-native-geometry.json`.

A0014 fixed-range branch uses12E1A8(flags2), then B7C50 shape, CCD50 range/height and at most the two endpoint heights1CC18. Ordinary accuracy13112C calls12EF94 ->12C7F4 (attack/facing calculation), not a verified projectile collision query. Native weapon range9FEF0 likewise must not be assumed to implement LOS merely because the item is a bow/gun. This audit has not established a native general projectile-blocking function in a later executor. The315 cases establish the geometry gap, not a claim about every native animation/trajectory routine.

**Required implementation:** extend the existing explicit-coordinate geometry wrapper with a Tomahawk-only LOS predicate after the original geometry succeeds. It receives evaluated actor/target coordinates and remains valid after Move and on copied units. No global current actor lookup or unitF6/F7 lookup. Do not ship a range-only clone under a LOS description.

If no native helper can be verified, define the new rule explicitly: deterministic tile-supercover ray between tile centers, endpoints excluded, symmetric in reversal, blockers from verified native map validity/terrain and height intersecting the ray. Exact corner behavior, projectile height clearance and whether occupants intercept are currently unspecified design details, **not verified native conventions**. Record the chosen semantics and test them; do not silently label a Manhattan scan or arbitrary high-tile cutoff native LOS. Occupancy should not be added as a blocker without a chosen rule: otherwise the visual target and actual receiver can disagree.

## Acceptance recipe

1. All347 original action geometries/callbacks and all native animation table entries remain unchanged.
2. New range0/1/4/5 and diagonal Manhattan cases; height +/-3 accepted and +/-4 rejected; moved explicit origin, copied unit, invalid endpoint/impassable flags; both incoming SP residues, exact8 arguments, no mutation/RNG.
3. LOS clear/blocked/cardinal/diagonal/corner/reversed/uphill/downhill with obstacle adjacent to each endpoint; runtime player and AI target list excludes identical blocked cells. Endpoint-only native control must still accept the wall fixture.
4. Native primary-axe formula, weapon element/absorb/restorative, stronger offhand ignored, native weapon drain/effect3E excluded, no crit/second hit/consumption;4MP charged exactly once and not on cancelled/invalid targeting.
5. Real preview, committed hit and miss at range4: correct name, numeric damage, no inherited secondary-effect text, visible Soldier/axe animation and no descriptor/script hang. Exercise opposite sides and a Move-before-attack.

The source donor/range/height/descriptor and animation dispatch fields are verified. LOS semantics and rendered visual suitability remain explicit acceptance work.

## Adopted new LOS policy and isolated implementation acceptance

The parent chose the explicit new-rule semantics after the donor audit: straight tile-center segment one native height unit above both endpoints; closed-square supercover; a corner touching either obstructing tile blocks; endpoints excluded; invalid intermediate map tiles and terrain top touching/intersecting the segment block; occupants do not intercept. This supersedes the earlier open implementation details in this note. It is our Tomahawk policy, not a claimed vanilla rule.

Implemented only new `src/engine/projectile-los.c`, exported `ffta_projectile_los(actorX,actorY,targetX,targetY)`. It rejects coordinates outside0..15 before the native readers truncate them, validates both endpoints through1CC7C, obtains raw native heights through1CC18, then examines each intersected closed tile square in the endpoint bounding rectangle. Native1CC7C independently respects map origin/dimensions via1CD4C and treats a zero-height grid entry as invalid. No guessed terrain flags or unit/owner lookups. With coordinates<=15, denominator<=30 and height<=256, all rational cross-products fit signed32. No float, division, RNG or mutable state.

Each tile's entry/exit fractions are clipped using integer comparisons. Uphill rays compare the tile top against entry height; downhill against exit height. This catches collisions missed by testing only the tile center and preserves exact reverse symmetry. Adjacent diagonal shots still inspect both corner-touch side tiles. Height255 remains valid; the endpoint clearance becomes256 without byte overflow.

`scripts/test-projectile-los.py` compiles only this source into a disposable ROM overlay, executes the ARM7 Thumb machine code with actual native map readers, and compares it against an independent Python Fraction oracle that intersects the segment with four tile edges. **68,058 checks,6,414 cases,12,828 native helper executions pass**. Both incoming SP residues preserve callee-saved registers, exact SP, caller stack/guards, map and header. Any RNG or out-of-range native reader coordinate is a hard failure. Fixtures cover every native origin, short slopes, cardinal/diagonal/corner walls, invalid holes, uphill/downhill entry/exit, extreme heights, endpoint exclusion, offset map bounds, ignored terrain flags, oversized arguments, reversed paths and randomized maps.

Accepted isolated source SHA1 `033ca80a0e66f953fd9a9cb282fc54ddbedb5001`, binary `5d7eebc21408f0769674fb731bd117f95060a259`. Results `build/expansion/probes/projectile-los-tests.json`. The test also supports `--current`, which calls the symbol from the current compiled engine over the clean native reader image. Parent owns compile-list/geometry integration; this isolated pass does not claim installed Tomahawk UI/AI or rendered acceptance.

## Installed Tomahawk geometry acceptance

Current combat SHA1 `e967ee06310e0358348298d574c06cc956f8578f`, engine `7d963b9cd35c82820c75728b14e54fb1aa4c4d31`:

- `scripts/test-projectile-los.py --current`: **68,058 checks pass** against the actual compiled engine helper, with the same independent Fraction oracle/native map readers as the isolated acceptance.
- New `scripts/test-tomahawk-geometry.py`: **81,421 checks pass** against the installed A0014 wrapper and real native B4A1C shared player/AI candidate-list interface. It verifies native record getters MP4/range4/height3/animation144, physical3F/noop stages and preview message0. All347 original action geometries match the unmodified native entry in2,082 cases; all347 original shared tile lists match at both SP residues (694 comparisons). No original invokes the custom LOS helper.
- **2,420** Tomahawk range/height/copy cases cover diagonal Manhattan distances, +/-3 accepted vs +/-4 rejected, and deliberately stale unit Move coordinates. Walls, zero-height holes, exact-corner side tiles and reversal are compared against the independent LOS oracle; the untouched native donor control deliberately continues to accept the obstructed path.
- **128** Tomahawk shared tile-list fixtures cover both live/copy pointers, four direction arguments, both SP residues and eight map scenarios including random heights/holes. Every emitted tile matches independent range/height/validity/LOS expectations; there are no duplicate tiles, writes beyond output guards, unit/descriptor/map mutations or RNG calls. These are the actual shared list functions, not mocked geometry or a Python-generated replacement list.
- **9,088** exact eight-argument observations,20,168 geometry C alignment checks and5,399 LOS C alignment checks pass. Geometry uses the explicit evaluated coordinates. Native original high-argument truncation is preserved by the installed wrapper; oversized direct LOS inputs retain its stricter rejection.
- Updated `scripts/test-chop-eligibility.py`: **22,971 checks pass**, including512 shared Chop/Tomahawk descriptor fixtures for primary order, actor Charm, target base side, Confusion, HP, copies and both SP residues. Action425 is treated as an enabled custom action, never an inert native-fallback neighbor.

Frozen ROM/input/manifest/symbols and results are under `build/expansion/probes/tomahawk-geometry-council/e967ee06310e0358348298d574c06cc956f8578f`. Summary `tomahawk-geometry-tests.json`. Complete native target-list generation legitimately exceeds the older50,000-instruction single-function harness limit; this suite uses a bounded300,000-instruction budget and retains return/SP/register assertions. No engine defect was found. This accepts installed geometry and shared candidate enumeration, not rendered animation, a complete AI turn, MP spending, damage/application or law outcomes; those remain the parent's and engine council's complementary acceptance work.
