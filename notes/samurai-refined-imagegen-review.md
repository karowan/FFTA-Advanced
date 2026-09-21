# Samurai native-scale imagegen refinement

September 17, 2026 local. Prior commit ef49aa7 proved explicit animation frame
assignment; this continuation makes actual artwork progress through that path.
All G gates remain open. No external provider, agents, publication, game launch
or player-file mutation.

## Artwork and review

Built-in imagegen created two six-frame revisions from a blank Samurai design
and authenticated original human proportion references. Exact prompts, roles,
settings, source hashes and private PNG paths are recorded in
`src/art/imagegen/samurai-march-v3.json` and `samurai-march-v4.json`.
The tool's underlying model name is not exposed. Original sprites were used
only as references. Code converted/composited pixels; it drew no character art.

- v3 source SHA-256: cdb60ddc2fcfed6f164540da227e14c42bf56f2f5d1321435fc23b7844042395.
  Narrower costume, but the eye and crescent disappear inconsistently after
  native conversion. Converted bounds are 16x26/27.
- v4 source SHA-256: 17deae2a4046fafbd2420f0f93fbefae0b6e3f96f688673977f1e5dd5b1f44d1.
  Targeted face/crest edit. All six converted cells are 16x27. Front features
  remain more consistent; leg movement is weak and costume/back details drift.

Both PNGs are 1536x1024. Conversion uses three columns, two rows, common height
27, nearest sampling and direct native palette 0x419d80. Source pixel density
still does not exactly obey the requested logical grid. These are unaccepted
drafts, not finished production sprites. The generated edit also changes some
body/back details despite the prompt asking to preserve them; review does not
claim that edit invariant was met.

`scripts/review-samurai-refined-art.py` authenticates the originals and generated
sources/converted tile hashes and writes the comparison and measurements under
`build/art/imagegen/samurai/native-scale-study/`:

- `march-v4-comparison.png`: original Soldier, original Paladin, v3 front,
  v4 front A, v4 front B, v4 back A, all at the same pixel scale.
- `march-v4-review.json`: dimensions and phase differences. Sampled v3 pairs
  differ by 144-176 pixels, v4 by 53-80. These are descriptive measurements,
  not an art acceptance threshold or a requirement for fixed feet.

Inspected that comparison and the actual passing `mapped-move-90.png` capture.
The new Samurai is narrower/smaller beside the original characters than the
previous broad draft. Its lower body still lacks convincing alternating steps.
Keep final visual acceptance open.

## Private native integration

`src/art/imagegen/samurai-refined-transport.json` maps frames 0,1,2,1 and
3,4,5,4 to Samurai land slots 0-3 with native timing retained. Private action
stage SHA-1: `0fa7d1707e2d85fb2a8602f061b5eb4479ff3211`, resolved through
`build/art/generated-actions/refined-samurai-current.json`. It uses 119,484 bytes
in the existing action reservation. Base remains d1241ede; paired comparison
remains de09bc0f. This stage is not assembled or packaged. Existing a6d883b5
technical delivery, a860ad38 four-frame proof and 352df0a6 idle proof are unchanged.

The existing explicit-plan/walk tests now accept named plan/current arguments,
retaining their prior defaults. The plan check reads the declared frame order
instead of assuming source cell number equals native phase. Its test scope
remains explicitly limited to Samurai land slots 0-3.

## Evidence and reproducibility

Declared runner 20260918T013422.633473Z passed:

- `test-samurai-refined-plan`: 10,642 checks; report
  build/art/animation-plan-tests/20260918T013423.242959Z/report.json.
- `test-samurai-refined-walk`: 3,649 checks; report
  build/art/explicit-walk/20260918T013433.309654Z/report.json.

Actual recruited Human Samurai Move/cancel displays three distinct generated
phases during interpolated motion; paired gameplay outcomes match, owned
allocation is verified, and the retained world fixture is unchanged.

Review found conversion folders were keyed only by asset name and palette
offset, so different revisions named `walk` overwrote that regenerable output.
The importer now keys folders by source hash, conversion settings and exact
palette hash. This prevents revision collisions without changing ROM bytes.
Earlier reports remain historical evidence; mutable old conversion paths must
not be assumed unchanged merely because a report names them.

Only `test-samurai-refined-plan` was repeated after this metadata/workspace fix:
runner 20260918T013613.937999Z, 10,644 checks passed, report
build/art/animation-plan-tests/20260918T013614.478835Z/report.json. Two additional
checks prove same-name revisions use distinct folders and preserve the newer
manifest while converting the older source. ROM SHA-1 remains 0fa7d170, so
the exact-candidate movement pass is reused. No runtime failure this turn;
all previous failed runs remain documented in the earlier checkpoint.

Reproduce via `Test Expansion.ps1 -Plan scripts/native-art-test-plan.json -Only
test-samurai-refined-plan,test-samurai-refined-walk` in PowerShell. For an
unchanged ROM, reuse the recorded movement evidence rather than rerunning it.
Then run the review script for the static comparison. Generation from a prompt
is not deterministic: the pinned PNG bytes are required build inputs.

Next refine the leg/arm phases and costume continuity with imagegen, using the
smaller silhouette as the current design direction. Do not substitute more
transport tests for the remaining artwork. All other new jobs, directions,
actions, water, UI/portrait consistency and final assembled acceptance retain
their documented production-art gaps.
