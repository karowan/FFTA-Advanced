# Working native-art pipeline

This is the reproduction guide for the user-approved first pass, integrated in
commit `94b9907`. It explains the decisions that worked, the constraints behind
the conversions, and how to repeat the process without reviving rejected art.
The acceptance record is [approved-round8.json](approved-round8.json), not the
newest file in a generation directory. Future revisions need their own receipt.

The assembled ROM is `f53fedb8421f48fd10faabf60700a5d7ed60ddf8`; its parent is
`316a40524b960c49ad7213ac4b0bea539bfa9513`. See the
[integration checkpoint](../../../notes/approved-first-pass-integration-2026-09-20.md)
for the actual test run and local evidence. This is first-pass visual approval,
not a guarantee of final polish or full campaign coverage.

## 1. Separate creation, conversion, approval and import

1. Start from a new class design. Original FFTA jobs supply style, anatomy,
   proportions and animation references; they are not costume bases to recolor.
2. Prepare references for the specific consumer: battle actor, portrait, badge
   head or job-wheel miniature. Include the approved concept, clean same-race
   native references, exact logical dimensions and existing native colors.
3. Use image generation for new artwork and visual corrections. Preserve the
   exact prompt, reference hashes, raw output, tool/model identity and settings
   actually exposed by the tool. Do not invent an underlying model version.
4. Convert the prescribed grid into native indexed pixels. Save raw generation,
   sampled image and indexed result separately. Record every crop, sampling
   choice and registration transform. Code handles transport and validation;
   it does not draw replacement costume/face pixels.
5. Review the indexed result at native size, enlarged without smoothing, and
   beside the previous accepted version. Approve these exact pixels before
   propagating a new color treatment across a class.
6. Freeze the approval by file hash, then import those files without a second
   aesthetic conversion. Inspect the final assembled ROM's actual consumers.

Generated files, screenshots, ROMs and saves stay ignored. Source receipts and
procedures are committed. Receipts point to private local inputs: a fresh clone
alone cannot regenerate the approved pixels, and rerunning image generation is
not a deterministic reconstruction of a prior output.

## 2. Design for the native consumer

| Consumer | Reviewed area / storage | Important constraint |
| --- | --- | --- |
| Class body pose | 32 x 32, 4bpp, 512 bytes | Index 0 transparent; 15 opaque choices from the selected native palette |
| Portrait | 48 x 56 reviewed, inside 64 x 64 8bpp transport | Preserve framing and readable face before import; use the original 48-entry portrait palette |
| Equipment head | 16 x 14 within a 32 x 16 badge | Front-facing; shared facial anchors; native frame and lettering |
| Job-wheel miniature | 32 x 40, 20 tiles, 640 bytes | Preserve existing archive and bright/dim palette routing |

These consumers have different palettes and layouts. A body PNG or menu badge
does not prove portrait, weapon, effect or status integration. Do not reuse a
portrait palette ID as a body selector or treat these formats as interchangeable.

## 3. Native colors and material consistency

Native palette selection is a class/side property, not a race-wide limitation.
Use only existing native palette words and existing selection properties. Never
introduce custom banks, palette ownership, runtime remapping or allocation.
Read colors from the authenticated ROM, including the actual ally/enemy or
bright/dim interpretation. The conversion used here expands each RGB555 channel
with `channel * 255 // 31`; compare against that same representation in validators.

The initial independent nearest-color conversion was technically valid but
visually poor: dull reds, red skin and merged scarf/face colors. The useful
sequence was to compare RGB555, OKLab and neutral conversions, or generate a
revision with a native swatch reference, then choose the exact native-size base.
Numerical color error is diagnostic; it cannot approve readability or materials.

Accepted decisions:

- Human Dark Knight: approved native base, then calibrated color transfer from
  the aligned source/base pair. See
  [study-approved-native-transfer.py](../../../scripts/study-approved-native-transfer.py)
  and the [transfer checkpoint](../../../notes/native-color-transfer-2026-09-20.md).
  That study uses OKLab neighbors weighted by inverse distance; repeated source
  samples retain their observed native-index frequency. Its selected conversion
  receipt, not a new automatic fit, identifies the imported result.
- Samurai: restore the approved palette-1 neutral conversion with the muted
  scarf. White and yellow scarf experiments were not the final choice.
  [prepare-approved-human-native-colors.py](../../../scripts/prepare-approved-human-native-colors.py)
  requires the base to reproduce exactly and retains the previously imported
  Dark Knight sources instead of mutable study intermediates.
- Freeze established source-RGB-to-index assignments across poses. Supplemental
  generated references may supply missing action-only colors, such as water,
  without replacing approved base assignments.
