# New job art: executable runbook

Start here when adding a class. This replaces the assumption that a long prompt
plus a resize can reproduce the accepted classes. The reliable part is the
reference construction, fixed geometry, exact native conversion, recorded
retries and approval boundaries. Image generation itself is not deterministic:
no prompt guarantees good artwork. This runbook makes failures visible and
recoverable before they spread to dozens of poses.

Worked example: [Physician and Sapper checkpoint](notes/chemist-job-art-2026-09-26.md).
The [source receipt](src/art/new-job-review/chemist-base-2026-09-26.json)
preserves the actual prompts, references, conversions and separate base approval.
The user separately approved both concept directions and then both native
front/rear bases on September 26. Preserve the separate approval receipts; do
not infer native approval from a concept response in future jobs.
Historical integration details live in the
[accepted first-pass guide](src/art/native-ui-review/README.md).

## The sequence that actually worked

**Concept illustration -> same-race reference worksheet -> native front base ->
native rear base -> user approval -> individual movement/action drawings ->
independent portrait/head art -> complete review -> exact-pixel native import.**

For the original ten classes, a generated shared racial anatomy anchor sat in
the fifth slot beside four real native jobs. A separate illustration supplied
the new costume. The generator retained the worksheet's scale and pose; the
converter sampled the entire declared grid once and extracted the fifth cell.
Shared native facial pixels were preserved in technical conversion where
appropriate. Neither a full illustration shrunk to 32 pixels nor a recolored
original-job costume is a substitute for this process.

The September 26 restart reproduced this method for Physician and Sapper. The
first Sapper looked detailed at large size but lost its eye/goggle distinction
after conversion. A focused generation simplified the goggles, followed by
bounded shared-face preservation from four native race references. The failed
version remains beside the revision. That is a useful example of recovery, not
a reason to hide the intermediate image or call conversion a quality test.

## Gate 0 — Scope and inputs, before any generation

Record one job sheet with:

| Field | Required value |
| --- | --- |
| Identity | Label, race, job ID, gameplay role and equipment restrictions |
| Design | Three large visual identifiers; face visibility; silhouette; material/color roles |
| Source authority | Current design/spec and accepted parent build identity |
| Race references | Four authenticated originals in the same pose, plus existing generated anatomy anchor |
| Native formats | Body 32x32, portrait 48x56, head 16x14, miniature 32x40 |
| Palette | Existing bank selector, original ROM hash, offset and all 16 words; separately identify portrait/head palettes |
| Output | Fresh ignored dated directory, exact prompts, source hashes and revision IDs |
| Approval state | Concept / native base / poses / UI / import, each separate |

For this example Physician is Nu Mou job 126, a Chemist/White Mage progression
using staffs/maces. Sapper is Moogle job 127, a Chemist/Gadgeteer progression using
knives/maces, **no gun**. Their data-only implementation is not playable and does
not provide a finished graphics consumer. Art preparation must not enable the
job switch or write the current release as a side effect.

Read `AGENTS.md` and the actual current spec. Preserve unrelated working changes.
Use built-in imagegen by default. Code composes references, samples images,
maps existing colors, packs native formats and verifies; it does not hand-draw
replacement pixels. External inference requires the user's explicit request.

### Preflight

Run these read-only checks from the repo root, using the configured Python:

```powershell
git status --short
python -c "from PIL import Image; import numpy; print('image dependencies available')"
python scripts/prepare-new-job-reference.py --help
python scripts/new-job-art.py --help
```

The preparation helper requires the authenticated USA clean ROM at
`roms/clean/FFTA_US_clean.gba` (SHA1 `4ac05441f4de70a4ec3dd932116346c61b8783d9`),
the local `build/art/native-reference/actor-NNN/` exports, and the reference/anchor
files named by `src/art/race-study/approved-class-sprites-v1.json`. They are private
inputs, not guaranteed by a source clone. A missing file is an input-recovery
problem: recover the authenticated export or use the documented native exporter.
Do not replace it with an Internet thumbnail, new guessed crop, or rejected art.

## Gate 1 — Original costume concept

Inspect the original same-race illustration panel before calling imagegen.
For our example, the panels are under
`build/art/illustrated-class-concepts-v2-2026-09-19/references/`:
`ffta-race-nu-mou.jpg` and `ffta-race-moogle.jpg`.

Use one generation per class, not a mixed multi-character commission. Prompt:

