> Historical record, archived September 21, 2026. For current guidance, see [the repository overview](../../README.md). Paths in code examples are relative to the repository root.

# Parallel job implementation

## Experimental art comparisons

The retained [provider-comparison tools](../../src/art/provider-comparison/README.md)
prepare requests and reference sheets offline, separately from the accepted
native-art workflow. They do not authorize external inference or accept generated
results as production art. Use the manifest's active request list rather than
older files retained in the same build directory.

## Release artifacts are the play source

[MOD-RELEASE.md](../../MOD-RELEASE.md) defines the current build/share/play workflow.
Build through the configured acceptance recipe and output an immutable BPS ZIP,
then atomically promote `build/releases/current.json`. The launcher reconstructs
the game from that exact ZIP plus the authenticated clean ROM, validates the
target hash and retains the existing save basename/directory. Never hardcode a
new target ROM/hash in a launcher or select a candidate by newest file time.
Keep private paths/evidence outside the share ZIP. Delivery-only changes use
the declared packaging/launcher checks and existing byte-identical gameplay
evidence. Explicit ARM7TDMI helper-stub requirements below still apply to code.

Maintain the standalone player overview in [MOD-README.md](../../MOD-README.md).
The release builder renders it as the ZIP's README, filling version and ROM
checksums from the accepted artifact. Cover the complete mod, progression,
controls, installation, saves and limitations there; reserve recipe release
notes/CHANGELOG for recent changes. Do not copy stale launcher paths or old
placeholder-art status from historical guides into a current player README.
Describe added or changed gameplay, not tutorials for unchanged base-game
mechanics or lists of unimplemented features. Retain concise prerequisite-table
keys, mod-specific restrictions, installation, update/save guidance and actual
limitations needed to use the release.
Treat fixes that restore base-game behavior as short changelog entries, not new
features or explanations in the overview. Keep packaging/test evidence in the
developer documentation and local receipts, not boilerplate in the player notes.

## Save-compatible menu hotfixes

The [job-visibility checkpoint](../../notes/job-visibility-fix-2026-09-20.md) documents
the current approved-art gameplay hotfix, discovery-byte/ROM reservations and
save compatibility. Compile bounded patches against an authenticated parent,
verify linked helper bodies, retain every unrelated byte, and use explicit Thumb
BX stubs for distant ARM7TDMI calls. A newer-CPU simulator can accept linker
veneers that fail on the GBA core; require the affected real-core menu/save check.
Preserve existing save basenames/directories and prior ROMs when packaging.
Use an in-game save and cold Continue across code updates, not an emulator state.

## Reproducing the accepted art workflow

The [working native-art pipeline](../../src/art/native-ui-review/README.md) documents
the successful process in detail: generation for exact native dimensions,
existing palette selection, shared face anchors, animation color consistency,
complete review pages, approval receipts, exact-pixel import and affected-consumer
verification. Start there for future artwork changes. It distinguishes accepted
inputs from retained failed experiments and explains why each conversion step
exists. The relevant conversion and import scripts also carry inline comments.

## Current assembled artwork checkpoint

The user approved the complete round8 page as a first pass and requested its
commit and game integration. The [approved first-pass integration checkpoint](../../notes/approved-first-pass-integration-2026-09-20.md)
records the exact approval receipt, playable package, targeted verification,
and current screenshots. All ten portraits and badges and four corrected Samurai
walking poses are imported; all675 poses and796 populated sequences are retained.
The Bangaa Dark Knight's blue cloth remains behind his helmet. The Samurai keeps
the selected muted scarf. Technical checks and primary-agent review do not
replace user visual approval for future revisions. Retain each generation
stage beside exact imported pixels and actual game crops. Show all badges and
every animation's ordered keyframes, including control records and unused slots.
Use Codex integrated browser annotations only; do not add page note fields,
approval dropdowns, local storage or note exports. Generate each portrait and
head icon for its intended native pixel area, using original jobs of its race
plus the approved concept. Sample the prescribed worksheet grid once; do not
shrink a generated portrait again to fit. Preserve prompts, references, raw
outputs and any explicit cell-layout deviation. Review the existing native
palette conversion separately before importing. This approved import selects
original native portrait palette IDs and the existing plum badge donor for
Dancer. It adds no palette payloads, banks, executable code or runtime palette
system. The existing native-art save is retained unchanged.

To import approved review pixels, freeze asset hashes in a source approval
receipt, authenticate the parent ROM, and use fixed native transport placement
without resampling. Execute the declared affected-consumer plan, authenticate
each component report's actual ROM hash, then package and validate both launchers.
Do not rely on the generic test runner's default engine-ROM field when testing
an explicitly selected art candidate. Keep historical screenshot comparisons
labeled separately from fresh captures of the packaged ROM.

Review pages include a Sprite size selector and keyboard-accessible frame
close-ups. Enlarge at integer pixel scales; hold the chosen animation frame
still in the close-up for Codex annotation. Preserve frame IDs and source images.
The shared `art_review_zoom.py` helper injects these controls into generated
pages and can update an existing page without rebuilding artwork.

For badge style references, use clean native-decoded job icons rather than
dimmed/stippled equipment-screen crops. Preserve the first sprite-based badge
as a comparison and identity reference. Check the fixed-grid native result:
eye separation, face/background contrast and recognizable headgear matter more
than apparent detail in the enlarged imagegen output. Preserve failed variants.

All equipment heads face directly forward. Derive explicit common facial pixels
from clean original race icons and retain them during native conversion; record
the source jobs and bounded face region. Generate job-specific costume around
those anchors in a shared reference row. Closed helmets use native eye-position
checks instead of exposed-skin masks. Preserve raw rows and record changed-cell
or letterboxing deviations. Inspect both generated and final native results;
passing an anchor check never substitutes for user visual approval. Portraits
have separate framing and feature checks, not the small badge mask.

When point sampling deforms generated portrait features, compare area sampling
at the same declared native dimensions before native palette conversion. Record
the selected method; never hand-repair generated eye shapes. Any fixed geometric
registration of a head must state its transform and source/target landmarks,
preserve the untouched generation, and pass the shared-anchor checks. Do not
silently fit a head to a detected bounding box. Keep before/after comparisons of
targeted revisions at the top of the complete review page.

Check generated facial alignment before restoring shared native face pixels.
A sparse anchor mask can pass while leaving duplicate eye pixels beside it.
Inspect the whole inner eye region for unintended dark clusters; for exposed
Human faces, validate exactly the two original eye columns across the eye rows.
Preserve fixed translation records when generated landmarks are displaced.

For animation color corrections, compare each material across all poses in the
affected cycle. A shared native palette does not prevent the same sleeve from
becoming skin-colored in a separately generated frame. Use accepted front/rear
neutral frames as immutable material-color references and include the original
concept. Inspect native-converted steps together before propagating revisions.
Preserve rejected attempts; label review-only pose overrides separately from
the prior ROM exports and in-game screenshot evidence.

The muted-scarf Samurai backup was restored in the preceding all-class native build
`316a40524b960c49ad7213ac4b0bea539bfa9513`. That is the approved first-pass
import's parent, not the latest accepted package. Use
[the final native-art checkpoint](../../notes/native-final-art-2026-09-20.md) for
reproduction, verified scope, screenshot evidence and the separate launcher.
The earlier rejected preview remains historical. All 675 class poses are now
imported, with final-ROM menu, battle and save checks; no custom palette system.

For color calibration, freeze the approved base mapping. A supplemental
imagegen reference can supply missing action-only colors (for example water
ripples) without changing established base colors. Authenticate every reference
and preserve identical source RGB-to-index assignments across poses. Existing
class/side palette changes require an exact source-receipt allowlist, validation
of the parent byte, and untouched native palette words. The current three
changes are Bard/Dancer ally1-enemy0 and Mystic Knight ally0-enemy1.
Menu miniatures reuse the exact native base indices with the game's original
bright/dim routing; do not quantize bright source art against the dim menu bank.
Preserve original archive entries and verify all native consumers separately.

## Earlier native-color calibration: rationale and reproduction

This section records the work leading to the current accepted package above.
Its earlier conversion commands are historical reconstruction steps, not a
replacement for importing the exact approved round8 receipt.

The user rejected the September20 native nearest-color conversion as visually
unacceptable. Functional runtime passes do not accept that artwork. Do not
launch or propagate the rejected preview as a finished release. Use the existing
native palettes only; no custom palette system. The comparison work is documented
in [the native-color checkpoint](../../notes/reviewed-native-color-2026-09-20.md).

For a native import, start from the accepted `a28b624b` engineering manifest and
run `build-reviewed-native-actions`, `build-reviewed-native-portraits`,
`build-reviewed-native-miniatures`, and `build-reviewed-native-badges` through
`Test Expansion.ps1 -Plan scripts/reviewed-art-test-plan.json -Only ...`.
The action import uses `--native` and quantizes approved RGBA sources directly;
never re-quantize the retired custom-palette output. Native miniatures replace
only archive pixels and pointers. Large portraits keep the existing native
portrait archive format. The complete contract check permits only declared
image/archive data and graphics pointers relative to accepted engineering.

Color-study outputs remain separate from the approved pose catalog. Compare
the original drawing, exact indexed conversion, and palette-guided imagegen
result at32px and integer magnification. Preserve prompts/references and native
palette indices. Judge costume color, face/eye readability and silhouette,
then inspect both ally/enemy and bright/dim interpretations before accepting a
new base. A pleasing large imagegen output is not a native-sprite acceptance.
Record approval against the exact native PNG hash. For focused visual revisions,
compare indexed pixels and alpha silhouettes with the preceding draft; retain
incidental generation changes in the review record rather than claiming a
pixel-identical edit. The native Dark Knight base and Samurai Palette1-neutral
backup with the muted scarf are approved. Preserve the exact approved PNG hashes
in the linked native-color checkpoint while propagating their conversions.
When matching skin, extract original human references with their actual class
selectors using `prepare-native-human-skin-reference.py`. Use those images in
imagegen and check the native-size face against adjacent cloth. Preserve a
user-selected fallback by exact file hash while comparing further variants.

For aligned bases, the approved-image color-transfer pilot is documented in
[the Dark Knight checkpoint](../../notes/native-color-transfer-2026-09-20.md). Keep
conversion manifests and candidate/evidence pointers separate from the current
combined build. Require exact native palette indices, unchanged pose silhouettes,
consistent cross-frame color mapping, and the exact approved neutral PNG. Review
the complete pose sheet, then exercise actual actions and water before extending
the method. This is build-time conversion only; do not add runtime palettes.

The combined human workflow and verified evidence are in
[the human integration checkpoint](../../notes/native-human-integration-2026-09-20.md).
Conversion recipes may contain a `units` list; require complete per-class pose
coverage and authenticate archived source PNGs. Retain already tested classes
by exact tile/OAM/selector comparison when another class's colors change.
Distinguish user-approved native bases from primary-agent-reviewed draft bases.
The nonhuman conversion receipt records primary-agent review rather than user
approval. Its formerly proposed selector changes are now integrated and checked
by the exact allowlist described above. Inspect all action and water sheets;
a standing-base calibration may misclassify colors absent from that base.

For the reviewed-art combined candidate, reuse its authenticated cold-world
checkpoint in `test-art-all-class-capacity.py --reviewed-entry`. The existing
formation324 six-versus-six scenario declares party/enemy class inputs before
native allocation. Clear only its explicit action-root canaries, authenticate
the complete manifest and world files, and retain every failed run. The reviewed
entry budget is3000 frames: retained timeout154655 and no-input diagnostic154819
show the first enemy turn reaching the menu240 frames beyond the old2400 bound.
Do not widen unrelated timing assertions. `test-art-capacity-action.py
--reviewed-capacity <passing report>` then reuses that exact ready allocation for
Thundaga and repeated Status lifetimes; prove complete heap restoration and live
palette refusal counters, not just free-byte totals. These checks do not waive
the independent strict Move/cancel response gate.

This is the durable workflow. Read `IMPLEMENTATION-STATE.md` for the latest
checkpoint and next actions, and each worktree's `scripts/jobs/<job>/STATUS.md`
for its local evidence. Update this document whenever the process changes.

For full engineering reconstruction, use build-full-engineering in the declared
native-art plan. Separate explicitly pinned historical gameplay source stages
from current later-stage graphics sources. Reconvert original PNGs and extract
native references again; never substitute cached tiles or component ROMs for
source build proof. A failed art suffix may reuse its freshly passed base only
with an exact report hash; preserve both failures and use unique output folders.
The recipe records private input hashes, conversion specifications and every
expected component. Review build-time native palette transport after any art
replacement; do not reintroduce the retired runtime ownership/remapping path.

The final audit verifies historical source pins using their recorded commit and
current shipping source pins against the checkout. Commit reviewed packaging
sources before producing the package so its sourceCommit identifies shipping
code. Package through package-full-engineering, then run the actual launcher's
ValidateOnly path with test-full-engineering-launcher. Require deterministic BPS,
exact patch roundtrip, wrong-source/ROM rejection, immutable documents and
independent save/state/screenshot overrides. Include transitive local Markdown/JSON
reference documents and validate their relative links inside the immutable bundle;
checkout links alone do not prove a complete standalone guide. Preserve old
launchers and player files, and do not launch the game as an acceptance side effect.

Encounter selection audits must cover all512 native mission slots, including
non-public and recovery records. Follow actual secondary-map lookup pointers:
native9C18 uses the roaming event base225, not event0. Distinguish initial roster
arithmetic from later scripted spawns, and descending scene search from direct
mission selection. Verify repeated menu returns against complete heap block
lists, not only free totals. A loaded libretro state has no published frame
until execution resumes. When selecting Wait/Status deterministically, identify
the yellow marker and verify the other unselected native label; the selected
label's outline changes. Decode native pixel1 as BGRX. Preserve unused sentinel
roots when their actual consumer deliberately leaves them untouched.

For capacity failures, preserve raw snapshots before attempting diagnostic heap
walks; a corrupt walk must not prevent writing the original failure report.
Distinguish a formation transplant from the original event's scene, setup flags
and eligibility. A native array bound is not proof of reachable occupancy, and
a record-domain iterator is not an actor-capacity guarantee. Reproduce the
specific offending native routine against original code with bounded controls
before changing the engine. Keep a diagnostic reproduction pass separate from
capacity acceptance, and use retained states for missing route inputs.

At a native-transport integration review, enumerate every descriptor slot,
including nulls; follow actual table pointers rather than comparing relocated
addresses. Authenticate full converted draw payloads and preserve all other
command/OAM/timing metadata. Derive weapon-family coverage from current equipment
permissions, and keep original copy-handler hooks distinct from clean-US hooks.
Reusing historical playback requires explicit graph/code/data dependencies;
never relabel its recorded ROM or claim newly executed frames. Keep runtime
consumer acceptance separate from capacity, campaign/save and final packaging.

World mode reuses battle globals: F434 is not a valid heap-owner oracle outside
battle. For a full world-party menu, derive its owner from context[0] and verify
that the native allocation contains the full context/list. Adapt a read-only
snapshot for a battle-specific walker; never rewrite the live world global.
An earned battle receipt can precede mandatory territory placement. Complete
that original controller before using Start as evidence of world-menu entry.

Reuse flash for cross-build compatibility checks and cold-allocate current state;
only reuse savestates with their exact ROM. When adapting a retained test, pin
its exact source and assert every substitution occurs once. Keep declared scene
entry separate from natural campaign eligibility and preserve all original
assertions. Historical note reconciliation uses the original recorded commit
when later documentation was corrected; record the revised note separately.

Before an art pass, read ART-TEAM-CONSTRAINTS.md and notes/art-team-contract.json.
Recheck exact palette selectors, intermediate/final reservation usage and each
successive source/pose writer. Separate current importer restrictions from hardware
limits and visual recommendations. Keep the brief and metadata synchronized when
those contracts change; a source-sheet replacement can be overwritten by a later
stage, particularly Dark Knight overrides or Moogle action completion.

## Native phase and writer attribution

For a base-sprite art review loop, lock the original design before generating
individual action poses. Use several native sprites for style; do not carry a
single donor's cap/hair/costume silhouette into the new design.
For generation, begin with a short design brief and the native reference row;
let the image convey style rather than prescribing facial pixel coordinates.
A short second instruction such as "Make the rightmost one adhere to the style
of the others" is a separate experiment. Keep technical conversion constraints
and acceptance checks out of the creative prompt unless a specific failure
requires them. Do not use a user-provided example output as an input when the
user asks to reproduce its quality independently.
For class concept exploration, the user clarified that full character
illustrations come first, matched to the original game's illustrated job art.
Use original FFTA concept illustrations as visual references and keep prompts
short; retain reference URLs, hashes, exact prompts and untouched model outputs.
Review costume and silhouette before adapting the accepted design onto the
racial sprite base. Do not substitute sprite studies for concept illustrations.
The ten-class illustrated study is recorded in
`src/art/race-study/illustrated-class-concepts-v1.json`; its private outputs and
reference copies are under `build/art/illustrated-class-concepts-2026-09-19/`.
For the revised illustration process, attach two reference panels: four original
FFTA jobs of the same race for drawing style and anatomical variety, plus one or
two Final Fantasy class illustrations for recognizable costume and equipment.
Avoid carrying one default race character's exact coloring and silhouette into
every job. Preserve all individual source images and their attribution alongside
the panels. The second pass is recorded in
`src/art/race-study/illustrated-class-concepts-v2.json`; reproduce its reference
panels with `scripts/prepare-illustration-reference-sets.py boards` and its gallery
with `scripts/package-class-illustrations.py --version v2` after generation.
For requested details, edit the selected design with a short single-change prompt;
use an older design only as the reference for that detail. Save a sibling revision,
retain both inputs and their hashes, and select it explicitly in the manifest.
When the user requires the SAME native pixel base, identify exact shared pixels
from aligned native same-pose references and preserve them as an unchanged
protected layer over imagegen-authored costume pixels. Verify coordinates and
colors after assembly; an imagegen instruction alone does not guarantee exact
retention. This layer is extracted original data, not hand-authored replacement
art. Keep it private and scope the proof to the actual references/pose inspected.
The first four-Human reference study preserved 68 shared foreground pixels;
`scripts/assemble-shared-base-study.py` reproduces the extraction and check.
For the other four races, run `scripts/assemble-other-race-studies.py prepare`,
generate each saved prompt with its own template, save outputs as
`build/art/race-study-2026-09-19/other-races/<race>-generated.png`, then run the
same script with `assemble`. Reference IDs, exact prompts and input hashes are
in `src/art/race-study/other-races-shared-base.json`; the checkpoint is
`notes/other-race-shared-base-study-2026-09-19.md`. Compare the original reference
cells with the final protected output, never model-redrawn reference neighbors.
Preserving common pixels does not prove that every remaining anatomical pixel
is shared, or establish other animation phases. Recompute the layer per pose.
Review camera
elevation across crown, shoulder and boot top planes separately from left/right
facing and eye visibility. Preserve the user's original reference as truth;
imagegen may redraw reference neighbors in contextual comparison images.
Keep source art and exact native-size conversion side by side. A bbox-fitted
downsample can shift an enlarged pixel grid and erase eyes: when a reference
workbench establishes a logical grid, recover that full grid before cropping,
then prohibit a second resize. This is technical conversion, not pixel repair.
Retain each prompt, source/reference hashes, conversion recipe and reviewer
verdict. A reviewer approval is not user acceptance or native integration proof.
Use review subagents only when newly requested, and stop at the user's loop cap.
The bounded example is notes/base-sprite-review-loop-2026-09-19.md.
When an approved costume covers the face or hair, do not composite exposed
anatomy back over that equipment. The user's closed Dark Knight helmet correction
overrides exposed-face retention for that design. Keep the revision and technical
palette/protection previews separate, and iterate base designs before producing
their animation frames. The selected Human Dark Knight base is recorded in
`src/art/race-study/human-dark-knight-fft-base-v2.json`. The user subsequently
approved proceeding with animation generation for all ten designs.

For every new animation pose or visual revision, include the approved original
concept illustration as an actual imagegen input. A sprite or sampled color
crop does not replace it. Also provide the native-pose worksheet and the
approved sprite where needed: the concept determines garment identity and
colors; the sprite and native frames determine pixel scale, anatomy and pose.
Record the role and hash of every supplied image. Check the selected concept
revision against the user's latest corrections before generating.
Generate the rear neutral view before rear steps, then use that rear view as the
costume anchor. Name the visible limb movement as well as the slot/phase meaning;
"walking step A" alone can preserve the neutral pose too strongly. Keep the
native frame order and command durations in metadata. Preserve rejected images
and prompts when correcting costume copying, facing, or weak pose separation.
The reproducible movement study is `scripts/assemble-class-animation.py`, with
prompts and sources in `src/art/race-study/animation-generation-v1.json` and scope
in `notes/class-animation-movement-2026-09-20.md`. These are review drafts, not
complete action coverage or accepted native artwork.

For a focused correction, keep the existing walking frame as the edit target
and supply the original concept separately. Name the relevant garments before
describing colors. Samurai trousers are charcoal; the teal cloth is a separate
waist scarf with hanging tails. Earlier v2-v4 prompts incorrectly called it
teal trousers and are historical failures, not current guidance. Cropped
references may supplement the full concept but must not replace it.
Review every pose and the complete loop for costume, stride, face, silhouette
and ground-shadow continuity. Reject collateral redraws even if the named
color improves. Preserve rejected images and prompts. The historical commands
in `scripts/prepare-animation-consistency.py` reproduce earlier attempts;
`--restore-concept` records the corrected source relationship and `--review`
rebuilds the comparison without drawing or repairing artwork.

The user explicitly authorized mechanical reuse of the approved Samurai face
after repeated imagegen identity drift: "yes do whatever you need to" in response
to the exact-face-pixel-copy proposal. For this correction, copy existing RGBA
pixels without recoloring, rescaling or drawing replacements. Preserve the old
frames, record source/target regions and hashes, and verify all pixels outside
the region are unchanged. `scripts/apply-samurai-face-reuse.py` implements and
verifies the 8 by 6 face region; step B offsets it down one pixel for its head bob.
This exception does not authorize replacing covered faces over helmets or
redesigning other approved units. Continue using imagegen with original concepts
for new artwork. For exact-color previews, protect the reused colors in one
shared GIF palette and verify decoded GIF pixels too: separate frame palettes
can create flicker even when the input face pixels are identical.

Native shared-palette conversion is a build-time stage after action completion.
Keep transparent index0 distinct from all opaque indices, preserve every native
command/OAM/descriptor field except declared draw tile pointers, and bound ROM
writes to authenticated hooks/table entries plus an unused reservation. Validate
both original job palette selectors. Final source art must be reviewed in both
native party and opposing ramps. The conversion is not final visual acceptance.

When `nativePaletteTransport` is present, custom ownership/variant observers no
longer describe the executing graphics path. Observe native OAM and exact side
palettes instead. Exclude only the authenticated original offscreen sentinel
`(0x00A8,0x00F8,0)` before associating tile0 with a body; retain shape, allocation,
upload and palette checks for actual objects. Distinguish allocated classes from
camera-visible classes. An already-native compositor cannot provide an
independent bypass performance control. Use actual original-renderer comparison
evidence and fresh candidate-specific actor allocations.

