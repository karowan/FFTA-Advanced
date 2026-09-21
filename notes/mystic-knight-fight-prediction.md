# Fight status-law prediction

Initial September 16, 2026 checkpoint. Candidate SHA1:
`b16841d2cad3ed2f75eb88920ec787a25babe5b6`, independently rehashed.
This implements status-law forecasting for the bounded scenarios below.
The later resource/secondary-weapon checkpoint is documented in
[mystic-knight-resources.md](mystic-knight-resources.md): candidate
`e4e00a0a04d54a58c80fb73346d7e6ec7f1b6f31`, 228-input status matrix passing.
It supersedes the resource and secondary-weapon gaps described below. Status
AI value and full AI turn acceptance remain open. This document preserves the
initial implementation and evidence chronology.

## Native behavior and implementation

The native law selector skips Fight for specific and broad harmful-status
laws. Simply bypassing that skip is incorrect: native status simulation at
`081342CC` immediately returns true for Fight, regardless of requested status.
The installed law selector instead asks an explicit enchanted-Fight forecast.
Committed result masks still use the separately accepted receipt transport in
`mystic-knight-fight-laws.md`.

`src/engine/mystic-knight-prediction.c` initializes an owned evaluated target,
obtains native weapon order, and predicts ordinary successful components up to
equipment-primary. The component helper in `mystic-knight-fight.c` retains
exact primary identity, including identical weapons and stronger offhand-first
ordering. Native formulas and existing shared modifiers calculate damage.
Earlier healing updates the temporary target; Damage to MP updates its MP;
defeated targets do not receive a status stage. Positive HP damage performs the
same damage-sensitive cleanup as the native result path before status prediction.

The primary stage uses the actual Poison, Sleep, Silence or Slow descriptor.
Native eligibility, nonzero native accuracy, application setters and prevention
observers determine the application mask. No accuracy roll is taken. Astra,
Immunity, Inoculated and War Cry retain their real rules; Slow remains outside
the native Cureall/Immunity whitelist. Sleep can apply again after damage wakes
the target. Friendly fire and Silence do not incorrectly disable ordinary Fight.

The live actor/target, job records, current native context and RNG are unchanged;
the evaluated target and query scopes are retired. No saved fields, new fixed
RAM reservations or pool-size changes. This is the ordinary-success forecast
convention, not a promise of a particular random hit, critical or multi-hit
outcome. Earlier secondary-weapon special effects beyond the tested restorative
case still require parity work: the forecast currently simulates HP/MP and
damage-sensitive cleanup, not every ordinary weapon application. Potential
primary applications after a preceding miss also need an explicit policy in
the AI/law forecast audit. The AI's effect-scoring path is a separate consumer.

## Deterministic evidence and reproduction

Run `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only
test-mystic-knight-fight-prediction` for the declared build/capture/native
prerequisites and complete focused matrix. Cached variants verify unchanged
source/image/capture prerequisites first. `test-mystic-knight-fight-prediction-follow-up` selects only the corrected immunity expectations, identical weapons
and earlier restorative-offhand cases.

The final matrix contains 212 distinct kind/condition/weapon inputs, each with
eight native execution seeds. Forecast queries cover both caller stack
alignments, specific and broad status laws, an unrelated law, live/context/RNG
purity and scope retirement. Native A433C executions supply actual primary-row
application masks. No hit, damage or status outcomes are injected. Conditions
include Sleep, Astra, Immunity, Inoculated, War Cry, friendly fire, lethal/zero
HP damage, Damage to MP, restorative weapons, Silence and Spell Parry.

- `20260916T103846.212269Z`: nine prerequisites passed; the focused check
  found a production omission. Immunity zeros status accuracy rather than
  rejecting the application callback. Added the native nonzero-chance gate.
- `20260916T104009.757019Z`: nine prerequisites passed. The matrix performed
  5,140 assertions and 1,248 native executions. Its six failures were an
  incorrect test expectation that Immunity/Inoculated block Slow; native
  execution and the approved whitelist confirmed that they do not.
- `20260916T104223.378579Z`: strict cached follow-up passed 2/2, with 2,640
  assertions and 640 native executions across 80 input combinations. This
  replaces the six incorrect expectations and adds identical/earlier-healing
  coverage. Every earlier nonfailing case remains retained evidence on the
  same final ROM; the earlier report remains marked failed rather than rewritten.

The complete 212-input coverage is the union of the last two reports, not a
claim that the earlier aggregate report passed. Raw reports and logs remain
ignored under the candidate directory and `build/expansion/test-runs`.
No full integration suite, campaign playback or unrelated persistence rerun.
