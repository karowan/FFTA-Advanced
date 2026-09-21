# Council review: native copy ownership and snapshot rollback

Reviewed 2026-09-14 against frozen ability-core ROM SHA-1 **`10ca5ae2bd69885be81513b931d120c1ee92f884`**, engine SHA-1 `7f7dc1b1f6785bc2a86f1c55ba7a8e0a7cb9d4df`. The ROM, manifest, symbols and reviewed source versions are retained under `build/expansion/probes/copy-council/`. Current project builds may subsequently differ.

**No demonstrated defect in the bounded allocation/ownership implementation.** Independent native tests establish that13-unit snapshots retain separate AP/preference values and that the actual native rollback loop restores them. Native manager allocation and selection create/destroy hooks also passed. This does not establish complete ownership of every UI/battle unit copy, nor enable the ten new jobs.

Reviewed `unit-copies.c`, its `abilities.c`/`persistent.c` integration, new `ability-hooks.s` wrappers, and `build-ability-probe.mjs`. No engine or builder edits were made.

## Repeatable native evidence

Run `python scripts/test-copy-constructors.py --current` for build integration. This verifies the current ROM and engine hashes, freezes ROM/manifest/symbols into `build/expansion/probes/copy-council/runs/<ROM-SHA1>/`, verifies installed constructor entry symbols, then executes only that frozen image. Its report is `constructor-tests.json` in the same per-hash directory. Without the flag it retains the historical frozen-mode behavior. The original tested build passed **490 assertions**, in addition to the execution harness's return, stack-balance and callee-saved-register checks; see the follow-up below for the current party ownership coverage.

| Coverage | Assertions |
|---|---:|
|Actual snapshot allocation capacities|6|
|Snapshot construction, native prefix equivalence and registration|24|
|13 sorted snapshot rows × native bytes, AP pointer,34 AP bytes, preference|312|
|Native middle/head/tail free order, remaining-node ownership, complete heap reclamation|16|
|C-call stack alignment across constructors and rollback|8|
|Actual native preview allocation/snapshot/rollback/free|84|
|Native manager parent/child allocation and owner lifecycle|18|
|Native selection constructor/destructor and owner lifecycle|16|
|Three exact heap-clear extents and adjacent nonmatching sizes|6|

Tests execute both native Thumb stack residues (`SP mod8` equal0 and4). mGBA supplies the original boot-installed IWRAM copy/clear routines; Unicorn executes native heap initialization/allocation/free, copied-record dispatch, constructor loops and rollback code. This is native routine testing, not a rendered battle or complete AI test.

The snapshot fixture supplies thirteen distinct roster records, thirty-four distinct AP bytes per unit, and distinct Auto-Potion preferences. It deliberately reverses the native `unit+104` sort key. A fixture callback replaces only battle-unit enumeration at`99CDC`, yielding real wrapper pointers to these records. Native `9DE94` sorts them, fills its pointer list, and copies all13 records through `142250` and the installed copy dispatcher. Every original byte in its`E1C`-byte prefix matches the clean ROM's constructor output for the same fixture.

The rollback test executes **the complete native `9F850` wrapper**. It allocates the snapshot, invokes the real constructor, runs a fixture simulation callback at`9E1E0` that deliberately changes live native fields, all extended AP bytes and preferences, then executes the real`9F88C..9F89A` reverse-copy loop and native free. All thirteen units and their sidecars return to their original values. Ownership and heap state are fully reclaimed. The simulation callback substitutes the action itself; it does not substitute capture, restore, or free.

The manager test executes native`96ED4`, including the enlarged parent allocation, native subheaps and`97000` constructor. Unrelated resource sizing/loading/render object functions are stubbed with bounded fixture values; real deployed resource sizes remain an in-game integration test. The selection test executes native`64EF8` for create and state255 teardown; unrelated scheduler-object functions are stubbed. Selection allocation, clear, pointer publication and free are native.

## Findings on the implementation

### Allocated tails and exact identity are sound in the tested paths

- Snapshot layout is consistent: original`E1C` bytes,8 bytes of next/magic metadata, thirteen36-byte tails =`FF8`. Each tail contains34 AP bytes, one preference byte and padding. All four identified native allocation literals were expanded to`FF8` before the constructor hook is used.
- Snapshot registration precedes the native clear. That clear retains its original`E1C` size, so it does not erase the new next pointer, magic or tails. Registration initializes them before any native record copy can resolve its destination owner.
- Manager allocation grows from`3B4` to`3FC`, exactly72 bytes for two tails. The parent capacity grows96 bytes (`84 <<3` becomes`90 <<3`), leaving24 bytes beyond the direct payload increase for native heap layout/alignment. The bounded native constructor succeeds with the patched size and initializes both tails.
- Manager units at`+40` and`+148` resolve only while the registered pointer matches native global`0200F4B0`. Selection unit`+A4C` resolves only while its registered allocation matches`0200F454`; its36-byte tail fits exactly at`+3800..3823` in the enlarged`3824` allocation. Misaligned/interior candidate pointers are rejected in tested cases.
- Snapshot records are identified by allocation membership and exact264-byte stride, not a copied character name, race, slot tag, or equipment combination. The linked list validates RAM extent and node magic before following a node and caps traversal. The64-node bound exceeds the number of`FF8`-byte allocations that can physically fit the permitted RAM interval.

### Copy semantics preserve independence and rollback

