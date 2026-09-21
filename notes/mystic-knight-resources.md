# Mystic resource forecasts and native AI values

September 16, 2026. Accepted candidate:
`e4e00a0a04d54a58c80fb73346d7e6ec7f1b6f31` (independently rehashed).

## Behavior

Execution and forecasts share a pure resource plan. Drain returns 35% of actual
HP removed, capped at 15% of actor maximum HP and missing HP. Undead reverses
the actor effect. Osmose removes up to one quarter of actual HP removed, capped
at 10 MP and target stock; actor credit is limited by missing MP, or actor MP
for undead reversal. Ally, self, miss, absorption and MP-redirection controls
retain the existing rules. Real results still authenticate the primary weapon
and spend one resource claim; forecasts cannot publish claims.

Fight forecasts simulate native weapon order on owned actor and target copies,
including earlier native drain, restorative healing, effect3E cleanup, and
Damage to MP. Native score entry BDECC and row entry C2618 include the resource
value: target MP debit plus actor recovery, minus undead loss. They preserve
native target admission, other row fields and existing damage value. This is
bounded consumer integration, not proof of complete AI turns (I05).

Native law kinds 11/12 compare signed recipient HP damage, and 13/14 compare
recipient HP healing. MP debit and actor drain credit are separate native
fields; they do not turn target HP damage into target healing. There is no
general MP-damage/healing threshold in this selector. The expansion preserves
native Drain reporting rather than manufacturing an extra healing recipient.
The matrix verifies those native domains with actual Fight/command result rows;
full Judge penalty/campaign acceptance remains a release obligation.

## Query storage and status forecast correction

Known native Fight queries and component simulation borrow an unused slot in
the existing eight-slot result snapshot bank. An exact live stack token owns
the slot; query end retires it. Real result callbacks keep their existing
barrier-publication path. No additional pool space or saved fields are used.
This avoids nesting an 820-byte snapshot beneath two evaluated-unit copies.

Status laws consider an eligible preceding miss and earlier weapon drain,
healing or effect3E cleanup. They use the native lower ordinary damage bound
before expansion factors: native 130072..13009A varies damage by
`+/- floor(damage / 10)`. Average damage must not suppress a warning when a
lower roll leaves the target alive. Native damage caps can make this bound
conservative. Resource ranking continues to use ordinary average forecasts.
Warnings describe possible effects, not guaranteed random outcomes.

## Evidence and reproduction

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only
test-mystic-knight-resources,test-mystic-knight-fight-prediction,test-mystic-knight-fight-preview`.
Declared build/capture/native prerequisites run once. Cached variants verify
unchanged prerequisites before reuse. All inputs are deterministic; no test
injects a hit, damage, status application or AI score.

Run `20260916T110457.901633Z` passed 12/12 selected steps:

- 12,652 resource assertions; 96 scenarios and 768 native Fight/command casts.
  Includes caps, full/missing resources, undead, allies, overkill, Damage to MP,
  Spell Parry, restorative/secondary weapons, native AI row/score purity and
  10,368 native HP-law comparisons.
- 7,496 status-law assertions; 228 inputs, eight execution seeds each (1,824
  casts), both caller stack alignments, live/context/RNG purity and scope
  retirement. All observed applications retain a forecast warning.
- 15,202 existing preview assertions; 4,266 native calls, including sorted and
  identical weapons, reaction consumers and independent native controls.

Earlier failed runs remain in `build/expansion/test-runs`: 105412.897297Z and
105539.010473Z found nested snapshot stack corruption; 105818.334511Z exposed
remaining deep AI corruption and the variance boundary; 110333.281906Z recorded
native rolls and HP writes proving the boundary. All have date prefix 20260916T.
Final guards preserve the executable IWRAM region through the affected queries.
Raw reports, ROMs and logs stay ignored. No full integration suite, cold-save
matrix or unrelated campaign playback was run for this bounded change.

Follow-up: `mystic-knight-ai.md` closes status-effect AI values, all 21
Spellbreak choices and five autonomous turns. Remaining: complete self/command/
area AI, combined Shell menu forecasts, and final assembled release coverage.
