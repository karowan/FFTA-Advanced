# Weapon icons in the release

Status: approved for release by the player on September 26, 2026 and
installed by the `item-icons` stage, the last stage of v0.7.3 (released game
`40c9bbb9115c53ddbab6381e93c963ae0bd31ee4`).

The 85 expansion weapons (IDs 376–460) previously showed their family donor's
original icon; the 17 axes shared one temporary generated icon. Each weapon now
has its own 16×16 icon. They come from the palette-constrained drafts in the
[draft checkpoint](item-art-drafts-2026-09-25.md) (prompts, donors and hashes in
[new-item-icon-drafts.json](../src/art/imagegen/new-item-icon-drafts.json)).

## Publication

[export-item-icons.py](../scripts/export-item-icons.py) authenticates each
selected native preview against the committed draft record, checking both the
PNG hash and the native pixel hash. It then copies the PNGs byte for byte to
[artwork/items](../artwork/items) and writes the approval receipt
[new-item-icons-approved.json](../src/art/imagegen/new-item-icons-approved.json).
Matching `item-icon` rows (16×16) are added to the
[artwork inventory](../artwork/manifest.json), which the Git guard enforces.

## Stage

[build-item-icons.py](../scripts/build-item-icons.py) is a bounded patch on the
memory-fixes candidate, in blank ROM `0x1FE0000..0x1FEFFFF` (11,509 bytes):

- The 85 icons are packed into one native icon container (the game's `05318`
  decoder format).
- The equipment icon draw pointer (literal `0CB984`) now goes to
  [item-icons.c](../src/engine/item-icons.c). This previously pointed to the art
  stage's generated-axe dispatcher.
- Item IDs overlap quest-item icon IDs, so the new dispatcher keeps the
  established caller gate. The six equipment draw callers and the shared shop
  in mode 4 draw the weapon's own icon; every other caller, mode and ID
  delegates to the previous dispatcher.
- The palette selector is unchanged. Every icon was drawn in its donor's native
  bank, and the build checks that bank against the selector data.

Held weapons in battle still use the family donor resources (and the axes'
generated resource). Those are separate native consumers with frames and
attachment data, as the draft checkpoint notes.

## Evidence

- [test-item-icons.py](../scripts/test-item-icons.py), 92 checks:
  - only the reservation and the pointer differ;
  - the container decodes to every approved icon;
  - native calls at 9 draw contexts × IDs 0–460: the 85 weapons draw their own
    icon at equipment callers and in shop mode 4, and all other draws,
    including quest icons, match the parent byte for byte;
  - the generic icon API (all native icons) and the palette selector are
    unchanged.

  The harness also checks ABI, stack and destination bounds.
- [test-item-icons-ui.py](../scripts/test-item-icons-ui.py), real core, every
  item owned once:
  - all eight Sell tabs of the Sprohm shop and the party Item List are scrolled
    to their ends;
  - each approved icon's exact pixels are searched for in VRAM after every step;
  - all 85 appear in both lists.
- The final ROM reruns the memory-fixes and game-pass real-core checks.
