> Historical placeholder-art checkpoint. See [the current overview](README.md) and [release workflow](MOD-RELEASE.md).

# Current full engineering art handoff

Read `ART-TEAM-CONSTRAINTS.md` and `notes/art-team-contract.json` first for the
complete current art-team limitations. The existing immutable bundle retains
its original documentation snapshot; these are supplementary handoff documents.

The full engineering candidate is a28b624bb13c8f2f2597a4d4bd3999b17c234b99.
Use Play Expansion.cmd after its package is delivered; see EXPANSION-PLAYER-GUIDE.md.
Only image quality and artist-authored poses are deferred. The historical desk
and replacement examples below describe7507ca5c; they remain useful source
references but do not identify the current renderer or prove its acceptance.

The current exact build recipe is notes/native-art-build-inputs.json. It pins
all original PNGs and conversion specifications. scripts/build-engineering-art.py
reconverts these sources, builds the separate class/menu/portrait/action and
weapon/effect consumers, completes native action slots, then performs native
shared-palette conversion. The final conversion removes runtime custom palette
ownership/remapping. Keep this last stage when replacing art: it resolves the
measured performance regression. Native timing and commands remain independent
of the temporary pictures and repeated poses.

For a later art pass, copy/version the desired source and conversion records,
update the per-class catalog or action plan, and review each affected consumer.
Record new input/component hashes in a new recipe after targeted acceptance;
the existing recipe deliberately rejects changes because it proves this release.
No new hook architecture is needed for same-format image or pose replacements.
Use the native shared-palette and consumer checks for the new candidate, rather
than interpreting the historical custom-palette desk as current acceptance.

The remainder preserves the earlier source desk and draft history.

# Working placeholders and the next art pass

The user deferred final sprite quality and artist-authored animation frames on
September18,2026, then clarified that the FULL engineering implementation remains
required. Only artwork may be a placeholder. The accessible replacement workflow
is complete, but it does not complete engineering acceptance. Rendering latency,
native action integration, capacity and final full-game acceptance remain tracked
in IMPLEMENTATION-CHECKLIST.md. G01-G04's visual-quality requirements remain
deferred; their engineering requirements are not waived.

## Use the build

Run **Play Art Pipeline Preview.cmd** from this project. The installed, tested
placeholder candidate is `7507ca5cb03c1db7a717fd6d21d97a9f5a4ae08b`. Its immutable
package includes the ROM, BPS patch, manifest and player guide. The launcher
keeps saves/states/screenshots in `saves/art-pipeline/<ROM SHA-1>/` and never
imports existing player saves. Preparing this handoff does not launch the game.

The ten new racial classes have generated battle/menu/portrait placeholders.
The equipment preview has a second L/R page with all ten jobs. Action slots
reuse poses and water uses crops; that is acceptable placeholder scope. Axes,
Tomahawk impact/projectile and two status icons have connected generated assets.
Other effects/weapon families retain their existing presentation. See
`ART-PIPELINE.md` for the measured gameplay coverage and remaining limitations.

## Locate exactly what is installed

Double-click **Review Placeholder Art.cmd** to refresh and open the private
art desk. `Prepare Art Pass.ps1` refreshes it without opening a browser. It reads
the immutable packaged candidate instead of a newer experiment, authenticates
the shipped files, 19 retained evidence reports and every source/conversion,
and produces these files in `build/art/placeholder-workbench/<ROM SHA-1>/`:

- `index.html`: ten-class gallery, each linked to its battle and menu source.
- `art-inventory.json`: exact source paths/hashes, resource IDs, conversion
  records, palettes, separate consumers and additional weapon/effect assets.
- `replacement-template.json`: one entry per job for the later art session.
- `battle-overrides.json`: a directly usable all-ten-job body-input manifest.

The desk is local and private. It does not publish, regenerate images, rebuild
the game or change a launcher/save. Body and menu sources can differ: the Human
Dark Knight's battle march uses a later source than its menu portrait. Samurai
v7/support refinements are also unshipped experiments, not the installed source.

## Replace artwork in a later session

1. Begin from the inventory and choose a class/consumer. Create a versioned new
   image with built-in imagegen, keeping its prompt and original output. Do not
   overwrite installed images, draw replacement pixels in code or recolor a
   native character. Original FFTA references are in `build/art/native-reference/`.
2. Convert a body sheet with `scripts/convert-generated-sprites.py`, specifying
   its actual rows/columns, common character height and resampling. For action
   sheets of the same character, use `--palette-file` and `--palette-sha256` from
   the retained class palette. Preserve 32x32 indexed frames and transparency;
   native timing and resource IDs should remain stable.
3. For a private body-only preview, use `samurai-v7-preview.json` as an override
   template. It selects source/conversion by hash and leaves the installed
   catalog unchanged. `samurai-support-v1-preview.json` demonstrates optional
   per-native-pose action assignments. `live_action_plan.py` preserves original
   commands and maps poses by authenticated native identity. The art desk's
   `battle-overrides.json` works for all ten jobs, including117. The no-change
   `test-placeholder-override-roundtrip` proves that this common interface
   reproduces the full installed ROM. Edit only the selected job's source and
   conversion paths/hashes in a versioned copy; no native hook changes are
   needed for an image replacement within the same format.
4. For a coordinated body/menu/portrait replacement, update that job's source,
   source hash and conversion entry in `src/art/imagegen/catalog.json`. Existing
   consumers are `generated_class_transport.py` (battle/miniature/eligibility),
   `generated_portrait_transport.py`, `generated_action_transport.py`, then
   `build-live-art-palette.py`. Refresh explicit parent pins when composing new
   assets; `rebuild-connected-art.py` intentionally proves the old ROM and is
   not a command that silently accepts changed art. Use `publish_current=False`
   until the new private candidate is reviewed and packaged.
5. Equipment/status/effect source records are separate JSONs under
   `src/art/imagegen/`; the inventory identifies their actual source/importer.
   A held axe derives from the equipment import; it is a separate native actor
   from the body. Do not assume a PNG swap updated every consumer.
6. Run narrowly affected checks through `Test Expansion.ps1` and the declared
   art plan. Preserve applicable passing evidence; avoid broad replay for an
   art-only change. Package a reviewed candidate with an independent save path.
   Keep the old immutable bundle available and leave player sessions alone.

The current sprite data can outgrow the live-palette reservation. The private
support draft has9,568 bytes left there. Existing action-art reservation
`0x1e9e000..0x1f80000` is925,696 unused FF bytes in the examined current chain.
That is a possible future data allocation, not an implemented spill area:
authenticate it and record ownership before using it. No engine redesign or
additional artwork generation is needed merely to play the shipped placeholders.

## Retained experiments

`09201aa` records the Samurai support-pose draft. Its import/native setter checks
pass, but the subsequent actual katana reference test stopped at strict body
display checks in two retained runs (`221837.301587Z` and `221952.770227Z`). The
first is the known native constructor retaining its old display; the second
stops at attack frame53 and is not diagnosed. These tests did not finish the
attack and do not establish that the game is broken or that the new animation
works. No ROM fix was made and neither draft replaced the installed package.
Preserve those records for the later animation session; do not pursue final-art
correctness as part of this placeholder handoff.
