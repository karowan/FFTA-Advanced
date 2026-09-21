# Native artwork integration

Investigation opened September 17, 2026. This is not completed artwork acceptance.

## Actor relocation and generated idle proof, September17

Private unchanged relocation7d9355d71c27a7adb96d0e410f84b6c3dda265cb now has
3767 native checks,38 roster/wheel comparisons and105 actual land-deployment/
idle checks. Source: scripts/native_actor_import.py. Samurai owns new resources
256/257 in ROM0x1d10000..0x1d80000; originals are preserved. The job wheel is
actually a separate compressed miniature-image consumer, not actor OAM/sequence
playback. Its table0x393f0c also needs extension when actor resource IDs change.
This corrects the earlier mistaken consumer description below.

Built-in imagegen produced samurai-idle-v3.png and samurai-idle-v4.png under
build/art/imagegen/samurai/. v3 crossed equal-cell boundaries; the first
median-cut conversion lost facial highlights. v4 fixes the sheet margins and
wider face. Native-v4-coverage is a technical15-color32x32 conversion, still a
draft, not aesthetic acceptance. Prompts are in src/art/imagegen/.

scripts/build-generated-actor-poc.py imports four converted frames into only
land idle slots0/1, preserving timings/commands/metadata, using one32x32 OAM
object and the unchanged native16-tile allocation. It maps colors into an
existing native palette without changing palette bytes. This does not prove
custom palette allocation. Private a914169fe4d715192028ebebcfbfc6437b8b458b
visibly renders a new red-armored Samurai in battle; both complete idle frame
blocks appear in VRAM. Its original strict single-block isolation check FAILED;
retained captures subsequently prove different valid native animation phases
for neighboring actors and map water, with unchanged allocation bounds. The new
independent12-actor/frame oracle passes2212 checks and rejects four deliberate
corruptions. Actual generated battle on a914169f passed2261 checks in183850.
Correcting the conversion reference from dim0x41a880 to normal0x419d80 creates
06cc1297497c89ec8e70ad446dd56a6816efd6cd; all2303 battle checks pass in
20260917T185223.404796Z, including actual OAM/OBJ palette validation at every
capture. Original UI reference exports also now use source bank=destination-13;
44 native exports pass. These close bounded technical defects, not production
artwork, all directions/actions/water or other native consumer acceptance.
See the latest checkpoint for exact runs, failures and next steps. No installed
ROM, player save or running session changed. G01-G04 remain open.

## Artwork method correction: imagegen required

The latest user instruction is to use imagegen, not assistant-drawn sprites.
It supersedes the earlier desktop-drawing preference and all source-row drawing
procedures below. Preserve those drafts as technical history only. Future artwork
and visual corrections use the built-in imagegen tool; code handles conversion,
native integration and tests without inventing character artwork.

First generated asset: `build/art/imagegen/samurai/samurai-model-v2.png`, with
full prompts/review in `src/art/imagegen/samurai-prompts.json`. v1's repeated front
directions were corrected through imagegen. The selected1536x1024 RGBA model
sheet has transparent alpha and an original red-armored Samurai design. It still
needs native pixel-density/palette adaptation and proven actor/animation import.
This is a design draft, not an installed sprite sheet or expansion completion.

## Current private preview and portrait drafts

`build/art/equipment-preview/current.json` resolves private candidate
`7bfdecde1130d8b3f9a9d3d6dccbe8fe1962b610`. It adds two-page eligibility grids
for Item List, Buy and Sell, and original menu portraits for jobs116-125.
The installed release/showcase remains `1b070824a8dad4995434eee3ab40fa08187a6120`.
No player ROM/save was overwritten and no game was launched.

The user rejected the first vertically stretched3x5 labels as barely readable,
and the continuing Ninja/donor faces as contrary to the original-art request.
The label renderer now uses proportional six-pixel-high letters with the native
light/dark outline colors; wide M/N/K receive appropriate widths. The page hint
uses seven-pixel lettering over72 pixels. Original42 icons are byte-preserved.
Do not restore the old font or call donor art finished.

`src/art/job-portraits.json` contains ten original18x16 head/bust drafts drawn
as explicit indexed pixel rows on blank grids. `scripts/job_icon_art.py` draws
the generic UI frame, packs these pixels, records hashes and produces private
review PNGs plus a generated C include. It never reads donor character pixels.
These drawings were authored in source, not through LibreSprite; the separate
older body/icon drafts retain their desktop-drawing provenance. Keep this honest.
The designs follow the briefs below but need further aesthetic refinement; menu
head drawings are not complete actor sheets or proof of other portrait pipelines.

`ffta_icon_decode` at the native0x080cb9e0 dispatch replaces only116-125 and
delegates all other jobs to the previous integrated decoder. The generated
portraits retain the existing native palette-bank choices. The renderer lays
out jobs2..43 on page0 and116..125 on page1, using actual native eligibility.
All native ability/gameplay/job data remains unchanged by this module.