For native-palette performance acceptance, `test-art-native-palette-entry`
constructs a bounded original-renderer control with only the existing Status
shortcut, then allocates each ROM's own actors from the authenticated world
checkpoint. Its exact report and own-ROM ready/entry states feed
`test-art-native-palette-response` and `test-art-native-palette-deployment`.
Preserve both established response offsets and the608-frame deployment interval.
Whole observed state/framebuffer must equal fresh ordinary execution; compare
raw motion, native colors and input/update/rotation cadence without shifting
timelines. Keep inherited inert-module metadata distinct from executing hooks.

For native-palette Combo chains, observe published native membership at080B32E8
and complete OAM at actual composition return. A profile-only native-donor
control can reuse the exact allocation because actor data/pointers are unchanged.
Respect the real participant range when declaring starting coordinates; do not
force membership. `native_tiles_hidden` proves original OAM and absence of all
references to a retained tile span without custom-tag assumptions. A hidden
initial constructor may retain an old verified upload; validate native reset
fields, bounded age, complete unchanged pixels and actual native construction
before accepting that observation. Never count it as a displayed new pose.

For native-palette casting, pass an authenticated paired entry selector to
`test-connected-art-casting.py --native-entry`. Each branch uses its own ROM
and ready allocation. Secondary command fixtures must include both native
selection+36 and resolved job+8; neither changes a preallocated body identity.
Select a different class before deployment through the entry script's explicit
profile option, and keep its selector separate from the accepted performance
entry. Compare actual native OAM/palettes and command outcomes without using
inactive custom ownership counters.

For auxiliary-resource controls, keep the executing renderer and body assets
the same and change only the declared native resource/icon selection. An older
weapon-stage parent may still execute a different renderer. Name the actual
control ROM hash separately from inherited component provenance. Restrict
native shared-palette body observers to generic presentation1; named story
characters retain their native appearance despite fallback gameplay jobs.

A queued upload may complete while the next graphics command is decoded.
Require the exact preceding observed command/source/layout, one-frame age,
pending flags, same allocation/channel, and the complete new pixels plus
unchanged allocation tail. Keep this proof distinct from an unchanged direct
anchor. Native graphics-command reproduction requires a real transfer context:
the null argument used by no-op proofs silently defers graphics. Declare a
bounded available queue for a controlled native proof and do not describe it
as reconstruction of the previous whole-game state.

For a bounded entry timeout, replay the retained state without state edits to
establish whether native enemy actions are still progressing. Preserve the failed
budget and exact later menu arrival before changing the declared route budget;
do not use a longer entry wait to waive Move/cancel latency acceptance.

Do not infer a palette writer from a rotated color sequence. Locate the first
raw divergence in retained route samples and use `--entry-checkpoint` on the
existing deterministic entry script to retain that boundary without changing
inputs or acceptance. Replay only the affected interval; compare every observed
complete machine state/frame to fresh ordinary execution of the same ROM.
If expected native callbacks are absent, trace actual bounded writes and inspect
their original caller. Thumb stores do not establish ARM copy, BIOS or DMA
coverage. Authenticate the original code and compare full memory before/after
the actual callback, including its real counter state. Preserve raw call counts,
phases and any slower update cadence separately from correct color arithmetic.
A passing same-ROM battle response test does not cover a separate deployment
route whose parent has different graphics/hooks/heap reservations.

Profile the exact conditional path before attributing an inclusive function's
cost to a child. Record actual sprite geometry and current demand counts; a
full-width row optimization does not help a horizontally clipped rectangle.
When using same-call prepared demands, independently reconstruct occupied banks,
requested history IDs and ordered8bpp indices from actual complete OAM/tags at
the consumer entry. Saved ready states are ROM-specific: use a committed manifest,
source and complete hash index for another candidate, not old actor pointers.
Lower CPU cost can still change input/scheduler phase and worsen a paired response;
keep the response gate separate and retain every failing offset/metric.

## Scoped ARM cost observation

For exact-byte cache optimizations, exercise a zero-primed mutation at every
byte of the cached unit, including the last comparison lane; then exercise hits
without changing those bytes. Keep transparent zero distinct from opaque
indices1..15. Block loads may advance scratch pointers before a mismatch, so
rescan from the unchanged original tile pointer. If extra scratch storage raises
leaf stack usage, raise the scoped-copy cutoff by that same amount and observe
actual execution immediately below, at and above the new cutoff. Verify the
native resident region and the complete interrupt reserve remain unchanged.

When comparing a planner that can reuse an existing plan, initialize both
implementations with the same prior plan and pixel cache for every case. A first
full-plan invocation may populate cache entries that preferred-plan reuse leaves
untouched. Compare all cache bytes against a freshly executed same-input
reference, not against the first invocation's side effects. Keep failed-plan
atomicity, structure padding, native-bank exhaustion and fallback coverage.

Separate wrapper allocation/copy from leaf execution before attributing an
inclusive fast-memory routine's cost. Authenticate the exact wrapper machine
code and leaf hash; observe actual branch/return PCs and verify every copied
execution target's full bytes, SP and LR. ARM and Thumb dispatch use distinct
host tables and PC biases. Pin the emulator DLL and verify both table reference
instructions and dispatch index calculation. Restore both tables on context
exit; require every complete state/frame to equal ordinary emulation.

Conditional ARM instructions rejected by the emulator's condition check never
reach its dispatch table. Use authenticated unconditional boundaries; do not
interpret table callbacks as all-instruction coverage. Record return-only shared
arrivals and unexercised fallback paths. An observer for one compiled wrapper
layout must fail closed for another. These measurements and isolated correctness
do not replace the same-ROM paired response gate at both declared input offsets.

## Native query dispatch and fallback proof

An optimized canonical-unit query must retain the original independent-copy
semantics. Use a dispatcher that restores original SP, arguments, callee-saved
registers and LR before tail-entering the original fallback; a C nested fallback
silently increases worst-case native stack depth. Observe the actual original
body entry, comparing initialized argument/saved-register areas and stack address.
Test every byte across native arrays/gaps against the original predicate, both
stack alignments, copied ownership and actual complete movement-grid consumers.
For entry veneers at2mod4 ROM offsets, compute literal alignment from the absolute
installation address, not only the assembler section's relative alignment.
Scoped correctness/rebuild proof does not establish response-time acceptance.

## Connected art transport workflow

Native-only frames can retain stale custom ownership tags because the native
composition path returns before scanning them. Do not interpret such tags as
visible actors. Authenticate and reconstruct the complete native OAM producer,
including clipping and affine writes, and prove no displayed tile span overlaps
the retained class allocation. Require the actual early-return phase, no custom
emission/overlay and no refusals. Keep this distinct from visible palette proof.

Foreground source buffers can advance after the displayed composition. Capture
bounded source data at the actual native composition return and require current
hardware to match that captured boundary; later foreground buffers are not its
provenance. Native afterimages may add copies during a constructor reset. Prove
the native geometry, every previous copy retained, unchanged full pixel allocation
and a bounded recent direct-upload anchor. Keep palette-bank proof separate.
Use the actual prior composition event in regression fixtures, not the current
hardware as a substitute. Reproduce constructor fields through the original
native routine and include all four facings: native flags45/65 are facing-specific.

Reuse an existing exact-ROM ready state through committed report/state/RAM/IWRAM
pins when its actors were already allocated in the required classes. Verify those
source captures unchanged afterward. Do not rewrite saved actor pointers or
postallocation class identities to claim new generic-body graphics acceptance.

Resource relocation can preserve a donor's holes that a new class's permitted
weapons actually request. Test generic actors allocated in the intended new
job/race; named-character gameplay evidence does not prove every generic body.
When a wrapper body pointer becomes invalid, authenticate the native constructor
and its descriptor before treating stale body memory as a display hold. Preserve
the failed capture; do not relax bounds or silently change the equipped weapon.

An explicit missing-stream stage may add only checked absent owned descriptors,
using appropriate native command/timing templates and the class's generated
pixels. Keep original character graphics out of replacement payloads. Prove
all old graphs/code unchanged, each added facing through native construction,
actual weapon playback and exact rebuild. Record the stage as a dependency of
future final assembly; an older connected builder alone does not include it.

To reuse historical graphics evidence, authenticate the reports and raw hardware
captures, follow both actual ROM table/sequence pointers, and compare complete
command/layout/tile graphs modulo relocation. Check actual job routing and size
tables, not only manifests. Keep executed and candidate ROM hashes separate;
never resume or rewrite old actor pointers to simulate current-ROM acceptance.
Equivalent assets do not prove changed compositor, heap, save or effect lifetimes.

Native animation entries include controls as well as graphics. Before changing
ROM content for a body-display mismatch, authenticate the native dispatcher and
the actor's cursor/source/layout. Only type1 uploads graphics; recognized control
commands, including observed native opcode0, may retain the nearest executed type1. Require exact cursor and pointer
agreement, expose the hold in evidence, and reject negative pixel/source/cursor/
opcode cases. A full action replay then validates the corrected observer scope.

Scoped IWRAM acceleration needs explicit code size, ABI, stack headroom and
interrupt reserve proofs plus exact ROM fallback for deep/external stacks. Test
both word alignments, read-only inputs, scratch fences and actual execution PCs.
Keep classifier and pixel scan accounting distinct. Such proofs do not replace
paired response acceptance, even when isolated instruction counts improve.

For compiled scoped leaves, isolate function sections, reject address/call
relocations, include literal pools, and record compiler/source/blob hashes plus
static stack-usage output. GNU V4BX is acceptable only after checking the actual
BX-register instruction; do not ignore arbitrary relocation records. Derive the
copy threshold from resident-code end, leaf size/stack and interrupt reserve.
Test both10- and20-history layouts when their struct packing differs.

A native producer can prove an unused sprite tail without rereading it during
every frame. Authenticate the full producer body/literals, derive its actual
clipping order, and compare computed bounds to actual native DMA destinations.
Preserve the omitted sentinel's bank demand; affine attr3 writes are distinct
from enable/palette fields. Independently inspect the complete omitted OAM/tag
tail at every observed application before accepting such an optimization.

If using that same-invocation producer to eliminate redundant hardware/source
comparisons, expose a separate native-only entry and retain the general validator.
Authenticate the intervening path's lack of source/OAM writes. Differentially
test the native entry after actual composition, then independently inspect every
copied main attribute and resulting owner tag at each observed runtime call.
Producer authority does not waive stale owner-record validation or justify reuse
across frames. Keep the constructor contract and generic refusal scope explicit.

For same-invocation prepared demands, independently reconstruct current OAM
classification at the actual consumer, after any history-tag remapping. Capture
dynamic stack structures and stack arguments through bounded mapped-memory reads
before the instruction executes; preserve ordinary state/framebuffer equivalence.
If a later feature filters owners, recompute its demands or retain a separately
verified fallback. Component comparisons must actually exercise simultaneous
same-class/different-bank requests; merely moving a unique class tests acquisition.
Keep raw-input compositor proofs distinct from live targeting UI and action proof.

A diagnostic difference is not an acceptance invariant. Retain complete raw
paired comparisons even when their mismatch list becomes empty; continue to
check every native phase, hardware write, input window and deadline. Reject
performance trials using actual cycles/responses, and isolate rejected options
from defaults while preserving exact compiled-byte and source provenance.

Use authenticated compiled call/return sites for actual GBA cycle breakdowns.
Keep inclusive and nested costs separate. An instruction after a conditional
call may also be a branch target: explicitly count/exclude arrivals without a
matching call, and reject incomplete or reentrant pairs. As with other host
observation, prove complete state/framebuffer equivalence to ordinary execution.

For native controller profiling, decode executed direct calls within authenticated
function bounds; local epilogue branches and literal-pool bytes are not callees.
Process a shared return/next-call address in that order, pair recursive instances
by stack, and state indirect-call/descendant limits. A long inclusive wrapper may
execute a callback or scheduler; inspect that consumer before inferring wasted
work. Optimization must preserve native results, not just reduce measured time.

Keep rejected compiler/code-size trials explicitly opt-in. For Thumb scoped
leaves, clear the symbol state bit when copying bytes and set it when entering
code; retain relocation/stack/fallback proofs. Verify default object bytes and
relocations still match. Use private completion-stage outputs without repointing
the active action selector when measuring rejected experiments.

For any validated reuse path, independently reconstruct the entire consumed
pixel footprint as well as comparing every listed byte. Require explicit
coverage fields and authenticate current ownership/history mapping at each
observed fast entry. Whole-state observer equivalence alone proves neither.
Measure hit and miss costs separately and check actual display return stays
inside VBlank; high hit rates and lower averages can hide deadline overruns.
Test-plan order controls execution, not the order in `-Only`. Place build steps
before tests consuming mutable candidate indexes, and inspect every ROM hash.

For held trails, authenticate the secondary descriptor channel separately from
body/primary routing. A directly uploaded frame can establish the anchor needed
for later native pending holds. Preserve the complete allocation and existing
age bound; repeated placeholder pixels can conceal missing observer semantics.
Prove a newly recognized control using original native dispatch/update and
negative pixel/pointer/opcode cases before rerunning its actual consumer.

For encounter capacity, inventory original formation records and native allocator
consumers before choosing fixtures. Template count, party deployment ceiling,
non-party record capacity and live actor count are different quantities. Resolve
secondary formations and scripted spawn/retirement; keep static content maxima
separate from reachable runtime demand and sampled heap/effect acceptance.

Placeholder artwork does not reduce engineering acceptance. Keep visual-quality
deferrals separate from action transport, performance, capacity, gameplay and
save-lifetime gates. A temporary generated pose can exercise a complete native
animation path; a low-level import check alone cannot close that path. Preserve
immutable baseline packages and failed experiments while building candidates.
Do not waive a measured engineering regression merely to ship a technical preview.

When a performance change touches a gameplay query, authenticate its actual code,
ownership and format dependencies rather than a broad ROM range containing
unrelated art tables. Preserve current-query validation and independent copied
cohorts. Compare original/native results and full movement grids under positive,
negative, lifecycle and support inputs before live response measurements. A faster
native child call does not prove the graphics regression resolved.

Install instruction counters before execution or flush Unicorn's translated code
after adding them to already-run functions. Require positive observed counts.
Place explicitly owned stack fixtures above the active stack, as the API requires;
do not loosen ownership rules to accept an invalid fixture. Include entry bridges
and nested fallback frames in stack accounting, not just compiler-reported C frames.

Separate observer correctness from performance acceptance. A native-frame-events
pass establishes faithful observation, not acceptable latency. Feed authenticated
complete traces to test-art-response-budget.py and keep both input offsets and
each response/duration metric explicit. Reconcile native animation phases with
their independent native oracle; preserve the original failed paired comparison
and do not imply skipped assertions ran. Raw mixed composition profiles must
match the retained capture's exact transient layout; use --installed-mixed for
the corrected7507 capture, without resuming its actor pointers on another ROM.

Use `--graphics-inputs` for exact native OAM/OBJ snapshots and Thumb STR/STRH/DMA
observations. Inspect `summarize-art-graphics-inputs.py` output alongside the
full trace. Changed-tile/write overlap is not complete byte-producer coverage;
ARM, BIOS and other stores remain outside that observer. For tracked-cache
candidates require explicit per-frame audit fields and compare every valid
mask with current tile pixels. A requested observer option without recorded
coverage is not evidence. Reuse retained traces for phase/response checks.
Keep incomplete writer-cache prototypes private and opt-in. Current-byte OAM
traversal changes need exact sentinel/owner/affine exceptional-lane tests and
actual paired timing; reduced instruction counts alone cannot close E01.

The user deferred final artwork on September18. Use `ART-PLACEHOLDERS.md` and
`Prepare Art Pass.ps1` for a local inventory of the immutable installed bundle.
Do not infer installed sources from newer experimental indexes. The art desk's
all-ten `battle-overrides.json` is directly usable by the private palette build;
`test-placeholder-override-roundtrip` proves a no-change override reproduces the
full installed ROM, including job117. Keep body and menu inputs explicit. Every
new custom sheet still uses imagegen, but placeholder delivery does not require
bespoke poses or final visual refinement. No art-pass continuation without a new
user request after this placeholder handoff.

For support/action revisions, an art override may specify authenticated
`actionPlan`/`actionPlanSha256`. `live_action_plan.py` matches original native
pose keys against the clean ROM and checks descriptor/frame control metadata;
it must not infer the pose from frame-index cycling. Every supplied sheet must
share the exact class palette, and source/conversion/image/tile hashes must agree.
Unmapped frames preserve the prior transport; explicit water art bypasses the
legacy crop. Coverage stays partial and productionAccepted=false. Use the
`test-samurai-support-build` and `test-samurai-support-native` pattern for source
preservation and real native actor/phase consumers; these do not establish live
battle action display. `review-samurai-support.py` reproduces conversion and
original-baseline comparisons. Check remaining ROM reservation capacity before
adding sheets; never silently spill into another reservation.

For private artwork revisions, `build-live-art-palette.py` accepts an explicit
`art_overrides` manifest and `publish_current=False`. Authenticate source PNG,
conversion manifest, palette and tiles; leave default catalog inputs unchanged.
Four/eight-frame legacy drafts keep their mapping; six-frame sheets map front
0/1/2/1 and back3/4/5/4. This does not turn repeated action poses or water crops
into finished art. The default117 diagnostic input stays pinned; explicit overrides now support all ten jobs.
`test-samurai-v7-build` proves unchanged defaults, only the intended compiled
color-table change, all other class pixels and native timing/commands, then
preserves installed/source indexes. Use fresh native entry after new sequence
pointers; do not apply old mid-battle states to a revised art ROM.

Review tiny features on a neutral background and verify actual indexed pixels
before declaring that conversion removed them. `review-samurai-march-v7.py`
reproduces authenticated native-size comparisons and a labeled composite loop.
`test-samurai-v7-entry` samples a full96-frame idle cycle; the separate
`test-samurai-v7-walk` checks actual native Move/cancel, frame hashes, palette
output and paired outcomes. A marching proof does not accept all action slots.

For native target/damage consumers, distinguish explicit shared native palettes
from class-color transforms. Authenticate native highlight copy caller, exact
addresses/size and full table before excluding its objects from custom ownership;
leave those objects in native bank-occupancy checks. Damage effects can start on
colors1..15 before an actor adopts the bank. Prepare from the complete authenticated
baseline, preserve color0, and prove interpolation/restoration against original
native setters. Keep arbitrary partial ranges and unmappable confirmed targets
explicitly refused. Use `test-art-native-highlight`, `test-art-damage-palettes`,
`test-art-damage-additional-operations`, `test-art-damage-boundaries` and the
narrow `test-art-highlight-thundaga`; the latter consumes an authenticated current-
ROM `mixed-first-fixture.json`. Relocated hook code requires a fresh normal
entry; never reuse an old mid-battle state as if pointers were compatible.

`test-art-highlight-write-trace` extends the pinned host observer to immediate/
register Thumb STRH stores in one declared palette bank. `--damage` also records
native effect/copy entry arguments. It proves every full state and framebuffer
against a fresh ordinary core on the same fixed inputs before using the trace.
This does not cover ARM/word/STM/DMA stores. Zero observed writes cannot establish
that no other writer exists. Keep retained diagnostic ROMs/states pinned.

Keep source-rebuild provenance separate from runtime fixture provenance.
`build-connected-art.py --fixture-source` authenticates the retained fixture ROM
and report; `rebuild-connected-art.py` forwards the clean chain's fixtureSource.
Consumers must use that explicit field instead of assuming a rebuilt gameplay
ROM folder contains the retained states. A metadata repair does not justify
repeating unaffected runtime checks.

For capacity fixtures, inspect template allegiance and native deployment limits,
not only the formation's unit count. `test-art-larger-encounter` substitutes one
complete original record in a private ROM and records both hashes. Keep native
allies, fixed story participants, enemies and judge distinct. Assert actual
roster/counter behavior before claiming simultaneous custom-class coverage.
Status release clears ownership magic while retaining balanced lifetime counters;
use the established destructor contract, not an all-zero-root assumption.

`test-art-native-phase-evidence.py --trace REPORT --trace-sha256 SHA --manifest
MANIFEST` verifies a new exact-ROM observation against original native callbacks.
It authenticates the entire trace, traced manifest and retained RAM/IWRAM hashes;
never silently apply an old trace to relocated hooks. The current delivery IDs
are `test-art-delivery-frame-events` and `test-art-delivery-phase-evidence`.

For connected delivery, use `test-connected-art-rebuild` to reconstruct every
art stage and current palette/menu hook from the authenticated corrected base.
Reuse the unchanged gameplay rebuild; require full final-ROM equality. Package
schema3 only through `package-connected-art` and its explicit19-report evidence list.
Guide/evidence revisions use separate content-addressed bundle folders within
the ROM delivery folder, preserving earlier packages and ROM-specific saves.
Read/write documentation explicitly as UTF-8 on Windows.
The rebuild runner must be terminal before starting the packaging invocation;
a completed child in a still-running parent is deliberately ineligible. Then run `test-art-pipeline-launcher` in validation mode. Keep failed enclosing
runs/scopes in the delivery manifest. Updating the preview delivery index does
not copy saves, replace vanilla/v0.7 or change an already running session.

For connected portrait isolation, restore only the original portrait archive
literals in an otherwise identical control ROM. Comparing against an old
pre-palette parent also changes scheduling. `--retained-generics` with a pinned
report hash can reuse ten completed generic cases before a later fixed-character
failure; authenticate each captured VRAM/palette/OAM/player record and completed
upload assertion. Never reuse the failed fixed-character comparison itself.

`test-art-battle-stage-events` extends the proven host observer with fixed
foreground callback sites and bounded native shadow/hardware snapshots. Each
observed branch must still match every full native state and framebuffer against
ordinary execution. Compare the complete shadow before/after composition and
all BG hardware bytes; use the actual DMA decision, not a presumed frame phase.
`test-art-native-phase-evidence` authenticates the retained trace and executes
original native rotation callbacks on a detached clone. Compare the complete
BG shadow against independent native phases and OBJ against the paired control
at the same navigation point. Keep raw mismatching timelines, failed oracles,
input delay and VBlank limits explicit. This is a specific scene/candidate
reconciliation, never blanket acceptance of older failed candidates or effects.

`test-art-native-frame-events.py --candidate-manifest MANIFEST --retained-report
REPORT` requires an exact-ROM captured state and raw RAM/IWRAM. Preserve the
report and manifest hashes, including when the captured scene failed a later
acceptance assertion. `--legacy-plan-control` is specific to the retained
plan-reuse trial: authenticate the aligned Thumb scene-apply entry and its
original live-planner target, then change only an eight-byte jump. It preserves
all class composition; the ordinary compositor bypass answers a different
question. Retain the small jump overhead in the interpretation. Compare each
observed branch against its own fresh-core, fixed-navigation ordinary replay.
For cache measurements, report actual hit/miss cost as well as hit rate; a
high-hit cache can still be slower. The rejected whole-frame key trial proves
that case. Do not run its native rebuild against restored production source;
use its retained component manifest or its private source patch in isolation.

