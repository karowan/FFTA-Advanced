# Samurai native cadence and direct palette transport — September 17, 2026

The previous checkpoint `edad18f` made useful native-scale art progress, but its
fixed-feet/breathing assumption was incorrect. Authenticated original resource4
idle slots0/1 each use three distinct poses in A/B/C/B order, with durations
16/8/16/8. The original moves its feet and arms. Foot movement by itself is not a
rejection criterion. Costume, anatomy, facing and silhouette continuity still
matter. Preserve the earlier measurements as observations, not proof of failure.

## Generated inputs and conversion

Only built-in imagegen was used. `src/art/imagegen/samurai-march-study.json`
records both exact prompts, source paths/hashes, references and review decisions.
The second six-frame sheet has SHA256
`47fd3199ab259a67c8291ae15e3ae757a64b7de5cd361c17e2cc11ab451edb8d`.
Both generated sheets remain unaccepted drafts. The second improves back-neutral
facing but still has weak stride reversal and loses eye detail at native scale.
No additional art generation is needed to establish the transport proof below.

`convert-generated-sprites.py --native-palette-offset 0x419d80` now maps sampled
source colors directly to the actual actor palette. This avoids an intermediate
generated palette losing rare colors before native remapping. Existing default
conversion remains byte-identical. This mode is consumer-specific: do not reuse
an actor-optimized conversion as proof of the differently paletted miniature.

Declared `test-direct-native-conversion` passed 51 checks in runner
`20260918T002943.027548Z`, report
`build/art/direct-native-conversion/20260918T002943.582501Z/report.json`.
It checks authentic inputs, default byte preservation, per-pixel closest native
color, alpha/padding, 4bpp roundtrip and importer identity. Aggregate squared RGB
error dropped 19.09% for the old v5 sheet and 25.28% for march-v1. This numeric
improvement does not establish aesthetic quality or production acceptance.

## Bounded native integration

`samurai_idle_transport.py` reproduces PNG conversion and imports six poses into
only Samurai land idle slots0/1 of the assembled technical preview. It preserves
the native four-entry cadence, every command/metadata byte, native palette and
foot baseline. Reservation `0x1f8c000..0x1f90000` is checked empty before writing.
The only other changed bytes are resource256's four-byte table entry. All other
actor, miniature, portrait, action, water, equipment, status and effect data stay
exactly as in the parent.

Private candidate: `352df0a698a4a946428807683475260c42b7d464`, resolved through
`build/art/samurai-idle/current.json`. This is an uninstalled technical draft.
The playable package/launcher still resolves `a6d883b5d7657f10c3eb6d9b8407c489d287dbc7`.
Neither production catalog nor player files were changed; no game was launched.

Run through the declared plan:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/native-art-test-plan.json -Only test-samurai-idle-transport
```

Final runner `20260918T004043.995426Z` passed 613 checks; report:
`build/art/samurai-idle/tests/20260918T004044.555541Z/report.json`.
This includes exact rebuild from generated PNG, whole-ROM bounds, native getters
for both idle sequences/all four facings, original timing and metadata, and actual
64-frame menu playback with all three front poses observed. Cancel/reopen passes.
Paired parent/candidate captures preserve roster, palette, hardware OAM and all
VRAM outside the actor's 512 displayed bytes at every sample.

The first runner `20260918T003843.355378Z` FAILED because the test wrongly required
the actual menu allocation to equal16 tiles. A retained accepted parent capture
(`generated-portraits/ui/20260918T000107.444744Z/generated-116-wheel0`) independently
shows20 allocated versus16 drawn. The corrected test requires that exact menu
contract. It passed613 in `20260918T003938.372854Z`; the final rerun was justified
by adding PNG conversion to the builder, and produced the same ROM hash. All
failures and earlier passes remain retained. Runner summary ROM headers refer
to its global probe; the per-test report above identifies the tested art ROM.

## Limits and next work

Both sequence pointers were executed through native getter code, but only the
front sequence was observed in the actual menu playback. This does not add new
battle, back-facing, water, action or final-art acceptance. Reuse unchanged parent
consumer evidence only within its original scope. The packaged preview and its
guide retain their existing coverage and limitations; this draft is not silently
substituted into that delivery.

Technical PNG-to-native three-pose transport now works. Keep remaining technical
consumer/full-scope gaps explicit before expanding final art production. All G
gates remain open; neither this proof nor the existing technical package means
every checklist item is complete. No Gemini/fal, councils, publishing or player
session changes were used.
