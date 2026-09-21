# Composure and Follow Through integration

September 16 follow-up: the prospective AI movement question is resolved in
`notes/ai-movement-policy.md`. Native planning policy is preserved; actual
movement and public-preview boundaries have current deterministic coverage.
The pending lists below retain this earlier batch's historical scope.

This batch implements the two approved movement-sensitive supports in the
assembled image. It does not complete the whole expansion, prospective AI
movement scoring, all law/AP/acquisition flows or every Combo presentation.
The primary agent owns implementation and review; all tests are scripts.

## Native movement evidence

The original bit4 at02001F70 is a command-spent flag as well as a Move flag.
Wait at08095671 and AI command completion at080937C3 set it without proving
voluntary movement. Those callers cannot grant Follow Through or disable
Composure. The native no-path/one-node completion at0809674D is also excluded.

Both player and enemy AI movement completion reach the flag setter with return
address080968D3. At that exact point the current wrapper at0200F4EC contains
the destination, while the unit's F6/F7 may still contain its pre-move tile.
The traces show player distances1 and2, and multiple enemy moves. Native undo
restores the wrapper and enters08096343 with value0. One B returns to the Move
selector; the second B returns to the ordinary command menu.

The original cursor-origin fields at0200F3C0/F3C4 are not assumed to prove an
arbitrary actor's turn start. The previous 0200F4E8+30 interpretation was wrong:
it yielded zeros in the trace. Explicit owned state records the tile when the
existing native turn-start lifecycle identifies the actual unit instead.

The retained initial traces are `20260915T102542.822391Z` and
`20260915T102644.018468Z`. They stopped on incorrect fixed menu navigation,
after preserving the meaningful movement/AI observations in the latter's
partial report. An earlier `102437.210253Z` stopped before play on a mistyped
expected opcode (native ADD bytes are9B18). The final trace uses the production
movement consumer behind its logging wrapper and verifies actual owned state.

## Owned state and arithmetic

Bytes12/13 hold the turn-start X/Y; byte14 holds active1, completed voluntary
movement2 and Manhattan displacement at least2 tiles4. Turn end, KO, Petrify,
job change and battle end clear this domain. Dispel, remedies and equipment
changes do not erase movement history. The existing exact-owner copy/save
machinery transports these bytes; there is no character-name/ID lookup back
to live state. These offsets are preserved by the schema2 storage migration described in
`remaining-state-capacity.md`.

Composure requires the native equipped Human support, an active own turn,
no earlier uncancelled voluntary movement and no Confuse/Charm. It contributes
25/20 to direct physical/magical HP damage and eligible direct restorative
healing. Follow Through uses the equipped Bangaa support and an active turn
with a completed move ending at least2 Manhattan tiles from its starting tile;
it contributes27/20 only to direct physical HP damage. Neither support requires
an axe/katana. Different supports cannot be equipped simultaneously.

Eligibility is frozen into legacy snapshot bit15 for Composure and extra bit7
for Follow Through. Later movement, copied actors and later live state changes
cannot retroactively change the current action. Native reaction origin,
Confuse/Charm, MP redirection, items, drain recovery and revival are excluded
at their appropriate effect paths. Percentage Murasame healing combines
Centered, Composure and incoming Recuperation before one rounding; ordinary
native HP restoration combines Composure and Recuperation before one rounding.
Combo contribution retains the original incoming Exposed/Poise formula and
excludes both new outgoing supports, including during the actor's own turn.
Explicit Combo action contexts and native action265 are excluded. Detailed
Combo playback remains a separate gate.

Both native support descriptions are installed in root help bank12D0000..DFFFF.
Independent job builds remain prerequisites and do not implement these root
consumers merely by having allocated lesson IDs.

## Acceptance work

Run the consolidated deterministic plan from the repository root:

```powershell
.\Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Suite combined
```

`test-integrated-turn-supports.py` exercises real equipped supports, exact
rational stages, complete native actions, callback admission, healing mixes,
frozen/copied state, lifecycle clearing and effect exclusions.
`trace-turn-admission.py` drives fixed native Move/undo/Wait paths for actual
Human and Bangaa units and observes native AI turns.

