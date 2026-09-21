# Native reaction queue prerequisite

Source-only handoff, September15 UTC. No new RAM or save layout. This prerequisite
is tested native queue transport, not acceptance of every job reaction or its
visible presentation. The shared Samurai build compiles the entry without
installing it. A consumer must install the guarded twelve-byte native span
A4ADC..A4AE8 directly to `ffta_reaction_queue_entry`; do not use a C binding veneer
that clobbers r12. `scripts/jobs/chemist/build.py` is the composed example.

## Exact contract

`ffta_additional_reaction_queue(unsigned *native_frame)` is a padded optional
provider. It runs at native A433C queue exhaustion, before its arena is freed,
with the primary snapshot temporarily COMPLETING. It can recur after appended
reactions: consumers must use their assigned one-shot claims. This is different
from event3, which runs after A433C and is too late to append presentation.

`ffta_reaction_queue_append(frame, acting, target, action, kind, payload)` returns
one on append, zero without mutation on rejection. Acting and target must be
exact units in the active snapshot and map to exact native wrappers in the
original actor or completed recipient rows. The composed Doublecast provider
may additionally return an exact first-result wrapper retained by its owned
continuation, after authenticating the active second-cast frame. There is no live-unit fallback,
coordinate identity inference or persistent pointer registry in the kernel.
The original primary wrapper remains separate from the target; self-target
Shell therefore retains reaction provenance. Consumer owns eligibility,
hostility, range, resource checks, payload calculation and claim acquisition.

`ffta_action_unit_at(index)` returns the exact snapshot unit or NULL. The custom
request kind/value getters return only authenticated RESULT/REACTION metadata,
never QUERY, unrelated frames or ordinary native reactions. All permission uses
mask low8 independently from kind/payload. Query inheritance strips payload.

The native frame is bound by the actual two A23B8 caller returns A4856/A4A9E and
their explicit caller SP, or by the installed queue-entry assembly supplying
its real body SP when an empty second cast has no result callback. The latter
requires an EXECUTING primary snapshot, aligned live-stack frame and exact
actor/action; it is a trusted assembly-entry contract, not a public queue
fallback or stack scan. Direct queue APIs still reject unbound frames.
The existing private result_object
word temporarily retains that frame while EXECUTING; public object getter stays
RESULT-only. It is retired at primary completion and zeroed with the820-byte
snapshot. No layout size changed. Unknown/stale/neighbor frame pointers reject.

## Native layout and continuations

A433C body frame: +20 output, +24 original wrapper, +28 original action,
+44/+48 targetXY, +4C current action, +50 mode, +68 allocated256-byte queue,
+6C read cursor, +70 write cursor, +74 current actor, +38 result count.
Each16-byte request: +0 acting wrapper; +4 original primary wrapper; +8 action16;
+A/+B targetXY; +C mode8; +D payload low8; +E reaction kind; +F payload high8.
Native mode reads byteC. The custom dispatcher sets one result and mode0, then
continues A4C3A, which advances the reader and reaches native constructor/apply.
Original empty/default cases replay to A529C/A4AE8 with exact registers/NZCV.
Custom kinds128..255 bypass the native1..15 switch. The original handoff's
maximum action435 has since grown to437; `reaction-ids.h` and
`shared-job-allocations.json` own the current 438-row domain. The queue remains
zero-terminated. At most13 displayed
objects are admitted because native output has14 slots and touches a scratch-next
slot even at exhaustion. Pending custom single-result requests reserve capacity.

Arena validation uses native allocated header magic616C and size, exact current
frame ownership, aligned cursors and bounds. The kernel uses native selected-item
buffer0200F888 and queue flag0200F890 only at their existing native setup boundary.
For kind136 payload is the explicit Potion item; other requests retain primary
gear. New action records must be installed separately; do not infer that a valid
numeric ID has implemented data.

## Build and verification

Add reaction-queue.c/.s alongside action-snapshot.c/.s in production compilation;
`scripts/build-samurai-probe.py` does this in the private pipeline. Rebind the
optional provider deliberately when composing jobs, never last-writer-wins.

Run `Test Expansion.ps1 -Suite samurai -Only test-action-context,test-reaction-queue`.
Run060243.400797Z passed five steps: original executor, compilation/capture,
4073 context checks and2339 queue checks on Samurai
4d0110964db2a11fa4e28c7042dc483ab0980b66. Queue checks include all256 kind bytes,
empty/nonempty, SP0/4, two NZCV patterns, all registers, real captured native heap
and frame, self-target original-wrapper provenance, payload0/362/65535 and no-write
negative guards. The composed Chemist version also passed2339 in060259.940652Z.

Chemist candidate1d4ac0da9caf3a0f42f23bf5a05e0ac80a265b16 separately passed1536 full
native Auto-Potion cases (6257 assertions,112 positive recoveries) across both
races and SP0/4, with real item objects and exact consumption. All347 native plus
accepted custom executor comparisons remain. These are not screenshots or
acceptance of DRK/CounterDraw visuals; actual visible reaction playback remains
for root integration. Shared Doublecast grouping now has bounded constructor/
queue evidence in `notes/mystic-knight-doublecast.md`; full controller/render
acceptance remains pending. Queue ABI/negative controls also passed on candidate
`c1fee872002c58941114f2d80aae2073ce910244` in `20260916T091435.519188Z`.
