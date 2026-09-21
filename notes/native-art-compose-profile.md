# Composition profile and rejected grouped-marker trial

September18,2026; follow-up `28d3266`. Current private ROM remains
`2908487c5de59274b03b71c59add5ab828bcba34`, stage161196/state8096, after rejecting
the trial below and reproducing the prior ROM byte-for-byte. No package,
launcher, player save or session changed. Built-in imagegen only; final sprite
refinement stays deferred. G01-G04 and battle timing remain open.

## Instruction locations

New declared `test-native-art-compose-profile` extends the existing isolation
test with bounded ARMv4T instruction-location counts. It uses authenticated raw
RAM/OAM/VRAM from the retained battle input, executes only palette composition,
and does not execute saved actor animation pointers. It checks one native color
phase, fresh/skipped DMA and stack residue0. Native DMA is modeled synchronously.
These counts identify work; they are not hardware cycles or frame improvements.

Current2908487c passes286 isolation checks in runner
`20260918T101935.850620Z`, report
`build/art/compose-isolation/20260918T101936.485926Z/report.json`.

| Instruction location | Fresh DMA count |
| --- | ---: |
| Scoped IWRAM pixel scan | 2518 |
| Ownership composition | 2361 |
| Preferred bank validation | 1869 |
| Unused-object tail scan | 1508 |
| Native ROM | 949 |
| Variant preparation | 905 |
| Palette/OAM application | 820 |
| Pixel-scan wrapper | 512 |
| 8bpp conflict traversal | 485 |

Repeated-DMA input has the same listed counts. Fresh-DMA generated latching
adds118 instructions elsewhere. Location counts exclude elapsed hardware wait
states and interrupt scheduling; do not treat percentages as CPU utilization.

## Rejected trial7cb635d5

The trial validated four exact native unused markers and four absent owner tags
at once, falling back to the existing scalar scan for other entries or unaligned
inputs. It ignored only native affine matrix words, as the original does. It did
not reuse native object counts or skip potentially conflicting objects; it is
distinct from the earlier discarded counted-tail and multirow pixel-scan trials.

Private SHA-1 `7cb635d555041513124cc28a0aa2b602d887b2ff`, stage161292/state8096.
Runner `20260918T102130.271651Z` passed:

- Profile286 at `build/art/compose-isolation/20260918T102131.008922Z/report.json`.
  Tail scan falls1508→630 instructions; palette outputs and isolation remain exact.
- Native/rebuild1153 at `build/art/live-palette/native/20260918T102131.180677Z/report.json`.
- Planner48009 at `build/art/palette-plan/20260918T102133.852072Z/report.json`.
  Added cases cover each late marker lane, changed geometry/banks, arbitrary
  affine words, invalid owner tags and unaligned owner arrays.

Actual timing runner `20260918T102203.804171Z` **FAILED** its final battle step.
Its two completed diagnostic steps remain bounded passing evidence:

- Exact-ROM ready capture:
  `build/art/live-palette/battle/20260918T102204.430957Z/observed.json`.
  Resolve the authoritative directory from the trial's `cost-fixture.json`.
- Cost30: `build/art/compose-cost/20260918T102223.215730Z/report.json`.
- Failed `test-live-art-palette-status-control`:
  `build/art/live-palette/battle/20260918T102226.602678Z/failed.json`.
  Its read-only `trace-audit.json` covers all1205 samples, including checks after
  the fail-fast ready-shadow assertion.

| Trial comparison | Move starts | Move ends | Moving frames | Cancel starts |
| --- | ---: | ---: | ---: | ---: |
| Exact-state active | 16 | 64 | 48 | 25 |
| Exact-state compositor bypass | 15 | 62 | 47 | 23 |
| Separate status-only native control | 15 | 62 | 47 | 22 |

The matched-state compositor delta remains1 frame before Move and1 during Move;
cancel delta is2 instead of current2908487c's3. The separate actual battle has
native-shadow/unowned-color phase differences in all1205 samples, one extra
movement frame, and1/3-frame Move/cancel response delays. Generated colors,
units, fences and native executable IWRAM remain exact; there are no allocation,
missing-overlay, new-unsupported or display-wrap violations. Maximum display
line202 does not establish smoother gameplay.

The trial is rejected: fewer instructions do not establish a satisfactory
timing improvement, and actual battle acceptance still fails. Different ready
arrival phases prevent attributing the absolute47→48 movement comparison solely
to the grouped scan. Do not claim a proven one-frame causal regression either.

Its source diff is retained privately at
`build/art/grouped-tail-trial/7cb635d555041513124cc28a0aa2b602d887b2ff/rejected-source.patch`,
SHA256 `9c9e6d165de6f954cb930b529cd886bf698fe6c6487faf3afb02e75b783b9e1d`.
The trial ROM, compile logs and complete reports remain private. The source
optimization was removed, and static rebuild restored2908487c exactly.

The expanded planner48009 passes on the restored implementation in runner
`20260918T102407.936293Z`, report
`build/art/palette-plan/20260918T102408.604313Z/report.json`.
Reuse unchanged2908487c's actual appearance/native/timing evidence from
`native-art-unseen-rotation-live.md`; no broad suite or repeated battle was run
merely to make a restored hash green.

## Next

Use the profiler and exact-ROM ready state to investigate scheduling and larger
composition costs. Do not repeat the grouped-marker trial from instruction
counts alone. Native palette phase versus different ready-arrival phase still
needs a causal scheduler analysis; keep the failed comparison explicit. Other
natural lifetimes, mixed-class capacity, cross-bank identities and complete
artwork/delivery gates remain open.
