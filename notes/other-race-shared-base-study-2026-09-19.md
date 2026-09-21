# Other-race shared-base study, 2026-09-19

Applied the Human protected-pixel method to one neutral front pose for Bangaa,
Nu Mou, Moogle and Viera. Each receives an imagegen cook costume around its own
race's native shared pixels. These are base studies awaiting user review, not
production classes or completed animation sets.

| Race | Native resource IDs | Exact shared foreground pixels | Matching before protection | Matching after protection |
|---|---|---:|---:|---:|
| Bangaa | 11, 13, 14, 16 | 97 | 95 | 97 |
| Nu Mou | 18, 20, 21, 25 | 102 | 91 | 102 |
| Moogle | 35, 34, 37, 39 | 119 | 103 | 119 |
| Viera | 26, 27, 29, 31 | 120 | 116 | 120 |

Counts include every common opaque pixel, including shared ground/shadow pixels;
they are not counts of facial pixels. They apply only to these four references
per race at slot 0, frame 1. Resource IDs are not job IDs.

## Reproduce

Use Python with Pillow. Run
`python scripts/assemble-other-race-studies.py prepare` from the repository root.
This extracts unchanged native reference cells with crop `(32,28,64,60)`, aligned
on a 160x64 logical reference row; the fifth cell is the edit target. It saves
the exact prompts, native input hashes and template hashes in
[the generation manifest](../src/art/race-study/other-races-shared-base.json).

Use built-in imagegen once per race with that race's saved prompt and template.
The common short prompt is:

> Turn the fifth sprite into a [race] cook job using the SAME underlying [race]
> pixel base as the others. Keep the shared face, eyes, anatomy, pose and pixel
> positions unchanged. Change only the job-specific appearance: cream rolled
> sleeves, mustard apron and teal sash, no hat. Keep the entire row and its layout.

Only `prompt` and `referenced_image_paths` were supplied. Model version and other
settings are managed by the built-in tool and were not exposed. No external
provider or user-generated example was used.

Copy each raw result into
`build/art/race-study-2026-09-19/other-races/<race>-generated.png`, keeping the
original output. Run `python scripts/assemble-other-race-studies.py assemble`.
The script recovers the contextual grid without bbox fitting, converts costume
colors to the original reference palette, and overlays only unchanged original
pixels common to all four references. No new pixel patterns are authored by code.

The ignored output folder retains raw generations, recovered grids, immutable
layers, transparent 32x32 sprites, magnified sprites, original-versus-new
comparison rows and per-race proof JSON including source hashes and exact pixel
coordinates/colors. `all-races-comparison-8x.png` stacks Bangaa, Nu Mou, Moogle,
then Viera; the rightmost sprite in each row is the new design.

## Verification and limits

All four outputs pass exact coordinate/RGBA equality for their protected layers,
32x32 bounds and at most 15 opaque palette colors plus transparency. Original
reference cells in comparison boards come directly from native exports.
The assembled comparison was visually inspected for alignment, silhouette and
face retention. Costume shading becomes flatter during native palette mapping.

These preview palettes are not verification of final ally/enemy palette routing.
No native import, game build, animation expansion or runtime test was performed.
The next pose study must extract that pose's own native layer and use the approved
base design as the identity reference; this front-pose mask must not be reused
blindly on a different keyframe.
