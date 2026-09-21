# Dancer implementation batch

Later admission and ordinary AI correction:
[Dance Silence and no-op decisions](dancer-ordinary-ai.md). It fixes the
Silence allowance omitted by earlier direct-executor tests and supplies
native primary/secondary-menu and actual Silenced player-cast evidence.
Historical pending lists below retain their original scope; use the root
implementation checklist for the current backlog.

## Forecast and player-flow acceptance follow-up

Current candidate `72c8be881e05dbf19fc4cebc7a6a8ac732c211db` also fixes the
player's chance and magnitude forecasts. After the targeting correction,
run `20260915T141017.990312Z` passed all49 combined steps on
`5f3b7d347354640abe078f0a952649ab5f283b39`, including468 assertions over twelve
player casts with selected-center and exact two-enemy membership checks.
Root review of its captured preview nevertheless showed0% rather than the
selected ailment's chance. Passing execution did not establish forecast fidelity.

Declared trace `20260915T141816.699466Z` identified native constructors called
from12DBD6 (chance) and130266 (magnitude), each supplying extra0 while target
validation supplied1. New adapters at12DBCA/13025C pass the same exact-owner,
mode/action-validated choice into the constructor. Chance has actor R6,
action R7 and primary atSP+10; magnitude has actor R6, action R2 and primary R7.
Original actions retain their primary operand, stack and native continuations.
The magnitude adapter replays its displaced actor store. The earlier discarded
12DBCA attempt was indeed irrelevant to target validation, but this separate
trace establishes its role in the displayed forecast.

Compact menu labels are Blind Dance, Silence Dance, Poison Dance and Confuse
Dance. The full Forbidden Dance title/help and shared AP identity remain.
Native font measurements limit each choice to13 tiles, and root reviewed the
saved choice/recipient-preview images. The ordinary fixture now displays30%
instead of0%; actual cast seeds still include both hits and misses.

Affected run `20260915T142013.832603Z` passes11/11 steps with unchanged inputs:
12,642 native choice/adapter assertions and516 player playback assertions.
Forecast checks include1,344 invocations across the two installed continuations,
matching context action/extra and unchanged SP at both stack residues.
The playback separately checks selected action/extra in the real recipient
preview, both recipients, one14MP cost, rendering and return to a usable turn.
A full native chance-function regression adds ten assertions: its controlled
routine fixture returns50% for each valid choice and0% for inert choice0.
The final49-step combined run `20260915T142155.015003Z` passes every step
with `inputsUnchanged=true` on this exact candidate. Final choice coverage is
12,652 assertions; player playback remains516 over twelve casts. The same
run also passes48 reaction playbacks, seven cold resumes, turn movement/undo,
and all existing combined job/native regressions. Root reviewed the assembly,
operand/stack lifetimes, original-action delegation, action-center metadata,
native row decoder and saved menu/forecast images. ROMs, fixture binaries and
raw reports remain private and ignored; the reproducible scripts are source.

Still open: AI option search, complete law/immunity/cancellation/secondary-job
acceptance, Passing Step, remaining jobs and campaign/acquisition coverage.
These checks do not establish full expansion or release acceptance.

## Player choice and target transport follow-up

Candidate `26a38a50286d7091ffaf024d1ad837c7beedafd4` added the two
missing player UI handoffs. B4CF0 validates a target using actor R9, action R4
and operand R6. The adapter substitutes the choice only for406 and the exact
active selection owner, with matching action, mode6..11 and choice1..4. Other
queries do not borrow a live choice. Native94342 separately gates copying the
UI extra into battle manager+A8. Its406 exception retains the existing item
and special-action branches without assigning item semantics to the dance.
The earlier A447A executor admission remains required. All three carry points
serve different consumers.

The base action now carries descriptor87 as its status template. The context
constructor still chooses87/111/125/95 from the explicit selection and makes
an invalid choice inert. The first attempted forecast hook at12DBCA was not
the observed target-validator path and has been removed. The private declared
`diagnose-dancer-choice-ui` trace identified B4CF6 and later caught an adapter
bug passing saved SP as the action. The adapter now loads the saved R4. Its
regression exercises the installed instructions, both stack residues, native
continuations and context fields, beyond testing the C helper alone.

