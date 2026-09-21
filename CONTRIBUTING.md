# Development and contributions

Read [the current workflow](PARALLEL-IMPLEMENTATION.md) and [AGENTS.md](AGENTS.md)
before changing the project. Artist contributions are welcome; discuss the
intended consumer and native constraints before producing a full animation set.
The automated authoring workflow uses image generation; technical conversion
and integration are separate steps.

## Local setup

The development tools currently target Windows and PowerShell. Install Git,
Node.js and Python 3.11 or later. Entry points accept `-Python` or `FFTA_PYTHON`,
then try Python on PATH. An optional local Codex runtime fallback preserves the
original workstation setup; it is not a required dependency.

```powershell
$env:FFTA_PYTHON = 'D:/Python/python.exe' # Use your installed executable.
git config core.hooksPath .githooks
& '.\Test Expansion.ps1' -Plan scripts/mod-release-test-plan.json -List
```

Python artwork and native-test tools also require Pillow, NumPy, Unicorn and
Capstone, plus the project's local mGBA test core. Tool versions and exact tree
hashes used for the clean rebuild are in
[the toolchain record](notes/reproducible-toolchain.json).
The locally installed ARM compiler, event assembler, upstream engine inputs,
character lookup, emulator and patcher live under ignored `tools/`.
They are not installed automatically or bundled with this source.

Supply your own clean USA ROM as `roms/clean/FFTA_US_clean.gba`;
SHA-1 must be `4ac05441f4de70a4ec3dd932116346c61b8783d9`.
Original reference worksheets, private fixtures and accepted parent artifacts are
additional inputs. Missing inputs must remain explicit failures, not bypassed
hash or acceptance checks. See [rebuild limits](REPRODUCIBLE-BUILD.md).

## Source layout

| Path | Purpose |
|---|---|
| `src/engine/` | ARM7TDMI code and native hooks |
| `src/art/` | Art specifications, prompts and provenance |
| `artwork/` | Generated artwork under MIT; original game references excluded |
| `scripts/` | Builders, converters, deterministic tests and local launchers |
| `scripts/*test-plan.json` | Test IDs, dependencies and suites |
| `notes/` | Design contracts and bounded implementation evidence |
| `notes/history/` | Archived checkpoint narratives and earlier procedures |
| `build/`, `roms/`, `saves/`, `tools/`, `.local/` | Ignored local inputs and outputs |

Many apparently unused probes are imported dynamically, named in test plans or
used by pinned historical builds. Before deleting a script, trace these paths.
Source history is a build dependency in the private development repository;
the public export carries the required bootstrap source separately.

## Checks and reports

Run tests through [Test Expansion.ps1](Test%20Expansion.ps1), selecting affected
IDs and prerequisites. See [TESTING.md](TESTING.md). Documentation-only changes
need link, format and Git-content checks, not game playback.

```powershell
. ./scripts/resolve-python.ps1
& (Resolve-FftaPython) scripts/audit-public-source.py
& (Resolve-FftaPython) scripts/check-git-content.py
git diff --check
```

The audit scans tracked files and nonignored new files, checks Python/JSON syntax,
local Markdown links, forbidden assets and specific credential signatures.
`--history` adds reachable Git blobs. `--require-private-paths-clean` rejects
personal paths as well. It never prints matched credential values. These checks
are useful gates, not a comprehensive security or legal review. Reports remain
under ignored `build/`.

In a fresh public checkout, the source-tool tests can also run directly with
`python scripts/test-source-cleanup.py` and `python scripts/test-git-content.py`.
The general game-test runner still requires its local engine/ROM baseline even
for a static plan; listing a plan and the direct source checks do not.

Before committing, stage only source and documentation and run the Git-content
guard against the index. Never force-add private assets. Preserve failed test
reports and saves. Do not publish or upload from an automated cleanup run.

Bug reports should include the release/emulator version and reproduction steps.
Do not attach a ROM, credentials or a private dump. Save files can be shared
separately when needed to reproduce a specific issue.