- Palette-selector edits need an exact allowlist and verified parent bytes.
  The earlier body import selected Bard/Dancer ally 1, enemy 0 and Mystic Knight
  ally 0, enemy 1. These body properties are separate from the later badge donor
  change described below. Native palette payloads stay unchanged.

Sharing a palette does **not** stop a generator from turning a sleeve into skin
or changing the color of trousers between frames. Compare each material across
the entire cycle with accepted front/rear neutral poses kept immutable.

### Cover every animation, not just a walking sheet

[prepare-reviewed-actions.py](../../../scripts/prepare-reviewed-actions.py)
inventories actual native drawing records before generation. Keep the resource,
land/water lifetime, sequence slot and record index for every use of a drawing.
Command-only records do not require invented artwork. Deduplicate drawings while
retaining all their uses; counting occupied sequence slots alone cannot establish
complete pose coverage. The checked-in per-class catalogs are indexed by
[full-animation-v1.index.json](../race-study/full-animation-v1.index.json).

Use the original action pose as an anatomy, facing and gesture reference beside
the accepted new front/rear design and costume concept. Generate the new class
at the prescribed cell size. Preserve the original command durations and events
when transporting the resulting drawing into the owned class resource. A missing
action represented by a repeated idle image is a placeholder, not completion;
historical scaffold scripts retain such records and must not be mistaken for the
final accepted art catalog.

Record native baseline and horizontal registration explicitly. In the existing
action workflow, [register-reviewed-actions.py](../../../scripts/register-reviewed-actions.py)
recalculates registration from preserved worksheets without changing artwork
pixels. Review attachment/contact positions in actual actions, especially held
weapons and water poses. Do not bake another held weapon into the body or treat
the review page's canvas padding as sprite data.

[record-reviewed-action.py](../../../scripts/record-reviewed-action.py) records
an agent's visual inspection against exact source bytes. That is distinct from
user approval, native palette acceptance and runtime verification. The final
round8 page and approval receipt connect those stages for this first pass.

### The successful Samurai walking correction

[revise-samurai-walk-colors.py](../../../scripts/revise-samurai-walk-colors.py)
keeps the rejected combined-sheet attempt for evidence. The accepted route was
`ingest-individual`, using four separately generated edits against the same
neutral frames, costume concept and native swatches:

| Sequence | Ordered poses | Duration in native ticks |
| --- | --- | --- |
| Land 00, front walk | p000, p001, p002, p001 | 16, 8, 16, 8 |
| Land 01, rear walk | p003, p004, p005, p004 | 16, 8, 16, 8 |

Only p000, p002, p003 and p005 changed. p001/p004 remain byte-identical in their
index arrays. The final receipts are [round8/individual-paths.json](round8/individual-paths.json),
with prompts in [round8/individual-plan.json](round8/individual-plan.json).
The initial paths and sheet attempt are history, not alternative accepted inputs.
p005 includes a further helmet pass, recorded in [round8/helmet-retry.json](round8/helmet-retry.json).

The generator placed p002/p003 one logical row too high. Their explicit `(0,+1)`
registration is applied before quantization; there is no detected-bounds fit.
Nearest native-color selection excludes transparent index 0, then restores the
original opaque footprint and contact shadow. This is a color-only revision:
changing its silhouette would require a different review scope. The four changes
affected 22, 48, 53 and 78 indexed pixels respectively. The marked p005 arm region
has fewer pale pixels, but that local diagnostic is not a general skin detector.

`build` updates every review occurrence of these pose IDs, preserving sequence
records, timings and all other art. The 64 x 64 review image places the 32 x 32
body at `(16,12)`; import the body image, not the surrounding review canvas.
The review draft's hash of unpacked indices differs from a ROM tile hash:
`tileSha256` must hash the packed 512-byte 4bpp payload.

## 4. Portraits and common badge anchors

Fitting pre-existing large concept art into a portrait produced poor results.
The successful process generated for the 48 x 56 portrait and 16 x 14 head from
the outset. [prepare-native-ui-regeneration.py](../../../scripts/prepare-native-ui-regeneration.py)
prepares same-race references and target worksheets;
[ingest-native-ui-regeneration.py](../../../scripts/ingest-native-ui-regeneration.py)
samples the declared logical grid once, extracts the exact cell, removes the
connected flat background and maps to existing palette candidates. It does not
shrink the extracted portrait again to fit its opaque bounding box.

For badges, clean native-decoded originals were better geometry references than
dimmed or stippled equipment screenshots. The first sprite-based badge remains
an identity comparison. The later useful generation worksheet places original
race heads beside the target in a common row; all new heads face forward.

