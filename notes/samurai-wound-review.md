# Higanbana implementation checkpoint

Private candidate `d7d6e31967d9a4627c08542d96f059bb499fb03e`, based on accepted
assembled ROM `ba1c33ea4191abd74d346cc2d22dc39e5d1df1b7`. The player launcher,
ROM and save are unchanged. This is an implementation checkpoint, not acceptance
of the full Samurai suite or the complete expansion.

Higanbana355 now uses the native physical executor, costs8MP, requires the
primary katana and deals0.80P. Its initial-hit reference is captured before the
combined final damage modifiers, using the same native variance sample.
An explicit44-byte stack scope owns the actor, target, action, result object
and exact recipient row. The private root occupies0203FF44..48. Nested
executions push a separate scope; queries cannot arm it; readiness is consumed
once, and closure erases the scope and restores its predecessor.

Wound application waits for an actual positive HP loss. Misses, Damage-to-MP,
restorative hits and immune targets cannot replace an existing wound. Lethal
damage clears it. The stored pulse is floor(P/2), with two remaining pulses;
Centered and Exposed change the initial damage but do not enlarge this snapshot.

`20260915T010213.812762Z/report.json` passes the native executor and lifecycle
checks on this exact private candidate. These include complete EWRAM comparison
for358 original/previously enabled actions, nested/query/reference ownership,
128 fixed initial-hit combinations, all36 canonical owners at both stack
alignments for KO and native status writers, full native broad-remedy dispatch,
job changes, scripted KO and battle-end cleanup. Each lifecycle differential
allows only the intended wound record to differ from the original operation.

The additional initial-hit run `20260915T011034.820285Z` passes192 combinations,
adding Protect to the native-P snapshot cases and restorative weapon healing.
The7346 lifecycle assertions remain applicable because no application code
changed between these runs.

Actual Higanbana selection, preview/cancel and commit pass in
`20260915T010934.252862Z/report.json`. The script equips Red Spider Katana446
from the registry, masters lesson152, and uses actual menu/Move/target inputs.
A native-P control and the unmodified candidate use fixed seeds. Hits and
misses verify the one-round initial coefficient with Centered/Exposed, exact
floor(P/2) wound replacement, one8MP payment, consumed Centered, unchanged
AP/inventory and no extra native RNG sample. The test initially equipped384,
which is not a katana; the failed payment assertion caught that fixture error.

The pulse implementation has a separate end-turn phase127 in the native battle
interpreter. Its private periodic phase42 uses the existing native damage-number
display, wait phase35, death-handling phase6 and finish phase39. Both interpreter
tables retain every original entry. There is no new Poison flag, native Poison
calculation, random sample, attack, reaction or weapon proc in that path.

The prior pulse candidate `ae3a381850fd7c0aab5a64aa318a7d4014c1943b` passed actual
Wait-input scenarios in `20260915T005938.255900Z/report.json`:100HP becomes89
at the first affected turn ending and78 at the second; five intervening turns
do not pulse. A lethal11-point pulse clears native statuses and returns to the
next unit's menu. A zero-point pulse retires the schedule without HP loss.
The current candidate adds lifecycle hooks. Its repeated pulse checks pass in
`20260915T010325.015707Z/report.json`, including complete EWRAM equivalence for
ordinary Wait with no wound. Native suspend after the first pulse and a fresh
emulator cold Resume Battle preserve89HP, one11-point pulse, AP and inventory;
the next affected turn ending applies only the remaining pulse.

`20260915T011141.335387Z` extends that same actual-Wait suite: Protect and Shell
plus Exposed/Centered leave each fixed11-point pulse unchanged, and native
Poison still ticks on its separate schedule without consuming a wound pulse.
The five scenarios, ordinary-turn differential and cold suspend/resume pass.

The reproducible checkpoint is
`build/expansion/checkpoints/samurai-d7d6e31967d9a4627c08542d96f059bb499fb03e`.
Its `evidence.json` reconciles four focused suites against unchanged application
sources, exact test/helper hashes, matching ROM hashes and complete log hashes.
This reuses passing evidence instead of repeating unchanged tests. It is not a
full private Samurai acceptance record.