> Design an original [race/job] full-body concept. Image 1 supplies FFTA racial
> anatomy, proportions, clean ink lines and flat shading. [Gameplay role and
> three large costume identifiers.] Use economical shapes that can become a
> 32x32 sprite. Keep [race-specific ears/muzzle/pom-pom/etc.] readable. One complete
> character, white or transparent background, no text. Do not copy/recolor a
> reference costume. [Explicit forbidden equipment.] This is an illustration
> for costume design, not the final sprite.

Save the exact sent prompt and reference SHA256s **before** the call. Copy the
returned PNG from the tool's reported path into the workspace; leave the cached
original intact. Record tool identity and model/settings actually exposed, not
an assumed internal model name. Inspect the result, then ask for concept approval.
The Physician/Sapper exact concept prompts are in their generation receipt.

Do not downsample this illustration into the battle sprite. It is a separate
reference supplied to the next generation. Large beautiful art is not native art.

## Gate 2 — Front base, exact worksheet and palette

The new preparation helper reconstructs the proven front worksheet from a
matching existing class's **reference metadata**, not its costume:

```powershell
python scripts/prepare-new-job-reference.py `
  --source-class nu-mou-chemist --label "Nu Mou Physician" `
  --concept build/art/chemist-job-art-2026-09-26/physician-concept.png `
  --palette 0 --out build/art/my-new-physician/front-request-v1
```

For Moogle use `--source-class moogle-chemist`; other examples are
`human-samurai`, `bangaa-viking`, `viera-dancer`. The source-class option selects
race reference records and a generated anatomy anchor. It does not copy that
class's design. Use a fresh output directory for a new request; the helper
refuses to overwrite an existing request.

Outputs:

- `worksheet.png`: four originals plus the generated racial anchor in slot five.
- `palette.png`: opaque colors 1..15 from the selected existing battle bank.
- `request.json`: exact suggested prompt, ordered input hashes, reference origins,
  grid/crop/strip coordinates, ROM identity and native palette words.

Inspect all three input images (worksheet, concept, swatches). Edit the prompt
in this **unsubmitted** request to name the job's three main costume cues and
material assignments, then freeze it. Do not tell the model to render fine straps,
embroidery or facial detail smaller than one logical pixel. In palette 0, for
example, Sapper's red concept pom-pom must become orange/gold: red is not available.
Show that difference in review rather than inventing a new bank.

Call built-in imagegen with `request.prompt` and the three `request.references`
paths **in order**. The tool is an agent operation, not a hidden Python API call.
Do not execute these preparation scripts expecting them to generate art.

The front geometry is fixed:

| Quantity | Value |
| --- | --- |
| Logical worksheet | 160x64 |
| Prepared enlargement | 1280x512, nearest neighbor |
| Target crop, exclusive right/bottom | [128,16,160,48] |
| Bounds-check strip | [128,0,160,64] |
| Body | 32x32 |

Register the returned tool image without overwriting an older attempt:

```powershell
python scripts/new-job-art.py register `
  --plan build/art/my-new-physician/base-plan.json `
  --request build/art/my-new-physician/front-request-v1/request.json `
  --image "<actual path returned by imagegen>" --id physician-front-v1
python scripts/new-job-art.py convert --plan build/art/my-new-physician/base-plan.json
```

`register` copies the raw image locally and authenticates the prepared inputs.
`convert` authenticates inputs again, checks aspect ratio, samples the whole
worksheet once, removes only the connected neutral backdrop, checks the complete
target strip before cropping, extracts 32x32, then maps opaque pixels to native
indices 1..15. Index 0 remains transparent. It saves sampled RGBA, indexed PNG,
12x enlargement and `conversion.json`. It refuses different pixels under an
existing result name. Retrying means a new request directory and asset ID.

The converter does not search for a convenient bounding box, recenter, stretch,
smooth or repaint the sprite. Its successful exit means **technical conversion**,
not approval. Inspect the native 32x32 PNG and nearest enlargement beside the
four originals: eye, muzzle, head size, body scale, feet baseline, ear/pom-pom
clearance, outline and each costume material must read correctly.

### Shared facial anchors: preserve anatomy, never invent repair pixels

The front generator receives a common anatomy anchor. If exact facial pixels
need preservation during conversion, the plan supports `sharedFace`:

