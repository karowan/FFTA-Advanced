# Native controller costs and rejected compact leaves

Full engineering remains required. Only final artwork content is deferred.
E01-E05 remain open. All runners below are terminal. Installed7507ca5c,
defaultfa3d12b4, private action-completion selector5a14e6c7 and player files
are unchanged. The compact candidate is not approved for delivery.

## Remaining generic weapon families

Runner20260919T024233.137603Z passes all eight selected checks on private
5a14e6c7b69f9f9984a6965faf5740d3b318e41a. Each passes4916 assertions with
actual Fight menus,608 every-frame body/palette observations, positive damage
and return to the next turn. Reports are under build/art/class-fight/:

| Test ID | Report directory | Weapon | Damage |
|---|---|---|---|
|test-human-dk-knightsword|20260919T024233.889086Z|52|27|
|test-human-dk-greatsword|20260919T024252.404479Z|62|29|
|test-bangaa-dk-knightsword|20260919T024311.022454Z|52|25|
|test-bangaa-dk-greatsword|20260919T024326.974398Z|62|27|
|test-numou-chemist-staff|20260919T024343.017541Z|149|16|
|test-geomancer-staff|20260919T024400.503052Z|149|16|
|test-dancer-rapier|20260919T024418.217342Z|88|20|
|test-mystic-knight-saber|20260919T024433.898380Z|32|20|

Together with the prior seven flows and three corrected Moogle/Bard flows,
these establish18 of20 generic job/weapon pairs on the unchanged or preserved
graphs. Samurai/Viking have historical actual action evidence that still needs
pointer-following reconciliation with the current candidate. Raw Samurai table
pointers differ; that alone neither invalidates the graphs nor proves reuse.
Auxiliary weapon/effect actors are recorded, not independently accepted here.
Combo, secondary actions, water attacks, UI and capacity remain separate gates.

## Compact scoped-leaf experiment: rejected

The optional --compact-leaves experiment uses Thumb -Os instead of ARM -O2
for the exact same scoped C leaves. The fused leaf shrinks from832 to552bytes
(560 padded), and publication304 to160. Static stack and interrupt reserves,
position-independent extraction, interworking and ROM fallback remain checked.
The copy wrapper must clear a Thumb function symbol's low bit, then set it on
the copied entry. The first ownership run failed UC_ERR_READ_UNMAPPED because
the source bit was not cleared; that failure is preserved, then fixed.

Corrected runner20260919T024815.042270Z:

| ID | Result | Report |
|---|---|---|
|test-art-compact-owners|17068 pass|build/art/palette-owners/20260919T024815.714763Z/report.json|
|test-art-compact-plan|488 pass|build/art/frame-high-slots/20260919T024818.045336Z/report.json|
|test-art-compact-build|8 pass|build/art/performance/compact-leaves/20260919T024818.896100Z/report.json|
|test-art-compact-consumers|244 pass|build/art/fused-consumers/20260919T024833.733558Z/report.json|
|test-art-compact-entry|failed paired nativeShadow|build/art/live-palette/battle/20260919T024834.841068Z/failed.json|

The initial runner20260919T024732.516011Z stopped at ownership; four later
checks were skipped. Its failed capture is at palette-owners/20260919T024733.135465Z.
The corrected entry failure also skipped its remaining assertions.

Final compact SHA1 is5a65d27a70da61e790e4d0fcc4d99c662161ce0a, including the
Moogle completion stage, and stays under the private compact-leaves selector.
complete-generated-actions.build(publish_current=False) permits this experiment
without replacing the accepted-for-further-work5a14e6c7 selector. No RAM added.

test-art-compact-frame-events passes31122 at
build/art/native-frame-events/20260919T024939.899355Z/report.json, SHA256
1c9b7f5aa371fe7379051f0690cc06cea5173df62d30c27860e7218c7d332af8.
All1024 ordinary/observed frames and full states agree; current demands are
independently audited. Nevertheless the owner helper takes5.25-5.51scanlines,
slower than ARM's4.51-4.69. Smaller copied code did not compensate for execution.

Runner20260919T025124.176529Z passes test-art-compact-phase6226, then fails
test-art-compact-response with six metrics: Move start/end+1 at idle0 and+2
at idle4; cancel start/end+2 at idle4. Move duration47 matches. Reports:
build/art/native-phase-evidence/20260919T025125.012108Z/report.json and
build/art/response-budget/20260919T025125.507120Z/failed.json. No waiver.

Default ARM reproduction is independently checked without native execution:
build/art/performance/compact-default-proof/20260919T025839.987336Z/report.json.
All four leaf blobs/stack proofs match original e1a87ecd. Complete wrapper
object text and relocation records are identical; text SHA256 is
ce524142a45634c85e9b832d310735b5f9a7690d2cd95f01caabe9d1819d78eb.
The rejected option is isolated; default scalar ARM remains byte-exact.

