# Samurai lower helmet detail, round seven

[Complete review page](../build/art/job-art-approval-v7-2026-09-20/index.html).
The user requested removal of the small lower helmet projections pointing
inward toward the Samurai badge's chin. This is a localized built-in imagegen
edit using the previous head in a row with four clean native Human references.
That first row attempt left the tips and added an unwanted edge. A focused
single-head model edit then removed them. Sampling the entire 16x14 canvas and
converting to the existing native palette changes exactly three indices from
purple to yellow: `(5,9)`, `(12,9)` and `(6,10)`. Every other head pixel matches
round six. No registration or rescaling beyond the declared grid sampling.
The full review retains every portrait, badge, animation and ordered keyframe.
User approval remains pending; the new head is not imported into the game.

Use [the round-seven script](../scripts/revise-ui-art-round7.py) with `prepare`
only for a fresh plan, then built-in imagegen with its exact prompt/reference.
Store the generation receipt and declared strip crop in `generated-paths.json`;
run `ingest`, then `build`. Raw generations and private native references remain
ignored in the local build folders. The source record retains prompts, hashes,
native palette choices and technical conversion settings. The tool manages the
model version and seed. No manually drawn replacement pixels or new palettes.
The final receipt overrides the initial row prompt and uses `focused-target.png`.
Rejected row receipts/results and the focused prompt are retained separately.

Source records: [plan](../src/art/native-ui-review/round7/plan.json),
[generation receipt](../src/art/native-ui-review/round7/generated-paths.json),
[results](../src/art/native-ui-review/round7/results.json), and
[native verification](../src/art/native-ui-review/round7/verification.json).

The builder checks all unchanged portrait/icon images against round six,
preserves the entire animation inventory, verifies native colors and shared
facial anchors, and checks the whole inner eye region for extra dark pixels.
Passed: those checks, exactly-three-pixel difference, 19 unaffected surfaces,
1,711 linked assets, unchanged 675 poses and 796 sequences, page JavaScript syntax,
and source document links. The final native before/after was visually inspected.
No ROM/runtime change is involved. Game screenshots still represent the
previous assembled build. Codex browser annotations are the only annotation
mechanism. Live browser layout QA remains unavailable after the earlier local
file-navigation restriction; no alternate browser route is used.

## Frame enlargement

The same round-seven page now includes a Sprite size selector (128, 192, 256 or
384 display pixels for each 64x64 frame image). Clicking a frame, or pressing
Enter/Space while it is focused, opens a still close-up at 4x through 16x its
source dimensions. Escape or Close returns to the review. Pixelated rendering
retains hard edges, and the selected side and mirror state carry into the
close-up. These are inspection controls, not an annotation system.

[The shared injector](../scripts/art_review_zoom.py) loads
[styles](../scripts/art-review-zoom.css.txt) and
[interaction code](../scripts/art-review-zoom.js.txt). Both reusable review builders
apply it, so future art rebuilds preserve the feature. To update an existing
page, pass its index.html path to the injector. JavaScript syntax and unchanged
embedded review data were checked. No artwork regeneration or game test is
needed for these display-only controls; live browser QA remains unavailable.
