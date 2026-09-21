# Native status iterator cost — September 18, 2026

Follow-up to checkpoint `30e03b7`. Current private candidate is
`29453def10826d971c689b6169a316b182c2fda1`, resolved through
`build/art/live-palette/poc.json`. Stage155836 bytes, transient state8096 bytes
within the existing8KiB reservation. No package, launcher, player save or running
session changed. Built-in imagegen only; final sprite refinement stays deferred.
All G gates and complete battle acceptance remain open.

## Identified bottleneck and implementation

Declared `test-live-art-palette-cpu-profile`, runner
`20260918T073939.686794Z`, passed1212 checks on existing21052 evidence. Report:
`build/art/compose-cost/20260918T073940.291685Z/report.json`.
It reproduces all1200 retained position observations while sampling serialized
CPU registers. Repeated PCs resolve to storage-format validation, owned-state
readers and native arithmetic inside status selection. This sampling is at
video-frame boundaries, not a CPU-cycle percentage or call-count profile.

The native status iterator called the complete custom-status limit search on
every cursor advance, including ordinary keys1..24. Every possible limit is at
least24. Consequently `(int8_t)(uint8_t)(previous+1)<=24` always returns that
next byte without any status lookup. This also preserves native signed wrap
through128..255 and255-to0. No getter expiry or mutation is being skipped: the
queried getters are read-only. Custom keys25..55 still use the original path.

`src/engine/integrated-jobs.c` now implements that early return for subsequent
full builds. `src/engine/status-iterator-fast.s` backports the same condition to
the authenticated existing private parent without rebuilding unrelated layers.
It changes the native9DD58 entry pointer, advances the cursor and restores the
already-pushedr3 on the fast path; otherwise it delegates to intact091E631C.
The builder authenticates the entire existing9DD52..9DD62 entry. The32-byte leaf
uses no new persistent RAM, job IDs or save fields. Keep the C source change in
future assembled builds; the private backport is not a new save schema.

## Verification and retained failure

`test-status-iterator-fast` passes104472 checks with production `-Os -std=c11`
settings in runner `20260918T075635.750355Z`; report:
`build/art/status-iterator/20260918T075636.422351Z/report.json`.
It compares the compiled C shortcut with the existing original function for all
256 cursor bytes and every highest status key24..55 under controlled read-only
getter contracts. It executes both actual inline entries at both stack residues,
compares live registers/stack/cursor, proves zero getter calls on fast advances,
and checks real native getters on retained canonical units with combinations of
Exposed, Centered, Wound, KO and petrification. The real-getter stage checks all
cursor bytes and unchanged EWRAM. This is not every custom-status lifetime or a
replacement for existing class-specific tests.

The first run `20260918T074851.479843Z` failed by comparing dead CPU carry flags
too early. The exact native continuation at9DD62 is MOVS/LDRSB/CMP; CMP replaces
all condition flags before their first consumer at9DD68. The corrected test
authenticates those bytes and compares there. No production fix or relaxed live
register check was needed. The earlier `-O2` component run also passed104472;
the rerun intentionally verified the production optimization settings. The full
updated `integrated-jobs.c` compiles independently with its production flags and
warnings-as-errors. A complete production ROM rebuild remains future integration.

Runner `20260918T075018.456431Z`: `test-live-art-palette-native` passes1135,
including byte-exact current private rebuild and all authenticated patches.
The same runner's `test-live-art-palette-battle-short-input` **FAILS** strict
native-shadow equality. Report:
`build/art/live-palette/battle/20260918T075021.733381Z/failed.json`
(SHA256 `35b26fea1f86929b3d0a98ac34d28badf4be82631aa165ac30b97664a201bc76`).
Its complete offline audit covers1205 paired samples: all generated hardware
colors exact, no lost overlay, allocation failure, unsupported event, fence
change or display wrap; maximum display line205. Movement now takes47 frames,
versus126 on21052 and123 on the old parent. Move starts17 versus51; cancel26
versus49. Remaining shadow/hardware differences are native BG162..175 cycles.
The old parent still has the expensive status iterator, so this comparison alone
does not isolate artwork overhead.

## Fair engine control and remaining overhead

`test-live-art-palette-status-control`, runner `20260918T075259.970249Z`, creates
a private control from0fa7 with only the exact same32-byte leaf and entry pointer.
All other bytes match the original parent; it gains no palette hooks, generated
colors or RAM reservation. Control SHA1:
`82a8624e788d081e8394c3babb821f8e1cd853dc`.
This comparison also **FAILS**; report:
`build/art/live-palette/battle/20260918T075300.631359Z/failed.json`
(SHA256 `ea1f16e733993dbe5d41e021f8642cc4b64d817086fba79ffc4695e84d181001`).

| Case | Move starts | Move ends | Moving frames | Cancel starts |
| --- | ---: | ---: | ---: | ---: |
| Status-only control | 15 | 62 | 47 | 22 |
| Current artwork candidate | 17 | 64 | 47 | 26 |

The1205-sample audit has exact generated colors, preserved units/fences, no
allocation/refusal/wrap and maxdisplay205. It retains native palette-phase
differences and two/four frames of action-response delay. Equal movement duration
does not close input-response or palette-phase acceptance.

`test-live-art-palette-fast-status-cost`, runner `20260918T075517.005446Z`, passes
1212 diagnostic checks. Report:
`build/art/compose-cost/20260918T075517.645639Z/report.json`.
It reuses the exact29453 ready state and compares active code with a private copy
restoring only the original compositor entry, as in the prior cost procedure.
Every active position observation is reproduced; both final gameplay states
match. No deployment replay or new game fixture is needed.

| Matched-state case | Move starts | Move ends | Moving frames | Cancel starts |
| --- | ---: | ---: | ---: | ---: |
| Active | 17 | 64 | 47 | 26 |
| Compositor bypass | 16 | 63 | 47 | 23 |

Palette composition adds zero moving frames but one/three response frames in
this exact-state experiment. Frame-boundary CPU samples now land at native wait
PC0800042A1092/1200 times active versus1136 bypass (old21052 active403). These are
sample locations only, not CPU utilization. The bypass intentionally lacks
custom colors and is never an acceptable deliverable.

CPU serialization layout was checked against official mGBA
[serialization headers](https://raw.githubusercontent.com/mgba-emu/mgba/master/include/mgba/internal/gba/serialize.h)
and [implementation](https://raw.githubusercontent.com/mgba-emu/mgba/master/src/gba/serialize.c).
The local libretro core saves format11 (0100000B); the test authenticates that
magic, reads GPRs at20/CPSR60 and never reloads its sample. The desktop0.10.5
format must not be substituted. Preserve the emulator provenance in runner logs.

## Next

Keep this measured improvement; do not restore rejected counted-tail or multirow
scan trials. Reuse applicable palette/planner/fade/variant evidence. Investigate
the remaining compositor response cost using the current matched-state report,
and separate unchanged native cycle behavior from arrival/scheduler phase with
an authenticated native execution oracle. Do not silently normalize phase or
mark the failed battle comparisons passed. Remaining color operations/reloads/
late entry, scene/heap/stack and other consumer coverage, final artwork and
reproducible playable delivery remain open. No broad regression is justified by
this bounded shortcut alone.
