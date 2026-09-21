# Hide undiscovered expansion jobs

Current distribution and launching use the [BPS release workflow](../MOD-RELEASE.md).
The raw-ROM packaging steps below are historical; the accepted game bytes and
gameplay evidence remain unchanged.

The approved-art wheel appended both new racial jobs unconditionally. It now
omits undiscovered jobs until a matching clan member meets the prerequisites,
already holds the job, or has earned AP in that job. Discovery reveals the job
for that race; only the selected unit's own prerequisites make it selectable.
Chemist has no prerequisites and remains immediately available to Nu Mou and
Moogles. Original job discovery, restrictions and confirmation code remain native.

## Delivered build and saves

ROM SHA1 `267fd273bffe2c26a7ed3507d236af80a29b74a8` extends approved first-pass
art SHA1 `f53fedb8421f48fd10faabf60700a5d7ed60ddf8`.
[Play New Sprites.cmd](../Play%20New%20Sprites.cmd) selects the fixed package at
`build/releases/job-visibility/FFTA_Reviewed_All_Classes.gba`. All art is retained.
The preceding approved and native-final ROMs remain unchanged. Saves continue at
`saves/native-art-final-2026-09-20/FFTA_Reviewed_All_Classes.sav`.

In-game saves remain compatible: no record sizes, IDs, inventory/AP arrangement,
format version, save checksum or serialization code changes. Two previously
zero reserved bytes at state offsets `0x1E7A..0x1E7B` hold ten sticky discovery
bits (bit0=job116). Quin history at `0x1E79`, spare `0x1E7C..0x1E7F` and preferences
at `0x1E80` remain untouched. Reads/writes require current `FFTAEXP1` format.
Migration already zeros the entire inventory allocation including these bytes.
Native saves already serialize them. Once discovered, a job stays known even if
the qualified member leaves. Old saves recover knowledge from current roster
eligibility, current jobs and earned AP; they cannot reconstruct a previously
dismissed member's history. Merely encountering an enemy is not a new discovery
trigger. No player save was loaded into a test or replaced.

Save normally in-game, exit when ready, reopen Play New Sprites, and use Continue.
Emulator save states capture old code and transient menu state and are not an
update compatibility contract. A running emulator is not hot-reloaded. Future
changes that move saved records or IDs require a separate compatibility review;
ordinary code/art fixes do not inherently invalidate in-game saves.

## Reproduction and verification

[Declared plan](../scripts/job-visibility-test-plan.json) contains the exact
affected checks: `test-job-visibility` and `test-job-visibility-save`, with the
authenticated build prerequisite. Run:

```powershell
& '.\Test Expansion.ps1' -Plan scripts/job-visibility-test-plan.json -Only test-job-visibility-save
& $fftaPython scripts/package-job-visibility.py --run <passing-run-report.json>
& scripts/launch-approved-art.ps1 -ValidateOnly
```

`$fftaPython` is the bundled Python configured in Test Expansion.ps1. The
[builder](../scripts/build-job-visibility.py) authenticates the complete parent,
existing helper machine-code bodies and hook bytes. It compiles current
[wheel source](../src/engine/job-wheel.c) into verified blank ROM space
`0x1FF0000..0x1FF0FFF` (838 bytes used) and changes only two eight-byte function
entry trampolines, at `0x1101F0C` and `0x1101F7C`. All other ROM bytes are checked
identical, including graphics and save/load code. This reservation is now owned
by job visibility; future builds must not overwrite it.

Use explicit Thumb `BX` helper stubs for distant ARM7TDMI calls. Untyped linker
symbols produced ARM `LDR pc` veneers that passed a newer-CPU Unicorn model but
entered undefined-instruction mode on the actual mGBA GBA core. The failed ROM
`deca77aed2bdd0c633566300b128f9b3f7ba11a0`, compile failures and navigation/state
captures remain preserved. Do not relax the real-core test or ship that candidate.

All three steps pass in
[run 20260921T052326.612995Z](../build/expansion/test-runs/20260921T052326.612995Z/report.json).
Its generic top-level engine hash is unrelated; each step authenticates the
actual `267fd273` candidate. The candidate and logs reside under
`build/expansion/job-visibility/20260921T052327.318985Z/`.

- 520 native ARM checks cover all ten jobs/five races, hidden jobs, prerequisite-
  free Chemists, clan eligibility/current-job/earned-AP discovery, equipment-only
  and inactive/wrong-race exclusions, last roster slot, personal eligibility,
  sticky discovery after removal, Human paging and protected identities.
- 17 real-core checks cover an older save's cold Continue, actual hidden wheel,
  qualified two-page wheel, native save and fresh-emulator Continue, remembered
  grey jobs after synthetic mastery is removed, reopening and source-save isolation.
- The primary agent inspected the hidden, eligible and cold-load grey wheel
  screenshots. The package authenticates every component report, preserves
  protected player files by hash and reuses the exact save basename/directory.

This is a localized menu/discovery change. No battle, campaign or graphics
pipeline changes justify replaying their broad suites; their prior evidence is
retained. The disposable fixed-input save test proves compatibility of this
change, not every possible historic save or emulator save state.
