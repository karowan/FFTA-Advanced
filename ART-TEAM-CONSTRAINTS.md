# Art team brief: limits of the completed FFTA expansion

For the subsequently approved first-pass art, use the
[working native-art pipeline](src/art/native-ui-review/README.md) and its exact
approval receipt. This brief describes the earlier engineering handoff; its
provisional portrait crop/fitting and head extraction are superseded by generation
for exact 48 x 56 portraits and 16 x 14 frontal heads. Existing native palettes
remain mandatory; later art work does not authorize a custom palette system.

This brief applies to the delivered full-engineering ROM
`a28b624bb13c8f2f2597a4d4bd3999b17c234b99`, source checkpoint `f07411c`,
accepted at checkpoint `22b40e3`. The original game and approved v0.7 engineering
are complete. Final character designs, pixel quality and authored animation
poses are not accepted. Repeated poses, rough crops and palette compromises are
temporary art, not the intended final visual standard.

Read this before commissioning or generating a full set. The constraints below
describe the **current import pipeline**, not every capability of GBA hardware.
Larger actors, different frame timing, new effect systems or independent battle
palettes require separate engineering; they are not ordinary picture swaps.

## What the art team should deliver

- Original generated designs for all ten racial class options, consistent across
  body, menu head, wheel figure, large portrait and action poses. Use imagegen;
  keep exact prompts, model/settings, original outputs and source hashes.
  External provider APIs need the user's request. Do not hand-draw replacements
  or generate coded pixel patterns under the current project instructions.
- Match native FFTA proportions, race anatomy, pixel density, silhouettes and
  visual hierarchy. Use original sprites as references, not recolor/decorate
  bases. A Ninja with additions is not an accepted Samurai design.
- Transparent source PNG sheets with explicit cell order, facing, action and
  phase labels in a separate manifest. No captions, checkerboard texture,
  background scenery, shadow outside the intended sprite, or adjacent-cell
  contamination in the actual art cells. A larger source does not increase
  the game's final resolution.
- Native-size conversions alongside the source: inspect at 1x and integer
  nearest-neighbor magnification. Approval of an attractive large sheet does
  not approve its conversion. Faces, eyes, hands, silhouettes and class identity
  must survive conversion and the actual in-game palettes.
- A per-consumer coverage list identifying every finished, repeated, cropped,
  shared, native-retained and still-missing image/pose. Mark drafts as drafts.
  Do not label a generic sixteen-pose sheet a complete native animation set.

## Sizes and color limits by consumer

| Consumer | Current import contract | Consequence for artwork |
|---|---|---|
| Battle body, land and water | One 32x32, 4bpp object per body draw; 512 bytes, 16 tiles. Transparent index 0, at most 15 opaque indices. | Keep the complete silhouette inside the cell. Large weapons, capes or effects cannot silently extend the body canvas. |
| Wheel/party miniature | Separate 32x40, 4bpp image: 640 bytes. Current importer inserts a 32x32 body image with a donor-relative vertical offset of 0–8 pixels. Separate wheel palette. | A correct battle sprite does not establish a correct wheel figure. The 40-pixel canvas is not permission to enlarge the battle body. |
| Small job head and eligibility badge | Whole badge 32x16, 4bpp; current generated head fits 16x14 inside its frame. Labels occupy the right side. | Keep head, frame and lettering separate. Current head extraction is provisional and may need a dedicated source/crop adapter. |
| Large portrait | 64x64, 8bpp canvas; current conversion fits a crop within 60x60, centered horizontally and bottom-aligned. Up to 47 opaque colors, mapped to palette indices 97–143; index 0 transparent. | This is a separate format, not an enlarged 32x32 sprite. Current upper-body crop and duplicated palette variants are placeholders. |
| Axe inventory/projectile image | 16x16, 4bpp, 128 bytes; native palette bank 0. | One shared image currently serves the selected axe item family; not independent art for every item. |
| Held axe | Separate native weapon resource 276 using the equipment image, 16x16 primary object. Original attachments, auxiliary layout, timing and command-only frames retained. | Match hand/contact position in actual Fight animations. Do not bake a second copy of the held weapon into the body. Auxiliary tiles are currently transparently padded. |
| Tomahawk impact | Source is three square cells in one row; conversion is three 24x24 compositions. Only three opaque reference colors plus transparency. Native multi-object layout yields an 864-byte tile payload. | Not a free-color or arbitrary-length particle animation. Keep the existing impact origin, frame order and native scheduling. |
| Two custom status glyphs | Two 8x16 images, 4bpp, 64 bytes each, existing native palette. Source has two side-by-side cells. | Design for recognizability in very few pixels. Existing status selection, layout and timing remain unchanged. |

