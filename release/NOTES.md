# FFTA Advanced v0.7.2

Mystic Knight enchantments for every weapon and readable help text for FFTA
Advanced, the Final Fantasy Tactics Advance (USA) expansion with eight new jobs,
129 added abilities and 85 teaching weapons.

Download **FFTA-Advanced-v0.7.2.zip**. It contains the BPS patch, installation and
gameplay guide, release notes, and checksum manifest. Apply the patch to your own
clean USA ROM using [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)
or another BPS-compatible patcher. No ROM or emulator is included.

- Clean ROM SHA-1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`
- Patched ROM SHA-1: `cc9465277898509fda703b1163cad877fc694405`

## Changes

- **Enchantments on any weapon:** the eleven Mystic Knight enchantments,
  Spellbreak, Arcane Burst and Break Ench. accept any primary weapon, not only
  rapiers and sabers. For example, a Sniper with secondary Spellblade can
  enchant a greatbow. Enchant strikes and Spellbreak use the weapon's own attack
  range, and enchantments can still target your own tile. Spell Parry and Blade
  Combo still need a rapier or saber.
- **Spellbreak:** removes one random buff from the target on a hit, instead of
  offering a list of 21 statuses. The long list also caused stray graphics
  while scrolling the Spellblade menu, which no longer happens.
- **Names:** the enchantments are now "X Ench." (Fire Ench., Holy Ench.,
  Break Ench.) to fit the menus.
- **Help text:** descriptions longer than two lines continue on a second page;
  press A to read it, as with original multi-page help. Previously the third
  line of 114 descriptions was cut off.
- **Weapon descriptions:** the "Teaches ..." text on new weapons now uses the
  skill names shown in menus.

Saves from v0.7.0 and v0.7.1 remain compatible. Back up your save and use an
in-game save followed by a cold Continue after updating; do not carry emulator
save states across versions.

Tested with mGBA. A full campaign playthrough and physical GBA testing remain
outstanding. Enemy AI use of ranged enchant strikes has not been tested in real
battles. Geomancer field outlines can temporarily disappear during memory-heavy
animations while their effects remain active. The new weapons still use
existing item icons.

GitHub Actions verifies the accepted patch and builds this ZIP. It does not
compile the game or receive a ROM; gameplay acceptance was performed locally.
