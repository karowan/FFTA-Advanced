# Large-portrait technical import, September 17, 2026

Current private candidate: `75029dea8310b93cd5e462ee7517248c9452fa0a`, resolved
by `build/art/generated-portraits/current.json`, based on generated-class
candidate `595782ba32f4a20ff2053218f8722ab5e491112d`. Not packaged or installed.
It adds independent large portraits for all ten classes. Existing imagegen
upper-body crops are temporary transport inputs, not accepted portrait art.
The real Samurai menu now displays its generated face instead of Ninja.
Its crop/placement still needs the deferred art pass; no visual acceptance claim.

## Format and ownership

- Original pixel archive ROM `3e105c`: width4/count103, offsets relative to
  archive+4. Each stream begins with a big-endian decoded size. The importer
  preserves all original compressed streams and appends literal-encoded images.
- OAM archive `417f88`: width2/count103, the same relative-offset convention.
  Each layout is a count and six-byte attributes. Portrait objects are 8bpp;
  tile indices still use 32-byte units. They are not 4bpp actor objects.
- Palette archives `3d5a1c`, `3d965c`, `3dd360`: A7-compressed 165-entry
  containers, 96 bytes/48 BGR555 colors per entry. Actual menu palette uploads
  occupy hardware bytes `050002c0..05000320` (OBJ indices96..143).
  New opaque pixels use indices97..143; zero is transparent.
- Dedicated ROM reservation `1d80000..1e80000`, disjoint from the existing
  equipment grid and actor reservations, must be blank FF before import.
  Current appended archives consume326,925 bytes. No persistent RAM is added.
- Original103 pixel/OAM entries and495 palette variants are byte-preserved.
  New portrait IDs103..112 and palette IDs165..184 fit existing byte selectors.
  Only new-job record bytes13..15 and nine authenticated archive literals change
  outside the reservation. All prior actor/miniature/grid code and data remain.
- Pixel literals: cb828/cb864/cb88c/cb8d0; OAM: cb948/cb97c;
  palette modes0/1/2: cb924/cb910/cb900. Native helpers resolve the appended
  entries through their original code; no new portrait hook is needed.
- Temporary64x64 crops use one native square8bpp object, an allocation of4096
  bytes and47 opaque colors. Both class palette alternatives and all three
  custom color-mode entries intentionally match pending art/color tuning.

## Evidence and limits

Declared runner: `Test Expansion.ps1 -Plan scripts/native-art-test-plan.json`.
All runs preserve exact ROM identity, complete logs and fixed inputs.

| Test | Runner run | Checks | Scope |
| --- | --- | ---: | --- |
| test-native-portraits | 20260917T212559.273642Z | 4,020 | All103 original native pixel/OAM decodes, literal re-import, archive lookups, both stack alignments;495 original/re-encoded palette decodes and canaries |
| test-generated-portraits-native | 20260917T213304.630793Z | 1,796 | All113 current pixel/OAM records and555 palette entries; original preservation; ten real generic-unit lookups; actual Marche/Montblanc identity controls; exact rebuild and unchanged miniature encoding |
| test-generated-portraits-ui | 20260917T213051.629576Z | 355 | All ten large portraits in actual menus, exact VRAM/OAM/palettes, coexistence with idle actors and wheel figures, three idle advances, cancellation/reopen; Montblanc frame/VRAM/OAM/palette/owned-unit differential control |

The first generated-native run212911.916058Z passed2,620 checks but used
arbitrary IDs2..43 as purported named-character controls. That identity coverage
claim was incorrect. Retain its report; the corrected run above uses actual
Marche appearance2/ID80 and Montblanc appearance8/ID82, with same-race jobs.
The separate rendered Montblanc control was already authentic and passed.
No candidate change resulted from this test correction.

Original private extraction: `build/art/native-reference/portraits/manifest.json`
with103 pixel/OAM records and495 palettes. Current actual UI captures:
`build/art/generated-portraits/ui/20260917T213052.159909Z/`.
The source showcase save is authenticated and unchanged. Named identities retain
their original faces. No emulator window or player session was launched/changed.

This closes the bounded large-portrait transport proof, not full artwork or the
technical project. Full action/water and custom actor palettes, weapon/equipment,
effect/status imports and assembled delivery remain. G01-G04 stay open. The
earlier separately packaged preview and release remain untouched. No external
generation, council, publication or incident-note access occurred.