Reservation: ROM offsets0x1d00000..0x1d04000 (GBA0x09d00000..0x09d04000).
Hooks: party0x8e488/0x8e578, Buy0x6aede/0x6afb8, Sell0x6cf5a/0x6d034, and the
integrated icon trampoline pointer0xcb9e4. Every native hook is authenticated
against clean bytes; the dispatcher retains its previous pointer. Compilation
rejects overflow and writable data/BSS. No persistent/save RAM is allocated.
Party/shop tilemaps are0x06005000/0x06005800. Page identity is the offscreen
row19 column31 cell (0xa700|page); L/R toggles and native A/B exit clears it.
The hint uses party0x06004800 or shop0x0600f000 (288 bytes); icon graphics remain
party0x06000020 or shop0x0600b000. Full ranges are guarded by native canaries.

Actual inputs: world Start→Party A→roster Start opens Item List; A on the
highlighted item opens the grid. In Buy or Sell lists, Select opens item help,
A advances the description, A finishes category text, then Select at the prompt
opens the grid. R from the list is the different equipment-teaching panel.

Passing reports:

- `20260917T175038.360804Z`:514 original-portrait consumer checks,3567 native
  preview checks,8 Item List checks,21 Buy checks, on42e3d2412c4f3dec22f22d44b65c686238f75096.
- `20260917T175229.202142Z`:21 Sell checks on current7bfdecde. This adds only
  the Sell-specific wrappers/hooks; unchanged prior renderer/portrait evidence
  is reused. The compiler still builds the entire bounded module.
- Buy/Sell compare original-page tile coordinates and palettes against the
  shipping ROM and compare WRAM deltas across the same native entry/help route.
  This resolved a preservation assertion that had included native shop-entry
  changes. No money, live save or transaction changes were introduced.

Full failure history and counts are in the latest implementation checkpoint.
Earlier mechanically passing tiny-font/donor candidates are visually superseded.
Current actual render: `build/art/equipment-preview/ui/20260917T175045.972659Z/party-new-jobs.png`.
Current Samurai R-panel: `build/art/equipment-preview/attempts/20260917T175038.861767Z/consumer-right-shoulder.png`.
These establish icon/grid transport only. G01-G04 remain open pending final
art review, actor and other graphics consumers, clean rebuild and delivery.

## Scope and preservation

The user requests native-style art for all expansion content and a large original
reference library, with a preference for hand drawing in a desktop pixel editor.
Ten racial jobs implement eight concepts. Inventory battle land/water animations,
weapons, job/menu icons, portraits/party figures, equipment icons, effects and
status icons separately. The equipment preview grid omission is an independent
UI defect. Keep all extracted original assets, tools, PNGs, editable art files and
experimental ROMs under ignored private directories. Preserve the running player
showcase, vanilla, and release ROM/save paths. No publication is authorized.

## Reused findings requiring end-to-end proof

Candidate SHA1 `1b070824a8dad4995434eee3ab40fa08187a6120` has donor graphics for
new jobs 116-125: donors 6,3,13,15,25,27,41,36,29,30. Animation table 0x390E44
has 248 entries; sizes are at 0x391224. Sequences use 12-byte descriptors and
20-byte frame records. Tile and OAM offsets are relative to 0x69B89C and
0x852E7C. Preserve duration, commands, unknown metadata, layout and palette.
The previous audit only round-tripped 4bpp nibbles; it did not prove importing.

Native actor, weapon, job icon, equipment icon, party/portrait and action-effect
consumers differ. `job-wheel.c` and `equipment.c` deliberately remap to donors;
changing actor tiles cannot replace those displays. Existing presentation-only
weapon fallbacks must preserve actual equipment/gameplay semantics.

## Gates

The user rejected the initial Samurai icon (a Ninja donor with a crest) as a
reskin. It is a rejected technical prototype, not production artwork. All new
class character designs must start from blank canvases, with original class-
appropriate silhouettes, clothing and equipment. Extracted originals are for
proportions, palettes, animation cadence and format study only. Do not repaint
or lightly modify donor characters. Preserve this distinction in asset manifests.

1. Lossless reference export/import with authenticated ROM and bounded parsing.
2. Isolated new-job resource ownership and one actual native replacement.
3. Manually authored native-size artwork, coherent across directions and motions.
4. Targeted declared runtime checks and visual review, with failures and missing
   coverage retained. Do not broaden tests solely for a changed graphics hash.

## Original design direction

These are drafting directions, not accepted or completed artwork. Preserve each
race's anatomy while drawing new clothing, silhouettes and equipment from scratch.

