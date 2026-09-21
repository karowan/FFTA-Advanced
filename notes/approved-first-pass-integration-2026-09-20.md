# Approved first-pass artwork integrated

The user approved the complete round8 review as a first pass and explicitly
requested a commit and game integration. The accepted asset hashes and native
palette choices are frozen in
[approved-round8.json](../src/art/native-ui-review/approved-round8.json).
This is first-pass visual acceptance, not a claim that later art polish or
full campaign coverage is complete.

## Delivered

- ROM SHA1: `f53fedb8421f48fd10faabf60700a5d7ed60ddf8`.
- [Candidate manifest](../build/art/approved-first-pass-2026-09-20/candidate.json).
- [Complete review with 14 current in-game screenshots](../build/art/approved-first-pass-2026-09-20/review/index.html).
- [Evidence and screenshot hashes](../build/art/approved-first-pass-2026-09-20/evidence.json).
- [Play New Sprites.cmd](../Play%20New%20Sprites.cmd) opens the approved build.
- [Play Previous Sprites.cmd](../Play%20Previous%20Sprites.cmd) retains the preceding sprite build.

Ten approved48x56 portraits and ten frontal16x14 badge heads are imported. Four
Samurai walking drawings (p000,p002,p003,p005) use the reviewed consistency fixes;
p001/p004 remain unchanged. All675 body poses,796 populated animation sequences,
3025 drawing records and1116 controls remain in the game. Portraits, badge heads,
wheel figures, all animations and ordered keyframes remain together in the page,
including pixel enlargement and the Codex browser annotation workflow.

## Native import details

[import-approved-round8.py](../scripts/import-approved-round8.py) authenticates
the prior `316a40524b960c49ad7213ac4b0bea539bfa9513` build and applies35 bounded
data replacements: ten portrait payloads, ten two-byte portrait palette selectors,
ten badge payloads, four walking tile payloads and one Dancer icon donor byte.
Every other ROM byte is verified unchanged, including all animation descriptors,
timings, controls, executable code and palette payloads.

Portrait images retain their exact48x56 indices. Transport maps opaque indices
to native OBJ96..143, places the image at(8,8) in the existing64x64 object, and
inverts the native horizontal flip so the displayed portrait matches the review.
There is no image fitting, resampling, palette synthesis or new palette bank.
Job records now select original native portrait palette IDs
10,16,22,22,50,50,68,70,62,58 respectively for jobs116..125. Native color-mode
variants use the corresponding existing records.

Dancer's existing icon donor property changes29 to30, sharing the native plum
badge palette already used by Mystic Knight. The source donor table in
[job-wheel.c](../src/engine/job-wheel.c) matches that one-byte data change.
No runtime routing code, hook or palette system is added. Badge lettering and
frame geometry use the reviewed native equipment renderer output.

## Verification

[Declared targeted plan](../scripts/approved-art-test-plan.json): all8 steps
passed in [run20260921T035318.715869Z](../build/expansion/test-runs/20260921T035318.715869Z/report.json).

- `test-approved-import`: exact review-to-ROM pixels, bounded native portrait
  decoding, all ten generic-unit routes, three original native color modes,
  original palette selections for other jobs, and allowed-byte boundaries.
- `test-approved-contract`: all675 poses retain native colors; final assembly
  adds no custom palette ownership, menu palette changes or executable changes.
- `test-approved-entry`: authenticated disposable cold battle entry for this ROM.
- `test-approved-menus`:815 checks for all ten portrait menus, native placement,
  exact uploads/colors, wheel and idle-actor coexistence, reopening and unchanged
  named-character controls.
- `test-approved-equipment`:3787 native renderer checks across inventory/shop,
  both pages and eleven equipment items, including exact eligibility palettes.
- `test-approved-inventory-ui` and `test-approved-shop-ui`: actual fixed-input
  screens, paging/close behavior, and approved head pixels reaching VRAM.
- `test-approved-fight-116`: Samurai movement and native attack playback/captures.

The generic runner's top-level default engine hash is not this art candidate.
Every step's own report authenticates the above approved ROM SHA1; packaging
requires that match for all8 reports. Logs and fixed-input records are retained.
The primary agent visually inspected a contact sheet of all14 captures, plus
enlarged Human Dark Knight and Viera Mystic Knight menu screenshots. Review-page
asset links and JavaScript syntax passed. Both sprite launchers passed
`-ValidateOnly`; no desktop game launch was needed for this integration.

This localized graphics change does not alter combat rules, save format, roster
lifetime or campaign progression. The prior mixed-class, water, all-class attack
and cold-Continue evidence is retained, not misrepresented as a new full-suite run.
Browser visual automation was unavailable for local file pages; page verification
used source/link checks and direct screenshot inspection.

## Packaging and reproduction

With the ignored private inputs already present, run:

```powershell
& $fftaPython scripts/import-approved-round8.py
& '.\Test Expansion.ps1' -Plan scripts/approved-art-test-plan.json -Suite approved-art
& $fftaPython scripts/package-approved-art.py --run <passed-run-report.json>
& scripts/launch-approved-art.ps1 -ValidateOnly
& scripts/launch-native-art-final.ps1 -ValidateOnly
```

`$fftaPython` is the configured bundled Python executable. The importer validates
all input hashes and immutable output identities. The native original palette
decoder and existing4bpp/8bpp packers perform technical conversion only.

[package-approved-art.py](../scripts/package-approved-art.py) verifies all8
candidate-specific reports and preserves all11 existing files under saves and
roms/play. The new ROM is independently stored in
`build/releases/approved-first-pass/FFTA_Reviewed_All_Classes.gba`. The prior ROM
at `build/releases/native-art-final/` is not overwritten. Both art launchers use
the existing compatible `saves/native-art-final-2026-09-20/` directory; the save
is neither copied nor replaced. Vanilla and expansion launchers/save directories
remain unchanged. Packaging authenticates protected file hashes before/after.

Only source, approval receipts, scripts and this reproducible checkpoint enter
Git. ROMs, generated artwork, screenshots, test logs and saves stay ignored.