[revise-ui-art-round4.py](../../../scripts/revise-ui-art-round4.py) derives anchors
from indexed pixels that agree across four original heads inside a recorded
face region. The contract is specific to those references and that region,
not a universal race mask. The conversion restores only those documented common
native pixels. Job-specific headgear remains generated artwork. Preserve the
source job IDs, crop, coordinate list and any later conversion-anchor override
in the receipt rather than reconstructing them from this prose.

Closed helmets use landmark validation instead of copying exposed face pixels.
For the Human Dark Knight badge, the accepted check places gold index 7 in
columns 7 and 10, rows 7 and 8. It checks the generated result; it does not paint
eyes. Inspect the whole inner face as well: sparse matching anchors previously
left additional eye-like clusters. Portrait faces use their own checks and
must never receive the tiny badge mask.

Specific successful review decisions:

- Dark Knight portrait: two simple matching golden rounded eyes in black
  darkness; no realistic pupils, skin, nose or third eye. Area sampling at the
  declared native size preserved the rounded shapes better than point sampling.
  This was a recorded choice, not a global switch to smoothing every sprite.
- Viera Mystic Knight portrait: readable eyes and a distinct small mouth, checked
  after native conversion, not just in the large generation.
- Bangaa Dark Knight: blue cloth is intentional and emerges behind the helmet.
- Samurai badge: compact helmet around a balanced frontal face; final revision
  removes the inward lower helmet tips while preserving the shared face.
- Human Dark Knight badge: centered symmetrical helmet, then slightly widened
  while preserving eye spacing. The trailing blue cloth may be asymmetric.
- Viera badges: Dancer uses short hair, hoop jewelry and a wine-red collar;
  Mystic Knight uses long hair, angular gold/metal ornament and armored collar.
  Recognizable differences at 16 x 14 matter more than decorative detail.

Rounds [4](round4/results.json), [5](round5/results.json),
[6](round6/results.json) and [7](round7/results.json) retain exact transformations
and generation provenance. Recorded registrations may correct a known worksheet
displacement, but must not become an unrecorded adaptive fit. Keep unsuccessful
rows and retries. Never manually repair the eyes or draw code-defined costume art.

## 5. One complete approval page

Keep all ten jobs together, including portraits, eligible/ineligible badges,
wheel figures, every populated land/water sequence, ordered keyframes and unused
slots. Repeated poses remain in sequence order. Native control records are shown
but are not simulated by the page; unknown actions retain their sequence IDs.
The accepted catalog contains 675 distinct poses, 796 populated sequences,
3,025 draw records and 1,116 control records.

Put focused before/after comparisons at the top while retaining the full catalog.
Label raw generation, sampled image, native conversion, proposal and actual ROM
capture separately. A proposal replacing an image on the page is not yet an
import. Historical screenshots must retain their previous-build labels.

[art_review_zoom.py](../../../scripts/art_review_zoom.py) adds integer-scale
sprite sizes and a click/keyboard close-up with a frozen selected frame. Preserve
side, mirroring, source image and stable pose/record IDs when enlarging. The user
annotates with Codex's integrated browser comments; do not implement note fields,
approval forms, local storage or an annotation-export system in the page.

## 6. Exact approved-pixel import

[import-approved-round8.py](../../../scripts/import-approved-round8.py) is a
bounded importer for this specific receipt and parent, not a generic latest-art
scanner. Authenticate the receipt's review, parent manifest, parent ROM and every
input file before mutation. It applies 35 bounded data patches: ten portraits,
ten two-byte portrait palette selectors, ten badges, four walking payloads and
one native badge-donor byte. Every other ROM byte must remain unchanged.

### Portrait transport

The approved indexed PNG stays 48 x 56 with indices below 48. Compare its palette
against the selected original portrait palette. Shift opaque indices by 96;
index 0 remains transparent. Thus opaque pixels occupy OBJ indices 97..143,
within the native palette window 96..143. Flip the source horizontally, then
place it at `(8,8)` in a 64 x 64 image. The flip compensates the native menu OAM
flip; it is not an artistic change of facing. Pack 8bpp and encode using the
existing archive format, requiring the payload to fit the authenticated slot.

The job record's two selectors at `record + 14` use the chosen original palette
ID; the portrait index at `record + 13` stays unchanged. IDs for jobs 116..125
are `10,16,22,22,50,50,68,70,62,58`. All three native color-mode archives retain
their original palette bytes. No palette payload is imported.

### Badge and body transport

Badge heads occupy `(1,1)` through the exclusive endpoint `(17,15)` in the native
32 x 16 badge. During review composition, transparent head pixels become native
UI background index 3. Keep the native frame and game-rendered lettering outside
that region. The final importer packs the whole approved badge into 256 bytes.

