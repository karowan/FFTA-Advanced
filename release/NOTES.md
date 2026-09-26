# FFTA Advanced v0.7.3

A stability and fixes release for FFTA Advanced, the Final Fantasy Tactics
Advance (USA) expansion with eight new jobs, 129 added abilities and 85
teaching weapons. It also gives every new weapon its own icon.

Download **FFTA-Advanced-v0.7.3.zip**. It contains the BPS patch, installation and
gameplay guide, release notes, and checksum manifest. Apply the patch to your own
clean USA ROM using [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)
or another BPS-compatible patcher. No ROM or emulator is included.

- Clean ROM SHA-1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`
- Patched ROM SHA-1: `40c9bbb9115c53ddbab6381e93c963ae0bd31ee4`

## Fixes

- **EXP for the new jobs:** units in the ten new jobs earned no EXP from any
  action. The original game treats every job numbered above 82 as a special
  story unit. The new jobs now earn EXP like original jobs; for example, a
  Chemist's Potion on a hurt ally earns the same EXP as an Item-command Potion.
- **Pre-battle unit Info:** pressing R on a unit during deployment could show
  garbled graphics and leave a black screen after closing it.
- **Corrupted unit abilities:** opening a unit's Info or Status could corrupt a
  different party member's saved abilities, for example stray "Shieldbearer"
  or "Blizzara" labels and abilities shown as mastered. Saves that were already
  affected keep that damage.
- **Chemist:** using an item on an enemy or an empty tile froze the battle.
  Single-target items such as Potion and Phoenix Down also affected adjacent
  units; only Healing Mist affects an area now.
- **Reactions:** Counter, Return Magic and other original reactions again
  respect Petrify, Silence and other disabling statuses.
- **Battle stability:** the enemy AI's working memory had been accidentally
  doubled, a cause of rare battle stalls. A Mystic Knight Doublecast into a Shell
  target came within a few bytes of crashing and now has a safe margin.
- **Equipping:** two original item-list routines still read the old inventory
  layout after equipping.
- **Job wheel:** moving off Mystic Knight left a stray fragment of the name.

## Changes

- **Weapon icons:** each of the 85 new weapons has its own inventory and shop
  icon in its family's original palette, instead of sharing its family's
  original icon. Held weapons in battle still use their family's sprite.

Saves from v0.7.0 through v0.7.2 remain compatible. Back up your save and use an
in-game save followed by a cold Continue after updating; do not carry emulator
save states across versions.

Tested with mGBA. A full campaign playthrough and physical GBA testing remain
outstanding. Enemy AI use of ranged enchant strikes has not been tested in real
battles. Geomancer field outlines can temporarily disappear during memory-heavy
animations while their effects remain active.

GitHub Actions verifies the accepted patch and builds this ZIP. It does not
compile the game or receive a ROM; gameplay acceptance was performed locally.
