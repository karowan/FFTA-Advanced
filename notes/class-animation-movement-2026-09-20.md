# Class movement animation review

Current costume correction: the original Samurai concept has CHARCOAL trousers
and a TEAL WAIST SCARF. The v2-v4 descriptions of teal trousers below document
an assistant mistake and rejected iterations, not the intended design. Every
future imagegen revision must include the approved original concept itself.

The user approved the Human Dark Knight FFT base v2 provisionally and resumed
animation generation for all ten classes. This checkpoint contains front and
rear walking drafts for every class: 10 retained front bases, 48 newly generated
poses, and two reused Samurai front steps. There are 60 body crops, ten movement
sheets and twenty animated previews. No ROM or runtime graphics were changed.

## Local review assets

- [Animation gallery](../build/art/approved-class-animation-2026-09-19/index.html)
- [Combined animation preview](../build/art/approved-class-animation-2026-09-19/all-unit-walk.gif)
- [All poses](../build/art/approved-class-animation-2026-09-19/all-unit-movement.png)
- [Exact prompts and provenance](../src/art/race-study/animation-generation-v1.json)
- [Assembly procedure](../scripts/assemble-class-animation.py)

The dated output folder retains the session's original September 19 name;
this batch finished on September 20. Generated and original reference images
remain local and ignored by Git. The folder name refers to approved character
designs; the animation drafts themselves have not received user approval.

## Repeatable process

1. Resolve the selected base revision, record its hash, and retain that front
   neutral crop without repainting it. Human Dark Knight uses FFT base v2.
2. Extract the same target animation phase from four original jobs of that race.
   Preserve source pose IDs, frame commands and durations. Human references are
   actors 0, 2, 5 and 7, not Ninja.
3. Put the neutral references above their target poses in a five-column worksheet.
   Place the approved class at top right and its neutral placeholder below.
4. Supply both that worksheet and an isolated enlarged costume image to built-in
   imagegen. Ask it to replace the bottom-right character with the demonstrated
   pose, keeping the costume from the isolated reference. Keep prompts short.
5. Generate rear neutral separately. Check facing and costume before using it
   as the reference for each individual rear step.
6. When a pose remains too close to neutral, describe the visible movement:
   wide feet with bent knees versus narrow crossing feet and swinging arms.
   Preserve failures and their prompts before regenerating. Do not repair art
   with code or composite exposed-face pixels over closed helmets.
7. Recover the worksheet's logical 160 by 96 grid using nearest-neighbor sampling,
   check the full target strip for overflow, then crop the 32 by 32 body once.
   Keep generated colors for design review; final shared-palette conversion is
   a separate, still-unaccepted step.
8. Assemble native-order loops and review the full sequence as well as static
   frames. Compare against original source references, since imagegen redraws
   the worksheet neighbors too.

Tool: built-in imagegen. Its model version and other settings are not exposed.
Early poses used a single worksheet. Costume drift prompted the two-image
procedure; per-pose metadata preserves the actual inputs and prompts rather
than rewriting the history to imply every image used the newer process.

## Pose mapping and preview timing

| View | Native reference slot | Phase 0 | Phase 1 | Phase 2 |
| --- | --- | --- | --- | --- |
| Front three-quarter | 0 | Step A | Neutral | Step B |
| Rear three-quarter | 1 | Step A | Neutral | Step B |

Sequence: 0, 1, 2, 1; durations: 16, 8, 16, 8 ticks. GIF previews approximate
these at an assumed 60 ticks per second, rounded to GIF centiseconds. Both
authored views point toward screen-left. Other directions and other slots have
not been silently substituted with mirrored images.

The manifest inventories all 84 slots of one original reference actor per unit.
That is a reference inventory, not coverage of the final expansion's consumers.
Slots 2 and 3, for example, must be inspected separately rather than assumed
identical to 0 and 1. Null/control/repeated entries are not 84 distinct drawings.

## Review and limits

Initial failures copied donor costumes, pointed a rear view the wrong way, or
kept neutral legs. Those images and prompts were retained. The isolated costume
input reduced donor copying. Explicit limb instructions improved the Dancer
and Geomancer steps. The final review is a draft review, not aesthetic approval:
minor head/outline/color changes remain between separately generated frames;
some armored silhouettes have subtle pose separation. Dancer front step A also
has a small green accent inherited from a reference that needs color cleanup.
Rear armor orientation, especially Bangaa Dark Knight, needs user review.

These crops do not guarantee pixel-for-pixel native anatomy retention. They are
not final 15-opaque-color palettes. Attack, casting, damage, incapacitation,
special actions, water variants, miniatures, portraits, weapons and effects
remain unfinished. Native import and party/opposing palette acceptance have
not been attempted. A local GIF is not in-game animation evidence.

