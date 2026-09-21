# Field display under mixed-job load — September 17, 2026

Accepted candidate: `1b070824a8dad4995434eee3ab40fa08187a6120`.
Previous functional/performance witness: `1f197f6c8ca0a28445dd6c3fec245bacf5660df2`.
This completes I07 within the native/Windows-emulation scope below. Final assembled
release acceptance remains R02. No job formula, field effect, saved state, memory
reservation or native animation is changed.

## Problem and implementation

Actual Doublecast with a live field and a queued Absorb Damage reaction exposed
repeated failed display construction while native temporary combat allocations
occupied the heap. The renderer had already surrendered its optional cache,
but every map update still rebuilt field geometry and tried allocating it again.
The previous image completed correctly yet added824/952 emulated frames to the
two paired Doublecast cases—approximately14/16 seconds. Passing HP/MP checks did
not make that delay acceptable.

`geomancer-renderer.c` now admits an absent cache only at the original player
command/facing boundaries (phases37/47), before collecting/projecting its board.
Existing caches continue through actions normally. A genuine native allocation
failure still reclaims graphics and retries the native request; field effects
stay in the unchanged job bank. After memory becomes available, the display
returns before the next interactive turn. During a memory-heavy animation,
outlines may temporarily disappear; their gameplay effects do not.

## Paired actual-game acceptance

`test-geomancer-mixed-playback.py` reuses the candidate's already accepted Rime
and Refuge cast states. Mastery, Viera Red Mage/Summoner job, Spellweave, Bangaa
Absorb Damage, formation, HP/MP and RNG seed are declared setup inputs. Native
Move, targeting, Doublecast/summon execution, queued reaction, facing and next
turn use fixed button scripts. Fields, hit results, allocation success, damage
and animation output are never injected. The control patches only the display
update to retire its optional graphics; field mechanics stay enabled.

| Scenario | Native display / outlines, frames | Added frames | MP spent | Reaction |
| --- | ---: | ---: | ---: | --- |
| Rime + Fire/Thunder Doublecast |1600 /1616|16|12|one final Absorb|
| Refuge + Fire/Blizzard Doublecast |1680 /1696|16|12|one final Absorb|
| Rime + Madeen |1600 /1664|64|36|one final Absorb|
| Refuge + Shiva |1648 /1712|64|18|one final Absorb|

The table measures confirmation-to-native-facing playback, excluding setup,
observation settling and the later facing-confirmation input. Display publication
is separately required within the observer's60-frame bound. The four controls
are paired on the current candidate, not a claim of identical historical fixture
bytes. Current sampled-playback overhead is approximately0.27 seconds for
each Doublecast and1.07 seconds for each long summon sequence (1–4% of these
playbacks). A regression guard limits added frames to the larger of120 frames
or10% of the corresponding native control. Root accepts these measured costs.

All eight executions preserve field records, inventory/AP and native renderer
code; HP/MP outcomes and reactions match their controls. Spellweave finishes
once as Magic; Doublecast continuation is retired; neither subcast charges twice
or reacts early. The display is verified published before confirming facing and
again at the following command menu. Native heap samples stay within the existing
boundary; minimum free payload is4,260 bytes for Doublecast and5,828 for summons.
Doublecast genuinely reclaims the cache during its queue, while the summons keep
it. Sparse samples are not a complete allocation trace.

Root inspected the Shiva summon frame, native darkening and the restored field
at the next menu. Earlier accepted backdrop-selector, Fire/Fira/Firaga, camera,
overlap, pixel/capacity and terrain-readability evidence remains in its original
scope in `geomancer-field-presentation.md` and `geomancer-outline-readability.md`.
The compositor itself is unchanged by this admission fix.

## Exact focused runs

- Build `20260917T080609.980738Z`: six-stage integrated build closure passes.
- `20260917T080703.856021Z`:554 native ownership/allocation checks and146 checks
  across four actual Rime/Refuge occupied/empty casts. The native allocator
  refusal/retry test adds32 bounded absent-display updates across phases39,49,
  57,58 with zero allocation calls and no heap mutation, then recreates at47.
- `20260917T080830.023332Z`:634 checks across four actual suspend/cold-resume and
  two-caster-turn expiry flows;3,612 mixed playback checks across the eight
  executions above. All selected steps pass. No full integration suite ran.

The current candidate's reports and SHA1 values are:

| Report | SHA1 |
| --- | --- |
| `geomancer-renderer-report.json` | `ec1b275077cce434a98e04ee21a184004f1cc8bc` |
| `geomancer-playback/report.json` | `ab22eceb90bd952dca1d60fd9e7489f945135deb` |
| `geomancer-field-lifecycle/report.json` | `b009d5f044fc8034f74bb26d3e07b03e86a4ec47` |
| `geomancer-mixed-playback/report.json` | `daf84a6c47cb83dc3b145c3e221493dd8be8bfbb` |

Raw logs, ROMs, state/heap samples, script snapshots and images remain ignored.
The mixed script's passing source SHA1 is `a943744c047b503a25bddcacb07ff48b293d248a`.
Use its declared normal/resume IDs with the common runner; resume requires exact
ROM/control/scenario/source-state/prepared-state hashes. Preparation itself is
cached against the complete AST-extracted setup function and ready-state hashes.

## Retained failures and limits

The early mixed-script attempts are not acceptance evidence.075238 submitted
commands before native Move reliably returned.075438/075735 revealed wrong-target
outcomes; the proposed alternate seed did not fix them. Full result inspection
found a retained enemy sharing the declared target tile.075949 still reused the
old setup because its substring-based cache fingerprint stopped at text inside
its own string literal. The corrected full-formation, uniqueness and AST-bound
cache checks invalidate those inputs.080211 on the previous image passes4,006
functional checks with the corrected setup, but its observed824/952-frame
performance penalty is the production defect fixed here. Those earlier reports
are not combined into the current passing count.

This is representative native-effects/queue acceptance, supported by the
separate all-map conservative graphics bound and native forced-pressure tests.
It does not claim every possible animation combination, physical GBA performance,
or campaign earning of the declared jobs/skills. Campaign A01/V06 and final
assembly/package R02/R03 remain explicit gates.