| Job | Distinct visual construction |
| --- | --- |
| Human Samurai | Flared kabuto and gold crest, exposed face, red lamellar armor, separate shoulder and skirt plates, sheathed katana. |
| Human Dark Knight | Angular closed helm, asymmetrical dark plate, short torn mantle, heavy gauntlets and broad sword stance. |
| Bangaa Viking | Open muzzle, fur mantle, round cloak brooch, broad leather belt, axe harness and a stance built around Bangaa legs and tail. |
| Bangaa Dark Knight | Low armored crest, plated neck and chest, exposed Bangaa jaw, segmented tail protection; distinct from the Human armor pattern. |
| Nu Mou Chemist | Protective brow goggles, short work apron, reagent satchel and bottle harness fitted around Nu Mou ears and snout. |
| Nu Mou Geomancer | Layered earth-toned hood and mantle, stone pendants, broad sleeves and grounded staff stance; preserve Nu Mou proportions. |
| Moogle Chemist | Small safety cap, fitted work coat and vial belt, visible pom-pom and wings, compact tool satchel. |
| Moogle Bard | Feathered cap, split performance coat, scarf and instrument harness; preserve Moogle wings, ears and pom-pom. |
| Viera Dancer | Layered wrap costume, flowing sleeves, sash and ankle ornaments, a balanced dance posture with unobstructed Viera ears. |
| Viera Mystic Knight | Fitted silver-and-violet armor, split mantle, runic belt and saber stance; a clear armored silhouette. |

The shared style is native-size pixel clusters, disciplined palettes, consistent
light direction and original-game anatomy/animation cadence. A familiar donor's
outline with recolored clothes or an added emblem fails the design requirement.
The first replacement body construction was drawn on a new transparent32x32
LibreSprite canvas, not over an imported character. Its8 used colors and pixels
are preserved exactly in `src/art/drafts/samurai-body-construction.json`.
It is a rough block-in: contour, proportion, shading and palette work,
back view, action frames, and native actor import remain outstanding. Do not
promote it to production or advertise it as a finished FFTA-quality sprite.

## Evidence and current limitations

Private library: `build/art/native-reference/library.json`, clean ROM SHA1
`4ac05441f4de70a4ec3dd932116346c61b8783d9`.106 resources,3261 tile/OAM poses
and21438 frame records preserve native bytes exactly. Resource65535 is a
sentinel; final resource247 lacks a proved descriptor extent and is not parsed.
Previews currently use one native palette bank. They do not establish correct
per-job colors, battle palette allocation or a custom animation importer.

Visual inspection found that the first flattened pose PNGs were blank: converting
a palette-index mask through RGB luminance erased their pixels. Stored native
tile/OAM/sequence bytes and indexed tile atlases remained correct. The corrected
mask tests index zero directly. Declared static `test-native-art-format` passed
8 checks in run`20260917T165228.933343Z`; all3261 recomposed previews now have
visible pixels. A failed inline preview-rebuild command had a quoting syntax
error and made no edits; the reusable `--rebuild-previews` path replaced it.

Declared `export-native-ui-reference` passed44 native decoder/canary/indexed
roundtrips in`20260917T162129.043229Z`. These32x16 assets are face/abbreviation
icons. The job wheel actually displays animated actor miniatures. This corrects
the earlier audit's inferred consumer name; do not reuse that assumption.

Private POC SHA1`7d250040e81f20d793fb7fe29d19c7c32f6c0159` conditionally supplies
the manually redrawn Samurai icon only for job116. `test-native-art-poc` passed
504 checks in`20260917T164256.677725Z`: all124 job decoder comparisons/canaries,
palette preservation, authenticated private seed and actual Moonblossom teaching
panel rendering. The R panel contains the full256-byte icon at VRAM offset0xECA0;
`build/art/poc/consumer-right-shoulder.png` is the observed screen. This verifies
the icon integration path only. The installed expansion/showcase ROMs and all
player saves were not changed.

Failed attempts are retained as failures in the common runner's reports/logs:
`163819.391782Z` tested the wrong consumer (wheel); `163908.431011Z` also guessed
the wrong wheel asset dimensions; `164116.471876Z` opened the inventory on the
wrong item/category. All are September17 runs. The first diagnostic failed.json
path was reused, so the individual runner logs, not that latest JSON alone, are
the historical record. Future attempts now get unique artifact directories, and
the assertion explicitly selects the observed R consumer. These test-only
hardening edits have syntax validation, not a redundant new runtime pass.

The outer runner's default combat.json ROM hash differs from these script-selected
clean/POC ROMs. Use each art report's authenticated ROM hash for art evidence.
Actor/water animations, portrait/party graphics, equipment-grid enumeration,
weapon attachments, effects, status icons and aesthetic acceptance remain open.

## Sources

- Local ROM and current build pointers; engine source is authoritative for this
  candidate. External read-only audit is in the prior private sprite studio.
- [FFTA Engine Hacks](https://github.com/LeonarthCG/FFTA_Engine_Hacks), bundled
  Graphics Helpers.event and job/party graphic installers, corroborate formats.
- [LibreSprite](https://github.com/LibreSprite/LibreSprite) provides a local
  indexed-pixel/animation editor. Pin its official release and download hash.
