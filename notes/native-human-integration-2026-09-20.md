# Approved human native colors: verified battle checkpoint

The user chose the exact Samurai Palette 1 neutral backup with its muted scarf.
The approved PNG SHA256 is
`2fbe4a56e9b68e9a919cf8b6eb9cc76e4ae7b5aaafee5cf711b72ef63178b76b`.
It is the whole backup, not a composite of later face/scarf trials. The Human
Dark Knight approved base remains
`df111ab83c90de87948abb7aaf73e16a80de2b5dd6ebefba35ea518309cf3eed`.

## Reproduction

Run [the human plan](../scripts/human-native-color-test-plan.json) through
`Test Expansion.ps1 -Plan scripts/human-native-color-test-plan.json -Suite human-native-colors`.
The affected behavior is the Samurai's changed native colors across movement,
Fight, Combo and water entry/cancel. The plan also authenticates all original
animation records and retained Dark Knight bytes. This is a targeted art
change; no full campaign/integration rerun is justified.

[The converter](../scripts/prepare-approved-human-native-colors.py) applies
the exact approved neutral Oklab mapping to all 66 Samurai poses. Neutral poses
reproduce the approved backup byte for byte. It reuses the 66 Dark Knight PNGs
archived in the previously tested candidate. All other classes retain their
previous conversion in this candidate. No palette words, runtime hooks, player
saves, installed ROMs or launchers change.

[The importer](../scripts/import-reviewed-actions.py) accepts a combined
`units` conversion manifest, rejects duplicate classes or missing poses, and
archives the actual imported PNGs and recipe. The previous single-class format
remains supported. [The contract](../scripts/test-native-color-transfer.py)
verifies original source hashes, exact native indices, actual ROM tiles,
unchanged silhouettes and consistent cross-frame RGB/index mapping. It also
compares every retained Dark Knight tile, OAM and side selector to the tested
`bee412823471003eb42b4f7cbf0f65bc81a095a2` candidate.

## Passed evidence

ROM: `a586d625c7a017dc18436f424b5b0a85d0164a85`.
Candidate: `build/art/native-human-integration-2026-09-20/candidate.json`.
Runner: `build/expansion/test-runs/20260920T174747.216348Z/report.json`.
All eight declared steps passed, runner exited 0, inputs unchanged. Per-test
ROM hashes identify the candidate; the runner's legacy global hash does not.

- Native conversion contract: 41,110 checks.
- Complete animation import: 26,921 checks; 675 poses, 3,025 drawing records,
  1,116 command-only records preserved.
- Own-ROM cold entry: 38 checks.
- Samurai Move/Fight/next turn: 6,141 checks, 608 sampled action frames,
  28 damage, katana 106.
- Samurai Move/Combo/next turn: 26,640 checks, 608 sampled action frames,
  31 damage and one 3-JP debit.
- Samurai water entry/cancel: 1,270 checks.

[The gallery builder](../scripts/build-native-color-transfer-review.py)
with `--human --run <runner-report>` saves six intact in-game screenshots and
the actual imported Samurai sheet. Gallery:
`build/art/native-human-integration-2026-09-20/index.html`.
Screenshot hashes and source reports are retained in `review.json`. The primary
agent inspected movement, water and Combo captures. This proves the human
battle checkpoint, not final all-class/consumer acceptance.

## Remaining race color trials

Eight additional base color trials and two corrective generations used built-in
imagegen. Exact prompts, reference hashes, outputs and native conversions are in
[the source receipt](../src/art/race-study/nonhuman-native-color-v1.json).
These are primary-agent reviewed bases for an integration draft, not user
approvals. Raw generations sometimes lost outlines/shadows. Color calibration
therefore retains the original pose alpha instead of inserting those drawings.
The original full animation catalog is unchanged.

[The draft converter](../scripts/prepare-nonhuman-native-colors.py) reproduces
all eight base comparisons. `--all-poses` checks the reviewed base hashes, writes
543 other-race poses using the same five-neighbor color calibration, and creates
a separate combined conversion recipe. All eight full pose sheets were visually
inspected. Gallery:
`build/art/native-nonhuman-integration-2026-09-20/index.html`.

Historical checkpoint (superseded by [final integration](native-final-art-2026-09-20.md)):
the Bangaa Dark Knight's water ripple highlights mapped too strongly
to gold. Correct that before accepting its full animation set. Bard and Dancer
propose existing native palette 1; Mystic Knight proposes existing palette 0.
Those three class/side selector swaps are only declarations in the draft recipe;
they have NOT been applied to any ROM. The importer still requires parent
selectors to match. Do not silently weaken that check: future support must allow
only the authenticated declared class bytes and retain all native palette words.

The all-class final ROM, menus/portraits, complete consumer checks, separate
packaging and visible game launch remain unfinished. The broader user goal
stays active. The verified human candidate remains separate from these drafts.
