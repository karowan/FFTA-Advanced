# Native target highlighting and damage palettes — September 18, 2026

Follow-up to source checkpoint `734c937`. Built-in imagegen only; technical
E2E precedes final artwork refinement. No new art/provider, agents, publication,
visible game launch or player-save writes occurred in this checkpoint.

## Result and remaining gates

Connected candidate `7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b`, palette parent
`fa3d12b4ce149537d3b2776dc726bd214b9303b4`, fixes two actual native consumers:
area-target shared highlighting and late appearance during a damage flash.
Thundaga371 now passes target confirmation, casting, self/target hit reactions,
MP payment, damage and next-turn return. Both composition-active and exact-ROM
composition-only bypass branches deal14 target damage, leave80 MP and retain
33,668 bytes minimum free heap /28,164 largest block over four-frame samples.
Modes63(cast) and11(hit) actually reach VRAM. This is a bounded12-actor/four-new-
class encounter, not maximum capacity or all ability/effect families.

Full art-stage rebuild reproduces the candidate byte-exactly. The installed
preview remains `4a7d55ce09cd4a40965a0bb97de2701d276789c5`: it has the two now-
reproduced limitations. Do not describe that old package as having these fixes.
No replacement package was published. Current candidate is resolved from
`build/art/connected/current.json`; installed package has its independent
`build/art/pipeline/delivery/current.json` index. G01–G04 remain open under final
art scopes. Next: concrete larger encounter/effect capacity, final applicable
consumer reconciliation and updated isolated delivery, then sprite refinement.

## Native causes and implementation

The original area-target setup at080B70F2 copies exactly32 bytes from native
bank15(03003C40) to bank9(03003B80), then marks target objects with palette9.
Original080B4FF8 independently pulses colors2..15. This is intentionally a
shared highlight, not an alternate normal/dim class palette. The prior matcher
rejected it and suppressed all class-color overlays.

The copy hook now recognizes only exact caller080B70F7, source, destination,
length and full original reference table08419F40. It retires any former bank9
class history and leaves highlighted shapes under native palette ownership.
The allocator still sees those objects as native occupants, so another custom
palette cannot overwrite them. An overlapping later native copy revokes this
recognition; heap reset clears it. Original target setup, pulse code, native
palette shadow and custom shape tiles are unchanged. Four transient bytes at
live offset11312 bring the state to11,316 bytes inside the same12KiB reservation.
No serialized player data or heap limit changes.

After the highlight fix, actual Thundaga hit playback exposed bank12. Original
080DAF4F starts a blend over449..463 (colors1..15), duration6;080DAFCD restores
from native bank0 colors1..15. At effect start bank12 is the exact authenticated
normal reference, before the class changes to that bank. The prior history
tracker required all16 colors, so it missed the valid late-appearance history.

Variant tracking and mapped effect starts now support full banks or colors1..15.
The complete16-color baseline is still authenticated. Partial table mapping
reads only the supplied15 colors, preserves color0 and maps original or uniform
targets. Native interpolation already accepts an explicit mask; it now receives
the matching prepared history. Provisional history reconciliation uses the
same range. Other partial ranges, unrecognized confirmed targets and unsupported
durations remain explicit refusals. No generic approximate color matching.

## Evidence

All runtime checks used the declared plan through `Test Expansion.ps1`, with
exact IDs and purpose announced. All enclosing runners listed below are terminal.
Reports and complete captures remain private under `build/`.

| Test ID | Checks | Child report under build/art |
| --- | ---: | --- |
| test-art-damage-mixed-entry |632| live-palette/battle/20260918T210407.312558Z/observed.json |
| test-art-damage-palettes |4,320| connected/damage-native/20260918T210402.437648Z/report.json |
| test-art-damage-additional-operations |8,886| connected/damage-native/20260918T210558.209041Z/report.json |
| test-art-highlight-thundaga |4,568| connected/casting/20260918T210607.758256Z/report.json |
| test-art-damage-boundaries |26| connected/damage-native/20260918T210802.664343Z/report.json |
| test-art-native-highlight |157| connected/highlight-native/20260918T210803.082966Z/report.json |
| test-connected-art-rebuild |3| connected/full-rebuild/20260918T210803.391213Z/report.json |

Runners: `20260918T210401.641437Z`, `20260918T210557.444151Z`,
`20260918T210801.928456Z`. Native component oracles use ARMv4T TI925T and actual
original setters/callbacks, all ten generated palettes, both stack alignments,
transparent-color preservation, partial restoration and unrelated-memory checks.
Blend cases include durations0/6/17 and interruption. Additional operations
cover black/white/gray/tint/RGB/solid/brighten/darken/exposure/per-channel exposure/
table-exposure/table-blend at duration6. Boundary cases distinguish unconfirmed
retirement from confirmed rejection and exercise uniform partial targets.

The Thundaga test observes32 actual composition boundaries with every highlight
hardware color unchanged. Remaining generated body colors equal their computed
visible buffers over the cast; this is not an independent every-frame oracle for
all transformed live colors. Root viewed the highlight and lightning/hit captures.
Their temporary generated shapes remain visibly crude and are not final art.

Thunder365 active/bypass already passed on4a7 in the retained failed combined
report `connected/casting/20260918T203709.455123Z/failed.json`: damage8, MP94,
cast mode63, minimum free33,668. Reuse its bounded unchanged-gameplay evidence;
do not relabel it a7507 exact-candidate pass or rerun merely to recover context.
The existing4a7 menu/portrait/weapon/impact passes retain their original scopes.

## Retained failures and diagnostic provenance

- Runner203518.468750 / casting203519.192332: test rejected the native caster
  sequence reset at frame200 after Thunder. The later strict retained-display
  rule authenticates the preceding full allocation and actual hardware objects;
  it never counts the stale display as a newly uploaded casting pose.
- Runner203708.735640 / casting203709.455123: actual4a7 Thundaga area-target
  refusal, already369 occurrences at confirmation. This is a real integration
  failure, not the earlier native-reset test issue.
- Runner204050.373794 / highlight-trace204051.015743: no palette-copy calls in
  idle confirmation;97 state/frame equality checks pass, missing-call assertion
  fails. Transition trace204207.113220 passes2,355 checks/10 calls and identifies
  the actual bank15-to9 load.
- Runner204910.953771 / highlight-writes204911.653514:34 checks,420 bank9 writes
  at080B50D4 from080B5A89. Every32-frame full native state/framebuffer matches a
  fresh ordinary core. No game instructions/state were changed by observation.
- Runner205352.919591: intermediate3f049cac passes157 native highlight checks
  and its mixed entry. Runner205549.206047 / casting205550.006179 then fails a
  test-only native return-to-idle reset assertion at444; highlighting already
  passes. Exact retained source/layout/hardware evidence permits only mode7,
  flags167, phase1 of its four-frame native sequence within four video frames.
- Runner205729.442572 / casting205730.189020: intermediate3f049cac then exposes
  the real damage-bank failure at500. The corrected reset check did not hide it.
- Damage write traces205924.559505 and210027.133615 each pass582 full-state/frame
  equivalence checks over580 frames. The latter includes original fade entry
  arguments and full bank12 snapshots, proving exact normal baseline before
  native449..463 blend/restore. Diagnostic ROMs remain pinned to their captured
  states; do not load an old mid-battle state against relocated new hook code.

No broad integration suite was run. No maximum-encounter, every-cast-family,
complete-campaign or final-art acceptance is inferred from these bounded passes.
