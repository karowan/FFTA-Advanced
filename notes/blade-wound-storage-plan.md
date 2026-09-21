# Blade Wound storage plan

This document retains the storage investigation. For the subsequently
implemented private initial hit, scoped capture, end-turn pulses, lifecycle
cleanup and deterministic evidence, see `samurai-wound-review.md`. The accepted
main build includes storage/copy integration only.

September14,2026. Record layer implemented in an isolated callable-code test
artifact; no Blade Wound gameplay behavior enabled.

The existing format1 migration clears the entire inventory reserve
1940..1F1C before writing compressed counts and its header. Current assigned
fields end at1EBC;1EBC..1F1C remains96 unused zero-initialized bytes. A proposed
two-byte record for each of36 units consumes72 bytes at1EBC..1F04, leaving24.
Verify all current writers and old format1 loads before accepting this layout.

`blade-wound.c/.h` implements a two-byte record with a14-bit pulse amount and
two bits for remaining pulses. Count zero is inactive; count three is invalid
and never deals damage. Replacement schedules exactly two new pulses and no
immediate pulse. Each tick returns the stored amount and retires one pulse;
the battle caller will own actual HP application. Unrepresentable/nonpositive
references are rejected without altering the previous record, never clamped.

The isolated ARM-code fixture `e6fba4262eb982fd1d3038bd6b844ed79a36e9aa` passes
491161 assertions in
`build/expansion/test-runs/20260914T235955.945457Z/report.json`.
These enumerate all65536 serialized values, every positive signed16 reference
at both byte alignments, every byte offset in live/staging unit domains,
all party swap pairs including out-of-range indices, complete-state clear
guards, original migration and existing/unknown format handling. This proves
the record layer, not copy hooks, native save/load or gameplay acceptance.

Before integration, lock the snapshot insertion point and the native reference
bound. Read-only disassembly shows effective offense/defense capped at999,
the scalar at12FE28 is offense minus half defense, and12F5E0 adds primary
power plus up to five nonweapon equipment powers. For valid nonnegative stats
and byte power values, a conservative power bound is6*255. Base damage is then
at most15284, the largest affinity factor gives22926 and normal variance gives
at most25218, whose halved pulse fits14 bits. Higanbana must exclude critical
mode and the special last argument, final damage bonuses and interceptions.
Verify those actual call inputs and table-byte assumptions in deterministic
native execution before treating this mathematical bound as runtime acceptance.

Ownership must extend the existing explicit paths:

- Canonical24 party and12 enemy records use the same exact pointer/stride
  validation as Exposed/Centered. Staging save blocks require their explicit
  base, not a guessed live-owner identity.
- Adding two bytes to `Extra` makes its stride38. Proposed rounded allocation
  sizes: manager400 (two Extra records), selection3828, party7268, and
  Snapshot1014 (thirteen Extra records, struct padding included). Verify these
  through compiler assertions and actual allocator/copy hooks.
- `FFTA_EvaluatedUnit` can reuse two of its three reserved tail bytes and
  remain276 bytes. The bytes start unaligned for a Thumb halfword; access them
  as bytes or use an aligned representation. Initialization, copying, clear,
  heap retirement and stack-scope closure must carry/reset the wound record.
- Roster sorting, replacement, partial/full clears,13-unit snapshots and
  native state import must preserve or clear the correct unit's record.

Do not reserve a global current-owner shortcut. Preview/law copies must stay
independent, and a foreign or stale unit pointer must not resolve by identity.

Future status capacity is still a broader requirement. A read-only scan found
Human blank racial records0,103,104,142,143; other races have unused native AP
capacity and unused Human AP sidecars. Those bytes are **not assigned for
status storage** by this observation. Their native AP, theft, learning and
copy consumers would need proof before reuse.

Timing still needs native end-turn integration: exactly two subsequent
end-turn pulses; replacement without stacking; broad remedy removal;
KO/Petrify/job-change/battle-end cleanup; no reaction, proc, drain, critical or
outgoing damage bonus. Existing native Regen must coexist according to the
approved rules. Save/resume must not add or lose a pulse.

## Snapshot integration trace

Read-only native trace after the storage integration:

- A3072 calls131B20 after the accuracy/recipient path, but Damage-to-MP is
  resolved later atA30CE..A3116. In particular, reaction13 and positive target
  MP change the result kind from HP to MP. A positive magnitude atA3072 alone
  therefore cannot commit Blade Wound. Preserve an old wound on interception.
- 131B20 calls the descriptor magnitude callback at131B46, then the native
  factor133988 and story/invulnerability predicate130868. Do not replace that
  entire dispatcher with a bare physical formula and bypass those semantics.
- 1300E2 is the existing combined final-modifier insertion point. Capturing
  ordinary P there can retain the same variance sample as the immediate hit.
  Recovering P by dividing rounded final damage by0.8 is lossy. Recomputing P
  later with a new RNG sample is also unsuitable.
- A315A remains the actual-HP application hook used by Ashura/Osafune. Wound
  commitment must wait for a positive before/after HP difference there and
  carry the earlier captured P through an explicit, scoped execution record.
  Do not turn a pure query callback into a live saved-state write or use a
  guessed character identity to associate the snapshot with a result.

The concrete execution-record carrier and stack/heap lifetime still need
implementation and deterministic validation. No snapshot hook is enabled.

The native A433C output is not safely replaceable by a single2C4-byte local
copy: A44FC..A450E indexes multiple2C4-byte result objects from the outer
output. Do not shrink or replace that array to append a custom snapshot.

A suitable next implementation is an explicitly registered stack execution
scope, linked through a dedicated RAM root, with exact action/object/row and
evaluated actor/target pointers. Arm it only around the real A3072 magnitude
call, capture the pre-final reference at1300E2, and commit only for the matching
A315A row after positive HP loss. Queries must not arm it. A new recipient
clears previous readiness; nested executions push/restore separate scopes.
This avoids taking over native result fields or replacing native131B20's
compatibility/factor/story behavior. Reserve and test the RAM root explicitly;
do not introduce implicit ROM-module BSS or infer an owner by character bytes.
The shared root currently ends at3FF44; extending it by four bytes would require
moving the existing guard start and updating reset/save/constructor evidence.
This remains a proposed implementation, not an enabled or tested hook.
