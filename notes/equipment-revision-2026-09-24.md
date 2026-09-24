# Compact skill names and weapon attack revision

Status: built and tested; not packaged or promoted to **Play Mod.cmd**.
Builds on the [teaching-row fix](teaching-rows-fix-2026-09-23.md).

## Skill names

The longest original learned-ability names measure eleven tiles with the native
width routine `80161BC`; equipment help, command lists and previews are sized
for that. 26 approved expansion names were wider (up to 18 tiles) and were
clipped. [Compact display names](../src/ability-display-names.mjs) now cover
them, the two earlier aliases (Nature Wrath, Counter Rhy.) and, for a
consistent family, all Mystic Knight Spellblades ("Fire Blade" etc.). Full
approved names remain in the design documents and ability help. The source
build and [install audit](../scripts/audit-installed-design.mjs) use the map.

## Weapon Attack

The added weapons were weaker than original shop weapons available at the
same time (for example Gloom Sword 18 against Shortsword 25 and Silver Sword
30 at the opening shop). [The revision](revise-weapon-attack-2026-09-24.mjs)
derives each value from the clean ROM and the original shop tiers:

- S0 spans the family's opening-tier range; S1, S2 and S3 rise to the best
  first-upgrade, second-upgrade and second-upgrade+4 weapons respectively,
  positioned by price inside each shipment.
- Axes compare with Greatswords/Broadswords plus 2 for excluding shields and
  second weapons. Families without opening stock start two below their first.
- Values never decrease. 68 of 85 weapons rose; the strongest late weapons
  kept their existing 42–46. Magic Power, prices, gates and lessons are
  unchanged.

`notes/equipment-acquisition.json` records `previousWeaponAttack` for every
changed weapon. The ledger, axe addendum and class specification tables were
updated together; `node notes/validate-equipment-plan.mjs` and
`node notes/revise-weapon-attack-2026-09-24.mjs --check` pass.
`build/expansion/registry.json` is regenerated only by a full source rebuild.

## ROM and evidence

[Builder](../scripts/build-equipment-revision.py) is data-only on teaching-row
candidate `3447490f`: 29 names are rewritten inside their own strings (any
second pointer must be in an unreferenced superseded text table) and 68 Weapon
Attack bytes change. Every other byte is checked identical.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/equipment-revision-test-plan.json -Only test-revision-teaching-rows-ui
```

Run `20260924T055206.504473Z` passed all five steps on final candidate
`631497ccf8ffedaf3d88e4343124305fb08402e8`; the teaching-row step rebuilt
`3447490f` identically.

- [Revision test](../scripts/test-equipment-revision.py), 1161 native checks:
  all 452 learned-ability names of the five races fit eleven tiles; original
  names and item records 0..375 are unchanged; every added weapon matches the
  design; only declared bytes differ.
- Teaching-row native (1864) and real-core (28) checks pass on the final ROM.
  Screenshots show Weapon Atk 25/28/29/31 and "Sanguine Cut" unclipped.

Not covered: battle damage playback with the new values, AI weapon choice and
cold saves. The Weapon Attack field is the native record read by the original
damage and equipment code; no code changed in this stage.