`ffta_on_unit_copy` applies only to full264-byte copies in the migrated live format. It saves source AP/preference into a local value before writing the destination tail, then the wrapper resumes the original IWRAM native copy. This avoids treating a snapshot's AP as a live reference to the current roster slot. An unowned source initializes the owned destination's extension to zero instead of preserving stale values. The independent rollback test confirms the required transaction behavior; direct getter tests alone would not establish it.

The public ability accessor still rejects Human reserved indices142/143, routes144..177 to explicit owners, and preserves inline native access below142. The roster ownership calculation uses exact264-byte slot alignment across24 entries. Copy transfer includes preference bytes independently of race, while Human-specific ability access remains gated by race and storage format.

### Free and reset lifecycle

The `7170` wrapper passes its native allocation argument in`r1` to the owner invalidator before reproducing the original `allocation-12` native heap-free call. Three simultaneously registered snapshots survive non-LIFO frees without losing remaining nodes; after the final free the chain is empty and the native heap header matches its initial state. Native selection teardown clears both the registered root and native selection global.

Manager individual free invalidates its owner. Native normal manager-parent teardown additionally clears the public manager global (`96D50..96D54`), so a stale cached root pointer cannot resolve a copy afterward even when the outer allocation, rather than the manager payload, was freed. The separate full-heap reset hook clears the16-byte root for the three audited heap-clear start/end pairs. Tests verify exact clear extents and reject nearby nonmatching sizes. Real scene transitions should still be included in the parent's emulator pass: these tests do not prove the three reset call paths exhaust every possible heap reinitialization.

Every tested new C entry receives an8-byte-aligned stack. Snapshot, manager, selection and free wrappers preserve native callee-saved registers and stack balance under both incoming residues. The shared copy wrapper restores native arguments before branching to the original IWRAM routine; the parent owns the broader copy/permutation matrix.

## Remaining integration boundaries

1. **Unregistered copies intentionally lack Human extension AP.** This implementation covers live roster records, thirteen records per registered snapshot, two manager copies, and one selection copy. It does not register arbitrary stack copies or the party menu's temporary record at menu base`+1BE4`. Native reads through those contexts need either an explicit owner/copy lifetime or access to the actual roster owner. Do not conclude all AP consumers work merely because the central accessor returns safely for unknown pointers.
2. **Full-copy dispatch is the integration boundary.** Paths that construct a record by selected fields, use a different copy primitive, or clear/reuse a container without either the full-unit clear or native allocation free will not automatically transfer/reset its extension. The current hooks cover the demonstrated full native snapshot copies; identifying all alternate construction paths remains separate work.
3. **Register fresh allocations once.** Current native snapshot callers all allocate immediately before calling`9DE94` (`9E874/9E87C`, `9F798/9F7A0`, `9F7FA/9F802`, `9F85E/9F866`). `ffta_snapshot_register` is not an idempotent reinitializer: calling it twice for an already linked allocation could create a cycle. No known native caller does so, so this is a helper contract rather than a demonstrated game regression. If a later hook reuses allocations, unregister before re-registering or make registration explicitly idempotent.
4. **The native constructors assume allocation succeeds.** This was already true of their original implementations. Larger allocations require real in-game heap-margin evidence; the fixture manager constructor uses substitute resource sizes and cannot close the loaded-scene memory-budget question.
5. **Gameplay effects and copied preference use are not covered.** Preserving a preference byte through snapshots does not prove Auto-Potion consumes that preference correctly; likewise, ownership preservation does not prove new jobs, action effects, UI selection or saved constructors are complete. The ten new jobs should remain disabled until those independent gates pass.

Within the tested constructor/lifetime scope, the implementation preserves native record behavior while supplying the missing AP rollback ownership. No change request to the parent engine is required from these tests.

## Follow-up: party preview ownership

The latest independently tested frozen ROM is **`900201d5411e4c8a87157e34213db11800a79e99`**, engine`5e064df644bf5eb11f327f6add623419afab675b`. The expanded suite passes **808 assertions**. This supersedes the specific unregistered party-preview concern in boundary1 above; arbitrary unrelated stack/partial-field copies remain outside the ownership model.

The owner root is now20 bytes (`0203FF30..0203FF43` inclusive). Both native`7109C` constructor modes allocate`7264` bytes through the two patched size literals. The original BIOS clear still covers`7240` bytes; post-constructor registration initializes the36-byte tail at`+7240` separately. The party preview at`+1BE4` is recognized only while its registered party allocation matches native global`03002818`.

Tests execute both complete native constructor branches and their corresponding native`71234` destructor branches, under both stack residues. GBA BIOS CpuSet is emulated as a firmware fill/copy primitive; no game constructor, allocation, library-copy, unit-clear or free code is replaced in this test. Thirteen successive full copies through the newly wrapped native library routine`1443FC` reproduce all264 original bytes and the correct AP/preference tail. Mutating the original roster afterward does not change the preview snapshot. A260-byte partial copy leaves the tail unchanged; a full264-byte native clear clears its AP/preference and preserves all live roster AP. Detachment rejects ownership; normal native teardown retires the owner. Guards immediately after the20-byte root remain unchanged. Exact heap-reset tests now include a nonzero party pointer and an adjacent guard.

New coverage adds party24, library-copy212, clear60 and free12 assertions, four additional ABI assertions, and six stronger reset guards. Snapshot rollback, manager, and selection coverage continue to pass on this newer build. No party-owner defect was demonstrated. Real menu rendering is assessed separately by the parent's command-browse tests.
