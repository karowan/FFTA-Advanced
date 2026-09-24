# FFTA Advanced v0.7.1

Equipment fixes and a weapon balance pass for FFTA Advanced, the Final Fantasy
Tactics Advance (USA) expansion with eight new jobs, 129 added abilities and 85
teaching weapons.

Download **FFTA-Advanced-v0.7.1.zip**. It contains the BPS patch, installation and
gameplay guide, release notes, and checksum manifest. Apply the patch to your own
clean USA ROM using [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)
or another BPS-compatible patcher. No ROM or emulator is included.

- Clean ROM SHA-1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`
- Patched ROM SHA-1: `631497ccf8ffedaf3d88e4343124305fb08402e8`

## Changes

- **Equipment Info panel:** Dark Knight swords and Chemist knives that teach two
  skills to two races no longer overflow the panel. The overflow garbled badges,
  dropped titles and left stray graphics over Clan Funds in shops. Matching
  racial rows now share one cycling badge, as in the original game.
- **Skill AP:** each skill row shows its own AP. Previously the second skill on a
  weapon repeated the first skill's AP.
- **Skill names:** long names now fit the menus, for example Blizzard Blade,
  Sanguine Cut, Black Night and Nature Haven.
- **Weapon Attack:** the new weapons were weaker than original shop weapons sold
  at the same time. 68 of 85 now match the original weapons of their type from
  each shop stage; the strongest late weapons are unchanged and none were
  weakened.

Saves from v0.7.0 remain compatible. Back up your save and use an in-game save
followed by a cold Continue after updating; do not carry emulator save states
across versions.

Tested with mGBA. A full campaign playthrough and physical GBA testing remain
outstanding. Geomancer field outlines can temporarily disappear during
memory-heavy animations while their effects remain active. The new weapons
still use existing item icons.

GitHub Actions verifies the accepted patch and builds this ZIP. It does not
compile the game or receive a ROM; gameplay acceptance was performed locally.
