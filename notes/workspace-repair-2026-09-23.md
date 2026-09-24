# Consolidate the working repository

The first public release used a fresh Git history in a nested export. The saved
project still opened the original private checkout, leaving 49 modified and
19 untracked files visible there. Publication succeeded, but the working-folder
transition was incomplete.

The repair makes the existing main project folder the active public checkout,
tracking `origin/main` at karowan/FFTA-Advanced. It preserves the original Git
directory, refs, index, source working files and local-only notes in an ignored
archive under `.local/workspace-repair-2026-09-23/`. The old export is retired.
Private ROMs, local tools, release artifacts and saves retain their existing
paths. The private archive must never be pushed or merged into public history.

The local-only balance council is retained as an explicitly unimplemented
proposal. The private publication note and original unredacted receipts remain
in the archive. Existing public code, generated artwork, licensing and CI are
retained. This repair does not change gameplay or the v0.7.0 release assets.

## Privacy-check repair

The old exporter redacted a regex literal inside its own privacy checker,
disabling POSIX home-directory detection while leaving valid Python syntax.
The corrected pattern detects Windows, macOS and Linux paths without matching
its own source. Automatic redaction now applies only to documents and JSON;
executable source and authenticated bootstrap inputs require manual correction.
Regression checks cover all three platforms, unchanged exported checker behavior,
and rejection of automatic executable-source rewriting.

## Verification scope

Use source/history privacy and document-link checks, the staged Git asset guard,
source-cleanup regression tests, and launcher `-ValidateOnly` verification.
Local migration receipts record original file hashes, old/new Git identities,
and unchanged save/release identities under the ignored archive. Gameplay bytes
are unchanged; this repository repair does not require battle or campaign tests.
