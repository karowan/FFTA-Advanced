# Geomancer outline readability — September 17, 2026

The revised compositor uses a two-pixel light core over a four-pixel dark
shadow, clipped to the original sixteen-pixel native quarter. All shadows are
combined before all cores, so overlapping fields cannot erase each other's
light pixels. Rime remains dashed and Refuge continuous. Native palette banks,
quarter-plane ownership, field mechanics, memory allocations and save layouts
are unchanged.

An initial unbounded shadow passed the pixel oracle but exceeded the conservative
672-slot bound on eleven maps (run `20260917T073211.217141Z`). It was rejected.
The bounded stroke passes run `20260917T073430.218616Z`: 240,847 detached ARM
pixel/ownership assertions, all 162 maps with independent animation states
(maximum 669 tiles), and an authenticated two-caster terrain comparison.
Production module source digest: `584557ef8234102bba9d87c132150d639cb83f14`.
The historical display-capacity experiment is explicitly labeled historical;
`test-geomancer-animation-capacity` is the current conservative capacity gate.

The comparison reuses battle RAM `f22c785b38ec5c2d014be328a4981407940da3c4`
from candidate `55f231768cfffdbfc2383191f8648716d452375d`, map70, camera(-19,262),
eight field cells. It calls the current compiled production compositor on that
scene without creating a new gameplay fixture. The revised view changes348
visible pixels and uses203 tiles; the retained old view used228. Root inspected
the terrain-only comparison: the core is clearer against grass and the dashed
and continuous shapes are distinct. This is not yet across-terrain readability,
live publication, sprite occlusion or performance acceptance.

Next bounded acceptance: build the composed candidate through
`build-integrated-jobs` and its six-step build closure, then select
`test-geomancer-renderer-cached`, `test-geomancer-cycle-budget-cached`, and
`test-geomancer-field-ui` (including its native battle preparation and four
actual casts). These directly cover installed allocation/publication, CPU cost,
and Move/Act/Status consumers. Reuse all unrelated job evidence. Final release
cold lifecycle and other remaining I07 gates remain separate.

## Installed candidate acceptance

Candidate `1f197f6c8ca0a28445dd6c3fec245bacf5660df2` builds in
`20260917T073606.909621Z`. Targeted run `20260917T073649.600544Z` passes:
488 native allocation/ownership/publication checks,146 checks across four
actual Rime/Refuge occupied/empty casts,220 checks across twelve paired native
Move/Act/Status flows, and four paired CPU timing scenarios. No full suite ran.

Move readiness (native display / outlines) is178/189,156/173,165/179 and173/187
frames:11–17 added frames, or6.2–10.9% for these fixed scenarios. At the emulated
60Hz rate this is approximately0.18–0.28 seconds. Original inputs/stats/fields,
inventory/AP and menu behavior agree. Camera-fringe reuse saves56.3%,65.9%,
59.1% and62.1% versus a full redraw on maps4,27,67,155. These are current paired
controls, not a historical speedup or physical hardware claim. Root accepts
this bounded cost for the Windows-emulation target; field readability improves
without increasing memory reservations. Pathological load and final mixed-job
acceptance remain explicit I07 work.

`test-geomancer-readability-terrain` consumes those authenticated timing outputs
without recreating their native fixtures. Its initial073936 artifact exposed
that animation-following cameras could leave fields offscreen. It is not used
as visibility evidence. The corrected `20260917T074039.055238Z` explicitly centers
only the detached review camera on the existing field cells and requires at
least12 changed visible pixels for each style. Both styles render on all four
maps. Root inspected the resulting native/dashed/continuous comparisons against
carpet, stone, detailed indoor scenery and outdoor paving, plus the earlier
actual grass scene. The shapes are distinguishable; sprites and HUD can still
obscure terrain normally. This artifact does not claim those indoor placements
were legal player casts or a campaign playthrough.

Reports remain under the exact candidate's `geomancer-renderer-report.json`,
`geomancer-playback/`, `geomancer-field-ui/`, `geomancer-cycle-budget/`, and the
source-digest `geomancer-compositor/` directory. RAM/images/ROMs remain ignored.
The final release must still cover mixed-job pressure/action effects and cold
restoration on its frozen layout. No job formula, AP, item, law or save field
changed in this batch; their retained evidence is not rerun solely for a ROM hash.

## Current-layout cold and animated terrain acceptance

Run `20260917T074302.835903Z` passes only assembly verification,
`test-geomancer-display-lifecycle-cached`, and
`test-geomancer-render-timing-cached`. The four existing cast states enter native
suspend, cold boot from cartridge SRAM and Resume Battle. All634 checks pass:
field owner/timer/center/coverage, stats/AP/inventory and current turn survive;
only caster turns tick; after two caster turns the field clears and the display
retires. Root inspected the unobstructed portion of the empty-target Refuge
cold-resume capture; the continuous outline is visible on grass around units.

The native animation consumer passes160 producer/update/pump steps across four
maps,320 exact independent published-plane comparisons, camera/fringe reuse and
final-frame draining. Neither suite regenerates the gameplay fixture. This
closes cold/animation acceptance for this candidate's current layout. Revisit
only if later changes affect those consumers/lifetimes, or at the assembled
release gate; remaining I07 mixed-job pressure/native effects are still open.
