# Expansion showcase

Open **Play Expansion Showcase.cmd** and Continue from file1. This is a separate,
deliberately boosted early-Cyril campaign for trying the expansion immediately.
The ordinary expansion and vanilla launchers/saves remain separate.

The original six named clan members cover all five races. Their available old
and new lessons are mastered, unlocking all ten new racial job options and the
Soldier/Gladiator additions. All85 teaching weapons and original equipment/
recipe supplies are stocked at99. The clan has999,999gil; each member starts
with500HP,200MP and10JP, with their primary new Combo assigned.

| Member position | Primary command | Secondary command | Equipped weapon |
|---|---|---|---|
|1 — Marche|Samurai|Dark Knight|Moonblossom|
|2 — Montblanc|Bard|Chemist|Nameless Pipe|
|3 — Human|Dark Knight|Samurai|Sacrifice Edge|
|4 — Bangaa|Viking|Dark Knight|Tidal Axe|
|5 — Nu Mou|Geomancer|Chemist|Gaia Rod|
|6 — Viera|Mystic Knight|Dancer|Flare Saber|

Use Change Jobs and Pick Abilities to try the other combinations and equip
supports/reactions. Normal weapon requirements still apply: change equipment
when a command needs a different weapon family. Mastery does not remove those
rules. The campaign remains early; later story and postgame events are not
falsely marked complete. This is a content sandbox, not a balanced progression
save or evidence of earning the abilities naturally.

Keyboard: X confirms, Z cancels, Enter is Start, arrow keys move/select, A/S
are the usual shoulder bindings if unchanged in mGBA. In-game and emulator saves
go to `saves/expansion-showcase-v0.7/`. Normal save basename:
`FFTA_Expansion_Showcase_v0.7.sav`. The standalone ROM copy under
`roms/play/expansion-showcase-v0.7/` is byte-identical to the accepted v0.7 build.
No existing save is replaced by showcase installation.

## Preparation evidence

`prepare-expansion-showcase` in `scripts/showcase-test-plan.json`, through the
common runner, performs native job changes, verifies unlocks/mastery/stock, and
writes an ordinary save through fixed buttons. A fresh unmodified emulator
cold-loads it and checks the entire party, AP banks, inventory, preferences and
gil. Six native equipment setters install legally allowed teaching weapons.

Run `20260917T160010.694284Z` passes240 checks in16.4seconds. The earlier
155815 run passed234 checks; the final run adds JP and assigned Combos before
the native save/cold transaction. No game ROM changed. Final seed SHA1:
`7831543efb239ef145764889214f8d83cd56eb14`; report SHA1:
`bb452139cb88881e2424e37ac52dd503a9b91fa0`.
Private artifacts are `build/showcase/20260917T160011.215713Z/`.

`scripts/install-expansion-showcase.py` installs only an authenticated passing
seed, refuses to replace any existing showcase save, and validates the separate
launcher without opening it. Later player progress is never reset by reopening
the launcher. Regeneration is optional; do not rerun it merely to launch.

The user explicitly requested the visible desktop launch. The elevated normal
desktop launch succeeded and Computer Use observed the standalone mGBA window.
Interactive gameplay was left to the user; no new gameplay acceptance was
inferred from that window observation.
