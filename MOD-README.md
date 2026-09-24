# {{MOD_NAME}}

Release: **{{VERSION}}**

A mod for **Final Fantasy Tactics Advance (USA)** that adds eight jobs, new
abilities and equipment, spritework, and menu improvements.

## What the mod includes

- **Eight new jobs across ten race/job options:** two additions for each
  of the five playable races. Dark Knight and Chemist each belong to two races.
- **129 added ability entries:** 85 actions, 18 supports, 18 reactions and eight
  combos, including the extensions to the original Soldier and Gladiator jobs.
- **85 new teaching weapons**, introduced through normal shop progression and
  available for repeat purchase.
- A **two-handed axe weapon family** for Soldier, Gladiator and Viking, with
  new skills inside Soldier's Battle Tech and Gladiator's Spellblade Tech.
- New AI-generated spritework for all ten added class options, including battle
  sprites and animations, portraits, job-wheel figures and equipment icons,
  using the game's existing native palettes.
- Mission-item safeguards, repeatable access to otherwise missable monster
  ability sources, eligible secret-recruit retries and rare-equipment recovery.
- Manual clan sorting, visible Morpher transformations, Missions first in the
  pub menu, and expanded equipment and ability displays.

## New jobs and how to unlock them

The numbers in this table count **mastered action abilities on that character**.

| Race | Job | Required action mastery | Play style |
|---|---|---|---|
| Human | Samurai | Fighter 2 + Ninja 1 | Katana techniques and the Centered buff. |
| Human | Dark Knight | Paladin 2 + Black Mage 2 | Sword attacks, HP sacrifice and drain. |
| Bangaa | Viking | Warrior 3 + White Monk 1 | Two-handed axes, theft and storm magic. |
| Bangaa | Dark Knight | Gladiator 2 + Bishop 1 | Sword attacks, HP sacrifice and drain. |
| Nu Mou | Chemist | None | Ranged healing, revival and ingredient mixtures. |
| Nu Mou | Geomancer | Sage 2 + Black Mage 3 | Nature magic, terrain bonuses and battlefield fields. |
| Moogle | Chemist | None | Ranged healing, revival and ingredient mixtures. |
| Moogle | Bard | Animist 2 + Juggler 2 | Songs that buff and heal allies. |
| Viera | Dancer | Fencer 2 + White Mage 2 | Debuffs, evasion and movement skills. |
| Viera | Mystic Knight | Red Mage 2 + Elementalist 2 | Weapon enchantments and Spellblade attacks. |

## New job mechanics

- **Samurai:** Centered strengthens follow-up Iaido techniques.
- **Dark Knight:** damaging and draining sword arts require a suitable sword.
  Dark Mind, Black Night and self-mode Last Resort are weapon-free,
  allowing those defensive options in other weapon builds.
- **Chemist:** Mix combines inventory ingredients into medicines.
- **Geomancer:** nearby terrain strengthens nature arts. Each caster can maintain
  one Rime Field or Nature Haven at a time.
- **Dancer:** Passing Step lets you move after attacking, using up to two points
  of your remaining movement.
- **Mystic Knight:** Spellweave rewards alternating physical and magical actions.
  Spellblade strikes count as magic for this bonus, although they deal physical
  damage.

### Axe additions to the original jobs

Each of Soldier and Gladiator receives four actions, one support and one reaction:

- **Soldier:** Chop, Tomahawk, Overpower and Shatter Guard; Recuperation and Haft
  Guard add healing support and axe defense.
- **Gladiator:** Armor Splitter, Reaping Arc, Executioner and Fell Cleave;
  Followthrough rewards positioning, while Axe Reprisal offers an axe counter.

## Finding the new teaching equipment

Cyril stocks every unlocked new teaching weapon. Shipments are cumulative:

| Campaign progress | New teaching weapons available in total |
|---|---:|
| First normal Cyril shop visit | 18 |
| Complete Twisted Flow | 41 |
| Complete Pale Company | 64 |
| Complete Desert Patrol | 85 |

Other towns stock new weapons for these jobs:

- **Sprohm:** Dark Knight, Viking and the original-job axe additions.
- **Cadoan:** Geomancer and Chemist.
- **Baguba Port:** Bard and Chemist.
- **Muscadet:** Dancer and Mystic Knight.

## Added quality-of-life features

- **Clan sorting:** press Select on a sortable member, move to another member,
  then press Select again to swap them. Marche and Montblanc keep their protected
  story positions.
- **Equipment previews:** in Item List, Buy and Sell, use L/R to switch
  eligibility pages and inspect the ten added class entries.
- **Job wheel:** L/R switches pages when Human jobs exceed one page.
- **Auto-Potion:** in Pick Abilities â†’ Reaction, choose Potion or Hi-Potion.
  The saved choice is marked `- set`.
- **Morpher visuals:** transformations now show the appropriate monster form.
- **Pub menu:** Missions appears first.
- **Content recovery:** safeguards for mission items, repeatable encounters for
  missable monster abilities, and retries for eligible secret recruits.
- **Rare equipment:** six paid dispatch services recover rare equipment after
  clearing the game.

## Installation

This ZIP contains `FFTA_Expansion.bps`, this README, `CHANGELOG.md` and
`manifest.json`. Supply your own clean **Final Fantasy Tactics Advance USA**
ROM. No game ROM, save, emulator or development tools are included.

1. Extract the ZIP.
2. Open [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) or another
   BPS-compatible patcher.
3. Select your clean USA ROM and `FFTA_Expansion.bps`, then apply the patch.
4. Open the resulting `.gba` file in your GBA emulator and start a new game,
   or follow the compatible-save guidance below.

Each release patches the **clean original ROM** directly.

- Required original size: **{{SOURCE_BYTES}} bytes**.
- Required original SHA-1: `{{SOURCE_SHA1}}`.
- Patched game SHA-1: `{{TARGET_SHA1}}`.

Full checksums are in [manifest.json](manifest.json).
See [CHANGELOG.md](CHANGELOG.md) for the latest changes.

## Saves and updates

This update supports existing saves from the preceding expansion release.
Back up your in-game save before updating. Keep its filename matched to the
patched ROM, or select it through your emulator's save settings.

For an update, **save in the game's menu, close the game, open the updated ROM
and choose Continue**. Emulator save states are not supported across updates.

## Artwork and contributions

The new spritework is AI-generated. I'd love contributions from artists to
improve or replace the sprites, animations, portraits and menu graphics.

## Known issues

Tested with mGBA. A full campaign playthrough and physical GBA testing are still
outstanding.

During memory-heavy spell animations, a Geomancer field outline may temporarily
disappear while its effect remains active; the outline returns at the next
command boundary.

For bug reports, include your mod and emulator versions, steps to reproduce the
problem, and an in-game save if available.

## License

Original project code and generated artwork use MIT. The complete license notice
is included in manifest.json. Original game assets remain the property of their
respective rights holders, including Square Enix, and are not licensed here.