For native cycle/event observation, use `scripts/mgba_instruction_trace.py` only
with its pinned private test-core DLL. It observes selected host Thumb dispatch
entries while preserving the native run/event loop. Do not replace runFrame
with a native-step loop: that rejected method crosses a different IRQ boundary.
Announce and run `test-art-step-trace-equivalence` before extending the observer
into a new scope. `test-art-native-frame-events` compares entire native states
and complete framebuffers against ordinary execution at every action frame.
Use fresh cores plus the same authenticated seed and fixed navigation in both
branches; same-core replay and newly captured mid-scene restoration failed
byte-exact audio-state equality. Never mask those differences into a pass.
Preserve/restore host table protection/reference and every original handler;
never patch game memory to measure timing. Record raw cycles/input phase and
source hashes. `scripts/summarize-art-frame-events.py REPORT` summarizes retained
events without another runtime. See `notes/native-art-instruction-trace.md` for
ABI provenance, failures, measured limits and the required observation checks.

When isolating an optional optimization, keep the rest of the custom renderer
active in its control. `test-live-art-palette-compose-cost.py --planner-bypass`
authenticates the scoped-planner call target and following zero-return branch,
then disables only that four-byte call in a private derived ROM. Its source
ready state must match the exact candidate, including serialized actor pointers.
The ordinary compositor bypass answers a different question. Record both native
scanline costs and actual action response/duration; a lower instruction or
scanline count is not a demonstrated gameplay improvement. See the rejected
scoped-planner experiment for retained controls and source recovery.

For the shared battle-menu and compact US keyboard candidate, build the palette
parent with `--history-slots 20 --all-classes --workspace-low-address
--provisional-history --fast-rotation --owned-menu-buffer
--shared-battle-menu-heap --compact-us-keyboard`, then pass
`--source build/art/live-palette/keyboard-current.json` to the connected builder.
Parent compilation can refresh manifest metadata without changing ROM bytes;
assemble children afterward to pin the exact source manifest. Earlier indexes
remain distinct; the rejected `--separate-menu-ram` recipe is diagnostic only.

Use exact native caller/root checks when sharing an outer heap. Do not suppress
unrelated heap initialization or free the borrowed global battle root. The native
party destructor releases each child; check payload preservation and restored
free-list topology on the actual fragmented heap. Use
`test-art-shared-menu-lifecycle` and the pinned exact-ROM
`test-art-shared-menu-battle-ui`. Passing one battle does not prove worst-case
capacity: its menu construction leaves only1,068 free bytes.

Fresh-start tests must explicitly erase their isolated SRAM before boot, as in
`test-new-game-opening.py`; loading a ROM alone does not establish a fresh game.
Use bounded native allocation observation before keyboard inputs. Preserve both
US pages and native L/R wrap bounds when reducing glyph backing to `4200` bytes.
Do not enlarge the connected ROM heap for a reference: it overlaps active palette
state. Use the authenticated pre-palette parent with its original `F000` heap.
`test-art-keyboard-cold-ui` covers both tabs, editing, confirmation and free;
`test-art-keyboard-evidence` reuses pinned complete captures. Compare the original
`(17,33,176,126)` lettering crop, excluding the animated cursor, and both actual
native glyph buffers. Never describe that crop as whole-frame timing acceptance.

Follow the native context+2D50 list pointer, with RAM and count bounds. Never
assume fixed0203C000 is free: the prior item/ability list and new palette state
collided there. Enlarging a nested context requires every parent allocation
path too. Use `test-art-owned-menu-bounds` for actual constructors/teardown and
full460-row capacity, `test-art-owned-menu-preference-ui` for the shared ability
consumer, and `test-connected-art-equipment-ui` for actual Inventory/Buy/Sell.
Movable-address component success does not prove live battle-parent capacity.

`test-art-owned-menu-battle-ui` reuses the pinned mixed ready state only after
authenticating the exact three-byte parent-allocation delta and initial raw
RAM/IWRAM. Obtain a rendered frame after restoration before screenshot checks;
failure capture must also work without one. Its live Status failure is retained.
Use actual heap headers to distinguish insufficient total capacity from a
fragmented largest block; neither native constructor-only nor canary passes
establishes successful allocation in a live scene.

`test-generated-actions-battle.py --weapon --manifest ...` checks connected
class palettes with the held weapon. Skip only the exact native command marker
(FFFF,FFFFFFFF); validate with `test-native-art-command-marker`. Distinguish
un-emitted pending uploads from displayed-frame proof. A steady trail-palette
comparison requires the unique full-control value and actual native palette
shadow, and must not be described as timing acceptance.

Connected status checks require an exact-ROM passing ready report through
`--retained-ready`. Validate raw initial RAM/IWRAM; change only the128 glyph
bytes in the paired control. Read `notes/native-art-owned-menu.md` for evidence,
failed trials and current limitations.

Use `scripts/build-connected-art.py` to compose the explicit all-class palette
parent with status, equipment/projectile, held-weapon and impact imports. It
publishes only `build/art/connected/current.json`; historical component indexes
and installed builds are preserved. The manifest pins its immutable palette
source. Keep schema3 separate from old packaging acceptance. Use explicit base
manifests and `publish_current=False` for subordinate builders; reconstruct the
weapon table from the latest parent so palette-aware actor pointers survive.

`test-connected-art-native` verifies reproduction/native composition boundaries;
`test-connected-art-mixed-entry` is a bounded fresh battle. The optional
`--manifest` on `test-generated-projectile.py` adds four declared racial allies,
the generated impact and exact class/effect color-bank coexistence checks.
`test-connected-art-projectile-impact` runs that natural action. Its control
changes only the projectile dispatcher; both sides share the generated impact.
Do not call this all-effect/caster-class/timing acceptance. Read
`notes/native-art-connected-consumers.md` for exact evidence and limitations.

Verify UI labels before treating them as missing class artwork. In particular,
the battle `WT` field is turn order, not the White Mage abbreviation `WHT`.

Derive job/race mappings from the authenticated class manifest. In particular,
122/123 are Moogle and124/125 are Viera; do not copy stale fixture labels.
Keep declared presentation-profile replacements separate from natural recruitment
or legal class-switch claims, and preserve required story appearance identities.

Use `--natural-water --live-palette-water --water-job <id>` for one class's actual
native water resource/cancel path. Explicit profiles are unarmed; Moogle uses an
isolated generic slot5 identity. `scripts/native-art-water-test-plan.json` runs
independent remaining cases with `-Suite art`, preserving failure status. Reuse
passing class evidence; the dedicated plan is not a request to repeat all cases.
Every-frame body reads use native-enumerated wrapper addresses, while auxiliary
and weapon paths remain separate. Exact pending-facing acceptance requires the
preceding decoded source and allocation, never an arbitrary matching pose.

Pin retained raw consumers in `notes/native-art-all-class-water-evidence.json`.
`test-live-art-all-class-water-evidence` authenticates/reconciles these without
playback; it does not erase their sampling limits or establish timing/final-art
acceptance. Read `notes/native-art-racial-water-coverage.md` for failures/scope.

For the all-class rotation cost fix, append `--fast-rotation`. The builder and
native rebuild test preserve that flag. `test-art-rotation-permutation` compares
complete installed binding state against the pinned prior algorithm; the live
workspace late-rotation ID separately checks actual hardware phase. A component
pass never substitutes for live timing. Read `notes/native-art-rotation-permutation.md`.

For composition-cost diagnostics, `--current --candidate-manifest ...
--retained-report ...` can reuse a completed failed battle's existing ready state.
Require exact candidate ROM identity and serialized RAM/IWRAM equality; preserve
report/state hashes and original failed status. Read profile offsets from that
candidate's manifest. Bypassing the compositor is diagnostic only, never release
or battle acceptance. Do not create another ready fixture when an exact-ROM
capture already exists. Keep rejected trial sources and measured failures.

For provisional ownership builds, append `--provisional-history` to the current
20-history/all-class/low-address-workspace build. Read the compiled confirmation
offset from the manifest; scene reset initializes every key to255. A reference
palette match before emission is provisional. Supported unseen effects remain
tracked; unknown full-bank table replacement can retire only an unconfirmed key.
Never use current visibility alone to retire confirmed off-screen histories.

`test-art-provisional-history` uses the retained native bank12 transition and
checks later fresh/unknown appearances. `test-live-art-workspace-native` preserves
all build flags and verifies reset boundaries. Use the workspace late-entry/
late-rotation IDs for first appearance; count exact authenticated identities,
not one hardcoded history when several classes share a native baseline. Compare
unowned hardware with the paired native control, never with a backup that stores
only overwritten banks. The mask-control rotation ID is diagnostic only; it must
not establish full-class acceptance. See `notes/native-art-provisional-history.md`.

For mixed heap failures, verify both the physical block chain and native free
list; total free bytes do not establish contiguous allocation capacity. Use
`test-art-workspace-request-trace` and `test-live-art-mixed-write-trace` only for
bounded diagnostic captures. Their intentional traps fail the runner; keep that
status explicit. The trace ledger includes subordinate allocations and is not a
substitute for physical outer-heap validation. Poll the runner to terminal exit
before edits, even after its child reports failure.

Build the scoped low-address workspace candidate with `--history-slots 20
--all-classes --workspace-low-address`; separate `all-classes-workspace-current.json`.
`test-art-workspace-placement` proves the captured allocation/free sequence and
malformed-input refusal. `test-live-art-mixed-workspace-first`/`second` retain
strict mixed-game checks. `--trace-target` plus `test-art-palette-target-trace`
uses a separate diagnostic candidate to capture the first unrecognized table;
never package it or count its intentional halt as passing acceptance. See
`notes/native-art-workspace-placement.md` for the current next work.

Keep separate palette candidate indexes: default `poc.json`, larger-history
`history-current.json`, all-class `all-classes-current.json`. Build with
`scripts/build-live-art-palette.py --history-slots 20 --all-classes` for the last;
the builder authenticates original imagegen pixels and preserves native commands.
Do not interpret successful assembly or individual menus as mixed-battle proof.
Use the selected manifest's compiled layout, capacity and RAM boundaries in tests;
source-class count and physical palette-bank count are different limits.

For history changes, declared `test-art-palette-history-capacity`,
`test-live-art-history-native` and `test-live-art-history-appearance` cover the
component, installed hooks/clear boundaries and first visible frame. All-class
native/menu checks are `test-live-art-all-classes-native` and
`test-live-art-all-classes-menu`. Reuse their passing evidence for unchanged code.
`test-live-art-mixed-classes-first`/`second` preserve Montblanc and require four
actual same-race recruits each. The first currently fails; the second is unrun.
A generic replacement for a story character can alter fixture deployment;
verify the native roster rather than assuming the original fixed formation.
Keep mixed fixture indexes separate from normal cost-fixture.json, and require
exact ROM identity before any saved-state continuation. See
`notes/native-art-history-capacity.md` for retained failures and next diagnosis.

Before enabling additional custom class palettes, run read-only
`scripts/audit-art-palette-capacity.py` on its authenticated class references and
captured native colors. Separate simultaneous visible palette demand from
history acquired before appearance by a full-range effect. Existing deployment
colors can imply17 class/bank histories even though fewer actors are displayed.
Do not evict transformed absent histories to make a capacity test pass. Keep
this potential-demand audit distinct from actual all-class runtime acceptance.

For palette performance, compare actual planner scanlines as well as input and
movement frames. Current cost reports store profile after-owners/after-observe/
after-copy/after-plan; planner duration is profile3 minus profile2 modulo228.
These are display-line measurements, not exact CPU cycles. ARM-mode ROM routines
can execute fewer instructions while taking longer; see the rejected trial in
`notes/native-art-composition-memory.md`. Aligned tag word operations require
separate unaligned fallback/canary checks before adoption.

Use `test-native-art-compose-profile` for bounded instruction-location counts
on authenticated raw compositor inputs. It executes no saved actor animation;
native DMA is synchronous and counts are not hardware cycles or frame gains.
Keep the original isolation checks. Confirm any optimization using exact-ROM
ready capture and actual paired input/movement before retaining it. Lower
instruction counts or VBlank line numbers alone do not close timing acceptance.
See `notes/native-art-compose-profile.md` for the rejected grouped-marker trial.

Timing replay of a saved game state requires **exact ROM identity**, including
generated sequence/OAM addresses. Matching RAM layout, source art and native PC
is insufficient because actor records contain absolute ROM pointers. Use
`test-live-art-palette-cost-fixture` to reach ready through the declared route;
then reuse its ROM-local hashed index with `test-live-art-palette-current-cost`.
Do not silently repair actor pointers or compare relocated builds on old state.
Keep diagnostic compositor bypass separate from deliverable behavior. See
`notes/native-palette-timing-followup.md` for invalidated layout-only reports.

Occupied color history can exist without a fade counter or emitted actor:
rotation/cycling creates it. Fresh native DMA must latch those slots; skipped
DMA must preserve their previous visible phase. `test-native-art-compose-isolation-current`
covers this boundary under the synchronous DMA model. Use the separate
`test-live-art-late-rotation` for actual hide/reset/effect/reveal playback, with
active/completed rotation and cycling and zero fade starts. Capture every video
frame after reveal; don't hide a first-frame color error behind a multi-frame
settling wait. Only initial native double-buffer transfer may lack an overlay;
the first actual overlay must already match the native displayed effect phase.
Keep controlled menu input distinct from natural scene-transition acceptance.
Aligned bank copies are8 words and never target
the native palette shadow. Planner/compositor components must select ARMv4T
before memory mapping, especially when shared ARM/Thumb helpers move.

For native rotation/cycling run `test-native-art-rotation` through the original
dispatcher, then `test-live-art-rotation` for real callback/DMA playback. Type2
must permute fade targets/errors/deltas as well as colors; type4 inserts literal
table colors without permuting interpolation records. Test partial ranges, both
directions, delays/step counts, concurrent fades and first-appearance history.
Keep single-bank support distinct from cross-bank identity refusals. Before
extending obscure native helpers, run `scripts/audit-native-art-effect-reachability.py`
and inspect its call sites; absent direct/pointer references are not proof of
dynamic unreachability. See `notes/native-art-rotation.md`.

For native task controls, run `test-native-art-task-controls` before
`test-live-art-task-controls`. Compare actual cancellation/list/heap operations
and observable return ABI, including range trims within a bank, a task spanning
two banks, paused/type-excluded tasks, null/active/completed collection and task
reuse. Excluded colors and interpolation errors must freeze through the final
step. Native148738/14873C are identities, not selectors. Live playback must verify
the actual dispatcher pauses remaining duration and generated state. Keep clone
commands within declared palette/effect and private art memory; never copy their
stack or input scratch into the running game. See `notes/native-art-task-controls.md`.
This does not establish palette heap destruction or other task constructors.

For source-table effects, `test-native-art-table-colors` verifies the two native
seven-argument setters against original execution with independent generated
inputs. Cover normal/dim and uniform identity, prefixed table ranges, all three
caller-stack parameters, source immutability, interruption and explicit unknown
refusal. Table exposure floors its target source only; it does not apply the
direct exposure setter's current-color mutation. Follow with
`test-live-art-table-colors` and shared mapped-restoration/late-entry checks.
See `notes/native-art-table-colors.md`. Common setup coverage does not establish
standalone task cancellation, range trimming, separate callbacks or rotation.

Native effect setup can mutate its source before interpolation. For the two
exposure-style setters, verify the immediate minimum-three channel floor in both
current generated colors and contiguous display source, then compare targets and
all callbacks against the original engine. `test-native-art-extended-colors` and
`test-live-art-extended-colors` cover the five direct mix/brightness/exposure
setters; extend late-entry coverage for each newly supported operation. Never
treat a final-color-only check as proof of correct source/timing behavior.
Four-argument hooks require r3-preserving entry stubs as well as preserving
trampolines; authenticate the whole displaced prologue. See
`notes/native-art-extended-colors.md` for the failed short-entry example.

For appearance during effects, use `test-native-art-late-entry` before the actual
`test-live-art-palette-late-entry` consumer. The component compares installed
setters/callbacks with the original engine, with no preexisting ownership. Cover
normal/dim source identity, delayed/completed appearance, slot-pressure history,
unknown/capacity refusal and first-tick/DMA boundaries in nonidentity slots.
The live test authenticates actor draw flag0x40, removes queued emissions and
uses the owned initializer as declared input; it does not fabricate output colors.
Keep controlled hide/reveal distinct from natural scene transitions. See
`notes/native-art-late-entry.md`.

Observation helpers must resolve a binding from its class/native-bank key or
current per-object tag. A class is not a fixed slot number once variants and
absent history exist. Capture startup counters and compare controlled deltas;
earlier natural effects are legitimate history, not a reason to erase diagnostics.

For native palette reloads use `test-native-art-palette-reload` and
`test-live-art-palette-reload`. Authenticate the actual copy callback and retain
its observable return register, unit notifications and unrelated copies. Compare
active continuation against the original engine with generated colors as input;
preserve targets/errors/tasks and distinguish current colors from the DMA latch.
Retire unused history without accepting a future unknown palette. Actual
deployment is a direct consumer, covered by the narrow variants test. See
`notes/native-palette-reloads.md` for exact rejected and accepted candidates.

Instruction/ABI component tests must use an ARMv4T CPU (Unicorn TI925T), selected
immediately after creating the emulator and before memory maps/writes. A newer
default CPU can falsely accept ARM LDR-PC interworking. Absolute Thumb targets
from C need explicit typed pointers or correctly typed Thumb symbols; inspect
compiler veneers. Keep the retained bad-ROM entry-mode negative control and
actual mGBA evidence. A passing component alone cannot establish GBA execution.

For native color-operation integration, use the original pure conversion
functions for generated target colors and the established native callback
progress for interpolation. Compare installed setters with original setters on
identical input; run an independent original-engine oracle with generated colors
as its native source. Cover interruptions, argument truncation, caller-stack
arguments and explicit unsupported boundaries. Then verify actual hardware
playback with `test-live-art-color-operations`. Clone input guards must account
for exact fifth/sixth stack arguments without copying them into the live game.
See `notes/native-art-color-operations.md`.

For compositor color isolation, `test-native-art-compose-isolation` compares
installed and original entries on identical authenticated captured inputs,
including native-derived cycle phases and both palette-DMA cases. Reuse the
bounded synchronous DMA model only for write/copy correctness; it is not a
VBlank or scheduler oracle and cannot erase full-route timing/phase failures.

When a shared engine optimization changes the comparison cost, retain the old
baseline result and construct an authenticated private control containing only
the same optimization. `test-live-art-palette-status-control` copies the exact
status shortcut and pointer into the original parent, verifies every other byte,
and retains strict color and input checks. Do not describe engine-speed changes
as palette performance. The current state-only diagnostic is
`test-live-art-palette-fast-status-cost`; it avoids replaying deployment or old
passing diagnostic cases. See `notes/native-status-iterator-cost.md`.

For native inline shortcuts, exhaust the input cursor domain and added selector
boundaries, compare the original entry's live registers/stack/writes at both
stack alignments, and execute the unchanged continuation through its first flag
consumer. Authenticate instructions that make intermediate flags dead. Check the
equivalent C source with production compiler settings and real retained getter
inputs separately from controlled contract cases. `test-status-iterator-fast`
does this for the unconditional native keys and signed-byte wrap. It does not
replace class-specific status-lifetime tests or actual battle acceptance.

Optional CPU samples in the composition diagnostic read the local core's
authenticated mGBA serialization layout without reloading/changing state. Require
unchanged active position traces. Frame-boundary PC frequencies are diagnostic
locations, never CPU-cycle shares; keep core-format/provenance checks explicit.

For composition-cost isolation, use declared
`test-live-art-palette-compose-cost`: authenticate an existing report/ready
state and ROM, restore only the original compositor entry in a private control,
and require exact initial RAM/IWRAM, reproduced active position observations
and matching final native gameplay state. Keep every other hook/resource intact.
Capture per-frame native skipped-update cadence as well as movement and display
timing. This diagnostic does not accept the bypass's missing colors or replace
full active-candidate acceptance. Archive a rejected trial's exact source patch
with its private ROM and logs, restore the better candidate byte-identically,
and reuse applicable passing evidence. See `notes/native-palette-composition-cost.md`.

For native palette-phase diagnosis, authenticate both the initializer and actual
rotation callback. Test cadence/range preservation separately from scheduling.
`test-native-obj-palette-cycle` identifies OBJ418..424's getter4 source and
six-call callback, then audits every retained phase without replay. Membership
in a native rotation set does not prove matching callback timing or authorize
normalizing away a delay. Keep diagnostic and acceptance claims distinct.

Treat class identity and simultaneous native color variants as distinct axes.
Authenticate the actual native transformation and entire source palette before
creating a new variant binding; preserve source class and brightness through
fade restoration. The deployment multiplier is153/256 (equivalent to19/32 for
five-bit channels), not a similarly colored static palette. Refusal diagnostics
must separate variants, setup, target and tick failures. Prove both variants
concurrently across consecutive live frames, not only isolated palette arithmetic.
See `notes/native-deployment-palette-variants.md` and declared
`test-art-palette-variants` / `test-live-art-palette-deployment-variants`.

When a native constructor rewinds the sequence while a queued upload completes,
capture the actual prior tile-source field. The index may already name the next
command. Authenticate the captured source, prior command/layout, complete output
allocation, direct recent anchor and unchanged hardware geometry; never accept
an arbitrary matching pose. Reproduce a retained failure from its matching saved
test state and require exact failure RAM/VRAM plus negative controls. Declared
`test-native-layout-rewind-queued` complements `test-native-layout-queued-commit`.

Native unused OAM entries may be ordinary offscreen objects, not hardware-disabled
objects. Trim only a fully authenticated trailing marker and absent owner tag;
retain interior holes and later enabled consumers. Keep full-planner demand
diagnostics unchanged when optimizing a preferred-bank path.

For scoped executable IWRAM, copy a bounded position-independent leaf including
its literal pool into the active stack, preserve the ABI, and verify its exact
results from both relocated and ROM paths. Guard resident native code and keep
interrupt headroom; fall back on deep/non-IWRAM stacks. A conservative margin is
not all-scene stack acceptance. Retained native-code snapshot guards now appear
in `audit-live-art-battle-trace.py`; their scope is snapshots only. See
`notes/native-palette-scan-performance.md` for the current bounds and failures.

Reuse authenticated battle states for narrow native callback or original draw
diagnostics through declared IDs `test-native-battle-palette-cycle` and
`test-native-battle-draw-trace`. Do not infer continuous cycles from retained task
records: the native linked list pauses at menus. Trace the actual draw caller;
different HUD consumers can use different upload paths and VRAM targets.

A preferred palette bank is only a hint. Revalidate the complete current OAM
and every potentially visible unowned 8bpp pixel before applying it. Partial tiles
remain whole; affine/mosaic footprints remain complete. Refuse unsupported cases
before writes and fall back to the full planner. Last-plan demand diagnostics
must not be described as freshly measured usage. Back up allocated banks only
after validation; read untouched native colors directly from hardware.

