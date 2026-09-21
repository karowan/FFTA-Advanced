# Samurai face alignment and Dark Knight badge width

[Complete round-six page](../build/art/job-art-approval-v6-2026-09-20/index.html)
contains two new badge proposals with before/after comparisons. All ten jobs,
portraits, previous in-game screenshots, animations and keyframes remain on the
same page. Use Codex browser annotations. The proposals are not imported.

The round-five Samurai generation displaced its eyes relative to native anchors.
Restoring only the 19 shared pixels left additional dark pixels beside the right
eye. Thus a passing sparse-anchor check did not establish a coherent face. This
was an inspection failure, not a native palette restriction.

Built-in imagegen repaired the face using the compact round-five badge and
round-four face reference. Its generated eyes landed at columns 6 and 9. The
recorded integer translation moves the entire generated head one pixel right
before native conversion and anchor restoration. No scaling or manual painting
is used. The final inner eye area now contains exactly four dark pixels: columns
7 and 10 at rows 7 and 8, with no extra dark patch. The intermediate unregistered
conversion failed this expanded check with two unwanted pixels at column 9.

The Dark Knight badge was separately regenerated to extend each helmet side one
pixel outward while preserving eye positions and height. It uses no geometric
registration or horizontal rescaling this round. Native eye checks pass. At rows
5 through 8 the helmet-width estimates changed from `[10,10,10,11]` to
`[12,12,12,13]`, excluding background and blue-cloth indices. This estimate is
documented separately from human visual approval.

## Reproduce and inspect

- [Preparation and conversion](../scripts/revise-ui-art-round6.py)
- [Full review builder and targeted checks](../scripts/build-art-approval-round6.py)
- [Exact prompts and references](../src/art/native-ui-review/round6/plan.json)
- [Generation receipts and explicit crop/translation](../src/art/native-ui-review/round6/generated-paths.json)
- [Converted results and hashes](../src/art/native-ui-review/round6/results.json)
- [Native verification](../src/art/native-ui-review/round6/verification.json)
- [Expanded face and width checks](../src/art/native-ui-review/round6/targeted-verification.json)

With the private native references and raw outputs preserved under ignored build
folders, run `python scripts/revise-ui-art-round6.py ingest`, then
`python scripts/build-art-approval-round6.py`. The prepare action is only for a
fresh initial plan and refuses to overwrite an existing one. Imagegen's model
and seed are tool-managed. Both calls and their original outputs are preserved.
The 90%-opaque-row crop removes transparent letterboxing, then samples the
declared 80x14 row once and extracts the fifth 16x14 cell. The Samurai then uses
the explicit integer translation. Colors remain in existing native banks.

## Verification

Passed native palette membership, reference/output hashes, 19 Human face anchors,
full Samurai inner-eye dark-pixel check, Dark Knight eye-position and width
checks, and unchanged frame/lettering indices. Eighteen unaffected portrait/icon
surfaces remain byte-identical to round five. The full 675 poses, 796 sequences,
3,025 drawing records, 1,116 controls and 884 unused slots remain unchanged;
1,713 linked review assets resolve. JavaScript syntax and document links pass.
Final badges were visually compared at integer magnification.

No ROM, saves or runtime code changed, so no game build/runtime test was run.
Screenshots still show the previous assembled build. Live browser layout QA
remains unavailable after the earlier file-navigation restriction; no alternate
browser route was attempted. User visual approval remains pending.
