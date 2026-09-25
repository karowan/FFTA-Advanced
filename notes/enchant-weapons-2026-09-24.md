# Mystic Knight enchantments on every weapon

Status: released in v0.7.2 (game `cc946527`, acceptance run `20260925T010005.954289Z`).
Builds on the [equipment revision](equipment-revision-2026-09-24.md).

## Behavior

- The eleven enchantments, Spellbreak, Arcane Release and Break accept any
  primary weapon (native categories 1–19 plus axes), not only rapiers/sabers.
  A Viera Sniper with secondary Spellblade can enchant a greatbow.
- Enchant strikes and Spellbreak use the weapon's own Fight range and height
  (action range bytes `80/80`): melee 1, spears 2, bows/greatbows 5, guns 8.
  Enchantments keep self preparation. Release and Break keep their ranges.
- Spell Parry and Spellblade Combo still require a rapier or saber.
- Spellbreak removes one random buff on a hit (native RNG `2804`, drawn only
  at resolution) instead of a menu choice. Its 21 "Break …" rows widened the
  ability window; the native list renders each entry's text into tiles
  `0x200 + index × width`, which at that width reached BG2's own tilemap
  (tile `0x300`, `0xE000`) and drew a garbage strip when the list scrolled.
  One row keeps the window narrow. Its preview now uses the real weapon.
- Names: "X Spellblade" → "X Ench." (Fire, Blizzard, Thunder, Poison, Sleep,
  Silence, Drain, Flare, Slow, Osmose, Holy) and Break Blade → "Break Ench.";
  Blade Combo keeps its name. Break and Spell Parry help text follow the rules.
- A ranged strike plays the enchantment's charge and elemental impact on the
  target, not an arrow flight; the native self forecast still shows a weapon
  hit percentage although self preparation always succeeds (as in v0.7.1).

## Implementation

[Builder](../scripts/build-enchant-weapons.py) is a bounded patch on the
equipment-revision candidate. It authenticates the installed integrated code
and compiles the current Mystic Knight state, action, reaction and dispel
sources, the choice menu ([dancer-choice.c](../src/engine/dancer-choice.c)) and
the targeting hook ([asm](../src/engine/mystic-knight-targeting.s)) into blank
ROM `0x1FF2000..0x1FF3FFF`, now owned by this change. Calls back into installed
code use generated Thumb `BX` stubs, each authenticated against the integrated
build. Changes: fourteen function-entry trampolines (argument registers
preserved), a whole-entry hook at native `B42E4`, strike action bytes 6–7 for
actions 410–421, and three help pointers (Spellbreak, Break, Spell Parry). Native `B42E4` builds the targeting UI's range mode word; for
weapon-relative ranges it always set `0x100` ("exclude the actor's tile"),
ignoring the action's self flag, so the hook clears that bit for enchantments.
Source rebuilds use the same rules: `build-integrated-jobs.py` writes `80/80`
and the engine/help sources carry the new checks and text.
[Battle fixtures](../scripts/create-battle-fixture.py) accept optional declared
`secondary` and `equipment` profile fields ([profile](../scripts/fixtures/enchant-sniper-profile.json)).

## Evidence

```powershell
& '.\Test Expansion.ps1' -Plan scripts/enchant-weapons-test-plan.json -Only test-enchant-weapons-ui
```

Run `20260924T084943.175083Z` passed all eight steps; stages rebuilt
identically to `3447490f`, `98581027` and final `2a93fa4306ca2dc239fd35342c2abf4c1a64ad81`.

- [Native test](../scripts/test-enchant-weapons.py), 49,063 checks: weapon and
  blade gates for every item (337 enchantable); for one weapon of every
  category, A0014 geometry over a 13×13 grid equals native Fight except the
  enchantments' self tile, Release/Break unchanged; the targeting mode word
  changes only the self bit; Spell Parry by category; action and help data.
- Equipment revision (1161), teaching rows native (1864) and real core (28)
  pass on their stages/final ROM.
- [Real core](../scripts/test-enchant-weapons-ui.py): a generated Giza battle,
  Viera Sniper with Windslash Bow and secondary Spellblade. Fire Ench. on her
  own tile and on an enemy five tiles away through native menus: 6 MP, Fire
  bound to the greatbow (`0xAE1`), 18 damage only to the target (44 checks in
  all). Self preparation also succeeded with high RNG values in discovery runs.

The same plan's real-core test also scrolls the full 14-entry list (menu map
above the window unchanged) and replays Spellbreak on a target with Haste and
Protect over fixed seeds (one buff per hit, both occur, none on a miss).

Not covered: enemy AI choosing ranged enchant strikes, laws, Doublecast with
ranged weapons, every weapon family in real battles, cold saves.
