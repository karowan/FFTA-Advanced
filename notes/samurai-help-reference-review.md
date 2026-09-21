# Samurai help, Wound reference and harmful-status law

Private candidate `c8b98986a406255ff8732fb9fdcfbb045517738f`, based on accepted
main ba1c. This follow-up has focused acceptance, not a repeated complete
Samurai regression. The earlier bf941 checkpoint retains the complete declared
25-step evidence. The suite now declares29 steps as new acceptance work is added.
The separate `trace-samurai-laws` diagnostic is selected explicitly.

## In-game descriptions

All nine Samurai action lessons have concise native help. A guarded private
arena at11C9000..11CB000 holds the extra text and extended help pointer bank.
Existing pointer entries are copied verbatim; existing strings are untouched.
Only the nine new lesson help IDs and the bank pointer/range change.
Native decoding passes3487 checks: all1721 earlier help IDs preserve routing
and text; all nine additions have the expected decoded text, header, racial
lesson association, at most three lines and at most27 characters per line.
Run `20260915T015537.757873Z` includes the current candidate's help checks.

## Wound P and capacity

The approved shared formula explicitly says original attack/defense supports
modify vanilla inputs. Attack Up therefore remains part of P; it is not an
extra final-damage multiplier. Doublehand remains Fight-only. Centered and
Exposed are later multipliers and do not change the captured Wound amount.
Future Composure/other new damage bonuses must enter that later phase.

Native reference tests pass13003 assertions over1440 formula calls. Fixtures
vary base offense/defense, every available original Human support, Protect,
normal/query modes, fixed seeds, equipment power bytes0/255, Centered and Exposed.
Observers do not change the calculation. Actual native calls use action355,
auxiliary argument0, normal mode0 or query mode2, and special mode0; no critical
mode1 or special last argument enters the stored reference.

Observed scalar inputs stay between0 and999 after native caps, and the equipment
power sum stays below6*255. Native noncritical damage divides their product by100,
has at most1.5 affinity and ten-percent variance. This yields the conservative
25218 bound discussed in the storage investigation, fitting a14-bit half-P pulse.
The largest reference observed in these boundary fixtures is13020, deliberately
above the native final999 damage cap. That observed maximum is not claimed to
be the mathematical maximum. Stored P is captured before the cap.
Run `20260915T015537.757873Z` includes the current candidate's reference checks.

## Harmful-status law implementation

A native post-attack breakpoint revealed caller135072 passes signed **HP damage**
in argument6, and an optional native status-result mask in argument7. Those are
not a weapon ID and an arbitrary scratch pointer. The HP argument is zero for
Damage-to-MP interception:135028..135032 reads delta1E only when the HP result
flag is set. At that point the execution scope has closed, while the applied
Wound record survives. Original type15 specific-status laws inspect native
status bits; type16 is the broad harmful-status law.

The private hook at134834 preserves the common native actor/KO and movement gates,
and delegates every action other than355 to its original type16 branch. Higanbana
predicts its harmful status using explicit actor/target inputs, native eligibility,
physical magnitude and Damage-to-MP admission, while preserving RNG and live state.
The committed path requires positive HP loss, a remaining wound, a living
nonpetrified recipient, and no native Immunity. Wound does not impersonate Poison
or any other original status bit. Existing specific status laws are unchanged.

The complete original-law differential passes on current code in
`20260915T014840.354879Z`:347 original actions across20 kinds, plus existing
Samurai weapon/element and Guarding Draw status contracts. The new native law
matrix covers prediction and committed results at both stack alignments, native
movement gates, source/RNG isolation and positive/zero/negative HP results.

Actual menu-confirmed Higanbana executions reach the real post-action law caller
in `20260915T015120.849714Z`. A disposable copy changes the first native banned
rule from Charm to the broad status rule, or to Poison as a negative control,
and stops immediately after the query returns. Successful Wound returns1;
MP redirection, Immunity, lethal damage and specific Poison return0. The script
uses the native result object and actual HP/MP/wound outcomes, not injected
results. This is law-query acceptance; the subsequent Judge check below covers
the penalty and its persistence.

## Native Judge penalty and save acceptance

`20260915T020354.562671Z` passes the scripted Judge sequence on the same c8b9
ROM. It starts from the actual Higanbana confirmation, changes only a disposable
copy's banned-law data and initial RNG seed, and runs without an execution
breakpoint. Seed0 applies Wound and increments Marche's displayed yellow-card
count from0 to1; seed3 misses and receives no card. The specific Poison-law
control also receives no card. All three cases return to the native turn menu.
Native Save Now and a fresh emulator cold Resume Battle preserve the yellow
card and zero red cards. The native status-menu field is unit+103 for yellow
and unit+102 for red, established by the getter instructions at757A0/757BC;
an initial test incorrectly assumed101 and failed before gameplay. That failed
report is retained in `20260915T015909.674110Z`.

The accepted script is `scripts/test-samurai-judge-in-game.py`; its report,
states, screenshots and disposable law-control ROMs are under the c8b9
`judge-game` directory. This proves native penalty resolution and persistence;
it does not claim visual inspection of each animation frame.

## Remaining integration obligations

- Check preview behavior at the lethal/nonlethal variance boundary, where the
  average query magnitude and a later actual damage roll can straddle target HP.
- Before Auto-Cureall/other immediate custom cures are enabled, carry the original
  Wound application event through result processing. The current committed law
  gate observes the remaining record and could otherwise forget a just-cured
  application. Inoculation must join both application and prediction admission.
- Complete native AI acceptance for Higanbana, broader reaction/pulse combinations,
  the new Samurai supports/reactions, main assembly and full regression.

No player ROM, launcher or save has changed. All execution and verification use
local deterministic scripts; no agents run or monitor tests.

## Focused regression and retained inputs

Run `20260915T015306.360710Z` also passes native Samurai execution/lifecycle,
actual two-pulse/Poison/cold-save checks and both status-display suites on c8b9.
The harmful-status native matrix passes547 assertions. Its final entrypoint and
the help/reference checks pass again in `20260915T015537.757873Z`, with the
runner's child-process/reporting self-tests.

The runner now fingerprints generated compiler headers/includes,
content-data.json, the clean ROM and early-town fixture SRAM. Those were
previously missing from its input list. The final short run proves their current
values reproduce this exact same c8b9 ROM. Earlier focused gameplay reports
already identify that exact ROM; their original input lists are preserved,
not retroactively claimed to contain the added fingerprints.

The focused checkpoint is
`build/expansion/checkpoints/samurai-c8b98986a406255ff8732fb9fdcfbb045517738f`.
It retains source, generated inputs, engine/ROM, full logs and the evidence
index. It does not supersede the bf941 full-suite checkpoint with a claim of
full-suite execution on c8b9.
