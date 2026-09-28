"""Source policy for the additive shop update; historical ledgers stay replayable.

Original ordinary stock is read from the authenticated clean ROM. Opening
teachers retain affordable entry prices. Later teachers cost at least the
cheapest ordinary weapon of the same family at that native tier which meets
their Attack. Above the native ceiling, use the cheapest strongest weapon.
Axes compare to two-handed swords with their existing +2 Attack allowance.
Final story-only teachers inherit the prior shipment's price floor; no new
native tier is invented. Magic/lessons/procs are not treated as Attack, and
this is a conservative price floor, not a complete balance simulation.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA1 = '7bbd46a45bcaab5482d45cb4d4965bb291045512'
PARENT = ROOT / 'build/expansion/chemist-progressions/help' / PARENT_SHA1 / 'manifest.json'
CLEAN_SHA1 = '4ac05441f4de70a4ec3dd932116346c61b8783d9'
FAMILIES = {'Sword': [1], 'Saber': [3], 'Axe': [5, 6], 'Knife': [7],
            'Rapier': [8], 'Katana': [9], 'Staff': [10], 'Rod': [11],
            'Mace': [12], 'Instrument': [16]}
TOWNS = {'Cyril': 2, 'Sprohm': 3, 'Muscadet': 4, 'Cadoan': 5, 'Baguba Port': 6}
FLAGS = [0, 774, 780, 786]

def catalog():
    """Return all 95 teachers with canonical flags, town masks and price floors."""
    clean = (ROOT / 'roms/clean/FFTA_US_clean.gba').read_bytes()
    assert hashlib.sha1(clean).hexdigest() == CLEAN_SHA1
    registry = json.loads((ROOT / 'build/expansion/registry.json').read_text())
    ids = {i['id']: i['romItemId'] for i in registry['items']}
    rows = []
    for i in json.loads((ROOT / 'notes/equipment-acquisition.json').read_text())['items']:
        rows.append(dict(id=ids[i['id']], name=i['name'], family=i['category'],
                         stage=int(i['stageId'][1:]), attack=i['weaponAttack'],
                         oldPrice=i['basePriceGil'], towns=sum(1 << TOWNS[t] for t in
                         [i['primaryShop'], *i['additionalShops']])))
    for i in json.loads((ROOT / 'notes/chemist-progression-equipment.json').read_text())['items']:
        rows.append(dict(id=i['id'], name=i['name'], family={7:'Knife',10:'Staff',12:'Mace'}[i['type']],
                         stage=int(i['stage'][1:])-1, attack=i['attack'], oldPrice=i['price'], towns=4))
    assert len(rows) == 95 and {r['id'] for r in rows} == set(range(376,471))
    for r in rows:
        r.update(flag=FLAGS[r['stage']], price=r['oldPrice'], anchors=[])
        if r['stage'] not in (1,2): continue
        pool = []
        for ident in range(1,376):
            at = 0x51d180 + ident*32
            if clean[at+8] in FAMILIES[r['family']] and clean[at+12] & (16 << r['stage']):
                pool.append((ident, clean[at+16], int.from_bytes(clean[at+4:at+6],'little')))
        assert pool, r
        target = min(r['attack']-(2 if r['family']=='Axe' else 0), max(p[1] for p in pool))
        qualifying = [p for p in pool if p[1] >= target]
        floor = min(p[2] for p in qualifying)
        r['price'] = max(r['price'], floor)
        r['anchors'] = [p[0] for p in qualifying if p[2] == floor]
    # Raising a midgame price must not make later stronger teachers cheaper.
    # Preserve the historical within-shipment price ordering as well.
    for family in FAMILIES:
        floor = 0
        for stage in range(4):
            group = [r for r in rows if r['family']==family and r['stage']==stage]
            for old in sorted({r['oldPrice'] for r in group}):
                band = [r for r in group if r['oldPrice']==old]
                floor = max([floor, *(r['price'] for r in band)])
                for r in band: r['price'] = floor
    return rows