Dancer's existing icon donor changes from job 29 to 30, selecting the same native
plum bank as Mystic Knight. The importer requires the unique expected donor table
at `0x11064b0` and changes only its byte at `0x11064b8`; the source table in
[job-wheel.c](../../engine/job-wheel.c) must agree. These addresses belong to this
authenticated parent and are not safe assumptions for another build. Eligible
and ineligible colors still come from the original equipment renderer.

The four walk PNGs are packed directly into their authenticated 512-byte slots.
No animation timing, control, geometry descriptor or executable code changes.
Archive immutable output by ROM hash and fail if an existing archive differs.
Do not edit an old receipt or silently overwrite an accepted candidate to make
a later revision pass. Several scripts serialize module docstrings into evidence;
prefer ordinary comments for documentation-only edits to those modules.

## 7. Validate affected consumers, then package

With the ignored authenticated inputs and local dependencies present, run from
the repository root. `$fftaPython` must name a Python installation with the
project's dependencies; on this machine the bundled runtime is shown below.

```powershell
. ./scripts/resolve-python.ps1
$fftaPython = (Resolve-FftaPython)
& $fftaPython scripts/import-approved-round8.py
& '.\Test Expansion.ps1' -Plan scripts/approved-art-test-plan.json -Suite approved-art
# Substitute the successful report path returned by the preceding command.
& $fftaPython scripts/package-approved-art.py --run '<passed-run-report.json>'
```

Before a runtime run, identify affected behavior and test IDs. The above plan
covers this import's eight steps:

| Test ID | Evidence needed |
| --- | --- |
| test-approved-import | Exact approved pixels, native decoder/routing, three palette modes and patch boundaries |
| test-approved-contract | All 675 poses, assembled native contract, unchanged palette payloads and code |
| test-approved-entry | Authenticated disposable battle entry for this candidate |
| test-approved-menus | All ten portraits, actual uploads, native OAM placement, wheel coexistence and named-character controls |
| test-approved-equipment | Inventory/shop renderer, both pages, eligibility and unrelated-data preservation |
| test-approved-inventory-ui | Actual inventory display, paging and approved head tiles reaching VRAM |
| test-approved-shop-ui | Actual shop display, paging and approved head tiles reaching VRAM |
| test-approved-fight-116 | Revised Samurai movement and native attack |

Use declared deterministic scenarios, never player saves or improvised gameplay.
Retain ROM hash, inputs, complete logs and failures. Successful structural checks
do not approve aesthetics: inspect current screenshots and native pixels too.
The accepted run included 815 menu and 3,787 equipment checks and 14 new captures.
The packager authenticates **every component report's ROM hash**. The generic
runner's top-level engine hash can name an unrelated default ROM and is not
sufficient evidence for an explicitly selected art candidate.

The graphics-only import reused previous save/water/mixed-class evidence with
its original scope. It did not establish new full-campaign coverage. Broaden
tests when changed lifetimes or observed failures require it, not merely because
the ROM hash changed. Documentation-only changes require link/format validation
and the Git content guard, not a ROM rebuild or runtime suite.

[package-approved-art.py](../../../scripts/package-approved-art.py) stores the
new release separately, preserves the previous ROM, authenticates protected
save files before/after, and places fresh screenshots above the complete review.
Both sprite releases intentionally use `saves/native-art-final-2026-09-20/` and
the basename `FFTA_Reviewed_All_Classes`; packaging does not copy, replace or
import that save. Vanilla and other expansion saves remain separate. Do not run
both sprite releases concurrently against the shared save.

## Source map and continuing work

- [PARALLEL-IMPLEMENTATION.md](../../../PARALLEL-IMPLEMENTATION.md): reusable project procedure and earlier implementation context.
- [ART-TEAM-CONSTRAINTS.md](../../../ART-TEAM-CONSTRAINTS.md): earlier engineering consumer constraints; its provisional portrait fitting is superseded by the exact 48 x 56 process above.
- [approved-round8.json](approved-round8.json): exact accepted inputs and palette choices.
- [test-approved-round8.py](../../../scripts/test-approved-round8.py): inverse transport and native routing assertions.
- [approved-art-test-plan.json](../../../scripts/approved-art-test-plan.json): declared consumer checks.

For a new round, copy the workflow into a new dated output and receipt, preserve
the current accepted fallback, and review the smallest coherent change alongside
the full catalog. Do not blindly rerun historical `prepare`/`ingest` commands:
some intentionally refuse to replace prior plans, and some retain rejected
experiments. Read their receipt and chosen mode first. Script comments added
later explain the process; historical evidence retains the source hashes and
raw assets from its original run and should not be regenerated just to match
new documentation.
