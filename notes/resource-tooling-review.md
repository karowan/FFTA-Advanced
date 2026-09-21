# Resource-tooling review — September 17, 2026

The user approved the existing admission, process containment, emulator cleanup
and automatic retention changes for use. They are tooling changes; no shipping
game code or candidate bytes changed. The unrelated incident note was not read.

Root reviewed the complete guard/pruner, runner/rebuild diffs and emulator close
path. The review corrected the rebuild's premature argument parse, exposed
`-KeepWorkspace` in its PowerShell entrypoint, and corrected the rebuild guide's
obsolete claim that failed workspaces are always retained. Logs/reports remain;
large copied workspaces are removed unless explicitly kept.

Windows children now start suspended, join the memory-limited Job Object, then
resume. This closes the original spawn-before-assignment race. Job setup errors
close handles and kill/wait any created child. Limits reject zero, negative and
non-finite settings. Before deletion the pruner resolves its target, restricts
it to the private probe/reproducibility trees, and rejects symlinks/junctions in
the path. Reports/logs are never selected as captures. Rebuild cleanup also
checks its resolved target and rejects a linked workspace.

`test-resource-tooling`, selected alone through the common runner in
`20260917T124457.556144Z`, passes18 bounded checks in0.4seconds: actual contained
exit/accounting, setup-failure/no-start, descendant termination on timeout,
memory ceiling, invalid limits, dry-run preservation, path/root/junction
rejection, capture-only deletion and argument parsing. The junction negative
uses a mocked junction predicate; no system link or player file is created.
Private fixture/report: `build/resource-tooling/`. No emulator runs.

Earlier run `20260917T124414.992885Z` remains failed: Python's private temporary
directory ACL denied the restricted child access. Normal inherited workspace
ACLs fixed this test setup. The failed directory is left untouched; no broad
permission changes were made. Complete logs remain in both runner directories.

The existing many successful campaign/cold tests supply emulator-teardown
consumer evidence. Assembly-only prerequisite reuse excludes precisely these
resource/teardown drivers: they neither compile game source nor define ROM
bytes. Executor/fixture reuse keeps its separate exact source identity checks.
Current clean-source equality is reused; a new gameplay run is unwarranted.