Measure actual motion duration and input-to-action delay as well as VBlank bounds.
A run can finish its overlay within VBlank and still slow gameplay. For a complete
retained paired battle trace, run `scripts/audit-live-art-battle-trace.py` with
its `failed.json` or `report.json` path. The derived audit pins source/script hashes,
evaluates all samples past a fail-fast assertion and remains failed on discrepancies.
It does not create fixtures or rerun playback. Reuse byte-identical ROM evidence
after reverting a slower trial. See `notes/live-palette-preferred-bank.md`.

Treat native palette-DMA suppression separately from disappearance of sprites.
FFTA repeats ordinary battle frames with03000E10 set; restoring and removing a
custom overlay on those frames produces flicker. Keep the displayed custom phase
latched to actual native palette transfers and prove the repeated-frame consumer.
Menu216F8 and battle8F1F4 are distinct actor renderers; hook and authenticate their
actual emissions independently. See notes/live-battle-palette-lifetime.md.

Profile before moving code between instruction modes. An ARM routine in ROM is
not automatically faster. Exact tile-byte caching may reuse masks only after full
byte comparison; a geometry key or hash alone is insufficient. Measure both steady
frames and sliding/appearing UI, and retain failed scan/display wraps. Longer test
button holds do not accept responsiveness regressions. Preserve exact cycle-phase
failures until native ownership/timing supplies an independent explanation.

During a bounded native layout reset, a pending command can finish uploading.
Require the exact previous pending command, direct recent anchor, complete expected
allocation and unchanged hardware geometry. Canonicalize only authenticated owned
palette nibbles for geometry comparison; retain actual OAM/colors separately. Reject
arbitrary pose matches, unqueued changes, altered pixels or stale anchors.

Explicit animation sheets use `generated_action_transport.build` with an
`animation_plan` JSON. Schema 1 names authenticated PNG sources/conversion
settings and `(job,lifetime,slot)` assignments with exactly the native frame
count. Frame references select an asset and zero-based source cell. Preserve
native timing/commands and align each image to the native frame baseline.
Partial coverage preserves unmapped temporary transport; complete coverage
requires every present land/water slot for declared jobs. Coverage never grants
art acceptance. Build with `publish_current=False` for private proofs. See
`src/art/imagegen/samurai-walk-transport.json` for a labeled draft example.

Key conversion output folders by source PNG hash, all conversion settings and
exact palette hash. Asset names such as `walk` recur across revisions and cannot
identify immutable evidence. Record exact prompts and input roles, retain PNGs
as pinned build inputs, and compare native-scale conversions before runtime.
The explicit-plan/walk scripts accept `--plan`/`--current` selections for named
draft checks; declare each intended run in the plan. Reuse same-ROM runtime
evidence when only conversion storage/metadata changes.

Separate palette loss from shape/pose defects with same-source, same-crop,
same-scale conversions into the actual consumer palette and a generated15-color
comparison palette. The latter demonstrates only color feasibility, not native
allocation. Record both palettes/hashes and visual findings; do not fix a shared
palette by overwriting vanilla colors. For motion review, compare A/B/C/B loops
at native cadence, label any GIF timing approximation and keep review composites
distinct from actual game captures. Pixel-difference counts alone cannot accept
motion or costume continuity.

Palette allocation must consider a complete frame, not only the target actor.
4bpp OAM uses a bank nibble;8bpp OAM ignores it, so account for every nonzero
pixel index in its actual tile footprint. `art-palette-plan` implements a bounded
1D frame primitive with caller-authenticated custom owner tags. Supply fresh
native palette/OAM inputs for each application; owner discovery and restoration
are separate integration duties. Refuse unsupported layouts or exhaustion without
writes. Never turn a slot unused in retained captures into a global reservation.
Native216F8 uses context byte9 plus actor1C/1D for palette offset; byte10 is
priority. Preserve that distinction when intercepting the renderer.

Track custom ownership at native emission, reset it with the same OAM bank, and
translate through actual 12BC composition. Hardware indices are not persistent
actor IDs: native priority/UI groups shift the main actor span and can clip it.
Authenticate attr0/1/2 against the emitted snapshot; attr3 belongs to native
affine matrices. `art-palette-owners` implements this bounded bridge with
caller-owned storage. Its synchronous DMA test proves ordering, not live timing.
Do not claim global RAM or palette restoration from the helper alone. See
notes/native-actor-palette-ownership.md for native addresses and reproduction.

Live palette stages must reserve their transient RAM through every relevant heap
limit and preserve native clear-owner retirement at the new boundary. Never
borrow apparent free bytes. Native 147A44 transfers the complete palette shadow
before OAM composition; its caller also skips this on ordinary repeated frames.
Restore prior overlays before native updates, reapply the displayed custom phase
when DMA is skipped, keep native shadows unmodified, and verify full
paired hardware colors outside the exact owned bank. A menu cancel can leave a
header actor visible: follow actual ownership until the consumer disappears.
Measure live timing; isolated instruction tests do not establish VBlank fitness.
The current lookup accelerates exact 8bpp demand but has limited sampled margin.
`build-live-art-palette.py` creates a private stage; do not silently replace the
packaged art pipeline. See notes/live-dark-knight-palette.md for proof and gaps.

Sample transition frames as well as steady views. Record the scan finish and
actual native display-enable VCOUNT; finishing a helper does not establish that
the remaining native VBlank work fits. Treat native03000E10 as a consumed
one-frame DMA-suppression request, including ordinary battle repeats. For8bpp
demand, fully off-screen normal tiles
may be omitted with correct signed coordinates/flips; keep partial tiles and
affine/mosaic footprints conservative and validate against a pixel-coordinate oracle.
Do not relax paired native color equality to conceal an introduced frame delay.

Native fade behavior must be compared with original setup and callbacks, not
inferred from approximate color ratios. art-palette-fade supplies exact RGB555
interpolation with caller-owned storage and bounded durations. It neither
reserves that storage nor discovers native effect targets/owners. Prove the
live target, binding, interruption and release paths separately; a menu trace
with zero observed fade endpoints is not fade acceptance. See
notes/native-palette-transitions-and-fades.md for current evidence and limitations.

Capture an actor's original native palette bank at composition before changing
its OAM bank nibble. A later snapshot can already contain a reused source buffer.
Bind custom fades to actual native effect task identity and invalidate on overlap
or task reuse. Preserve r3 for four-argument native entry hooks; test real table
pointers/flags through the trampolines. Unknown target operations must remain
explicitly unfinished, not guessed from color ratios or silently marked passed.

Controlled native-command tests can execute a setter on a paused-state clone and
transfer back only its declared palette/effect and private binding writes. First
verify all other bytes unchanged; exclude test input scratch and clone stack.
Then let the actual game execute its callbacks and DMA, comparing native and
custom hardware colors at the same observed phase against original callbacks.
Distinguish this proof from a naturally triggered scene/campaign event. Record
whether cancel/reopen actually reloads the bank or retains its faded state.
See notes/live-native-palette-fades.md for the bounded implementation and gaps.

Test the actual selected race/class movement instead of assuming dedicated walk
mode numbers. Human Samurai uses native manual phase selection on shared
idle/march slots 0/1. Native 08021E28 clears the timer and selects current index;
the frame verifier requires exact manual flag/current/source/layout and pixels.
Brief layout resets require a recent direct anchor with identical full VRAM
allocation and hardware OAM; label retained display separately from fresh
upload. Never widen a verifier merely to accept a failed observation: authenticate
native behavior and retain bounded negative controls and failed reports.

Use built-in imagegen for artwork; code only extracts/converts/imports pixels.
When the user defers sprite polish, use existing generated drafts as labeled
technical inputs and continue consumer proofs without calling them finished.
Keep provider comparisons separate; do not resume discontinued external calls.

Menu figures use the native A7 dictionary codec, distinct from actor sequences
and small job icons. Export32x40 images (640 bytes), preserve all original
entries and append private images. Extend the actor-to-image table for wide
resource IDs. `native_miniatures.py` handles the format; the declared native
decoder test checks actual ARM code, count/range semantics and write bounds.
For displayed menu proof, verify enabled OAM, actual palette, exact expected
figure bytes and complete surrounding VRAM against authenticated captures.
Do not assume a battle/icon palette applies to a menu; record the actual source
and baseline alignment in the import manifest. The current Samurai wheel uses
bank4 with opaque bytes matching ROM0x94ee5c, unlike its battle/icon reference.

`build-art-pipeline.py` composes isolated stages without replacing existing
component pointers. `--manifest build/art/pipeline/current.json` selects that
candidate in shared test consumers. The seven `test-art-pipeline-*` consumer
IDs cover icons, native preview, party, Buy, Sell, miniature and battle. Run
only changed paths except at a justified combined milestone. The separate
rebuild step reproduces every selected image conversion and art-source stage;
it reuses the unchanged verified v0.7 base. Original generated PNGs are pinned
build inputs; regenerating artwork from a prompt is not deterministic.

Packaging requires successful exact-candidate consumer and rebuild reports,
freezes their hashes, and proves BPS roundtrip and wrong-source rejection.
Run packaging after the rebuild runner has finished writing its report.
Launcher validation checks a separate save/state/screenshot folder and rejects
wrong ROMs without starting mGBA. Use .NET hashing in Windows PowerShell as in
the existing release launcher; Get-FileHash is unavailable in this environment.
Keep partial technical delivery labeled and leave complete-art gates open.

For wider actor IDs, audit every consumer's intermediate storage, not only the
native job getter and animation tables. Generic animated menu headers use a
different path from static roster/wheel images and fixed story-character art.
Use existing generic members from all five races; verify the selected roster
pointer before comparing output. Established roster traversal is Down once for
slots4/5 and Right(slot%4), then A. Reuse existing authenticated fixtures.
The native generic menu widget currently stores its resource byte at+0x1085;
adjacent fields are occupied. Preserve complete creation/update/teardown lifetime
and adjacent bytes when extending it. An exact native frame uploaded from a
truncated wrong resource is still a failure, even if OAM and palette match.

## Resource containment and retention

For a user-authorized art council, reviewers inspect authenticated source sheets
and explicitly name the native conversions/consumers they reviewed. Preserve
per-class identity, continuity and game-size findings with one-based review
coordinates. Keep visual review distinct from runtime acceptance. Root alone
owns a separately authorized gallery's Site checkout, credentials and publishing.
Authenticate copied generated assets from src/art/imagegen/catalog.json; exclude
ROMs, saves, original extracted graphics and local tools from shared galleries.
Use separate labels for design drafts, unfinished conversions and import proofs.

Every runtime step started by `scripts/run-expansion-tests.py` and every stage
of `scripts/rebuild-expansion.py` runs through `scripts/resource_guard.py`:

- Admission guard. Before locking the workspace, and again before each step,
  the runner refuses when the build volume has under 40 GB free, under 8 GB of
  physical memory is available, or commit headroom is under 16 GB. The refusal
  names the limit. Override deliberately with `FFTA_MIN_FREE_DISK_GB`,
  `FFTA_MIN_AVAILABLE_MEMORY_GB` or `FFTA_MIN_COMMIT_HEADROOM_GB` only for a
  bounded diagnostic, and record the override in the checkpoint.
- Process-tree containment. On Windows each step and all of its descendants
  join a Job Object at below-normal priority with a job memory ceiling
  (`FFTA_STEP_MEMORY_LIMIT_GB`, default 24). A timeout terminates the whole
  tree. Each step reports `peakMemoryMB`; the run report records the
  resource snapshot before and after.
- Retention. After each run the runner calls
  `scripts/prune-build-outputs.py`, which keeps every report, log and manifest
  and removes only regenerable bulk: ROM images, emulator states, RAM dumps and
  screenshots of integrated candidates other than the current one, the newest
  spare and any named by a plan; emulator captures in unreferenced probe
  directories; and the private workspace copy of all but the newest clean
  rebuild. `--dry-run` shows the plan first. `rebuild-expansion.py` removes its
  own workspace after writing the report unless `--keep-workspace` is given.
- Generated build outputs are not permanent evidence. Evidence is the
  report, its hashes and the logs; a stale candidate's image can be rebuilt
  from the recorded source commit and pinned toolchain.

The emulator harness `close()` is idempotent, releases the native core, and
drops its ROM buffer, frame, memory-map pointers and callbacks; use the
instance as a context manager for lifetime-sensitive checks.

For clean-source assembly, use `Build Expansion.ps1` as documented in
`REPRODUCIBLE-BUILD.md`. It creates an isolated workspace from source, pinned
tools and the clean ROM, with no generated inputs inherited from this checkout.
Use `-CompareCurrent` to establish byte equality with an already-tested image;
do not replace existing gameplay evidence with a build-only pass or rerun it
solely because the identical ROM was reconstructed elsewhere.

Use `IMPLEMENTATION-CHECKLIST.md` as the authoritative current backlog. Update
it with each accepted implementation checkpoint, preserving stable item IDs
and distinguishing missing implementation from missing verification. Check off
only the stated scope with appropriate evidence; keep partially completed
items open with their remaining work. Add newly discovered gaps there. Keep
test chronology in `IMPLEMENTATION-STATE.md`, not in `AGENTS.md`.

For graphics work, separate pure composition/pixel checks, all-content capacity
bounds and live allocation/lifecycle acceptance. Compile a detached pure module
for localized checks without rebuilding unrelated game code. A safe capacity
bound must include arbitrary relevant overlap, partial-scroll margins and all
animation streams, independent timing and partial transfers; a uniform board
screenshot is not a worst-case proof. Preserve native visible unloaded graphics
by authenticated snapshots rather than inventing zero-filled source data.
Treat proposed reclaimed tilemap space as occupied until its native writer and
background ownership are replaced. Keep the live integration checklist open
even when a detached frame builder and its capacity bound pass.

For animated graphics, distinguish controller tick, source DMA, composition
and publication. Compare published pixels with an independent native producer
and require stationary-camera changes plus a final drain after ticks stop.
Observe expensive-call entry directly when claiming it stays outside VBlank;
a postcondition or instruction count alone does not prove timing performance.
Install instrumentation before the first execution of its target, and assert a
known positive call is observed before trusting negative observations. For CPU
cost, use an isolated deterministic GBA-timer benchmark with the game's actual
WAITCNT and compare real function outputs; distinguish this from whole-game
responsiveness. Keep the benchmark driver, explicit RAM inputs and ROM/output
hashes reproducible, and state which emulator subsystems it disables.
When the concern is player responsiveness, measure from the fixed input to the
actual native phase and rendered-menu readiness. Keep stabilization waits out
of that interval, compare a control that disables only the optional display,
and record latency separately from gameplay-state equality. Passing functional
comparison does not erase a measured slowdown. Batch allocation-sensitive UI
and cold-save checks after a completed memory-layout sweep; reuse those results
for later arithmetic-only refinements unless evidence reveals a new lifetime risk.

Treat display caches as optional users of native memory. Total free bytes do
not prove a large native allocation can succeed: inspect contiguous blocks and
constructor order. Let native scene buffers settle first, prevent immediate
cache recreation during resource-heavy work, and test both reclamation and
recreation through the real allocator. Keep visual presence and gameplay-effect
persistence separate when documenting graceful degradation.

For multi-slot save tests, record the native selector's initial remembered slot
and its wrap behavior. Distinguish serialized emulator state, EWRAM captures and
explicit SRAM: authenticating a state file does not establish that a fresh core
has loaded its flash data. Resume a completed save from the preserved native
SRAM, record its input hash and prior report provenance, and use fresh boots for
independence checks. Failure capture must tolerate no rendered frame yet.
For ending-save tests, distinguish live state from the staging block read from
the selected saved slot. Start native event tasks only with an active scene
scheduler, and observe task execution separately from constructor invocation.
Save writing, completion-dialog dismissal, parent-scene return and a cold load
are separate acceptance points. A synthetic scene can establish the first two
without proving the real ending return; preserve that limitation explicitly.
Inspect the native terminal branch before asserting a parent acknowledgment:
a clear-save task may intentionally reset to title instead. Authenticate and
resume the saved dialog endpoint, including its SRAM separately, to verify
title/Continue and loaded-clear consumers without replaying the passed save.
Keep natural campaign entry into that task as separate milestone evidence.
Before writing an expected UI branch, inspect the original capacity/eligibility
gate. A missing offer can be correct native behavior. Separate eligibility from
the actual controller admission and preserve original rules. When a results
screen closes, distinguish its legitimate AP/reward writes from identity/copy
corruption; use a paired scenario or an independent reward oracle. Resume plans
must retain every required earlier checkpoint, not only the latest one.
For current-candidate acceptance, import only reusable helper definitions from
older test modules. Importing a test must not silently execute an unrelated
suite. Never overlay a historical engine binary onto the integrated image and
call that current-build evidence. Parameterize the existing oracle's image input
and authenticate the actual ROM/capture; keep legacy reproduction available.
For a downstream playback consumer, authenticate its successful producer's
report and required artifacts instead of making that producer a mandatory
runtime dependency on every invocation. Preserve per-owner/per-case checkpoints.
A completed miss can prove menu return, but not a successful-hit animation;
add only the missing positive control and retain the original miss. Once a
bounded deterministic search identifies a positive seed, use that seed directly
for routine reproduction. Catch final aggregate-coverage failures in the report
as well as individual case failures.

For native menu/lifecycle tests, follow the active command set rather than
assuming every form offers Fight and secondary skills. Confirm the real facing
endpoint before expecting coordinate commits. A same-square Move can cancel
instead of consuming movement. KO may skip facing, and Sleep can make the same
actor receive consecutive ready turns; actor identity change alone is not a
universal completion predicate. Additional native menu rows may move exact text
anchors in both axes. Validate the translated strokes/outlines against retained
frames rather than loosening the thresholds. Distinguish mandatory territory
placement from the normal world/system menu before attempting a save.

For a long playback failure, retain the last good state and isolate the failing
transition with a short deterministic script. First distinguish incomplete
animation/input timing, an allocation failure and an actual CPU exception;
do not extend waits to hide a crash. Use declared A/B controls, record exactly
what the diagnostic changes, and keep those controls in a separate diagnostic
plan. Reuse the passed prefix and unchanged build rather than starting over.
For UI comparisons, make any control's single disabled behavior explicit and
compare native states/results as well as relevant static text pixels. Preserve
passed cases from a partially failing run; rerun only the corrected subset.
For a continuous transaction test, checkpoint after payment, collection and
other meaningful phases. Preserve candidate/seed/state/RAM hashes and the
previous report hash when resuming. A failed later phase must not invalidate
or replay the completed prefix; keep failed reports failed. Distinguish native
tentative selection from committed state using the actual debit/assignment
invariants. Native menus may skip empty categories: locate the intended item
in a bounded native list rather than hardcoding a relative tab offset.
For resumable player-flow batches, retain completed case artifact paths and
the source report hash; authenticate the candidate and instrumented image
before selecting unfinished player/cold cases. Leave earlier failed reports
failed and describe the combined evidence explicitly. Once a bounded RNG
search finds its positive control, commit that fixed seed for routine
reproduction instead of repeating the exploratory sweep.
A text-color observer can reject a correctly selected orange command, and
formation changes can occupy a previously valid Move destination. Diagnose
those separately from native execution or graphics failures.
Preserve native camera-stream origins; hardware scroll offsets are a separate
consumer. Observe native menu readiness before submitting dependent inputs.
When a case needs another race, declare that clan profile before native battle
construction so the game creates matching sprites, wrappers and turn order.
Keep it in a separate hashed fixture cache; do not rewrite races on existing
battle wrappers or regenerate the ordinary fixture. Distinguish cast-before-Move
from move-then-cast: the former returns to a menu with Move still enabled and
needs explicit Wait/facing inputs to finish the turn.
For display/control combat comparisons, menu timing can change the native RNG
stream even when formulas are identical. Declare the same seed at the actual
executor boundary, preserve its calling contract and record the test-only ROM
patch/hash. Preserve misses as valid native outcomes; a scenario intended to
exercise positive damage must identify its seed rather than force an outcome.

Current workflow: all delegated handoffs are finished. The primary agent works
alone in substantial implementation sweeps, using localized deterministic
checks selected by change impact. Full integration runs are major milestone
and final acceptance gates, not a per-batch or per-commit routine. The worktree
procedures below remain as the recorded isolation method; they do not authorize
another wave of agents.

For acquisition audits, distinguish candidate generation, visible posting,
acceptance and saved history. A hidden template or repeat bit is not a player
access route. Use the complete native queue generator and consumer with declared
eligibility inputs; trace completion into the next route where applicable.
Honor native cooldowns before expecting expired offers to be removed. Identify
history flags from their writers as well as their readers: an acceptance receipt
that blocks later absence is not necessarily a dedicated death flag. Preserve
passing consumer evidence while checking the remaining transition separately.

For connected progression tests, distinguish battle/story receipts from scene
execution and territory placement. Begin with authenticated opening history,
earn subsequent flags through native consumers and record controlled outcomes
and selected calendar/location inputs explicitly. Native mission acceptance
does not include the pub's earlier selected-item binding: execute that original
binding step before claiming consumption. A fully placed, mostly story-only
profile can saturate the native64-offer queue. Free capacity through documented
native completion/expiry, not by deleting cached offers or inserting flags.
Record connected stage captures and their hashes for downstream milestone tests;
do not replay the earlier source/stock matrix merely to create another fixture.

For installed-content reconciliation, read current native table pointers and
compare approved source contracts, rather than validating only historical probe
manifests. Check shared-race lesson/help assignments explicitly. For an isolated
text patch, reconstruct all permitted changed bytes and compare the complete ROM
with its tested predecessor. If code, combat data and memory layout are unchanged,
use native text routing/decoding and formatting checks; retain unrelated gameplay
evidence instead of recreating battle fixtures solely for the new ROM hash.
For semantic review, distinguish an explicitly rounded base from later combined
modifiers. Derive weapon-family checks from approved equipment categories and
native item records, rather than copying a shared helper's existing constants
into the test oracle. Include command admission, state ownership and dependent
reactions when changing that helper. Native accuracy tests must observe hits and
misses and include nonvacuous controls; a fixed seed is not a promise of success.
Keep completed independent test sections when only the final section's harness
needs repair, retaining the failed original report and a separate continuation.
New weapon permissions require actual racial actor-pose playback: a native
formula and valid item category do not prove that the race has that animation.
Use a supported pose only at the presentation selector, retaining real weapon
properties for other consumers, and compare all affected race/job identities.
Shared bootstrap source is historical and pinned. Modern fixes to its behavior
belong in a compiled final-layer override with an authenticated old binding;
do not compile modern job-state-dependent source as the standalone first stage.
See `REPRODUCIBLE-BUILD.md` for clean assembly and
`notes/mystic-knight-cold-lifecycle.md` for the saber example.