```json
{
  "region": [10, 14, 17, 19],
  "references": [
    {"path": "<native reference PNG>", "sha256": "<verified hash>", "crop": [32,28,64,60]},
    {"path": "<second reference>", "sha256": "<verified hash>", "crop": [32,28,64,60]},
    {"path": "<third reference>", "sha256": "<verified hash>", "crop": [32,28,64,60]},
    {"path": "<fourth reference>", "sha256": "<verified hash>", "crop": [32,28,64,60]}
  ]
}
```

That region is the **Moogle front study's** bounded face region, not a universal
mask. Physician's corresponding region was `[9,12,16,17]`. Derive each contract
from inspected native references in the exact same registered pose. The script
finds only opaque pixels identical across all four, maps those native reference
colors into the selected native bank, and records before/after coordinates. It
fails if a face anchor falls outside the generated silhouette. Keep the unanchored
conversion as a separate asset, then copy its plan row to a new ID and add the
contract. Never add arbitrary coordinate/color lists as a replacement face.

Inspect the entire face after preservation: extra model-drawn eyes can survive
outside a sparse mask. A moved face or incompatible helmet requires regeneration,
not a larger patch. Closed helmets use their own generated eye-landmark checks,
not an exposed-skin mask. The common foreground mask from old scripts includes
shadows/body pixels too; do not apply it wholesale to a new costume.

## Gate 3 — Rear base and cross-view continuity

Prepare a two-row worksheet with the selected native front at top right and
matching native rear references across the bottom:

```powershell
python scripts/prepare-new-job-reference.py `
  --source-class nu-mou-chemist --label "Nu Mou Physician" `
  --concept build/art/chemist-job-art-2026-09-26/physician-concept.png `
  --front build/art/my-new-physician/physician-front-v1-native.png `
  --palette 0 --out build/art/my-new-physician/rear-request-v1
```

Use the actual selected front ID (including an anchored/revised ID if selected).
Inspect and send the request exactly as for the front. Generate **only the empty
bottom-right cell**, keeping the top-right front as the immutable design anchor.
Logical grid is 160x96, target `[128,56,160,88]`, bounds-check strip
`[128,48,160,96]`; the prepared worksheet is 1600x960. Register a new rear ID and
convert with the same plan/bank. The plan refuses mixing native palettes.

Check: no eyes on the back, no front goggle lenses on the back of a cap, correct
strap continuation, same anatomical bag/weapon side, same cap/ear height, same
cloth colors and readable tail/wings. Rear gear occlusion should make anatomical
sense; simply mirroring the front is not a rear design.

Present concept, raw/sample, native front/rear at 1x and integer zoom, original
reference rows, previous attempts and all provenance together. Use ordinary
images and Codex browser comments, not a custom annotation system. The supplied
`review` command rebuilds the Physician/Sapper page from its frozen example plan;
its current page labels/layout are specific to that two-job checkpoint. Do not
silently relabel it as a universal gallery generator for another class.

**Stop here for explicit approval of the exact native front/rear pixels and
palette.** Concept approval alone is insufficient. Record user wording and the
two file hashes, palette words/selector and material-color roles in a new receipt.
Only then propagate colors and identity across animations.

## Gate 4 — All animations, one drawing at a time

1. Inventory the new job's actual land/water resource descriptors from its
   authenticated candidate. Adapt the extraction in
   [prepare-reviewed-actions.py](scripts/prepare-reviewed-actions.py); do not
   rerun its hardcoded old ten-class preparation against a new job.
2. Record every sequence slot, draw record, control record, duration, tile/OAM
   pointer and native use. Deduplicate identical drawings while retaining **all**
   uses. Empty slots remain identified. Commands without drawings need no invented
   image. Never report slot count as authored-pose coverage.
3. For each distinct drawing, create the same two-row worksheet: accepted neutral
   design at top right, native pose/anatomy references below, empty target cell.
   Pass the isolated accepted front/rear and concept as references. Generate one
   target drawing per call. Start with walk steps; continue with all native action,
   hit, cast, incapacitated and water drawings actually in the inventory.
4. Preserve native pose shape, facing, contact baseline and command timing. Freeze
   material-to-index conversion from the approved bases. Compare sleeve, skin,
   pants, scarf and armor across the whole cycle. Sharing the palette alone does
   not guarantee consistent material assignment.
