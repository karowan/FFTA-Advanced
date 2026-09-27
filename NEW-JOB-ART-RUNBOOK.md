# New job art: executable runbook

Start here when adding a class. This replaces the assumption that a long prompt
plus a resize can reproduce the accepted classes. The reliable part is the
reference construction, fixed geometry, exact native conversion, recorded
retries and approval boundaries. Image generation itself is not deterministic:
no prompt guarantees good artwork. This runbook makes failures visible and
recoverable before they spread to dozens of poses.

**September 27 correction:** the Physician animation pass failed visual review
for distorted proportions and frame-to-frame positioning. Palette, provenance,
canvas-size and coverage checks passed but did not test anatomy. The four
approved neutral bases remain approved; the action proposals are not accepted.
Follow the fixed-coordinate reference audit at Gate 4 before further generation.
The previous action preparer is now historical-replay-only.

Worked example: [Physician and Sapper checkpoint](notes/chemist-job-art-2026-09-26.md).
The [source receipt](src/art/new-job-review/chemist-base-2026-09-26.json)
preserves the actual prompts, references, conversions and separate base approval.
The [complete proposal receipt](src/art/new-job-review/chemist-proposals-2026-09-27.json)
records all chosen action revisions and the independent UI preparation, with
worked exact requests. Its status is awaiting animation/UI review, not approval.
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

### Required correction: measure original positions before generating

The old action worksheet is insufficient. `native_pose` in
`prepare-reviewed-actions.py` dynamically chooses a crop and, for some large
poses, fits the original into 32x32. It does not preserve one coordinate system
across every reference. Missing same-race actions were also substituted with
the canonical donor. Both operations remain in historical receipts; neither is
an acceptable basis for new positional constraints.

The rejected Physician walk did **not** use resized native references. Its
generated anatomy drifted even where the original reference crops were fixed.
Therefore removing resizing alone is not a fix. On a common nominal origin,
the p000 proposal occupies 20x22 pixels versus the original's 16x25; its bottom
edge is five pixels higher. The approved p001 occupies 17x26 versus 16x26.
Bounds include clothes and shadows, so this diagnoses extent/registration drift,
not a measured five-pixel foot displacement. Do not repair it by stretching the
finished image or cropping each frame to its silhouette.

Build the complete native reference atlas first:

```powershell
python scripts/audit-new-job-animation-anchors.py `
  --manifest build/art/chemist-job-art-2026-09-26/actions/actions.json `
  --selections build/art/chemist-job-art-2026-09-26/actions/selections.json `
  --out build/art/chemist-animation-anchors-2026-09-27
python scripts/test-animation-anchors.py `
  --atlas build/art/chemist-animation-anchors-2026-09-27
```

The reusable extractor currently accepts these two worked-job contracts. It
reads all eight original jobs per race from authenticated ROM job records. Its
`anchors.json` covers all 336 inherited slots: 150 populated sequences, 533
drawing records, 204 control records, 186 null slots and all 148 unique drawings.
Each populated record retains its original address, descriptor, command,
duration, parameters and actual source actor. Sapper actions can have different
canonical actors; never assume all action slots belong to one donor.

Use these distinct forms of evidence:

| Evidence | Meaning and permitted use |
| --- | --- |
| OAM origin `(0,0)` | Exact encoded registration, rendered at `(48,64)` on a 96x96 canvas; not a foot or ground joint |
| Object x/y, size, flip and tile | Exact native part placement; object rectangles are not anatomical segments |
| Occupied bounds and per-row spans | Exact silhouette extent including clothing, shadows and actor-contained effects |
| Shared pixel patches | Connected groups of at least two nontransparent palette-index matches, unanimous across at least three corresponding original jobs |
| Named face/hand/foot landmarks | Must be visually identified on the original pose; the ROM does not supply a named skeleton |

Native images use one fixed inspection crop `[16,8,80,72]`, without resampling.
The displayed origin is consequently `(32,56)`. A display enlargement uses
nearest-neighbor pixels and does not change stored geometry. Original images
and coordinate exports remain ignored; they must not enter the public artwork
inventory. No new palette or runtime registration system is introduced.

Cross-job comparisons require identical ordered duration/command/parameter
schedules before contributing shared patches. Missing actions stay empty; never
repeat the canonical donor in missing columns. Matching schedules are necessary
but do not prove matching anatomical pose. Inspect the original row. Patch IDs
are local to one frame: patch 1 in another frame is **not** automatically the
same eye or limb. Unanimous patches may be outlines or shadows. Where there is
no shared patch (23 drawing records in this audit), retain the exact canonical
pose and visibly mark the absence of cross-job landmark evidence.

