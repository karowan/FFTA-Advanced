# Chemist medicine reference

Chemist is available to Nu Mou and Moogles without job prerequisites. Learn its
abilities from equipment as usual. All ten medicine actions use items instead
of MP; each ingredient below means one item. A two-item recipe needs both items
and consumes each once, including when it affects several allies.

| Action | Items used | Effect |
|---|---|---|
| Potion | Potion | Ordinary Potion healing at range4 |
| Field Remedy | Choose Antidote, Eye Drops, Echo Screen or Soft | Only the chosen item's cure, range4 |
| Phoenix Down | Phoenix Down | Ordinary revival, range4 |
| High Tonic | Choose Hi-Potion or X-Potion | Only the chosen item's healing, range4 |
| Healing Mist | Potion + Hi-Potion | Ally cross within range3; heals20% max HP, minimum50 and maximum100 before applicable healing bonuses |
| Ether | Ether | Ordinary MP recovery, range4 |
| Cureall | Cureall | Cures the applicable native ailments and custom ailments listed below, range4 |
| Resuscitating Draught | X-Potion + Phoenix Down | Revives one ally at half maximum HP, range4 |
| Inoculation | Potion + Cureall | Prevents new enemy applications of the listed curable ailments for two turns, range4 |
| Guarding Draught | Potion + Soft | Ordinary Protect and Shell on one ally, range4 |

Healing and revival target eligible non-undead allies. Recovery is capped by
missing HP/MP; revival has a minimum of1 HP. Inoculation does not cure an ailment
already present. Guarding Draught does not heal.

## What preventive medicine covers

Inoculation and Auto-Cureall cover **Petrify, Toad, Poison, Blind, Sleep, Silence
and Confuse**, plus **Blade Wound, Challenged, Wisp Exposure, Polka's physical
weakening and Heathen Frolic's magical weakening**.

They do not prevent KO, Slow, Stop, Charm, Immobilize, Disable, direct damage,
forced movement or paid costs. Last Resort's linked drawback and self-inflicted
Exposed are not intercepted. Inoculation prevents an eligible application before
Auto-Cureall decides whether it needs to spend an item.

The native portion comes from the original Cureall handler's harmful-status
list. The native handler also removes Conceal as reveal bookkeeping; preventing
that beneficial status is not part of either preventive medicine.

## Mixing supports and reactions

**Pharmacology** improves eligible consumed-item HP/MP recovery by1.5, including
ordinary Item and item reactions. It does not increase revival, full recovery,
spell healing or the list of curable ailments. **Long Throw** extends eligible
single-target item actions: a shorter range becomes4; a range of4 becomes5.
It does not extend Healing Mist's area or remove line-of-sight/height rules.

Choose **Auto-Potion's Potion or Hi-Potion entry in Pick Abilities before
battle**. Both entries equip the same reaction and save a separate medicine
choice. After surviving enemy HP damage at half HP or less, it uses only that
chosen item. Empty stock does not cause a substitution. A successful use locks
the reaction until the user's next turn. The default choice is Potion.

**Auto-Cureall** spends one Cureall to prevent qualifying ailments from one
enemy action; damage still applies. It needs stock and ordinary reaction
eligibility. It does not provide a general immunity or stop an uncurable effect.

Full AP, teaching weapons and growths remain in the
[class specification](JOB-CLASS-SPECIFICATION.md) and
[equipment acquisition plan](WEAPON-ACQUISITION.md).
