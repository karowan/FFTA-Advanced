# Mystic Knight native commands and shared undead policy

September15,2026 Pacific. This accepts a bounded command backend, not the
complete Mystic Knight or expansion. State/support prerequisites are described
in `mystic-knight-state.md`; approved behavior remains the v0.7 specification.

## Implemented behavior

Actions410..423 now have native costs, admission, target descriptors and damage
execution. All require an ordered primary saber/rapier and reject Silence or
Confuse. Eleven enchantments support a Sure self mode and an A-accuracy enemy
strike. A committed miss still prepares the blade. The immediate strike uses
one primary weapon, excludes ordinary weapon drain/procs and uses the shared
single-rounding modifiers. Poison, Sleep, Silence and Slow require actual
positive HP loss before their independent native status roll. Sleep uses S/2;
the others use ordinary S. These commands sequence as Magic while their HP
damage remains physical. Spellbreak sequences as Physical.

The persistent-Fight checkpoint also corrects Sleep/Astra admission: preserve
Astra's native guaranteed interception instead of halving it with S/2. This
applies to immediate commands and persistent Fight; see `mystic-knight-fight.md`
for fixed-seed consumption evidence and the final combined/affected runs.

Drain uses35% actual HP removed, capped at15% user maxHP/action and missing HP.
Osmose uses floor(actualHPremoved/4), capped at10, target current MP and the
user's missing MP for recovery. Neither derives resources from forecast or
overkill. Owned extension claim21 limits the rider to once per acting unit in
the native action. Both use the corrected shared undead policy below.

Flare's immediate strike evaluates75% effective physical defense. Release
consumes its eligible frozen Fire/Ice/Lightning/Flare/Holy enchant at commitment,
even on a miss; it uses r3/cross, projectile LOS and ordinary friendly fire.
Its native M40 formula uses an internal M44 template for neutral Flare before
rounding. Break uses one native Petrify S descriptor, no preliminary HP hit,
and does not replace the prepared enchant. Reflect, Return Magic and Doublecast
are disabled for these fourteen commands.

Spellbreak carries an explicit selected effect through native menu, player
selection, forecast, commitment and status-law evaluation. Selection never
silently falls back. The21 choices are Auto-Life, Regen, Astra, Reflect,
Invisible, Haste, Shell, Protect, Centered, Last Resort, TBN, War Cry,
Inoculated, Battle Chant, Inspired Magic, Magick Boost, Fury, Updraft Float/Move,
Updraft Jump, Steady and prepared Spellblade. Native choices intersect verified
beneficial statuses with native Dispel's removal mask. Harmful statuses, gear,
supports/reactions and placed fields are excluded. Custom choices clear only
their own fields; they do not call a broad lifecycle reset.

The chosen effect is removed after the successful hit/interception boundary
and before physical damage. Prediction removes it on an explicitly owned
stack copy. Native status-law prediction uses its supplied copy and exact
selected native bit; original units and RNG remain untouched. If interception
already consumed the choice, the admitted hit continues without substituting
another buff.

## Storage and native interfaces

The native command-menu descriptor3 at391454+3*20 allocates its row and flag
arrays in27DA0. Its capacity rises22→42, adding100 payload bytes. Native
allocation, pointers and cleanup remain intact. The ordinary Mystic menu has
34 rows:11 enchantments,21 Spellbreak choices, Release and Break. The restricted
constructor26F9C intentionally retains its native nonzero-power filter; its
Mystic result contains only Release. Individual spellbreak rows gray out when
no hostile unit in the exact owner cohort has the selected effect.

The action bank contains446 rows; internal445 is an M44 formula template and
is excluded from the public/queued limit445. No descriptor or application IDs
are added:237 descriptors and112 applications remain. Mystic command code is
in the reserved1300000..132FFFF region. Current sizes are31,864/32,768 bytes
for central integration,10,280 bytes for Mystic and1,408 for Geomancer AI.
The820-byte snapshot ABI, eight owned result slots and save schema are retained.

Root review found that removing selected TBN/Last Resort state alone left its
frozen damage multiplier active. A16-byte stack scope now authenticates the
exact actor, evaluated defender and selected effect during the synchronous
native formula. Its transient pointer owns0203F72C..F72F. Incoming calculation
and barrier admission omit only that selected multiplier. The frozen snapshot,
Poise's action-start eligibility and all other defenses remain unchanged. The
pointer restores its preceding value on return; foreign RAM, expired stack and
bad self tags cannot override factors. The shared Dark Knight helper accepts
an explicit removed-bit mask, with zero preserving its ordinary behavior and
early payment checks. Non-Spellbreak paths skip scope inspection.

Existing effective-defense, success and status-law veneers delegate to Mystic
wrappers and preserve their native register/stack contracts. The success
wrapper retains Samurai's wound capture/disarm path. Chemist's payment and
geometry call sites delegate through Mystic admission/LOS and forward all
other actions. Rebinding uses each compiled region's start/length and protects
instructions with ELF mapping metadata. Literal-only veneer patches assert
their preceding bytes before replacement.

## Shared bug found during review

Older custom code treated unitE8 bit2 as undead. Native application33 at132498
sets that bit for Auto-Life. Native undead predicate1308F4 instead reads native
unit flags through C7EA4(field27), tests0800, and otherwise checks Zombie11
through CD9A4. It reads the explicitly supplied original/copy without mutation.