Before the next generation pass:

1. Use the atlas to identify the visible face/eye or muzzle location, head/body
   connection, hand/contact locations, and supporting or airborne feet for each
   distinct pose. Record a landmark as occluded or unresolved instead of guessing.
   Store the source actor, record, coordinates, interpretation and review status.
   Shared-pixel extraction alone does not complete this semantic review.
2. Prepare each target on the same origin as the originals. Keep the approved
   new-job neutral as the identity reference, and the actual original action as
   the positional reference. Give wide/tall poses a larger fixed reference canvas
   rather than shrinking anatomy to 32x32. Native storage feasibility is a
   separate technical gate; a 64x64 reference export is not a new runtime format.
3. Preserve head proportions, facial landmarks and costume identity while
   changing only the parts that move. Ask imagegen for a visual revision if the
   anatomy drifts. Code may annotate reference diagrams, never draw new limbs,
   faces or corrective replacement pixels.
4. Review the complete front and rear walk/run cycles on the fixed grid before
   extending to every other action. Compare each output with the measured native
   pose and the approved new-job base. A palette/hash/size check cannot approve
   this gate, nor can a good neutral stand in for the moving frames.
5. For every later animation, retain the same positional evidence, ordered
   keyframes and original controls. Require explicit per-pose landmark review;
   do not silently propagate unreviewed geometry to the whole set again.

The atlas intentionally does not alter any generated art or ROM. The approved
bases remain immutable. Existing proposals are displayed at a **diagnostic**
placement (nominal crop `[32,28,64,60]` plus any recorded extraction translation),
not a claim that those files already have authenticated runtime registration.

### Fixed-origin revision workflow

The September 27 motion retry uses `prepare-anchored-job-revisions.py`. Each
128x128 logical worksheet contains four 64x64 cells: original neutral/action on
top, approved new neutral/target below. Each original is the atlas's unchanged
fixed-window export. The neutral is from the **same actor** as that action,
including inherited Sapper actions that use another native actor. The model
receives the worksheet, one matching approved view, and the native palette.
Supplying separate front **and** rear identity images caused the model to
rearrange some action requests into front/rear studies; those attempts are
preserved and excluded. More references were not automatically more useful.

```powershell
python scripts/prepare-anchored-job-revisions.py `
  --atlas build/art/chemist-animation-anchors-2026-09-27/anchors.json `
  --pose-notes build/art/my-reviewed-pose-notes.json `
  --out build/art/my-anchored-motion
```

`--pose-notes` is a reviewed JSON map keyed by job slug and pose ID. Each entry
can specify `note` (observed anatomical landmarks and occlusions), `identity`
(`front` or `back`, when a turn changes the visible view), and `blankTarget`.
This is a worked two-job preparer, not an automatic anatomical landmark detector.
Do not infer final facing from odd/even sequence numbers: the later frame of a
rear action can face front. The original action image is the authority.

Use the approved neutral as the editable target for small walk/run movements.
For collapsed poses and substantial turns, an empty target is often necessary:
an upright neutral can bias the generator into drawing a shortened standing or
kneeling character. Name where the head, torso and feet actually are. For the
Physician's face-down fall, the cap is the lower-left mass, the torso is above
and right, and the eyes are occluded. Merely asking for the correct bounds did
not produce that posture. Water frames must retain the native waterline and
occluded legs; airborne frames must not acquire a standing shadow.

Inspect the composed inputs before calling built-in imagegen with the recorded
prompt and ordered references. Generate one requested drawing, preserving the
whole worksheet. Conversion is a separate explicit operation:

```powershell
python scripts/convert-anchored-job-revision.py `
  --request build/art/my-anchored-motion/physician/p000-request.json `
  --source "<actual PNG path returned by imagegen>" --revision v1
```

The converter samples the whole grid once, extracts the declared bottom-right
cell, removes the connected backdrop, and maps to **existing palette indices
used by the approved base**. This prevents new material colors leaking into a
frame. It does not create a palette bank or change palette words. It preserves
the raw output and rejects clipping, wrong aspect, changed references/palette,
and reused result names. The 64x64 result is a review window, not an allocation
of new runtime graphics. Import still needs a native storage/layout proof.

Inspect every result against the original and the approved identity, then inspect
the full timed sequence. Bounds are a diagnostic, not a pass/fail anatomy score.
A frame may match all four bounds while retaining the wrong arm pose or shadow.
For a retry, preserve the old request and prepare a new one:

```powershell
python scripts/revise-anchored-job-request.py `
  --request build/art/my-anchored-motion/physician/p016-request.json `
  --revision v2 --blank-target --note "<specific observed pose correction>"