## Reproduction and validation

Use Python with Pillow from the repository root:

```powershell
python scripts/assemble-class-animation.py templates
# For each requested pose: invoke built-in imagegen with its saved prompt and
# input paths, inspect it, and copy the result to the manifest's source path.
python scripts/assemble-class-animation.py assemble --slug <unit> --pose <pose>
python scripts/assemble-class-animation.py gallery
python scripts/validate-class-animation.py
git diff --check
python scripts/check-git-content.py
```

`prepare` initializes a new manifest only; it refuses to overwrite existing
provenance. `templates` resumes pending poses without changing ready/generated
entries. Revised anchors require explicit regeneration of their dependent
worksheets; hash checks prevent silently using a different anchor.

Validation checks retained-base hashes, generated source/output hashes, native
reference hashes, input hashes where recorded, 32 by 32 crops, distinct image
data within each three-pose cycle, GIF frame counts/timing, sheets, and gallery
links. Evidence is saved beside the local assets. These checks verify packaging
and provenance, not whether an animation looks natural. Game builds and runtime
tests are not applicable to this art-only checkpoint.

Checkpoint results: packaging validation passed for 10 units, 50 generated pose
records, 60 body crops, 331 authenticated file/hash pairs and 30 gallery links.
All five links in this checkpoint resolved. `git diff --check` passed and the
Git content guard passed for the existing index (1410 source/document files).
No commit, staging operation, remote publication or runtime run was performed.

## User-reported consistency corrections

The user identified changing pants colors in Human Samurai's front loop and
changing head size in Nu Mou Chemist's rear loop. Both defects were visible in
the original cropped frames. The two Samurai front steps and two Chemist rear
steps were revised individually with imagegen; the neutral frames were retained.
This replaces the two reused Samurai pilot steps in the active movement set.

Each input places the unchanged neutral at left and the existing step at right,
with a short correction specific to pants colors or head/hood size. The logical
worksheet is 96 by 48, enlarged with nearest-neighbor sampling. Assembly recovers
that grid and crops [64,8,96,40]. Code performs conversion and presentation only.
The manifest retains old generation metadata under `previousGeneration`, old
crops under `*-before-consistency.png`, and separate v2 source images, prompts,
input hashes and conversion settings. Original native references remain provenance,
not inputs to these focused edits.

- [Before/after loops](../build/art/approved-class-animation-2026-09-19/consistency-review.html)
- [Revised frame comparison](../build/art/approved-class-animation-2026-09-19/consistency-after.png)
- [Correction preparation and review script](../scripts/prepare-animation-consistency.py)

The revised frames keep the Samurai pants teal and reduce the Chemist's large
head/hood silhouette changes. Small pixel and shading differences remain; this
is a revised animation draft awaiting user review, not a claim of pixel-identical
anatomy or final palette acceptance. Both sequences retain three distinct poses.
The gallery uses new revision filenames for the affected GIFs to avoid stale
cached previews. Other unit art and all neutral anchors were left unchanged.

Reproduction: run `python scripts/prepare-animation-consistency.py` once on the
original movement manifest, generate each of its four queued edits, and assemble
each pose with the existing command. To resume, use the saved manifest rather
than rerunning preparation. Then run:

```powershell
python scripts/assemble-class-animation.py gallery
python scripts/prepare-animation-consistency.py --review
python scripts/validate-class-animation.py
```

Revised packaging validation passed: 10 units, 50 generated pose records, 60 body
crops, 332 authenticated file/hash pairs, and 30 gallery links. These checks do
not assess appearance or establish in-game integration.

### Samurai stride restoration (v3)

The user rejected Samurai v2's reduced movement. Its full neutral-body reference
had pulled both steps toward a standing pose. For v3, each original step is the
edit target, enlarged on its unchanged square canvas. The second image is only
a fabric crop from neutral at [15,21,18,26], enlarged without interpolation.
Built-in imagegen received the short color-only prompt preserved in the manifest;
no full neutral-body reference was supplied. `--restore-stride` prepares these
inputs and archives v2 crops and metadata; normal assembly recovers the original
32 by 32 canvas. No programmed recoloring or silhouette repair was applied.

Visual comparison shows the original bent leg, wide stride, and arm positions
retained, with teal fabric replacing the pale gray-blue shift. Alpha-silhouette
comparison against the original steps found zero changed pixels in A and one
in B, with identical bounding boxes for both. This measures outline retention,
not exact interior-pixel equality or user approval. The neutral was unchanged.
The comparison page now includes original, v2, and v3 Samurai loops, with the
original frame order and timing. The Chemist revision is unchanged.

