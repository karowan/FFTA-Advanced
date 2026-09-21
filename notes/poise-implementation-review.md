# Poise implementation checkpoint

September14,2026. Private candidate
`c8e339d1b5e24b922ad05704b134c0e3212449be`, based on accepted main
`ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`. The player launcher and save are
unchanged. This is a partial support integration, not full expansion acceptance.

## Implemented behavior

Poise uses Human support129/lesson154 and the existing equipment/AP system.
It reduces eligible native physical/magical damage and custom Iaido damage by
one quarter when a qualifying status was present at incoming-action start.
Current native tags are Regen3, Invisible12, Haste21, Shell24 and Protect25;
their actual native application callbacks establish these bit IDs. Centered
also qualifies, while its consumed execution marker does not. Float, Last Resort
and enchantments require the additional tagged-state provider when those effects
are implemented; no native status bit is invented for them.

`action-snapshot.c` keeps a bounded, temporary snapshot on the CPU stack. Its
only root is four private bytes at0203FF48, after the existing Higanbana root.
It captures the native battle's explicit unit pointers, records actor provenance,
and propagates snapshots through native copies and evaluated containers. It
retires aliases when their stack container closes or heap payload is freed.
No saved per-unit status bit doubles as transient action state.

The action boundary is A433C; the native result boundary atA23B8 covers complete
Counter/Return Magic result objects. Same-actor calculations inherit their
action snapshot, including explicit actor copies. A different incoming actor
gets a fresh snapshot. A support equipped without an initial buff still opens
a scope, so a buff acquired midway through that same action cannot grant
retroactive protection.

Native stage/Fight/combo paths combine applicable Poise and Exposed factors
before dividing. Custom physical finalization combines the action coefficient,
Centered, Exposed and Poise once, after Higanbana captures its P reference.
Original native formulas remain the baseline for original actions. Positive
HP damage classification is explicit; costs, recovery and fixed/percentage
callbacks are not classified merely from a positive result. The complete
category audit remains pending below.

Poise has its own native help entry. The preview and combo bridges now align
the stack before entering C and preserve their extra native arguments.

## Deterministic evidence

### HP-only mitigation and native reaction routing

The earlier b51f candidate discounted redirected MP damage: with49MP, native
Higanbana seed1 removed32MP, but Poise removed24. This failed deterministic
regression is retained in `20260915T024619.395833Z`.

The HP-only factor now reuses native reaction availability, MP and action flags.
It does not recursively call native12E6E0/1306E0 from a damage finalizer: those
functions themselves dispatch damage calculations. Their positive-HP condition
is supplied by the already admitted positive HP stage. Actual native execution
also has reaction gates beyond the assigned ability, including reaction-disable
and position checks. AtA28E2, the new observer records the native executor's
resolved reaction from its per-recipient frame, after those gates. Snapshot
bits3/4 carry known-reaction and Damage-to-MP permission through exact copies.
An explicit native reaction0 therefore takes precedence over equipped13.

This distinction matters for native Counters: they deal HP damage while
bypassing Damage-to-MP. The first attempted correction wrongly removed Poise's
HP protection when MP remained during a Counter. The actual battle test caught
that in `20260915T025656.777315Z`: both control and Poise lost35HP with49MP
unchanged. The regression now requires Poise to retain its25% HP protection in
that case, while preserving the native absence of MP interception.

Native checks on c8e3 pass in `20260915T030146.674123Z` and the expanded status
matrix passes in `20260915T030248.653301Z`. The full-executor MP matrix covers
Fight0, Fire23, actions90/112/125/266, Ashura347 and Higanbana355; each has four
MP amounts and eight fixed seeds. Every action must exercise both positive MP
interception and actual HP mitigation. The status matrix tests every status bit
against native reaction eligibility/admission, with independently neutralized
Poise controls. Explicit copied recipients retain the executor's reaction choice.

The35-step Samurai regression passed its first20 steps in
`20260915T030310.922677Z`, then failed an overly strict ordinary-Wait whole-RAM
comparison. There were226 differing bytes. Matching the next animation frame
left differences solely in native audio: SoundInfo84E0..8E60, CGB channels
8EF0..8FF0, and MusicPlayerInfoF2A0's clock+0C and tempo accumulator+22.
Native initialization literals14519C/1455F4 and1451A0 establish the sound buffer
bases and size; native1416D4 returns the music-player object. The revised test
retains all full RAM/state captures, compares every non-audio byte at a phase
within two frames, and separately requires exact persistent/unit/inventory
equality at every captured frame. No gameplay region is broadly masked.

