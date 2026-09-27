# Physician and Sapper: fixed-origin motion revision

The user requested more faithful sprites and animations using the completed
native position atlas. This pass preserves the four approved neutral drawings
and regenerates motion proposals against the actual native action records.
Gameplay source, ROMs, releases and saves are outside this art task.

Local review and generation inputs are under ignored
`build/art/chemist-anchored-revisions-2026-09-27/`. The complete native atlas is
under `build/art/chemist-animation-anchors-2026-09-27/`. They contain original
references and mixed worksheets and must not enter the public artwork inventory.

## What changed

Each request compares the same original actor's neutral and action in the top
row, with the new approved neutral and target below. Every cell retains the
same native coordinate system. The original images are never fitted or resized
relative to each other. The generator receives one relevant identity view and
the existing native palette, rather than conflicting front/rear references.

Small steps use an editable neutral; substantial pose changes use an empty
target with explicit instructions about the head, torso and feet. Face-down
collapse and mid-sequence turns needed those anatomical instructions. Matching
the four outer bounds alone did not prevent the wrong posture or a standing
shadow on an airborne frame. Missing anatomical evidence is not replaced by a
claim that shared pixel patches are a named skeleton.

Water collapse initially reverted to an upright figure. The final retries used
the revised land collapse as an explicit related-pose anchor, paired with its
original land drawing and the original water target. A neighboring bowed water
pose similarly anchored its alternate ripple frame. Turning frames were checked
from the drawing itself, not inferred from sequence parity.

Conversion samples the whole declared grid once and extracts the fixed 64x64
reference window. It uses only the approved base's existing native palette
indices. No palette bank or runtime graphics allocation is added. Inspected
uniform placement errors may receive a recorded rigid translation tied to the
raw generation hash. This preserves every pixel and cannot repair proportions.

The review preserves ordered native records, timing, repeated keyframes and
controls. Browser players simulate the drawing durations; they do not execute
native control commands. The page has stepping, integer zoom, mirroring and
image enlargement. Annotations use Codex browser comments only.

## Reproduce

Follow the fixed-origin revision section of
[NEW-JOB-ART-RUNBOOK.md](../NEW-JOB-ART-RUNBOOK.md). The source tools are:

- `prepare-anchored-job-revisions.py`: fixed reference requests and optional
  reviewed pose notes, blank targets and identity-view overrides.
- `revise-anchored-job-request.py`: immutable retries or inspected registration.
- `convert-anchored-job-revision.py`: palette-constrained technical conversion.
- `contact-anchored-job-revisions.py`: unchanged reference/result contact sheets.
- `review-anchored-job-revisions.py`: explicit selected attempts and full review.
- `test-anchored-job-revisions.py`: real-input integrity and playback coverage.

Requests preserve exact prompts and ordered reference hashes; receipts preserve
raw/native hashes, conversion geometry, palette words and any registration.
`choices.json` names each selected revision explicitly. Failed attempts remain
available and are not selected by a newest-file heuristic.

## Acceptance boundary

The completed proposal review contains all 68 Physician and 80 Sapper drawings:
144 regenerated motions plus the four immutable bases. All 150 animation previews
and 737 ordered records are present. The complete integrity check passed,
including rejection of changed reference hashes, changed palette words, an
unbound translation and an excessive translation. The page's script passed
Node syntax checking; its local targets, asset links and ordered frames were
validated offline. Browser automation could not read this file URL, so these
checks do not establish interactive browser behavior or native game playback.

All selected results were inspected against native references. Two remaining
extent differences exceed two pixels: Sapper p071 has a longer lower pompom/ripple
extent, and p072 has wider surrounding ripples. These remain explicit visual
review items, not hidden fitting operations or automatic failures of anatomy.
The selected drawings and source prompts are recorded in
[the source provenance receipt](../src/art/new-job-review/chemist-anchored-motion-2026-09-27.json).
Mixed reference sheets, raw generations and page builds remain ignored locally.

New motion art is proposed for user review, not automatically approved by its
technical checks. Native storage/OAM packing and actual actor, weapon/effect,
portrait, badge and wheel consumers still require a separate import and final-ROM
verification. The data-only Physician/Sapper jobs are not made playable here.
