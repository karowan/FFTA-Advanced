# Connected technical-preview delivery — September 18, 2026

The user directs built-in imagegen only, technical E2E first and sprite
refinement afterward. Current ROM is `4a7d55ce09cd4a40965a0bb97de2701d276789c5`.
This follow-up assembles delivery evidence; G01–G04 remain open under their full
final-art scopes. No new artwork, external provider, agent, publication or game
launch is involved.

## Current-candidate consumer acceptance

Runner `20260918T202224.211166Z` passes seven bounded consumer checks. This is
the final connected graphics/menu delivery milestone after the palette, memory
ownership, Status and keyboard work, not a broad gameplay or campaign replay.
Applicable component/campaign evidence is reused instead of rerunning it.

| Test ID | Checks | Child report under build/art |
| --- | ---: | --- |
| test-connected-art-portraits-reconciled | 587 | generated-portraits/ui/20260918T202224.846573Z/report.json |
| test-connected-art-preview-party | 8 | equipment-preview/ui/20260918T202233.661878Z/report.json |
| test-connected-art-preview-buy | 21 | equipment-preview/ui/20260918T202236.768623Z/report.json |
| test-connected-art-preview-sell | 21 | equipment-preview/ui/20260918T202242.962052Z/report.json |
| test-connected-art-status-current | 206 | generated-status/tests/20260918T202249.756136Z/report.json |
| test-connected-art-held-weapon | 90,348 | generated-actions/battle/20260918T202252.510064Z/report.json |
| test-connected-art-projectile-impact | 4,069 | generated-projectile/20260918T202338.177874Z/report.json |

The first runner `20260918T201942.811467Z` failed at the old fixed-character
whole-frame comparison after all ten generic-class checks completed (324 checks
total). Its baseline was the much earlier pre-palette parent. Raw VRAM, palettes
and player records matched, but OAM/cursor animation phase differed. This is
retained in `generated-portraits/ui/20260918T201943.434265Z/failed.json`.

The corrected fixed-character control starts from the exact current ROM and
restores only the nine original portrait archive literals. All other renderer
and menu behavior is identical. Both native fixed-character branches now match
full frame, VRAM, palette, OAM and owned player data at every checkpoint.
The ten completed generic cases are authenticated from the failed report
(SHA256 `44137dcc091ddc17fa48ed4da318f8d8eebac629cf017c20bfb3e70c98d71ae8`),
including actual VRAM/palette/OAM/player records and each completed upload
assertion. They were not replayed merely to change the later control.

Reused current-ROM evidence includes native composition/rebuild (3,981),
equipment icon UI (30), actual Status/help/return (38), and the direct native
phase reconciliation (6,225). Earlier water and other native-effect component
checks retain their own scopes. Neither a phase reconciliation nor the 8 KiB
Status component pressure case establishes every effect or maximum encounter.

## Build and package gates

`test-connected-art-rebuild` authenticates the corrected gameplay source-build
result, then rebuilds class resources, class/menu artwork, portraits, explicit
action transport, current palette/menu hooks, status, equipment, weapon and
impact. It must reproduce the entire tested ROM. Historical subordinate indexes
are preserved; final provenance is refreshed only after byte equality.

Schema 3 packaging now has an explicit current-candidate evidence list. It
cannot fall through to the obsolete single-Samurai acceptance list. It rejects
diagnostic instrumentation, verifies source hashes and records each test's
scope, report/log hash and enclosing run failures. It produces an immutable
ROM/BPS/manifest/guide folder and advances only the preview delivery index.
Patch roundtrip, deterministic generation and wrong-source rejection are
required. `test-art-pipeline-launcher` validates save/state/screenshot isolation
and changed-ROM rejection without launching or creating a player save.

## Delivered result and retained packaging refusal

Source checkpoint `a81cd1e` precedes the full art rebuild. Runner
`20260918T202829.646963Z` passes `test-connected-art-rebuild`: all source art
stages and current palette/menu hooks reproduce the entire current ROM. Child:
`build/art/connected/full-rebuild/20260918T202830.390580Z/report.json`.
The unchanged corrected gameplay eight-stage rebuild is authenticated and reused.

That enclosing runner remains **failed**: packaging deliberately refused to use
its rebuild child while the enclosing runner was still running. It had no other
eligible completed rebuild report under the new ID. No package was written by
that attempt. The workflow now explicitly uses a separate packaging invocation
after the rebuild runner reaches terminal status; the gate was not weakened.

Runner `20260918T202938.440786Z` then passes `package-connected-art` and
`test-art-pipeline-launcher`. It reuses the completed source rebuild from the
failed prior runner and records that runner's package refusal in the manifest.
Launcher report: `build/art/pipeline/launcher/20260918T202941.306887Z/report.json`.
All runners are terminal.

Private immutable delivery folder:
`build/art/pipeline/delivery/4a7d55ce09cd4a40965a0bb97de2701d276789c5/`.

- ROM SHA256: `05f3107ffb4826e8e2d9e0a62040574f65c2556626c05a6ac9be3c1acfc6f2b1`.
- BPS SHA256: `ae07d975c30f2ea48fcd3e922b7d51f9dc3aa156e7566768afbba496b76ae607`.
- Patch size: 5,583,836 bytes. Deterministic creation, exact application to clean
  USA SHA1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`, and wrong-source rejection pass.
- Manifest has 12 exact-current-ROM evidence entries with report/log hashes and
  explicit scope. Guide hash equals the delivered guide and workspace source.
- Save/state/screenshot path: `saves/art-pipeline/4a7d55ce09cd4a40965a0bb97de2701d276789c5/`.
  No save is imported or created by packaging/validation. Existing protected
  ROMs and player save files compare unchanged. No visible game is launched.

Root reviewed the source control restoration, whole-ROM rebuild equality,
schema3 gate, evidence lineage, immutable output and launcher isolation. Root
visually inspected the current new-jobs page, Samurai portrait/wheel and native
mixed Tomahawk impact. Labels and separate consumers render; the small crops,
body details and repeated poses remain temporary, not accepted final artwork.

`Play Art Pipeline Preview.cmd` now resolves this package. Older preview folders,
vanilla/v0.7 and any already-running game remain separate. This delivers a
connected technical preview, not maximum encounter/effect demand or every natural
caster/action family. Those remaining technical acceptance checks and final
artwork/animation keep the full G gates open; the guide states these limits.
