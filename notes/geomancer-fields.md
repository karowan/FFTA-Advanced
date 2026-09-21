# Geomancer movement and field batch

Historical implementation batch. Later work accepts all nine player actions,
terrain/material rules, Torrent/Gaia AI and native Rime/Refuge cold saves and
expiry. See `IMPLEMENTATION-STATE.md` and `geomancer-field-presentation.md` for
current evidence and remaining scope. The limitations below describe this
original batch; they are not the current implementation inventory.

This batch implements Updraft's timed movement/Float/conditional Jump, Rime's
base Ice attack and movement field, and Nature's Refuge's placement/protection.
It does **not** complete Geomancer or the expansion. Rime's ice-affinity Slow,
terrain mappings, other active abilities, field map outlines, complete command
presentation and dedicated native cold-save playback still need work.
Native AI action scoring for the new field/Updraft utility is also unaccepted:
an independently owned prediction record is necessary, but does not establish
that the AI values and chooses the utility. Do not equate the empty-area native
executor check with complete player cursor or AI placement acceptance.

## Runtime contracts

The three native commands are377/380/382, with8/12/12 MP and a chosen r3 cross
within2 height. Existing native recipient/accuracy/effect/payment consumers run
the commands. Geomancy is weapon-free and classified Magic for sequencing;
Silence, Reflect, Return Magic and Doublecast flags are disabled. Updraft uses
descriptor233/application109, an ordinary willing-ally application observed by
the existing first-persistent-benefit observer. Refuge has no recipient effect.

Updraft stores its Float/Move T2 in byte18 bits1..3 and lower-recipient Jump T2
in bits4..6 of the existing22-byte owned record. Each timer independently skips
its application turn when the recipient is the caster. A lower recipient must
be at least two native height units below the caster. Refresh does not stack;
a cast without the height bonus does not erase an earlier unexpired Jump bonus.
Float here is an explicit timed tag, not an invented native status bit or a
grant of unrestricted flight. It excludes Rime costs and Refuge protection.

The native Move getterCA394 already belongs to Light Foot. Integration wraps
its existing `ffta_move_with_support` function, adding Updraft once. The native
turn allowance therefore sees both bonuses. Jump is added after the ordinary
CA2E8 mobility rebuild, together with Surefoot, saturating the signed-byte
upper boundary and retaining its native complement byte. No coordinates,
occupancy, movement mode or immediate movement change.

Fields share exactly one slot per caster: bytes15/16 center coordinates,
byte17 low2 kind (1Rime/2Refuge), bits2..4 T2. Field creation uses event2 after
the native result, its authenticated object center10/11 and actual payment.
This also runs for empty areas and misses. A caster's new field replaces its
old one, preserving Wisp's separately reserved high bits. Caster KO, Petrify,
job change and battle-end events clear it; ordinary Dispel is not a field
removal. Two subsequent caster turns expire it, excluding the casting turn.

Every field query enumerates the explicitly owned same-cohort peers. Independent
evaluated copies never borrow live battlefield casters absent from their copy.
Cross membership is Manhattan distance<=1 with native height difference<=2;
nonexistent map cells do not qualify. No field changes the underlying height
or water flags used by terrain affinity.

The native97814 tile callback retains every ordinary blocked, occupancy and
height bit. Rime adds one to the entering-cost nibble of legal generated tiles,
regardless of allegiance or overlap count. Float, innate/equipped flight and
Surefoot bypass that surcharge. Surefoot normalization runs after Rime. Native
pathfinding and the existing Passing Step budget read these same costs.

Refuge is frozen as extra snapshot bit18 at incoming-action start. Only
grounded allies of a field caster qualify. Enemy magical direct HP damage is
multiplied by4/5 in the shared rational finalizer; the outgoing-bonus exclusion
for reactions does not remove incoming shelter. MP interception retains its
existing exclusion. Occupancy is not a beneficial status and never qualifies
Poise or Encouragement. Updraft's tagged recipient benefit does qualify Poise.

Status39 is the recipient's Updraft arrow. Status40 is a field caster's cross,
not a status on occupants. They use OBJ tiles1FC..1FF. Native dynamic allocation
starts at200, using a verified `MOV r3,128; LSL r3,2` replacement for the former
byte-sized doubled constant. Caster icons are not field outlines on the map.

