# Worktree readiness and Git exclusion

September 14, 2026 (local time). Initial source-only commit: `706596a`.
The Git index contained 475 source/document files and no ROM, save, dump,
downloaded tool or generated build. `.gitignore`, text-only index inspection
and the local pre-commit hook enforce this. No remote was configured or pushed.

Each job worktree was seeded from that commit with 8,721 private local files
(about 2.17 GB), including copied tools, the clean ROM, accepted main binary and
tables, exact native executor captures and a fixed test save. The source tree
is Git-managed; these prerequisites are ignored. Files are copies rather than
shared writable links. Source and relocated local hashes are recorded privately
in each worktree's `.local/worktree-seed.json`.

Eight prerequisite steps passed separately in each checkout:

| Job | Local deterministic run under build/expansion/test-runs |
|---|---|
| Dark Knight | 20260915T035027.353761Z |
| Viking | 20260915T035148.906893Z |
| Chemist | 20260915T035148.929082Z |

Checks cover private asset/isolation hashes, compiler availability, runner
contracts, original complete native execution, a fresh private Samurai build,
executor fixture preparation, Samurai and Blade Ward native execution, and a
fresh headless native battle. Viking and Chemist suites ran concurrently in
different worktrees without shared output or lock conflicts. All reproduce
candidate `b6daf87deb52ad84d72021e7bc6ea359ebd8bce1` over accepted ba1c.

The primary checkout additionally passes Git guard negative tests and runner
self-tests in `20260915T035050.120486Z`: forbidden ROM extension, binary renamed
as text, forbidden private path and staged binary hidden by a clean working
copy are all rejected. These checks are now declared in the main plan.

This is workshop readiness, not completed job implementation. All three jobs
have implementation agents assigned to their own branches. The first shared
integration requirement identified is persistent status capacity: the existing
inventory reserve has only 24 spare bytes. Root owns an expanded saved/copy
state contract; agents can implement native effects independently while that
prerequisite is resolved. No agent may silently reuse unassigned RAM or AP.
Independent job acceptance and combined merge/regression remain ahead.