The first46-step combined run is `20260915T103614.963102Z`. Its original-action
differential found that native action101 now clears the newly allocated turn
record on its lifecycle path, while the older baseline retains previously
unused bytes. The original-action compatibility comparison must initialize
this new domain empty in both inputs, leaving every output byte compared;
the dedicated turn-state test separately checks active-domain behavior. The
comparison must not mask those bytes in outputs. That correction and the fixed
Move/undo navigation passed all11 affected steps in `20260915T104422.951940Z`.
The native action matrix uses actual legal racial commands and weapons:
Human Soldier/White Mage/Black Mage/Samurai/Dark Knight, and Bangaa
Bishop/Gladiator/Dark Knight. In particular, Fell Cleave uses axe399, not the
unrelated rapier400. The matrix executes240 actions across both supports,
three movement distances, enabled/disabled controls and four fixed seeds.

The extended trace in `20260915T104634.467619Z` also passed actual AI
stationary/moved action-state checks and two native suspend/cold resumes.
Native suspend follows returning to the free cursor, cancelling an
uncommitted Move. Both resumed units correctly retain that undo state and
their original HP/MP, AP, inventory and cleared transient roots. The trace
delegates flag operations to the production consumer and never injects a
movement record. It logs the exact owned state at actual AI action entry.
That run's last step stopped in the newly appended help check because its
baseline path omitted one parent directory; the240 native actions themselves
passed. The help path is corrected. Final combined results are pending.

The first combined continuation, `20260915T104825.345200Z`, found two more
copies of the old inactive-domain fixture in Chemist and Blood Edge's full
executor comparisons. Their complete retained differences are the same
three turn bytes for action101; these inputs need the same explicit empty
new domain rather than any output masking.

The Dark Knight zero-damage boundary check also found a production regression:
moving Fight's rational calculation inside its query snapshot kept its
pre-barrier candidate there, where query-phase writes are correctly rejected.
A positive hit rounded to zero could consequently leave TBN unconsumed.
The correction must calculate from the frozen query but publish its
pre-barrier value only after returning to the enclosing native result scope.
The existing native zero-rounded grid remains the regression gate; preview
queries without a real result scope must remain read-only.

All13 targeted steps passed in `20260915T105406.962857Z` on corrected
candidate `c1a7b7db270fdcb7da7686bbae38be103cc49ff3` (shared base6158684).
This includes the full Chemist and Blood Edge native comparisons and the
unchanged Dark Knight zero-rounded boundary grid. The turn-support script
passes1,004 assertions with240 complete native actions and24 native Combo
formula comparisons, each with enabled/disabled and ended-turn controls.
Its appended native help decoder passes3,554 checks, including preservation
of every previous help route/text and both new racial lesson assignments.
These formula tests do not establish native Combo selection, JP or playback.
All46 combined steps passed in `20260915T105543.754802Z` with unchanged
inputs on that corrected candidate. Its native movement trace includes22
state checks,95 logged events, actual stationary/moved AI actions and two
native suspend/cold resumes. The existing36-case reaction playback and its
five native cold resumes also passed.

Further acceptance includes prospective AI moved-destination evaluation,
all native Combo/UI/AP/acquisition flows and restorative-spell undead
inversion with combined incoming/outgoing classification. Do not infer
coverage of an inverted healing effect from the ordinary direct-healing
matrix. The remaining jobs also require additional state capacity beyond
the previous single unassigned byte; the shared schema2 migration now
reserves their full domains, with acceptance tracked separately.

## Design correction after the green movement batch

Review against the shared rules in `JOB-CLASS-SPECIFICATION.md` found that
the original own-turn Combo multiplier contradicted the approved exclusion
of new outgoing bonuses from Combos. The24 previous green formula cases
had encoded the same design mistake. The new implementation removes that
wrapper, restores the original native Combo route, and changes the oracle
to require equal damage with/without either support. Nonzero baseline damage,
explicit Combo contexts and ended-turn controls prevent vacuous passes.
The correction passed1,008 assertions and240 native actions in
`20260915T113723.698711Z` on2416455f0f8b0b3994b63dc71f3d49002d07300f,
including24 native Combo exclusions, positive damage controls, explicit
Combo/reaction origins and off-turn controls. See the checkpoint for the two
unrelated fixture corrections in the combined run. The historical green
run above does not establish correct Combo behavior.
