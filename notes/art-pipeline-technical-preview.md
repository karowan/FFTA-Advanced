# Connected art pipeline technical preview — September 17, 2026

The user stopped Gemini/fal and directs built-in imagegen only, technical
integration first, sprite refinement afterward. No further generation request
was made. Existing built-in drafts supply explicitly temporary transport assets.
The overall goal and G01-G04 remain open.

## Connected candidate

ROM SHA-1 `0edf9489f2a29c4e806129903a395d7f03914a00`, resolved from
`build/art/pipeline/current.json`. It composes the existing isolated Samurai
land/water resources256/257, generated land idle slots0/1 and corrected foot
baseline; a new compressed menu image54 for resource256; and the paged equipment
preview with temporary imagegen-derived portraits for all ten classes.

`generated_menu_icons.py` authenticates catalog sources and converted tile
hashes, records the provisional top-half head crop and remaps into each native
icon palette. No new character pixels are drawn. Dedicated portrait sources
and visual refinement remain open; these small crops lose detail.
`art_candidate.py` selects an explicit composed manifest for existing tests
without replacing old component pointers or their earlier passing evidence.

## Miniature format and palette proof

The A7 dictionary container at ROM0x3b5a5c has54 entries of640 bytes, arranged
as32x40 4bpp images. It is not16x80. `native_miniatures.py` decodes the dictionary
and emits a literal encoding accepted by native0x08005318/0x080051c4. The new
55-image container is35,707 bytes. All54 original images remain exact.

Literals0x87bd8/0x87c58/0x87d90 select the container. The actor-to-image mapping
has two-byte records; its literals are0x87bd4/0x87c54/0x87d8c. Only private
Samurai resource256 changes from image4 to54. The generated source is padded
to32x40 with its opaque baseline aligned to original image4.

Initial candidate39fac6d5 rendered wrong colors and failed actual palette
equality. Enabled OAM objects11/12 use bank4 and tile168/184 (32x32 plus32x8).
Their opaque palette bytes match source ROM0x94ee5c, not battle/icon0x419d80.
Corrected conversion maps into that menu palette, producing component
04df42d89976d877b1f70b3d7fc837a7718ab6e8. This is a constrained-palette proof,
not custom allocation or a general rule for every menu context.

## Evidence and retained failures

- `20260917T200004.623329Z`: native miniature decoder passes1,447 checks:
  all54 originals and55-entry rebuild, stack alignments, ABI, count/range/invalid
  indices, complete canaries and deliberate corruption. An earlier unquoted
  PowerShell runner invocation never started a test; corrected invocation passes.
- `20260917T200356.278303Z`: miniature UI **failed** on displayed palette equality.
  Captures and failed report remain. `20260917T200521.983476Z` passes91 corrected
  display/palette/isolation checks, eight idle snapshots and unchanged owned data.
- `20260917T200909.470047Z`: all seven composed consumers pass: icons514,
  preview-native3567, party8, Buy21, Sell21, miniature91 and battle2303 (6,525).
  Original passing captures are authenticated and reused. This is a targeted
  combined display milestone, not a gameplay full integration suite.
- `20260917T201341.666501Z`: art rebuild passes15 checks. Ten original PNGs
  reproduce all selected tiles/palettes, then four art-source stages reproduce
  the exact tested ROM. Unchanged v0.7 clean-source rebuild evidence is reused.
- `20260917T201414.982339Z`: packaging **passes**, launcher validation **fails**
  because Windows PowerShell lacks Get-FileHash. The launcher now uses the
  working release launcher's .NET hashing approach; that old run stays failed.
- `20260917T201455.103923Z`: only launcher validation reruns and passes.
  All three storage overrides are separate; a wrong-ROM tree is refused before
  launch. Existing player games and saves remain unchanged.

Private delivery:
`build/art/pipeline/delivery/0edf9489f2a29c4e806129903a395d7f03914a00/`.
BPS SHA-256 `aed36098ab1701af7e0468ccb8fa0c905f693be3d6ee3ca115bafeb5edc8e467`.
Patch roundtrip, deterministic output and wrong-source rejection pass. Manifest
freezes ROM, guide, candidate and evidence hashes. See `ART-PIPELINE.md` and
`Play Art Pipeline Preview.cmd`. No game launched or player save imported.

## Remaining technical work before sprite refinement

This is one connected playable prototype, not the complete end-to-end scope.
Generalize private actor/menu ownership to the other nine jobs; prove action
and water replacement, all facings and per-consumer custom palettes. Prove
larger portrait, equipment/weapon, effect and status paths separately. Test
generic changed-class roster display independently from the selected wheel;
story-character fixed appearances remain their own native path. Then assemble
and verify the complete technical package before refining final sprites.
Do not generate more concept batches or close G gates from this slice.
