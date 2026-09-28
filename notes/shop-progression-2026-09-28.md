# Shop progression update

The first two new teaching-weapon shipments now unlock at the original shop
upgrades or their existing story milestones, whichever happens first. This
fixes the case where side battles unlock Flamberge and other original weapons
while new jobs still have only their opening teachers.

| Shipment | Condition | Total new weapons in Cyril |
|---|---|---:|
| Opening | Normal shop access | 20 |
| First | 10 battles OR completed Twisted Flow | 47 |
| Second | 20 battles OR completed Pale Company | 74 |
| Final | Completed Desert Patrol only | 95 |

These totals assume the preceding shipments are unlocked. Native battle
progress is cumulative; the final shipment does not acquire a battle-count
shortcut. Normal town access and each weapon's regional stock remain intact.
Physician/Sapper call their opening tier S1 in their source ledger: their
S2/S3 use the same first/second flags as the other jobs, not an extra gate.
The implementation keys off native completion flags 774/780/786 rather than
the different ledger tier names. Mission acceptance and liberated territories
do not unlock new teaching shipments. Original territory merchandise remains
available under its original rules.

## Prices

[The executable policy](../scripts/shop_progression.py) is the authoritative
final price overlay for all 95 new teachers. The historical equipment ledgers
remain inputs for replaying earlier build stages. Apply this overlay last;
do not assume rebuilding the legacy registry also installs these prices.

- Opening prices are unchanged.
- First/second shipment prices cannot undercut the cheapest ordinary original
  weapon in the same family and native tier that meets their Weapon Attack.
  Where the custom weapon exceeds that tier's ceiling, use the cheapest of
  the strongest original weapons. Axes use the existing two-handed sword
  comparison with the two-point Attack allowance.
- Existing higher prices remain. Preserve the old within-shipment price
  ordering, and carry earlier shipment price floors into later shipments.
  The final shipment has no invented fourth native tier.
- Native town/clan discounts and half-base-price resale remain. Existing owned
  copies use the new resale value too; no inventory or save migration occurs.

56 prices increase. Representative base prices:

| Weapon | Previous gil | New gil |
|---|---:|---:|
| Infernal Edge | 1,000 | 1,600 |
| Polka Foil | 1,600 | 5,000 |
| Murasame Echo | 1,600 | 10,000 |
| Mercy Mace | 3,500 | 6,000 |
| Moonblossom | 6,500 | 12,000 |

The candidate receipt lists all 95 results, their previous values and native
comparison item IDs. This is a conservative price floor, not a claim of full
campaign economy balance. Weapon stats, abilities, AP costs and job unlocks
are unchanged. Original weapons can have effects beyond their Attack; this
price comparison does not claim those effects or lesson sets are equivalent.

## Build and verification

Run from the repository root with the project's resolved Python interpreter:

```powershell
. ./scripts/resolve-python.ps1
$fftaPython = Resolve-FftaPython
& $fftaPython scripts/build-shop-progression.py
& './Test Expansion.ps1' -Plan scripts/shop-progression-test-plan.json -Only shop-progression-native,shop-progression-ui,shop-progression-learning
```

The builder requires the authenticated local parent manifest under
`build/expansion/chemist-progressions/help/7bbd46a45bcaab5482d45cb4d4965bb291045512/`.
It refuses an occupied ROM reservation, changed parent, changed original
teacher prices or changed Attack inputs. It compiles only the Buy constructor
into ROM offsets `0x1FFC000..0x1FFE000` (1,040 bytes used), imports the exact
parent inventory helpers through ARM7TDMI Thumb BX veneers, and redirects the
existing Buy entry while preserving the fourth argument (town).

Every changed byte is recorded: the new code/constant table, the old Buy
entry's 16-byte trampoline, and the 56 teacher buy/sell fields. All other ROM
bytes match the AI-speed baseline. This preserves AI code, battle stats,
abilities, artwork and save layouts. A later rebase must explicitly select and
authenticate its new parent and recheck the reservation/imported entries.

Accepted local candidate: `e13b1c7afa34fcb608a8360911b0425eb27e46fc`.
Baseline: `7bbd46a45bcaab5482d45cb4d4965bb291045512`.
Pointer: `build/expansion/shop-progression/current.json`.
Test run: `20260928T050544.713117Z`, all three steps passed with unchanged inputs.

- `shop-progression-native`: 4,320 stock combinations across all five towns,
  all six tabs, 0/7/30 territories, battle counts 0/9/10/19/20/65535, and all
  independent combinations of the three story flags. Exact original prefix,
  expected new IDs and buffer guards pass. All 375 original item records and
  original town-stock tables match the clean ROM. All 95 teacher prices pass
  in five towns and three clan ranks (1,425 quotes); native purchase commits
  pass for quantities one and three (190 purchases), with unrelated quest
  data preserved.
- `shop-progression-ui`: the retained early-town save cold-loads in mGBA.
  Fixed inputs open Sprohm's real weapon menu at 9/10/20 battles and an early
  Twisted Flow clear. The displayed new IDs match the expected shipment in
  every case, and final teachers remain absent. Native dialogs buy Infernal
  Edge for 1,440 gil after the native discount on its 1,600-gil base price.
  Screenshots, input frames and an isolated replay checkpoint are retained.
- `shop-progression-learning`: the existing Physician/Sapper prerequisites,
  AP, teaching equipment, combo and story-gated stock checks pass unchanged.

Private logs and screenshots are beside the candidate and under
`build/expansion/test-runs/`; they are ignored, not public source assets.
No full integration rerun was needed: the bounded byte audit preserves every
non-shop gameplay path and no save lifetime changed. These checks establish
shop admission, real menu execution and purchase correctness, not a full
campaign or a new AI timing measurement. The baseline AI evidence is retained.

This is a local tested update, not a published release. No player save was
read or written, and no running game was closed or restarted. A running game
continues using its loaded ROM; use an ordinary in-game save and cold Continue
when next launching this candidate.