For ordinary AI work, separate native discovery/admission, recipient rows,
area placement and complete autonomous turns. Admission bytes inherited from
an item donor need explicit review for a nonconsumable command. A placement
callback cannot establish discovery or affordability by itself. Preserve native
consideration probabilities; a legal utility spell need not be chosen on every
seed. If a positive case is missing, trace discovery and the actual considered
recipient before replaying more whole turns. Declare a reachable support
situation and seed, never a chosen command or outcome. Keep passed cases and
rerun only the missing subset. Native working objects may be heap allocations;
read their owning pointer instead of assuming an adjacent fixed address.
Placement harnesses require distinct friendly/opponent groups and native
center-list buffers. Keep scoring pure and small: an extra full prediction can
exhaust IWRAM stack even when isolated row checks pass. Pair low-stack guards
with one relevant complete turn. Exact-ROM captures are preferred; help-only
reuse requires full allowed-byte reconstruction, retained input/output hashes
and separate reporting of capture and current ROM hashes.
For ordinary native area search, order those groups by the consumer contract:
BE5F4 uses intended recipients first and collateral recipients second. Harmful
actions and beneficial actions therefore use opposite faction ordering.
Derive status/command flags from the native caller and selector, including
whether a bit is an allowance or a prohibition. Direct executor success under
a status does not prove menu/discovery admission; check both, including legal
secondary commands. Older playback scripts must wait for native menu readiness
after movement before supplying dependent inputs, rather than assuming a fixed
frame delay still suffices on a later build.

For acquisition audits, keep item possession, an accessible source and a
completed acquisition as separate evidence. Decode special/unaligned records
through their native consumers; a reward-pool entry without a live caller is
not a source. Record unresolved event selectors instead of silently dropping
them. Compare lessons by racial AP record, not just their displayed names.
Use `audit-vanilla-teaching-sources.mjs` for the rare vanilla gear ledger and
`test-vanilla-clan-gifts-cached` only when the gift consumer or its inputs change.
For repeatable acquisition, follow the native disposal/release/reaward consumers
before adding replacement content. A filled slot is not a permanent grant flag.
Keep declared unit metadata, direct native consumers and real player-input
playback distinct in reports. Reuse hashed cold-world inputs when they supply
the needed state; a source audit does not require a new battle capture.
Authenticate table indexing through the native selector and record consumer,
not a third-party editor's shifted layout. Keep map/deployment formations
separate from enemy formations. Native formation IDs1..442 use
`54CD54 + 40*id`, count+0 and unit pointer+4; `A024` selects event+4 when present.
See `notes/repeatable-encounter-access.md`. A corrected source label can retain
unchanged unit-template combat evidence, but must replace the old encounter
attribution and verify the newly identified route. Native completion chains
must carry their own flags into the next offer and honor posting cooldowns.
Keep controlled completion outcomes distinct from actual battle victory.
Read-only source ledgers are test consumers, not assembly inputs. Explicitly
classify such files in prerequisite reuse only after checking that no builder
or fixture consumes them; do not weaken checks for actual production inputs.

Native combat arguments require caller evidence: a variable named `index` is
not proof of weapon-hand identity. Verify its producers and branches before
attaching per-hand effects; identical dual weapons need the actual iteration.
Also authenticate ordering: native Fight sorts weapons by attack, so iteration
zero is not necessarily the first equipped weapon. Preserve that identity
through nested read-only formulas without granting queries mutation rights.
See `notes/mystic-knight-fight.md` for the tested carrier contract.
For late consumers such as Judge reporting, preserve the original component
identity in manager-owned temporary storage and authenticate the native result
rows. A reaction may clear the live status before reporting. Observe committed
results before native retirement; do not reconstruct success from current unit
state. See `notes/mystic-knight-fight-laws.md`. When adding a workspace slot,
include its zeroing, reuse and retirement in the allocation matrix; use a
cached targeted run when production inputs and captures are unchanged.
For custom effects, record the successful setter event rather than the current
status or a before/after byte difference. Refreshes can leave identical bytes;
later reactions can remove the effect before Judge reporting. Preserve exact
result-row ownership, and classify effects against native law groups before
inventing status aliases. A native unit in another party slot needs that slot's
AP sidecar stride, not Marche's address. Keep actual cast observation bounds
consistent with the relevant animation. See `notes/custom-status-laws.md`.
Trace predictive consumers before assuming they belong to player menus: native
AI law flags and late Judge reporting are different paths. An encounter with
no Judge can correctly skip AI law flags. Declare Judge presence as a fixture
input and let native enumeration/admission decide; never supply the result.
For elemental law integration, distinguish static action metadata from dynamic
damage-element hooks. Correct fixed metadata directly; preserve executed
choices or consumed fuel in authenticated result storage for late consumers.
The native law's item-used boolean is not a choice or equipment ID. Verify
actual native operand publication, foreign-mask rejection and the real late
caller; see `notes/carrier-law-audit.md`.
Classify item costs, primary-weapon delivery and HP/MP law domains separately.
A native weapon-mode flag can omit a required weapon on utility techniques;
a recipe can consume inventory while the native Item boolean stays false.
Verify both pure selectors and representative actual late callers. If a menu
rejects an empty area before payment, retain that boundary instead of forcing
an invented recipient; do not generalize it to untested executor/AI paths.
Preserve completed playback prefixes and rerun only a corrected setup case.
A successful immutable build/capture chain can be reused even if its native
comparison test needs a correction. `verify-integrated-build-prerequisites`
certifies only those eight preparation steps; run `test-integrated-native-cached`
to establish the missing comparison without rebuilding. Ordinary cached tests
still require the normal verifier, which joins that exact ROM's passing native
report with matching source/compiler/build/capture fingerprints. Neither mode
certifies an unrun consumer. Preserve failed reports and explain any exact
expected-memory adjustment; never hide a new receipt behind a broad RAM mask.
For noncombat content checks, `verify-integrated-assembly-prerequisites`
certifies the exact six-step ROM assembly and source/compiler fingerprints
without creating battle captures or running combat comparisons. It does not
certify those omitted consumers. Use assembly-only cached tests for pub/text
and mission-native cases whose inputs do not require battle fixtures. A changed
ROM hash alone never justifies an unrelated combat run. Retain the failed
consumer report when reusing successful immutable assembly.
A native command menu can start on its first enabled choice rather than row0.
Use the observed initial selection when declaring fixed scroll inputs, and
assert the selected action and operand before execution. Preserve setup failures
as test evidence without attributing them to the game.
When an action combines self and hostile modes, verify actual native target
admission separately from executor eligibility. Keep weapon-free self metadata
and hook only the hostile formula consumers that need primary-weapon terms.

Native self-action forecasts can contain two distinct evaluated copies of the
same unit. Use authenticated source-origin identity only in query contexts;
retain pointer identity for execution and reject unregistered byte copies.
A candidate descriptor mask is not a defect until actual result publication
proves it. Empty terrain effects can complete without a recipient: preserve
native Judge hit/recipient gates while checking payment and placement separately.
For effect prediction, check native eligibility, accuracy and application
separately: Immunity can express prevention as zero accuracy. Use the verified
status whitelist rather than a name-based assumption; Slow is not native
Cureall/Immunity coverage. When a test oracle is wrong, retain its failed report
and rerun only corrected/added cases against verified unchanged prerequisites.
Document the union of retained and follow-up coverage explicitly. See
`notes/mystic-knight-fight-prediction.md`.
For nested forecasts, track the actual native caller stack depth and protect
IWRAM executable bytes in deterministic query checks. Several individually
valid stack objects can overflow when composed. Borrow existing authenticated
query storage where appropriate; preserve real result publication separately.
For status-law possibilities, average damage is not proof of certain defeat.
Use native variance bounds before custom factors and retain the observed
execution that exposed the boundary. See `notes/mystic-knight-resources.md`.
Keep actual-execution call depth unchanged when extracting a heavy query
fallback: a new wrapper frame can break rendering even when shallow native
checks pass. Dispatch in an existing wrapper and run the affected whole native
flow, including an ordinary-action control with the new lesson unavailable.
If a linked code region reaches its bound, place job-specific helpers in its
already reserved region and test the direct shared consumers; do not silently
move tables or another job's reservation. See `notes/mystic-knight-ai.md`.
For AI correctness, verify both the candidate row and detailed score; a
positive removal bonus can hide failed native damage admission. Carry selected
operands through an authenticated actor/action scope when native admission
constructs a weapon-based context. Include a no-op/refresh control for
self-benefit decisions and preserve player eligibility separately. For full
battle controls, preserve native faction membership: a unit control-bit edit
alone does not rebuild cached team lists. Use formation/range changes when
that isolates the intended behavior. Save playback summaries per run/case and
log a completed prefix on failure so targeted reruns cannot erase evidence.
Dispatch to a separate search before allocating unrelated large local matrices.
Use the native node buffer or an existing authenticated forecast bank for heavy
scratch, respecting actual allocation bounds. For AI playback, seed planning
at its input boundary separately from combat rolls; an executor seed does not
vary earlier native willingness. A first active-unit frame can still contain
the previous unit's completed AI node. Advance native setup before replaying
that planner, and verify embedded-structure offsets from callers. Do not reset
the planner onto a guessed movement map or treat such a replay as a defect.
Before repurposing a native AI field, inspect its later consumers: a sorting
field may also gate random willingness. Prefer moving complete candidate
records while preserving probability, law flags and native admission. Native
void routines can leave the return address in R0; verify actual caller-visible
ABI and memory rather than incidental caller-saved values. Separate custom
helper context purity from original native query-context publication.
A retained-capture diagnostic is a test consumer, not a build dependency;
explicitly classify only verified consumers in prerequisite reuse. Native
planning replays must retain movement maps and other setup from skipped phases.
Do not treat an incomplete replay as evidence of a gameplay defect.
For paired-action menus, distinguish selection indexes from execution indexes
and confirmed coordinates from stale future operands. Bind to the exact live
native targeter and caller; do not lend old selections to generic forecasts.
Test both the native formula caller and a real positive reaction through the
renderer. Small context backups also count toward the nested stack budget;
use already owned heap scratch when needed. Clear declined query snapshots
before returning borrowed slots. Reuse retained setup captures for bounded
input diagnostics, and wait on the deterministic native menu observation after
movement instead of assuming animation duration. See `notes/mystic-knight-shell.md`.
For mixed native area spells, use each action's actual area shape when defining
included/excluded controls; a summon need not share a basic spell's cross.
After menu cancellation, native cursor positions may be remembered. Separate
first-entry inputs from re-entry inputs, and check actual displayed values after
re-entry so stale controller data cannot produce a vacuous cancellation test.
For pre-battle choices, distinguish editable assignment menus from read-only
AP browsers. Reuse the real lesson/help identity and commit saved preference
only on native confirmation. Import private-module hooks into the central
composer explicitly; compiling a module alone does not install its UI. Test
unequal resource stocks to prove a no-substitution rule: equal empty stocks
cannot expose an unintended fallback. See `notes/chemist-preference.md`.
For terrain rendering, compare projection and per-quarter occlusion with the
native submission routine before allocating display resources. Native world
depth and the renderer's later tile-depth operand can differ. Declare canvas
bounds separately from mission bounds when reusing map components. Hash-retained
native captures support targeted follow-ups; passing geometry does not prove
visible rendering or ownership of apparently unused video memory. Capacity
audits must cover mixed placements, not just uniform effects. Distinguish a
conservative upper bound from a reproduced legal overflow; retain both failed
assumptions and later refinements. No acceptance follows merely because an
audit calculation completed successfully. See
`notes/geomancer-field-presentation.md`.
For reaction capability, compare against native status masks rather than
assuming restrictions from translated status names. See
`notes/mystic-knight-parry.md` for the corrected Fight investigation.

For completion content, first build a semantic dependency ledger from the
hash-checked original and current tables. Distinguish required from consumed
items using native code; count direct rewards separately from availability.
A repeatable bit alone does not prove a surviving campaign source, and finite
supply alone does not prove a lockout. Check native prerequisite/calendar/link
conditions and remaining consumers before adding recovery. Keep generated
reports ignored and maintain the reviewed ledger as source documentation.
For repeatable recipes, use fixed-point ingredient closure: only supplies with
already-proven ingredients may enter the next layer. Keep a witness for each
choice and exclude conditional recovery services. Acyclic ingredients and
positive prerequisite tests do not prove natural progression or flag lifetime.
Trace unknown flags through native writers before treating them as item or
link requirements. Pub rumor history uses0x500|topicID; topic IDs and quest-item
IDs are separate namespaces. Validate topic retirement separately from the
history flag. For multi-day dispatch playback, close ordinary arrival menus
before moving the world cursor again; a blocked cursor may be a menu state.
Different native mission result consumers can write completion independently.
Cover event results and cached dispatch retirement, plus distinct success and
failure cooldown fields. Full caches can invoke original posting eviction;
optional recovery should wait for free space. Keep conditional earned-copy
services separate from independent renewable supplies in dependency reports.
Native constructor/retirement tests do not prove fee payment, reward dialog
confirmation or save persistence; retain those as explicit player-flow checks.
Trace the real Yes branch and debit order before placing an acceptance guard;
a later acknowledgment may already follow payment. Native pub enumeration can
change offer state while displaying it, so stale pruning must cover both
displayed and undisplayed offers without touching active dispatches/cooldowns.
Reuse hash-verified accepted-world captures for downstream return tests rather
than reconstructing the same pub flow for every reward variant.
For full-bag rewards, use native Swap/OK and explicitly confirm the discard
choice (default No). Compare the entire quest inventory, then save/cold-load
each retained/rejected outcome. Reuse those hashed cold captures to test
cooldown/duplicate suppression in the actual pub. Compare mission-completion
bits separately from ordinary world/event flags that legitimately advance.
Verify native iteration bounds and packed-field getters against actual callers;
legacy helper counts and format comments can be incomplete. Distinguish posting
predicates from queue insertion, acceptance and actual campaign reachability.

The repository contains source, design and test scripts. ROMs, saves, compiler
downloads, generated builds and test captures are local ignored files. Nothing
is published. Before committing, run `scripts/check-git-content.py`; the local
Git pre-commit hook also runs it. Commits authored by this assistant use the
explicit local identity `Codex <codex@localhost>`, not an invented user identity.

## Isolation and prerequisites

Each job has a branch and a real Git worktree under `.worktrees/`. Run
`scripts/setup-job-worktree.py <job>` with the installed Python from the primary
checkout after committing prerequisites. It copies, rather than links, the
clean ROM, accepted engine, generated tables, native executor captures, fixed
early-town test save, compiler and emulator dependencies. It never reads the
player saves. A private `.local/worktree-seed.json` records original and local
file hashes, including relocated local pointers. Assets remain ignored.

The accepted assembled base is ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7.
The shared current source additionally builds the private Samurai b6da candidate.
Keep this distinction: rebuilding the main engine from newer sources is not
reproduction of the frozen accepted engine. Job work starts from the local
Samurai candidate produced by `scripts/build-samurai-probe.py`, retaining the
already integrated foundation and effects. Source and fixtures accompany the
base; no agent needs campaign play to reach a test battle.

Every worktree has its own compiler copy, emulator process, fixture output,
test logs and runner lock. No links to parent outputs and no player window.
The root coordinator verifies prerequisites and runs a build, native execution
checks and fresh headless battle preparation in each worktree before dispatch.
This proves the workshop runs, not that the assigned job is implemented.

## First implementation wave (completed handoffs)

| Branch/worktree | End-to-end ownership | Reserved ROM offsets |
|---|---|---|
| jobs/dark-knight / dark-knight | DRK: both Human and Bangaa, all 14 lessons | 0x1200000–0x123FFFF |
| jobs/viking / viking | VIK: Bangaa, all 14 lessons | 0x1240000–0x127FFFF |
| jobs/chemist / chemist | CHM: both Nu Mou and Moogle, all 15 lessons | 0x1280000–0x12BFFFF |
| main / primary checkout | Samurai completion, common infrastructure, integration | Existing allocations |

During the first wave, root supplied shared status persistence and copy
ownership. Dark Knight supplied the common action-context prerequisite as a
separate source commit, coordinated with the other jobs.

Shared prerequisites are versioned dependencies. Root validates and commits
common changes, then each job adopts that exact source commit in its own branch
and reruns affected deterministic checks. It must not read mutable parent build
outputs. Record the adopted prerequisite commit and local rebuilt ROM hash in
the job's status. Do not merge unrelated unfinished job code to obtain a common
prerequisite. `notes/shared-job-allocations.json` coordinates new descriptor and
application IDs; table relocation must preserve all native and other job rows.

These are ROM file offsets; add 0x08000000 for runtime addresses. Check erased
bytes before allocation. No new persistent RAM reservation is implied. Extend
the owned state/copy/save machinery explicitly if needed and record the schema
and migration requirements for integration. Shared statuses and hook changes
must be named in the handoff. Do not silently steal unused bytes or IDs.

Agents own their entire job implementation in their worktree, including source,
native hooks, lesson descriptions, equipment/acquisition behavior and scripted
integration tests. Prefer job-named source files and `scripts/jobs/<job>/` for
builders, test plans and acceptance manifests. They may change shared engine
sources locally when required; list those changes for deliberate integration.
Read approved `notes/job-theme-audit.json`, `JOB-CLASS-SPECIFICATION.md`,
`WEAPON-ACQUISITION.md` and cross-class rules before implementing. Allocated
registry IDs, AP, growths, prerequisites, item ownership and acquisition gates
must be preserved and exercised through actual native consumers.

## Shared state changes

For a regression comparison, run the accepted build as a positive control and
assert the hash of the ROM actually loaded by the deepest fixture loader.
Changing an outer manifest variable is insufficient when scripts compose
nested source. Record every ablation's hash and changes; an analysis script
that successfully collects failures is not gameplay acceptance. Retain failed
inputs and observations without replacing fixed-input acceptance with longer
delays merely to obtain a pass.

Keep native forecast queries cheap. Shared damage helpers run repeatedly for
menus and AI, so reject irrelevant supports before looking up their owned
state, enchantments or reactions. A specialized query may skip irrelevant
providers only outside an action; during a live action it must return the same
frozen, exactly owned snapshot for originals and copies. Use localized native
forecast/arithmetic checks for numerical changes. Add the affected menu/AI
playback when transport, timing, stack lifetime or native control flow changes;
retain broader playback coverage for the major assembled gate.

Verify native status semantics with the actual setter and predicate before
using a bit in new effects. A familiar label in existing custom code is not
evidence. Include independent natural-flag, temporary-status and beneficial
lookalike controls on original and copied units. For consumable commitments,
resolve the exact selected target within its owner cohort and revalidate before
debiting inventory. A still-valid area recipient is distinct from an invalid
single-target action. Preserve that distinction in cost assertions.

For effects removed before damage, test the frozen snapshot as well as the
live status record. A successful removal must affect the current calculation
where specified without rewriting unrelated action-start benefits. Compare
actual casts with the effect absent, selected and retained. Keep any exception
bound to the exact synchronous actor/defender scope, and test retirement and
invalid ownership. The native ARM fixture helper writes only r0..r3: marshal
arguments5 and later explicitly at the declared stack pointer.

For position-sensitive player menus, account for ordinary Move updating the
live wrapper before execution synchronizes unit F6/F7. Resolve displayed
coordinates only with exact native ownership and selection-lifetime checks;
copied AI candidates retain their supplied coordinates. Never synchronize the
unit by writing during an AP/menu query. A deterministic playback should move
a real racial sprite across distinct affinity neighborhoods, select each
choice, and retain forecast/execution/rendering evidence. Declare any private
material changes as test inputs and keep their hash separate from the candidate.
Field-placement tests must include empty areas through actual player selection.
Directly executing an empty action object cannot prove the native menu accepts
it. Preserve zero recipient rows and use the native legal tile list; do not
manufacture a recipient to unlock confirmation. For a wrapped shared helper,
compare original action results, memory effects, RNG and both stack alignments.
When correcting only a test-loader failure, compare the run input manifests
and assembled ROM hashes. Reuse unaffected passed checks and rerun the failed
and skipped checks with their dependencies. Record both reports and the exact
input difference; do not relabel a failed combined report as a passing run.

When wrapping native applications, retain a direct route to the original
callback. Reading the relocated application table from inside an observer can
re-enter that same observer using the current custom descriptor. Exercise a
complete native cast to catch recursion. Treat native damage classification
and the expansion's sequencing category as separate contracts; test both,
including actual cross-job damage modifiers.

Terrain-affinity content must bind to verified native map IDs and coordinates.
Decode and render local ROM maps reproducibly into ignored build outputs;
commit only the source decoder and material annotations. Validate component
pointers and aliases against the clean ROM instead of trusting a third-party
map count. Check annotations against the rendered surface and native height
grid. Unknown cells stay neutral. Fixed material masks in mechanic tests prove
rule behavior, while the production catalog needs its own coverage checks.
Do not describe synthetic masks as accepted campaign terrain mappings.

When adding native status icons, update both the documented OBJ tile reservation
and the dynamic graphics allocator's start. Verify the encoded instruction can
represent the new boundary; a byte-sized doubled constant cannot encode every
tile index. Test adjacent video-memory guards and retain native rendered
regression. A caster status icon does not substitute for a placed field's map
presentation or prove that occupants can see its boundaries.

Native result fields may carry custom choices where the original renderer expects
item IDs. Trace both immediate and deferred presentation consumers. Resolve the
real weapon only at those reads; keep the action's original choice intact for
formulas and late Judge processing. Instruction-level comparison should verify
native arguments, preserved registers/stack and read-only result headers, while
fixed playback proves the actual animation returns. When adding Unicorn hooks
after executing a fixture, flush translated blocks so the new observers also
see previously compiled helpers. See `notes/mystic-knight-interface.md`.

Before expanding per-unit state, allocate the complete remaining domains in
`src/engine/job-state.h` and `notes/shared-job-allocations.json`. Preserve
existing effect offsets or provide explicit versioned migration. Verify native
flash bounds, every copy-container size and parent allocation; recompile all
consumers that allocate the changed container on their stack. Keep transient
action snapshots within their separately proven stack budget.

Test a shared ABI change as one coherent batch with the relevant declared
capacity, copy and persistence checks. A completed cross-cutting ABI migration
can justify a major integration gate; do not repeat `combined` for each local
fix within that migration. Include independent old-format inputs, corruption and
generation rejection, full-record copy/clear/roster assertions and cold native
save transport. Never carry a fixture from the old ABI into a new comparison
without explicit input migration; preserve full output comparisons. Record
current schema, actual acceptance and any correction in feature/checkpoint
documents, keeping this procedure independent of a particular record size.

Validate nested stack usage through actual queued battle playback as well as
native callback tests: an artificial test stack can conceal writes into IWRAM
rendering code. An external transient bank needs explicit heap exclusion,
exact live ownership, parent restoration and stale/copy rejection. Check every
native heap ceiling and retain full code and neighboring-memory guards.

## Deterministic testing

### Select tests by impact

Use either of these modes: implement a very substantial portion of a remaining
job/subsystem before its acceptance run, or use highly targeted tests while
developing that portion. Compilation/static checks can run during either mode.
Do not run a broad feature suite merely because its name matches the edit, and
do not follow every localized pass with `combined`.

