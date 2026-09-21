# Current handoff

Current release recipe: **0.7-art1-job-visibility**, in
[scripts/mod-release.json](scripts/mod-release.json). Its accepted game SHA-1 is
`267fd273bffe2c26a7ed3507d236af80a29b74a8`.

Use [MOD-RELEASE.md](MOD-RELEASE.md) for build and packaging procedures and
**Play Mod.cmd** for the selected local release. The launcher authenticates the
BPS archive, reconstructs the game and retains the save basename and directory.
The older **Play Expansion.cmd** remains a separate engineering release.

## Accepted scope

The mod includes the v0.7 jobs, abilities and equipment, followed by native-palette
art integration and the job-discovery menu fix. The accepted first-pass artwork
includes all 675 class poses, ten portraits and ten badges. The later menu fix
preserves the accepted art parent outside its bounded patch.

- [Approved art integration](notes/approved-first-pass-integration-2026-09-20.md)
- [Job-discovery correction](notes/job-visibility-fix-2026-09-20.md)
- [Player features and limitations](MOD-README.md)

A full campaign playthrough and physical GBA testing remain outstanding.
Each test proves only its recorded inputs and behavior. The earlier engineering
acceptance does not establish unlimited scene/actor capacity.

## Public-source preparation

The cleanup separates current guidance from the old checkpoints, makes runtime
selection portable and adds source/privacy checks. The intended public repository
starts with fresh history; the development history and private evidence remain
local. See [the cleanup checkpoint](notes/public-source-cleanup-2026-09-21.md).
Nothing has been published. Licensing and redistribution review remain necessary.

Do not rewrite the local history, delete private evidence, migrate saves or run
broad game tests solely because documentation or release wrappers changed.
The [earlier handoff](notes/history/HANDOFF.md) retains its original bounded
findings. Current art procedure is [documented here](src/art/native-ui-review/README.md).