Run `20260915T134357.601931Z` passes11/11 affected steps:7,206 native choice /
adapter checks and368 player playback assertions over twelve fixed inputs.
The four real choices render, can be targeted and reach the executor; each
ailment has a positive playback, with misses retained, one14MP cost, unchanged
inventory/learning, preserved heap/IWRAM guards and return to the turn menu.
The native caster is checked through its result record (the executor argument
itself is a wrapper pointer). Status targeting takes one confirmation press
before the final prompt, unlike the earlier Fight script.

The full49-step run `20260915T134535.046473Z` passed on that candidate with
unchanged inputs, but its player playback asserted effects on only one actual
recipient. The original supposed second enemy was the Judge at020034EC.
Declared diagnostic `20260915T135914.981956Z` confirmed native rejection of
all four ailments for the Judge and acceptance for enemies020033E4/02002FC4.
The corrected fixture keeps the Viera's real starting tile, then uses native
Move before Act. Live movement updates wrapper coordinates before unit F6/F7;
the latter synchronize in A433C and are not an immediate movement oracle.

The strengthened run `20260915T140034.653806Z` exposed a production targeting
bug: result+A/B contained caster tile0,13 despite selecting1,13. Action byte8=3
is a fixed caster center; byte8=1 selects the cursor center. Byte9=5 separately
chooses cross geometry. Dancer's four area actions, Bard's five ranged area
songs and Chemist Healing Mist now use selector1. Deliberately self-centered
Hide, Chakra, Moon Blossom and hidden self reactions retain their selectors.
Candidate `5f3b7d347354640abe078f0a952649ab5f283b39` contains this correction.
Target-centered playback requires two confirmations after moving the cursor.
Native recipient rows have stride0x2C, not56; the two-recipient assertion caught
that test decoder error. Both corrections retain strict center and membership
checks rather than accepting a caster-centered cross or injected outcomes.

The separate64 native casts already have positive effects on both enemy recipients.
Full AI choices, detailed immunity/law queries, cancellation/secondary-command
scenarios, Passing Step and wider expansion acceptance remain open.

## Forbidden Dance follow-up

`dancer-choice.c` composes Chemist's existing menu/context handlers and adds four
Forbidden Dance rows retaining the same racial lesson index. Choices1..4 mean
Blind, Silence, Poison and Confuse; native descriptors87/111/125/95 respectively
use native S accuracy and status application. The command has14MP, range3 and
enemy cross targeting. Its unselected row is inert. Selected context construction
updates both the four-byte vector and the initial descriptor pointer, without
new persistent state. The central builder generates its assembly adapters and
native option labels. Original actions and Chemist choices delegate unchanged.

The initial consolidated run `20260915T125959.354730Z` passed47/48 on
`6387f497a552feb83d5aa78b0f4adedc91b2969f`; the new test incorrectly expected choices in the native restricted
(Doublecast) menu. Correcting that expectation exposed a real cast transport
gap in `20260915T130713.364087Z`: MP was paid but no status was applied.
The read-only native trace `20260915T130829.196541Z` showed the action constructor
receiving the primary weapon416 instead of choices1..4. A433C's native weapon
enumeration keeps the supplied extra only for an item action or its original
special case. Do not turn on item semantics for a dance merely to retain it.

`dancer-choice.s` now extends the A447A..A4484 admission to406 alone, preserving
the original item and special-case branches. The caller's R8 choice is written
into the native one-element operand list, so every recipient receives it. The
existing original branch destination at A448E is preserved. No native debit,
item-action flag or persistent state is added.

Run `20260915T131057.716678Z` passed all10 affected steps on
`92f0c19fdec3f0a0bcac86b2b64e116c0533e5e6`. The choice test passes684 checks:
16 native menu configurations, AP identity/read-only learning, MP greying,
capacity guards, names/widths, selected halfword and both descriptor pointers,
and64 full native casts across the four choices, eight seeds and Silence on/off.
Two enemies occupy the same cross; each must demonstrate every chosen ailment,
with no alternate ailment, target HP/MP damage, inventory debit or duplicate MP
cost. Misses remain in the fixed matrix. Restricted menus exclude dances and
invalid selections have an inert vector. The full corrected combined run
`20260915T131152.868000Z` passes48/48 with `inputsUnchanged=true` on the same
92f0c19 candidate, including original actions, all existing integrated job
checks,48 reaction playbacks, seven cold resumes and the movement trace.
This playback coverage belongs to the existing reaction families, not the
new Forbidden Dance input flow. Rendered player selection, full AI option search, detailed immunity/
law acceptance and Passing Step remain open. The accepted prior subset is below.