Before each runtime run, record a short selection rationale in the working
checkpoint or progress note: changed behavior, affected consumers, exact test
IDs, required prerequisites, and any deferred milestone coverage. Use the plan's
dependency closure; prerequisites are not a reason to select unrelated tests.
Prefer `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only
<comma-separated-test-IDs>`. Inspect the selected dependencies before invoking
a long test. The examples below are starting points, not automatic bundles:

| Change | Initial localized checks | Expand only for relevant impact |
|---|---|---|
| Fight damage forecast | `test-mystic-knight-fight-preview` | Shared hand/effect helpers: `test-mystic-knight-fight`, `test-mystic-knight-fight-status`; installed hook/address changes: `test-integration-relocations` |
| Mystic formula or command effect | `test-mystic-knight-formulas` or `test-mystic-knight-commands` | The changed reaction, resource or cross-class consumer |
| Parry interception | `test-mystic-knight-parry` | Fight/status cases affected by ordering or consumption |
| Magic Shell | `test-mystic-knight-shell` | Shared success-hook Parry; outer Doublecast or rendered feedback when their lifetimes change |
| Doublecast continuation | `test-mystic-knight-doublecast` | Native hook edits: relocation checks; ownership/free changes: workspace checks; use the cached lifecycle section for test-only extensions |
| Doublecast Magic Shell forecast | `test-mystic-knight-doublecast-shell` | Single-action Shell when its shared forecast/storage changes; continuation when ownership changes; cached variant for test-only extensions |
| Shared Doublecast snapshots/reactions | `test-doublecast-reactions` | Queue entry changes: `test-integrated-queue`; Mystic continuation and pair-Shell are direct consumers; cached reaction variant for test-only extensions |
| Doublecast controller/render lifetime | `test-doublecast-playback` | Fixed Red Magic inputs, same/first-only recipients, Spellweave, queued recovery and natural caster KO; cached variant reuses verified build/captures; `test-doublecast-interruption-cached` selects only the interruption section |
| Mystic help/status UI | `test-mystic-knight-ui` | Native command playback when controls or graphics allocation change; preserve passed help checks when text/loader inputs are unchanged |
| Choice-bearing action rendering | `test-mystic-knight-visual`, affected player playback | Compare original native instruction behavior and caller stack alignments; `test-mystic-knight-remaining` selects only Osmose and Spellbreak corrections |
| Geomancer terrain annotations | `test-terrain-campaign` and its dependencies | Field rendering or AI only if its behavior changes |
| Choice transport | `test-dancer-choice` or `test-ai-choice`, as applicable | The affected native choice playback/AI path |
| Battle allocation/stack lifetime | `test-battle-workspace`, relevant native execution | `test-new-game-opening` if startup/heap capacity changes; the affected queued playback if native stack nesting changes |
| Persistent state/copy layout | The affected state, ownership and migration checks | Relevant cold-save lifetimes; major assembled acceptance after the complete migration |
| Documentation only | Review document consistency, links and diff; Git asset guard | No runtime suite |

If a needed scenario is buried in an expensive monolithic script, add a
deterministic case selector when needed, keeping its default full coverage.
Declare the selected scenario in the test plan/report. Avoid rerunning every
job's playback to check one path. Do not replace the common runner or create
one-off fixtures as a shortcut. Reuse hash-compatible fixtures/prerequisites;
if they are incompatible, regenerate only the affected dependency chain.

For test-only extensions on an unchanged integrated image, a declared step may
depend on `verify-integrated-prerequisites` instead of rerunning all builds and
captures. It requires every build/capture/native prerequisite to have passed
with unchanged inputs, even if a later consumer test failed. A failed consumer
does not invalidate successful immutable prerequisites. The verifier matches
every compact build-manifest field and native-test ROM hash,
verifies the actual image hash, native-source inventory and original build/
fixture inputs, then verifies executor input and capture hashes. Test source
and plan edits, documentation and the verifier itself are permitted; changed game/build inputs fail closed and require
the ordinary dependency chain. The report identifies the reused baseline.
Example: `test-mystic-knight-shell-lifecycle` runs only the declared lifetime
section; the main Shell test still defaults to all sections. Never represent
reused prerequisite evidence as a fresh full regression.

### Full integration gates

Run `combined` only after a very substantial completed milestone (for example,
finishing a job's remaining gameplay and player/AI integration, closing several
related backlog items, or completing a shared save-layout migration), on the
final assembled release candidate, or for a documented widespread regression
whose affected consumers cannot be reasonably bounded. A single helper edit,
new ROM hash, source commit, or passing localized run does not trigger it.
Explain the chosen gate in `IMPLEMENTATION-STATE.md` before running it.

Long playback, cold-save and campaign scenarios follow the same impact rule;
they are not mandatory companions to an arithmetic or forecast correction.
After failures, fix related findings as one batch and rerun affected checks.
Broaden only when failure evidence or newly changed shared behavior requires
it. A source commit may contain locally verified work with clearly recorded
deferred broad coverage; a commit is not release certification.

Retain the most recent full-suite baseline and every later targeted report.
Record which image each actually tested and why older evidence remains useful;
never present an old pass as a run on new bytes. The final release still needs
the full assembled suite and all open verification gates. This changes testing
cadence and selection, not the approved feature requirements or final standard.

Invoke `Test Expansion.ps1 -Plan scripts/jobs/<job>/test-plan.json -Suite <job>`.
Plans use the existing runner's dependency ordering, fixed inputs, complete logs,
hashes, timeouts, fail-fast behavior and JUnit reports. Initial plans contain
prerequisite checks only and say so; agents must add their job's real behavioral
tests. No testing agents, interactive play, vision-driven inputs or adaptive
agent test loops. Implementation agents can invoke scripts and repair code
against deterministic failures, as requested for independent integration.

Required acceptance includes native menu selection and descriptions, weapon
teaching/AP and racial transfer, acquisition gates, full battle execution with
fixed seeds, positive/negative/immune/KO cases, native AI/law behavior, relevant
cross-class combinations, exact costs and RNG behavior, copied/evaluated unit
lifetimes and native cold save/resume. Test formulas against independently
defined approved expectations and native controls; never inject expected
results during execution. Reuse unchanged evidence with explicit input hashes.
Support/reaction effects must work in other legal jobs, not only the new job.

When adding a field inside a shared state byte, document each owner's mask and
preserve neighboring fields in every lifecycle writer. Update differential
fixtures on both inputs to initialize the entire inactive domain; retain the
complete output comparison rather than masking away unexpected differences.
Compare captured movement allowances against the ordinary native Move getter
on a read-only clone, and test terrain cost independently of tile distance.
Controlled route-map tests establish reader/accounting behavior; real scripted
Move, undo and cold resume are separate required checks. Neither establishes
acceptance of a new movement ability's UI or post-reaction playback.

Playback fixtures must preserve a valid loaded racial sprite and supported
weapon pose. Reclassifying an already-loaded monster into a Human is suitable
for neither animation acceptance nor diagnosing a production pose failure.
Record controlled allegiance/stat inputs explicitly. Follow the native UI
transition after the selected commands (including facing confirmation), then
require return to a usable turn. Native result objects alone do not prove
rendering; retain rendered frames and test suspend/cold resume with the ordinary
uninstrumented candidate. Keep exact scenario coverage and limitations in the
feature's evidence note rather than presenting a narrow pass as full acceptance.

Budget nested native stack frames against loaded IWRAM code, not just the
32 KiB RAM boundary. Keep large optional locals in separate non-inlined helpers
so an unused branch does not reserve their stack space. Extend per-action data
through an explicitly reserved, heap-excluded temporary bank when needed;
bind it to exact scope ownership and retire it deterministically. Guard known
executable IWRAM and its fixed tables against their native ROM image during
playback. Establish boundaries from the source bytes; nearby mutable runtime
data is not a code-corruption oracle. A routine-level result pass alone cannot
detect later renderer failure from stack damage.

Before replacing a native instruction span, inspect branches entering the
middle of that span as well as its ordinary fallthrough. A hook's displaced
instructions can be a shared branch destination. Preserve that destination or
redirect every verified incoming edge; a literal pool must never occupy a live
entry. Keep original-byte assertions in the builder and run original-action
differentials with whole-state comparison. To isolate a concrete regression,
declare a deterministic diagnostic that restores candidate hook spans
individually and records the resulting differences; do not normalize away
changed native results.

Measure display labels with the native font consumer before relying on
character counts. Reaction previews have a fixed twelve-tile name area;
oversized text can corrupt the following heap header before any combat runs.
Keep a full approved title in design data and help when a compact game label
is needed. Exercise the actual preview, require its final confirmation mode,
and guard heap-adjacent memory. An unexpected extra prompt or failed allocation
can be a consequence of earlier text corruption; extra inputs or null-free
guards alone do not repair that cause.

For RNG comparisons, fix the seed at the native transaction entry and observe
at the matching return. A seed written while a menu is open is insufficient:
native input updating advances RNG, and different instruction timing can change
the number of advances before combat. Keep instrumentation in private test
ROMs, verify overwritten instructions and unused space, preserve registers,
stack and native combat RNG, and record both source and instrumented hashes.
Do not alter the playable ROM to make timing comparisons pass. Retained-fixture
rechecks must verify their fixture/candidate compatibility. Regenerate affected
fixtures when needed; complete UI execution remains required for UI acceptance,
with final fresh-fixture coverage at the assembled release gate.

For per-cast choices, retain the existing racial lesson/AP index across menu
options. Expand within the native 22-row command allocation and preserve learned,
equipment and MP flags; measure each option through the native font routine and
grow the command window descriptor. Compose existing job menu handlers instead
of replacing their stock checks or selection transport. Carry the choice through
the native extra halfword, not a persistent unit flag or mutable global. When
replacing a context's descriptor vector after construction, update its initial
selected-descriptor pointer too. Verify construction, every recipient's real
execution and original-job regressions. Menu/helper checks do not establish
rendered input transport, full AI option search or law behavior; record those
gates separately until exercised.

Trace the actual caller when a choice reaches the menu but disappears in
targeting or execution. Native target validation, player operand publication
and executor operand enumeration may each need an explicit handoff. Do not
enable item flags merely to transport a non-item choice. Derive the actor and
action registers from the caller's stores/consumers, and test the installed
adapter through its native continuation at both stack residues. A C helper test
does not catch loading the wrong saved register in an inline adapter.

For area abilities, verify the real selected center and native recipient list
after player input. Direct executor calls already supply a center and can mask
incorrect menu metadata. Native action byte8 selects the center (1 selected,
3 caster); byte9 selects the shape (5 cross). Check actual unit identity and
native eligibility when placing fixtures: the Judge is not an enemy recipient.
Decode result rows using the native0x2C stride and require an off-caster flank
target, so a self-centered cross cannot accidentally satisfy the test. Observe
live wrapper coordinates immediately after Move; saved unit coordinates may
be synchronized only when the action executes.

For actions that move after their attack, verify both the native animation
endpoint and the position retained across the next turn transition. The
earlier attack may already have committed a different tile. Keep any required
position commit after actual native movement, never during route preview.
Modal tests must cover declining the optional segment, rejecting an illegal
destination, and cancelling the underlying attack; a nonzero native dialog
result does not necessarily mean confirmation. Preserve the original target,
payment and command ownership across the modal handoff.

For turn-transition assertions, observe the live battle actor rather than
assuming the player-selection manager follows AI turns. Record the next
action counter as well: a later legal attack or knockback can change the
position being checked. Assert the completed action's result at its actual
handoff, then separately require a usable subsequent player menu. In a fixed
scenario matrix, retain each independent case's failure and continue the
remaining cases so related problems can be corrected together.

For AI acceptance, let the native selector choose commands and targets from
declared unit, equipment, mastery and formation inputs. Do not force a desired
command or replace the scoring function and call that an autonomous turn.
Capture preselection, actual payment, completion and turn handoff. Pair a
native scenario with focused callback tests when a specific boundary is not
chosen by the native AI. Keep the scopes distinct. Check already queued
commands when an effect consumes a later Move or Act opportunity.

Establish declared battle positions and status inputs at the tested turn's
input boundary. If setup advances through other turns, account for native enemy
actions before publishing the scenario; assert the intended destination is
unoccupied before movement inputs. For isolated AI comparisons, declare which
spectators can act so earlier AI turns cannot silently change target health or
position. Preserve a separate ordinary encounter smoke test. Do not repair a
failed action by altering its outcome or by changing fixture inputs mid-case.

For reaction interruption, equip the reaction through its native racial
ability record and observe the queued reactor/recipient and actual result.
Compare enabled/disabled cases and retain fixed hit/miss seeds. A status or KO
injected at confirmation is an invalidation boundary test, not evidence that
the original reaction delivered it. Render one frame after loading an emulator
state before requesting an image; restoring state alone creates no frame.

Check the recipient forecast separately from target eligibility and committed
execution. A selectable ability may execute correctly while its chance or
magnitude preview loses the per-cast operand. Trace both native constructors,
then test installed continuations, original-action operands and the full native
forecast function. Preserve rendered preview evidence and bound option labels
using the native font measurement so the menu's cost column stays readable.

## Merge and completion

For abilities with per-cast choices, trace available-action capacity, native
score records, movement search, publication and final execution separately.
Do not duplicate action IDs in a bounded native AI list to imitate player menu
rows. Use exact, synchronous forecast ownership when native callers omit the
option. Tests must include preexisting ailments/immunities, irrelevant weapon
operands, stale owner rejection and complete native AI turns without injected
choices or scores. Terrain-dependent options must use the evaluated movement
position. Record heuristic limits separately from correctness and avoid claiming
that an anchor-target choice is an exhaustive tactical optimization.

For campaign terrain authoring, use the deterministic `terrain` suite in
`scripts/integration-test-plan.json` and the decoder procedure in
`notes/terrain-decoder.md`. Compare decoded layout, height and clipping data
against the original native loaders before annotating materials. Preserve
component inheritance and animation offsets. A missing lower-layer tile may
be omitted only when its entire rectangle is proven hidden by opaque
foreground; visible unresolved graphics remain errors. Keep rendered maps,
extracted bytes and private probe ROMs ignored. Decoder acceptance does not
establish surface annotations or campaign gameplay acceptance.

Keep surface decisions as explicit sixteen-by-sixteen symbol rows in
`notes/terrain-materials.json`, bound to the reviewed clean-ROM component
hashes. Inspect coordinate-labelled surface crops with
`scripts/review-terrain-cells.py`; do not classify surfaces from palette color
alone or transfer a foreground object's material to a lower, occluded cell.
Combine material bits where the reviewed surface warrants it. Unresolved
cells stay neutral. The production builder requires all 162 native map records;
do not remove a reviewed map to bypass an authoring or decoding error.
Use `review-terrain-cells.py --materials <map IDs>` to label the authored
symbols on coordinate crops and full overlays before acceptance. Inspect both
palette variants before reusing rows. Shared geometry alone does not establish
the same material. Exposed wood, vegetation on stone and ice-covered vegetation
may combine existing bits; colored masonry, crystals and canvas must not gain
affinity from color alone. Unrendered centers/perimeters are candidates for
neutral treatment, not input to a color-based material classifier. Some scene
boundaries have ordinary flags, so flag8 alone does not identify all of them.
Keep independent reviewed surface anchors in the campaign test when adding a
new ambiguous material family, alongside native spell execution on real grids.
For outdoor maps, distinguish exposed bedrock from loose sand, and autumn
foliage from actual wood/heat. Inspect each palette variant. A transparent
center is a review prompt: a sloped dead-trunk cap may still establish the
cell's material, whereas an offstage boundary does not. Record that distinction
in the entry rationale and preserve independent positive and negative anchors.
Waterlogged reeds can combine existing water and vegetation bits (`M=6`).
Keep a fixed native cast on wetland with no native water flag nearby, comparing
against a private zero-material control; ordinary stream casts cannot prove
that annotated wetland alone supplies the water bonus. Keep ice-positive snow
cases separate from negative blue-mineral and fabric cases.
Run the consolidated `terrain-campaign` suite after an annotation batch. It
compares the shipping table with source rows, checks native coordinate
projection and neighborhood lookup, and exercises representative native casts
on captured campaign height grids. Review its material overlays before merge;
changed gameplay ROM bytes alone do not trigger combined regression. These checks do
not establish rendered player choice, AI, laws or a full campaign playthrough.

Each agent commits source only on its assigned branch, and reports commit ID,
candidate ROM hash, deterministic report paths, implemented lesson IDs, shared
hook/state changes and remaining gaps. Do not merge into main or modify sibling
worktrees. Root reviews the diffs and merges one branch at a time, resolves
shared hook dispatch and save-schema conflicts, rebuilds a combined ROM, then
selects affected tests and concrete cross-job interactions under the policy
above. Reserve full integration for the assembled milestone. Never combine
ROM patches with last-writer-wins behavior. The primary agent reviews the
assembled implementation after deterministic checks, fixes findings and retests.

The existing agents finish their assigned work and provide source-only
handoffs. No additional agents, job waves or councils are to be started without
a new explicit request. The primary agent handles all subsequent implementation,
integration, testing and final review, including Geomancer, Bard, Dancer and
Mystic Knight. Those jobs are not implemented merely by finishing infrastructure
or the current assignments.

For movement-dependent AI options, use an exact synchronous position scope;
never edit a live unit or wrapper to simulate movement. Keep the native search
node allocation and publication layout. A replacement coroutine must have a
bounded cursor, honor native movement/range/height providers, score every
recipient with the same choice, and retire its scope before every return.
Test both the native callback contract with fixed movement maps and complete
native AI turns. Synthetic search coverage cannot substitute for execution,
payment and turn handoff. When splitting a ROM code section, emit each section
separately, assert disjoint reservations and include all sections in relocation
scans; do not copy an address-spanning binary over intervening tables.

For compiled ARM modules, restrict table-pointer rewriting to ELF-classified
data: ARM `$d` mapping intervals and explicit OBJECT extents. Include
`--special-syms` when reading mappings with nm. An aligned word that numerically
falls inside a table can be two real Thumb instructions; alignment alone is
not evidence of a pointer. Record skipped collisions and verify linked code
bytes against the candidate after relocation.


When reducing a global RAM reservation, prove when each native owner is actually
constructed. A battle-named manager may also exist during opening dialogue.
Allocate large transient buffers at an explicit combat boundary, authenticate
both owner and native allocation, and keep getters free of allocation/repair.
Test exact manager free, containing-parent free, independent buffer free,
reallocation and whole-heap scene resets. After relocating banks, derive test
addresses from production accessors and move boundary guards only into dedicated
padding. Never retain hardcoded addresses inside the newly returned heap space.

Fresh-game tests must use an erased cartridge and bounded deterministic input
scripts. Observe actual scene readiness rather than pressing keys according to
old frame counts that can type into a delayed name keyboard. Compare rendered
controls and later scene anchors with the original game, verify real allocation
sizes/headroom and preserve the complete input trace. Reaching a blank panel or
preserving a canary does not establish successful startup.

Validate native allocation capacity before reading an appended owner header.
Account for the allocator's actual rounding and unsplittable remainder rules;
exercise those cases through real allocation, not only fabricated headers.
Retirement must cover owners that never created their optional buffer as well
as owners with live buffers. Keep ordinary null/invalid frame lookups cheap.

For animated graphics, a frame-boundary capture can fall between native upload
chunks. Validate static bytes and every animated chunk against native source
phases and their update order, then require distinct complete frames within a
fixed observation bound. Do not hardcode an animation phase based on an older
fixture's timing, or drop graphics comparisons to make a test pass. Bind raw
observations and reports to the exact candidate hash.


Native Fight may bypass ordinary effect-descriptor loops. When adding a status
rider, authenticate the exact hand/component and actual HP loss, then preserve
native damage-sensitive cleanup order, prevention, timers and effect-context
restoration. Distinguish ordinary accuracy adjustments from guaranteed native
interception admission (such as Astra); halving that admission can incorrectly
retain a protection charge. Validate fixtures through actual item fields and
native getters/results, not item names or an assumption that low attack is zero.

Test recorders must publish count/readiness only after the entire payload is
complete, and consumers must wait for readiness. An emulator video frame may
end inside the recorder. Preserve failing evidence and compare the finished
native result before diagnosing a partial capture as a gameplay failure. For
a test-only recorder fix with unchanged game bytes, rerun all affected consumers
and retain applicable passing coverage from the full run; label this explicitly
as full-suite plus affected-rerun evidence, not one completely passing full run.


Authenticate standalone damage forecasts at their real native callers. Preserve
callee-saved loop indices and original stack arguments before a shared wrapper
opens a query snapshot; do not confuse a reaction discriminator with a weapon
index. Trace item transport through constructor/search callers, especially when
native code sorts equipment by power. Use independent item/defense controls at
actual UI/AI entry points, including identical/reversed pairs and both stack
alignments. Require unchanged live units, owned state, RNG and retired scopes.
A correct damage query does not prove status/resource simulation or late Judge
reporting; keep those consumers as explicit remaining acceptance obligations.

For native AI audits, separate learned discovery, probabilistic consideration,
recipient rows, later application filtering, placement and actual execution.
Construct placement nodes with the real native constructor and use its returned
callback; manually filling a subset of fields can bypass or invent behavior.
An application category in an AI row is not an executed effect. When a custom
benefit uses a native category, audit that category's existing-status predicates
and extra heuristics against the custom effect's own state. Preserve common
restrictions and explicitly test the original fallback for unrelated actions.

Inline-hook tests must capture registers before state-reading helpers that can
invoke native calls. Compare real continuations, both stack alignments and live
registers. An artificial test stack must not overlap a purported code guard;
verify actual renderer preservation separately during emulator playback.
When normal AI randomness prevents a positive case, first inspect the saved
decision. A declared bounded seed sweep may preserve negative cases and stop
at the first real cast. Pin that exact input for future regression instead of
repeating discovery or changing production probabilities to obtain a test pass.

### Stack diagnostics and reuse of playback evidence

Inspect generated code when a large local array has an early fallback: the
compiler may reserve that frame before the branch. Dispatch unrelated commands
before entering the large-frame function. Runtime stack headroom must include
native interrupts, not only the deepest sampled main-thread stack pointer.
When comparing instrumentation with native execution, keep saved inputs, every
button frame and execution RNG identical; a minimal seed-only entry can isolate
the recorder's stack overhead. Preserve inconclusive controls separately.

To avoid replaying passed cases after a seed sweep, an evidence-aggregation
script may verify saved positive cases for the exact current ROM. Check permitted
instrumentation changes, hash the source artifacts, and independently validate
raw before/result/handoff data against the expected effects and costs. Do not
accept a positive result merely because a JSON flag says it passed, change a
failed whole report to passing, or reuse old-ROM captures across code changes.
Keep partial native checks and campaign/final acceptance distinct.

For an initial changed-image run, select ordinary dependency-chain test IDs.
Cached verifiers require a completed immutable preparation report; do not
schedule them alongside the fresh build they would need to authenticate.
After that preparation completes, use cached IDs for the affected follow-ups,
including when a consumer failed. Retain successful sibling checks.

