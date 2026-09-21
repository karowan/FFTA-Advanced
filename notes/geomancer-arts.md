# Geomancer remaining arts implementation

This records the current implementation batch and its acceptance boundaries.
The approved behavior remains in `JOB-CLASS-SPECIFICATION.md`.

## Native commands

All nine Geomancy actions now have owned command records. Stone Pulse uses
Earth damage with a rock multiplier; Tanglevine adds native Immobilize after
positive HP damage; Torrent carries one cardinal direction through the native
command operand and uses the native legal displacement planner. Earthen Ward
applies native Protect and a separate timed displacement immunity. Wisp Flame
applies weak or strong Exposure after positive damage, with existing custom
status prevention and cleanup. Rime uses Ice damage and a gated native Slow
stage. Gaia Surge carries a selected local element through the same native
operand. Existing Updraft and Refuge retain their owned implementations.

The native element IDs are Fire1, Wind2, Earth3, Water4, Ice5, Thunder6, Holy7,
Dark8. This batch corrects Rime's earlier record from Earth3 to Ice5; the prior
field acceptance did not establish elemental correctness.

Torrent and Gaia rows share one AP lesson per command. The selected value is
not an equipment index. Expanded menus remain within the existing22-row
capacity. The Dancer choice hooks now carry all three explicit-choice commands.
Native AI alternate-choice enumeration and actual Geomancy player playback
remain separate acceptance work.

The native-menu batch checks affinity after ordinary Move. Source
review shows `dancer-choice.c` obtains Gaia options from the active unit,
while `geomancer-arts.c` reads that unit's F6/F7 coordinates. The accepted
`test-dancer-choice-playback.py` observes that native Move updates the live
wrapper first and A433C synchronizes F6/F7 later. This is a concrete stale-menu
risk. The candidate resolver uses the active wrapper only when the selection
manager is in modes 6..11 and both manager and wrapper own the exact unit
pointer. Other units and copied AI candidates retain their own coordinates.
It writes neither unit/AP state nor RNG. Native ownership, bounds and copy
controls extend the arts suite.

`test-geomancer-playback.py` declares a real Nu Mou turn, ordinary Move from
(0,14) to (0,13), then all sixteen expanded Geomancy rows at three fixed seeds.
A private material tile at (0,12) distinguishes the old and displayed
neighborhoods. All nine actions, four Torrent directions and five Gaia choices
must reach native preview, execution and subsequent rendered turns. The
candidate and instrumented ROM hashes remain separate. Run `geomancer-player`
through the integration plan; acceptance evidence follows below. This is player transport
coverage, not AI choice search, thematic animations, law or cold-save acceptance.

The first complete playback pass found that Refuge's all-inert descriptor
vector could not pass the native B4C90 target filter. Direct execution had
bypassed that player gate. Descriptor 236 now supplies the existing owned
eligibility route, Sure accuracy, zero magnitude and the shared harmless
application 96. Field placement still occurs once from the completed action
object, independently of recipients. The expanded playback includes empty
crosses for Rime and Refuge and checks the resulting field center and kind.

Empty-center playback then exposed B5920's eligible-recipient requirement at
the native B780A/B76AE player call sites. The installed entry retains the
original helper for other calls. These two calls may accept Rime/Refuge's
selected center only with exact active wrapper/manager ownership, matching
action and cursor, selection stage 0/1, a valid native tile, and membership in
the existing native legal range/cross list (at most 25 cells for these r3 arts).
No recipient is inserted. Ordinary native range, MP, preview and confirmation
flows remain in place. The focused placement run `20260915T224857.688835Z`
passes 12/12 steps on candidate `1b83cd2b641bb41138447862ae44deb985fbbb0a`,
including occupied and empty casts of both fields at three fixed seeds.

`test-geomancer-selection.py` adds native helper differential checks across
all 347 original actions and both stack alignments, plus read-only ownership,
caller, lifetime, list, stage and cursor guards.

### Player integration acceptance

Candidate `1b83cd2b641bb41138447862ae44deb985fbbb0a` passes all 54 declared
player casts in `20260915T230352.387751Z` (17/17 affected-suite steps).
The playback report passes 1,873 assertions, including all nine arts,
four Torrent directions, five Gaia elements, and occupied/empty casts of both
fields at seeds 0, 3 and 18. All casts follow native Move, selection, forecast,
confirmation, execution, rendering and next-turn inputs. Empty fields have
zero recipients, the intended center/kind and one MP payment. Menu learning
and inventory/AP remain unchanged. Root inspected native menu and empty-field
confirmation captures. This does not certify thematic animations or outlines.

The selection report passes 870 assertions: all 347 original actions at both
stack alignments preserve return values, EWRAM effects and RNG; the field
override passes exact-owner, caller, lifetime, list and cursor controls.
Arts pass 1,410 assertions and 456 native executions. Integration code is
29,048/32,768 bytes. The new native entry replays the original B5920 prologue
before continuing at B592C; the wrapper preserves the fifth argument, caller,
high registers and both stack alignments. Descriptor 236 fits below the
application reservation and uses the existing harmless callback 96.

Combined run `20260915T225325.151057Z` passed the 61 existing steps, then
failed before executing the new selection test because its fixture-loader
split matched a quoted string. Playback was skipped. The corrected affected
suite above passes both outstanding checks and their dependencies on the
same ROM. Both reports have `inputsUnchanged=true`; input-manifest comparison
finds only `scripts/test-geomancer-selection.py` changed. All 63 combined
step IDs therefore have passing evidence on this candidate. Retain the failed
report as failed; this is composed evidence, not a single green combined run.
The earlier script-selection and real native placement failures are retained
with their original reports. No new agents or interactive gameplay were used.