The earlier implemented subset passes the deterministic checks below. This is not a
complete job or release. Root alone implements and reviews deterministic tests.

The batch adds Mincing Minuet, Witch Hunt, Slow Dance, Polka, Heathen Frolic,
Jitterbug, Sword Dance, Fury and Counter Rhythm. Grace/Light Foot already exist
in the accepted foundation's mobility-supports.c/.s and are preserved. Forbidden
Dance required a native per-cast chooser and AI choice transport. Passing Step
requires a preselected route executed after immediate reactions with remaining
movement accounting. Both were disabled at the earlier checkpoint below;
Forbidden Dance's current partial implementation is described above.

## Native contracts

Pdance has two independent native gear terms:12FDC4 adds weapon/nonweapon gear
to supported character Attack;12FF64 selects weapon power for the same P formula.
Both now use min(35,12+floor(3*level/5)) plus retained nonweapon Attack bonuses.
Native constructor C983A..9852 establishes level at unit9; slot8 is a secondary
command job, not level. Exclude every hand weapon; retain shields and nonweapon
gear, native Frog handling, accumulated Attack and original defensive/support
stages. Primary knife/rapier types are7/8; Sword Dance retains its actual primary.

These call sites cannot reach the new module with a short Thumb BL. Long wrappers
replay the displaced native instructions and preserve saved/high registers and
both stack residues. Element routing excludes held elements for virtual dances;
weapon laws enumerate no weapon for those dances and one primary for Sword Dance.
Existing Grace's12C89C hook and Light Foot's movement getter remain installed.

Polka/Frolic use owned byte3's independent T2/application-turn skip domains.
They are admitted only after actual positive enemy HP loss, with custom immunity
and Chemist prevention applied to the rider. Frozen weakening and Fury enter
one exact rational damage calculation. Quotient/remainder decomposition avoids
multiplying the already large common numerator by400 or rounding intermediate
results. Reactions, Combos, MP interception and healing/absorption are excluded.
Jitterbug uses actual HP removed and native accumulated actor recovery, with
undead reversal, no overkill and the quarter-max-HP cap.

Fury and Counter Rhythm use hidden actions441/442, queued only from authenticated
incoming HP loss. Fury owns one charge; Counter Rhythm uses one native Slow S
attempt with20 added points and95 cap, preserving immunity/interception. The
source currently needs consolidated native queue/playback and copied/law state
coverage before these are accepted. Polka/Frolic law prediction is still an
explicit outstanding path; actual HP commit alone cannot prove it.

Three status glyphs occupy OBJ1F6..1FB. Native tables grow to443 actions,
233 descriptors and109 applications/masks. Dancer help uses12E0000..12EFFFF.
Schema2 transports the already reserved state without another ABI change.

## Testing and remaining gates

The declared integration plan includes test-integrated-dancer.py. Its coherent
native matrix covers real MP payment and HP/MP effects, virtual weapon invariance,
primary requirements, independent timers and unchanged record domains. Broader
cross-class reactions, actual status graphics, native menus/AP/acquisition,
choice/route UI, complete law/AI queries and cold-save effects remain required.
Compilation is not acceptance. The full expansion goal remains active.

## September15 regression correction

The first consolidated47-step candidate run (`20260915T120115.466799Z`)
failed the unchanged original-action differential on action15. Native special
weapon branches enter12FF6E directly; the initial12-byte power hook overwrote
that shared multiplication with literal data. The deterministic declared
`diagnose-dancer-native` script isolated the power hook: restoring only that
site eliminated all seven RAM differences, while restoring only the Attack
hook retained them. The corrected compact hook preserves the original12FF6E
instruction and returns to it. Do not replace this with a generic long hook.

