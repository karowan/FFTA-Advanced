# Reproducible campaign map decoding

`scripts/ffta_maps.py` reads only the verified clean USA ROM, SHA1
`4ac05441f4de70a4ec3dd932116346c61b8783d9`. It does not patch the game.
The 162 valid map records begin at ROM offset `569104`, stride `58` hex.
Record 162 is invalid; the material reservation's extra slot stays neutral.

## Decoding rules

- Graphics use the game's custom LZSS, containers 20/22 hex. Type22 carries
  an explicit destination byte prefix; do not derive that prefix from the
  animation count. Animation descriptors copy `(control & FFE0)` bytes from
  the selected frame into the record's destination. Giza's static graphics
  begin at byte820 hex, and its captured battle state uses animation frame2.
- Palette selectors1/2 use unsigned halfword offsets in their shared tables.
  Other palettes use the map's own raw or GBA LZ77 component.
- Arrangement, height and clipping components have independent inheritance.
  A type1/11 parent is loaded first, then the child's packed delta is applied.
  Following the parent and discarding the child silently changes real maps.
  Native loaders are `0801F1A8`, `0801F2EC`, and `0801F438` respectively.
- Arrangement runs index overlapping halfword entries in the strip dictionary.
  Bit15 supplies an explicit second tile; otherwise the second tile is the
  next index. Native `0801ED24` confirms the encoding. Final writes replace
  earlier entries, including transparent tiles. Height and clipping use
  offset/byte-count runs. Native height storage is512 bytes; clipping is8192.
- Some lower-layer indices exceed the graphics bank. The renderer accepts
  these only when every pixel of that8x8 rectangle is covered by an opaque
  foreground tile. It rejects any visible missing tile. Native arrangement
  output proves these references are present in the game data. The initial
  decoder exposed520 such uses, all completely occluded; they were not missing
  animation data or a reason to synthesize blank visible tiles.

The decoder checks indices, lengths, source bounds, back-references and alias
cycles. It rejects unsupported component formats. The current clean ROM uses
dictionary arrangement streams for every map and packed height/clipping runs.

