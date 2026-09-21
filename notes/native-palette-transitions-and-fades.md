# Palette transition timing and native fade interpolation

September 17, 2026 local. Previous checkpoint 43c1461 was progress, not
completion. This continuation found a real live timing defect, corrected it,
and implemented a separately tested native-compatible fade primitive.

Private candidate: `19c8d9e05546607ad12d76be27fab1be6a4f9dbf`, resolved through
`build/art/live-palette/poc.json`. Parent remains 0fa7d170; packaged a6d883b5
is unchanged. No new art, publication, window launch or player-file mutation.
G01-G04 remain open. Built-in imagegen remains the art source; no external
provider was used.

## Real defect and correction

The former steady-menu samples did not cover transition frame load. New
`test-live-art-palette-transitions` samples every frame of wheel -> header ->
roster -> world, plus three explicit one-frame suspension requests and resume.
On caff9140, seven active frames crossed the end of VBlank: examples were
172..1 and 175..4 with scanline wrap. The world palette sequence also lagged
the parent by one frame over eight samples. This is retained failed evidence,
not a passing baseline or proof that the earlier whole transition was safe.

First optimization: skip exactly transparent 16-byte blocks before ROM lookup.
Private 6c7ec331 then avoided the measured scan wrap, but ended as late as 227
and retained the one-frame world palette delay. It was not accepted.

Final optimization: normal 8bpp objects scan only tiles intersecting the screen.
The native 64x64 portrait is positioned at x=-32, y=-8, horizontally flipped;
much of its source footprint cannot be displayed. Whole off-screen tiles are
skipped with signed/wrapped OAM coordinates and both flips honored. Partial
tiles stay whole, conservatively reserving all their colors. Affine and mosaic objects
retain their full source footprint. Mosaic can repeat an off-screen source
pixel into the visible region, so ordinary clipping is not valid for it. Entire source bounds are checked first.
An independent pixel-coordinate oracle covers thirteen clipping/flip/affine/mosaic
cases, while all fifty retained actual-menu demand cases still pass.

The private stage additionally hooks native display restoration at 08000788,
preserving its exact prologue through a trampoline. It records VCOUNT and
DISPCNT after native display enable, so the check covers work after the scan.
Two uint16 fields at state offset 2736 bring the transient structure to 2740
bytes; the existing reserved page and all earlier observation offsets remain.
ROM stage now uses 149,936 bytes of 01F90000..01FD0000.

Final actual transition pass: 571 frames per paired machine, 205 active-overlay
frames. The latest observed scan finish is 220; native display enable is 221.
The ready sample is 166..213, display enable 214. Complete native shadows,
all hardware colors outside allocated banks and canonical unit bytes match
the parent at the same frame. The one-frame delay is gone; no alignment waiver
or ignored palette mismatch was introduced. This remains bounded menu evidence,
not a worst-case whole-game timing budget.

Native 03000E10 is a one-frame suspension request, consumed and cleared by the
game. The test reasserts it before each of three requested frames. All restore
the previous custom colors, keep the applied counter unchanged and skip the
new overlay; resume reapplies it. The first test incorrectly assumed a lasting
flag; that failed assertion is retained.

No fade descriptors or solid-color custom-actor fade endpoints were observed
in this menu trace. Its zero endpoint count is explicit. It does not establish
software fade coverage merely because the scene changes.

## Native fade primitive

`art-palette-fade.c/.h` adds a caller-owned 212-byte RGB555 interpolation state
for one 16-color palette. It reproduces native half-duration error accumulators,
signed channel deltas, endpoint handling and native transparent-index behavior.
Duration zero becomes one. Durations above 255 are refused without writes:
native setup stores sixteen bits, but callback 1465E8 uses the low eight bits
of total duration. Native 256 is not a safe interpolation contract to copy.

The test invokes actual 08146E54 allocation/setup and 08148740/081465E8 updates
against the authenticated retained native palette pool. Native function bytes
match the authenticated clean ROM. The compiled sidecar is compared color by
color at every tick for black, white, from-black, from-white and mixed targets,
seven durations and both transparent-index modes: 70 cases, 7,284 checks.
It also verifies exact initial accumulators/deltas, retirement, bounds, stable
finished state, native-state isolation and unsupported-duration refusal.
Compiled code: 456 bytes, SHA256
`04e98c4c0b14fbd0bafcb7204397857b84076aa5795afc6e9819d24c30bd577a`.

