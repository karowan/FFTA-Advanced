# Native deployment palette variants — September 18, 2026

This is technical integration progress, not final artwork or G01–G04 acceptance.
Previous checkpoint: `a53c38b`. Current private candidate:
`21052ed615a6463251cba9b98952b4cc07ba4546`, resolved through
`build/art/live-palette/poc.json`. Parent remains
`0fa7d1707e2d85fb2a8602f061b5eb4479ff3211`. Stage uses 155804 bytes;
transient state uses 8096 of the existing 8192 reserved bytes at
`0203D000..0203F000`. Only Dark Knight is enabled, with the existing unaccepted
built-in-imagegen draft. No package, launcher, player save or session changed.

## Actual native consumer and implementation

The deployment screen simultaneously renders the same class with native bank0
and dimmed bank9. Diagnostic candidate `3979dfe594840cedbd8a6f378271f7d610003558`
separates variant/setup/target/tick refusals. Its retained report
`build/art/live-palette/battle/20260918T064034.204059Z/observed.json`
(SHA256 `ce58165d3aea82d809f9c17f4c0409c03c63d84fdbb3324a161bd09b4ae00e4c`)
attributes all157 refusals to simultaneous variants; other categories are zero.

Native preview setup `0802C0E0` gets the normal palette through `080CBA3C`, then
at `0802C11A` calls `08148104(source,destination,16,0x99)`. Its RGB multiplier
`08148384` computes floor(channel*153/256), equal to floor(channel*19/32) for
all five-bit channel values. It selects bank9 and copies32 bytes to `03003B80`.
The earlier hypothesis that getter `080CBABC` palette21 supplied this variant
was wrong; its failed test remains recorded below.

`art-palette-variants.c` allocates up to ten simultaneous `(class,native bank)`
bindings using a20-byte key/scale map. New bindings require an exact complete
normal or deployment-dim native palette match. Existing bindings retain their
fade state. Slot identity is separate from source class identity: a dim copy
must restore that class's dimmed custom baseline after a fade. Unknown newly
encountered palettes, excessive simultaneous demand and invalid remap tags
refuse before state/color/tag mutation. An identity mapping avoids an extra
OAM pass; masks/tags originate in the authenticated native compositor bridge.
Four counters at8060 distinguish refusals; the map begins at8076. Heap reset
initializes both. Existing field offsets remain unchanged.

This is deliberately incomplete for palette reloads, late entry during an
already active fade, other color operations and all scene/stack/heap lifetimes.
The native reference table currently enables only the demonstrated class.

## Deterministic evidence

All runtime checks use `Test Expansion.ps1 -Plan scripts/native-art-test-plan.json`
with the named `-Only` selections. No broad suite was run.

| Test | Runner | Result |
| --- | --- | --- |
| test-art-palette-variants | 20260918T065348.353736Z | PASS23; native multiplier/all96 channel probes, compiled slot mapping, independent dim fade/restoration, shared-bank classes, atomic refusal |
| test-live-art-palette-native | 20260918T065734.242112Z | PASS1134; current byte-identical rebuild, native hooks and reset including all three heap starts |
| test-live-art-palette-fades | 20260918T065514.330715Z | PASS610 on current candidate |
| test-live-art-palette-transitions | 20260918T065514.330715Z | PASS2933 on current candidate |
| test-live-art-palette-deployment-variants | 20260918T070118.914719Z | PASS587;65 consecutive simultaneous normal/dim observations |
| test-native-layout-rewind-queued | 20260918T070633.818093Z | PASS13; exact retained failure replay and negative controls |
| test-native-layout-queued-commit | same | PASS8; prior verifier case remains valid |
| test-live-art-palette-battle-short-input | 20260918T070659.916367Z | **FAIL**; native shadow/phase mismatch and timing regression remain |

Variant component report:
`build/art/palette-variants/20260918T065348.948736Z/report.json`.
Live deployment report:
`build/art/live-palette/battle/20260918T070119.539575Z/observed.json`.
Both normal and dim copies use exact source-class colors and brightness in
actual hardware. All refusal categories are zero. Native and candidate
screenshots are retained beside that report as `*-entry-10-variants.png`.
Visual inspection confirms two rendered brightness variants; the artwork is
still a transport draft, not an accepted production sprite.

Current battle report:
`build/art/live-palette/battle/20260918T070700.550270Z/failed.json`.
Its derived `trace-audit.json` checks all1205 paired samples beyond fail-fast:
exact generated colors throughout, overlay present, no allocation/ownership
failure, zero unsupported events, preserved units/reservation/native-code
snapshot guards, no scan/display wrap and maximum display line206. Move starts
at51 on both; elapsed movement is126 versus123 frames. Cancel starts at61 versus
49. Every pair still differs in native shadow and unowned hardware colors.
Same final gameplay outcome does not waive timing or native palette acceptance.

