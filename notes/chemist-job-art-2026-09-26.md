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

## Animation work in progress

The authoring inventory inherits the Nu Mou and Moogle Chemists' native
land/water drawings and command records: 68 and 80 distinct drawings. Four
exact neutral drawings are fulfilled by the approved bases; the remaining 144
require individual generation and inspection. Requests and progress are under
`actions/`; no new runtime resource IDs have been allocated by this artwork task.

The first walk/run drawings are being inspected. Preserve the rejected
Physician rear step with the medicine case on the wrong side; `p003-v2` corrects
it. Sapper running revisions remove invented standing shadows and restore the
required stride. Generated images are proposals until the complete animation
review. Portraits, badges, miniature graphics, effects and runtime import remain
unfinished. Neither this checkpoint nor the inherited inventory completes a job.

## Reproduce and continue

Follow [NEW-JOB-ART-RUNBOOK.md](../NEW-JOB-ART-RUNBOOK.md). To rebuild the approved
base review from the preserved raw inputs:

```powershell
python scripts/new-job-art.py convert --plan build/art/chemist-job-art-2026-09-26/base-plan.json
python scripts/new-job-art.py review --plan build/art/chemist-job-art-2026-09-26/base-plan.json
python scripts/test-new-job-art.py
```

The page is `build/art/chemist-job-art-2026-09-26/index.html`; it supports sprite
enlargement and Codex browser comments. It contains no custom annotation system.
Keep immutable raw attempts and use separate revision IDs. Do not resurrect the
withdrawn art from the other task or automatically enable the data-only jobs.
