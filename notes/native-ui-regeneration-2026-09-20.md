# Native UI art regeneration: approval round 2

The previous portrait workflow asked for a general 64x64 image, then fitted it
again inside 44x54. That was the wrong design target: the extra reduction could
damage faces and headgear. This round generates ten new portraits for a 48x56
content area and ten independent head icons for the badge's 16x14 head window.
The whole worksheet is sampled once and the fixed cell extracted; no subsequent
bounding-box fitting, hand-painted corrections or generated pixel patterns.

## Review

- [Complete single-page review](../build/art/job-art-approval-v2-2026-09-20/index.html)
- [Generation and palette evidence](../build/art/job-art-approval-v2-2026-09-20/regeneration-proof.json)
- [Native-palette contact sheet](../build/art/native-ui-regeneration-v2-2026-09-20/native-review-contact.png)
- [Original build export evidence](../build/art/job-art-approval-v2-2026-09-20/export-proof.json)

All proposals await user approval. The Bangaa Dark Knight's blue cloth is
intentional and is generated behind the helmet. The Samurai's muted-scarf actor
remains unchanged. The review uses Codex browser annotations, with no custom
annotation controls or storage. Those controls were also removed from the
round-one page template and rebuilt local page.

The page retains every existing animation and ordered keyframe: 675 distinct
poses, 796 populated land/water sequences, 3025 draw records, 1116 control records
and 884 unused slots. Every job includes moved, attack and job-wheel screenshots;
the full equipment, mixed-class battle and cold-Continue screenshots are included.
These screenshots and all animation pixels are explicitly the previous build,
not evidence that the new portraits/icons have been imported.

## Inputs and generation

Each worksheet supplies four original jobs of the same race, plus an approved
actor reference anchoring the third column. The concept is supplied separately.
Icon calls also receive the existing native badge palette. Original tall portrait
references are normalized for the reference worksheet only; they are not the
new character base. New character costume and headgear come from the approved
concept. Built-in imagegen generated every new portrait and icon independently.

The tool exposes prompt and references, but not a model version, seed or exact
raster-output dimensions. Its large output is sampled to the logical worksheet
grid, then the prescribed 48x56 or 16x14 cell is extracted. This is an explicit
generation target, not a claim that imagegen emits a pixel-perfect native file.

The initial blank-third-column worksheet led to misplaced output and was
preserved as a rejected attempt. The actor anchor improved placement. The Moogle
Bard portrait still appeared in the middle bottom cell; that complete 48x56 cell
was extracted instead, without fitting or repositioning. The first Mystic Knight
icon painted a checkerboard; it was regenerated with explicit true transparency.
All attempts and prompts remain preserved locally.

Portrait conversion chooses among the four referenced original portrait palettes
by color error, using only their existing 47 opaque colors. Icons use the existing
15 opaque badge colors. Both generated samples and converted versions are shown
for visual judgment. Native palette compliance does not establish color approval.
Badge previews insert only the new head into the fixed head window, retaining
the existing labels/frame and eligible/ineligible palette interpretation.

## Reproduction

Source recipes and immutable receipts:

- [Reference preparation](../scripts/prepare-native-ui-regeneration.py)
- [Fixed-cell ingest](../scripts/ingest-native-ui-regeneration.py)
- [Complete page builder](../scripts/build-art-approval-round2.py)
- [Page template](../scripts/art-approval-round2.html.txt)
- [Generation plan](../src/art/native-ui-review/plan.json)
- [Output receipts](../src/art/native-ui-review/results.json)
- [Rejected attempts](../src/art/native-ui-review/rejected-attempts.json)
- [First worksheet plan](../src/art/native-ui-review/rejected-layout-plan.json)

Preparation refuses to overwrite references once generated files exist. Invoke
built-in imagegen with each preserved prompt and the listed reference paths.
Keep every raw output; populate `generated-paths.json` in the generation folder.
The recorded Moogle Bard crop and the corrected Mystic Knight icon prompt must
be retained. Then run `scripts/ingest-native-ui-regeneration.py` and
`scripts/build-art-approval-round2.py` with the configured Python runtime. The
builder uses the prior complete review and final-integration screenshot evidence.
Raw art, game data and generated page artifacts stay ignored by Git.

## Verification and limits

The builder checks all 20 target dimensions, indexed palette bounds, source
hashes, unchanged badge pixels outside the head window, all page image paths,
and equality of the complete animation inventory with round one. JavaScript
syntax was checked with Node. The final native-palette contact sheet was visually
inspected. Browser navigation to local review files was denied by its security
policy, so live browser layout verification was unavailable; no alternate server
or browser was used to work around that block.

No game build or runtime tests were needed: this is an offline art proposal and
review-page change. ROM `316a40524b960c49ad7213ac4b0bea539bfa9513`, native palette
banks, animation data and player saves are unchanged. Final native UI import and
new in-game screenshots must follow user visual approval.
