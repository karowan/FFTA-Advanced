# Live palette phase and foreground timing — September 18, 2026

Current connected ROM `4a7d55ce09cd4a40965a0bb97de2701d276789c5` is unchanged.
The measured mixed-battle Move/cancel path now has direct evidence that its
different background colors are ordinary native animation phases. This is a
bounded reconciliation of this candidate and scene, not retroactive acceptance
of the rejected optimization candidates or their failed reports.

## Evidence

All checks ran through the declared native-art plan and `Test Expansion.ps1`;
all runners are terminal. Private paths below are under `build/art/`.

| Test ID | Runner (20260918T…) | Child report | Result |
| --- | --- | --- | --- |
| test-art-foreground-events | 200310.536246Z | native-frame-events/20260918T200311.228371Z/report.json | 1,069 checks; all 1,024 native states and framebuffers exactly match ordinary execution |
| test-art-battle-stage-events | 200700.664580Z | native-frame-events/20260918T200701.275078Z/report.json | 5,173 checks; exact observation equivalence and actual palette boundaries |
| test-art-native-phase-evidence | 201139.952277Z | native-phase-evidence/20260918T201140.570479Z/failed.json | Failed: original ready-state OBJ palette was the wrong post-navigation oracle |
| test-art-native-phase-evidence | 201316.126719Z | native-phase-evidence/20260918T201316.851984Z/report.json | 6,225 checks; original native rotation oracle and paired post-navigation OBJ shadow |

The complete stage-event report SHA256 is
`5580a5e1652576ff9324e8b14b7e364016b0dad7b1fe52dd5cadb8d2135a5bd0`.
The phase test authenticates it, the current ROM and original RAM/IWRAM. It
restores the original eight bytes at native rotation entry `08146864` in a
detached clone, then executes both original tasks at `03003C7C` and `03003CB4`
for 64 ticks. This independently produces seven full native palette phases.
Only BG offsets 324–351 change. Every observed complete 512-byte BG shadow
matches one of these exact phases; no arbitrary colors or frame alignment are
allowed. Every complete OBJ shadow matches the paired same-input control.

The failed oracle had used the ready-state OBJ bank 12 before navigation.
Navigation changes that bank identically in both branches. The corrected test
compares the appropriate post-navigation native OBJ shadow and retains the
failure. It does not broaden the allowed BG phases or mask an OBJ difference.

At all 1,024 observed composition boundaries, the full 1,024-byte native shadow
is unchanged by composition, all 512 BG hardware bytes are unchanged, and the
native fresh/skipped DMA decision exactly determines the displayed BG phase.
Composition and display return finish within VBlank. Active display-return
maxima are scanlines 214/215 during Move and 211 during cancel.

Raw active/control phase differences remain in the report: Move differs in all
128 frames at both input offsets; cancel differs in 98 and 113 frames. These
timelines have not been shifted, normalized or converted into pixel equality.

## Response cost and root decision

Inputs and frame origin are unchanged from the instruction-trace note: eight
held frames followed by 120 idle frames, with extra pre-Move idle 0 or 4.

| Extra idle | Active Move start/end/duration | Control | Active/control cancel return |
| ---: | --- | --- | --- |
| 0 | 24/71/47 | 23/70/47 | 32/28 |
| 4 | 24/72/48 | 24/70/46 | 33/28 |

The first pressed input reaches the native poll in frame zero. The longest
cancel work is the native battle controller `08092784`, within callback
`08096E79`. Its interval takes about 6.347 video frames excluding VBlank work
with composition active, versus 6.342–6.343 in the control. Inclusive intervals
are 9.200/9.336 versus 7.724/8.032 frames. Extra per-interrupt rendering explains
the longer foreground response; this is not evidence of a lost button press.
Nested inclusive callback durations must not be added together.

Root accepts the measured four-to-five-frame cancel cost (about 67–84 ms at
60 Hz) for this technical Windows-emulation preview and this scene. Zero
additional latency is not an acceptance requirement. This is consistent with
the earlier explicitly bounded Windows cost decision in
`notes/geomancer-outline-readability.md`; that precedent is not a substitute
for the direct measurements above. No speculative optimization is retained.
Larger encounters, different effects and input phases remain separate coverage.

## Next boundary

This resolves the current mixed Move/cancel phase question and accepts its
measured response cost. It does not prove maximum heap demand, all natural
caster/effect/weapon families, current-candidate packaging or final artwork.
Continue technical integration and separately playable delivery. Built-in
imagegen remains the only requested artwork provider; final sprite refinement
is deferred. No player save, installed preview or running session was changed.