## Authenticated queued upload during a constructor rewind

The earlier current-candidate battle run stopped at candidate/move-21 because
the verifier did not recognize a queued upload crossing a native constructor
rewind. Preserve
`build/art/live-palette/battle/20260918T065737.392257Z/failed.json`
(SHA256 `4ae57e412418cf284f679d86eb884dd76480068d73a68d27001a6d857bf90936`).

The13-check proof reuses its matching existing ready state, pinned to SHA256
`43270a7f2985e94387afe45bce707035fff67f4998ca41ad366fd0016e5e6d70`,
and exactly reproduces failed RAM and VRAM without deployment replay. Native
body `02020A2C` has a queued upload at move20 and index/current pointing to the
next command. Its actually captured tile-source field identifies command1.
At move21 constructor flags167 reset index/current to the first command and
clear layout/source while that exact preceding upload finishes.

`native_body_display.py` now accepts this bounded case only with that captured
source, correct prior sequence index and layout, pending flag, a direct recent
anchor, full allocation bytes and unchanged hardware geometry. Ages0/5, changed
source/index/pixel/flags and inferred anchors are rejected. Report:
`build/art/layout-rewind-queued/20260918T070634.446884Z/report.json`.
This changes verification, not game code or timing requirements.

## Retained failures and next work

- Runner `20260918T065022.223242Z`: array-parameter declaration mismatch at
  compilation. Corrected; compile log remains.
- Runner `20260918T065058.011064Z`: wrong palette21 hypothesis. Corrected using
  the actual native multiplier, not by substituting an approximate palette.
- Runner `20260918T065514.330715Z` initially passed48 deployment checks; the587
  check run extends its live observation coverage to65 consecutive samples.
- Runner `20260918T065734.242112Z`: queued constructor-rewind verifier failure,
  independently reproduced and covered as described above.
- Runner `20260918T070659.916367Z`: current battle acceptance remains failed.

Next resolve remaining foreground timing and the native OBJ418..424 palette
copy/phase, then native palette reload/late-entry/color modes and remaining
consumer/lifetime coverage. Finish the technical package before final sprite
refinement. Built-in imagegen only. All G01–G04 remain open.

## Follow-up: original OBJ cycle identified; slower optimization discarded

After checkpoint `06c5fdc`, declared `test-native-obj-palette-cycle` passes2673
checks in runner `20260918T071659.656524Z`. Report:
`build/art/native-obj-cycle/20260918T071705.339739Z/report.json`.
Native initializer `080BA728` calls getter `080CBABC(4)` and at `080BA7A8`
copies14 bytes from returned palette+4 to `03003BA4` (OBJ418..424). Callback
`080BA66C`, called from `080B8434`, rotates these seven colors every six calls.
The isolated component verifies all42 calls in a full seven-phase period,
the counter and complete shadow preservation outside that range. Its draw list
is deliberately empty; this does not cover linked actor rendering or scheduling.

Every one of the1205 retained battle samples on each machine is an exact
rotation of the same native getter source. Parent remains at phase1 and
candidate at phase2. Thus the previously unexplained OBJ difference is a native
cycle-phase difference, not an arbitrary color value. Exact scheduler/input
timing and phase acceptance are still unresolved; no normalization waiver or
G-gate closure follows from this diagnostic.

A full-width multirow scan trial produced private
`39bad79d744c6bed24df288d763473b6fbb6c854`. Native1134 and planner47961 passed
in runner `20260918T071321.895976Z`, but battle FAILED. Its report is
`build/art/live-palette/battle/20260918T071327.503884Z/failed.json`; the derived
audit measures132 movement frames versus123, Move beginning at52 versus51,
cancel at61 versus49 and maximum display line204. It was slower than21052's126
frames, so the implementation was removed. Keep the failed ROM/logs/trace.
The preceding runner `20260918T071253.644515Z` failed its rebuild comparison
against the preceding candidate manifest before gameplay; the new source
revision had produced a different ROM, subsequently verified byte-identically.

Rebuilding after removal reproduces `21052ed615a6463251cba9b98952b4cc07ba4546`
exactly. Runner `20260918T071659.656524Z` passes native1134 and planner47961 on
that restored implementation, alongside the native OBJ diagnostic. The added
planner controls remain: vertical clipping/flips plus a single occupied tile
row ensure invisible rows can be excluded without missing a visible collision.
Reuse the current21052 battle/fades/transitions/deployment evidence; no need to
repeat it after this byte-identical restoration. Next work is native scheduler
timing and remaining color/lifetime/asset consumers.