```

If inspection establishes correct anatomy but a uniform worksheet displacement,
the same helper accepts `--translation DX DY --source <exact raw PNG>`. This
records a source-hash-bound rigid translation and its required inspection reason.
Convert that request under a new revision. Translation never changes relative
pixel positions, colors or proportions, and clipping still fails. Do not use it
to disguise a changed height, tilted limb, misplaced head or wrong posture.

If a water or adjacent frame keeps reverting to an upright neutral, use a
reviewed related motion as the identity anchor. `--motion-anchor` accepts that
motion's conversion receipt. It pairs the original related pose with the exact
original target above, and the corresponding new pose with a blank target
below. For example, the Sapper's corrected land collapse anchored its water
collapse; the neighboring bowed water pose anchored its second ripple frame.
This transfers a small observed change without asking the model to solve the
entire fall again. The helper records the anchor receipt hash and keeps its
native reference, origin and palette consistent. It does not grant user approval
to the anchor or copy original-game pixels into the new character.

```powershell
python scripts/revise-anchored-job-request.py `
  --request build/art/my-anchored-motion/sapper/p070-request-v3.json `
  --revision v4 `
  --motion-anchor build/art/my-anchored-motion/sapper/p016-v3-receipt.json `
  --note "Keep the fallen head low and feet above; transfer the original submersion and ripples."
```

Inspect that worksheet before generating. A changed pose is still model-created
art and must be reviewed after native conversion. Do not confuse a matching
outer rectangle with matching anatomy or approve a frame solely from its receipt.

`choices.json` explicitly maps each job/pose to the chosen revision; `v1` is the
declared default, not a newest-file search. Approved neutral bases are copied
unchanged and checked separately. Build and validate the single review page:

```powershell
python scripts/review-anchored-job-revisions.py --out build/art/my-anchored-motion
python scripts/test-anchored-job-revisions.py --out build/art/my-anchored-motion --require-complete
```

The page retains every repeated drawing, duration and native control record,
with image enlargement and stepping. Missing drawings remain visibly pending;
incomplete sequences do not pretend to be complete players. The test checks
source/alpha/palette integrity, immutable bases, record order and page targets.
It does not approve anatomy, simulate native control commands or prove runtime
integration. Use Codex's own browser comments for art review.

1. Inventory the new job's actual land/water resource descriptors from its
   authenticated candidate. Adapt the extraction in
   [prepare-reviewed-actions.py](scripts/prepare-reviewed-actions.py); do not
   rerun its hardcoded old ten-class preparation against a new job.
2. Record every sequence slot, draw record, control record, duration, tile/OAM
   pointer and native use. Deduplicate identical drawings while retaining **all**
   uses. Empty slots remain identified. Commands without drawings need no invented
   image. Never report slot count as authored-pose coverage.
3. For each distinct drawing, use the fixed-origin worksheet above: matched
   original neutral/action on top, new neutral/target below. Use one appropriate
   identity view and the native palette; use a related motion anchor for stubborn
   changes as described above. Generate one
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

### Historical action preparation for Physician/Sapper

This recipe reproduces the rejected proposal process for provenance only. Do
not use it to prepare another generation batch. The CLI requires the explicit
historical flag; the fixed-coordinate audit above is the current entry point.

These two jobs have no allocated runtime graphics resources yet. Their authoring
inventory inherits the existing race Chemists' complete native land/water
requirements (68 Nu Mou and 80 Moogle drawings). This is an explicit provisional
authoring contract, not evidence that jobs 126/127 have runtime support. Reconcile
it against the eventual new-job resource tables before import.

```powershell
python scripts/prepare-new-job-actions.py `
  --historical-replay `
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

Inspect those fallbacks before sending the worksheet. Several Moogle jobs lack
the same action, so three apparent references can actually repeat a Black Mage.
That repeated pointed hat caused Sapper headgear drift even with a written
warning. For a focused revision, retain the authenticated reference column that
really implements the action and the approved new-job neutral column; leave the
other reference cells empty. Preserve the worksheet coordinates, original-sheet
hash and retained column in the request receipt. This is reference composition,
not hand-drawn replacement art. Use the approved native base as the identity
reference and describe the required cap, ears and goggles explicitly. Do not
silently change the already-generated request or copy the donor's costume.

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