When an ARM emulator control rewrites an inline hook inside a translated basic
block, explicitly invalidate the affected translation-cache range before
execution. Otherwise cached instructions can read newly restored literal bytes
and create an instrumentation-only invalid branch. Keep the original failed
control, exact address and correction in the diagnostic evidence. Do not alter
shipping code to accommodate an emulator cache artifact.


### Terrain presentation review without repeated gameplay fixtures

For compositor-only changes, group stroke, clipping and independent pixel/capacity
oracle changes before running `test-geomancer-compositor` and
`test-geomancer-animation-capacity`. Keep the reserved capacity fixed unless a
separate ownership change is justified. A failed bound rejects a proposed stroke.
Use `test-geomancer-readability` for an authenticated retained battle comparison.
After installed timing checks, `test-geomancer-readability-terrain` reuses their
hashed native-derived RAM outputs. Center detached review views on the existing
field cells and require positive visible differences; an offscreen field cannot
establish readability. Declare detached camera/kind changes in reports. These
artifacts do not establish player placement, sprite visibility or campaign access.
Keep native publication, actual UI timing and final cold/mixed-job lifetimes as
separate evidence; avoid recreating already passed gameplay fixtures for artwork
review. Historical display-capacity experiments are not the production bound.


### Mixed-action display tests and reliable prepared-state reuse

Reuse accepted field-cast states to test a different action family. Reset the
complete declared formation, including retained enemies, and assert unique
occupied tiles both before saving and after loading the prepared state. A
correct cursor can otherwise target an older occupant rather than the intended
recipient. Wait for the observed native menu after Move before submitting Act;
a fixed release delay alone does not prove movement completion.

Bind resumed case results to the exact prepared-state hash as well as source
state, ROM, control image and scenario. Fingerprint complete setup functions
with AST source spans; string delimiters may also occur inside literals and
silently omit later code. Keep tested script snapshots and dated reports.
Treat unexpected zero damage as a diagnostic, not permission to assume a miss
or loosen a positive-control requirement. Inspect recorded native recipients.

For optional graphics under pressure, compare actual queued actions with a
mechanics-preserving display control. Record memory ownership and input-to-
completion frames; correctness alone can hide repeated failed allocation work.
Use native allocation observers to prove bounded deferral/no retry churn, then
actual playback to establish restoration before the next interactive decision.
Rerun only affected failed cases with valid inputs; invalidate prior results
when a discovered setup flaw changes the scenario itself.

### Connected ending-scene verification

For scene suffix coverage, authenticate the original script banks, descriptors,
opcode table and handlers against the clean ROM. Declare initial scene selection
separately from natural campaign entry. A one-time argument substitution at the
native queue call preserves the scheduler; queueing from an arbitrary flag read
can be overwritten by the normal event selection later in that frame. Copy only
PC-independent displaced instructions into a trampoline and preserve registers.

Observe original scene callbacks, credit instructions and the real save opcode
without changing their return values. Bound both initial entry and the complete
sequence, retain every fixed input and hash captures. Verify native title/Continue
and unmodified cold loading when the tested scene owns the ending save. Reuse
the accepted suffix when testing a missing incoming path; do not repeat credits
just because another campaign milestone changed. See
`notes/campaign-ending-scenes.md` for the current proof and remaining limits.

When verifying battle-exit scene connections, classify native actors by
allegiance, not by whether their record lives outside the party bank. That bank
also holds judges, guests and story actors. Assert non-hostile records remain
unchanged by controlled defeat inputs. An automated pass with an invalid setup
must be recorded as superseded/excluded, then rerun only its affected path.
Retain authenticated deployment entry checkpoints to avoid replaying accepted
scene prefixes while correcting battle preconditions.

For town-conditioned recruitment, the native condition interpreter can queue
a scene directly rather than through09AFC. Observe the actual script identity
and recruit opcode; do not require an unrelated queue observer to fire. Separate
world-to-offer native mutations from cancellation/acceptance ownership checks.
Compare cancellation against the actual generated offer, recording earlier
inventory or scene-field changes rather than hiding them in broad exclusions.
After acceptance, observe the world screen and responding cursor before saving;
extra fixed A inputs can re-enter the pub after the scene has already ended.
Authenticate and resume the accepted endpoint when only this suffix is missing.

### Territory and final-arrival milestone verification

Declare map ownership separately from placement coordinates. The native region
record's ownership byte and reserved fixed positions matter to real rendering
and travel; setting only the position getter's byte is an incomplete fixture.
Distinguish manually placed awards from original fixed-location creation.
Carry all changed native mission-service bytes forward, recording the delta;
selectively copying flags/queues can omit original bookkeeping.

For final entry, `D17C4` is a menu selector; `D1A18` is the original post-save
selection called before departure. After the real Ambervale save, close the
slot picker and select a different destination. The native controller then
chooses Royal Valley/scene93 before travel. Use the actual controller and scene
observer, not an injected event. Reuse the accepted final-battle/credits suffix
when only its incoming path is missing. See `notes/campaign-territory-scenes.md`.

Normalize CRLF before extracting an authenticated helper prefix and assert that
the intended boundary was found. Prefer AST extraction for independent helpers.
A failed split must never execute the producer's complete runtime. Preserve
failed diagnostics, but exclude invalid setup/oracle runs from acceptance and
remove obsolete diagnostic modes from the normal declared test plan.

### Resource-tooling acceptance

Use `test-resource-tooling` through the integration plan after changing process
containment or pruning boundaries. It uses small private fixtures, real bounded
child processes and no emulator/player saves. Normal inherited workspace ACLs
are needed for sandboxed descendants; Python private-temp ACLs may deny them.
Keep errors/logs instead of broadening permissions. Cleanup must resolve and
check the destination inside private build roots and reject junctions/symlinks.
`Build Expansion.ps1 -KeepWorkspace` retains copied build workspaces when needed;
the default preserves reports/logs and removes the large regenerable copy.

### Release evidence and private delivery

Reconcile closed checklist requirements against later source changes before
reusing old reports. Keep their original candidate identity and scope. Use
`audit-release-evidence` to authenticate the retained clean-build source inventory,
the changed-path report hashes and supporting notes; this is a read-only audit,
not a new gameplay run. It requires the retained local evidence workspace.

Use declared `package-expansion` for deterministic BPS generation, wrong-base
rejection and byte-for-byte roundtrip. It creates an immutable private expansion
ROM and patch, guide/reference copies and a manifest. It never migrates saves.
`test-expansion-launcher` can then authenticate that package and invoke the actual
PowerShell launcher's validation-only branch, including a wrong-ROM negative.
Select it alone for a failed launcher continuation when packaging is unchanged.
The common runner records exact selected IDs, logs and resource results.

Record the shipping-source checkpoint and packaging source hashes separately
from gameplay acceptance. Node subprocess spawning may be restricted; use the
already authenticated source checkpoint rather than requiring a Git subprocess
inside the packager. Windows PowerShell may inherit a different module path;
the launcher uses .NET hashing and does not depend on Get-FileHash discovery.
Local manifest refresh does not authorize a game launch or remote publication.

### User-requested showcase saves

For an all-content sandbox, use the separate `scripts/showcase-test-plan.json`
and exact step `prepare-expansion-showcase` through the normal runner. It starts
from the read-only early-town seed, declares mastery/stock/resources, performs
native job changes and save writing, then verifies a fresh cold load. Keep these
declared inputs distinct from campaign earning and release acceptance.

`scripts/install-expansion-showcase.py` authenticates the passing output and
installs to dedicated showcase ROM/save paths. It refuses every existing save,
including an identical seed, because that path belongs to the player after
installation. Launch subsequently with `Play Expansion Showcase.cmd`, never
regenerate/reinstall as part of ordinary play. Use the verified visible desktop
launch procedure only when requested. See `EXPANSION-SHOWCASE.md` for contents.

### Native references and original pixel artwork

Read `notes/native-art-integration.md` before artwork work. Extract original
references only from the authenticated clean ROM into ignored `build/art/`.
`scripts/native_art.py` preserves tile atlases, raw palette/OAM/sequence records
and original-byte roundtrip evidence. `--rebuild-previews` recomposes existing
authenticated exports without repeating native decode tests. A single reference
palette does not establish correct per-character colors. Distinguish indexed
tile atlases (lossless) from flattened OAM previews (overlap hides pixels).

Test transparency against palette index zero, never RGB luminance. Use declared
`test-native-art-format` for compositor/flip/overlap/packing changes. Original
job-label icons are32x16 assets. Roster/wheel miniatures are a separate
compressed640-byte image pipeline, indexed through0x393f0c by land resource ID;
they do not consume the battle actor sequence/OAM tables.
Use `export-native-ui-reference` and `test-native-art-poc` only for their actual
consumers. Invoke exact IDs via `Test Expansion.ps1 -Plan
scripts/native-art-test-plan.json -Only <ID>` after announcing runtime purpose.
Keep the script's authenticated ROM hash alongside the runner report: the
outer runner may still label its unrelated default combat-manifest ROM.

Use built-in imagegen for new class artwork and visual revisions. The user's
latest instruction supersedes manual pixel-editor and coded-pixel drawing.
Do not repaint donor characters; use them only for proportions, light direction, native
pixel density, anatomy and animation cadence. Preserve species-specific anatomy
and distinct costume silhouettes. Original engine timing/layout metadata may
guide import compatibility but does not supply accepted new character artwork.

Save generated artwork privately under `build/art/imagegen/`, preserving alpha
and the original generated output. Store generation/edit prompts and truthful
draft/import status in source documentation. Inspect directions, hand/weapon
contact, native pixel density and palette constraints before bulk animation work.
Use imagegen for visual corrections; code may perform technical format conversion
and native import checks without inventing replacement artwork.

The earlier manual-draft archival workflow is retained for existing artifacts
only. Save editor/PNG assets privately under `build/art/authored/`. For reproducible
source pixels, `scripts/authored_art.py record <PNG> <JSON> --authorship <text>`
records the actual manual drawing with an exact RGBA roundtrip and at most15
visible colors. `render <JSON> <PNG>` reconstructs it. This format is a draft,
not an animation importer or an aesthetic acceptance test. Keep status and
provenance explicit; construction drafts must not enter player builds.

Private POCs must authenticate their source ROM, allocate only verified free
space, dispatch changes only to the selected new job, and preserve other native
consumers. Each runtime attempt needs a unique output directory, fixed inputs,
full logs and failure records. Never patch installed player ROMs or reuse their
live saves for artwork experiments. Reuse applicable passing decode evidence.

### Equipment preview and native menu portraits

`scripts/equipment_preview.py` builds a private overlay from the authenticated
integrated manifest and writes its own `build/art/equipment-preview/current.json`.
It does not update the installed/player ROM or the integrated current pointer.
The integrated source builder invokes the same `apply` function for eventual
assembled delivery. Reserve ROM0x1d00000..0x1d04000 for this module; do not reuse
that region for actor animation tables or graphics. Compiler/linker checks reject
reservation overflow and persistent writable sections.

The earlier manual portrait source is `src/art/job-portraits.json`; it is now
superseded by the imagegen requirement, not production artwork. The compiler
packs only these pixels plus an explicitly drawn generic frame; no donor heads
are bases. Original palettes may be references, but their source indices and
VRAM destination banks are different quantities. Verify native palette routing
before treating exported colors as authoritative. A draft remains a draft even
when exact pixel transport passes.

Use the declared native-art plan and targeted IDs:
`test-original-portrait-consumers` checks all-job dispatch/canaries and the actual
Samurai R teaching panel; `test-equipment-preview-native` checks52 jobs/11 items,
both map layouts and write bounds. `test-equipment-preview-ui`,
`test-equipment-preview-shop`, and `test-equipment-preview-sell` cover distinct
native modal entry points. Announce the selected IDs and affected behavior first.
Use unchanged passing evidence for consumers whose implementation is unchanged.

Correct routes: world Start→Party A→roster Start→Item List A. Shop Buy/Sell:
Select→A→A→Select through the help/category prompt. R on a shop list instead
opens the teaching panel. Do not mistake a full inventory purchase rejection or
that teaching panel for a broken eligibility hook. Each test starts from a private
authenticated seed; do not drive the user's game or modify a player save.
Compare shop ownership changes to the same shipping-ROM route because native
shop entry can reconcile unit fields. Retain both deltas and reject any added
changes. Keep failed route attempts and visual rejections in the checkpoint.

### Separate actor import proof

`scripts/native_actor_import.py` authenticates the current integrated ROM and
the private native reference exports, then clones Samurai land4/water192 into
resource256/257. Reserve ROM0x1d10000..0x1d80000 separately from the UI module.
The bounded arena rejects occupied space/overflow. Preserve original248 actor
table entries/sizes, duration/command/unknown frame metadata, OAM and hidden
tile bytes. Patch only checked table literals and Samurai's two resource IDs.
The separate miniature mapping needs extension too: literals0x87bd4/0x87c54/
0x87d8c reference0x393f0c. Changing actor IDs without extending this mapping
reads beyond the intended miniature table; this is not evidence of ID truncation.

Use declared `test-native-actor-import` for all-job native getter comparisons,
wide IDs and exact relocation; aliases must use a concrete fallback job2, not
themselves. `test-native-actor-ui` compares unchanged roster/wheel output only.
`test-native-actor-battle` reuses the authenticated shipping accepted-world
checkpoint and saved Giza route. Set generic Human slot2 to Samurai before
native deployment, then compare deployment/idle rendering, owned state and
renderer guards, and require private resource pointers in actual battle actors.
No new fixture generation or player save is needed for this bounded proof.

`scripts/convert-generated-sprites.py` performs only alpha/cell extraction,
common native scaling, shared15-color quantization and tile packing. It rejects
figures touching cell borders. Maximum-coverage quantization preserves rare
facial highlights better than the first median-cut conversion; record source
hash, crop, scale and palette. Visual revisions still go through imagegen.

`scripts/build-generated-actor-poc.py` is explicitly an incomplete idle proof:
generated frames replace only land slots0/1, using one32x32 OAM object and an
existing native palette. It does not change global palette bytes, other jobs,
actions, water or miniatures. `test-generated-actor-battle` reuses passing
unchanged baseline captures and checks full frame transport and ownership.
Its initial fixed-VRAM-block assertion failed and is retained as failed evidence.
Native actor upload timing can differ from the baseline by a video callback.
Use `actor_render_evidence.py` to authenticate all12 actor records against their
ROM descriptors, unchanged native allocation ranges and displayed tile data.
Allow only the preceding sequence frame when native queued/deferred flags
0x120000 permit it; never arbitrary frame matches or unexplained diff masks.
Require exact OBJ bytes outside original actor allocations and an exact whole
BG match to authenticated original phases of the same scene. The declared
`test-render-isolation-oracle` exercises retained captures and corrupts neighbor
tiles, unowned tiles, BG tiles and allocation size to require rejection. Bind
that regression to immutable manifests, not a changing current candidate.

For color conversion, distinguish source palette indices from destination OBJ
banks. UI icon banks13..15 map to source indices0..2 for native0x080cba3c.
Normal palette base is0x419d60; mode1 uses0x41b340 and mode2 uses0x41a860.
Samurai's actual battle OAM bank1 matches normal source0x419d80. Capture actual
OAM/palette memory and assert that displayed opaque colors match the importer
reference. Pixel transport alone cannot detect using a dim palette as input.
The converter supports explicit --columns/--rows for2x2 canonical-facing
sheets; opposite native mirroring remains a separate consumer verification.
For uneven generated row spacing, --row-cuts specifies original-image Y
separators. It requires a completely transparent two-pixel band at each cut
and still rejects cells whose opaque bounds touch an edge. This only extracts
existing figures; never repair missing anatomy or draw pixels in conversion.
Record the exact crop in the conversion manifest and retain failed equal-cell
attempts. Track design hashes and each consumer independently in
src/art/imagegen/catalog.json; a source or converted sheet is not acceptance.

`scripts/build-art-gallery.py` authenticates catalog source hashes and embeds
existing PNGs unchanged in private build/art/gallery/index.html. Serve only
that directory on loopback for review, never the repository root. The gallery
distinguishes generated design sheets from unfinished native conversions and
provides stable row/column labels, enlargement and optional pixel comparisons.

Conversion experiments use --quantizer coverage|median and --resampling
nearest|box|lanczos, with old coverage/nearest defaults unchanged. Write each
variant into its own folder; compare indexed tile/palette hashes to preserve
old evidence. Quantization MSE only measures color reduction after resampling,
not total detail retention. A lower value cannot accept blurred eyes, dropped
bottle colors or loss of native outlines. Visual revisions still use imagegen.

Align imported actor art against the native opaque baseline, not the bottom of
its allocated OAM rectangle. Compose the original frame's authenticated OAM and
tiles, find nonzero palette-index bounds, subtract preview world anchor(48,64),
then offset the new canvas's opaque baseline to match. Palette zero alone is
transparent; RGB luminance is not a valid occupancy test. Preserve the computed
alignment in the import manifest. An unchanged-tile coordinate correction can
reuse old captured hardware: require only intended OAM coordinates to differ,
with every other OAM field and VRAM identical at matched deterministic snapshots.


### Wide menu resource IDs: reproduction and evidence reuse

Build the isolated all-class transport with scripts/native_class_resources.py.
The result resolves through build/art/class-resources/current.json; it does not
replace the packaged player build. Announce and run the declared
Test Expansion.ps1 -Plan scripts/native-art-test-plan.json -Only
 test-native-class-menus,test-native-menu-width checks. The latter discovers
the latest successful racial-menu capture for exactly the candidate hash and
records full RAM/IWRAM source hashes. Preserve those ignored captures with the
report; a missing applicable capture requires the menu test first, not a new
one-off seed. Both tests reuse the existing authenticated showcase save.

Keep the racial header and generic widget separate. Header fields434/435 share
adjacent byte storage; its full ID belongs in the explicitly extended manager.
The common widget's ID belongs outside its native allocator extent, in owned
buffer tail space. Check actual actor IDs, creation and recreation, neighboring
fields and allocator boundaries. A static wheel miniature is a third consumer.
Helper-level isolated buffers do not establish real menu placement, UI timing,
VRAM display or teardown; report these limitations explicitly. Exact resource
payload equality permits reuse of previous descriptor/tile/OAM preservation
evidence while changed consumers receive targeted checks. Never use an old
fixed-character menu proof to claim generic-character acceptance.


### All-class generated transport and retained display verification

Build scripts/native_class_resources.py, then scripts/generated_class_transport.py.
The latter authenticates catalog images/conversions, writes a separate generated-
classes/current.json and preserves the earlier playable preview. Run declared
 test-generated-classes-native for native decoding/metadata and exact rebuild;
 test-generated-classes-ui for the actual ten-class generic presentation cohort.
Use Test Expansion.ps1 with scripts/native-art-test-plan.json and explicit -Only.
Do not infer full animations or final artwork from these idle/miniature proofs.

For changed sprite allocations, derive ownership from actual native actor
records at every capture, including menu cancellation: a closed wheel can leave
its header actor alive. generated_class_ui_evidence.py authenticates retained
captures and permits exact miniature replacements plus the original actor's
bounded range. Its corrected comparator can verify a complete failed-run capture
without replay when only the oracle was wrong. Keep the failed report, source
capture hashes, fixed inputs and corrective result separate. The fixed historical
 test-generated-classes-retained is for595782ba's preserved capture; fresh runs
use the corrected comparator already included in test-generated-classes-ui.

The real dispatch widget also calls08029cd8 to replace only its animation mode.
Include that path when testing resource-ID storage, alongside creation and full
update. Native helper checks alone did not reveal its legacy byte read. Reuse
racial-header evidence across this fix only with an exact ROM-difference proof
restricted to the mode-reader instruction and its field literal.


### Large8bpp portraits: independent append-only import

Export scripts/native_portraits.py against the authenticated clean ROM. It
writes private103-record pixel/OAM and495-palette references. Prove unchanged
native decode/re-encode with declared test-native-portraits. Build
scripts/generated_portrait_transport.py only after generated_class_transport.py;
its independent current pointer is build/art/generated-portraits/current.json.
The new1d80000..1e80000 reservation must be blank FF; preserve original records
and append new IDs, guarding all native pointer literals and job-field writes.

Use test-generated-portraits-native for current native lookup, preservation and
exact rebuild; test-generated-portraits-ui for actual all-class menu upload,
OAM, hardware palette, coexistence, cancel/reopen and named-character control.
Invoke through Test Expansion.ps1 with native-art-test-plan.json and exact -Only.
A portrait uses8bpp tiles,32-byte OAM tile units and48-color palette uploads;
do not substitute the4bpp actor or miniature oracle. Authenticate actual named
identity flags/IDs (e.g. Marche2/80, Montblanc8/82), not arbitrary generic job IDs.
Temporary custom palette alternatives can match, but record that color-mode
art tuning remains deferred. These proofs do not accept the image crops as art.


### All-sequence temporary actor transport

Build generated_action_transport.py after generated_portrait_transport.py.
It appends to1e80000..1f80000 and changes only owned animation-table entries.
Preserve null descriptors, already-proved idle descriptors, all frame commands,
durations and metadata. Distinguish repeated idle-pose/water-crop transport
from an authored animation set. Align each imported opaque baseline against
its original pose, and guard the unchanged native tile allocation.

Declared test-generated-actions-native checks all20 resources, every supported
mode/facing creation and exact rebuild. test-generated-actions-battle performs
a separate paired actual deployment/Move/Fight/return check. Its first baseline
can fail: do not attribute such failure to the new stage or count the unexecuted
candidate as tested. Keep selection-step screenshots and final failure state,
RAM/IWRAM alongside hashes/inputs. Diagnose the earliest changed stage with
bounded entry checks before replaying long completion waits or broad suites.


### Combat graphics fixture identity and actual frame verification

For the Giza Move/Fight route, use native_battle_wrappers.fixed_giza_formation
before movement inputs and assert actual wrapper positions. Unit cached F6/F7
coordinates can disagree with RNG-dependent live encounter placement. Preserve
Marche/Montblanc's named identities before story encounter construction; making
them generic creates replacement guests and changes deployment slots. Use
recruited same-race units for generic-body proofs. Record every setup input.

The old world seed predates transient action roots3ff44/3ff48. Clear those eight
owned bytes as existing integrated fixtures do, guard3ff4c onward and separately
verify root retirement after execution. Command-manager5/result1 is not a
universal stall signal: require the actual mode11 confirmation and completed
attack/turn return. Distinguish an empty target from an animation stall.

Use native enumerated wrappers' current44 pointers to identify unit-body actor
records. Auxiliary resource128/effect objects have a different contract; retain
them separately. Across a mode change, a native pending/deferred transfer can
leave the preceding frame visible: permit only one sampled hold of the complete
previous verified allocation with unchanged ownership and exact bytes. Record
such cases. Collect graphics mismatches and their full captures through the
complete paired scenario, then fail, so oracle corrections can reuse evidence
instead of repeatedly stopping at the first frame. No broad any-pose tolerance.

### Controlled native water transitions and retained frame acceptance

Use declared test-generated-actions-water for the paired Viking scenario. Only
tile4,14's water flag is changed before Move; leave native height/resource
selection to the engine. Native B uses input mask1. Assert submerged destination,
actual wrapper/body resources, pixels and return to land. Label a water-flag
fixture honestly: unchanged Giza background is not a natural water-map test.

