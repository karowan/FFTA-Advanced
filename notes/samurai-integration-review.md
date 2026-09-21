# Samurai four-strike implementation and verification

September14,2026. All tests use deterministic local scripts. No testing agents.

Private ROM `c683be6ff39ba02b4a1e9f650705f8b254fd59e5` is built over accepted
main ROM `d1565a7ee341621e58bd2bb791b065144fe51aec`. It is not installed in the
player launcher or assembled main build. Its artifacts are under
`build/expansion/probes/samurai/d1565a7ee341621e58bd2bb791b065144fe51aec/c683be6ff39ba02b4a1e9f650705f8b254fd59e5`.

## Implemented behavior

- Ashura347: primary katana, adjacent enemy, 4MP,1.10P non-elemental. Positive
  enemy HP damage grants Centered; a miss does not manufacture the buff.
- Osafune349: range2,height3,6MP,0.85P. Positive enemy HP damage removes up
  to10 actual MP without recovering the actor's MP.
- Guarding Draw352: adjacent enemy,6MP,1.00P. An admitted attack grants native
  Protect even on a miss, before immediate Counter damage.
- Kiku-ichimonji353: range4,height3,10MP,1.45P non-elemental.
- Centered is a T2 beneficial state. Ashura's own application turn does not
  consume a duration tick. Eligible Iaido consume once at paid execution,
  including misses. The consumed value remains available only for that
  execution's damage calculation, then retires. Ashura does not consume it.
- Centered5/4, target Exposed6/5 and the action coefficient multiply before
  one division. Samurai's native incoming stage excludes these custom actions
  from receiving a second Exposed factor. The shared payment gate preserves
  Fell's native-Immunity rejection and paid Exposed application.
- Native Dispel-family effect53 removes only Centered's packed bits; original
  ailments/buffs remain under the native dispatcher. All five original users
  (10,107,154,244,327) are covered, including Centered-only admission and query
  guards. Broad harmful-status remedies preserve Centered.
- Both native equipment setters compare the ordered primary before and after
  the complete native transaction. Changed primary clears Centered; armor,
  offhand and same-item operations that retain primary preserve it. Native AP,
  teaching, inventory and assignments remain the transaction's responsibility.
- Guarding Draw's status-law simulation applies native Protect to the native
  evaluated actor copy. The original weapon/status/element law machinery is
  retained. Confusion and Charm restrictions remain part of action admission.
  Compatibility uses native effect82, distinct from Protect's status bit25.
  The effect's native removal mask, timer cleanup and derived-unit refresh are
  retained; this includes removing Invisible. Removal-law simulation examines
  the actor's affected status rather than the struck enemy's status.

## Retained deterministic evidence

| Script/report | Result |
|---|---|
| `test-samurai-native.py` / `native-report.json` | 562 checks;358 original/previously allocated executor IDs preserved without skips;48 new combinations including active target Exposed and Centered |
| `test-samurai-lifecycle.py` / `lifecycle-report.json` | 11,012 checks; native Dispel across44 status bits, query and packed-state cases;1,000 complete equipment transactions; explicit copy ownership and both stack residues |
| `test-samurai-laws.py` / `law-report.json` | 43,744 checks; all347 native actions across20 law kinds; Guarding Protect admission and native self-removal masks across44 actor statuses and queried status IDs; live state unchanged |
| `test-samurai-in-game.py` / `game-report.json` | 275 checks; each strike selected through its Human Samurai menu, preview/cancel, bounded normal-RNG hit/miss, nativeP control, turn completion and cold SRAM suspend/resume |
| `test-samurai-retaliation.py` / `retaliation-report.json` | 78 checks; immediate native Counter after hit and miss matches a pre-Protect control and reduces positive incoming damage |
| `test-samurai-protect-native.py` / `protect-native-report.json` | 900 checks; complete unit-byte comparison against original Protect's actual dispatcher across native and custom statuses, with both stack residues |

The complete ten-step Samurai suite passed in one uninterrupted run:
`build/expansion/test-runs/20260914T225157.322346Z/report.json`. Inputs remained
unchanged throughout. This supersedes the earlier four-strike candidate and
split reports, whose Protect cleanup was less complete. The runner's seven
deterministic self-tests also pass after adding the Samurai suite.

The Counter comparison changes only the test control's Protect-grant function.
It additionally runs that control with Protect already active. At seed0,
the same64-damage outgoing strike receives70 unprotected Counter damage,
versus61 with either preexisting Protect or Guarding Draw. At seed4 the strike
misses:51 unprotected Counter damage versus37 for both protected variants.
These are native observed outcomes, not a claimed fixed Protect multiplier.

## Still required

**September14 continuation:** Murasame and Kiyomori are now implemented in
private candidate `41c51aa1f597b1bb6419166ccca3ddaa91597176`. All twelve Samurai
test steps pass on that candidate, including the six existing checks above.
See `samurai-restoration-review.md` for its exact run and additional evidence.
The four-strike results above remain the historical c683 acceptance.

Wind Draw, Moon Blossom, Higanbana/Blade Wound, Composure,
Poise, Blade Ward and Counter Draw remain unimplemented. The final class needs
all associated shared-effect composition and cross-class acceptance. The four
private strikes still need assembled integration and appropriate complete
regression; menu-help integration and broader AI/geometry/weapon-effect edges
must be covered there. This private milestone is not release acceptance.

The main d156 ROM separately has all91 declared implemented-feature regression
steps covered across resumed runs; see `build/expansion/d156-regression-coverage.json`.
Final council review remains after complete implementation and scripted checks.