This primitive is **not installed in the playable hook**. It does not yet
intercept native effect ownership/targets, allocate sidecars, handle native
blink/cycle flags or prove live fades. Do not substitute a color-ratio guess
for the native target operation. All ten palettes require an explicit storage
and effect-lifetime design; 212 bytes per palette is not implicitly reserved.

## Evidence

All runtime execution used `Test Expansion.ps1`, the declared native art plan
and the exact announced IDs. No broad integration run was used.

| ID | Runner | Checks | Component report |
| --- | --- | --- | --- |
| test-native-art-fade-contract | 20260918T031608.540137Z | 7284 | build/art/palette-fade/20260918T031609.113033Z/report.json |
| test-art-palette-plan | 20260918T032812.112346Z | 426 | build/art/palette-plan/20260918T032814.830864Z/report.json |
| test-live-art-palette-transitions | 20260918T032116.301838Z | 2710 | build/art/live-palette/transitions/20260918T032116.845155Z/report.json |
| test-live-art-palette-native | 20260918T032812.112346Z | 1122 | build/art/live-palette/native/20260918T032812.739817Z/report.json |
| test-live-art-palette-menu | 20260918T032226.503305Z | 99 | build/art/live-palette/menu/20260918T032229.170897Z/report.json |

The native pass recompiles and produces the exact 19c8d9e0 ROM, verifies all
patches/animation metadata/pixels and exercises native clears at every reserved
heap boundary. Menu pass proves exact generated colors and cancel/reopen.
The unchanged fade primitive's pass on 6c7ec331 is reused after the unrelated
planner/display changes; its native oracle bytes and compiled primitive are
unchanged. This is not a live fade pass on either ROM.

The transition and menu passes ran on49d39464. Final review added the mosaic
exception, producing19c8d9e0. Their entire32MiB ROMs differ only at offsets
01F90918 (80->88) and01F9091D (00->01): the two Thumb immediate operands
constructing mask0100 versus1100. All symbols and instruction locations match.
All1142 paired transition OAM frames and18 retained menu captures were checked:
none contains active8bpp mosaic. Thus their executed scan decisions and instruction
counts are unchanged; the passes are reused, with no claim of live mosaic
acceptance. The compiled planner separately proves conservative mosaic demand.

The observational body-to-current-buffer lookup resolves198 of205 active samples;
seven have no current-buffer match. Native buffers can advance after composition.
This helper is not an effect-ownership proof, and no fade endpoint acceptance is
claimed from these unmatched records. Future live fade binding must capture the
original palette identity at composition, before native buffer reuse.

After the transition runtime pass, its retained 205 active hardware palettes
were independently compared with the authenticated generated palette, all
exact. The same assertion was added for future transition runs without repeating
the already captured game playback. Retained report SHA256:
`57d6a725e467c98ac15cbc9b0b4b30ef1f8224a154e5e486182b1b2c6b2898c6`.
The report's 2710 runtime-check count is not retroactively inflated.

Failures retained:

- 20260918T030813.519784Z / transitions/20260918T030814.064212Z:
  wrong assumption that the native suspension flag remains set after a frame.
- 20260918T031347.269552Z / transitions/20260918T031347.836967Z:
  caff9140 native shadow mismatch at world-29; retained trace additionally
  demonstrates seven late active overlays. Later selected fade test did not run.
- 20260918T031638.441923Z / transitions/20260918T031638.966697Z:
  6c7ec331 still mismatches at world-29 after only the transparent-block change.

The intermediate 413-check planner pass in 031608 is retained but superseded by
426 with clipping/mosaic cases. The intermediate424 pass and native1122
rebuild on49d39464 are also retained. All failure directories and complete runner logs stay.

## Next work

Connect authenticated native fade target/ownership events to the sidecar and
prove actual live fades and color variants. Verify battle actor/weapon/effect
coexistence, heap capacity and worst-case timing. Then promote the fully accepted
technical stage through the existing reproducible package, retaining separate
saves. Final artwork and complete animation remain deferred and unaccepted.
