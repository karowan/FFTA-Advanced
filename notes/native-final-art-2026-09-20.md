# Native artwork integration, September 20

The user-selected Samurai Palette 1 neutral backup with muted scarf is restored.
Its base SHA256 is `2fbe4a56e9b68e9a919cf8b6eb9cc76e4ae7b5aaafee5cf711b72ef63178b76b`.
The approved Human Dark Knight base remains
`df111ab83c90de87948abb7aaf73e16a80de2b5dd6ebefba35ea518309cf3eed`.
Nonhuman native-color bases are primary-agent reviewed, not additional user
approvals. Their prompts, references and exact outputs remain in
[the source receipt](../src/art/race-study/nonhuman-native-color-v1.json).
Its pending-status text is retained as historical input to authenticated builds.

## Delivered build and scope

Final ROM SHA1: `316a40524b960c49ad7213ac4b0bea539bfa9513`.
Manifest: `build/art/native-final-integration-2026-09-20/candidate.json`.
The build replaces all 675 class poses across 20 land/water resources, preserving
3025 draw records and 1116 animation controls. It also contains ten portraits,
ten native job-wheel figures and ten equipment badges. Actor animations include
movement, actions, casting, reactions, defeat and water; coverage is not limited
to walking. Original weapon/effect consumers remain native.

Native palette tables and executable behavior are unchanged from the accepted
engineering baseline. Only three existing class palette selector bytes change:
Moogle Bard and Viera Dancer `0x10 -> 0x01`, Viera Mystic Knight `0x01 -> 0x10`.
These are existing ally/enemy palette choices, not new banks or runtime remaps.
All other changes are allowlisted graphics data and graphics pointers.

The Bangaa Dark Knight water correction uses an imagegen supplemental reference
to calibrate colors absent from its standing base. Existing base mappings stay
frozen. Menu figures reuse exact native sprite indices; the existing menu
bright/dim routing remains intact. Badges retain their fixed native UI palettes.

## Verification

All runs below passed with unchanged source inputs during execution:

| Runner report under `build/expansion/test-runs/` | Scope |
| --- | --- |
| `20260920T181518.788201Z/report.json` | 30 all-race conversion/import/entry/mode/Fight/Combo/water steps |
| `20260920T182422.978603Z/report.json` | Four portrait/menu assembly checks |
| `20260920T182508.538155Z/report.json` | Nine final assembly/consumer checks |
| `20260920T182832.915620Z/report.json` | Ten final-ROM class Fight captures |

Final consumer coverage includes 815 menu assertions, inventory and shop badges,
a 13-actor mixed battle (18016 assertions), and native save plus cold Continue
(21 assertions). Every final-ROM Fight capture passed 6141 assertions and sampled
608 action frames. Mode/resource construction covers every native animation
binding; this is not a claim that every pose was individually played through
every possible campaign situation. Earlier human action evidence is retained.
The off-camera Bard in the mixed battle has its own final-ROM Fight check.

Primary review inspected all full pose sheets, all ten final menu captures,
portraits, equipment badges, mixed battle and representative final Fight images.
The initial portrait-import failure `20260920T182352.837608Z` is retained; the
missing output-directory creation was corrected before the passing retry.
Earlier rejected visual experiments and their evidence remain available.

No full campaign replay was rerun: this milestone changes graphics plus three
native class/side selector bytes. Exact final-ROM contracts, direct consumers,
cross-class capacity and save lifecycle bound the affected behavior. The prior
engineering acceptance still supplies unchanged gameplay coverage.

## Reproduction

Use the local bundled Python runtime for these scripts. Runtime checks must run
through `Test Expansion.ps1` with the declared plans. First reproduce the human
conversion checkpoint, then run:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/all-native-color-test-plan.json -Suite all-native-colors
& '.\Test Expansion.ps1' -Plan scripts/final-native-art-test-plan.json -Suite native-final-consumers
& '.\Test Expansion.ps1' -Plan scripts/final-native-art-test-plan.json -Suite native-final-screenshots
```

Select the plan's explicit IDs with `-Only` when resuming partway. Do not edit
source during an active runner. Use the passing final consumer and screenshot
runner reports with
[the gallery builder](../scripts/build-final-native-gallery.py) (`--run` twice).
It copies intact screenshots and records image/report hashes. The current
gallery has 33 images at `build/art/native-final-integration-2026-09-20/index.html`.

Run [the packager](../scripts/package-native-art-final.py), then
`scripts/launch-native-art-final.ps1 -ValidateOnly`. The package pins the final
ROM hash, authenticates evidence, seeds only an absent showcase save, and checks
all pre-existing save/play files remain unchanged. Packaging preserved ten
existing files. It never imports or overwrites player progress.

## Launch

[Play New Sprites.cmd](../Play%20New%20Sprites.cmd) opens the standalone Windows
mGBA application with independent save, state and screenshot storage in
`saves/native-art-final-2026-09-20/`. Original, engineering and prior-preview
launchers and save folders remain separate. The release ROM is stored in
`build/releases/native-art-final/FFTA_Reviewed_All_Classes.gba`.

On September 20, `-ValidateOnly` passed. No existing mGBA window was present.
The external desktop launch succeeded; Computer Use selected and raised the
returned mGBA window and visually verified the running opening scene at about
60 fps. No interactive test/gameplay inputs were sent. The packaged showcase
save is available through Continue; cold Continue was tested deterministically.
This launch observation does not substitute for the test evidence above.

ROMs, images, saves and raw reports stay ignored and local. No remote publication.