5. For color-only corrections, retain the original opaque footprint/contact
   shadow and immutable neutral poses. The successful Samurai example is
   [revise-samurai-walk-colors.py](scripts/revise-samurai-walk-colors.py): individual
   edits, explicit integer registration when required, then native conversion.
   Its combined-sheet attempt was rejected. Do not use that rejected mode as a
   production shortcut.
6. Preserve actual command order including repeated drawings. Show animated
   previews and every ordered keyframe with pose/sequence/record IDs, timings,
   side palettes, mirror inspection and frozen-frame enlargement. Explain any
   control commands the HTML player does not simulate.

A body sprite does not replace native held weapons or effects. Inspect hand/contact
positions in Fight and relevant ability playback; avoid drawing a duplicate held
weapon into the body. New Sapper trap/fuse effects are separate assets and runtime
consumers, not completed by its costume canisters.

### Worked action preparation for Physician/Sapper

These two jobs have no allocated runtime graphics resources yet. Their authoring
inventory inherits the existing race Chemists' complete native land/water
requirements (68 Nu Mou and 80 Moogle drawings). This is an explicit provisional
authoring contract, not evidence that jobs 126/127 have runtime support. Reconcile
it against the eventual new-job resource tables before import.

```powershell
python scripts/prepare-new-job-actions.py `
  --plan build/art/chemist-job-art-2026-09-26/base-plan.json `
  --approval build/art/chemist-job-art-2026-09-26/base-approval.json `
  --out build/art/my-chemist-actions
