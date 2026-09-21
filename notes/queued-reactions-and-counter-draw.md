# Queued Viking reactions and Counter Draw

Primary-agent implementation after the completed handoffs. No new agents,
persistent RAM, save schema, teaching lessons or player-file changes.

## Behavior and integration

Absorb Damage now queues a named self-reaction after all original hits. Its
payload is 30% of actual direct HP loss, floored, capped at 15% maximum HP and
missing HP. The native healing application creates a signed HP result. The old
silent action-completion HP write is removed. KO and disabled reactions do not
heal; reactions cannot recursively trigger it.

Gil Snapper queues a separate named self-reaction for an actual native critical
physical hit. It awards half the qualifying direct loss, floored, within the
existing 50-gil-per-unit battle cap and money capacity. Only an exact player
origin can receive money. The application rechecks capacity before awarding;
it does not debit an enemy inventory or gil balance. The old silent award is
removed. Native Steal Gil's result transport writes award+1 at context+18;
A34B4 copies it to result row+28/+2A and sets row+C bit1000. The queued action
uses that existing transport instead of inventing a status/result bit.

Counter Draw requires the real equipped Samurai reaction and a primary katana.
After surviving hostile direct physical HP damage, it queues one adjacent
counter per native primary transaction. Both actors must still be alive and in
range after native displacement. The counter uses ordinary physical accuracy,
1.00P non-elemental damage and one primary weapon, without weapon procs, drain,
MP cost or another reaction chain. Positive actual counter HP damage grants
Centered; an existing Centered charge neither boosts nor is consumed by it.
Native status admission remains in effect. The reaction can be equipped on an
otherwise legal secondary build; it is not restricted to Samurai job identity.

Counter Draw is installed in the combined candidate. The standalone Samurai
image supplies its help entry and shared hooks, but does not yet install its
runtime consumer. Viking's independent builder and the combined builder both
install the native queue entry directly, preserving r12 and the shared ABI.

Hidden action rows are 435 Counter Draw, 436 Absorb Damage and 437 Gil Snapper.
The action domain is now 438 rows; descriptors221/222 and applications100/101
belong to Viking. The central action table has only 24 bytes before the next
bank, so adding another row requires explicit relocation. All 16 per-unit
claim bits are now allocated; further consumers need an explicit capacity
design. See `shared-job-allocations.json`. Hidden rows remain outside command,
AP and AI lesson lists. Queue capacity failures do not acquire a queued claim.

## Deterministic acceptance

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite combined`.
The suite builds the combined and separate Viking candidates, prepares
hash-verified native fixtures and runs the queued-reaction checks in both.
No model drives test inputs or gameplay.

The Viking matrix checks 768 fixed original-action configurations, KO and
repeated battle-cap cases, actual critical flag provenance, one native result,
the acting wrapper and exact signed HP/gil display values. Counter Draw covers
256 Fight/physical-art configurations with and without Centered, native hits
and misses, critical knockback, six exclusion groups, 32 two-weapon scenarios,
all 44 native status admission inputs and all 461 item-element inputs. Queue
tests verify authenticated metadata, bounds, output guards and register/flag
preservation on the combined image.

The first 34-step run, `20260915T075444.196063Z`, passed 33 steps and exposed a
Counter Draw test assumption: positive damage does not guarantee adjacency
after a critical knockback. Diagnostic run `080106.063485Z` observed the target
move from (5,14) to (6,14) while the attacker remained (4,14). The test now
checks actual direct-loss events and post-hit range instead of requiring a
counter outside katana range. No gameplay change was needed for this fix.

Run `080159.935695Z` then exposed an invalid pre-executor status31 fixture
assumption. The exclusion fixture now uses Petrify, and a separate exhaustive
44-status comparison verifies the reaction gate against native admission.
The ten-step dependency/check run `080343.018613Z` passed. Source review then
added the missing native queue hook to the standalone Viking builder and
included that candidate's reaction regression in the consolidated suite.

Final consolidated run **20260915T080445.472975Z passed all 37 steps**, with
`inputsUnchanged: true`. Combined candidate is
`c32c11e88c6b228b1fd451cd5d4c30bdcf37b66c`, shared base
`20b10e74dcd6a747123352de472a0758fbe1602c`, and independently tested Viking
candidate `c60b181ba44b816a9fa754a573eb58434f3b68c2`. Counter Draw passed
2,766 assertions. All prior combined native, Chemist, Dark Knight, Viking,
cross-job factor, direct/fall provenance and Abyssal checks passed in the same
run. Reports and game assets remain ignored; only source and documentation
belong in the commit.

## Remaining acceptance

Native result objects and display values do not alone certify rendered
animation, message placement, turn return or suspend/cold behavior. The later
`reaction-playback.md` batch adds bounded rendered-frame/turn-return and native
cold checks for Counter Draw, Absorb Damage and Vengeful Pulse on the same
source candidate. Gil Snapper, Dark Ward and Chemist playback, full
law/AI/AP/equipment/acquisition/save coverage, Composure and the rest of the
approved expansion remain unfinished. This private candidate is not a release.
Use `IMPLEMENTATION-STATE.md` for the latest evidence and report distinctions.
