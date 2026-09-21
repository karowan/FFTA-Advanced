# Current native Combo and Viking casting acceptance

September 18 Pacific / September 19 UTC. Full engineering remains required;
only final artwork content is deferred. E01-E05 remain open. This checkpoint
changes test observers and acceptance coverage, not ROM code or graphics.
Current action candidate remains `5a14e6c7b69f9f9984a6965faf5740d3b318e41a`;
the installed `7507ca5c` package remains unchanged and is not engineering-complete.
All runners are terminal. No player saves, launches, agents or publication.

## Current casting

`test-connected-art-casting.py` accepts an explicit connected manifest paired
with committed report/state/RAM/IWRAM pins. `native-art-current-casting-inputs.json`
identifies the existing passed current-ROM projectile ready capture. It already
has four generic new classes allocated through native deployment; no saved actor
pointers are rewritten. The source state and memory captures remain unchanged.

Runner `20260919T042311.767519Z` passes both declared checks with unchanged inputs:

| ID | Checks | Active and composition-bypass outcome | Child report under build/art/connected/casting |
| --- | ---: | --- | --- |
| test-current-viking-thunder | 4527 | Damage 8; MP 94, cost 6 | 20260919T042312.445701Z/report.json |
| test-current-viking-thundaga | 4569 | Damage 14; MP 80, cost 20 | 20260919T042322.671572Z/report.json |

Both use actual Move, native menus, target confirmation, casting and next turn.
They check owned caster command/pixel bounds, displayed palette banks, AP and
root retirement. Thunder displays mode 63; Thundaga displays modes 11 and 63.
Minimum sampled free heap is 33668 bytes, largest block 28164. The existing
Thundaga highlight proof observes actual composition boundaries. Sampling is
every four frames: unsampled frames, every transformed color, other casting
families and maximum encounter capacity are not established by these reports.

## Nineteen class/weapon Combo initiations

`test-samurai-fight.py --combo` allocates the intended generic race/job before
native deployment, selects a permitted weapon from the actual ROM table, and
assigns the corresponding mastered Combo. The initiator starts with three JP;
the other party members have zero JP and no Combo assignment. Human expanded
AP indices use their actual side table. Moogle profiles use a disposable Viera
slot before allocation and retain its controlled base stats.

The native sequence is Move, Act, Combo, target, confirmation, execution and next
turn. Assertions cover no early debit, JP 3 to 0 once, positive nonlethal damage,
preserved assignment/mastery/inventory/equipment, root retirement and next turn.
Eight confirmation-input frames and 600 subsequent frames each validate the
class body transport and palette; another 1200-frame settle is not sampled.
Auxiliary actors are recorded but not independently accepted here.

All ten primary cases passed in runner `20260919T043314.167781Z`. All nine extra
weapon cases and the final constructor proof passed in
`20260919T044901.880508Z`. Both runners report unchanged inputs. The compact
`native-art-current-combo-evidence.json` index pins every report and records
the exact IDs, ROM, counts and outcomes; raw captures remain ignored.

| Job | Weapon type | Checks | Damage | Native-only frames |
| ---: | ---: | ---: | ---: | ---: |
| 116 | 9 | 22960 | 31 | 283 |
| 117 | 1 | 12960 | 23 | 179 |
| 117 | 5 | 7837 | 30 | 95 |
| 117 | 6 | 7837 | 32 | 95 |
| 118 | 31 | 7814 | 13 | 95 |
| 119 | 1 | 12960 | 20 | 179 |
| 119 | 5 | 7837 | 25 | 95 |
| 119 | 6 | 7837 | 27 | 95 |
| 120 | 7 | 7683 | 9 | 90 |
| 120 | 12 | 7288 | 15 | 84 |
| 121 | 11 | 9768 | 6 | 143 |
| 121 | 12 | 7288 | 15 | 84 |
| 122 | 7 | 7718 | 16 | 89 |
| 122 | 12 | 7261 | 26 | 83 |
| 123 | 16 | 9021 | 16 | 129 |
| 124 | 7 | 7718 | 16 | 89 |
| 124 | 8 | 8613 | 19 | 130 |
| 125 | 3 | 7588 | 19 | 95 |
| 125 | 8 | 8613 | 19 | 130 |

Bard knife remains Fight-only because Bard Combo requires an instrument. Thus
the 19 Combo combinations correspond to the already accepted 20 Fight weapon
combinations less Bard knife. Earlier ten primary passes remain applicable;
they were not repeated for the later afterimage observer correction.

