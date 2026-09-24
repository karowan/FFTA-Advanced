> For public GitHub releases, use [release/README.md](release/README.md). The local build/acceptance procedure below remains the source of the verified BPS input.

# Build, share and play the mod

The release artifact is a ZIP containing **FFTA_Expansion.bps**, **README.md**,
**CHANGELOG.md**, and **manifest.json**. Share this ZIP. It does not contain a
ROM, save, emulator, private file paths, raw logs or development tools. Players
apply the BPS patch to their own clean Final Fantasy Tactics Advance USA ROM
using [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) or another
BPS-compatible patcher. No earlier mod installation is needed.

BPS is supported by [Rom Patcher JS](https://github.com/marcrobledo/RomPatcher.js)
and [Floating IPS](https://github.com/Sir-Walrus/Flips). The required original
and patched result checksums are included so a wrong region/revision or already
modified ROM can be rejected. The public release is available from
[GitHub Releases](https://github.com/karowan/FFTA-Advanced/releases/latest).
Local packaging updates only the local channel; public publication uses the
[release workflow](release/README.md).

## Build output

Run [Build Mod Release.ps1](Build%20Mod%20Release.ps1). It reads the build recipe
in [scripts/mod-release.json](scripts/mod-release.json), builds the current
candidate through its declared deterministic plan, runs that candidate's required
checks, and packages the accepted result. A failed check stops packaging. Current
recipe: new AI-generated spritework plus the job-discovery fix, compiled onto
the authenticated approved-art parent. This entry point does not claim a new
from-scratch rebuild of every historical gameplay/art stage.

To package already accepted, unchanged game code without rerunning gameplay:

```powershell
& '.\Build Mod Release.ps1' -Run build/expansion/test-runs/20260921T052326.612995Z/report.json
```

The candidate comes from that exact run's build log, not a mutable candidate
pointer. The job-visibility adapter verifies the complete required step set,
candidate/report ROM hashes and current wheel source hash before calling the
general packager. Future build pipelines should supply their corresponding
acceptance adapter and recipe; never remove acceptance to make packaging pass.

The output path is printed and saved in `build/releases/current.json`. Each ZIP
is immutable under `build/releases/artifacts/<ZIP-SHA256>/`. The ZIP's identity
covers its BPS patch, documentation, portable checksums and accepted-run digest.
ZIP entry order, timestamps and permissions are fixed. The build verifies two
identical BPS creations, exact clean-ROM roundtrip, wrong-source rejection and
deterministic ZIP output before promoting the channel. Local acceptance receipts
stay beside the ZIP and are not distributed.

Change the recipe's release name/version/notes as needed. The expected target ROM
hash is calculated from the accepted candidate and written into the artifact;
it is not maintained in a launcher. The clean original hash remains an explicit
input requirement. A changed release must not reuse an old gameplay acceptance
report unless its tested game bytes and source predicates remain applicable.

The share README is rendered from [MOD-README.md](MOD-README.md), the maintained
overview of the entire mod, rather than the recipe's latest-change notes. Only
its name, version and source/target identity fields are filled during packaging.
Keep the README self-contained, and link only files actually included in the
ZIP. Release-specific notes remain in CHANGELOG.md.

## Play the same artifact we share

[Play Mod.cmd](Play%20Mod.cmd) is the current launcher. [Play New Sprites.cmd](Play%20New%20Sprites.cmd)
remains a compatibility shortcut to the same launch path. The launcher:

1. Reads the stable `build/releases/current.json` channel.
2. Authenticates the selected ZIP and its contained manifest, BPS and documents.
3. Validates the local clean ROM against the artifact's input checksums.
4. Applies the ZIP's patch into a local cache keyed by the target SHA-256.
5. Checks the resulting bytes against the artifact's target checksums.
6. Starts mGBA with that cached ROM and the channel's explicit save paths.

A valid cache is reused. A damaged cache is rejected without silently overwriting
it. Remove that cache file deliberately to regenerate it from the validated
patch. The launcher never selects the newest `.gba` by directory order and never
opens the build candidate directly. It contains no specific ROM version, target
path or target checksum. Changing the build's verified channel changes what plays.

The local channel holds clean-ROM, emulator and save locations. Those settings
are separate from the portable sharing artifact. Saves retain the existing
`saves/native-art-final-2026-09-20/FFTA_Reviewed_All_Classes.sav` path and basename.
Prior releases and the separate vanilla/development/legacy expansion launchers
remain intact. No running game is closed or hot-reloaded by packaging.

Use an in-game save, restart and choose Continue across updates. Emulator save
states capture old transient state and are not a compatibility guarantee.

## Verification checkpoint

Current release: `0.7.1-equipment-revision.zip`, game SHA-1
`631497ccf8ffedaf3d88e4343124305fb08402e8`, packaged from
[run 20260924T055206.504473Z](build/expansion/test-runs/20260924T055206.504473Z/report.json)
through [its adapter](scripts/package-equipment-revision.py); ZIP SHA-256
`7baf6da23bfc2615889e06226863b06c0889cdc4765e010a34d7a2bc0720dc9a`, 2,881,948 bytes;
BPS 5,945,233 bytes. The packaging code and launcher are unchanged. The
remainder of this section records the preceding v0.7.0 checkpoint.

Previous game SHA-1: `267fd273bffe2c26a7ed3507d236af80a29b74a8`, unchanged by that
packaging work. It retains the new AI-generated spritework and discovery fix.
Share ZIP: `0.7-art1-job-visibility.zip`, 2,880,796 bytes; BPS: 5,944,501 bytes.
ZIP SHA-256: `b2b850d845b7aff4b77a57ee7d82de8f9027035aee3b5f3ba03bcf7ef919115a`.
The September21 documentation revisions describe the complete mod while
removing explanations of unchanged base-game mechanics, including job discovery,
and trimming repeated rules and generic caveats. The visibility fix is a short
changelog entry. Packaging verification boilerplate stays out of that file;
the manifest and local receipts still retain the evidence. Installation, update
guidance and mod-specific limits remain. The README and changelog disclose
AI-generated spritework and welcome artist contributions to improve or replace
it, without approval or first-pass labels. The BPS and game bytes match both the
preceding full-overview `be6008e2` ZIP and the original release-artifact
`8c67124a` ZIP. Archive document/hash/link checks and the actual launcher
ValidateOnly path pass again; gameplay evidence is retained unchanged.

[Declared packaging plan](scripts/mod-release-test-plan.json) passes all32 checks
in [run20260921T053945.779574Z](build/expansion/test-runs/20260921T053945.779574Z/report.json).
It covers fresh patch-to-play installation, exact reconstruction, cache reuse,
a second synthetic release selected without launcher edits, wrong clean ROM,
missing/corrupt archive, corrupt patch/cache/documents, unsafe paths, unexpected
ROM content in the ZIP, target-hash failure, both actual PowerShell launchers in
ValidateOnly mode and unchanged player saves/ROMs. The synthetic artifact remains
test-only and is never selected by the real channel or launched.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/mod-release-test-plan.json -Only test-mod-release
& scripts/launch-mod-release.ps1 -ValidateOnly
```

The earlier job-specific raw-ROM package remains historical. Current packaging
and launch procedures above supersede the packaging section of the
[job-visibility checkpoint](notes/job-visibility-fix-2026-09-20.md). Its gameplay
evidence remains valid because the patched output is byte-identical. No new
battle/campaign run is warranted by the delivery-only change.

Local requirements are the existing Python, Node.js, mGBA and RomPatcher.js
installations. They are not bundled into the ZIP; recipients only need their
own original ROM, a BPS patcher and a GBA emulator. Source files are committed;
generated patches, ROMs, ZIPs and test evidence remain ignored.
