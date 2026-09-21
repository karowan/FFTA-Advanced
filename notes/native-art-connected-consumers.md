# Connected palette, weapon and effect consumers - September 18, 2026

Follow-up to2d18368. Built-in imagegen only; technical integration first and
final sprite refinement deferred. No new art, external provider, agents,
publication, game launch, package installation or player-save changes.

## Corrected HUD interpretation

The preceding checkpoint misread the bottom `WT` indicator as `WHT` and treated
it as a donor job abbreviation. It is the native wait-turn indicator, followed
by turn position/unit count. The fresh mixed capture clearly shows `WT 1/12`.
The [FFTA FAQ](https://ffextreme.com/ffta/faq/) independently explains that exact
display. This is a documentation error, not a missing class-label consumer.
No HUD/icon hook or native lettering was changed. The `ffta_job_icon` donor
wrapper is not proof of an incorrect battle label: the equipment decoder is
already independently redirected. Other real UI acceptance remains separate.

## One connected technical ROM

Candidate **b4993232e05eeb20ce536cca6f4b9738aa4a2b12**, index
`build/art/connected/current.json`. Reproduce with the declared Python runtime:

```powershell
& $fftaPython scripts/build-connected-art.py
```

The builder authenticates the existing all-class palette candidate6443725d,
then explicitly builds status glyphs, equipment icons/projectiles, held axe276
and Tomahawk425 impact on top. Existing class/menu/portrait/action transports
are inherited from the authenticated parent chain. All276 prior animation
references are copied from the latest palette-aware table, rather than an old
weapon build. Every live-palette hook and the complete reserved module remain
byte-exact. The added stages are:

| Stage | SHA-1 |
| --- | --- |
| Status | ff2a98eda778e4fd7c626227561ceeda8c0f33ef |
| Equipment | ed8632de8cebcf87398b9aa778fe395cbb31c713 |
| Held weapon | d2ac02901509c806c3fbb60c0922b670d3d10efc |
| Impact/final | b4993232e05eeb20ce536cca6f4b9738aa4a2b12 |

Weapon/effect builders now accept explicit manifests and `publish_current=False`.
Their historical default behavior remains. The connected builder preserves the
old component, assembled, palette and release indexes. Only its own connected
index is published. Schema3 deliberately denotes a new unaccepted composition;
do not package it through the older schema2 acceptance list.

The manifest pins the immutable source palette manifest. A metadata-only cleanup
removed a changing rebuild-report field and replaced the mutable source-index
path with this pin. Rebuild20260918T132053.326392Z reproduced the exact tested
ROM; no runtime was repeated for that metadata cleanup. The source hash is also
checked before a subsequent native reproduction test.

## Targeted acceptance

Runner **20260918T131655.986900Z** passed both declared tests:

- `test-connected-art-native`:3981 checks. Exact four-stage rebuild, all276
  previous allocation getters plus appended held axe,461 item identity/resource
  selectors, all461 action IDs plusFFFF at two stack residues through the final
  effect hook, continuation/register/stack fences, final payloads and source
  image authentication. ARMv4T TI925T is set before memory mapping.
  `build/art/connected/native/20260918T131656.617500Z/report.json`.
- `test-connected-art-mixed-entry`:632 checks. Fresh native deployment and
  ready/idle captures for Human Dark Knight117, Bangaa Viking118, Nu Mou
  Chemist120 and Viera Dancer124, with original story identities preserved.
  `build/art/live-palette/battle/20260918T131701.701324Z/observed.json`.

Runner **20260918T131915.696681Z** passed
`test-connected-art-projectile-impact`:4069 checks, report
`build/art/generated-projectile/20260918T131916.393888Z/report.json`.
It starts at the authenticated world checkpoint and builds battle objects using
the final ROM. Marche remains a Soldier with declared axe454/Tomahawk learning;
four generic, unarmed same-race allies use Samurai116, Viking118, Chemist120 and
Dancer124. Both original-projectile and generated-projectile controls retain the
same generated impact and custom class palette module.

The native menus select/confirm Tomahawk. Four-frame observations verify the
moving projectile in hardware bank8, all three generated impact poses in bank6,
exact native cycling impact colors, generated body colors, no palette refusal
or allocation failure, and disjoint active effect/body banks. Each control has
ten effect/projectile coexistence samples with all four class owners visible.
The Dancer moves from bank6 during the projectile to7 and then8 during impact;
its generated colors stay exact. This is a real native effect-induced bank
handoff, not a manually toggled palette fixture. Both controls deal18 damage,
pay4MP (12 remaining), gain8EXP, preserve equipment/inventory/AP and advance to
the next turn. The source world state remains unchanged.

Visually inspected final mixed-ready and generated-impact-1-260 captures. The
temporary bodies and impact render together. This accepts that transport path,
not the design quality, repeated poses or complete animation.

## Boundaries and next work

The current palette parent stays6443725d. Its retained correct-race/all-ten-water
evidence remains applicable to unchanged assets and code, within its original
scope; those water scenarios were not replayed onb4993232. The prior movement
timing/phase failure remains unresolved and is inherited, not waived by the
successful action. Prior failed runs and discarded optimization evidence remain.

This closes one connected projectile/impact/coexisting-body path and proves a
natural bank handoff. It does not cover all effects, custom classes casting,
every held weapon/action family, worst-case heap, response timing, campaign,
final artwork or delivery. Status and equipment inputs are now assembled but
their live consumer evidence remains from earlier isolated builds. G01-G04 are
still open under their full scopes. Next continue actual held-weapon/action
and remaining natural lifetimes, resolve timing and maximum-heap acceptance,
then perform assembled review and reproducible separately playable delivery.
Reuse passing evidence; no broad suite ran. Installed previewa6d883b5, vanilla,
player saves and running session remain untouched.
