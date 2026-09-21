# Resource incident: September 15, 2026

This is a historical incident record, revised September 21, 2026. It does not
pause current work or assert the machine's current service/resource state.
At the time, the user reported that the computer was nearly unresponsive and
expansion testing was paused. Temporary test-entrypoint guards used
`.local/testing-paused.json`; those guards were later removed at the user's
request. No emulator stress reproduction was run during the initial investigation.
Current resource-containment procedures are documented in
[PARALLEL-IMPLEMENTATION.md](../PARALLEL-IMPLEMENTATION.md#resource-containment-and-retention).

## Observed evidence and intervention

- The last46-step combined suite finished successfully at04:01 Pacific,
  report `20260915T105543.754802Z`, with `inputsUnchanged=true`, on candidate
  `c1a7b7db270fdcb7da7686bbae38be103cc49ff3`. It is a bounded movement-support
  checkpoint, not full expansion completion. Its source changes were uncommitted
  when this incident was first recorded.
- At the user's report, no Python, mGBA or ARM test/compiler processes remained.
  The user reported improvement after testing ended, but incomplete recovery.
- At04:04, Windows reported112.33GiB committed of145.64GiB commit capacity,
  29.26GiB physical RAM free of61.64GiB, and2,916 pages read per second.
  A later idle-test snapshot still showed112.52GiB committed.
- LGCalibratorScheduler.exe, PID9352, held209,820 handles. A bounded native
  handle audit identified209,645 as Section/shared-memory handles and only
  one as a Process handle. The audit identifies types by matching known
  handles created in its own process, not by assuming static Windows type IDs.
- The owning service was `LG Calibration Studio Service`, executable
  `C:\Program Files (x86)\LG Electronics\LG Calibration Studio\bin\LGCalibratorScheduler.exe`.
  Its Authenticode signature was valid, signed by LG Electronics Inc.
- Ordinary service control lacked administrator rights. A narrowly scoped
  Windows administrator helper verified that exact service/PID/path, stopped
  that service and recorded the result. It did not change startup settings.
- Immediately after the stop at04:09:39, committed memory fell to67.24GiB.
  At04:10:29 it was66.89GiB, with30.70GiB available RAM. System Section objects
  fell from246,959 to36,875. The service remained stopped; no test processes
  were present. This is about45.6GiB less committed memory.

The intervention strongly implicates the LG service's retained shared memory
in the continuing memory pressure. It does not prove which application or
event caused the accumulation. Testing may have contributed to pressure or
triggered retention; no controlled causal reproduction has been performed.
Do not describe all112GiB as emulator memory, or equate committed memory with
resident physical RAM.

AMD's AUEPDU service also had about78,000 handles, mainly another object type;
it was left running because this audit did not establish it as the retained
memory cause. Previously disabled Razer services remained stopped/disabled.
Games, browser sessions, player saves and calibration profiles were untouched.

Private diagnostic evidence: `build/resource-incident/handle-audit.json`,
`lg-service-before.json`, `lg-stop-result.json`, `after-lg-stop.json` and the
exact one-service administrator helper. These remain ignored, outside Git.

## Initial follow-up recommendations (historical)

The LG service retained automatic startup after the intervention, which stopped
it temporarily. A permanent startup change was not authorized. The recommendation
was to confirm responsiveness and stable system memory before resuming tests;
the successful service stop alone did not demonstrate complete recovery.

The emulator harness also had cleanup weaknesses found by source inspection:
`close()` called native unload/deinit but retained its ROM buffer, frame,
memory-map pointers and callbacks. Callback closures referenced the instance,
so cleanup depended on cyclic GC; construction failure and repeated close were
not robustly handled. These observations did not quantify a leak or establish
the source of the retained memory. The recommendation was to fix and verify
cleanup in an isolated, resource-bounded run before another full suite.

The runner then lacked a memory budget and system-pressure stop condition;
timeout cleanup did not guarantee descendant-process cleanup. The recommended
work was process-tree containment, low scheduling priority, peak-memory reporting
and an admission guard, verified first with lightweight synthetic processes and
then a bounded emulator lifecycle check. These are historical recommendations;
the subsequent implementation is recorded below.

## Follow-up: September 17, 2026

The follow-up recorded substantial disk pressure: the system volume held
22 GB free of 3.7 TB with a system-managed page file on it. This could constrain
page-file growth and worsen performance under memory pressure, but it does not
by itself prove that commit could not grow, that the SSD had no free blocks,
or that disk space was the sole sustained cause of the reported thrashing.
`build/` held
151 GB across 301,693 files (113 GB of ROM images, 16 GB of emulator states,
9 GB of RAM dumps), with 28 integrated base trees and no retention at all;
`.worktrees/` held another 33 GB of copied tools and probes for three merged
job branches. A clean rebuild copied the pinned toolchain into a new
workspace on every run and kept it.

Changes: `scripts/resource_guard.py` (admission guard, Job Object
containment, peak-memory reporting, shared workspace lock),
`scripts/prune-build-outputs.py` (retention with dry run), runner and rebuild
integration, and idempotent emulator cleanup. Containment was verified with
lightweight synthetic processes (peak reporting, grandchild termination on
timeout, 1 GB ceiling stopping a 2.5 GB allocator). The first prune removed
79 GB across 229,728 files while keeping every report and manifest.
See [Resource containment and retention](../PARALLEL-IMPLEMENTATION.md#resource-containment-and-retention).

At that checkpoint, the LG Calibration Studio service was recorded as stopped
with automatic startup. This note does not verify its present state or authorize
a startup-setting change.

## What this establishes, and what remains uncertain

Stopping the identified LG service coincided with a large reduction in committed
memory and Section objects. Disk use from retained build artifacts was also
substantial, and cleanup/containment work addressed concrete operational risks.
Neither observation proves that FFTA tests caused the LG accumulation or that a
single resource issue explains every reported symptom.

The later symptom report narrowed to mouse-motion stutter that stopped when FF7
closed. That observation was not a controlled reproduction and does not establish
FF7, the mouse, Codex or an overlay as the cause. Lower committed memory alone
had not resolved all freezing. Preserve these distinctions instead of promoting
the initial theory or a successful mitigation into a complete causal diagnosis.
