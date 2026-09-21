# Expanded technical artwork preview - September17, 2026

Latest assembled ROM is **a6d883b5d7657f10c3eb6d9b8407c489d287dbc7**.
`build/art/assembled/current.json` describes the eight connected art stages.
`build/art/pipeline/delivery/current.json` now selects its separately playable
package through `Play Art Pipeline Preview.cmd`. The old preview package remains
intact. No game was launched and no player save/session was modified.

This delivers a reproducible expanded **technical preview**, not accepted final
sprites or blanket expansion completion. G01-G04 remain open for their final
art/review/full-scope requirements. The user's latest direction defers actual
sprite refinement; Gemini/fal remain discontinued.

## Scope decision

Keep actor/miniature conversion constrained to existing consumer palettes for
this technical delivery. Static inspection confirms CBA3C selects native mode
banks419d60/41b340/41a860. Native2292C and related paths bulk-load16 palettes;
the job palette nibble is not an independently allocated per-class palette.
Retained actual battle evidence shows palette sharing with weapons/effects/UI.
Changing source palette IDs alone would not prove safe allocation. Independent
actor palette expansion is deferred to sprite refinement, not silently called
implemented. Large portraits already use their independent48-color palettes.

All ten classes have independent actor resources, miniatures and large portraits.
All770 present non-idle land/water slots use repeated generated temporary poses
with native timings/commands. All17 axe items use the generated icon and held
resource276. Tomahawk projectile and primary impact, plus Exposed/Centered glyphs,
have distinct proved paths. This does not cover every other effect format or
action family, finished animation, natural water-map traversal or final art.

## Repaired map consumers

`test-repaired-map-consumers` passes253 checks in runner
`20260917T235839.189112Z`, report
`build/art/repaired-map-consumers/20260917T235839.713994Z/report.json`.
All139 repaired words match the clean original in the assembled candidate.
The15 affected maps execute the unmodified arrangement, clipping and height
loaders using mGBA's BIOS; outputs match authenticated retained native captures.
The existing boot probe uses only the reset vector and an explicitly empty
private ROM reservation. This is original loader execution, not actual mission
traversal. Other repaired-data consumer classification remains open.

## Assembled acceptance and retained failures

The ten-class assembled UI/rebuild milestone justifies the selected seven-check
acceptance batch. It is not the broad gameplay integration suite; applicable
battle/weapon/projectile/impact results were reused instead of replayed.

Runner `20260918T000052.285508Z` completed:

- `test-assembled-art-rebuild`: all eight art stages reconstruct the exact tested
  ROM from the authenticated corrected gameplay build; two final assertions
  plus the component builders' own checks.
- `test-assembled-portraits-ui`:355 checks, all ten actual portrait/idle/wheel
  combinations, advances, cancel/reopen and fixed-character differential control.
- `test-assembled-equipment-ui`:26 actual inventory/Buy/Sell checks.

That run then **failed** before native preview execution: it expected the
retained IWRAM fixture beside the clean rebuilt ROM. The fixture is actually
beside the authenticated historical source. The selector now carries separate
fixture provenance; its report, frozen ROM and source identity are verified.
No ROM change was needed. The passed steps above were retained, not repeated.
The equipment harness was also corrected to honor the assembled ROM path instead
of silently selecting its earlier equipment component when given a manifest.

Runner `20260918T000505.459103Z` completed3,567 native preview checks,8 Item List,
21 Buy and21 Sell checks. Packaging in that same run **failed closed**, because
the enclosing runner had not finalized its input-integrity result. No package
was written by that attempt. Run packaging separately after evidence finalizes.

Runner `20260918T000546.154586Z` packages successfully, using ten completed
exact-candidate reports and three applicable parent reports. The evidence ledger
explicitly records failed enclosing runs and their other failed steps. Reused
held-weapon/projectile reports require the exact parent ROM; a whole-ROM byte
comparison permits only the independently tested425 impact hook/payload delta.
The exact-candidate effect results remain3,707 native and42 actual battle checks
from `20260917T234709.326823Z`; no repeat was needed.

The5,359,163-byte BPS applies byte-exactly to the pinned clean USA ROM. Two patch
constructions match and a wrong source is rejected. The package holds the ROM,
patch, candidate manifest, hashed evidence ledger and `ART-PIPELINE.md`.

Runner `20260918T000612.154004Z` passes three launcher checks: actual validation
and all three save/state/screenshot overrides; changed-ROM rejection before
launch; existing player ROM/save files unchanged. The independent save directory
is `saves/art-pipeline/a6d883b5d7657f10c3eb6d9b8407c489d287dbc7/`.

Root inspected the current Viking wheel/portrait and Bronze Helm new-job page.
Assets coexist and labels render; native-size conversions still visibly lose
detail. These observations are transport review, not aesthetic acceptance.

## Next

The separately playable technical preview is now available. Remaining work must
retain the distinctions in its guide: final imagegen sprite design/animation,
expanded color allocation if needed for that art, uncovered action/effect and
natural-water consumers, remaining repaired-data classification/traversal, and
full-scope final acceptance. Do not restart passed implementation or call the
entire checklist complete because a preview was packaged.
