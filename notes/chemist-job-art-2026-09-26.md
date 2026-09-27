# Physician and Sapper art restart

Fresh artwork task, 2026-09-26. The prior withdrawn drafts are not inputs.
The gameplay implementation remains a separate, unplayable data-only candidate.
This task follows the successful earlier class sequence: original illustrated
concept, exact native reference worksheet, native front/rear base review, then
approved anchors propagated to animations and independent UI consumers.

Work is isolated under ignored `build/art/chemist-job-art-2026-09-26/`.
No game ROM, release selector, player save or gameplay source is modified here.
Built-in imagegen creates artwork; code composes references, converts the native
grid and validates outputs. Existing same-race artwork is reference only.

## Approved checkpoint

The user separately approved the ivory/teal Physician and goggled utility-vest
Sapper concept directions, then answered **"Approve both native bases"** for the
exact front/rear designs and native palette-0 colors on September 26. The
[source receipt](../src/art/new-job-review/chemist-base-2026-09-26.json) records
the prompts, input/output hashes, shared-face masks and exact approval scope.

Selected files inside the work directory:

- `physician-front-anchored-native.png`
- `physician-rear-native.png`
- `sapper-front-anchored-native.png` (from the simplified-goggles revision)
- `sapper-rear-native.png`

The front worksheet preparer reproduced both historical reference worksheets
pixel for pixel. Conversion replay reproduced all seven native base-study
outputs. Six offline checks passed, including rejection of changed sources,
palette words, clipping and incorrect worksheet aspect ratios. Private report:
`build/art/new-job-art-check-01af4f33052d/report.json`. This is technical evidence,
not runtime acceptance.

## Complete proposal checkpoint, September 27

The authoring inventory inherits the Nu Mou and Moogle Chemists' native
land/water drawings and command records: 68 and 80 distinct drawings. Four
exact neutral drawings are fulfilled by the approved bases; the remaining 144
received individual generation and inspection. Requests and progress are under
`actions/`; no new runtime resource IDs have been allocated by this artwork task.

All 68 Physician and 80 Sapper drawings are now selected on the complete review
page, including four immutable approved bases. The remaining 144 are proposals.
The [proposal receipt](../src/art/new-job-review/chemist-proposals-2026-09-27.json)
records every chosen attempt, source/request/conversion/native hash, translated
crop registration, menu provenance and representative exact generation requests.
The full immutable requests and raw attempts remain in the ignored work folder.

Focused revisions corrected the Physician's case side, skin-color drift and one
background box; Sapper revisions corrected front/rear facing, airborne shadows
and headgear contamination from repeated Black Mage fallback references. Failed
attempts remain preserved. Tall poses and status sparkles that fit a 32-pixel
cell received inspected, source-bound vertical extraction translations; those
origin deltas still need to be carried into actual native import.

Two independently generated 48x56 portraits and two frontal 16x14 heads are
converted to existing native palettes. Equipment badges use original frame
pixels and the current engine's unstretched font. Wheel figures preserve the
approved body indices in 32x40 storage. These are previews, not verified runtime
consumers. The dim badge uses colors from the preserved native screenshot and
still requires real eligibility rendering checks. No custom palette was added.

`review.html` contains concepts/bases, UI proposals, all 150 populated animation
players, all 737 ordered frame/control records, and every distinct keyframe.
Controls provide stepping, pause, size selection, mirroring and enlargement.
Use Codex browser comments; no page annotation storage was added.

Eight offline checks passed (`build/art/new-job-art-check-3bb343e3d0cf/report.json`):
base replay, source/palette/crop/aspect rejection, four UI replays including face
anchor proof, unknown-pose rejection and Python syntax. The complete page audit
found 148/148 drawings, 871 image elements, 1,049 unique targets, no missing links
and no pending drawing placeholders. Playback durations match the inherited
ordered drawing records. Its JavaScript passes syntax validation. Codex opening
returned `queued`; browser layout and interaction have not been visually verified.

Remaining: user animation/UI review, inventory approval for generated assets,
native resource allocation/import, any job-specific weapon/effect requirements,
and separate final-ROM consumer tests. Browser playback does not simulate native
control commands. The data-only jobs remain unplayable and are not enabled.

## Reproduce and continue

Follow [NEW-JOB-ART-RUNBOOK.md](../NEW-JOB-ART-RUNBOOK.md). To rebuild the approved
base review from the preserved raw inputs:

```powershell
python scripts/new-job-art.py convert --plan build/art/chemist-job-art-2026-09-26/base-plan.json
python scripts/new-job-art.py review --plan build/art/chemist-job-art-2026-09-26/base-plan.json
python scripts/test-new-job-art.py
python scripts/review-new-job-actions.py --manifest build/art/chemist-job-art-2026-09-26/actions/actions.json --selections build/art/chemist-job-art-2026-09-26/actions/selections.json --base-page build/art/chemist-job-art-2026-09-26/index.html --menu build/art/chemist-job-art-2026-09-26/menu/menu.json --output build/art/chemist-job-art-2026-09-26/review.html
```

The complete page is `build/art/chemist-job-art-2026-09-26/review.html`; it supports sprite
enlargement and Codex browser comments. It contains no custom annotation system.
Keep immutable raw attempts and use separate revision IDs. Do not resurrect the
withdrawn art from the other task or automatically enable the data-only jobs.
