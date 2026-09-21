# v0.7 delivery — September 17, 2026

The release is local and separately playable through `Play Expansion.cmd`.
No game was launched and no remote publication occurred. The old vanilla and
development launchers and their game/save hashes remain unchanged.

| Artifact | Identity |
|---|---|
| ROM | `roms/play/expansion-v0.7/FFTA_Expansion_v0.7.gba`,33,554,432bytes |
| ROM SHA1 | `1b070824a8dad4995434eee3ab40fa08187a6120` |
| ROM SHA256 | `1032590068ae10188705e3cd920e1f1dae48d07a74b150b65a4bd1286a39fddb` |
| Patch | `build/releases/v0.7/FFTA_Expansion_v0.7.bps`,4,713,283bytes |
| Patch SHA256 | `5c93ca6f7c99c94bae6b617ee8c193d4c01e51f3073ee0015bcada2cf2e1ca95` |
| Manifest | `build/releases/v0.7/manifest.json` |
| Guide | `EXPANSION-PLAYER-GUIDE.md`, also copied into the release folder |
| Saves/states/screenshots | `saves/expansion-v0.7/`, using the expansion ROM basename |

R02 run `20260917T124951.415017Z` passes read-only assembly reuse and final
evidence reconciliation:218 unchanged shipping source/build files,52 evidence
notes and28 exact reports/logs. The certificate is
`build/release-acceptance.json`, copied into the release as `acceptance.json`.
Root review and retained coverage limits are in `release-acceptance.md`.
The clean-source reconstruction remains the accepted094234 run; it was not
repeated simply because release documentation or tooling changed.

R03 run `20260917T125641.116392Z` passes both declared delivery steps:

- `package-expansion`: clean-source BPS roundtrip equals all target bytes,
  changed base rejected, second independent generation equals the first patch,
  accepted source/report hashes checked, existing player files unchanged.
- `test-expansion-launcher`: actual Windows PowerShell validation mode checks
  the delivered ROM, manifest and explicit three output-path overrides. A wrong
  ROM in an isolated space-containing fixture is rejected. Nine game/save/
  launcher files are hashed before/after with equality. No emulator is started.

The launcher uses mGBA0.10.5's command-line configuration override interface.
The upstream [argument parser](https://github.com/mgba-emu/mgba/blob/0.10.5/src/feature/commandline.c)
applies `-C` overrides, and [core configuration](https://github.com/mgba-emu/mgba/blob/0.10.5/src/core/config.c)
reads `savegamePath`, `savestatePath` and `screenshotPath`. The
[Qt startup path](https://github.com/mgba-emu/mgba/blob/0.10.5/src/platform/qt/Window.cpp)
loads the explicitly supplied ROM. These source checks support path behavior;
no interactive-window visibility or new player save is claimed by validation.

## Retained failed delivery attempts

`125354.669605Z`: patch construction/checks completed, then sandboxed Node
could not spawn Git for metadata (`EPERM`); no manifest was produced and the
independent launcher consumer failed on that missing file. The packager now
uses the authenticated source checkpoint from the acceptance certificate.

`125434.811328Z`: packaging passed; launcher child returned an error hidden by
the original test wrapper. `125519.527789Z` retains the exposed error: Windows
PowerShell could not resolve `Get-FileHash` in this inherited environment.
The launcher now hashes through .NET and the wrapper preserves child errors.
No execution-policy restriction was established. The final run above passes.
These earlier reports remain failed; successful packaging phases are explicitly
separate from their failed launcher consumers.

## Reproduction

Build using `REPRODUCIBLE-BUILD.md`. In the retained acceptance workspace, run
`audit-release-evidence` and `verify-integrated-assembly-prerequisites` through
the common integration plan only when freezing/changing evidence or source.
Then select `package-expansion,test-expansion-launcher`. If only launcher
verification needs continuation, select `test-expansion-launcher` alone; it
authenticates the existing package first. No gameplay fixture is required.

The evidence audit deliberately requires the retained reports and source
history; it cannot certify a fresh checkout with no test evidence. The clean
build procedure itself does not require these reports. Package/ROM bytes are
immutable: a different existing delivery is rejected, never overwritten. The
manifest records the accepted shipping-source checkpoint and exact packaging
source hashes. Recreating the same patch on the same image is deterministic;
metadata may differ with a new audited checkpoint.

Save migration and compatibility with another overhaul remain outside scope.
See the player guide and final review for representative campaign/hardware
limits. All generated binaries, reports, ROMs and tools remain outside Git.
