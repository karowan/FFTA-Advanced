# FFTA Advanced

[![Source checks](https://github.com/karowan/FFTA-Advanced/actions/workflows/ci.yml/badge.svg)](https://github.com/karowan/FFTA-Advanced/actions/workflows/ci.yml)

A Final Fantasy Tactics Advance (USA) mod with eight new jobs across ten
race/job options, 129 added ability entries, 85 teaching weapons, native-palette
spritework, and quality-of-life improvements.

This repository contains source, build tools, specifications and development
records, plus [our generated artwork](artwork/README.md). Game ROMs, player saves,
emulators, original Square Enix graphics and build outputs are not included.
The new character spritework is AI-generated; artist
contributions to improve or replace it are welcome.

## Playing

The player distribution is a ZIP containing a BPS patch, README, changelog and
checksum manifest. Apply the patch to your own clean USA ROM. See the
[player guide template](MOD-README.md) for jobs, progression, installation and
save guidance. Its `{{...}}` fields are filled when a release is packaged.
**[Download the latest release](https://github.com/karowan/FFTA-Advanced/releases/latest).**

For an already provisioned developer checkout, **Play Mod.cmd** opens the exact
release selected by `build/releases/current.json`. **Play New Sprites.cmd** is
an alias. The other launchers retain older builds with separate save locations;
they do not select the current release.

## Working on the mod

- [Setup and contributions](CONTRIBUTING.md): dependencies, source layout and checks.
- [Build, package and play](MOD-RELEASE.md): the current release workflow.
- [GitHub release CI](release/README.md): verified BPS-to-ZIP packaging.
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

Original project code, documentation and generated artwork use the
[MIT license](LICENSE). Original game assets and third-party dependencies are
outside that grant; see [NOTICE.md](NOTICE.md).