## State and storage

Wisp uses the previously reserved high3 bits of job-state byte17 and bit0 of
byte18. Steady uses byte19 low3; preserve the high5 movement-ledger bits.
Timers and copy ownership use the existing schema2 machinery. There is no
new persistent RAM or saved-record size. Frozen Wisp flags occupy extra
snapshot bits16/17. Status icons39..42 use OBJ tiles1FC..203, with the native
dynamic graphics allocator moved to204. Native rendered regression remains
required after extending that boundary.

## Terrain catalog

`notes/terrain-materials.json` covers all 162 native maps. The builder emits
an immutable163-map,256-cell material table at ROM offset11F0000. Masks are
rock1, vegetation2, water4, wood/heat8, snow/ice16. Explicitly neutral cells
contribute no material. Native water detection independently contributes water affinity.
All arts keep their baseline behavior without material affinity.

The current reviewed catalog contains 162 map records and 21,625 annotated cells.
`terrain-decoder.md` documents source rows, reviewed overlays, native projection
verification, and the separate `terrain-campaign` acceptance suite. The
builder rejects a missing native map. Neutral sand, fabric, unresolved furnishings
and scene borders remain deliberate content decisions. Mixed wetland vegetation
uses existing bits 6; no new engine factor or save field is introduced.

The focused tests supply explicit masks on a private flat board. Those inputs
exercise the rules; they do not establish campaign terrain correctness. Static
inspection confirms the native identity:19FCC loads table08569104,19FD0 loads
02007F10,19FD2 reads its first halfword, and19FD4..19FDA multiplies that ID by
58hex and adds the table base. Each annotated map still requires a check
against its rendered geometry before filling the catalog.
Do not infer grass, rock, wood or snow solely from height or movement flags.

## Deterministic acceptance

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite
geomancer-arts` after completing the batch. This includes affected native
Geomancer, Viking and Dancer choice checks. Each report retains the assembled
ROM hash, declared scenarios and output. Run `combined` on the final assembled
candidate after resolving related failures together.

Current unaccepted scope includes appropriate
action animations, field outlines, native player and AI choice execution,
law prediction/penalties and dedicated field/Exposure/Steady cold-save playback.
A green command contract does not complete those gates or the whole expansion.

### Renderer research for the next batch

Static inspection of the clean USA ROM finds valid graphics/arrangement/
clipping/palette/height pointers for IDs0..161. The older utility's count163
includes ID162, whose arrangement pointer resolves outside the ROM. Do not
decode that entry as a map. The current reserved material table has163 slots;
the extra unannotated slot is neutral and is not evidence of another map.
Valid graphics containers comprise82 type20 and80 type22 entries. Arrangement
containers comprise116 type11 and46 type1; clipping161 type11 and1 type1;
height159 type11 and3 type1. Resolve each component's aliases independently.

FFTAUtils `Form1.cs` gives useful rendering references: lines382..436 describe
arrangement runs; lines439..465 pair8px tiles into16x8 strips; lines593..624
unpack height runs; lines628..684 project the height overlay. On that reference
canvas the derived tile-top center is `(256+16*(x-y),264+8*(x+y-height))`.
The subsequent native decoder/projection comparisons accept this formula;
see `terrain-decoder.md` for evidence and the partial reviewed material catalog.
Preserve foreground/background layers
and animation tile offsets so transparent water or foliage is not mislabeled.
The graphics stream's type22 adds an extra four-byte header before the custom
LZSS stream. The editor has incomplete type10/type12 branches; actual clean
map graphics above do not use those branches.

## September15 command acceptance

Candidate `7af41803aeaa1e566d166d796a65af865f0212e4`, shared base
`473cf0f4546cabb55ce614abe84f8536a947847a`, passes17/17 focused steps in
`20260915T191044.689812Z`. The arts report has1,327 assertions and456 complete
native executions. It covers all nine command costs and native magic flags,
positive/missed damage, Immobilize/Slow, terrain-height boundaries, all four
Torrent directions with legal/occupied controls, selected Gaia elements and
Attunement refunds, Wisp damage/weak-refresh/prevention, native Damage to MP,
Tanglevine with War Cry, Steady compatibility and expanded AP menu rows.
Existing field, Geomancer passive/reaction, Viking and Bard checks plus
rendered Dancer choice playback pass on the same candidate.

The failed precursor runs are retained. They identified Ward recursion through
the relocated application observer, missing native magic classification,
and the old Dancer-only expected branch in a shared choice test. Native magic
classification is distinct from the expansion's Magic sequencing category;
testing only that category would have missed the absent damage modifiers.

Full combined `20260915T191211.585109Z` passes58/58 steps with
`inputsUnchanged=true` on the same7af41803ae candidate. The runner's top-level
ba1c33ea hash is the prerequisite fixture base, not the assembled candidate.
The reaction playback includes native suspend/cold resume; dedicated saves
containing the new Geomancer states remain separately unaccepted. Root's
source review covered the application observer route, explicit choice ABI,
single-rounding modifiers, reserved state bits, lifecycle masks, native table
and icon bounds. Integration code occupies28,648 of32,768 reserved bytes.
No new agent or council was started.
