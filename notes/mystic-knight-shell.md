# Magic Shell implementation and evidence

Implementation resumed after the user's September 16 instruction to execute
autonomously with targeted testing. This is bounded native acceptance, not
release acceptance.

The successful native descriptor hook delegates magical HP actions to Magic
Shell before calculating their damage. Readiness and allegiance come from the
incoming-action snapshot; successful opportunities are claimed once there.
The unshelled forecast bypasses the reaction, uses a read-only child snapshot,
and restores native descriptor context and RNG. Positive forecast damage that
would leave at most half maximum HP grants native Shell before the real
formula. Existing Shell is neither stacked nor refreshed. Ordinary native
Shell setters (application83 at `0x081335EC`) supply status24 and timer3.

Native damage previews first calculate the unshelled result. Eligible threshold
crossings recalculate against an owned evaluated copy with ordinary Shell.
The copy inherits the pre-action snapshot, so newly granted Shell cannot make
Poise retroactively qualify. No preview may grant live Shell or spend a claim.

## Selected verification

Changed behavior: successful magical HP hits and native read-only previews.
Affected shared consumer: the successful-descriptor hook also handles Parry.
Selected IDs: `test-mystic-knight-shell`, `test-mystic-knight-parry`.
Prerequisite closure: six declared private/composed builds, integrated battle
and executor captures, then `test-integrated-native`. No other jobs' playback,
cold-save suite or full `combined` run is selected.

The Shell script uses fixed native casts and ordinary Shell controls, with
threshold, hit/miss, element immunity/absorption, original/new magic,
physical/status/MP exclusions, Arcane Ward and Blackest Night cases; it checks
RNG, live-state purity and both forecast stack residues. Observation hooks
never inject results or rewrite execution registers.

Initial run `20260916T082043.287202Z` passed all11 selected steps on
`b8aaa1b7f10d8d53739e365046c52f1bf749b66b`. Follow-up selection adds only
`test-mystic-knight-shell-lifecycle` for native status masks, legal Viera jobs,
removal/reapplication, context/RNG restoration and origin/permission guards.
Its prerequisite verifies the prior build/native report, unchanged build
inputs and exact capture hashes instead of rebuilding/recreating fixtures.
The original test defaults to all cases at the next major gate; this follow-up
does not repeat the already-passed core matrix or Parry.

Follow-up `20260916T082628.578337Z` passed2/2,101 assertions and6 casts. The
core run covered3,236 assertions and1,112 casts; companion Parry covered1,120
assertions and496 casts. Both runs had unchanged inputs; an independent
post-run hash confirmed the candidate. The follow-up guard and fixture-assumption
failures/fixes are preserved in `IMPLEMENTATION-STATE.md`.

