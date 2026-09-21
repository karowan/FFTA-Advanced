# Public-source cleanup, September 21, 2026

The requested publication strategy is a fresh public Git history, preserving the
original development repository and private evidence locally. This checkpoint
records preparation only; it does not authorize or claim an upload.

## Changes

- Added a repository README, contributor/setup guide and current documentation map.
- Archived the long handoff, state, checklist, workflow, initial setup and lab
  narratives under notes/history, with links fixed for their new locations.
  Short root guides now distinguish current art/release work from earlier builds.
- Repaired stale design-snapshot links and removed personal paths from narrative
  documentation and executable entry points.
- Centralized Python selection, propagated explicit Python selection into the
  release runner, and replaced an obsolete clipboard dependency with an explicit
  private-reference requirement.
- Added staged credential rejection and local config/credential ignore rules.
- Added source/link/privacy auditing and a reproducible separate-source exporter.
- Made the gameplay rebuild read exact historical source from a checked text
  bundle when old commits are absent. Public export includes the bootstrap and
  three pinned overrides; source hashes and resulting compiled-code expectations
  are retained. Old campaign evidence audits remain local-history workflows.

## Export and privacy

```powershell
. ./scripts/resolve-python.ps1
& (Resolve-FftaPython) scripts/export-public-source.py --output .local/public-source
```

The destination must be absent and under .local/. The exporter does not delete,
initialize Git, commit or publish. Inspect and audit the resulting tree before
creating its fresh history. The original source and Git history stay intact.

Original artwork receipts retain exact local paths and bytes in this repository.
The public copy replaces personal home prefixes and records original/public
hashes in notes/public-provenance.json. Those redacted copies are descriptive
provenance, not substitutes for the original receipt bytes when authenticating
private historical builds. Prompts, source image hashes and rejected attempts
are retained. Public source contains no generated images, ROMs or saves.

## Validation scope

Use the source-cleanup plan for Python/JSON syntax, Markdown source links, asset
and credential guards, runtime selection and original-versus-bundled source
identity including the bootstrap layout adapter. Use the mod-release plan for
affected PowerShell launchers, exact BPS reconstruction and save isolation.
These are source and delivery checks; no changed gameplay requires runtime
battles or a full integration run. Private reports live under build/.

The initial audit inspected 1,662 tracked files and 4,100 reachable historical
blobs. No forbidden asset or recognized credential signature was found. It found
personal paths in 66 current files, plus historical versions, and 35 real broken
source links (the player template's two archive-only links are intentional).
The detector is scoped and does not guarantee that every possible secret is absent.

The source-cleanup run `20260921T092909.335421Z` passed all three declared steps:
five source-tool checks, eight staged-content tests and the repository audit.
The packaging run `20260921T092939.489170Z` passed all 32 release checks on game
SHA-1 `267fd273bffe2c26a7ed3507d236af80a29b74a8`, including actual launchers in
ValidateOnly mode and unchanged player ROMs/saves. The generic runner header
still displays its legacy engine ROM; the packaging component report records
the actual current game identity and is the relevant evidence here.

## Remaining public-release decisions

- Choose a source license and review upstream code/asset redistribution terms;
  no license was inferred or added during cleanup.
- Provide the intended GitHub repository and explicitly authorize publication.
- A fresh checkout still needs private artwork, authenticated parent artifacts,
  tools and retained fixtures. Full current-art clean-checkout reproducibility
  is not established by this source cleanup. The earlier engineering rebuild
  and its exact source bundle are documented separately.

Historical probes were not deleted merely for lacking a literal filename
reference: dynamic imports, test plans and pinned build inputs also consume them.
Accepted game/art bytes and player save locations are unchanged.