`20260915T121332.991284Z` passed all10 prerequisite/original/Dancer steps on
the corrected candidate. The first Dancer matrix verifies seven active native
execution paths, native MP payment, virtual-power invariance, Sword Dance's
primary requirements and timer lifecycles. Witch Hunt's A-type misses remain
in the fixed input grid; a separate assertion requires an actual successful
MP-damage case. Expanded cross-class and reaction playback checks are pending;
this evidence does not complete either the job or expansion.

The expanded run `20260915T121617.286455Z` exposed Fury's Fight-consumption
gap: ordinary Fight never enters the MP-payment callback. Its authenticated
native completion now consumes the charge, while failed paid commands and
reaction-origin actions remain excluded. The same run stopped before Counter
Rhythm execution. The fixed diagnostic `20260915T122038.095212Z` found intact
IWRAM code and a live preview menu, not an executor hang. Increasing the fixed
wait did not repair it. An additional acknowledgment exposed a damaged heap
header; the apparent extra page was a consequence of that corruption.

The invalid-free diagnostic `20260915T123444.688177Z` caught a null allocation
passed to native free from B59E8, through22854/7170. Native B594C had requested
4096 bytes after the heap chain was damaged. The original cleanup does not
accept null, and its writes reached the EWRAM end guard. Do not mask that guard
or merely suppress null free; the earlier corrupted allocation chain matters.

Changing only the private display text to `Rhythm` eliminated the corruption
and restored the ordinary confirmation mode in `20260915T123758.118146Z`.
Native font measurements in `20260915T123917.506909Z` identify `Counter Rhythm`
as the only new reaction label over12 tiles: it measures13; `Counter Rhy.`
measures10. The patch retains the approved full name in the registry and
help and assigns the compact game label through the existing Other-name table.
All new reaction labels now have an explicit native width check. The standard
fixed confirmation inputs are restored and must reach native mode11 with the
heap/root guards intact. No diagnostic memory repair is part of the candidate.

The first alias patch updated the inactive content-data Other table. The
command-data stage later clones it, and native reaction preview reads the live
table through ROM literal2C08C. The builder now checks that literal against the
command-data manifest and edits the active row. The width regression also
executes the real2C05E..2C09A reaction-name lookup before measuring each label;
measuring an unreferenced pointer table is not UI evidence.

## Accepted subset and remaining work

Final candidate: `8c8b46fc9e98190f9aab635f7a774427bfb5076d`, shared base
`3540440aafbeebb560a14669b92da252971a5174`. Run124036 passed46/47 combined
steps on5fb05c6f4c7f1fd2afac97868cbff498d8c060c2. Run124811 passed all11
affected steps on the final candidate. Both full timestamped report IDs are
in `IMPLEMENTATION-STATE.md`; reports have `inputsUnchanged=true`.

The final image differs from5fb05c6 only at102D010..102D012 and
102F284..102F286: six changed bytes restore the unused name pointer and update
the live one. Machine code, action records, state/save transport and other
text are byte-identical, so their passing full-run results remain applicable.

- 2,520 Dancer assertions across408 complete native actions: seven active
effects, once-only MP payment, weapon-free formula invariance, actual-weapon
Sword Dance, T2 domains,64 mixed physical/magical modifier configurations,
Fury/Counter Rhythm admissions and borrowed Red Mage reactions, Fury physical
attempt consumption including Fight, and preservation on ordinary magic.
- 3,593 native help assertions plus every new reaction's actual name lookup
and bounded native font width.
- 12 Dancer enabled/disabled fixed-seed menu-to-result playbacks, intact
IWRAM/root/heap guards, rendering and next-turn return, and two real suspend /
cold resumes. Fury persists; Counter Rhythm must first successfully apply Slow
and that Slow must persist. Saves resume in the uninstrumented candidate.

Still required: Forbidden Dance's chooser and AI choice, Passing Step's
preselected native movement route, full law/AI prediction for weakening and
all actions, broad immunity/dispelling/forced-action combinations, complete
lesson/AP/acquisition and campaign acceptance. The wider Geomancer/Mystic
Knight implementation and final clean-source assembly remain open. No full
expansion completion or release is claimed.