The failed and pending checks pass in `20260915T031428.077264Z`. Together the
two runs cover all35 declared Samurai regression steps on the same c8e3 ROM.
Earlier passed evidence is reused: the only changed fingerprint is the pulse
test itself, which is not imported by the earlier passed tests. The corrected
Wait comparison matches control/private frame offsets0/1 and1/2, with every
non-audio byte equal. Persistent data, inventory and all canonical units are
also identical at all six captured frames.

The expanded Poise native suite has1752 checks; the separate full-executor MP
matrix has2322. The actual Counter/MP test has12 checks. Guarding Draw's native
Counter loses35HP in the control and26HP with Poise, both when MP is empty and
when49MP remains. In both cases MP stays unchanged by the Counter, as required
by native reaction routing. Other original/native attacks still redirect the
full damage to MP when admitted. The four earlier Counter/status timing cases
and the cold native save/resume test pass again on c8e3.

`build/expansion/checkpoint-poise-mp.py` reconciles exact source fingerprints,
per-step commands and logs, and the private ROM/engine bytes. It freezes the
35-step evidence at
`build/expansion/checkpoints/samurai-c8e339d1b5e24b922ad05704b134c0e3212449be-poise-mp`.
This is implemented-feature regression coverage, not acceptance of the missing
Samurai passives/reactions or the complete expansion.

### Earlier snapshot checkpoint

`20260915T024114.776333Z` passes the native Poise tests, native Samurai executor
regression, Higanbana execution/scope checks and help decoding on b51f.
The Poise test checks every single native status bit, four Human job settings,
all Centered encodings, buffs gained/lost after the snapshot, actor-copy
provenance, independent incoming actors, nested scopes, real copy/free routes,
single-round factor combinations, original physical/magic/Fight/combo previews
and both incoming stack alignments. Help preserves every previous main help
route and decodes all ten new descriptions.

Earlier candidate9a7b failed an actual Counter case: Guarding Draw granted
Protect, but Poise inherited the preceding attack's unprotected snapshot.
The corrected80d1 and964d candidates pass all four actual Counter cases:

| State before the Counter | Native control damage | Poise damage |
|---|---:|---:|
| Guarding Draw just granted Protect |35|26|
| Kiku consumed the only Centered buff |59|59|
| Kiku consumed Centered, Regen remains |59|44|
| Successful Ashura just granted Centered |47|35|

The control disables only the Poise factor; it retains identical native inputs,
weapon, RNG, protection and snapshot plumbing. Outgoing damage is identical.
The964d cold-save check retains474/500HP, Poise154, mastered AP255, equipment and
Protect, with no transient snapshot root after a fresh Resume Battle.
The same focused gameplay/cold-save checks pass on b51f in
`20260915T024135.968051Z`. Exact source inputs and retained evidence are frozen
under `build/expansion/checkpoints/samurai-b51f5e6fe9bcea4990f99ced142795f1ef659447-poise`.
This combines seven focused suites; it is not a full Samurai or expansion
regression. The native Poise suite has703 checks and the help suite3492.

## Remaining acceptance obligations

- Audit multi-stage cases where recipient eligibility changes between the
  executor's resolved reaction and its final HP/MP application. The recorded
  native decision must remain authoritative; check status changes and MP
  depletion within multi-hit actions explicitly.
- Audit every original damage category, original multihit/multicast action,
  direct law simulation and native AI path. The four Counter cases do not prove
  every reflection/reaction path or law/AI copy lifetime.
- Verify transfer with fully legal equipment and native skill selection on other
  Human jobs, and the native damage result after cold resume.
- Join the future Float/Last Resort/enchantment state providers; test status
  loss, ward consumption, redirection and all final modifier combinations.
- Run the full assembled regression and final council after the remaining
  expansion is implemented. Composure, Blade Ward and Counter Draw are not
  implemented by this checkpoint.

All test execution and fixture generation are deterministic local scripts.
No testing agents or player playthrough are used.
