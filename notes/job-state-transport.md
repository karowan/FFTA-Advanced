# Common job state transport

The private builder is `scripts/build-job-state-probe.py`. Current acceptance
and remaining steps live in `IMPLEMENTATION-STATE.md`; do not infer whole-job
completion from this infrastructure. All generated ROMs/logs stay ignored.

## Inputs and installation

The builder starts from the local `probes/samurai/current.json` ROM and verifies
its hash. It imports known accepted-main functions and Samurai copy observers,
recompiles the owned-copy/evaluated modules and the sole physical-rider stack
consumer, and installs code at ROM offset `0x11D0000`. Generated bindings must
not force ARM compiler helpers into Thumb mode; libgcc supplies those locally.

Only declared existing code regions are rebound. Original native hook bytes
and allocation operands are asserted before modification. The new module is
appended after rebinding the base so explicit original-function imports remain
original. The output manifest lists every changed call/pointer/allocation and
all imported addresses, along with base and resulting ROM hashes.

The main heap ends at `0x0203F400` instead of `0x0203F800`. The bank consumes
808 bytes of the explicitly reserved 1 KiB; the inventory view starts at
`0x0203F800` and copy/action roots remain above it. This is not spare AP space.

## Ownership and public API

`src/engine/job-state.h` exposes a 22-byte independent record for exact live
party/enemy units and explicitly registered native copies. Origin tokens are
1..24 party, 25..36 enemy, 0 unknown. No character-name/stat/ID lookup recovers
ownership. A copied origin identifies its source; it does not return a pointer
to live state, and simulated mutations must remain local to their recipient.

Enlarged tails belong to actual native allocations: snapshot `0x1140`, manager
`0x430`, selection `0x3840`, party `0x7280`, evaluated unit 304 bytes. Exact
copy chains propagate record/origin/preference. Full clears erase copy records
and origin; partial copies do not change sidecars; foreign sources clear owned
destinations; freed/retired/interior pointers are rejected. Native snapshot
rollback copies saved records back to canonical slots. Original AP, preference,
Exposed and Wound behavior is retained and tested. Evaluated stack frames must
be allocated with the new header, and Samurai observers must remain composed.

`ffta_job_peers(unit, output, capacity)` enumerates the complete exact owner
group only if the output buffer fits. Otherwise it returns0 without writing.
Groups are canonical36, one native snapshot13, one manager2, or a singleton
selection/party/evaluated owner. `ffta_job_peer(unit, token)` returns a unique
matching peer; missing or duplicate origins return NULL. No lookup crosses
owners. Missing representation does not prove a caster dead. For lifecycle
cleanup use enumeration so duplicate-origin manager copies are both handled.
Independent singleton actor/recipient evaluations may be connected only by
their explicit native transaction context, not by scanning all heap copies.

The native persistent roster reorder now swaps job records together with the
original AP/preference sidecars. It reindexes the two assigned source-token
fields (DRK byte1, Viking byte5) in canonical and registered copy records.
Full canonical clears forget the old token; a forgotten TBN source also clears
DRK byte2. Unknown token0 is never reassigned. Heap previews retain their exact
ownership. Transient stack evaluations end before the native roster UI can
reorder or replace a unit; they must not outlive that transaction.

## Save format

Suspend slot2 writes an 824-byte footer at byte `0xCA8` of its fourth 4 KiB flash
sector. The native payload CRC and length stay unchanged. Footer fields are
magic `FFTAJS02`, schema2, record size22, record count36, save generation,
independent CRC32, payload length792, reserved zero bytes, then the records.
The native payload marker `JST1` occupies `0x1F04..0x1F07`, four explicitly
available bytes after Wound. Save staging tail and marker are restored after
the synchronous native write on every return. The footer binds to the native
generation; a marked corrupt/stale footer rejects load before live publication.
Ordinary loads initialize transient job records to zero. Valid schema1 footers
migrate bytes0..2 and4..14; formerly reserved bytes3/15 and added bytes16..21
start empty. Both schemas validate the whole envelope before publication.
See `remaining-state-capacity.md` for the allocation and current acceptance.

## Reproduce in an independent worktree

1. Adopt the coordinator's exact common source commit on the job branch. Keep
   local source changes committed or otherwise safely preserved; do not replace
   the worktree or force-discard changes. Resolve overlapping plan/docs changes.
2. Use the worktree's own accepted binary, generated tables, compiler, emulator,
   and private Samurai build. Run the named `job-state` steps through its local
   `Test Expansion.ps1`; no parent output links or ROM commits.
3. The local result is `build/expansion/probes/job-state/current.json`. Record
   adopted source commit, local ROM hash and deterministic reports in the job
   `STATUS.md`. Build job consumers over this local base with explicit hook
   composition; do not silently use the old Samurai-only base.
4. Regenerate native test fixtures with the new candidate and heap end. Old
   frozen heaps contain smaller allocations and are not valid enlarged-owner
   fixtures. Preserve them as native controls only where their scope permits.

## Remaining acceptance boundaries

Canonical roster permutation and assigned source-link remapping now pass the
native UI and independent permutation tests. Complete replacement flows still
need their native acceptance. The transport does not implement individual job status
timers, relationship cleanup, reaction latches, immunity or action payment.
Ordinary save-slot independence,
new-game paths, larger action-context stack pressure and full cross-job combat
regression remain. These limitations must remain visible in each consumer's
acceptance report until implemented and tested.
