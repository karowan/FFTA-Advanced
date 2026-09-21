# Native shared palettes remove the reproduced all-ten allocation failure

Full engineering is still required; only final artwork and authored poses are
deferred. Private candidate `a28b624bb13c8f2f2597a4d4bd3999b17c234b99` passes the
declared all-ten capacity scenario. It is not yet release or performance
acceptance. Selector: `build/art/native-palettes/current.json`. Installed7507ca5c,
action5a14e6c7, opposing79e88695 and performance200ca35b remain unchanged.

## Implementation and artwork contract

`scripts/native_palette_transport.py` converts existing imagegen body pixels
at build time to each job's original native party palette. Index0 remains
transparent; opaque indices1..15 map to the nearest RGB555 native index1..15,
using squared channel distance and the lowest index for ties. The original
opposing palette selector then supplies native enemy coloring. This is technical
conversion of existing artwork, not newly drawn art or final visual acceptance.

All ten classes and twenty land/water resources remain. The stage copies796
nonempty streams, preserving every native control command, duration, OAM layout
and descriptor flag; only3025 draw-command tile pointers change. Deduplication
produces52 converted512-byte tiles. The payload uses118752 bytes in the unused
tail of the existing action reservation, starting at0x1F10000. It asserts the
entire reservation is unused and bounds every ROM change.

The stage restores29 authenticated native palette/render/fade hook entries and
sets the custom ownership mask to zero. Original native OAM, palette loading
and effects execute without runtime class-color translation. It keeps the
separate verified heap/menu fixes, reserved memory and lifecycle helpers.
The old module remains as source provenance/inert code; inherited live-palette
metadata does not mean those graphics hooks still execute. Consumers must
recognize the explicit `nativePaletteTransport` component before selecting an
observer. Do not run an old custom-compositor assertion against this path.

Later artwork must be reviewed in both native party and opposing palettes.
Prefer designing against those native ramps rather than relying on automatic
nearest-color conversion for final quality. The existing all-ten source overrides
remain the input; this stage follows action completion. No arbitrary ten unique
hardware palettes are promised by the import interface.

## Passing evidence

Exact report and failure hashes are pinned in
`notes/native-art-shared-palette-evidence.json`; raw files remain ignored.

- `test-art-native-palettes`:6581 checks pass in runner
  `20260919T065414.902630Z`, report
  `build/art/native-palettes/tests/20260919T065415.714225Z/report.json`.
  Actual native getters resolve all retained nonempty resource slots and both
  side palette selectors. Action/control metadata and29 restored hooks match.
  That runner as a whole fails at the following capacity step, not this build.
- `test-art-native-palette-capacity`:17696 checks pass in terminal runner
  `20260919T070002.202864Z`, report
  `build/art/all-class-capacity/20260919T070003.108000Z/report.json`.
  Original formation324 in the disposable Giza shell allocates six party,
  six enemies and judge:13 actors, including all ten added jobs. Every body
  retains its correct resource, bounded native allocation and exact live tile
  upload over120 idle frames and120 return frames. Status opens in its owned
  compact context, closes with balanced lifetime counts, and preserves all13
  actor wrappers. No custom palette ownership demand remains. Sampled minimum
  free heap is11052 bytes; largest free block minimum8776. These are samples,
  not a proof of all intermediate peaks or maximum reachable encounters.

The fixed camera visibly covers nine classes: owners0..6,8,9. Bard owner7 is
allocated and its tile upload is verified, but is offscreen in these observations.
Do not present this as a simultaneous on-screen proof of all ten or a final
visual review. The fixture's same-race substitutions and unchanged native enemy
levels/positions are declared inputs, not campaign eligibility evidence.

## Retained failures and observer corrections

- Runner`20260919T065332.379083Z`: builder asserted28 restored hooks; the
  authenticated inventory contains29. It stopped before publishing a candidate.
- Runner`20260919T065414.902630Z`: conversion passes, capacity fails waiting
  for a menu after1800 frames. Failure retained at
  `build/art/all-class-capacity/20260919T065417.931001Z/failed.json`.
- Diagnostic runner`20260919T065652.133770Z`: screenshot requested before
  the first rendered frame. The terminal log retains the harness error.
- Corrected `test-art-capacity-entry-diagnostic` passes as a diagnostic in
  runner`20260919T065731.327343Z`, report
  `build/art/capacity-entry/20260919T065732.199504Z/report.json`.
  Both no-input and one-confirm branches reach the actual party menu within600
  additional frames. The retained body coordinates show the enemy turn advancing;
  no unit, ROM or state edits resolve it. The acceptance route now permits2400
  frames and observes the menu at2380. This is an evidence-based entry budget,
  not relaxation of the separate Move/cancel performance gate.
- Runner`20260919T065827.573035Z`: all-ten allocation passes; display observer
  confuses native offscreen OAM sentinels with the body allocated at tile0.
  The exact sentinel `(0x00A8,0x00F8,0)` is now excluded. Real matching OAM still
  must have the native32x32/4bpp shape and the exact side/brightness palette.
  Screen bounds determine which owners count as displayed. The retained failure
  is `build/art/all-class-capacity/20260919T065828.442231Z/failed.json`.

## Next acceptance

The old exclusive-bank shortage is eliminated in this tested representation.
E01 remains open: removing the costly graphics hooks is an architectural fix,
but it is not itself measured deployment/Move/cancel acceptance. Obtain a fresh
native-palette ready state with the established Giza inputs and compare raw
native scheduling, motion and input phases to an authenticated original-renderer
control. Do not load historical custom-resource pointers into this candidate or
pretend bypassing an already-native compositor supplies an independent control.

Reconcile E02 effects/participation/UI consumers using the native palette path;
reuse unchanged gameplay/action-graph evidence with explicit dependencies.
Continue E03 demanding encounter/lifetime coverage, E04 campaign/save relevance,
then E05 review, clean full build and independent-save packaging. No promotion,
performance waiver, player-save mutation or completion claim is made here.
