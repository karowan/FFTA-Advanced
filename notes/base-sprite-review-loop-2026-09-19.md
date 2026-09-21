# Single Human base: five-round review experiment

Scope: one original bald cook base only. The user paused other races and pose
production to refine this base, then authorized two independent art reviewers
and at most five refinement rounds. No game build, ROM/save changes or runtime
tests were needed or performed. Artwork is still a draft, not a finished class.

All character creation/revisions used built-in imagegen. Model name, seed and
inference settings were not exposed. Exact prompts are in
`src/art/race-study/review-loop-{1..5}.json`; private generated sources, references,
conversion manifests and comparisons are under
`build/art/race-study-2026-09-19/`. Preserve all rounds, including failures.

## Findings and decisions

| Round | Method | Independent review / decision |
|---|---|---|
| Baseline v3 | Repeated single-sprite facial edits | Both: needs refinement; oversized eyes, too-fine shading and elongated proportions. |
| 1 | Redraw from native style plus original cook | Both: needs refinement; far eye merges into outline at native size; narrow body. |
| 2 | Edit the reduced sprite against native reference | Both: needs refinement; key eye correction did not happen; torso improved. |
| 3 | Generate cook in fifth cell beside four native sprites | Both: source eye angle now right; conversion loses eyes; head detail and added ground oval remain. |
| 4 | Preserve face; simplify head and remove ground oval | Both initially said this looks right. User rejected the camera elevation: eye-level instead of slightly above looking down. Both reviewers withdrew approval. |
| 5 | Correct whole-body camera elevation | Both: needs refinement. Elevated source view improved; native eye/pupil detail fails. Reviewer A flags broad cranium; B flags frontal apron/boot planes. Five-round cap reached. |

Final status: no accepted base. Latest candidate is `review-loop-5.png`; full
raw context is `review-loop-5-context.png`; native review is
`review-loop-5-grid-review/comparison-8x.png`, all under the private study folder.
Reviewer outcomes are retained in `src/art/race-study/review-loop-outcome.json`.
Root agrees these are unresolved visual issues; the user has not approved a base.

The user's camera correction is a central requirement: native characters are
viewed from slightly above, not straight ahead at ground/eye level. Turning the
face left/right or revealing the second eye does not establish the correct
camera. Crown, shoulder tops, torso foreshortening, boot tops and foot depth must
agree. Native reference hats can obscure this difference; a bald design exposes it.

## Reproduction and technical conversion

Use the bundled Python runtime with Pillow. This process performs only cropping,
color-keying, scaling, palette conversion and image comparison; it paints no art.

For contextual sources (rounds 3 onward), the output has five equal-width cells.
`scripts/extract-context-art-study.py SOURCE OUTPUT` extracts cell five and removes
only border-connected neutral background pixels using the recorded color key,
20-channel tolerance and maximum chroma 22. Retain the extraction JSON and raw
full image. This key is specific to this neutral-background experiment; inspect
edges and pale clothing instead of treating it as a universal extractor.

The contextual input workbench is 1280x512: logical 160x64 at 8x. Its fifth cell
is logical 32x64. `scripts/review-base-art-loop.py SOURCE OUTPUT --context-grid`
recovers this full cell grid using nearest sampling, crops logical rows 16..47,
asserts no opaque content is clipped, then uses the existing converter with
scale exactly 1. It creates a 32x32 indexed draft with at most 15 opaque colors.
The full image generator may output different dimensions; the grid is recovered
from proportional cell coordinates. Requested grid alignment is not guaranteed.

Earlier bbox-fit conversions remain preserved. At round 3, height 27 dropped
thin eye cores. Height 28 retained dark cores at canvas (13,10) and (15,10), but
changing the target height is not a general correction. Round 4 introduced the
full-cell grid method to avoid arbitrary per-character scale/phase changes.
Even this method requires visual inspection: fine or off-grid source details
can still disappear after conversion.

The conversion uses a generated 15-color visual-study palette. It does not prove
final shared ally/enemy palette quality, native actor import or animation. The
reference comparison uses the original user image, never regenerated neighbors.

## Next gate

Finish visual acceptance of this one base with the user before generating more
poses. Then keep the approved base as the identity reference and provide a
separate exact native keyframe as the action/facing reference for each individual
pose. Review the base first so a weak donor-derived identity is not multiplied.
