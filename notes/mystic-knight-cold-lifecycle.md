# Mystic Knight saber presentation and cold state

Candidate `687ed5d48494dcb46d8b70612680ede56d5dec86` corrects a real native
animation stall exposed by accepting the approved saber weapon family.
Viera Mystic Knight125 now uses its existing rapier actor pose when the real
primary weapon is a saber. The true item/category remains available to combat,
AP, equipment, sound and law consumers. Other races/jobs retain their native
saber pose; existing Nu Mou Chemist and Viera Dancer knife aliases are retained.
No new art, save state or equipment permission is introduced.

The override is installed in the **final integrated layer**. The first engine
stage deliberately compiles pinned historical bootstrap source; changing a
modern shared source file alone cannot change that binary. Root compiles the
current pose assembly into the Mystic code reservation and replaces only the
authenticated actor-switch pointer at986E0. The other three visual hooks keep
their existing bindings.

## Evidence

Initial run `20260917T050820.776322Z`, on9fef4cbe, executed three actual native
player flows. The rapier Osmose case completed and cold-resumed successfully:
enchantment kind10 bound to item88 plus Magic sequence2, encoded17802;
SRAM SHA1 `b298edb7b8b6762e2eebf4ae454bf6220fa7baa7`.
Fire self-preparation and Spellbreak with sabers resolved their effects, but
stalled during actor animation and never returned the turn. That report
remains failed; its2,197 recorded assertions are not a full-pass claim.

The passing rapier case remains retained under:

```
9fef4cbe557b69ec9fc9d63ed0f39ed38e8782a6/
  mystic-knight-lifecycle-20260917T050821.439517Z/report.json
```

Follow-up run `20260917T051337.366785Z` selected only
`test-mystic-saber-pose`, `test-mystic-knight-saber-lifecycle` and their seven
assembly/battle preparation steps:

- 32,640 native pose assertions pass. Every24-race/126-job pair at both stack
  alignments proves the saber exception is confined to Viera125. All22 native
  and added sabers follow native rapier pose behavior across12 animation modes,
  four facing values and both stack alignments. Registers, flags, native frame
  and actor state match the independent native control.
- 405 player-flow assertions pass. Fire preparation with original saber35
  completes in681 observed playback frames, does no strike damage, and retains
  encoded16945 (Fire, item35, Magic sequence). Spellbreak with teaching saber440
  finishes in666 frames, deals20 HP, removes the selected Protect only, retains
  the prepared Fire enchantment and establishes Physical sequence1 (15233).
- Both native suspend saves resume in a fresh uninstrumented emulator. The
  complete owned22-byte record, gear/lessons, AP/inventory and HP/MP survive;
  transient roots are empty and native renderer code is intact. Save SHA1s are
  `18c1e6ffe27f26133c0953d1dab984cb31431db1` and
  `9def2f0fbe0d02ab2edb5677ff36f896878bfe8c` respectively.

Passing reports under the current candidate directory:

```
mystic-saber-pose.json
mystic-knight-lifecycle-20260917T051422.961566Z/report.json
```

Root inspected the actual cold-resumed/next-turn images: native menus return
and the P+/M+ sequence indicators remain visible. The script checks glyph
uploads and renderer bytes independently. Actual flows give mastery/equipment
and declared initial conditions before inputs, then use native menus and a
fixed RNG input. They never inject hit, damage, save outcomes or enchantment
results. Spellbreak's initial existing enchantment is a declared fixture input;
Fire and Osmose earn theirs through the actual cast.

A direct `Build Engine.ps1 -SkipTests` attempt failed to link modern job-state
providers before the correct final-layer installation was selected. No game
image was produced by that failed attempt. The linker removed its output ELF;
the exact pinned bootstrap ELF was recovered from the successful clean-source
build workspace233352.530133Z after verifying matching engine bytes/symbols.
Future clean reconstruction follows `REPRODUCIBLE-BUILD.md`, not a modern
standalone first-stage compile. No bootstrap pin was changed.

## Limits and reproduction

This closes the specific Mystic enchantment/sequence cold-state gap and the
newly found saber stall. It does not certify every save slot, full-roster
replacement, all animations, full campaign progression or final combined
acceptance. Those remain separate checklist entries. The passed Osmose flow
was not repeated when only saber presentation changed.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-saber-pose,test-mystic-knight-saber-lifecycle
```

For a later relevant whole Mystic lifecycle gate,
`test-mystic-knight-lifecycle-cached` runs all three cases on authenticated
unchanged assembly. It is not needed merely to update these documents.
