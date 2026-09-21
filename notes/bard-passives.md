# Bard supports and reactions

This batch adds the four approved Bard lessons to the integrated runtime. It
does not certify the whole expansion, campaign, acquisition/AP flows or every
AI/law path. The preceding active-kit checkpoint is in `bard-actions.md`.

## Contracts

**Clear Voice** wraps the actual MP-cost consumer after existing native and
Dark Knight pricing. A positive cost becomes ceil(3*cost/4). The explicit
Moogle-legal incantation list is Black Magic23..32, Time Magic34..42 excluding
the empty37, and Song393..400 excluding Hide398. Stunt, Gunmanship, Animism,
Item and martial techniques do not gain a discount merely from having MP cost.
No other race gains this support or a Moogle-illegal command. Compatibility
effect56 and the individually authenticated Silence/Bad Breath component
setters prevent Silence before any Auto-Cureall consumption for that component.
Other effects still use Viking compatibility and Chemist prevention unchanged.

**Encouragement** observes the original native/custom beneficial applications
around their real callbacks. It compares explicit recipient state before/after
the application and requires a newly absent-to-present persistent tag, a
different ally, the equipped support and a paid primary result. The observed
native tags are Auto-Life, Regen, Astra, Reflect, Invisible, Defense, Boost,
Advice, Haste, Shell, Protect and the native positive stat buffs. Integrated
tags include Marching Strength, Inspired Magic, Inoculated, TBN, War Cry,
Centered and Last Resort. Quick/Smile, cures, passive readiness and field
occupancy are absent from the tag set. Queries do not acquire claims or heal.
Confuse/Charm admission is frozen at action entry; a later native status change
does not turn a forced cast into a voluntary buff application.

One high-byte action claim per recipient queues a separate hidden native HP
restoration. Its payload is min(15% maxHP,60) combined with incoming
Recuperation before rounding; missing HP is capped at application. This
follow-up uses the recipient's own recovery presentation, so it retains the
established exact-wrapper native reaction metadata. It is not another spell,
does not retrigger support/reaction effects, and receives no outgoing charge.
The primary song's healing and this heal remain separate native events.

**Magick Boost** admits actual surviving enemy direct HP loss through the
shared authenticated HP writer, including fixed/percentage HP damage, while
excluding costs, displacement and reaction chains. It queues one visible charge
result. A frozen charge applies13/10 to the next qualifying magical damage or
song HP healing before combined rounding, even though later live state changes
cannot change the current action's snapshot. Qualifying completed casts consume
the charge even on misses or zero healing; Hide and Fight retain it. It expires
at the end of the next own turn, without banking charges.
Forced Confuse/Charm casts neither amplify their output nor consume the charge.

**Encore** requires physical direct HP loss, survival, native reaction
availability and no Silence. Its hidden callback invokes ordinary native Haste
and owns a T2 expiry. A later ordinary Haste replaces this custom expiry with
ordinary duration. It never issues an immediate turn. Both reactions work on
Moogle Black Mage with no instrument; teaching job is not an equipment gate.

## Storage and integration

Owned byte11 contains charge/own-turn-skip in bits0..1 and Encore's three-bit
T2 value in bits2..4. Byte10 retains the two song buffs. The existing16-byte
records and608-byte save footer do not grow. Extra frozen flags use bits2..6;
the temporary bank's high byte owns action claims24..28. The original820-byte
stack snapshot ABI remains intact. High-byte claims require an authenticated
primary RESULT/COMPLETING scope and never mutate a QUERY.

Root adds hidden actions438..440, descriptors228..230 and applications105..107.
All17 native action pointers and checked interior references are rebound.
Descriptors/applications/masks move to11EC000/11EC400/11ED000. Independent job
builds retain438 actions; the shared queue's optional root provider permits441
only in the integrated image. Magick Boost uses status key35 and tiles1F4..1F5;
the dynamic OBJ pool begins1F6. All12 Bard action/support/reaction descriptions
are installed. The machine-readable allocation ledger is authoritative.

## Evidence and limits

`scripts/test-integrated-bard-passives.py` exercises native MP pricing/payment,
both native queued reactions, first/refresh buff healing, charged Fire and
Angelsong, Recuperation, preventive Chemist recipes, Silence and Bad Breath,
Quick/Smile/self exclusions, charge consumption and Haste replacement/expiry.
The corrected affected run `20260915T095313.608791Z` passed943 assertions,
including254 actual native action executions on candidate
`a68bb42ad69a61aeab2d171545490b5ae281c305`.

The first44-step suite `094606.356063` retained41 passes and three test failures.
The shared queue test still treated the newly valid438 as out of bounds; its
boundary is now441 for root and438 for independent builds. The synergy helper
needed the same bounded3M native instruction allowance as other executors.
The reaction test's Disable assumption was replaced with explicit Petrify;
native reaction availability remains authoritative. A later healing test found
the shared equipment helper parsed `SLD-AX-S1` as an action and wrote the R slot.
It now uses the registry lesson type and verifies the exact returned lesson ID.
Neither failure was fixed by weakening the gameplay arithmetic.

The expanded36-case playback run `20260915T095634.042211Z` passed all43 preceding
combined steps and all attack/playback scenarios, then failed the Bard charge
precondition for cold save. Captured RAM showed the charge present after actual
reaction execution and rendering, but absent at the next player menu. The
controlled hostile Moogle had taken its intervening AI turn, correctly reaching
the charge expiry before the test attempted to save. Bard's revised fixture
initially tried Act before Move so Marche could suspend with the charge still
active. Report `100447.127373Z` retained the failure of that attempt: native
FFTA ignores the menu-cancel/Start path after spending the action. A bounded
scripted capture in `100910.700688Z` shows it remaining on the turn menu and
then entering Status rather than saving. The final fixture instead declares
the attacker hostile and the reacting Moogle player-controlled before attack
inputs. Move, Fight, reaction, rendering and the next-turn menu remain native;
saving can occur before the reactor completes its next turn. No saved state,
allegiance after execution, or reaction output is repaired by the test.

The same `100447.127373Z` run caught live-status-only forced-action admission:
Confuse could be cleared during the native cast before charge retirement.
The fix reserves extra frozen bit6 and uses that action-entry decision for
both Magick Boost and Encouragement. The corrected native test passed967
assertions including262 native action executions in `100910.700688Z`, with
charged/un-charged Fire comparisons and positive native Haste controls under
both Confuse and Charm. This verifies these explicit forced statuses, not all
unexamined AI/control paths.

The consolidated run also includes existing job regression and deterministic
playback/cold-resume cases. Native Bard command banners, every song animation,
full AP/acquisition, detailed law reporting and complete AI/forced-action
acceptance remain explicit expansion obligations. Exact latest results are
recorded in `../IMPLEMENTATION-STATE.md` after completion of the run.

Final candidate `828b2c3667bcbe919a1c2618c5e311a1a49a8732`, shared base
`6158684473d543b83be6c7233aaf804d2d93360b`, passed all44 combined steps in
`20260915T101350.142914Z` with unchanged inputs. The script records967
assertions and counts262 successful native executor returns. Reaction playback
records539 checks,36 scenarios and five native cold resumes. Both Bard effects
are positive before saving and preserved after a fresh ordinary-ROM boot:
Magick Boost byte11=01; Encore byte11=08 plus native Haste21. Earlier affected
playback report `20260915T101029.955255Z` passed the same539 checks. Source and
documentation are committed separately from all private binary artifacts.