The older [FFTAUtils source](https://github.com/spiiin/FFTAUtils) was a format
reference, locally inspected at commit0283a3d0faf0b82fd47fa9e71a8e5700e28f879a.
The native comparisons, rather than that editor's incomplete branches or
map count, establish the accepted decoding behavior.

## Deterministic verification and outputs

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite terrain`.
It runs the three terrain checks and the declared shared fixture prerequisites.
`terrain-loader` selects just the independent all-map component comparison;
`terrain-native` selects the decompressor/Giza capture comparison.

`test-terrain-loader.py` builds a private boot harness from
`terrain-native-probe.s`, supplies map IDs0..161 in fixed order, and captures
the unmodified game loaders' output using mGBA. The ROM's own functions and
mGBA's BIOS process the compressed data. No Python decoder substitutes for a
native loader. Each case has a30-frame completion limit and an acknowledged
request counter. The report compares all16,384 arrangement bytes,512 height
bytes and8192 clipping bytes for every map.

`test-terrain-native.py` separately runs110 unique custom LZSS streams through
the native decompressor in Unicorn, checks full output and guard bytes, and
compares Giza's height grid and complete composed graphics bank against the
existing real-battle fixture. `test-terrain-maps.py` emits every composite,
coordinate overlay and contact sheet, retaining canonical component hashes.

All images, extracted bytes, probe ROMs and logs stay ignored under
`build/expansion/terrain/<clean-ROM-SHA1>/`. Only authoring/test source is
committed. Open `contact-000.png` through `contact-144.png` for the overview;
`map-NNN-grid.png` carries the individual coordinate overlay.

## Accepted evidence and remaining scope

Run `20260915T204957.023678Z` passes12/12 with unchanged inputs: all162 native
layout/height/clipping comparisons, all162 renders,110 native LZSS comparisons,
and the Giza captured-bank comparison. The gameplay candidate remains
`7af41803aeaa1e566d166d796a65af865f0212e4`; this authoring batch changes no
shipping ROM bytes. Its previously accepted58-step combined gameplay report
is `20260915T191211.585109Z` and remains applicable to that unchanged ROM.

Failed predecessors remain in the run history. The all-map loader comparison
`204539.430214Z` isolated15 maps whose layouts or heights differed because the
decoder discarded inherited deltas. Earlier rendering failures exposed the
occluded references, while the Giza differential exposed a one-tile static
offset and an incorrect assumed animation phase. These errors were corrected
in the authoring tools, not hidden by changing native game data.

The subsequent material batch is documented below. The renderer shows base
scenery at a selected fixed animation frame, not event-driven changes or all
dynamic objects. Dedicated native Geomancer UI/AI/law/save acceptance and other
unfinished jobs remain open.

## Reviewed material source and campaign geometry

Schema2 of `notes/terrain-materials.json` contains explicit16x16 symbol rows,
a review rationale, and hashes for each map's decoded height, arrangement and
static graphics. `ffta_terrain.py` validates the clean-ROM identity, map range,
unique map IDs, dimensions, symbols, component hashes and absence of material
on void cells before the integrated builder writes the immutable table at
ROM11F0000. Material bits and the existing reservation remain unchanged.

Symbols are `R` rock, `V` vegetation, `W` water, `H` wood/heat, `I` ice/snow,
`S` mixed ice/snow and vegetation, `G` mixed rock and vegetation, `T` mixed
wood and vegetation, and `.` neutral/unresolved. These are
reviewed content choices, not an automatic palette classifier. Native water
recognition remains independent of annotations. On volcanic maps151..154,
native lava cells use flag4 and do not use water's flag2; no water-filter
engine change was necessary.

The first batch covers23 map records: snowy schoolyard0/1; masonry10..14,
36/37; wooden platforms54..57; stream grasslands68/69; Giza70/71; snow
basin118/119; and volcanic151..154. Remaining139 maps are unannotated.
Grassland objects receive coordinate-specific rock or wood overrides.
Snow basin rows distinguish snow, dried vegetation, mixed cover, and the
fallen log. Native boundary cells in the masonry maps remain neutral after
overlay review exposed offstage areas with nonzero height. Foreground
occlusion does not transfer an object's material to the lower cell behind it.

Run `scripts/review-terrain-cells.py 70 118` with the project Python to export
coordinate-labelled crops as an authoring aid. Run
`Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite terrain-campaign`
for consolidated acceptance. The same new checks are included in `combined`.
`test-terrain-native.py` now compares every valid cell's projection through
native0801CA98 (grid to world) and0801C918 (world to canvas), and verifies
the captured battle's256/256 origin. All24,731 valid cells match the overlay
formula `(256+16*(x-y),264+8*(x+y-height))`.

`test-terrain-campaign.py` checks the shipping table against independent
source-row serialization, all41,472 coordinates' material neighborhoods,
and24,731 valid-cell Gaia option lists using captured native height grids.
Its128 fixed native casts cover Stone Pulse, Ward, Wisp, Rime, Tanglevine,
and Torrent on representative real layouts. Same-seed controls remove only
the private material table; they retain original terrain geometry and native
water. The two stream positions verify water within reach and just outside
reach. Outputs include `terrain-campaign.json` beside the candidate and
`map-NNN-materials.png` in the terrain authoring directory. Root reviews these
overlays. No agent plays, drives or monitors game tests.

The first focused run `20260915T210718.904594Z` caught an incorrectly positioned
Torrent caster in the test: water was two cells away. The corrected scenario
and retained out-of-range negative control pass in `20260915T210830.447000Z`
(12/12). After boundary-cell cleanup, final candidate
`595dd83dd9dcfed61a0accce5506fba9d66a3bd7` passes61/61 combined steps in
`20260915T210938.441004Z` with unchanged inputs. The final catalog contains
3,441 annotated cells; the campaign report contains66,683 assertions and128
native executions. Only those3,441 material bytes differ from7af41803ae;
code and save layout are unchanged. Root reviewed every final material overlay.
Passing native geometry and executor checks does not certify complete map
coverage, rendered player menus, autonomous AI or a campaign playthrough.

## Settlement and interior material sweep

The next coherent batch adds58 records, bringing the reviewed catalog to81
maps and10,528 annotated cells. Every ID0..71 now has an explicit review;
the same reviewed stream geometry also covers144..146. The earlier snow
basin118/119 and volcanic151..154 entries remain. Remaining unreviewed IDs
are72..117,120..143,147..150 and155..161. Neutral cells include intentionally
unclassified furnishings, fabric and scenery boundaries, not only voids.

The new rows distinguish snowy streets, wood furniture/barrels/bridges, marble
and sandstone paving, garden plants, palms, mossy pavers and lit braziers.
Green architectural patterns remain stone; white canvas remains neutral;
blue/white cave crystals remain mineral rock. Orange rock and green water on
map32 are explicitly separate. `G=3` and `T=10` combine the existing bit groups;
they add no new engine factor or saved state. Each applicable modifier still
applies at most once. The native neighborhood height rule remains unchanged.

Root reviewed coordinate crops and all58 new full overlays before testing.
The `--materials` option on `review-terrain-cells.py` exports labelled crops
and `map-NNN-review-overlay.png` without executing the game. Review exposed
90 incorrect boundary/cactus-tip annotations across eight maps, including one
older map14 cell. These were cleared before acceptance. Scene perimeters can
have ordinary flags, so the review also considered rendered surface coverage;
transparency rejects unknown surfaces and never determines their material.

The expanded campaign test retains ten explicit, independently reviewed
surface expectations and adds native casts beside mossy paving, a palm canopy
and cave crystals. Its176 fixed native executions include a negative Rime
Slow check on mineral terrain. Final candidate
`7654efd5e0095e6f0f497375317ac49cb0f0a32d` passes61/61 combined steps in
`20260915T213138.912230Z` with `inputsUnchanged=true`. The campaign report
contains66,872 passing assertions and176 native executions. Exactly7,089
terrain-table bytes differ from595dd83dd9, with no executable or save-layout
changes. Broader Geomancer and job completion gates remain open.

## Forest, mountain and desert material sweep

The outdoor batch adds 36 records (72..107), bringing coverage to 117 maps
and 15,038 annotated cells. Root reviewed coordinate crops for all 18 layouts
and full authored overlays for all 36 daylight/night variants. The rows use
existing symbols and component hashes; no engine factor or saved state changed.

Forest vegetation, palms/conifers, cut stumps and dead trunks are distinct.
Mountain ledges separate rock, grass and leafy cover on rock. Desert records
separate exposed stone and plants from loose sand, which stays neutral.
Night palettes do not make grass, sand or stone into ice. Autumn foliage and
orange flowers do not supply heat. Foreground trees do not classify lower
ground cells behind them. Review corrected a conifer/rock pair and two forest
occlusions before acceptance. The sloped dead-trunk footprint on map 96 at
(0,3) has a transparent exact center but visible wood in the cell; it remains
wood. Offstage ridge and basin centers remain neutral.

Fourteen fixed semantic anchors and five new native cast scenarios supplement
the existing campaign checks. The declared total is 256 native executions:
same-seed material-enabled versus zero-mask controls, preserving native grids.
The new cases check forest-stump heat, no heat from autumn leaves or desert
sand, no ice from night sand, and a rock bonus from exposed desert stone.
Candidate `d7bf7772f5bdebca551074108656272e2f3d5be5` passes all 61 combined
steps in run `20260915T215232.519357Z`, with `inputsUnchanged=true`.
The terrain report records 67,227 passing assertions and 256 native casts.
All 4,510 changed bytes relative to `7654efd5e0095e6f0f497375317ac49cb0f0a32d`
lie inside the existing material table; executable bytes, ROM length and save
layout are unchanged. Root reviewed the source and all new overlays, including
the final forest occlusion corrections.

Unreviewed maps are 108..117, 120..143, 147..150 and 155..161 (45 records).
Explicitly neutral sand and unresolved scenery are not additional material
groups. Terrain executor acceptance still does not establish native menu
playback, AI behavior, law handling, cold-save coverage or a campaign playthrough.

## Complete native-map material coverage

The final catalog batch adds the remaining 45 records: 108..117, 120..143,
147..150 and 155..161. All 162 native maps now have reviewed explicit rows
and component hashes, totaling 21,625 nonzero material cells. Root inspected
coordinate crops and all 45 new full overlays, including every alternate
palette. The production builder requires the complete native map set; its
extra reservation slot 162 remains neutral for the existing defensive lookup.

`M=6` combines existing vegetation and water bits for waterlogged reeds. Open
water, dry banks, flowers, boardwalks and rock clusters are separately authored.
Snow maps distinguish ice cover, exposed rocks, vegetation and a fallen log.
Mineral caverns stay rock, including blue and prismatic formations; native lava
and visible flames in the volcanic cavern receive heat. Ruins separate masonry
from surrounding vegetation and decorative fittings. Interiors separate stone,
wood, plants, flames and fountain water from carpet and upholstery.

Neutral sand, cloth, unresolved furnishings and offstage borders are deliberate
choices, not absent map records. A transparent exact center on a sloped branch
does not erase a visible shrub footprint: map 147 (0,9) retains vegetation.
This differs from unrendered scene boundary cells. All source edits preceded
the acceptance run; no automatic color classifier or interactive fixture was used.

The campaign script declares 368 fixed native executions and fourteen new
surface anchors. Added scenarios cover wetland boardwalk heat, snow Slow,
winter-log heat, volcanic-cave heat and negative blue/prismatic mineral cases.
A new Torrent case at map 108 caster (11,1), target (10,1), south destination
(10,2), has no native water flag in the caster's neighborhood. Only the enabled
reviewed wetland table may supply its push; the same-seed zero-material control
retains damage without pushing. Removing one map must fail the production
table builder.

Candidate `1a4601dc73478e55f9ee0654cb55bd2d92905c7f` passes all 61 combined
steps in run `20260915T221353.996549Z`, with `inputsUnchanged=true`.
The terrain report contains 67,714 passing assertions and 368 native casts,
including the new wetland-only push and snow-positive/mineral-negative cases.
All 6,587 changed bytes from `d7bf7772f5bdebca551074108656272e2f3d5be5`
fall inside the material table; executable bytes, ROM length and saved-record
layout are unchanged. Logs and native results remain under the ignored
hash-addressed candidate and test-run directories. The runner's top-level
`ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7` is the prerequisite fixture base,
not the assembled candidate.

All map records are reviewed, but native menu playback, AI, laws, dedicated
cold-save coverage and complete job/expansion acceptance remain separate gates.
