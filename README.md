# FFTA Expansion

A Final Fantasy Tactics Advance (USA) mod with eight new jobs across ten
race/job options, 129 added ability entries, 85 teaching weapons, native-palette
spritework, and quality-of-life improvements.

This repository contains source, build tools, specifications and development
records. Game ROMs, player saves, emulators, generated images and build outputs
are not included. The new character spritework is AI-generated; artist
contributions to improve or replace it are welcome.

## Playing

The player distribution is a ZIP containing a BPS patch, README, changelog and
checksum manifest. Apply the patch to your own clean USA ROM. See the
[player guide template](MOD-README.md) for jobs, progression, installation and
save guidance. Its `{{...}}` fields are filled when a release is packaged.
No public download URL has been established in this source tree.

For an already provisioned developer checkout, **Play Mod.cmd** opens the exact
release selected by `build/releases/current.json`. **Play New Sprites.cmd** is
an alias. The other launchers retain older builds with separate save locations;
they do not select the current release.

## Working on the mod

- [Setup and contributions](CONTRIBUTING.md): dependencies, source layout and checks.
- [Build, package and play](MOD-RELEASE.md): the current release workflow.
- [Implementation workflow](PARALLEL-IMPLEMENTATION.md): change and acceptance rules.
- [Testing](TESTING.md): choose deterministic checks by affected behavior.
- [Current handoff](HANDOFF.md): accepted scope and remaining limits.
- [Art pipeline](src/art/native-ui-review/README.md): native sizes, palettes and imports.
- [Class specification](JOB-CLASS-SPECIFICATION.md) and [equipment progression](WEAPON-ACQUISITION.md).
- [Historical records](notes/history/README.md): earlier builds, experiments and evidence.

The latest release recipe requires an authenticated local art parent and
retained build inputs. A fresh source checkout alone cannot reproduce that
release. [Build prerequisites and limits](REPRODUCIBLE-BUILD.md) distinguish the
earlier clean engineering rebuild from current release packaging.

## Current limits

Testing uses mGBA. A full campaign playthrough and physical GBA testing remain
outstanding. A Geomancer field outline can temporarily disappear during
memory-heavy animations while its effect stays active.

The source has no project-wide license yet. Publication and licensing decisions
must be made before a public release; the presence of source does not establish
permission to redistribute third-party code or game assets.
