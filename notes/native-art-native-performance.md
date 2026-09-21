# E01: reproduced rendering regression resolved

Root accepts E01 on private candidate
`a28b624bb13c8f2f2597a4d4bd3999b17c234b99`. Only this performance gate is closed;
E02-E05 remain open. The installed game and player saves are unchanged.

## Cause and engineering fix

The extra latency was not an unavoidable property of the game or the new class
artwork. The custom palette layer intercepted native rendering, tracked emitted
class objects, scanned competing native palettes and reassigned hardware banks
during frame composition. Its extra work changed foreground/update/input timing.
Earlier optimized versions reduced measured work but still failed response or
deployment cadence. Their raw failed evidence remains applicable to those builds.

The new stage converts generated body pixels to original shared palette indices
at build time and restores29 authenticated native palette/render/fade entry
patches. There is no runtime custom palette ownership or color translation on
this path. Original side selectors, native effects and OAM composition handle
the new pixel data. All20 land/water resources, action graphs and ten class
identities remain, with final art quality explicitly deferred. See
`native-art-shared-palettes.md` for the implementation and native color contract.

This addresses both the exclusive-bank capacity shortage and the costly palette
layer rather than waiving its overhead. Separate heap/menu fixes remain active.

## Independent control and fresh allocations

The control is authenticated original-renderer build
`0fa7d1707e2d85fb2a8602f061b5eb4479ff3211` plus only the previously verified32-byte
Status iterator shortcut and its native pointer. That shortcut removes unrelated
menu cost from the comparison. The private control patch is strictly bounded.
The control is not formed by bypassing an already-native compositor.

Both builds start from the same authenticated accepted-world fixture and apply
the same four existing same-race class profiles117/118/120/124 before deployment.
Both preserve the fixed story profiles. Every build allocates its own original
twelve-unit Giza battle. The existing scripted dialogue observation and route
are retained. Original native palette/render/fade entry bytes agree in both ROMs.

The paired entry compares all26 route boundaries, preplacement/ready states,
and20 idle samples: frame counts, native update counters, canonical unit bytes,
complete native palette shadow and hardware palettes agree. After comparing the
entry route, the established Giza coordinate input is applied to both builds.
This fixes the declared timing scenario, not an action outcome. Fresh per-ROM
ready states prevent using obsolete absolute animation pointers.

## Measured response

All frame values are relative to the start of the declared action window.

| Input offset | Action | Candidate start / end / duration | Original-renderer control | Added frames |
| --- | --- | --- | --- | --- |
| 0 | Move | 24 / 71 / 47 | 24 / 71 / 47 | 0 / 0 / 0 |
| 4 | Move | 23 / 70 / 47 | 23 / 70 / 47 | 0 / 0 / 0 |
| 0 | Cancel | 29 / 29 / 0 | 29 / 29 / 0 | 0 / 0 / 0 |
| 4 | Cancel | 28 / 28 / 0 | 28 / 28 / 0 | 0 / 0 / 0 |

The full ordered movement is identical, not just its endpoint. Both128-frame
windows retain exact raw input, native update and foreground cadence with no
mismatches or timeline shifts. Complete shadow/hardware colors match at actual
composition boundaries. Every observed native state/framebuffer matches fresh
ordinary execution of that same ROM:1024 action frames total. Original DMA
fresh/skipped decisions and actual display return remain inside VBlank.

Native composition means3385-3427 cycles (about2.75-2.78 scanlines) in these
action windows. Candidate and control peaks are3486 cycles or lower. Tiny
inclusive cycle differences do not add a response/update frame. These are raw
inclusive measurements, not claimed universal worst-case timings.

## Deployment regression

The previous608-frame interval is replayed from each build's own entry-6 state,
with the same eight-frame confirm input and600 subsequent no-input frames.
Both builds have591 native deployment color callbacks and99 actual shifts at
exactly the same relative frames. Every one of608 complete palette shadows,
hardware palettes and canonical-unit snapshots agrees. Input, foreground return
and draw cadence is identical without phase alignment.

The observed state/framebuffer equals fresh ordinary execution for both branches:
1216 deployment frames. Full native palette preservation, original DMA behavior
and VBlank completion pass at every composition boundary. Both branches have
mean3444.5378 and maximum3470 native composition cycles in this interval.

## Evidence and review

`native-art-native-performance-evidence.json` pins all reports, enclosing runner
reports and both per-ROM ready/deployment state/RAM/IWRAM captures.
The immutable connected manifest is also pinned and byte-identical to the
native-palette selector recorded by the tests, preserving that input identity
if a later candidate replaces the selector.

| Declared test | Checks | Terminal runner | Child report under build/art |
| --- | ---: | --- | --- |
| test-art-native-palette-entry | 66 | 20260919T070814.886679Z | native-palette-entry/20260919T070815.647048Z/report.json |
| test-art-native-palette-response | 6191 | 20260919T071142.675194Z | native-palette-response/20260919T071143.467631Z/report.json |
| test-art-native-palette-deployment | 7891 | 20260919T071431.436280Z | native-palette-deployment/20260919T071432.102714Z/report.json |

All three pass on their first runtime run. No broader suite or repeated art build
was needed. Root reviewed the independent control construction, matching profile
and input routes, raw motion/cadence comparisons, complete palette snapshots,
observer equivalence, original hook restoration and retained source hashes.

These checks close the specific measured Move/cancel and deployment regression.
They do not assert that every possible original-game scene has constant frame
rate, nor accept remaining action/effect/participation graphics, demanding
encounter lifetimes, campaign/save compatibility or final reproducible delivery.
Those remain E02-E05. Final artwork and poses remain a later art pass.
