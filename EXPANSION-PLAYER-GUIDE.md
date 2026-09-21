> Historical v0.7 engineering player guide, before the accepted art import. See [the current overview](README.md) and [release workflow](MOD-RELEASE.md).

# FFTA Eight-Job Expansion â€” v0.7

Open **Play Expansion.cmd** in this folder to play the expansion in standalone
mGBA. Choose **New Game** to begin your separate expansion campaign. Your existing
vanilla and development launchers remain available for those games.

This build adds eight job concepts across ten race/job options,129 lessons and
85 teaching weapons, plus Soldier/Gladiator axe skills. It retains the original
campaign and adds completion safeguards, equipment recovery, manual clan sorting,
visible Morpher forms and expanded equipment/ability displays.

The full engineering implementation is included. The ten added class options
have independent actor/menu/portrait resources, connected native animations,
weapon/effect graphics and equipment eligibility pages. **Artwork is temporary:**
repeated poses, rough pixel conversions and palette compromises remain for a
later art pass. The measured extra Move/cancel delay has been resolved.

## Your games and saves

| Launcher | Game | Save storage |
|---|---|---|
| Play FFTA.cmd | Original vanilla | Existing vanilla location, unchanged |
| Play Development Build.cmd | Earlier experimental foundation | Existing development location, unchanged |
| Play Expansion.cmd | Full v0.7 engineering, temporary artwork | `saves/expansion-v0.7-engineering/` |
| Play Previous Expansion.cmd | Previous gameplay release | `saves/expansion-v0.7/` |

The expansion ROM is `roms/play/expansion-v0.7-engineering/FFTA_Expansion_v0.7.gba`.
Its normal save is `saves/expansion-v0.7-engineering/FFTA_Expansion_v0.7.sav`; emulator save
states and screenshots also go to that expansion folder. Both in-game save slots
belong to this separate save. The launcher explicitly supplies the expansion
paths each time. Use it instead of opening the ROM through another configured
emulator if you want the same save location.

Save normally in the game and close mGBA before backing up the whole expansion
save folder. The delivery does not copy or migrate an existing campaign. The previous expansion and art-preview saves remain in their original folders. Keep
vanilla saves and old emulator states with their original game; importing them
is not part of this release's acceptance. Do not run two expansion instances
against the same save simultaneously.

## Unlocking the new jobs

Requirements count mastered **action abilities on that character**. They do not
count levels, support/reaction lessons or another clan member's progress.

| Race | Job | Requirement |
|---|---|---|
| Human | Samurai | Fighter2 + Ninja1 |
| Human | Dark Knight | Paladin2 + Black Mage2 |
| Bangaa | Viking | Warrior3 + White Monk1 |
| Bangaa | Dark Knight | Gladiator2 + Bishop1 |
| Nu Mou | Chemist | None |
| Nu Mou | Geomancer | Sage2 + Black Mage3 |
| Moogle | Chemist | None |
| Moogle | Bard | Animist2 + Juggler2 |
| Viera | Dancer | Fencer2 + White Mage2 |
| Viera | Mystic Knight | Red Mage2 + Elementalist2 |

Chemist is available when normal job changing becomes available. Learn the new
lessons through their teaching equipment and AP as usual. Equipment permission
does not grant another job's unmastered lesson. Normal racial ownership and the
existing support/reaction slots still apply.

## Finding teaching equipment

Cyril carries every unlocked new teaching weapon, with cumulative stock:

| Campaign progress | Total new teaching weapons available |
|---|---:|
| First normal Cyril shop visit |18|
| Complete Twisted Flow |41|
| Complete Pale Company |64|
| Complete Desert Patrol |85|

Visit the shop after successful completion. The other towns add their local
specialties when normally accessible: Sprohm for Dark Knight/Viking/axe skills,
Cadoan for Geomancer/Chemist, Baguba Port for Bard/Chemist, Muscadet for
Dancer/Mystic Knight. Samurai equipment is in Cyril. Prices retain normal
town/clan adjustments. All new teaching weapons can be bought repeatedly.

See [the complete equipment catalog](WEAPON-ACQUISITION.md) for names, lessons,
AP and base prices; [the class specification](JOB-CLASS-SPECIFICATION.md) gives
the full rules, and [the axe additions](AXE-SKILL-EXPANSION.md) covers the original
Soldier/Gladiator extensions.

## Useful controls and mechanics

- In equipment eligibility previews (Item List, Buy and Sell), use L/R to
  switch pages and see the ten added class entries.

- In the clan roster, press Select on a sortable member, move to the desired
  member and press Select again to swap them. Marche and Montblanc retain their
  protected story positions.
- In **Pick Abilities â†’ Reaction**, Auto-Potion offers Potion or Hi-Potion.
  Confirm the preferred row; `- set` marks the saved choice. It consumes nothing
  during selection and will not substitute the other medicine when stock runs out.
- Chemist recipes require their listed ingredients. Stock payment and reactions
  follow the learned/equipped abilities; a full clan does not grant extra slots.
- Geomancer field outlines distinguish their shapes. During memory-heavy spell
  animations an outline may disappear temporarily while its effect stays active;
  it returns at the next command boundary.
- Recovery services appear only after their original eligibility requirements.
  The six rare-equipment services additionally require clearing the game; they
  are paid dispatches, not automatic gifts. Repeat recruit access preserves the
  original eligibility and does not create duplicates or resurrect dead units.
- At the late Ambervale save, finish saving, leave the slot picker with B, then
  select another destination to continue the final event. After the ending's
  clear save and title reset, use Continue for postgame.

## Patch and rebuilding

The private delivery is selected by `build/releases/v0.7-engineering/current.json`:
BPS patch, manifest, this guide,
reference documents and acceptance certificate. The patch requires a clean USA
FFTA ROM with SHA1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`.
Apply the BPS to a separate copy; do not patch the vanilla play file in place or
combine it with another overhaul. The resulting32MiB ROM has SHA1
`a28b624bb13c8f2f2597a4d4bd3999b17c234b99`. The manifest also records SHA256 hashes.

[Reproducible build instructions](REPRODUCIBLE-BUILD.md) describe reconstructing
the game from source and pinned local tools. Packaging is deterministic and
checks the patch by applying it back to the clean ROM, comparing every output
byte, and rejecting a changed source. ROMs, saves and tools remain local.

Acceptance covers the documented job, cross-class, UI, save and representative
campaign scenarios. It is not an uninterrupted full-combat playthrough, every
original story variation, physical-GBA performance test or compatibility promise
for other mods. Detailed coverage and failed-test history are in the repository's
implementation checklist and release review. Report the action, job/equipment,
location and save type if you encounter a problem; retain a backup of the save.