These are independently consumed assets. Other weapon families, spells and
effects retain their existing presentation unless explicitly listed as replaced.
Original fixed story-character presentation is preserved; a new generic class
design must not overwrite named-character art. Native 8x8 tile packing, compressed
archives and OAM assembly belong to the converter, not a universal PNG layout.

Sources: [body/miniature importer](scripts/generated_class_transport.py),
[small head importer](scripts/generated_menu_icons.py),
[large portraits](scripts/generated_portrait_transport.py),
[equipment](scripts/generated_equipment_transport.py),
[held weapon](scripts/generated_weapon_transport.py),
[impact](scripts/generated_effect_transport.py),
[status glyphs](scripts/generated_status_transport.py).

## Battle palettes: the performance-critical restriction

The current build uses the original **shared native battle palettes**. It does
not allocate ten independent custom palettes. Changing a shared palette can
change original actors or other consumers as well. Do not modify it globally
to accommodate one costume without an explicit engineering impact review.

| ID | Class | Body resources, land/water | Ally / enemy palette selector |
|---|---|---|---|
|116|Human Samurai|256 /257|1 /0|
|117|Human Dark Knight|258 /259|0 /1|
|118|Bangaa Viking|260 /261|0 /1|
|119|Bangaa Dark Knight|262 /263|1 /0|
|120|Nu Mou Chemist|264 /265|0 /1|
|121|Nu Mou Geomancer|266 /267|0 /1|
|122|Moogle Chemist|268 /269|0 /1|
|123|Moogle Bard|270 /271|0 /1|
|124|Viera Dancer|272 /273|0 /1|
|125|Viera Mystic Knight|274 /275|1 /0|

Selector 0 is ROM file offset `0x419D60`; selector 1 is `0x419D80`.
Each contains sixteen RGB555 words. Exact palette words, display RGB values,
resource allocations and reservation snapshot are in
[the machine-readable contract](notes/art-team-contract.json). Those are
reference metadata, not a ROM or an importable graphics archive.

Opaque pixels may use only indices 1–15. Index 0 must remain transparent even
when black would be the closest color. Body conversion uses nearest RGB555
squared-channel distance, lowest-index tie breaking, and preserves transparency.
Different source colors can collapse to one output color. This can erase eyes,
outlines and clothing separation. Design against the final native ramps, and
check the **same indexed sprite in both ally and enemy palettes**, including
native brightness/fade/highlight states. The enemy palette is a change in index
meaning, not a separately generated costume sheet. Wheel, badge, large portrait
and effects use their own palette contracts; do not assume body colors carry over.

The removed runtime ownership/scanning/remapping system caused the measured
Move/cancel delay and deployment cadence regression. The final
[native palette stage](scripts/native_palette_transport.py) converts colors at
build time, restores 29 native graphics entries and clears custom ownership
demand. **Keep that stage after action completion.** Old live-palette metadata
and code still exist for build provenance and independent menu/heap fixes;
their presence is not permission to restore their retired graphics hooks.

## Source sheets, alignment and facing

The [body converter](scripts/convert-generated-sprites.py) requires a nonempty
figure with transparent space on all four sides of every source cell. Alpha
128 or higher becomes opaque; lower alpha becomes transparent. Soft opacity
and antialiased fringes are not preserved as translucent body pixels.

