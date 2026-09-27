# Implementation workflow

The primary maintainer handles implementation, integration, testing and final
review. Do not start additional agents without a new explicit request. Historical
worktree assignments and long experiment records are in the
[procedure archive](notes/history/PARALLEL-IMPLEMENTATION.md).

For AI performance comparisons, use the [paired timing procedure and findings](notes/ai-timing-investigation-2026-09-27.md).
Build fresh native allocations separately for vanilla and the candidate; never
transfer a savestate across ROMs. Match canonical combat inputs, action lists
and RNG at the planning boundary. Measure emulated planning frames separately
from camera preparation and attack animations; host wall time is not game latency.

Forecast optimizations must keep action snapshots frozen and temporary-unit
ownership authenticated. Request only the flags a damage formula consumes;
check equipped reaction/support eligibility before expensive readiness or
terrain queries. Never make a narrow query fall back to live values during an
active snapshot. Validate projected flags against the full query and modified
formulas against the previous binary, including active buffs, reactions and
freed/reused copies (`ai-forecast-fast`). Run timing separately for starting and
fully learned jobs; preserve baseline reports and inspect every paired choice.
Finish with `ai-timing-budget` against both completed profiles. It pins the
workload and allows at most 5% above each reviewed decision; investigate a
failure instead of automatically raising its budget. This guards the measured
improvement, not vanilla parity or unmeasured campaign cases.

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

When replacing coordinated engine modules, resolve installed weak extension
callbacks explicitly as well as strong imports. A successful link can silently
turn an omitted weak callback into zero, disabling snapshots, reactions or
lifecycle events. Check those paths through native execution. If an existing
captured battle predates an allocation change, use native allocation and owner
registration for the new capacity; never alter heap headers to make it pass.

When a shared record layout changes, retain every authenticated historical
entry address from the original engine and component symbol/import maps. Patch
all retained callers, including older import veneers; replacing only the newest
symbol value leaves old machine code reading the wrong stride. Recompile direct
stride consumers as well as accessors. Preserve installed fast dispatch paths
inside replacements and test them explicitly. Check all canonical unit slots,
ordinary movement without effects, and genuine buffs through the native status
query. Keep short native-input movement checks so slower replacements cannot
silently consume button presses during long calculations.

Do not merge component-local `original` aliases by name and assume they retain
their meaning. A wrapper's predecessor belongs to that component's authenticated
parent; a later symbol dictionary can turn a lifecycle chain into recursion.
Verify the ordered chain and one invocation of each lifecycle stage. When a
unit-copy tail grows, check the following list/array start as well as allocation
sizes. Physician/Sapper's 66-byte tail ends at +7282, so the full party item list
starts at +7290. The accepted native-palette build uses full battle Status;
the retired compact-palette constructor is not its runtime contract.

For a new assembled candidate, declare `candidateManifest` in the test plan.
The runner authenticates that manifest and ROM and passes the resolved path to
each test. Per-test reports must repeat the same hash; separately compiled codec
tests must explicitly identify their narrower scope. Run the complete new-job
acceptance gate once at integration, then package through its adapter. See the
[Physician/Sapper checkpoint](notes/chemist-progression-implementation.md) for
the exact build order and covered consumers.

## Native artwork

For a new class, start with the [executable new-job art runbook](NEW-JOB-ART-RUNBOOK.md).
It specifies the actual reference worksheets, crops, commands, approval gates
and recovery steps, with Physician/Sapper as the worked example. The
September 27 animation review requires its Gate 4 fixed-coordinate native
anchor audit before further pose generation; the old fitted action worksheet
is historical-replay-only. Palette and hash checks do not prove anatomy. The
fixed-origin revision workflow in that runbook uses matched neutral/action
reference pairs, one approved identity view, explicit pose notes and preserved
retries. Inspect turns, falls, airborne shadows and waterlines separately.
Whole-drawing registration corrections must be source-bound rigid translations;
never stretch a generated body to meet a bounding box. The
[working art pipeline](src/art/native-ui-review/README.md) retains the accepted
ten-class import history; its job-specific scripts are not generic new-job tools.
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
For new equipment icon drafts, use the [item-art checkpoint](notes/item-art-drafts-2026-09-25.md)
and its authenticated original icon references. Supply the native palette guide
to image generation, limit each prompt to colors in that palette, enforce those
prompt-listed colors during conversion, and review the indexed 16×16 result
before replacing shared donor icons.
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