Packaging validation passed with 335 authenticated file/hash pairs, 60 body
crops and 30 gallery links. Other action coverage and native-integration limits
still apply. Source images, earlier attempts and prompts remain preserved.

### Samurai forward-leg equipment (v4)

The user observed that v3's forward leg became fully blue. The missing detail
was equipment continuity: red thigh armor and the gold/pale footwear disappeared
into teal cloth. Only front step B was revised with built-in imagegen. The input
was its existing v3 pose plus the neutral lower-costume crop [8,18,24,31]. The
prompt requests red outer thigh panels on both legs, gold ankle bands, and
off-white toe caps while retaining the wide stride, foot positions and upper
body. The exact prompt and two input hashes are in the generation manifest.

`python scripts/prepare-animation-consistency.py --restore-equipment` prepares
the inputs once and archives v3; normal assembly and gallery commands rebuild
the preview. The revised crop retains the [8,3,24,31] bounding box and visually
keeps the separated feet while restoring red armor and contrasting footwear.
This is a targeted draft correction, not a claim of pixel-identical interior
detail. Step A, neutral, and all other unit drawings are unchanged. The main
gallery uses a new v4 GIF filename; earlier revision pages and GIFs are retained.

### Original-concept correction (v5)

The user supplied the original concept again and clarified that teal is the
scarf, not the trousers. Audit: the base-sprite manifest records the crescent
concept illustration as an input, but movement generation used sprite-derived
references; v2-v4 corrections did not include the original illustration. The
assistant's incorrect garment identification compounded that omission.

Both front steps were revised with the full user-supplied original concept as
an actual imagegen input. Its local copy and hash are recorded as the unit's
`costumeAuthority`. Prompts now distinguish charcoal trousers from separate
teal scarf tails. Step A required three initial attempts: the first two changed
the pose too much; a later refinement was also rejected. Step B's first result
removed the ground shadow; the retained refinement restores more of it using
the prior pose, corrected material reference, and original concept together.
All attempts, exact prompts, inputs and hashes remain in the manifest history.

The corrected drafts show charcoal leg fabric and separate teal cloth. The
tucked-foot/wide-step distinction remains, but face/chest/shoe pixels and the
ground shadow still vary between frames. These are not accepted finished
animations. The unchanged neutral remains the base reference. The original
concept is shown beside the revised loop for direct review. Other units and
rear frames were not revised by this targeted correction.

`--restore-concept` prepares the initial two-input corrections. For the retained
step-B refinement, replay the saved per-pose `imageInputs` in order with its
saved prompt; then use normal assembly, gallery, and review commands. No manual
pixel repairs, programmed recoloring, or head/limb compositing were performed.

### Exact face reuse (v6, explicitly authorized)

The user reported skin-color and eye-shape changes. A new face-only imagegen
attempt again redrew the face/body and was rejected. The assistant requested
permission to copy the approved face pixels mechanically; the user replied
"yes do whatever you need to". This supersedes the imagegen-only restriction
for this specific repair. The rejected imagegen prompt, inputs and source hash
remain in `src/art/race-study/samurai-face-correction-v6.json`.

`python scripts/apply-samurai-face-reuse.py` copies the neutral face rectangle
[10,8,18,14] into step A at [10,8] and step B at [10,9]. These are exact RGBA
copies without blending, recoloring, scaling or new pixel designs. The one-pixel
offset preserves B's existing head bob. Each step changes 46 pixels inside the
48-pixel region. Verification proves the face region equals neutral and zero
pixels outside it changed. Earlier crops and full generation history remain
preserved. Re-running the script verifies instead of overwriting the archives;
ordinary assembly also respects the saved correction recipe.

Preview inspection found that independent GIF palettes changed some neutral
face colors despite identical PNG face pixels. The preview exporter now uses
a shared palette with exact indices for the protected face colors. Validation
decodes all four animation frames and compares their aligned face RGB bytes to
the approved neutral; all match. PNG pose/artwork outside the face stays unchanged.

- [Face-corrected loop](../build/art/approved-class-animation-2026-09-19/human-samurai/front-walk-consistency-v6.gif)
- [Review page](../build/art/approved-class-animation-2026-09-19/samurai-face-review-v6.html)
- [Authorization, recipe and checks](../src/art/race-study/samurai-face-correction-v6.json)

Movement packaging validation passes for 60 crops, 337 authenticated file/hash
pairs and 30 gallery links, including the new source/output and decoded-GIF face
checks. This resolves face-region identity; it does not claim other costume,
helmet, footwear or ground-shadow differences have been eliminated, nor native
palette/in-game acceptance. No runtime testing or ROM change was needed.