### Worked UI preparation and review commands

The Physician/Sapper adapters are explicit contracts for these two jobs, not a
generic installer. `new-job-ui-art.py prepare` reads the approved base receipt,
authenticated original race portraits and head icons, and existing ROM palettes.
It prepares independent portrait and head requests. Generate each request with
its ordered references using imagegen, then ingest that exact returned file:

```powershell
python scripts/new-job-ui-art.py prepare --base-plan build/art/chemist-job-art-2026-09-26/base-plan.json --out build/art/chemist-job-art-2026-09-26/ui-new-round
python scripts/new-job-ui-art.py ingest --request build/art/chemist-job-art-2026-09-26/ui-new-round/physician/portrait-request.json --image RAW_IMAGE_PATH --revision v1
```

Use the request filenames actually emitted by preparation. Preserve each raw
attempt. A new revision must have a new ID; never overwrite a failed attempt.
Portraits have a 144×112 logical worksheet with a 48×56 target. Heads have an
80×14 worksheet: four authenticated original heads and a fifth target containing
only the bounded common face anchors. Original costume pixels are not a base.

The model sometimes pads a whole head worksheet vertically. If inspection
establishes the exact full-row rectangle, `ingest --worksheet-box L T R B
--registration-note "observed whole-row padding"` records that rectangle against
the immutable raw hash before the one logical-grid sample. This must include
the entire five-cell row. Do not fit the individual generated head by its bounds.
Opaque cream in a native head is also face/ear color: preserve it. Connected
background removal appropriate to a body or portrait can erase these features.

`prepare-new-job-menu.py` composes the separately generated head with existing
badge frames and the existing six-pixel UI lettering. It pads the exact approved
body indices vertically into the 32×40 wheel canvas; it does not redraw, resize
or requantize the character. The ineligible badge preview uses a preserved
native UI capture palette. That preview does not establish runtime eligibility
routing or a new palette ROM offset.

```powershell
python scripts/prepare-new-job-menu.py --base-plan build/art/chemist-job-art-2026-09-26/base-plan.json --ui-folder build/art/chemist-job-art-2026-09-26/ui-v2 --out build/art/chemist-job-art-2026-09-26/menu-new-round
python scripts/review-new-job-actions.py --manifest build/art/chemist-job-art-2026-09-26/actions/actions.json --selections build/art/chemist-job-art-2026-09-26/actions/selections.json --base-page build/art/chemist-job-art-2026-09-26/index.html --menu build/art/chemist-job-art-2026-09-26/menu/menu.json --output build/art/chemist-job-art-2026-09-26/review.html
```

The selection manifest explicitly maps each native pose ID to a native PNG path
and SHA-256. Approved neutral entries come from the approved base receipt; each
other selection is a proposal. Never select the newest filename implicitly.
The review shows every populated land/water sequence in original record order,
including repeated drawings and control records. Playback previews drawing
durations only; it does not simulate engine commands. Missing drawings remain
visibly pending and block a complete-coverage claim. Enlarge any image, stop a
preview and annotate with Codex's browser comments. No page-owned annotation
storage is needed.

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
| Concept skin/fine detail leaks into action | Order inputs as native worksheet, approved native design, native palette guide, concept; state that concept supplies costume information only |
| Turning pose faces the wrong way | Follow the actual bottom-row native frame, not sequence parity or the neutral reference; keep equipment on its anatomical side through the turn |
| Running sprite gains a standing shadow | Regenerate the airborne pose using native foot positions; do not erase the shadow by painting |
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
and wrong worksheet aspect ratios. It also replays both portraits and both head
icons against their saved hashes and checks rejection of unknown pose selections.
The review builder requires each selected pose to name its exact attempt and
hashed conversion receipt, then verifies the source, plan and native output.
It requires the private real inputs. A pass
proves those technical checks only; it does not approve a generated costume,
animation or in-game consumer.

If a complete action fits inside 32 pixels but is shifted vertically in the
worksheet, preserve the failed conversion and record `extractionCrop` plus
`registration.sourceSha256` and an inspection reason on that revision. The
converter permits a whole 32-pixel-cell vertical translation only; it never
shrinks the body to fit. Review the resulting contact point and carry the native
registration metadata into import. A drawing larger than the native cell needs
regeneration or an explicitly engineered native layout, not this exception.