All cells in one sheet share a scale. The current conversion bounds width to
28 pixels; default target height is 29, with explicitly selected heights 1–31.
The result is horizontally centered in 32 pixels, with `top = 31 - height`.
A crouch should therefore remain shorter than a standing pose, not be scaled up
independently. Transparent separators are required for custom row cuts. Do not
make one oversized pose shrink every other cell unexpectedly.

The initial class importer accepts four- or eight-cell drafts. Its selected
indices are `(0,0,2,2)` for four cells and `(0,4,2,6)` for eight. Native streams
reuse/mirror views, so arbitrary clockwise sheet order is unsafe. Explicit
animation plans allow 1–8 rows and columns. Identify facing and phase in the
manifest; verify actual native flipped views, handedness and equipment alignment.

OAM preserves the native ground/contact baseline. Current body objects are
centered at horizontal offset -16 with donor-relative vertical placement.
Do not change image origin, foot baseline or action contact point without
checking displacement and attachments. Water is a **separate resource**; the
current fallback retains only the upper 20 rows of a body picture. That crop
is a placeholder, not final swimming/water art or a requirement to crop new art.

## Animation is a mapping to existing commands

Keep descriptor identity, slot selection, null slots, frame counts, durations,
draw versus control commands, attachment behavior, ordering and event markers.
Visual changes must not alter movement speed, damage time, effect time, hit
windows, action completion or teardown. Do not add a frame merely by extending
a source sheet. A painted frame and a native command record are different things.

The current body tables have 84 descriptor slots per resource, 20 resources in
total. These are not 84 distinct artworks each: sequences and images can share
data, some slots are null, and some records are control-only. Preserve legitimate
sharing while providing enough authored poses for natural animation. Enumerate
the final actual tables rather than guessing coverage from an animation name.

[AnimationPlan](scripts/generated_animation_plan.py) maps exact
`job/lifetime/slot` sequences to source frames, preserving native frame counts.
A `complete` plan must cover every present slot of its declared jobs; even then
it does not approve visual quality. [LiveActionPlan](scripts/live_action_plan.py)
is a different interface: authenticated native-pose substitutions, exact shared
class palette, and **partial coverage only**. Unmapped frames retain placeholders.
Do not set its production flag to true to bypass its guard.

There are several successive writers. The live-art stage can replace earlier
body poses, and Human Dark Knight uses its separate `march-v2-own-palette` source
unless explicitly overridden. Updating only its catalog idle source does not
replace that battle march. The final Moogle completion stage supplies missing
weapon sequences from idle art: job 122 slot groups starting at 42 and 60, and
job 123 starting at 42. A plan authored before those slots exist cannot cover
them automatically. Final-art integration must explicitly support those later
streams, then apply native palette conversion. Review the final assembled ROM,
not just the first successful importer output.

These limitations may require small source-selection/pose-mapping adapters for
the art pass. Same-format replacement does not require a new renderer, but
dedicated portrait sources, new completion poses or arbitrary per-item weapons
are **not all exposed as a single drop-in PNG setting today**. Never silently
leave a later stage's placeholder over an artist's finished frame.

## Text and small-screen readability

The equipment badge's abbreviations are `SAM DKN VIK DKN CHM GEO CHM BRD DNC MYK`.
The current lettering uses variable widths, six-pixel-high glyphs at rows 5–10,
one-pixel spacing and dark outlines. See
[the actual label renderer](src/engine/equipment-preview.c). Preserve native
proportions and contrast. Do not generate lettering into character art or
stretch a tiny font to fill the badge. Full names require layout work rather
than squeezing them into the abbreviation area.

Review Item List, Buy and Sell on both L/R eligibility pages, in enabled and
disabled colors; wheel and full portrait screens are separate. A large browser
gallery alone cannot establish legibility at the game's 240x160 display size.

## Space and capacity: avoid accidental engineering changes