## Retained failures and independently justified observer corrections

1. Runner `20260919T042520.592651Z` failed Samurai at attack 111; nine remaining
   cases were skipped. Capture `build/art/class-combo/20260919T042521.380450Z`
   retains the complete failure. Native composition returns before ownership
   scanning during the Combo banner: old custom tags are stale, the class body
   is absent from hardware, and eight native banner objects are displayed.
   This was an observer error, not proof of a wrongly colored visible body.
2. `test-art-native-only-oam` passed 793 checks in
   `20260919T043042.093740Z`, child
   `build/art/native-only-oam/20260919T043042.701966Z/report.json`.
   It authenticates the original 12BC routine, reproduces all 1024 OAM bytes
   through native execution at both stack residues, and compares 756 native
   clipping/bank/affine combinations. Negative controls reject incorrect OAM,
   overlay/emission/phase/refusal/mapping and any reference to retained body tiles.
3. That runner then failed Samurai at attack 121; nine cases were skipped.
   Capture `build/art/class-combo/20260919T043043.097753Z` showed foreground
   source geometry already advanced beyond the displayed frame. The observer
   now records bounded source buffers and OAM at actual native composition return
   `080004DC`, using the existing read-only instruction observer. It compares
   hardware against that boundary, never against a later foreground buffer.
   All 19 live reports retain their 608 composition events. Prior observer
   equivalence supports that mechanism; these Combo runs do not themselves claim
   a paired whole-state/frame equivalence experiment.
4. Runner `20260919T043716.744871Z` failed Human Dark Knight greatsword at attack
   326; eight cases were skipped. Capture
   `build/art/class-combo/20260919T043717.419638Z` showed the native constructor
   resetting facing 1 to flags 45. The prior observer only allowed the 65 family.
   Original 21618 sets 45 for facings 0/1 and 65 for 2/3. No ROM fix was needed.
5. The initial constructor proof passed 44 checks in runner
   `20260919T044223.009520Z`, child
   `build/art/facing-reset/20260919T044223.702050Z/report.json`, but the live
   greatsword case still failed at attack 326, capture
   `build/art/class-combo/20260919T044223.937729Z`; eight cases were skipped.
   The initial proof used current hardware as its controlled anchor, so it did
   not test actual prior-frame object counts. Consecutive real composition events
   showed the original copy retained plus a native afterimage copy.
6. Final `test-art-facing-reset` passes 58 in the final runner, child
   `build/art/facing-reset/20260919T044902.556717Z/report.json`. It uses the actual
   previous OAM event and full current native geometry reconstruction. Only the
   palette-bank nibble is excluded from geometry comparison; palette/color checks
   remain separate. Every previous body copy must still be present, the complete
   pixel allocation must be unchanged, and the direct anchor must be at most four
   frames old. Added copies require actual producer proof. The original native
   constructor reproduces the complete captured 72-byte actor; all four facings
   at both stack residues and negative field/pixel/age/hardware controls pass.
   This is controlled native execution on retained RAM with recorded prior actor
   fields restored, not reconstruction of the entire previous game state.

The shared helper is `scripts/native_oam_evidence.py`. Hidden-body acceptance
requires full native OAM equality, no active custom overlay/refusals, native
early-return phase and zero emissions, and no displayed tile span overlapping
the retained body. Geometry-only afterimage proof is deliberately distinct from
that hidden-body proof. Neither permits arbitrary stale palette tags or pixels.

## Remaining work

E02 still needs participation-chain graphics, secondary abilities and remaining
casting/effect/UI consumers, with historical gameplay evidence reused where its
inputs remain applicable. The old gameplay Combo suite already covers actual
participant membership, donor controls and cold saves; it rewrites job identities
after its old ready allocation, so do not repurpose that as new generic-body
graphics evidence. Reconcile code/data first and use fresh preallocation only
for genuinely missing rendered consumers.

E01's scoped-copy trial still has six failed response metrics and a failed entry
shadow comparison. It is not unsolvable and is not waived. Continue measured
owner/publication/planner work. E03 needs scripted/secondary spawn and entry
occupancy reconciliation before demanding reachable capacity tests. E04 needs
final campaign/save compatibility reconciliation, and E05 needs final review,
clean build with action completion, acceptance and separately playable packaging.
No engineering gate is closed by this checkpoint.