## Native periodic damage correction

The earlier identification of status12/CD9BC as Poison was incorrect. The
native Poison Claw effect61 sets status9 viaCDE38; getterCD974 reads E9 bit02.
Native Poison executes in9ED38 phase5 at9F4AE, obtains a randomized max-HP-based
amount from1303AC, writes/clamps HP at9F500, displays the number viaA92E4 and
continues through phase35 to death handling. The read-only native trace plus
fixed-input battle cases are retained under the89855f5a candidate's
`native-periodic-trace` directory and run `20260915T005506.633456Z`.

That trace shows no Poison loss immediately after the affected unit's Wait;
loss occurs before its following command turn after five other friendly turns.
Blade Wound therefore must not piggyback on the ordinary Poison schedule.
Its separate end-turn phase preserves the approved timing. The9F642 path is
an ability5 revival path, not Poison damage.

## Remaining acceptance work

Higanbana's complete law/AI classification, native reference bounds and exact
outgoing-bonus exclusions still need acceptance. All nine actions need concise
in-game help. Additional reaction-interception cases for fixed pulses remain
useful before integrating the private work. Inoculation and the Samurai
supports/reactions remain future shared/gameplay features.

The status display and the complete declared25-step private regression now
pass on bf941, as recorded below. The old eight-action UI fixtures have been
rebased; they are no longer an outstanding blocker.

All testing is deterministic scripts through the declared test plan. No testing
agents are used; final council review remains after full implementation.

## Wound display follow-up

Private candidate `bf9414aaa75f28c950091d6edf83e1bc98864f97` adds visible key27
and a three-cut icon in two newly reserved graphics tiles. The old icon getter,
cycle and graphics routines remain bound to the accepted main implementation.
The inline C-call hooks now preserve R12; this fixes the actual register
clobber found by the renderer differential. This shared assembly source change
has not been rebuilt into the accepted main ROM.

Run `20260915T012527.786958Z` passes both focused display suites. They cover
all65536 Wound encodings, both stack alignments, old selectors and renderer
registers/frame/RAM/graphics, exact new tile writes, four-status coexistence,
expiry, native suspend and fresh cold resume. The mixed-cycle test calls the
complete native renderer: its caller rearms the internal state machine after
fade-out. Calling only the inner cycle function omitted that required step.

Older gameplay scenarios are being rebased to allocator-aware native wrapper
lookup. The new display also changes encounter RNG timing during fixture
creation. Fixed Giza scenarios now declare their starting unit coordinates and
native heights explicitly before inputs. They do not inject attack results,
movement outcomes, damage or save contents; all subsequent gameplay is executed
by the native engine. This prevents a changed random enemy deployment from
silently blocking the replay's Move destination.

## Complete declared private regression

Runs `20260915T013004.025595Z` (17 selected steps) and
`20260915T013524.415104Z` (12 selected steps) cover all25 distinct steps in the
declared Samurai suite. Every step passes, and the runner confirms no changed
inputs within either run. The reconciliation also verifies identical source,
harness, engine and base-ROM fingerprints between runs, exact step commands,
private ROM hashes in applicable logs and retained log hashes.

The checks include native execution/preservation, all nine actions through
actual battle input, fixed-seed hits/misses, Centered/Exposed composition,
Counter timing, healing and undead restrictions, line/cross recipients,
Silence/Reflect behavior, existing law contracts, wound ownership/lifecycle,
two scheduled pulses and lethal cleanup, Poison coexistence, exact status
rendering, and native suspend/cold resume. Auxiliary record-layer and native
Poison controls are included among the25 steps; they are not additional
implemented features.

The frozen checkpoint is
`build/expansion/checkpoints/samurai-bf9414aaa75f28c950091d6edf83e1bc98864f97`.
Its `evidence.json` and `build/expansion/samurai-bf941-regression-coverage.json`
record the reconciliation. It is split-run coverage of declared tests, not a
claim that pending requirements above have been tested, a final council review,
or completion of the whole expansion. The accepted main build and player
launcher remain unchanged.