## Deterministic acceptance

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite
geomancer-fields`, then the combined suite after the coherent batch. The script
reuses the current hash-matched native battle/executor capture. No interactive
test driver or manual playthrough is required.

Candidate `9471b6907d45c5b8a8f5c085674e19558e3b806c`, shared base
`473cf0f4546cabb55ce614abe84f8536a947847a`, passed all10 focused steps in
`20260915T174956.176246Z`. The field report has13,062 assertions and62 complete
native executions. Important positive controls include an empty cross, Rime
misses and hits, original Light Foot, copy ownership, Jump height conditions,
frozen shelter after movement/removal, and real incoming Fire after a prior
Refuge cast. Native Fire52/49/56 damage becomes41/39/44; the retained miss seed
stays zero. Grid expectations derive independently from center/height geometry.

Two earlier runs retain failed test evidence:174545 used an unallocated RAM
address for a stack-owned evaluated copy;174832 had no mapped VRAM for the
icon-writer boundary check. Corrected fixtures use an explicit valid stack
container and mapped video memory. Implementation review also fixed dynamic
OBJ overlap before the accepted run. The integration code is25,800 bytes of
its32,768-byte reservation. There is no saved-schema or RAM-bank growth.

Combined acceptance and final checkpoint are recorded in IMPLEMENTATION-STATE.md.

The first combined run175037 retained three player/AI movement playback failures
and the consequent skipped dependents. Its no-field Chemist command batch took
82.8 seconds versus42.7 on the preceding candidate. The field query originally
resolved every live peer's owned record twice even when no field existed. The
follow-up resolves the verified canonical cohort's contiguous records once,
scans timer/kind before other work, and keeps independent per-peer lookup for
simulated cohorts. The new regression counts actual record-accessor calls,
requires a nonzero observed count and caps it at two per live field query.
Source and input scripts were not changed during either running suite.
The final combined candidate's Chemist native batch takes47.6 seconds on this
machine, compared with82.8 before the lookup optimization. This is elapsed test
time, not a controlled gameplay frame-rate benchmark.

The movement failure was subsequently isolated to scenario initialization.
The current ROM moves correctly from the preceding accepted fixture, while
the preceding ROM fails with the new fixture. Restoring individual movement
hooks, restoring the OBJ allocator before fixture creation, and waiting180
additional frames did not fix it. These diagnostic comparisons are preserved
in runs180418,180925 and181428; they are observations, not acceptance.
`geomancer-diagnostic` uses ignored local baseline f8d905b and isolated ROM
variants; it requires that previous candidate's local ROM/fixture. Its helper
imports the current player preparation, so after the scenario fix it compares
corrected scenarios. The retained historical reports are the evidence for the
pre-fix occupied destination; the diagnostic is not part of combined acceptance.

At the Viera's input boundary, the new fixture's enemy Hanish had already
attacked her (500 to493 HP) and moved onto the intended destination0,13.
The old fixture left him at the declared1,13 position. Party coordinates and
the native height map agreed; initiative/RNG changed the intervening enemy
turn. The game correctly rejected movement onto an occupied enemy tile.
The player scenario now establishes its declared positions/HP/statuses after
reaching the Viera turn and asserts that the destination is unoccupied before
any tested inputs. AI diagnosis tried KO spectators (182057), then living
Immobilized/Disabled spectators and a narrower target formation (182456/182835).
KO spectators triggered encounter completion; changing the remaining targets
made ordinary Fight preferable. Those scenario changes were discarded.
The final AI fixture retains the ordinary encounter and previous formation.
Its assertion now accepts either legal native attack for each route seed and
requires at least one fully observed Passing Step selection/retreat across the
fixed seeds. Every selected Passing Step still needs all preselection, route,
payment, completion and cleanup checks. Ordinary Fight must not create a route
or spend MP. Unlearned and Immobilize controls remain. This preserves a strict
positive coverage requirement without claiming the native AI must always prefer
Passing Step to Fight, which its unchanged scoring never guaranteed.

Run182057 passed both player playback checks and the existing Geomancer suite.
Its added performance observer saw zero events at the imported-symbol shim.
The revised observer resolves the actual accessor, filters the instruction
stream, and checks that the queried map cell is valid. The first full-stream
diagnostic still recorded zero instructions despite a successful returned call:
cached Unicorn translations had not adopted the late-installed hook. The next
run flushes translation blocks after hook installation. Its nonzero count and
bound remain required; the observation failure has not been waived.

Root review additionally found that timer expiry or Dispel could remove the
Jump tag without refreshing the cached native Jump byte. Those removal paths
now rebuild native mobility immediately. Consolidated checks assert restoration
of both Jump and its complement, alongside retained Light Foot/Surefoot.
Run182456 passed both player suites and the new Jump restoration assertions.
Final focused run `20260915T183000.106008Z` passes11/11 steps on candidate
`16721a362ba456abc09317d6891d45c7e4c144ee`:13,100 field assertions,62 native
executions, exactly two accessor calls per live field query both with and without
a field. AI has59 assertions: seed0 selects Passing Step and retreats to0,13;
seeds3/18 select ordinary Fight; Immobilize and unlearned controls select Fight.
The strict cross-seed positive selection requirement passes. Full combined
acceptance `20260915T183042.178475Z` passes57/57 steps with unchanged source/test
inputs, recorded in IMPLEMENTATION-STATE.md. This includes nine reaction
families with native playback and suspend/cold resume; it does not substitute
for the dedicated new field/Updraft player and save scenarios listed above.

## Terrain research carried forward

The native height header02007F10 stores its grid pointer at+4 and **byte** width
at+8. Tile records are two bytes: native1CC18 reads height;1CD08 reads flags;
flag2 supplies water and the other examined flags control traversal. They do
not establish grass, stone, wood or snow. Do not assign those meanings to
unverified flag values.

[FFTAUtils's map editor](https://github.com/spiiin/FFTAUtils/blob/0283a3d0faf0b82fd47fa9e71a8e5700e28f879a/FFTA_MapEditor/Form1.cs)
and [its map-table utility](https://github.com/spiiin/FFTAUtils/blob/0283a3d0faf0b82fd47fa9e71a8e5700e28f879a/PrintMapsParams/Program.cs)
document a useful rendering/annotation route:163 map records,0x58 bytes each,
table base569104, with graphics/arrangement/clipping/palette/height offsets
relative to that table. Height containers include packed and compressed forms
and map aliases. Its rendered height overlay labels ordinary, impassable and
water cells, supporting the distinction from visual materials. The downloaded
source is ignored at tools/ffta-map-utils, commit0283a3d0f; it is research input,
not a new runtime dependency or a verified complete material catalog.

Next terrain work should decode and render the local ROM reproducibly, annotate
actual visible materials, and bind annotations to validated map identities and
coordinates. Keep unclassified tiles neutral and Wind always available. Do not
silently make affinity bonuses unavailable everywhere or infer materials from
movement flags. Torrent's whole-cast direction and Gaia Surge's element choice
must also have native selection/preview/AI transport before job completion.
