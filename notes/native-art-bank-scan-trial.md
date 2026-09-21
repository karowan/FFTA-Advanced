# Exact bank-scan experiments and engineering response gate

September18,2026. The user requires FULL engineering; only artwork and authored
frame content may remain placeholders. E01 is open. Neither experiment below
is accepted, installed, or a performance fix. Installed7507ca5c and all player
files remain unchanged. The optional builder flag defaults off and refuses
publication through its current index. Default palette compilation remains
byte-exact to installedfa3d12b4. No new art, game launch or remote publication.

## Measured implementations

Both trials preserve complete current-byte palette accounting, native clipping,
flips, affine/mosaic conservative footprints, transparent index0 versus visible
indices1..15, palette backup and all existing ownership checks. The planner
passes a rectangular range of visible whole source tiles to an ARM routine
temporarily copied below the existing IWRAM stack. Deep/non-IWRAM stacks use
the same ROM routine; no persistent memory reservation is added.

The first trial scans all visible pixels directly. Its connected ROM is
`8800cbf7ac36345c1ed647087e5eab38f77e4b5f`; palette8115d98e. It does not improve
response: cancel remains4–5frames slower than its exact-ROM compositor bypass.
Composition averages28.48–29.87scanlines. Component checks58589, build8, both
matched raw-input profiles292 each, mixed entry632 and frame observation5175
pass their declared scopes. The diagnostic pass is not timing acceptance.

The second trial, retained as the optional source experiment, keeps the existing
2124-byte tile cache and checks every cached tile byte before reuse. Changed
tiles are rescanned/copied, transparent words skip pixel work, and tiles beyond
the first32 use uncached exact scanning. The leaf is512bytes, saves40bytes,
and keeps512bytes below it for nested interrupt work; the wrapper's post-push
stack threshold is03007190. This conservative bound is not proof of every
possible interrupt lifetime. Connected ROM:
`0e1fb8164f785772903a9555fa9ced3c6fa75357`.

It reduces the isolated mixed-frame instruction count17928 to17216, but actual
composition still averages29.18–30.23scanlines. Both measured walks take53frames,
versus47/48 in its compositor-bypass controls. Cancel returns at33/32 versus29/29
frames. It is rejected regardless of its smaller instruction count.

The initial suggestion of mixed-object tile-cache thrashing was only a possible
mechanism. The retained ready frame actually contains one8bpp object (64x64,
horizontally clipped); that capture does not substantiate multi-object thrashing.
Do not promote that hypothesis into the root cause.

## Declared runs and preserved failures

All runs used Test Expansion.ps1 and scripts/native-art-test-plan.json, with
IDs/purposes announced. All enclosing runners are terminal. Paths below are
under build/art; runner timestamps are prefixed20260918T.

| Runner | Result / child evidence |
| --- | --- |
|225034.143679Z|Failed direct ARM test call in Thumb-only harness; palette-plan/20260918T225034.894540Z/failed.json. Corrected to compiler interworking veneer.|
|225125.404142Z|First scanner58589 passes; builder then fails locating connected metadata beside the generated-effect ROM. Complete log retained; no ROM defect implied.|
|225216.383990Z|Build8 passes; profile rejects old raw capture's different transientStateBytes before execution.|
|225339.941347Z|Corrected7507 control/candidate profiles292 each and first scanner entry632 pass.|
|225440.068299Z|First scanner frame observation5175 passes; native-frame-events/20260918T225440.730708Z/report.json records unchanged4–5frame cancel penalty.|
|225857.854538Z|Cached scanner61763, build8 and profile292 pass; entry fails paired native palette shadow at candidate/ready. Failed capture retained at live-palette/battle/20260918T225913.831039Z. Later frame test not run in that enclosing run.|
|230024.715421Z|Cached scanner frame observation5175 passes from that retained capture; native-frame-events/20260918T230025.438182Z/report.json records slower movement and3–4extra cancel frames.|
|230247.738575Z|Independent native phase6226 passes; response-budget fails nine measured metrics, with13 authentication/coverage checks passing.|

The phase proof is native-phase-evidence/20260918T230248.575800Z/report.json.
It reconciles the observed background phase against native rotation operations
and unchanged OBJ shadows; it does not silently pass the failed entry run or
execute the remaining skipped entry assertions. Full observed execution matches
ordinary execution across1024 states/framebuffers in each event run.

The explicit failure is response-budget/20260918T230249.273799Z/failed.json.
`test-art-response-budget.py` authenticates the complete trace, manifest, ROM,
both offsets and all128frames/action, then rejects any extra start/end/duration
frames relative to that candidate's exact-ROM compositor-bypass control. It
keeps each offset separate and does not realign frames or average away failures.
Passing this gate would remain bounded to its inputs, not every-game-scene proof.

## Reproduce and continue

`test-art-bank-scan-plan` compiles the optional scanner with its exact-byte
oracle, all256 pixel values in all word lanes, strides, zero spans, cache
boundaries, IWRAM/ROM fallbacks and the existing planner boundary matrix.
`test-art-bank-scan-build` privately builds baseline and experimental complete
chains, restores prior source manifests/indexes, and writes only the experimental
build/art/performance/bank-scan/current.json. `test-art-bank-scan-profile` uses
the corrected installed capture through --installed-mixed. Immutable trace IDs
pin both rejected candidates; do not repoint their historical IDs to a new ROM.
The cached candidate's current source differs from its build only by the later
publish_current prohibition; that Python guard changes no compiled ROM bytes.

Next investigate avoiding repeated whole-frame planning through authenticated
native input lifetimes, rather than another scan-loop micro-optimization. Static
clean-ROM inspection confirms VBlank calls08000D08 and080007C8 before the native
fresh/skipped-palette decision, and080012BC composes OAM unconditionally from
separate main/priority and UI/tail banks. Therefore the palette-DMA flag alone
does NOT prove OAM or VRAM inputs unchanged. Trace the actual OBJ upload and
buffer-publication paths before introducing dirty tracking or moving work.
Do not repeat the rejected full-key cache or skip overlays on repeated frames.
Keep palette restore, target/damage transformations and current-byte conflicts
correct. E02–E05 and full final acceptance remain open.
