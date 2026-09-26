# New equipment icon drafts

The expansion defines 85 new teaching weapons, IDs 376–460, in eight icon
families: Katana, Sword, Axe, Saber, Knife, Rapier, Instrument and Rod. This
checkpoint starts distinct inventory icon artwork for those item identities.
These are review drafts. No item icon has been approved, imported into a ROM,
or verified in the assembled game's inventory/shop/quest consumers.

The first draft sweep now has one selected candidate for each of the 85 items.
All 85 selected native pixel payloads are distinct. The deterministic draft
audit passed reference, prompt, raw-image, palette, format and pixel-hash
checks across all eight families. The exact selected prompts and hashes are
recorded in [new-item-icon-drafts.json](../src/art/imagegen/new-item-icon-drafts.json);
the raw PNGs, rejected attempts and comparison sheets remain ignored under
`build/art/item-drafts/`.

The 16×16 inventory icon is one visual consumer. In battle, all new weapons
currently inherit a family donor's held-weapon resource, except the 17 axes,
which share one temporary generated resource. The held resources contain
several drawing frames plus native attachment/OAM/timing data; one inventory
PNG cannot replace them. Projectile Throw uses the inventory icon. There are
no new item-specific hit effects in these records. Distinct held art for 85
weapons needs a separate native resource and attachment study.

## Source and generation

`scripts/export-native-equipment-reference.py` authenticates the clean USA ROM
and extracts all 522 original 16×16 icons into ignored
`build/art/native-reference/equipment-original/`. The donor inputs for the
eight families are original icon IDs 106, 001, 052, 032, 074, 088, 201 and
135 respectively. Their original palette banks and SHA-256s are recorded in
the export's `report.json`. Those Square Enix images are private references;
do not add them or mixed reference worksheets to Git.

Every new draft uses the relevant authenticated original PNG directly as a
`referenced_image_paths` input to the built-in image generator. The original
informs scale, outline, palette and item family; each item gets its own
name-led prompt and image. Record the exact prompt, tool identity, raw PNG,
reference SHA-256 and rejected attempts under ignored `build/art/item-drafts/`.
The built-in tool does not expose a reliable underlying model version; do not
invent one in receipts.

`scripts/prepare-item-icon-draft.py` crops the generated alpha footprint,
optionally mirrors the draft to match the family orientation, fits it within
14×14 logical pixels, and maps opaque pixels to the authenticated original
16-color palette. It saves a 16×16 indexed preview, a nearest-neighbor zoom,
and exact source/pixel hashes. Mirroring is a recorded technical registration
step; preserve the unmodified raw image. These conversions are proposals,
not accepted production pixels. Review at native size next to the original.

`scripts/make-item-art-review.py pilot|pipes|rods` creates private comparison
sheets from the ignored inputs. The pilot shows one item per family; the pipe
and rod sheets show each of those families. Compare color loss, readable
silhouettes, guard/hilt/tip distinction, and unwanted orientation changes.
After selecting one candidate folder per item in ignored `selection.json`, run
`scripts/refresh-item-art-drafts.py`, `scripts/audit-item-art-drafts.py`, and
`scripts/make-item-art-review.py all` to regenerate and audit every indexed
preview and create one comparison sheet per family.

Visual review remains open. At 16×16, 18 Axe/Saber candidates lose a named
accent or look too similar to siblings; Kiku Echo, Red Spider Katana and Gloom
Sword need further identity work; several Knife/Rapier motifs reduce to a hilt
or guard accent. The nearest selected pair in the draft audit differs at 20 of
256 indexed pixels. Pixel uniqueness is not a visual-approval criterion.

## Remaining acceptance

- Review all 85 indexed previews. Strong distinctions in raw images may collapse
  at 16×16; reject and regenerate indistinct or unreadable results.
- Freeze approved preview hashes in a new receipt and extend the authenticated
  public artwork inventory before committing any generated PNG.
- Extend the equipment-only icon transport for distinct item IDs without
  changing overlapping quest icon IDs. Native held weapon and effect artwork
  are separate consumers.
- Verify inventory, shop and relevant battle displays in the final assembled
  ROM. A generated PNG or indexed preview alone is not an in-game result.