## Actual native controller profile

scripts/art_controller_costs.py authenticates the battle controller's bounds
08092784..08096B28, actual Thumb BL encodings and full body hash. It observes
executed direct external calls and matching returns, including consecutive
call/return sites, checks restored stack pointers and rejects unfinished pairs.
Local branches to the common epilogue are excluded. Shared return arrivals
without a call are counted separately. Costs include interrupts and descendants;
they are not exclusive CPU costs and nested values must not be added together.
Indirect calls and individual descendants are outside this profile.

test-art-controller-costs passes27027 in runner20260919T025555.937953Z:
build/art/native-frame-events/20260919T025556.652652Z/report.json, SHA256
261012ca25b24679c35110bd42a9fa2702d5dd1af82c24f610b6fa489a599802.
The observed ROM is e1a87ecde67f265f666d3ab9d7e50ba401370633, using its exact
retained scene. Complete ordinary/observed state/framebuffer equivalence and
current-input audits pass. This adds profiling, not performance acceptance.
An initial pre-emulation failure in runner20260919T025518.900859Z omitted the
required --composition-costs flag; the guard was preserved and the plan fixed.

| Action / caller -> callee | Active idle0 / idle4 | Bypass idle0 / idle4 |
|---|---|---|
|Cancel 08093BF2 -> 0809A5E0, one call|9.265 /9.082 video frames|8.417 /8.341|
|Cancel 08096996 -> 08098A88, five calls total|4.157 /4.350|3.666 /4.141|
|Move 08093638 -> 0801D624,154 calls total|3.992 /3.194|3.790 /3.650|

Static follow-up shows9A5E0 queues callback08097814 through148860 and runs the
native priority work list through148914. Do not call this a busy wait or an
intentional nine-frame delay without tracing that callback. Native98A88's
movement-display loop repeatedly resolves a wrapper property and tile
occupancy;1D624 builds tile geometry. Side effects and dependencies need proof
before hoisting or replacing any work. These are concrete next profiling leads,
not evidence that the regression is unsolvable or permission to change gameplay.

Next inspect the callback/work-list and movement-display consumers, preserving
native results and actual paired response acceptance. Reuse existing passing
graphics evidence. E01-E05 stay open; no broad integration was justified here.

## Callback follow-up: repeated empty field queries

The callback at97814 is already hooked by the gameplay expansion. Its native
entry branches to ffta_geo_tile_entry, which runs the original tile builder
and then Geomancer's Rime/Surefoot cost rules. The additional observer option
--movement-costs authenticates five compiled function regions against gameplay
parent1b070824 and the exact installed hook. It measures their actual direct
calls and return values, with no emulated code/state edits.

test-art-movement-costs passes27027 in terminal runner20260919T030913.394203Z.
Report: build/art/native-frame-events/20260919T030914.089073Z/report.json,
SHA2567749287b71fad9b43f4ece72e83842c1862d9bddfaa8aea790beafe671f8748a.
All ordinary/observed frames and complete states still agree. It profiles e1a87ecd
and its same-ROM compositor bypass, using the unchanged retained input scenario.

Cancel performs257 tile callbacks. Of those,150 enter the field-membership
query; all150 return zero in each of the four branches. Inclusive costs:

| Cancel consumer | Active idle0 / idle4 | Bypass idle0 / idle4 |
|---|---|---|
|ffta_geo_tile complete257 calls|6.367 /6.295 frames|5.669 /5.979|
|Original native tile builder,257 calls|1.267 /0.981|1.215 /1.250|
|ffta_geo_field_at,150 calls|4.466 /4.359|3.820 /3.632|
|Its ffta_job_peers,150 calls|2.320 /2.277|1.612 /1.849|
|Its second bank accessor,150 calls|0.680 /0.324|0.324 /0.323|

These are nested values, not additive. Interrupt timing affects each inclusive
interval. Zero query results do not prove an empty global field bank; they prove
that no field matched these actual queried tiles. The source constructs the
canonical36-pointer peer list for each query, resolves its bank, then scans
records. Independent evaluated cohorts correctly take their own lookup path.
The older geomancer-fields.md optimization reduced per-peer accessor calls but
retained per-query peer-list construction. No gameplay optimization was made
in this profiling checkpoint.

A bounded next candidate can avoid constructing the canonical peer list while
retaining authenticated live-bank access and the existing independent-cohort
fallback. Prefer current-query validation over a persistent cache. Before
acceptance, compare complete field/grid results for live and copied cohorts,
invalid/unowned units, both field kinds, overlap, timers, caster incapacity,
height, allegiance, Float and Surefoot. Then measure actual Move/cancel at the
same offsets. This proposal is not a proven fix; E01-E05 remain open.
