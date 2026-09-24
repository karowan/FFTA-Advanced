# Current handoff

FFTA Advanced is [public on GitHub](https://github.com/karowan/FFTA-Advanced),
with [v0.7.0](https://github.com/karowan/FFTA-Advanced/releases/tag/v0.7.0)
published on September 21, 2026 and v0.7.1 prepared on September 24, 2026. Original project contributions use MIT, and
our isolated generated [artwork](artwork/README.md) is included.

The main project folder now tracks the public `origin/main`. The old nested
publication checkout is retired; original private history and working files are
archived locally. See [workspace repair](notes/workspace-repair-2026-09-23.md).
The [whole-game balance proposal](notes/whole-game-balance-council-2026-09-21.md)
is retained as an unimplemented proposal, not a change to the release.

Current release recipe: **0.7.1-equipment-revision** (public v0.7.1), in
[scripts/mod-release.json](scripts/mod-release.json). Its accepted game SHA-1 is
`631497ccf8ffedaf3d88e4343124305fb08402e8`. It adds the
[equipment-help row fix](notes/teaching-rows-fix-2026-09-23.md) and
[compact skill names and Weapon Attack revision](notes/equipment-revision-2026-09-24.md)
as bounded patches on the v0.7.0 game `267fd273`.

Use [MOD-RELEASE.md](MOD-RELEASE.md) for build and packaging procedures and
**Play Mod.cmd** for the selected local release. The launcher authenticates the
BPS archive, reconstructs the game and retains the save basename and directory.
The older **Play Expansion.cmd** remains a separate engineering release.

## Accepted scope

The mod includes the v0.7 jobs, abilities and equipment, followed by native-palette
art integration, the job-discovery menu fix and the v0.7.1 equipment fixes. The accepted first-pass artwork
includes all 675 class poses, ten portraits and ten badges. The later menu fix
preserves the accepted art parent outside its bounded patch.

- [Approved art integration](notes/approved-first-pass-integration-2026-09-20.md)
- [Job-discovery correction](notes/job-visibility-fix-2026-09-20.md)
- [Player features and limitations](MOD-README.md)

A full campaign playthrough and physical GBA testing remain outstanding.
Each test proves only its recorded inputs and behavior. The earlier engineering
acceptance does not establish unlimited scene/actor capacity.

## Public source and release verification

The cleanup separates current guidance from the old checkpoints, makes runtime
selection portable and adds source/privacy checks. The public repository
starts with fresh history; the original development history and private evidence remain
local. See [the cleanup checkpoint](notes/public-source-cleanup-2026-09-21.md).

[Source CI](https://github.com/karowan/FFTA-Advanced/actions/runs/35585989686)
and [release CI](https://github.com/karowan/FFTA-Advanced/actions/runs/35586077518)
passed. The downloaded public ZIP matched the locally verified ZIP byte for byte;
applying its BPS locally reproduced the accepted game SHA-1 above. ZIP SHA-256:
`61e1250fce14e6bfaca95def3a719ec152a65fd6e537f2222c8966f2480a7dd5`.
The [release workflow](release/README.md) verifies and packages an accepted BPS;
it does not compile or execute the game. Original Square Enix assets, game ROMs,
saves, private evidence and local tools are excluded from the repository.

Do not rewrite the local history, delete private evidence, migrate saves or run
broad game tests solely because documentation or release wrappers changed.
The [earlier handoff](notes/history/HANDOFF.md) retains its original bounded
findings. Current art procedure is [documented here](src/art/native-ui-review/README.md).
