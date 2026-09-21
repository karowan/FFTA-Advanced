# Complete sequence transport and open battle entry failure, September17

Status update: the apparent Fight-entry failure below was test setup and is
resolved without ROM changes. Actual paired Move/Fight now passes8,131 checks;
see native-action-battle-proof.md. The historical failure evidence remains below.


Private candidate `714f45eb9997ad39d11b13f92c35d5b0de1a0e7f`, resolved through
`build/art/generated-actions/current.json`, extends portrait candidate75029dea.
It is not packaged, installed or accepted for battle playback.

## Implementation and passing bounded proof

`scripts/generated_action_transport.py` appends all twenty owned resource
descriptor tables to a dedicated blank-FF reservation `1e80000..1f80000`.
It uses116,244 bytes. All770 present non-idle land/water descriptor slots point
to temporary generated poses; existing land idle descriptors remain byte-exact.
Null slots, frame counts, durations, command bytes1/2/8 and all five metadata
words remain unchanged. Only new tables and the twenty owned animation table
pointers change. Original jobs/resources and previous portrait/grid/miniature
code and data remain byte-exact.

This deliberately repeats authenticated imagegen idle poses through action
sequences. Water uses their upper20 pixels. No swimming, walking, attacking,
downed or other finished pose is authored or claimed. Each replacement has a
single32x32/16-tile layout, within the original allocation. Its opaque bottom
aligns to that particular original frame, not the old OAM rectangle edge.
The metadata records source frame, selected draft, crop, tile/OAM hashes and
baseline. Palette allocation remains unchanged and unfinished.

Declared `test-generated-actions-native` passes26,640 checks in runner
`20260917T213913.243435Z`. It verifies all mode/null selections, unchanged idle
descriptors, exact command/timing/metadata, tile/OAM bounds/baseline and rebuild.
It recreates real native widget actors for all1,580 supported mode/facing pairs
using authenticated retained menu RAM only as an isolated allocator context.
This does not run complete sequences through a live battle renderer.

## Failed actual battle proof: keep open

`test-generated-actions-battle` uses the shipping authenticated pre-deployment
world seed and native Giza route. Six same-race generic appearance/job/legal
equipment profiles are set before actors are constructed: Samurai, Bard, Human
Dark Knight, Viking, Nu Mou Chemist and Dancer. Stats/initiative are preserved.
The first native turn is slot3, Bangaa Viking. The intended paired check is
native deployment, Move, Fight and next-turn return on75029dea then714f45eb.

Both attempts fail on the **baseline75029dea before714f45eb is executed**:

- Runner214236.390277Z, capture214236.920923Z:3,907 checks before a next-menu
  timeout. Deployment and Move reach actual UI; the target remains250HP.
- Runner214507.237020Z, capture214507.760905Z: same failure, now with every
  Action selection step and final `.state`, `.ram`, `.iwram` and screenshot.
  No input or ROM changes between these attempts; the second adds diagnostics.

All paths are under `build/art/generated-actions/battle/` and the normal
ignored runner reports/logs. The source seed and player saves are untouched.

Observed state, not a confirmed cause:

- `baseline-action-stage0.png`: Action menu correctly shows Fight/Reaving/Item.
- After selecting Fight, the menu disappears. The command manager at0202d940
  remains state byte+4=5 with first word=1, through the long wait. It never
  reaches a forecast or weapon execution. Extra scripted inputs have no effect.
- The sampled Viking actor stays resource260/mode3 (idle), and the intended
  target remains250HP. Thus this has not established an attack-animation stall.
- Native renderer IWRAM6170..6d68 remains byte-exact to ROMa38d24..a3991c.
  The reserved D7 memory guard remains intact. These facts do not rule out a
  different graphics allocation or task-state problem.

Next isolate the earliest failing stage with the same declared profile and
fixed inputs: shipping1b070824, generated-class595782ba, portrait75029dea, then
action714f45eb as relevant. Capture the Fight-entry state without repeating
the full long timeout. Distinguish a profile/input issue from a wide-resource,
portrait/battle-HUD, or other runtime regression before changing game code.
Use the declared runner and announce the focused diagnostic test ID first.
The failed state is reusable for bounded native inspection; do not discard it.

Remaining technical gates also include real water transitions, all affected
action/weapon consumers, custom actor palettes, equipment/effects/status and
assembled delivery. Final sprite artwork stays deferred per latest instruction.
G01-G04 remain open. No external generation, council, publication, player-game
launch, or incident-note access occurred.
