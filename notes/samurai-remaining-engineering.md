# Remaining Samurai engineering entry points

For the latest Higanbana implementation and remaining acceptance work, see
`samurai-wound-review.md`. The storage constraints below are historical:
ba1c integrates the72-byte wound bank and38-byte Extra copy stride.

September14,2026. Research pointers, not enabled or accepted new actions.
Continue after private candidate41c51aa1 and its complete twelve-step test run.
Murasame/Kiyomori are implemented and tested; see
`samurai-restoration-review.md`. The native healing pointers below preserve
the earlier research, not outstanding implementation for those two actions.

Wind Draw348 subsequently passed focused native/UI/law checks onf71fceb6;
see `samurai-wind-review.md`. Moon Blossom354 subsequently passed the complete
seventeen-step suite; see `samurai-moon-review.md`. Higanbana355 remains pending.
Supports/reactions remain separate pending
work. Avoid re-running the accepted private suite until implementation changes
or a new concern warrants it. All tests stay deterministic scripts.

## Native healing and buff references

- Ability names use the Other text bank at5567F0, not item/job names526680.
  Reading the latter with action name IDs produces unrelated item names.
- Original Cure1 uses stage168 `[19,38,1,35]` and180 `[22,21,10,30]`.
  Original White Wind308 uses stage90 `[8,38,1,25]`.
- Magnitude25 points to131838. Its ordinary reference is the actor's current
  HP, with an effect-sensitive target check. A conditional Murasame350 handler
  would need its approved target-max-HP formula, Centered and missing-HP cap;
  the original callback must remain unchanged for every other action.
- Magnitude35 points to131960. Healing effect38 points to13254C, a no-op;
  native executor application/classification owns actual healing.
- Protect9 uses stage78 `[8,82,23,0]`, effect82 callback1335C0. Shell8 uses
  stage45 `[8,83,23,0]`, effect83 callback1335EC. Their status bits are25/24.
  **Compatibility133A58 takes the effect ID82/83, not the status-bit ID.**
- Protect setters CE094(value1),CE448(timer3); Shell CE070(value1),
  CE440(timer3). The common effect path also calls131C28(effect,recipient)
  for the native removal mask,131C58 for timer cleanup andCA2E8 for refresh.
  Omitting these left Invisible active in the first Guarding prototype; the
  full native-Protect differential now prevents that regression.
- Murasame/Kiyomori must retain primary-katana requirements, ally/self targeting,
  approved cross geometry, Sure accuracy and physical-technique interactions.
  Do not infer Silence/Reflect/Doublecast classifications from animation donors.

## Blade Wound storage constraints to resolve

The saved packed Exposed/Centered bytes occupy1E98..1EBC (36bytes). The migrated
inventory reserve ends at1F1C, leaving96bytes after that array. A36×2-byte
Wound record could fit, but a concrete representation and all future custom
effects must be planned before assigning this space. This is a capacity
observation, not an accepted layout or migration design.

Every ownership path needs the same data: canonical party/enemy, native state
staging, roster swaps, manager/selection/party copies,13-unit snapshots and
explicit evaluated law/preview copies. `unit-copies.c` currently has36-byte
Extra (34AP,potion preference,packed state); `evaluated-units.h` has a276-byte
container with three reserved tail bytes. Enlarged allocations, initialization,
copy/clear, save import and lifetime bounds all need deterministic verification.
Do not infer owners from matching character identity bytes.

The user-approved Wound snapshots ordinary P before final bonuses/interception,
has exactly two end-turn pulses, replacement without stacking, broad remedy
cure and KO/Petrify/job/battle-end cleanup. Pulses have no reaction/proc/drain/
critical/damage-bonus behavior. These contracts remain unimplemented.

## Moon Blossom leads

The earlier A4672 lead was disproved: its recipient rows are allocated but
have not executed HP changes. The implemented Moon grant instead examines the
finished output after original A433C returns, before Centered retirement.
The row count is at2C0, rows at20+2C*i, flags atrow+C and signed HP delta
atrow+1E. Actual native/UI tests distinguish positive HP loss from misses,
Damage-to-MP interception and restorative weapons. Multiple positive enemy
results grant Regen once for the action. No result or HP is injected by tests.

Native Regen stage195 is `[19,31,22,0]`; effect31 callback132450 marks status3
and callsCDD64(unit,1) outside query mode. Status3 is unitE8 bit08. It does
not set a Protect-style three-turn timer. Native compatibility/removal/cleanup
remain necessary: use effect31, not status index3, with133A58/131C28/131C58.
