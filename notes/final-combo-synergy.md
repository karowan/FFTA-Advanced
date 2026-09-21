# Current-build Combo and mixing acceptance

Candidate `687ed5d48494dcb46d8b70612680ede56d5dec86` completes V04's targeted
combined-combat gate. No shipping code, balance, lesson, weapon or save layout
changed. This is not final R02 acceptance or a campaign playthrough.

## Actual Combo controls and persistence

Run `20260917T060657.042206Z` passes all eight selected steps. Its Combo step
passes 432 assertions across all ten racial owners:

- Native command selection, target selection and cancellation preserve JP,
  target HP, equipment, all AP and assigned Combo.
- Actual initiation spends three JP once, preserves identity/mastery/gear,
  produces nonlethal damage, and returns to the native command menu.
- Every new Combo actually participates in a chain initiated by an original
  Combo. A native membership observation proves inclusion. A control changing
  only the new racial record's profile to its named original donor produces
  identical membership, HP, JP, equipment and AP results.
- Ten native Save Now / fresh SRAM-only Resume Battle flows preserve job,
  assigned Combo, JP, equipment, AP, identity and target HP.

Fixtures declare legal same-race jobs, weapons, mastery, JP and target HP on
disposable units. They preserve original identity, race, level and stats. These
are combat/persistence cases, not evidence of naturally earning three JP or
mastering the lesson during a campaign. The independent V03 matrix covers AP.

Artifacts are beside the candidate under `combo-ui/20260917T060710.789999Z/`;
final report `report-20260917T061012.251952Z.json`. Root inspected Samurai's
native Combo menu and a Geomancer animation frame. Thirty native menu returns
are observed across initiator and participant/control executions.

## Every permitted weapon family

Run `20260917T061020.778153Z` completes all 39 Fight/Combo playback cases with
156 assertions. Every case returns control with correct JP, unchanged gear and
identity, and a surviving target. Mystic Knight's original saber now completes
both Fight and Combo, covering the pose correction's direct consumers.

That run is **failed**, because its final coverage assertion requires at least
one successful hit per job/weapon family. Bard's knife Fight at native seed0
missed; instruments passed through Combo. A miss alone does not test a hit's
weapon animation. No gameplay change or forced hit was used to resolve this.

Run `20260917T061308.106846Z` authenticates and retains all 39 cases, then runs
only Bard's knife Fight with bounded declared seeds. Seeds1..5 miss; seed6
hits for9 HP and returns normally. Its accepted report has45 total cases and
180 assertions, with successful damage represented for every permitted family.
The failed original runner report remains failed. Ordinary reproduction now
uses the observed seed6 for that one case; the exploratory search is not repeated.

Artifacts: `combo-weapon-visuals/20260917T061022.389451Z/`, final report
`report-20260917T061322.857985Z.json`, SHA1
`d138fb4953cd8237f02784c6913b0cf970ae62ea`.
Bard knife Combo is correctly omitted because Chorus Combo requires an
instrument. The 39-case coverage count explicitly accounts for this rule.

## Native combined effects

The first run's five native suites and the last run's turn-support suite pass
12,661 assertions on the same actual candidate:

| Check | Assertions | Relevant scope |
| --- | ---: | --- |
| Combined factors/statuses | 4,240 | One rational product, preview purity, frozen harmful tags, prevention/stock/claims and coexisting status lifetimes |
| Geomancer passives | 2,852 | 664 native executions; transferable movement, actual payment/refund, once-only completion, reactions and affinity rules |
| Undead policy | 1,642 | 65 native casts; living/Auto-Life versus native undead/Zombie, HP/MP drain direction, resource costs and recovery restrictions |
| Mystic Doublecast | 1,258 | Actual native call-site slices/constructors, frozen sequence, one outer completion, Shell lifetime and ineligible-new-action controls |
| Doublecast reactions | 1,649 | Aggregated damage, one reaction opportunity, stock/payment, mixed outcomes, original controls and natural caster-KO cleanup |
| Turn supports | 1,020 | 240 native actions; legal cross-job damage/healing, frozen copies, reaction exclusions and24 native Combo formula pairs |

Composure and Follow Through leave Combo damage unchanged, including off-turn
controls and a positive base-damage check. Source review confirms the explicit
Combo-origin and action265 exclusions, and the primary-weapon gates for all
eight profiles match the approved families. The historical original-profile,
status/RNG and disallowed-weapon differential remains supporting evidence;
this checkpoint does not claim to have rerun that separate historical suite.

Reports in the candidate directory are `synergies.json`,
`geomancer-passives.json`, `native-undead-policy.json`,
`mystic-knight-doublecast.json`, `doublecast-reactions.json`, and
`turn-supports-native.json`. Each records the actual tested ROM. The runner's
legacy foundation hash is not the integrated consumer's ROM hash.

These native checks do not themselves prove full controller animation. Retain
the already accepted Doublecast/Shell/reaction player flows in their named
notes, plus the new Combo playback above. Historic report limitations describe
their original scopes; they do not reopen implementations closed by later
evidence. Outstanding informative presentation stays V01/A05, campaign Judge
outcomes V06, field-display acceptance I07, final assembled release R02.

## Reproduction and evidence reuse

Use the declared plan with `Test Expansion.ps1 -Plan scripts/integration-test-plan.json -Only`:

- `test-integrated-combos`, then `test-integrated-combo-weapons` for the whole
  bounded Combo/weapon gate when relevant. The latter consumes and authenticates
  the successful Combo report instead of automatically replaying its producer.
- Their `-resume` variants retain completed phases/cases and artifact hashes.
  `test-integrated-combo-weapons-positive` resumes only the Bard knife control.
- `test-final-mixing-synergies`, `test-final-mixing-geomancer-passives`,
  `test-final-mixing-undead`, `test-final-mixing-doublecast`,
  `test-final-mixing-doublecast-reactions`, `test-final-mixing-turn-supports`
  select their bounded native contracts using the authenticated cached executor.

Integrated modes use the current image without an old engine overlay. Legacy
modes remain available. Turn-support `--combat-only` omits the unrelated old
help differential; current installed help has its own accepted audit. Fixed
positive-seed selection after these passes changes no tested game behavior and
does not warrant another full playback. Raw ROMs, saves and logs stay ignored.
