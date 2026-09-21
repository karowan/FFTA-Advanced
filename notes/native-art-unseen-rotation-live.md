# Actual first appearance after unseen rotation — September 18, 2026

Follow-up `5bf50bc`. Private ROM remains
`2908487c5de59274b03b71c59add5ab828bcba34` through
`build/art/live-palette/poc.json`; stage161196/state8096 bytes. This checkpoint
changes verification only. Built-in imagegen only; final sprite refinement is
deferred. No package, launcher, player save or running-session change.

## Actual display proof

Declared `test-live-art-late-rotation` passes1595 checks in runner
`20260918T101602.403002Z`. Report:
`build/art/live-palette/fades/20260918T101603.041260Z/report.json`.

Eight paired original/candidate cases cover type2 rotation and type4 literal
cycling, both directions, whole-bank left and partial-bank right ranges, and
active or completed tasks when the actor first appears. Each uses the native
draw-enable flag to hide the existing menu actor, drains queued body buffers,
and invokes the owned-state initializer before the effect. The running mGBA
core advances the real native callbacks and palette DMA. Only declared native
command inputs are installed through the ARMv4T clone; expected colors are not
written to the game.

Before reveal, the candidate must have changed generated colors, an exact
class/native-bank history and zero fade starts, completions or refusals. This
exercises the previous latch bug's precise condition. The independent original
dispatcher supplies the native and generated color sequences.

All25 consecutive video-frame samples after reveal are recorded. Sample0 has
no overlay and remains exactly native; sample1 is the first visible generated
overlay in all eight cases. It already has the correct colors. Every subsequent
sample preserves exact paired native shadow, canonical units and unowned
hardware colors, with generated colors at the same identified native DMA phase.
There are no ownership/allocation failures or unsupported events.

The initial runner `20260918T101229.129096Z` passed1443 checks at
`build/art/live-palette/fades/20260918T101229.805025Z/report.json`, but skipped
three frames after reveal. Source review identified this blind spot. The later
1595-check run supersedes it for first-visible-frame acceptance. Neither run
failed. This remains controlled menu input, not naturally triggered scenes,
all classes, cross-bank identity, maximum capacity or battle timing acceptance.

## Current exact-ROM timing

Runner `20260918T101334.941664Z` passes the declared diagnostic pair:

- `test-live-art-palette-cost-fixture`: current-ROM native route and authenticated
  ready capture at `build/art/live-palette/battle/20260918T101335.606659Z/observed.json`.
- `test-live-art-palette-current-cost`:30 checks at
  `build/art/compose-cost/20260918T101353.995131Z/report.json`.

| Current2908487c exact-state case | Move starts | Move ends | Moving frames | Cancel starts |
| --- | ---: | ---: | ---: | ---: |
| Active | 17 | 64 | 47 | 26 |
| Compositor bypass | 16 | 62 | 46 | 23 |

The active build still adds1 frame before Move,1 during movement and3 before
cancel. Final positions and canonical unit records agree. This is diagnostic
success, **not timing acceptance or performance improvement**. The final unseen
latch fix now has a valid current measurement, identical to preceding9d577c53's
measured timing. The separate full battle's phase/input failure remains open;
the three invalid cross-ROM timing reports remain invalid. See
`native-palette-timing-followup.md` for their exact paths and reasons.

## Native clear and reproducibility

`test-live-art-palette-native` still used Unicorn's default CPU model. It now
selects TI925T ARMv4T immediately after CPU creation, before maps or writes, just
like the palette components. Runner `20260918T101510.513151Z` passes1153 checks;
report `build/art/live-palette/native/20260918T101511.147393Z/report.json`.
The byte-exact rebuild stays2908487c. Native clear boundaries, current/legacy
heap endpoints, unrelated-clear controls, original patch bytes and sequence
transport remain valid under the corrected CPU model.

## Remaining work

All G gates remain open. Investigate foreground/VBlank work with this ROM's own
ready capture; do not load saved actors into relocated ROMs. Natural effect and
scene lifetimes, mixed-class capacity and cross-bank color identity remain
unaccepted, as do the remaining complete-scope artwork and delivery gates. Use
the current evidence rather than repeating the passed appearance tests to
reestablish context. No broad integration run was needed for this checkpoint.
