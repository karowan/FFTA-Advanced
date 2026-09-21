# Bard active kit and action snapshot storage

This batch implements the eight approved Song actions, their native descriptions,
Marching Strength and Inspired Magic. The subsequent support/reaction work is
recorded in `bard-passives.md`. Chorus Combo acceptance, full command UI,
AI/laws, teaching/acquisition and dedicated song playback/cold-save cases remain.

## Native implementation

Actions393..400 use ordinary native effects for Protect, Shell, Regen,
Invisible, MP recovery and Holy damage. Custom descriptors223..227 and
applications102..104 add the two timed buffs and percentage healing/cures.
Soul Etude cures Poison, Blind, Silence and Confuse along with its healing.
Restoration combines the recipient's Recuperation before rounding once and
caps to missing HP. Ballad restores20 MP and excludes its caster. No song
requires an instrument. Hide alone works while Silenced; songs do not permit
Reflect, Doublecast or Return Magic.

Requiem uses the native Holy donor11, M60, and enemy-undead eligibility.
Native elemental affinity remains authoritative, including immunity and
absorption. A former failure came from the fixture monster's retained Holy
absorption at unit+0x13, not from a reversed damage routine: native Holy healed
the same fixture too. The test now declares neutral affinity for ordinary
damage and separately exercises all five affinity values. No engine workaround
forces Holy damage through absorption.

Owned job byte10 contains two independent three-bit T2 timers. Both tags clear
on KO, Petrify, battle end, job change and Dispel, and tick once through the
composed lifecycle. Native status keys33/34 use OBJ tiles1F0..1F3; the dynamic
pool begins1F4. The eight help strings/table occupy12C0000..12CFFFF. Exact
allocations are in `shared-job-allocations.json`.

The buffs apply6/5 to their corresponding direct physical or magical HP damage
and combine with the established job factors before the final division. They
do not amplify items, fixed effects, healing, explicit combos or reactions.
Action-start snapshots freeze the buffs across recipients and explicit copies.

## Stack correction

Adding another32-bit flag field to every snapshot unit grew each nested native
stack frame from820 to1076 bytes. Full playback exposed overwritten native
sprite-renderer code and stalled, despite the native result calculations
returning successfully. Merely restoring820 bytes was insufficient until an
unused820-byte local was removed from the ordinary result continuation path.
The large new-actor scope now lives in a separate noinline helper, allocated
only when a new result actor needs its own snapshot.

Extra flags use eight external260-byte slots at0203EA00..0203F21F instead.
The later Passing Step reservation lowers all three integrated heap-limit
literals to0203E800; this extra-flag bank stays at0203EA00. Each slot belongs to
an exact active snapshot address, carries64 flags and retires with that scope.
Stale inactive owners can be reclaimed. The original820-byte snapshot layout,
64-unit capacity stayed intact in this fix. Later schema2 uses22-byte owned
records and824-byte save footers; see `shared-job-allocations.json` for the
current complete layout.
Standalone builds have no bank provider and never touch this reservation.

Playback now guards native IWRAM6170..6D67 against its ROM source at
A38D24..A3991B, through Wait transitions and attack/reaction rendering.
IWRAM6000..616F contains changing runtime data and is deliberately outside this
code check. Earlier broad checks mistook this normal mutation for corruption.
An isolated old-pool comparison also reproduced the stall; OBJ allocation was
not its cause.

The executor fixture waits for the actual native menu after movement instead
of assuming that180 frames always completes it. Its cache binds both the menu
observer script and the observer's fixed pixel-anchor data.

## Deterministic evidence

Later native AI valuation, redundant-buff rejection, shared-support healing,
MP-command admission and autonomous Chant/Ballad evidence are documented in
[Bard native AI decisions](bard-ai.md). That bounded audit does not replace
the player-control presentation cases still listed in the checklist.

Run through `Test Expansion.ps1 -Plan scripts/integration-test-plan.json`.
The `combined` suite covers existing integrated jobs and the new Bard test;
`test-integrated-bard` and `test-integrated-reaction-playback` are independently
selectable with their prerequisites. Diagnostic steps retain the failed
controls but are not acceptance tests.

The Bard script covers all eight native executors at eight fixed seeds,
five Holy affinities, eligibility, exact MP spending, rational incoming healing,
preview purity, frozen/copy/nested flags, slot retirement/boundaries, T2 lifecycle
and combined damage factors. Playback uses24 fixed native attack/reaction
cases and three native suspend/cold resumes for Samurai/Viking/Dark Knight.
Those playback cases are regression evidence, not Bard-song visual acceptance.

All43 combined steps passed with unchanged inputs in
`20260915T092827.976722Z`, candidate
`497f6191a1061fa7a067000ca411aa80c98a8734`, shared base
`e8031f5b32c197c7d4c416dda4da289a7fe2a862`. Bard passed899 assertions with104
native song executions. Shared context/Poise/Ward passed4,073/1,752/1,596
assertions, and reaction playback/cold resume passed350 checks. The earlier
corrected11-step affected run `20260915T092533.417564Z` also passed.

Failed diagnostic/acceptance reports are retained: `085735.948722` (expanded
stack), `091035.438281` and `091512.844549` (remaining stack allocation and
absorbing fixture), `092222.747088` (overbroad IWRAM guard and absorbing
fixture). Fixed native controls are in `092400.577000`. These report IDs all
have the `20260915T` prefix and `Z` suffix. An intervening plan-order error
stopped before execution and was corrected before the final43-step run.