native_body_display.retained permits one exact prior directly proved allocation
when a pending native transfer crosses a mode or an explicit owned land/water
pair. It also handles a single same-sequence zero-timer/index rewind when source
upload and full previous allocation remain exact. Never chain retained holds,
accept arbitrary frame candidates or treat auxiliary effects as body records.

For a completed scenario whose only failure is this bounded oracle, preserve
the failed run and verify authenticated retained captures. The declared
test-generated-water-retained demonstrates ROM/report/capture authentication,
independent actor parsing, subsequent direct display and corruption rejection.
Reuse successful gameplay evidence; don't replay it only to change a report.

### Status/equipment pixels and clean-source collision safeguards

Use generated_status_transport.py for the owned128-byte two-glyph payload.
Keep selectors, timing, shape, palette and other symbols exact; verify actual
status cycling/coexistence/removal separately from grant/expiry gameplay.
generated_equipment_transport.py reserves1f80000..1f84000 and wraps CB980's
existing caller-aware ABI. New equipment IDs overlap quest icon IDs; preserve
the caller and shop-mode gate and delegate other IDs/contexts to the prior C
helper. Held weapon art and actual thrown playback require separate proofs.

Actual screenshot checks must match the retained libretro format: RGB565
green comes from GBA5-bit green shifted left once, then scaled by255/63.
Red/blue scale by255/31. Verify format and all opaque native-resolution pixels;
VRAM presence alone is insufficient. Buy's weapons tab takes two Rights from
the initial category; Sell's takes one. Reuse completed paired scenarios from
authenticated failed artifacts when only a later setup/oracle failed.

Always distinguish clean-ROM references from expansion-inherited originals.
An invalid expansion archive record does not establish invalid original data.
Compare authenticated clean bytes before weakening coverage or labeling a gap.
Export all522 equipment/quest references with export-native-equipment-reference;
their mode0 palette selector is3c7fe4+4+2*index, bank nibble mapped to419d60.

Native table relocation uses native_table_literals.py's explicit reviewed load/
literal pairs authenticated against the supported clean ROM. Compiled modules
retain ELF mapping/object classification. Never scan arbitrary ROM words as
pointers, use a guessed native-code cutoff, or treat a coincidental LDR pattern
as provenance. Unknown changed sites fail closed for review. Keep manifest
records for both applied relocations and preserved data/instruction collisions.

Historical repair-native-table-collisions.py authenticates the frozen shipping
manifest and each preimage, restores only recorded false relocations in a new
private child, and never overwrites release files. test-native-table-collisions
replays the actual builder loop, checks known references, corruptions/unknown
references, whole-ROM isolation and native affected consumers. A repaired hash
alone is not full acceptance. Inspect downstream copies too: decoded palettes
may retain corruption even after their source archive is restored. The separate
native_repair_copies.py/test-native-repair-copies stage demonstrates that audit.
Retain old failures and correct mistaken interpretations in source documentation.

Use rebuild-native-literal-policy for fresh isolated eight-stage source assembly;
retain its workspace when a subsequent stage must inspect/reuse its result.
Do not compare a deliberate repair directly with the known-corrupt old hash.
test-native-repaired-data authenticates build logs and reconciles every byte
against the explicit repair plus already-declared independent modules. Its map
audit uses exact compressed component extents; packed components' broad upper
bounds cannot establish ownership. Label decoded clipping/arrangement equality
as static data proof, separate from actual native movement and scene playback.

For clean art composition, pass explicit parent manifests into each transport
builder and use publish_current=False to preserve historical component pointers.
An already-installed owned preview requires full module/hash, tail, hook and
preimage validation before any removal. Reject conflicts before mutation;
never clear an occupied reservation merely to make assembly succeed. The
build-clean-art-chain procedure authenticates the fresh base/rebuild report,
checks negative controls and confines later equipment changes to their module.

Held weapons have a distinct contract: inspect all three descriptor words,
including the live primary and secondary sequences. Preserve command-only
tileFFFF/OAMFFFFFFFF frames verbatim. New resources need both animation and
allocation table extension plus the native item selector9 assignment; changing
an inventory icon does not change a held weapon. Enumerate the actual item
category across the whole table, not only the last contiguous range of IDs.
Preserve category, statistics, palette selector and all other native getters.

For actual held display, follow the unit's native wrapper attachments at4c/50;
do not mistake body/status/effect actors for its weapon. Check each descriptor
channel, uploaded tiles, allocation bounds and actual visible hardware OAM.
Primary colors come from the item's palette, while native98976 selects bank6
for the secondary trail. Compare that trail to the paired original capture.
An original motion path with repeated generated pixels/transparent auxiliary
tiles is a transport proof only. Keep production motion acceptance separate.

Completed baseline captures may be reused only with exact report/ROM identity,
completed outcome checks and retained state authentication. Carry over only
the completed baseline's inputs/checks, never failed candidate observations.
Record provenance in the new report. If the parent changes, use a justified
fresh pair or explicitly prove the affected consumer inputs unchanged.

For thrown equipment, follow the separate D5FD8/D65D4 icon-upload path. Native
FE070 assigns palette8; require exact uploaded pixels plus visible moving OAM
in that bank to avoid accepting an identically drawn held blade (banks0/6).
Native command manager+20 is the selected global action; +16 is a choice.
Keep failed menu-field assumptions and captured selections when correcting tests.

For the characterized Throw primary impact, native_effect_art.py authenticates
the2bpp/LZ source, expands it to4bpp, exports three24x24 OAM frames/seven palettes
and re-encodes a4bpp LZ container. Actual D758C/D7674 loader tests must distinguish
emulated BIOS decompression from executed native unpack logic. The original
2bpp unpacker writes one terminal zero into staging slack; measure that byte
and guard beyond it. A captured VRAM atlas proves upload, not visible impact.
Require live palette6 OAM at the atlas's tile range and all declared poses.

Preserve original shared effects: scope a generated resource list to its new
action context, authenticate stolen instructions, and test original-action
delegation, continuation, live registers and stack stores. A native confirmation
from the exact parent can be reused before effect allocation if the new hook/
reservation cannot invalidate any already-live object; preserve source report,
seed and RAM identity. This avoids replaying passed travel/deployment.


### Expanded art delivery and evidence reuse

Use build-assembled-art.py through declared test-assembled-art-rebuild to rebuild
all eight art stages from the authenticated corrected gameplay base. It preserves
historical component pointers through the six-stage clean builder; owned weapon
and impact stages then reconstruct the existing target exactly. Generation is
not deterministic: source image/conversion hashes are pinned private inputs.

Keep fixtureSource separate from a clean rebuilt comparison source; authenticate
the fixture report and frozen ROM before using retained IWRAM. An assembled
manifest must override the actual ROM under test, not only a display label.
Do not silently test the earlier component path instead.

For repaired map data, reuse authenticated clean native captures and the existing
terrain-native-probe.s. Execute only the affected map IDs with original recursive
loaders and mGBA BIOS; record probe/reset-vector modifications separately from
candidate identity. Native loader equality is not rendered mission traversal.

Finalize acceptance runs before running package-assembled-art in a separate
runner invocation; pending input-integrity results cannot authorize packaging.
A completed passed step within a later failed run can be reused when its inputs
are unchanged and its exact-candidate report passes. Preserve enclosing failed
status and failed-step IDs in the package evidence. Parent battle evidence needs
an explicit bounded whole-ROM difference and a separate current test of the
changed consumer; a shared filename or similar hash is insufficient.

After packaging, invoke test-art-pipeline-launcher separately in validation mode.
Never start a game or import player saves as part of packaging. Keep technical
coverage and exclusions in ART-PIPELINE.md and the immutable package manifest.


### Native-scale imagegen revision review

Measure authenticated original opaque bounds for the same race before prompting.
Distinguish body footprint from the32x32 import canvas; filling nearly the whole
canvas can change human proportions. Use original sprites only as references,
never bases to recolor. Record actual output dimensions when imagegen ignores
requested dimensions/grid, and never call an enlarged pixelated image native-ready.

Review conversions in the actual consumer palette, alongside original references
and the current packaged asset. Compare nearest and averaging only where detail
loss warrants it. Scale/baseline/quantizer changes are technical conversions;
new character pixels and visual corrections still come from imagegen. Record
per-frame opaque bounds and costume/foot continuity, not just a large sheet's
appearance. Changes in indexed pixels describe drift but do not automatically
accept or reject aesthetics. Reject inconsistent idle phases before extending
that model into expensive walk/action batches. Preserve rejected sources and
exact prompts without replacing the production catalog or playable preview.

### Native cadence and direct consumer palette mapping

Inspect original frame order, commands and timing before specifying animation
motion. FFTA human idle can be a three-pose stepping cycle A/B/C/B at16/8/16/8;
do not impose fixed feet or breathing merely because an animation is called idle.
Judge costume/anatomy/facing continuity separately from intended leg motion.

When a native palette is fixed, use convert-generated-sprites.py with
--native-palette-offset against the authenticated clean ROM. This maps original
sampled RGB directly to native indices, avoiding an intermediate quantization.
Keep the legacy conversion available and verify byte preservation. The palette
is specific to a consumer: actor and wheel miniatures may use different colors.
Never treat lower numeric color error as visual or production acceptance.

For generic actor colors, authenticate both native job properties6 and7: the
low and high nibbles of record+11 select party/opposing sources. A same-race
enemy fixture must allocate its body after the declared job change. Preserve
side, positions and unrelated template data; specify legal equipment inputs.
Palette-reference matching does not establish hardware-bank capacity. Count
current variant histories separately from native occupied banks, including
nonzero8bpp indices in potentially visible source tiles. Keep an exclusive-bank
shortage distinct from a hardware impossibility claim.

Private build checks must reproduce the selected candidate's complete option
set. Snapshot historical manifests before building even with publish_current
disabled: a byte-identical output can share its historical hash directory.
Restore those snapshots in finally, with a distinct backup variable that cannot
be reused by contract comparisons. Reuse a verified built ROM after a harness
failure when source/configuration and compiled bytes remain applicable. A passed
report emitted before failed cleanup does not make the runner successful.

Use samurai_idle_transport.py as the bounded three-pose example: authenticate
generated PNG; regenerate conversion; verify palette,4bpp and native allocation;
preserve sequence command/timing bytes; replace only intended tile/OAM pointers;
retain all other descriptors and prove a whole-ROM delta bound. Run the declared
test-samurai-idle-transport through Test Expansion.ps1 for native getters, exact
rebuild and paired actual menu playback. Capture all three distinct poses, not
just the number of sequence entries. Distinguish resource tile size from actual
consumer reservation: this menu reserves20 while its generated actor draws16.
Retain failures and use original captures to correct assumptions. Do not silently
publish a private draft into the accepted technical preview package.

### Original water-map fixtures and pending body transfers

For terrain-dependent graphics, keep a synthetic flag fixture distinct from an
intact original map. natural_water_fixture.py redirects one complete map record
within the existing encounter shell; its relative offsets still reference the
authenticated original table. Assert the whole-ROM change bound and record both
parent and actual fixture ROM hashes. Check complete native-loaded arrangement,
clipping and height data against original components before movement. Set only
declared starting unit positions; do not write water flags, live appearance IDs
or action results. This proves original-map terrain/rendering, not the map's
campaign encounter. Use the declared test-generated-natural-water.

A pending native facing transfer can retain its old image across two8-frame
samples. If this occurs, retain raw failure evidence and verify exact source
pixels before adjusting an oracle. pending_from_anchor requires pending flags,
an exact complete allocation and identity, and no more than16 video frames since
a directly verified image. Never reset anchor age from an inferred hold; discard
an anchor after any failed observation. test-native-pending-display supplies
negative controls. Do not infer whole-allocation history from unsaved captures:
separate visible-pixel retained evidence from full live allocation verification.


### Input-arrival sensitivity before timing changes

Use test-art-scheduler-phase to separate input-arrival variation from compositor
cost on its pinned mixed ready capture. Six fixed zero-input offsets precede the
same Move/cancel inputs; each active/bypass pair starts with exact ROM, RAM,
IWRAM and CPU wait point. Record complete positions, native input/frame/cycle
state and profiles. A compositor-bypass control intentionally lacks custom
colors and cannot become a playable candidate. Preserve ordered logical motion,
final positions and player records; report timing/color phases without silently
aligning them. Diagnostic pass does not close a failed performance gate.

Authenticate any later candidate difference before reusing earlier timing
observations. Never load older serialized actor pointers into a relocated ROM.
Reuse pinned endpoint RAM for heap census before replaying a map. Different
class profiles on the same encounter shell do not establish larger actor or
scene capacity. Before reducing a menu allocation, prove which list consumers
are reachable in that mode and retain the original copy/status/AP boundaries.


### Read-only Status ownership and inspection tests

See `notes/native-art-compact-status.md` for the measured checkpoint and limits.

Use --compact-battle-status only with the shared battle heap and owned-menu
builder options. Build the connected child from explicit status-current.json.
Compact ownership is marked solely by native entry08070688; mode1 alone is not
an adequate distinction from world menus. Retain the existing copy tail and
full460-row list in all unmarked contexts. Native lifecycle testing must include
both SP residues, an unmarked full context, normal compact context, native8KiB
pressure, preexisting allocated payloads and exact free-list restoration.

A Status global pointer can remain stale after teardown. UI tests must check the
live copy owner, allocated native block and shared-lifetime magic/counters too.
Directional controls switch Equipment/Abilities (ordinary states3/0F). Select
opens their inspection cursors (19/1B); A opens help1C. A outside inspection
closes Status. Help may consume B to complete text before closing. Use bounded
native-state transitions, preserving the exact inputs; never blindly press an
extra B or accept any nonblack screenshot. Keep failed harness assumptions and
visual-review rejections explicit even if a child originally reported passed.


### Mixed-class performance controls

Profile actual mixed-class raw inputs before carrying single-owner cost estimates
into a many-owner scene. Pin every input hash and compiled RAM layout. Component
composition may use an ABI-compatible relocated module only when no saved actor
animation pointers execute. Preserve native output/memory isolation checks.

For a preferred-assignment optimization, use an exact-state control that disables
only the validator and retains full palette composition/planning. Check that the
sampled scene still has multiple owners; include several fixed input-arrival
offsets and report response onset separately from movement duration. Retain failed
entry evidence even when its exact saved state can support a diagnostic replay.
Never call a faster instruction profile timing acceptance. Keep rejected source
patches and compiled candidates private, and pin historical test IDs explicitly
so restoring production does not silently change the experiment being examined.
See `notes/native-art-multi-preferred-trial.md` for the measured example.

### Reviewed full-animation authoring and import

Use `scripts/prepare-reviewed-actions.py` to inventory the final assembled actor
graph before authoring. Command1 publishes a drawing; native control records are
not separate drawings. Keep exact bindings from each distinct native pose to
every land/water sequence use, including the late Moogle additions. Final import
requires `gate-reviewed-actions-complete` in `scripts/reviewed-art-test-plan.json`;
an inventory-only pass explicitly does not close missing artwork.

For new poses, include the approved facing, several matching native pose examples
and the original illustrated concept as actual imagegen inputs. Preserve exact
prompts, source hashes and rejected attempts. Prefer individual pose worksheets
when a sheet trial changes identity or leaks donor clothing. Check the whole
target strip before extraction; a shifted pose may be translated into its cell,
but clipping raised limbs or inventing replacement pixels is not conversion.
Approved exact face reuse must remain a separately authenticated operation with
proof that all pixels outside its rectangle are unchanged.

Compare source art against the game's actual palettes before a large import.
Offline custom-palette previews do not establish hardware bank ownership. Any
palette architecture change needs explicit engineering impact review and direct
runtime consumer/performance checks. See
`notes/reviewed-sprite-integration-2026-09-20.md` for the active checkpoint.

The explicit importer is `scripts/import-reviewed-actions.py`. Its default path
requires every catalog pose to pass the reviewed-art gate. `--draft` is a private
diagnostic path: preserve missing mappings, count them explicitly, and never
publish it as complete. Archive the exact catalog and parent manifest beside
each generated ROM, so a later drawing revision cannot invalidate historical
test provenance. The extra action reservation is independently authenticated
as unused in the exact parent before writing any tiles, OAM or sequences.

Recover worksheet X translation from the generated top-right neutral and the
approved facing reference. Apply it as native OAM placement, not a pixel edit;
independently recompute the anchor during validation. Review both pose contact
sheets and native-positioned drawing loops with `scripts/review-reviewed-actions.py`.
Those loops omit native control execution and do not prove live action playback.
Use the `revise` command to preserve rejected artwork, prior metadata, the reason
and the exact revised imagegen prompt. Never overwrite the previous generated source.

Keep palette-only and explicit-action cold-entry evidence separate. The latter
uses `test-reviewed-action-cold-entry` and `action-entry-latest.json`;
`test-reviewed-samurai-fight` consumes that authenticated own-ROM world checkpoint.
Run test runners serially and wait for their process to exit: a printed final
step result does not mean the runner has finished retaining/pruning its evidence.

Record primary visual review with `scripts/record-reviewed-action.py` only after
inspection. It pins exact artwork, native-reference and original-concept hashes;
it is not user approval or runtime acceptance. Keep concise pose-meaning hints
with the prompt when references alone lose the action. Turning sequences can
alternate facings within one slot; choose the approved anchor by drawing phase.

Action imports archive each used PNG by content hash and archive catalog, parent
manifest and importer source in a provenance-specific folder under the ROM hash.
Review-only metadata changes can leave ROM bytes identical, so ROM hash alone is
not a unique provenance key. Historical archives must remain immutable.

`test-reviewed-samurai-water` uses an authenticated own-ROM world checkpoint and
an intact original water-map record. Preserve terrain, inventory and return
position checks. A relocated off-screen actor may leave stale palette tags;
verify its absence using native OAM at composition time, and separately require
the water actor to be visibly rendered with the new palette. Never waive a
visible mismatch by treating all stale tags as harmless.

The same water script accepts `--job 116..125`; it derives race, land/water
resources and palette ownership from the exact candidate. Use declared class
Fight/Combo/water IDs in the reviewed-art plan. Those checks preserve the existing
preallocation inputs and native menu route. Passing a test on a draft that still
contains placeholders never accepts the missing new artwork.

Save image-generation receipts immediately per pose, including the exact prompt,
three referenced image records, version and tool-returned source path. Resume
technical extraction with `scripts/ingest-reviewed-receipts.py`; serialise these
calls because they update the shared catalog. A receipt is not visual approval.
Inspect the entire worksheet before authorizing an exceptional horizontal
translation, and bind that authorization to the immutable generated source hash.

Portraits use `prepare-reviewed-portraits.py`, `ingest-reviewed-portraits.py`,
and `import-reviewed-portraits.py`. Review all ten against their concepts before
import. Rebuild portraits from the latest action candidate, preserving original
portrait records and all palette modes. Native menus flip object origins as well
as image pixels: authored X=-56 produces displayed X=-8 for the reviewed 64x64
portrait object. Fit the generated silhouette within 44x54 during technical
conversion and verify its actual opaque bounds in the 48x56 visible menu window.
Use declared `build-reviewed-portraits`, `test-reviewed-portrait-import`, and
`test-reviewed-portrait-menus` checks; inspect their real screenshots as well as
byte checks. Portrait acceptance does not establish wheel or small-icon colors.

When sprite and illustrated-concept colors differ, make the approved sprite the
explicit authority for face, ears/hair, headgear, palette and proportions. Keep
the original concept as an actual input for costume details, without allowing it
to redesign the approved sprite. Check a small identity-preserving pilot before
expanding an action batch. The Moogle and Viera identity pilots use this order.
If later comparative review reveals a defect, `prepare-reviewed-actions.py
revise` archives even a previously source-reviewed drawing and its review. It
also preserves raw output from failed extraction without inventing a valid PNG.
`apply-reviewed-action-decisions.py` applies explicit per-pose human review
records; it does not judge art automatically. `review-reviewed-actions.py
--awaiting-only` produces focused sheets for each revision batch.
# Complete reviewed animation and menu import

Use `build-reviewed-actions-complete` in `scripts/reviewed-art-test-plan.json`
after the source catalog reaches675 reviewed poses. This invokes the importer
without `--draft`; incomplete or unreviewed art is rejected. Extended horizontal
registration is allowed only by the same exact-source approval checked by the
catalog validator. Import actions before reviewed portraits. Preserve the
immutable per-ROM provenance and source copies, not only the mutable candidate
pointer. `test-reviewed-action-import` verifies every draw/control record and
native resource selector. Its success is not action playback or timing acceptance.

The private `build-reviewed-menu-miniatures` stage takes the combined portrait
candidate. It re-encodes64 menu figures with the original54 unchanged, binds
generated indices54..63 through the three native upload paths, and redirects
only the exact32x40 miniature layout at its native draw call. It clones the
menu palette table and keeps bright/dim variants separate. Banks0..8 and12,
background palettes, original figures and battle code remain unchanged.
Its264-byte upload map occupies0203ED00..0203EE08 inside existing reserved
palette pages; the builder must authenticate compiled Live and party-root bounds.
ROM storage is a checked suballocation after the action payload within the
action reservation. Do not assume these addresses remain free after another
component grows. Run both `test-reviewed-menu-miniatures-native` and
`test-reviewed-menu-miniatures-ui`; inspect the actual screen colors afterward.
Small equipment badges remain a separate consumer and are not completed by this
stage. Full production acceptance still requires affected native actions,
cross-consumer palettes, performance, isolated packaging and visible launch.
# Reviewed-art preview checkpoint and catalog storage

`scripts/snapshot-reviewed-art-catalog.py export` stores the complete animation
catalog as ten per-class JSON documents and an authenticated index. Each stays
under the source asset guard's four-MiB limit. After a fresh checkout, run the
same script with `restore` to recreate the ignored aggregate
`src/art/race-study/full-animation-v1.json` byte-for-byte. Run `verify` before
building; after changing source approvals or attempts, export again. No prompts,
failed attempts or review decisions are discarded. Private image files remain
separate, as before.

The combined preview chain is reviewed actions, reviewed portraits, reviewed
menu miniatures, then reviewed menu badges. Use the declared steps in
`scripts/reviewed-art-test-plan.json`. Build the gallery with
`scripts/build-reviewed-game-gallery.py`. After `test-reviewed-preview-save`
passes, `scripts/install-reviewed-art-preview.py` copies only the verified
disposable showcase into an absent preview save file. It preserves every existing
save and installed ROM; never use it to migrate player progress.

`scripts/launch-reviewed-art-preview.ps1 -ValidateOnly` authenticates the specific
preview ROM and isolated storage without launching. The ordinary launcher opens
standalone mGBA. Desktop launching follows AGENTS.md's interactive-desktop path;
window listing and successful launch are distinct from screenshot verification.

The preview is not final performance acceptance. The strict no-added-delay gate
remains open; keep its failed report visible in the checkpoint and gallery.
Do not replace `Play Expansion.cmd`, its accepted ROM, or its save paths.