`src/engine/native-unit.h` now uses that native predicate. Corrected consumers
include Dark Knight/Mystic/Dancer drain, Samurai/Bard/chemist healing,
Recuperation, Encouragement and Requiem. Auto-Life no longer reverses drain or
blocks friendly custom healing. Natural undead and Zombie both do. Native
positive-status/Poise tags are preserved. Older explicitly undead fixtures now
set Zombie11 instead of Auto-Life2.

All single-target Chemist recipes now resolve the exact selected tile within
the actor's owned cohort and revalidate allegiance/eligibility before paying.
The temporary context is fully initialized because revival reads native flags.
Missing, ambiguous, enemy or now-undead targets preserve inventory. Healing
Mist retains separate area admission. Area healing may still pay and heal a
valid caster while excluding an undead recipient; that is not a rejected cast.

## Deterministic evidence

Run from the checkout:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Suite native-undead
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Suite combined
```

Candidate `2bb467cc1c91256d69172317f8e159d519156271`, shared prerequisite
`98d78c6b5d35c09925a3115bef9ec4dee8a7ac45`, passes22/22 affected steps in
`20260916T032336.774912Z`, with `inputsUnchanged=true` and an independent
post-run ROM hash check. Frozen foundation remains
`ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`.

Mystic acceptance:2,383 assertions,200 command/self casts,96 resource-boundary
casts, invalid-commit preservation, native status-law copies, selected-effect
isolation and four ordinary/restricted native menu-constructor cases. Native
undead acceptance:1,642 assertions,315 status/flag combinations on both original
and copy pointers, the original Auto-Life setter,65 actual drain/healing casts,
all single-target recipe rejection cases, Recuperation and Requiem. Existing
native, Chemist, Dark Knight, Bard, Dancer and cross-class checks also pass.

Root's additional formula review passes805 assertions and48 native Spellbreak
casts in10/10 steps of `20260916T035019.174257Z` on candidate
`4ee1c9771bed8d1f4d5b0263113635690f1ce4c7`, with the same shared prerequisite
and unchanged run inputs. Central integration is31,864 bytes; Mystic is10,280.
This supersedes2bb467 for the selected frozen-defense correction. The oracle
uses ordinary native Fight for P and Fira for M40. Its separately hashed M44
reference changes only Fira's power40→44 and Fire→neutral; it does not call the
Mystic internal template or Release's dynamic-element callback. All108 physical
coefficient/defense cases and90 magic-power/defense/affinity cases pass.
Selected-defense casts compare absent, selected and retained TBN/Last Resort
at eight fixed seeds, retaining misses and requiring positive cases.

Earlier reports remain evidence of their actual outcomes:

- `20260916T030045.174938Z`:11/11 focused command steps,2,053 assertions on
  e335551b8dbdd756793737b846c2597835564bbb before resource-boundary additions.
- `20260916T030256.481672Z`:70/71 combined steps on that older candidate. The
  Chemist differential still classified newly implemented Break423 as an empty
  unchanged row. It now conditionally retains that comparison only for standalone
  Chemist images, while the integrated Mystic matrix owns Break behavior.
- `20260916T032027.038910Z`:21/22 on e72722a279c523c65729116129f91cd9f5a03166.
  The new tests found invalid single-target recipe spending and also wrongly
  expected an area cast with a valid caster to be free. Both were corrected.
- `20260916T032311.601705Z`:compiler failure because a zero initializer emitted
  unavailable memset in the freestanding Chemist image. Explicit initialization
  fixes the link; no runtime acceptance is claimed for that failed run.
- `20260916T032737.003036Z`:72/72 combined steps on2bb467, with unchanged inputs.
  This passing run lacked the frozen selected-defense comparisons; root review
  found that issue afterward, so it does not certify the later correction.
- `20260916T034651.667575Z`:20/21 on79977d2fcfcaa32f6814ab0c395bfbe045b40445.
  The48 native selected-defense casts and90 magic comparisons passed;108
  physical comparisons failed because the reference harness did not marshal
  arguments5..7 to the stack. The corrected native call uses explicit stack
  arguments. The subsequent helper refactor also preserves ordinary short-circuit
  lookup order and avoids scope calls for other actions.

The final assembled candidate `4ee1c9771bed8d1f4d5b0263113635690f1ce4c7`
passes all73/73 steps of combined run `20260916T035220.490899Z`, with
`inputsUnchanged=true`. The candidate file was independently rehashed after
the runner exited. This run includes the corrected selected-defense oracle,
Mystic commands, undead-policy checks, native reaction and menu playback,
movement/AI, Geomancer field cold saves and linked-code relocation checks.
Root's bounded source review is complete; no additional agents were used.

## Remaining work

Prepared-enchantment primary Fight effects, Magic Shell, Spell Parry, whole
Doublecast sequence ownership, Mystic descriptions/status presentation and
actual player/AI command playback remain unimplemented or unaccepted. Direct
menu constructors do not prove rendering, scrolling or player selection.
The enlarged command allocation must also be covered by native player playback.
General laws/acquisition/AP/campaign acceptance and fresh-game name-entry heap
allocation remain open. Do not promote this private image as a complete release.
