# Samurai v7 artwork and private native preview

September18,2026. Follow-up to ef1ca96. Prior turn completed corrected technical
delivery; this turn creates actual artwork refinements with built-in imagegen.
No external provider, agents, publication, game launch or player-save changes.
The installed7507ca5c bundle remains unchanged. All G01-G04 full scopes stay open.

## Artwork

Exact prompts and image/reference hashes are in
`src/art/imagegen/samurai-march-v7.json` and `samurai-march-v8.json`.
Both are1536x1024 six-cell generated edits of the original generated red Samurai,
not edits of a native character. The underlying tool model name is not exposed.
Private PNGs are retained under `build/art/imagegen/samurai/native-scale-study/`.

v7 targets stable face/helmet/costume while preserving opposite lifted boots.
v8 targets a wider white eye. Initial visual inspection against black preview
background incorrectly concluded that v7 lost the white eye. Exact converted
pixel inspection proves two white pixels at(16,12)/(16,13) in all three front
cells of BOTH versions. The comparison on a neutral background corrects that
claim. v8 does not materially improve that feature and is not selected.

v7 remains a private refinement candidate, not full design approval. Both-source
and native-scale review show alternating feet, exposed face, red kabuto and
lamellar armor, purple underclothes and sheathed katana. Small crest/head/back
outline shifts remain visible. No complete attack/casting/water set exists.
Native source pixels are not copied, recolored or decorated into the character.

Conversions tested native-palette nearest, own-palette nearest and own-palette
box. The selected conversion is own-palette nearest,3columns,2rows,height27,
shared15-color RGB555. Code only extracts/scales/quantizes/composites; it draws
no replacement art. `scripts/review-samurai-march-v7.py` authenticates source,
original human reference, conversion palette and tile hashes, then creates:
- `march-v7-v8-comparison.png`: originals Soldier/Paladin at left; six candidate
  frames at the same native scale. v7 top/v8 bottom.
- `march-v7-loop.gif`: front/back marching loop0/1/2/1, timings270/130/270/130ms
  approximate native16/8/16/8ticks. This is a composite, not emulator video.
- `march-v7-review.json`: measured dimensions, white-eye coordinates, upper
  region differences and actual moving-frame hashes linked to the runtime report.

## Import and preservation

The palette stage previously replaced the earlier v4 walk transport with catalog
repeated draft poses. A private explicit override now authenticates new source
and conversion identities and supports six-pose sheets for any non-diagnostic
class. The existing Dark Knight diagnostic source remains pinned; overriding117
is explicitly refused in this initial refinement interface.

`src/art/imagegen/samurai-v7-preview.json` selects only job116. Default builds
retain the existing catalog and produce the exact prior palette ROM. Six-pose
selection uses0/1/2/1 front and3/4/5/4 back with original timing/commands. Unfinished
other action slots repeat these poses and water remains a crop, clearly outside
finished animation acceptance. The override is not final-art acceptance.

`test-samurai-v7-build` compares the no-override build against the current
installed palette stage, then checks that the compiled engine differs only in
Samurai's32-byte color table, all symbols stay fixed, all other class pixels and
all native sequence control/timing words are preserved. It constructs the private
connected candidate without advancing installed or historical indexes. Source
manifest bytes temporarily reconstructed by the default build are restored.

Private candidate:`d80e763169223d98284b180a39fa047f650d50e5`.
Resolve through `build/art/refinement/samurai-v7/current.json` (palette view).
Full candidate manifest is in the build report. It is not packaged or installed.
Menu icons/portraits still use earlier temporary art; that mismatch remains open.

## Evidence

Declared runner20260918T214811.137559Z passes:
- `test-samurai-v7-build`:8,490 checks;
  `build/art/refinement/samurai-v7/20260918T214811.803347Z/report.json`.
- `test-samurai-v7-entry`:3,097 checks;
  `build/art/live-palette/battle/20260918T214823.774628Z/observed.json`.
  Fresh entry, four coexisting generated class palettes and96-frame focus idle
  cycle. Slot5 Moogle Chemist is an explicit presentation-only fixture retaining
  original Viera stats; no recruitment/class legality claim. Three distinct
  Samurai uploads pass, along with native shadow/unowned-bank/VBlank checks.

Runner20260918T215024.299075Z passes `test-samurai-v7-walk`:6,674 checks;
`build/art/explicit-walk/20260918T215025.008748Z/report.json`.
Actual native Human Samurai Move from(1,13) to(4,13) and cancel displays three
exact generated tile hashes. Native allocation, current hardware palettes and
paired canonical gameplay outcomes match. Root reviewed ready/moving/moved
screenshots. Some battle captures overlap nearby actors; the unobstructed
sprite-loop comparison is explicitly composited. No emulation failures in these
three checks. Runtime reports preserve scope; no all-direction/attack/water or
production-art acceptance follows from one passing march.

All runners are terminal. Installed delivery and existing player files are
unchanged. Next create Samurai's actual attack/cast/hit/KO/water poses, keep
front/back costume identity, and align menu/portrait art with the selected design.
Then extend the same generated-art review/import path to the other nine racial
jobs. Reuse current transport evidence; do not redo technical infrastructure or
mistake repeated march poses for finished action animations.
