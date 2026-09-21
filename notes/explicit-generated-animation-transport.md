# Explicit generated animation transport

September 17, 2026 local; report timestamps below are September 18 UTC.
This checkpoint extends the existing technical importer, not production art
acceptance. Built-in imagegen remains the only active artwork source.

## Result

`generated_action_transport.build(animation_plan=...)` now assigns exact source
sheet cells to individual native sequence frames, including shared idle/march
slots. The default build remains byte-exact. Partial plans leave unmapped
temporary animations explicit; complete plans must cover every present land and
water slot for their declared jobs. Neither coverage level accepts artwork.

The source plan is `src/art/imagegen/samurai-walk-transport.json`. It authenticates
the existing unaccepted imagegen walk-v2 PNG, SHA-256
`217025f421ecbab9897ee42c2cf36a18fb575a894bed08e394e72b222d897303`, converts
directly into the native palette, and maps Samurai land slots 0 through 3.
Native timing, commands, parameters and frame baselines are retained. No pixels
were drawn by code and no external provider was used.

Private action-stage ROM: `a860ad38cc1ee4b09e1de544266cc183524bd310`, resolved
through `build/art/generated-actions/mapped-walk-current.json`. Comparison:
`de09bc0f8a567b93c4ed5b899a7c7a71f3fe0aa3`; pre-action parent:
`d1241edec039980c665a84071250fd08837024ce`. The mapped stage uses 120,508 bytes
and includes 772 sequences. Packaged preview `a6d883b5` and private idle proof
`352df0a6` remain unchanged. No launch, publication or player-file mutation.

## Native behavior and verification corrections

Actual recruited Human Samurai movement uses mode 3 and manually advances its
shared idle/march sequence. Requiring modes 4 through 7 was an incorrect test
assumption. Both paired runs contain 605 observations, including 62 verified
interpolated movement samples. The parent displays two distinct payloads there;
the mapped candidate displays four. Move goes from world position (48,32,432)
to (144,32,432); B cancel restores the first position. Final owned data and
active-unit identity are exact between the two runs.

Native function `08021E28` sets index, clears the timer and sets current to
first + 20*index. Flag 0x100 bypasses timer countdown. The shared frame oracle
now recognizes that exact manual phase only when native tile/layout sources
and uploaded pixels match. Nine controls include actual ARM execution and
rejection of altered flags, timer, current entry, source, layout and pixels.

Native constructor `08021618` can briefly clear the live layout and set the
tile source to -1 while previous pixels remain displayed. A separate bounded
helper requires a direct anchor no older than four video frames, exact native
sequence/layout identity, unchanged full allocation and enabled hardware OAM.
It labels this as retained display, never a configured/new upload. Flag 0x167
is admitted only at index zero/current first. Nineteen controls cover this
signature. Only the new walking test uses this reset helper.

The declared fixture uses an existing recruited Human with a katana-only loadout
and the canonical Giza formation. Equipment was simplified during diagnosis;
there is no evidence that equipment caused the mode-selection observation.

## Passing evidence

All runtime was invoked through `Test Expansion.ps1` and the declared native-art
plan. No broad integration suite was justified or run for this localized change.

| Test ID | Runner | Result / private report |
| --- | --- | --- |
| test-walk-layout-transition | 20260918T010746.895218Z | 17 observed frames; build/art/walk-layout-transition/20260918T010747.527654Z/report.json; diagnostic only |
| test-walk-layout-retained | 20260918T011701.129418Z | 19 controls passed; build/art/walk-layout-retained/20260918T011701.675109Z/report.json |
| test-manual-animation-frame | 20260918T012155.226692Z | 9 passed; build/art/manual-animation-frame/20260918T012155.845541Z/report.json |
| test-explicit-animation-plan | 20260918T012155.226692Z | 10,641 passed; build/art/animation-plan-tests/20260918T012155.959569Z/report.json |
| test-explicit-animation-walk | 20260918T012253.207560Z | 3,649 passed; build/art/explicit-walk/20260918T012253.808073Z/report.json |

The plan test verifies default byte equality, all unassigned decoded pixels/OAM,
native commands/metadata, eight native mode getters, exact PNG-to-ROM rebuild,
and rejection of false completeness, duplicate/unknown slots, missing frames,
out-of-sheet cells, unknown assets and wrong source hashes. An earlier two-slot
plan passed 10,625 checks in runner 20260918T010422.630180Z; its private candidate
`6f6c4d96` was superseded by the four-slot mapping.

## Retained failures

- 20260918T010504.458253Z: parent layout absent at move-168. Report:
  build/art/explicit-walk/20260918T010505.036658Z/failed.json. A 17-frame native
  replay established the brief reset and exact retained display.
- 20260918T011048.843195Z: complete Move/cancel failed the incorrect requirement
  to observe a dedicated walk-mode number. Report:
  build/art/explicit-walk/20260918T011049.524293Z/failed.json.
- 20260918T011358.030662Z: reset oracle omitted the native manual constructor
  variant at move-20. Report:
  build/art/explicit-walk/20260918T011358.620069Z/failed.json.
- 20260918T011701.129418Z: manual phase 3 was uploaded at move-92 but the oracle
  expected phase 2. Report:
  build/art/explicit-walk/20260918T011701.829752Z/failed.json. Native function
  execution and strict negative controls support the correction.

These are retained failed runs, not retrospectively passing reports.

## Visual review and remaining scope

Inspected the actual `mapped-move-90.png` capture in the passing walk directory.
The new Samurai is visibly oversized relative to original characters. Costume,
sheath and phase consistency remain unaccepted. The transport result establishes
exact generated frames in the game, not good artwork.

This stage is not assembled or packaged. The existing separately playable
technical preview remains the delivery. Full action/direction/water coverage,
production sprite quality and independent actor palette allocation remain open;
no G01-G04 gate closes here. Use this proven explicit importer for subsequent
imagegen refinements, rather than repeat the same transport proof. Keep native
consumer evidence distinct from final art acceptance.
