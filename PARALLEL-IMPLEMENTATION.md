# Implementation workflow

The primary maintainer handles implementation, integration, testing and final
review. Do not start additional agents without a new explicit request. Historical
worktree assignments and long experiment records are in the
[procedure archive](notes/history/PARALLEL-IMPLEMENTATION.md).

## Current release path

[MOD-RELEASE.md](MOD-RELEASE.md) defines the build/share/play workflow. Build with
the configured acceptance recipe, output an immutable BPS ZIP, then atomically
promote the local channel. The launcher reconstructs that exact archive using an
authenticated clean ROM and preserves save storage. Never choose a ROM by newest
file time or hardcode a new target hash in the launcher.

Maintain the player overview in [MOD-README.md](MOD-README.md). Keep features,
progression, installation, saves and actual limitations there; put recent changes
in release notes. Keep test receipts and private paths outside the share ZIP.
Changing documentation does not invalidate byte-identical gameplay evidence.

## Implementation and tests

Make substantial coherent changes before testing. Use compilation/static checks
and affected runtime tests, including direct consumers and concrete cross-class
interactions. Before runtime execution, record the changed behavior, test IDs and
why they are needed. Use Test Expansion.ps1 with -Only and required prerequisites.

Reserve full integration for a substantial completed milestone, final assembled
acceptance, or a documented widespread regression. A changed hash or shared file
alone is insufficient. Long battle, cold-save and campaign checks are needed only
when their behavior/lifetime changes or at those major gates. Fix related failures
together and rerun affected checks; broaden only when evidence warrants it.

Preserve every run's ROM hash, fixed inputs, complete logs and pass/fail report.
Reuse valid evidence. No separate testing agents, interactive model-driven game
inputs or one-off fixtures. Passing a partial suite never establishes completion.
The primary maintainer performs the final review. [Test guide](TESTING.md).

Compile bounded menu patches against authenticated parents and verify linked
helper bodies. ARM7TDMI distant calls need explicit Thumb BX interworking stubs;
a newer-CPU simulator alone can miss invalid linker veneers. Preserve unrelated
ROM bytes and verify affected real-core menu/save paths. See the
[job-visibility checkpoint](notes/job-visibility-fix-2026-09-20.md).

## Native artwork

Start with the [working art pipeline](src/art/native-ui-review/README.md).
Use the game's existing class/side palettes, bright contrast and readable native
faces. No custom palette bank or runtime ownership/remapping system. Generate
new class designs from blank designs, with original sprites as references.
Review native-size color conversion before extending animation frames.

Preserve prompts, model/settings, references, raw images and failed attempts.
Generate portraits and badges for their intended dimensions, preserving shared
face anchors and clear identity. Code performs technical conversion/import, not
manual replacement art. Technical checks and maintainer review do not replace
user visual approval. Keep drafts distinct from accepted production pixels.

Authenticate approval receipts and parent ROMs before import. Preserve native
animation commands, timing, frame counts, OAM and unused slots. Check each actual
consumer separately: actors, portraits, miniatures, badges, weapons and effects.
A later build stage can overwrite earlier artwork, so inspect the assembled ROM.
The [approved import checkpoint](notes/approved-first-pass-integration-2026-09-20.md)
records the accepted first pass and source receipt.

Keep complete animation catalogs and immutable per-ROM provenance. Export/verify
catalog shards with scripts/snapshot-reviewed-art-catalog.py. Worksheets containing
original game references remain private. Standalone custom artwork is public
under artwork/, with exact hashes and role/dimension checks.
Never rewrite historical source receipts to make a
new conversion appear previously accepted.

## Source hygiene and public export

Use scripts/resolve-python.ps1 for PowerShell interpreter selection. Entry points
accept -Python and FFTA_PYTHON; do not add personal absolute paths. Keep reusable
procedures here and focused progress/evidence notes under notes/, not AGENTS.md.

Run scripts/audit-public-source.py for format, link, asset and credential checks.
Use --history when reviewing existing Git history. The staged asset guard is
scripts/check-git-content.py; run it before every commit. No ROMs, saves, dumps,
local tools or generated builds enter Git. Never force-add an ignored file.

Use the main project folder as the single active checkout, tracking
`origin/main` at `https://github.com/karowan/FFTA-Advanced`. The original private
history and its working files are archived under ignored `.local/`; never add
that archive as a public remote or merge its history into this repository.
Temporary exports are snapshots, not development checkouts. Retain required
historical build source as authenticated text inputs. Personal paths in public
documents are redacted and explicitly labeled; executable source with personal
paths must be fixed manually, never automatically rewritten by the exporter.
Original authenticated receipts stay in the local archive. A fresh source
checkout still needs original-game references, accepted parent ROMs and private
build inputs for the current art rebuild.
[Cleanup checkpoint](notes/public-source-cleanup-2026-09-21.md).

## Launching and saves

Launch only when requested, as a visible standalone Windows application. Prefer
an existing correct window to duplicate processes. A process ID does not prove
visibility. Use the approved interactive desktop path if sandbox launching is
not visible, following AGENTS.md. Never discard running progress.

Preserve separate vanilla, development, legacy engineering and current-art save
paths. Use launcher -ValidateOnly checks without opening a game. Across updates,
use an in-game save and cold Continue, not an emulator state. Packaging never
imports player saves or closes running games.

## GitHub publication

The user authorized publication to karowan/FFTA-Advanced with MIT licensing and
our generated artwork. Original Square Enix assets remain excluded. Run the
source/privacy, staged-asset, bootstrap, artwork and packaging checks before
pushing. Follow [release/README.md](release/README.md) to generate and publish a
ZIP through GitHub Actions from a checksum-pinned accepted BPS. The workflow
packages an accepted patch; it does not compile the game or receive a ROM.
