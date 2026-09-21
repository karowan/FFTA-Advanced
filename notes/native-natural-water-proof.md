# Original water-map rendering and movement proof — September 17, 2026

The previous goal turn (`7c6f3a3`) made concrete progress on native three-pose
idle import. This continuation closes a different bounded technical gap: the
earlier water test used a dry Giza map with one synthetic water flag. The new
fixture renders original map92 with its complete unmodified water geometry.
No additional artwork was generated and no packaged or player ROM was changed.

## Declared scenario

`scripts/natural_water_fixture.py` copies the clean original map92's complete
88-byte record into the existing encounter's map70 record. All component offsets
remain relative to the original map table, so native loaders consume the original
graphics, arrangement, clipping, palette, animation and heights. The rest of each
fixture ROM is byte-identical to its parent. This is the existing encounter shell
on original map92 terrain, not acceptance of map92's campaign mission.

Original map92 has ten natural water cells. The declared movement is dry bank
(5,5), height7, to water (6,5), height6. No terrain flags are written. A deterministic
starting formation places units on distinct original dry cells before movement;
the game then performs Move, submerged height selection and B cancellation.
Viking reaches world position (208,80,176), resource261, and returns to
(176,112,176), resource260. Named story identities remain fixed; four recruited
generic bodies are included in the display checks.

The test compares the pre-action-art parent `d1241edec039980c665a84071250fd08837024ce`
with assembled preview `a6d883b5d7657f10c3eb6d9b8407c489d287dbc7`.
Actual fixture hashes are respectively
`06a3a55ead66281e15f3d07545aa175de4316296` and
`70965333fb70b7f0a334a9c1f4f7dd55a0cda542`.
The per-case fixture manifests record the map-record replacement and hashes;
the outer report's ROM SHA identifies the parent candidate, not its patched fixture.

## Acceptance and retained failures

Declared final runner `20260918T005145.507140Z` passed:

- `test-native-pending-display`:16 controls. Report
  `build/art/pending-display/20260918T005146.122329Z/report.json`.
- `test-generated-natural-water`:7,889 checks. Report
  `build/art/generated-actions/battle/20260918T005146.290735Z/report.json`.

The runtime compares the complete native-loaded height grid, arrangement and
clipping with authenticated original map92, verifies generated body uploads and
native allocation bounds during movement, observes water and land resources,
preserves the entire original terrain after cancellation, and verifies matching
gameplay outcomes, unchanged inventory/AP/preferences/status and retired action
roots. Actual water and return screenshots were retained; the water view was
visually inspected against the separately decoded original map.

First runner `20260918T004801.020209Z` failed before emulation because the clean
rebuilt base directory has no world fixture. The test now explicitly uses the
assembled manifest's declared original fixture source, with existing ROM/state/
route authentication. This was a test-path correction, not a game fix.

Second runner `20260918T004832.058546Z` completed both movement/cancel scenarios
and7,887 checks, then failed one rendering assertion. Its immutable report is
`build/art/generated-actions/battle/20260918T004832.698616Z/failed.json`, SHA256
`c2c346249a0787db0aa549e0373759b0572a0ffefded435a1e22892990e28591`.
The unchanged original Judge resource102 retained a front image during a pending
facing upload across two8-frame sample intervals. All640 visible bytes exactly
matched the directly verified preceding native frame, and the next sample
directly displayed the new frame. This was not corruption in the generated body.

The new `pending_from_anchor` helper permits at most16 video frames from a
directly verified image, requiring pending flags and exact whole-allocation bytes
and identity. Live playback discards an anchor after a failed observation. It
never promotes an inferred hold into a fresh direct anchor. Controls reject bad
pixels, missing flags/anchor, inferred anchors, altered resource/tile/allocation
and ages outside the strict bound. Retained raw evidence independently proves
the visible640 bytes; full-allocation history is proved during the final live run,
not inferred from an earlier capture that was not saved. Existing single-sample
acceptance behavior is unchanged for other test modes.

## Reproduction and limits

```powershell
& '.\Test Expansion.ps1' -Plan scripts/native-art-test-plan.json -Only test-native-pending-display,test-generated-natural-water
```

Do not rerun unchanged passes merely to recover context. The complete logs,
fixture ROMs, screenshots and failed reports are private under build/art.

This closes one original-water-map graphics/geometry and Viking transition proof.
It does not establish the original map92 mission, every class/action in water,
custom actor palettes, complete animation or production artwork. Existing native
all-resource format checks remain useful but have their original narrower scope.
The packaged a6d883b5 preview and its immutable guide/manifest remain unchanged;
this note supplements that package's older water coverage. All G gates stay open.
No external models, agents, publication, game launch or player-save writes.