The ROM is 32 MiB and the existing reservation map is shared. Do not append or
claim a region because an old note calls it unused. The current native palette
payload occupies `0x1F10000..0x1F2CFE0`, within the reserved end `0x1F80000`.
At this checkpoint that reservation has 340,000 bytes left; it includes copied
sequences/descriptors as well as tile payloads. Deduplication makes actual growth
depend on unique pictures and sequences, not simply source PNG size.

Earlier action storage and later completion/native-palette storage share a
larger region. In particular, `0x1E9E000..0x1F80000` is **not entirely free now**:
completion begins at `0x1F00000` and native palette transport at `0x1F10000`.
The intermediate live-art reservation has only 11,072 bytes left in this build.
It remains in the source chain despite retirement of its runtime color layer.
New poses can overflow that earlier stage before the final stage runs. There
is no automatic spill allocator. Use the current per-stage `used/reservation`
values and overlap assertions, not sums of nominally unused parent ranges.

Keep 32x32/16-tile body allocation and existing object counts for a normal art
swap. Extra OAM objects, larger sprites, unique banks or larger decoded effect
buffers change runtime capacity and need engineering validation. Current
demanding coverage retains all ten class resources among thirteen native actors;
it is not a promise of arbitrary fourteen-actor transplants or 36 simultaneous
actors. That artificial fourteen-actor failure also reproduces in the original
native sort and remains documented. Observed Status free space of 11,052 bytes
(8,776 contiguous) is a scenario result, not an art team's additional RAM budget.

## Replacement and acceptance workflow

1. Start from the delivered ROM identity above and
   [the exact build-input recipe](notes/native-art-build-inputs.json),
   [class catalog](src/art/imagegen/catalog.json) and
   [full build instructions](REPRODUCIBLE-BUILD.md). The old7507ca5c gallery and
   override examples are historical references, not the current release.
2. Version original imagegen output, prompt/settings and conversion metadata.
   Keep private images, palettes, tiles and native reference exports ignored.
   Original FFTA resources under `build/art/native-reference/` are private
   style/animation references; do not commit or publish extracted game assets.
3. Prove one replacement through its actual final consumer before mass
   production. Compare source, converted pixels, final native palette pixels
   and in-game rendering. Record both final ally/enemy colors and native scale.
   Dedicated crops and final-pose mapping must be explicit and reproducible.
4. Rebuild every dependent consumer and later stage, using private outputs and
   `publish_current=False`. The pinned current recipe intentionally rejects
   changed art. Create/update a reviewed candidate recipe and hashes; do not
   weaken hash checks or claim the old exact-ROM proof covers new pixels.
5. Use `Test Expansion.ps1` with declared, narrowly affected IDs. Before runtime,
   announce exact IDs and purpose. Existing `test-art-native-palettes`,
   `test-art-native-palette-entry`, `test-art-native-palette-response`,
   `test-art-native-palette-deployment` and `test-art-native-palette-capacity`
   are reference checks, not an automatic full rerun list. Their candidate and
   fixture pins must be adapted explicitly for the new ROM. Select the actual
   weapon/cast/Combo/water/UI consumers changed; retain applicable passing proof.
6. Verify native commands/OAM/timing, transparent pixels, byte/allocation bounds,
   palette side/fade behavior, contact points and real action return. Broaden to
   capacity/scene/save lifetimes when object/buffer/code changes make it relevant.
   Do not use old custom-compositor observers against native palette transport.
7. Retain failed conversions and runs with their original labels. Record exact
   ROM, source inputs, logs and finite coverage. Art approval and transport
   acceptance are separate; a complete mapping can still look bad.
8. Package a reviewed candidate with its own manifest, patch, guide and isolated
   storage. Preserve the installed release and player sessions. No automatic
   save migration, cross-ROM savestate reuse, launch, public gallery or publication.
   New councils/subagents require a new explicit user request.

Full-engineering evidence remains in
[the delivery review](notes/native-art-engineering-delivery.md). Testing is
bounded emulator evidence, not every possible effect combination, an uninterrupted
full-combat playthrough, or physical-GBA timing. This documentation change does
not alter the tested ROM, packaged assets, launchers or saves.