```

The preparer authenticates the approved pixels and original reference images,
then produces one `pNNN-request.json` and worksheet per required new drawing.
Only the two exact neutral poses per job are fulfilled by the base approval.
Every other drawing remains `pending-generation`; a request file is not art.
Inspect each worksheet, send that request's exact prompt and ordered references
to built-in imagegen, and register its actual output with `new-job-art.py` as
shown at Gate 2. Keep separate conversion plans for each job. Use a new revision
ID for a failed drawing, and explicitly select the inspected version afterward.

The preparer currently implements these two worked jobs. A different job needs
an explicit source-class/race/animation contract rather than editing IDs by
guesswork. Inherited attack variants may need extra same-race references; each
fallback to the actual native drawing is recorded. Never claim this inheritance
implements a new class's runtime animations.

## Gate 5 — Portrait, head, badge and wheel independently

| Asset | Generate against | Acceptance check |
| --- | --- | --- |
| Portrait | Original same-race portraits + concept, designed directly for 48x56 | Clear mouth/eyes, silhouette fits, selected existing portrait palette |
| Head | Four clean original 16x14 heads + generated concept/base identity | Frontal, common face/eye positions, recognizable headgear at 1x |
| Badge | Approved head inside existing 32x16 frame | Native lettering unchanged; eligible/ineligible palettes both reviewed |
| Wheel | Exact approved native base, native 32x40 transport | Correct baseline and original bright/dim routing in actual menu |

Never crop the concept portrait out of the large illustration or simply shrink
the whole body into an equipment head. Generate those consumers deliberately.
The portrait eye failure that looked like a plus and a rectangle was addressed
with a targeted generated revision and documented area sampling at the same
48x56 size; do not apply smoothing indiscriminately to body sprites.

The earlier accepted UI scripts are examples with frozen ten-job IDs and paths,
not general new-job installers: `prepare-native-ui-regeneration.py`,
`revise-ui-art-round4.py`, `verify-ui-anchor-review.py` and subsequent round
receipts. Create a new plan with this job's actual palette and routing records.
Restore only authenticated common face pixels, and check the full eye region for
duplicates. Never copy a source job's whole portrait or costume into the new job.

## Gate 6 — Final review and import

Freeze a source receipt listing exact approved body/UI image hashes and their
native palette selections. Show all consumers and complete pose coverage on a
single page. A static mockup, preview-side PNG swap or clean palette audit is not
evidence those pixels reached the game.

The old [import-approved-round8.py](scripts/import-approved-round8.py) proves the
transport pattern, but its parent hash, addresses, reservations, job limits and
35-patch allowlist are **specific to that build**. Do not append job 126/127 to it
or disable its assertions. Add a new source-reproducible stage to the current
build chain after the new job has real graphics consumers. Authenticate parent,
owned bounds, native routing and unchanged unrelated data.

Native transport contracts to preserve:

- Body: 32x32, 4bpp, 512 packed bytes; index 0 transparent, existing palette words.
  `tileSha256` hashes packed tiles, not an unpacked index array or PNG file.
- Portrait: exact approved 48x56 at `(8,8)` in 64x64 8bpp transport; preserve 0,
  shift opaque source indices by 96, invert the existing native menu horizontal
  flip. Confirm the current consumer still uses that OAM convention. Select
  original portrait palettes; do not overwrite shared palette payloads.
- Head: 16x14 at `(1,1)` in 32x16; transparent head background uses the native
  UI background index during composition. Preserve frame/lettering outside it.
- Wheel: 32x40 and original bright/dim interpretation. Body palette selection and
  badge donor selection are different properties; do not confuse them.

Declare the changed consumers and exact test IDs before running deterministic
checks through `Test Expansion.ps1`. Validate actual uploads, palette routing,
menu coexistence, inventory/shop eligibility, movement/attack and the relevant
new effects. Match each component report to the candidate ROM hash. Inspect the
final assembled captures, because later stages can overwrite earlier art.
Use current release packaging, not a hardcoded historical launcher. Never use
player saves as test fixtures or publish without authorization.

## Failure recovery: do this instead of improvising

| Failure | Required response |
| --- | --- |
| Missing/mismatched reference | Recover authenticated input; never substitute an approximate picture |
| Output aspect/grid changed | Reject or record a reviewed layout correction; do not auto-fit |
| Ear/hat/pom-pom outside target | Regenerate at correct scale; strip check must fail before crop |
| Face vanished after conversion | Compare sampled vs indexed; simplify via imagegen, then inspect bounded native anchors |
| Duplicate eyes after anchors | Regenerate alignment; inspect full face, not only matching coordinates |
| Muddy or wrong material color | Compare existing bank choices or regenerate with native swatches; no new palette |
| Color changes between poses | Hold neutral reference fixed; revise each affected drawing; inspect whole cycle |
| Model changes anatomy with costume | Stronger same-race worksheet and shared landmarks; do not paint a repair |
| Same focused issue survives two retries | Preserve failures, show native comparisons, ask for design tradeoff; no endless hidden retries |
| Large source looks good, 32px looks bad | Reject native result; the large source is not the acceptance view |
| Shape is fixed only by manual/code pixels | Stop that approach; creation/revision must come from imagegen |
| New class has no graphics routing | Keep draft art separate; finish consumer engineering before import claims |

## Receipts and handoff checklist

Each generation record needs exact prompt, ordered input hashes, local raw output
hash, tool/model/settings, revision ID and reason. Each conversion needs logical
grid, crop/strip, sampling, alpha handling, any declared registration, selected
native palette words/offset, anchor sources/region/changed coordinates, output
hashes and actual review state. Keep generated worksheet edits to references out
of the accepted target export; compare against authenticated originals instead.

Each checkpoint says which gate is complete, what the user approved, exact
selected files, rejected alternatives, remaining consumers and next command.
Never use one ambiguous `approved` flag for concept, source inspection, native
color approval and runtime acceptance.

Commit scripts, runbook and textual provenance after syntax/link/format checks
and `scripts/check-git-content.py` against the index. Project-generated images
may be committed only through the authenticated artwork inventory. Original
sprites, mixed worksheets, third-party panels, UI frames, screenshots, ROMs and
saves stay outside Git. Drafts here remain in ignored `build/art/` until an
explicitly reviewed inventory step. Do not stage unrelated gameplay work.

For docs or offline conversion changes, no game build or runtime suite is needed.
Verify the conversion against its real preserved inputs and inspect native images;
keep this evidence distinct from in-game tests.

The worked offline check is `python scripts/test-new-job-art.py`. It replays the
seven preserved base studies, compares every native output hash, and verifies
rejection of changed source hashes, altered native palette words, clipped bodies
and wrong worksheet aspect ratios. It requires the private real inputs. A pass
proves those technical checks only; it does not approve a generated costume,
animation or in-game consumer.

If a complete action fits inside 32 pixels but is shifted vertically in the
worksheet, preserve the failed conversion and record `extractionCrop` plus
`registration.sourceSha256` and an inspection reason on that revision. The
converter permits a whole 32-pixel-cell vertical translation only; it never
shrinks the body to fit. Review the resulting contact point and carry the native
registration metadata into import. A drawing larger than the native cell needs
regeneration or an explicitly engineered native layout, not this exception.
