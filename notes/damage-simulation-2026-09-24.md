# Damage simulation by job and stage

Status: analysis only; no game change.

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" scripts/simulate-damage.py
```

[simulate-damage.py](../scripts/simulate-damage.py) drives the game's native
action executor (`A433C`) on the current candidate
(`cc9465277898509fda703b1163cad877fc694405`, paged help). It runs in the ARM
harness from the executor fixture of the integrated build, which
`scripts/jobs/viking/prepare-executor.py` creates. The method, including what
is not modelled, is in the script docstring. In brief:

- **Jobs:** 53 player jobs, original and new, across all races.
- **Stats:** each job's native base stats plus growth, as if levelled only in
  that job.
- **Equipment:** the best stage-available weapon the job's permission mask
  allows (shop tiers from `build/reports/vanilla-teaching-sources.json`, plus
  expansion shipments). No armor.
- **Skills:** only abilities a stage-available weapon teaches. Abilities from
  rare weapons count only in the late stage.
- **Target:** a same-level Human Soldier with neutral affinity to all nine
  elements, attacked from the side.
- **Seeds:** 48 fixed native RNG states.
- **When jobs count:** a job counts toward a stage once its prerequisite chain
  depth, read from the native requirement records, is reached. Opening stage
  is depth 0; Twisted Flow allows depth 1 (e.g. Paladin, Fighter); Pale
  Company allows depth 2 (e.g. Dark Knight, Samurai, Assassin). Jobs that
  aren't unlocked yet are still simulated, but not ranked.

The score is expected HP damage per action, with misses counted as 0.

Run `build/reports/damage-simulation/20260925T004651.028530Z/report.json`
(ignored): 0 errors. Stages and the median of each ranked job's best action:

| Stage | Level, stock | Ranked jobs | Median best | Median Fight |
|---|---|---|---|---|
| Opening | L5, first shop, S0 | 19 | 19 | 18 |
| After Twisted Flow | L10, tier 1, S1 | 44 | 34 | 30 |
| After Pale Company | L16, tier 2, S2 | 52 | 47 | 40 |
| After Desert Patrol | L22, S3 | 52 | 62 | 53 |
| Late | L40, rare-weapon skills | 52 | 106 | 74 |

## Design versus measured coefficients

Each new strike's damage relative to the same unit's Fight, at L22 against the
neutral target. Every new skill matches its design within about 4%. The
consistent small shortfall comes from variance and rounding against defense.

| Skill | Design | Measured |
|---|---|---|
| Ashura | 1.10P | 1.06× |
| Osafune | 0.85P | 0.81× |
| Guarding Draw | 1.00P | 0.96× |
| Kikuichimonji | 1.45P | 1.39× |
| Blood Edge | 1.50P | 1.47× |
| Sanguine Cut | 0.95P | 0.92× |
| Infernal Strike | 0.75P | 0.73× |
| Crushing Blow | 1.15P | 1.12× |
| Unholy Rite | 1.75P | 1.71× |
| Sword Dance | 1.60P | 1.54× |
| Fell Cleave | 1.80P | 1.75× |

An earlier run showed Blood Edge and Unholy Rite about 1.4× above their
designs. That was a simulator error, not a game bug:

- The executor fixture's enemy is a monster that absorbs Holy and is weak to
  Dark. Its elemental affinities are unit `+0C..+14` (0 weak ×1.5, 1 neutral,
  2 null, 3 absorb, 4 half), applied at native `130022`.
- The reused Bard setup neutralized only Holy (`+13`).
- Both Dark Knight sacrifice skills are Dark. The Dark Knight build forces
  element 8 for A1 and A8.

The simulator now sets all nine affinities to neutral.

## High outliers (≥1.5× stage median, ranked jobs)

New content:

- **Dark Knight**, from unlock at L16:
  - Blood Edge is 1.7–1.8×, the same band as Fighter's Backdraft (1.8×) and
    Gladiator's Fire Sword (1.7×).
  - Unholy Rite is 2.1–2.2× at S3 and 1.8–1.9× late. It costs 14 MP plus 20%
    max HP and hits every adjacent unit, allies included.
- **Gladiator, Fell Cleave** (new axe skill): 2.4× at S3 (1.80P, heavy axe).
- **Samurai, Kikuichimonji**: 1.6× at S3 (1.45P, range 4).

Original game:

- Blue Mage: Matra Magic 2.4–2.6×.
- Fighter: Air Render and Backdraft, 1.5–1.8×.
- Dragoon: Fight 1.5–1.6×.
- Gladiator: Fire, Bolt and Ice Sword 1.7×.
- Late: Ultima Sword, Ultima Masher, Ultima Charge, Ultima Shot and Ultima
  Blow, 1.9–3.4×.
- Late: Paladin Holy Blade, Alchemist Flare, Warrior Downsize and Time Mage
  Demi, 1.5–1.8×.
- Instant KO effects, reported separately: Roulette, Death and Last Breath.

## Low outliers (≤0.6× stage median, ranked jobs)

New:

- **Chemist** (both races): 0.5–0.6× late, and at the bottom at every stage. It
  has no damaging action; Fight only.

Original:

- White Mage: 0.3–0.45×.
- Time Mage: 0.27× until Demi.
- Illusionist: 0.5–0.6×; single-target damage only.
- Alchemist: until Flare.
- Archer: 0.4–0.55×.
- Gunner: 0.4–0.6×.

Morpher has no shop weapon and is not ranked.

## Caveats

- The model is one action on one adjacent target. It does not account for area
  size, range, charge time, Speed, MP over a battle, statuses, supports or
  reactions, which favor mages, Illusionist, area and ranged skills.
- HP costs are not deducted from the score: Blood Edge 10% HP, Unholy Rite 20%
  HP.
- Prerequisite depth approximates when a job can be unlocked; a player can
  reach a job later than its stage.
