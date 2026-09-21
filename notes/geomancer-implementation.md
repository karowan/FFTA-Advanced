# Geomancer implementation

Historical support/reaction batch. Subsequent implementation and acceptance
of active Geomancy are recorded in `IMPLEMENTATION-STATE.md`; field persistence
and remaining presentation work are in `geomancer-field-presentation.md`.

Scope: approved v0.7 `GEO-S1`, `GEO-S2`, `GEO-R1`, `GEO-R2` on the assembled
candidate. The nine Geomancy actions and their terrain/field rules remain
unimplemented. This document does not claim full-job or expansion acceptance.

## Shared contracts

Attunement freezes the equipped support at action start. Its final damage
factor is 5/4 for an elemental weakness, composed with existing final factors
before rounding. Native elemental resolution supplies the attack element,
recipient affinity, equipment overrides and applicable law adjustment.
Non-elemental, MP-only interception, fixed/percentage effects, reactions and
combos do not gain an outgoing damage modifier. Only voluntary primary direct
HP loss to an enemy admits a refund, including a killing hit. Refund is
floor(actual MP debit/4), once at completion, capped by missing MP. Multiple
recipients or repeated completion cannot multiply the refund.

The existing snapshot's 32-bit payment-count word is now two 16-bit fields:
payment count and actual MP debit. The snapshot remains820 bytes and the
external result slot remains824 bytes. Native entry captures pre-payment MP;
the paid callback records a nonnegative debit. Explicit nested queries inherit
the accounting, and scope retirement clears it. This is transient state only;
the22-byte job/save schema does not change. Consumers reading raw snapshots
must decode the two fields separately; the payment-count getter is unchanged.

Extra snapshot bits13/14/15 freeze Attunement/Stone Skin/Nature's Wrath.
Bits21/22 admit and queue a Geomancer reaction; bit23 seals the refund and bit31
admits it. Extra claims therefore accept bits21..31; bits0..20 stay immutable.
Existing Bard and Dancer allocations remain unchanged.

Stone Skin multiplies eligible enemy physical direct HP damage by3/4. A
surviving recipient queues native Protect once through hidden action443,
kind145. Nature's Wrath queues hidden action444, kind146, against the original
attacker within four Manhattan tiles. It uses native A accuracy and M24 Wind,
with no MP/JP payment, learned-action lookup or recursive reaction. A tagged
temporary actor removes outgoing support damage from the magnitude calculation
while preserving native Magic Power, equipment and target resistance. Accuracy
still sees the original actor. Native reaction readiness controls admission.

Both reactions use the existing bounded native queue and result pool. Protect
uses the native status and duration rather than introducing a second timer.
The native reaction display uses the bounded label `Nature Wrath`; the design
retains `Nature's Wrath`. All four lessons have in-game help.

## Native movement findings

`CA2E8` rebuilds movement modes and signed Jump into unitFC..FF. Its wrapper
adds one Jump for Surefoot, preserving equipment and the complementary downward
bound. `CA394` still supplies the unchanged Move allowance.

The per-unit tile callback `97814` receives the exact movement wrapper as its
fourth argument. It supplies native terrain validity, water rules, occupancy
and height to the seven-byte grid cells. The low nibble of cell byte1 is the
entering-tile cost consumed at `148E5E`; the pathfinder separately adds the
gap-jump segment cost. Surefoot normalizes only costs above one after native
tile construction, preserving all other bits. The inspected original callback
assigns cost one to passable tiles. Do not invent an additional vanilla terrain
penalty or treat impassability as a surcharge. Rime Field's future tile-cost
provider must compose before Surefoot normalization and requires its own
runtime acceptance.

## Reproduction and verification

Use `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite geomancer`
for the declared focused suite, then `-Suite combined` for assembled acceptance.
The focused script reuses the current ROM's native executor capture; it records
fixed inputs, misses and positive cases, reaction objects, actual HP/MP changes,
native movement rebuilding, preview immutability, rational cross-job factors,
and authenticated refund contracts. Shared reaction playback also includes both
Geomancer reactions, rendered code guards and native suspend/cold resume.

First compilation exposed an unsupported `+` in native help text; the help now
uses words. The first runtime fixture incorrectly used packed ROM affinities
where live units use nine bytes at0C..14. Explicit affinity assertions prevent
vacuous weakness tests. Native Stop was not a valid no-reaction control under
the existing native readiness rules; the incapacity control uses Petrify.

## Accepted checkpoint

Candidate `f8d905bde8386802d61c4b9b6258c6182b95fcec`, base
`473cf0f4546cabb55ce614abe84f8536a947847a`:

- `20260915T171410.179624Z`:54/56 combined steps passed. Only the raw snapshot
  decoder and old hidden-action boundary failed; the new native transactions,
  reaction playback, cold save and existing jobs passed.
- `20260915T172753.497212Z`:12/12 focused review steps passed after correcting
  those test assumptions. Both runs report unchanged tested inputs. The ROM
  hash did not change between runs. Existing passed evidence remains applicable.
- `geomancer-passives.json`:2,852 assertions,664 native executions. The added
  support control uses the actual95-entry original Nu Mou lesson bank, rather
  than scanning neighboring tables. It compares successful retaliation damage
  and preserves differences in A-accuracy; a miss is not a zero-power hit.
- `reaction-playback/report.json`:934 shared assertions. Both new reactions
  render, preserve native IWRAM code, advance the turn and survive native
  suspend/cold resume. This is not image recognition of every animation frame.

Root's final review covered native prologue/continuation preservation, exact
four-argument tile callback ownership, equipment-inclusive Jump, one-rounding
damage composition, actual-payment accounting, one-shot refund sealing,
temporary support-copy retirement, reaction bounds and unchanged save layout.
No additional RAM or saved-state reservation was introduced. The integration
code is23,936 bytes within its32,768-byte reservation.

Remaining: Geomancy actives and field/affinity behavior, live terrain surcharge
acceptance once Rime exists, broader legal AI builds, equipment/AP acquisition
and full campaign acceptance. A433C payment scopes do not by themselves prove
the complete voluntary Doublecast transaction; this batch adds no cross-race
access to Doublecast or Geomancer supports.