Commands (PowerShell from the project root):

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-knight-shell,test-mystic-knight-parry
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-knight-shell-lifecycle
```

## Combined menu forecast and rendered pair checkpoint

Candidate `83d8d026e0bdf76ca1a1265d1da218eef54b8ad9` passes the 12 selected
steps in `20260916T124836.145433Z`: 2,975 pair execution assertions, 815 native
menu assertions, and 182 checks across five complete player flows. The earlier
single-action Shell pass in `20260916T123634.865695Z` remains applicable to its
unchanged execution/formula paths. No full integration suite was repeated.

The original UI caller B55CC reaches 130200 at B572C. Only that caller may
request combined Shell prediction. The second targeting screen is owned by
controller0200F4E8, phase31h, selection index AE=1 (not execution index AF).
Its live B+60 targeter must match the exact actor wrapper, recipient wrapper,
action at EC and equipment at EE. The first confirmed center is CB/CD. CC/CE
still contain old data during this screen and cannot identify its current
second recipient. Cancellation/backtracking/finished scopes fail closed.

The first spell's native recipient constructor supplies its actual cross-area
membership and direct magical HP contribution. Both original spell costs must
fit current MP. Generic formulas and AI do not inherit this UI selection.
First-spell previews stay single-spell forecasts because the second selection
does not exist yet. Forecasts preserve units, extension state, RNG, controller
bytes and live Shell; only an owned copy receives predicted Shell.

Player replay creates a declared second Viera in the roster before entering
Giza, allowing native deployment to load correct graphics. It then uses fixed
Red Magic/Doublecast inputs. At257/500 HP, the first Fire forecasts6 damage.
With the same target chosen twice, the second panel shows3 with Magic Shell
and6 without it. Actual reaction HP is254 after the first spell and251 after
the second, exactly matching the ordinary-Shell control. The unprotected
control ends245. With the second area elsewhere, the first-only recipient
ends251 with or without the reaction and receives no premature Shell.
All five flows reach the next turn, preserve native renderer bytes and AP/
inventory, spend12 MP, retire continuation storage and avoid repeated damage.

The first rendered positive case exposed stack overwrite missed by shallow
formula checks. The shared selected-area forecast now stores its148-byte
context backup alongside its heap scratch, freeing nested battle-stack space.
Bank previews also erase inactive payloads when no snapshot was required.
No saved data layout, action IDs or persistent workspace reservation changed.

Reproduce with the three declared test IDs below. The cached playback variant
is allowed only when `verify-integrated-prerequisites` validates exact source,
compiler, image and capture provenance. Failed input/setup and stack reports
remain recorded in `IMPLEMENTATION-STATE.md`; none is relabeled as a pass.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-knight-shell-menu,test-mystic-knight-doublecast-shell,test-mystic-knight-shell-playback
```

## Mixed spells and cancellation acceptance

Candidate `020d043ebca6208365faf874e938d6deca697dd3` closes bounded I02.
Run `20260916T125758.949041Z` retains passing 2,975 pair-Shell, 749 original
menu and182 whole-playback assertions. Its failed new consumers were corrected
without game edits. Follow-up `20260916T130022.048247Z` passes46 actual
cancellation/re-entry assertions; `20260916T130137.691256Z` passes3,929 mixed
spell assertions. These are a union of named targeted results, not a full-suite
pass. Failure chronology is retained in `IMPLEMENTATION-STATE.md`.

A preceding native HP heal now changes the decision HP for the second spell.
The selected first area returns negative healing only for admitted native
application38/formula35; projection caps at maximum HP. Cure, Cura, Curaga,
Earth Heal, White Flame and Unicorn cover four HP levels, two MP budgets,
inside/outside areas, Arcane Ward on/off and both stack alignments. Healing
that still leaves HP below half can still trigger Shell; healing across the
threshold suppresses the false prediction. Elemental absorption remains
different: its first magical hit already owns the pair's one opportunity.

The original ten mixed-pair execution controls and nine additional fixed-seed
Shell/Barrier/Carbuncle cases compare actual outcomes with reaction enabled
and disabled. At least one second spell really damages a Shell-buffed target;
no duplicate application, changed HP/status, or changed RNG occurs. Existing
Spellweave, Arcane Ward, Blackest Night, one-opportunity, affordability and
recipient-exclusion evidence remains applicable. Native prediction remains
conditional on successful actions; it does not replace future random misses,
reflection routing or arbitrary buff outcomes with guaranteed simulation.

The real cancellation test loads the successful second-spell damage panel,
backs out through the native screens, and returns to the main menu without
spending MP, changing HP, granting Shell or executing an action. The targeter
and continuation retire. Re-entry uses the menu's remembered selections and
shows the raw6 first-spell damage instead of the old pair's3. No game state is
rewound between cancellation and re-entry.

```powershell
& '.\Test Expansion.ps1' -Plan scripts/integration-test-plan.json -Only test-mystic-knight-shell-mixed,test-mystic-knight-shell-menu,test-mystic-knight-doublecast-shell,test-mystic-knight-shell-cancel
```

This closes the approved reaction implementation and its bounded forecast,
interaction, menu/cancellation and rendered-turn contract. It does not close
all-job presentation, campaign law/AP progression or assembled release gates.
