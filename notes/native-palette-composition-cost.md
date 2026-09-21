# Palette composition cost from identical states — September 18, 2026

Previous checkpoint `792e08f`. This is diagnostic progress; battle acceptance
and G01–G04 remain open. Current private candidate remains
`21052ed615a6463251cba9b98952b4cc07ba4546` through
`build/art/live-palette/poc.json`. Stage155804 and state8096 are unchanged.
The counted-tail trial below was discarded and the current ROM reproduced
byte-for-byte. No player, launcher, packaged ROM or running-session change.
Built-in imagegen only; final sprite refinement remains deferred.

## Paired experiment

`test-live-art-palette-compose-cost`, runner `20260918T072940.916163Z`, passes
2424 checks. Report:
`build/art/compose-cost/20260918T072941.477572Z/report.json`.

For each of two retained candidates, the test loads the same authenticated
ready state into the active ROM and a private diagnostic copy. The latter
restores only the eight original bytes at native compositor entry `080012BC`;
all other hooks, resources and state remain identical. Loaded EWRAM/IWRAM must
match the original captures exactly. The active run must reproduce every one
of the1200 retained Move/cancel position observations. Both copies must reach
the original final positions and canonical unit state. The test creates no
gameplay fixture and does not replay deployment.

| Candidate/case | Move begins | Move ends | Moving frames | Cancel begins |
| --- | ---: | ---: | ---: | ---: |
| Current21052 active | 51 | 177 | 126 | 61 |
| Current21052 compositor bypass | 44 | 166 | 122 | 59 |
| Trialcd390 active | 53 | 183 | 130 | 61 |
| Trialcd390 compositor bypass | 52 | 175 | 123 | 57 |

These are sample offsets after the same eight-frame press. The current
composition hook adds four moving frames and seven frames before movement in
this matched-state experiment. The trial adds seven moving frames. Bypassing
only composition does not remove renderer-hook or other extension costs, and
its missing custom colors are intentional diagnostic output, never a deliverable.
This is not parent/candidate or final-art acceptance.

Native skipped-DMA observations during the600 Move samples are397 active versus
382 bypass for21052, and398 versus383 forcd390. Actual position changes remain
two or three video frames apart. The complete per-frame positions, native
`03000E10` state, cycle-list head, BG cycle colors and palette profile samples
are retained. Different arrival phases and changed execution costs both matter;
a smaller maximum VBlank line alone does not prove smoother gameplay.

## Rejected counted-tail trial

Private trial `cd390d3560ecd9e87279672a6f18b932d306ee01` passed its object count
from the authenticated native compositor to palette validation, avoiding a
backward scan over unused native OAM markers. It still validated all emitted
objects/pixels; full-planner fallback preserved the complete128-entry demand.
No new RAM reservation was needed.

Component runner `20260918T072501.538165Z` passed ownership720 and planner47980.
The count was compared with actual native DMA destinations/lengths, including
clipped priority/UI/main/tail groups and both buffers. Only exact native unused
markers were omitted. Invalid counters preserved all outputs. Counted versus
existing application compared complete OAM, palette, plan and backup bytes,
including late conflicting objects and full-planner fallback.

Runner `20260918T072545.711798Z` passed native1134 and transitions2933 but
**FAILED battle acceptance**. Retained report:
`build/art/live-palette/battle/20260918T072556.059316Z/failed.json`.
Its derived `trace-audit.json` covers all1205 paired samples: exact generated
colors, no ownership/allocation failures, zero unsupported events, preserved
units/fences, no scan/display wrap, maxdisplay202. Movement was130 versus123
parent frames; Move began53 versus51, cancel61 versus49. Native color-phase
differences persisted. This is worse movement than the current21052's126.

The trial source and added trial-only tests were removed. Their exact patch is
retained privately at
`build/art/compose-count-trial/cd390d3560ecd9e87279672a6f18b932d306ee01/rejected-source.patch`
(SHA256 `7951d3d5e8f404523ab24b363d0804d35ba1012fe6f21dc761f54906f624fe28`).
It applies cleanly to checkpoint792e08f (`git apply --check` verified); keep it
with the trial ROM, source hashes, compiled logs and reports. Do not reinstall
it merely because its component tests passed or display work ended earlier.

The builder now includes `art-palette-variants.h` in its source-provenance map
and describes runtime evidence separately from build identity. These metadata
changes do not alter the ROM. Rebuilding after the trial's removal reproduced
21052 exactly; reuse its existing native/fade/transition/deployment/battle
evidence and planner47961. No broad regression or campaign replay was justified.

## Next

Use matched-state composition cost as a diagnostic alongside actual battle
acceptance, not a replacement for it. Investigate native foreground/VBlank
handoff and repeated-frame work before another speculative optimization.
Static native entry points: foreground `080003F0` clears03000E10 then calls
`08003F10`/`08000460`; draw scheduler0460 reaches `080069F4` with mode3.
VBlank04B0 tests03000E10 at04C8, composes at04D8 and sets it to1 at051C.
These are disassembly leads, not a measured causal explanation or permission
to change native cadence. Preserve independent input/motion and palette-phase
requirements. Remaining color modes/reloads/late entry, scene/heap/stack and
other native consumer coverage, final art and reproducible delivery remain open.
