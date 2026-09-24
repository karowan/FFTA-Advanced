"""Native checks for compact skill names and revised Weapon Attack.

Measures every learned-ability name of the five playable races with the native
text-width routine (80161BC) on the revision candidate, and compares item and
name data with the teaching-row parent.
"""
import ast, ctypes as C, datetime, hashlib, importlib.util, json, re, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
WIDTH,LIMIT=0x080161bc,11
meta=json.loads(Path(json.loads((ROOT/'build/expansion/equipment-revision/current.json').read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
revision=meta['equipmentRevision']
parent=Path(json.loads(Path(revision['parent']).read_text())['path']).read_bytes()
assert hashlib.sha1(parent).hexdigest()==revision['baseSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
design=json.loads((ROOT/'notes/equipment-acquisition.json').read_text())
compact=dict(re.findall(r"\['([A-Z0-9-]+)','([^']+)'\]",(ROOT/'src/ability-display-names.mjs').read_text()))
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ARM','iwram_from_boot')],type_ignores=[]),'<native-harness>','exec'))
m=ARM(rom,iwram_from_boot())
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def text(image,address):
    offset=address-0x08000000;end=offset
    while image[end]:end+=2
    return image[offset:end+1]
others=revision['othersTable']
new_names={l['nameId']:l for l in registry['lessons']}
widths={}
for race in registry['races']:
    bank=struct.unpack_from('<I',clean,0x51ba84+race['id']*4)[0]&0x1ffffff
    for index in range(race['nativeCount']):
        name_id=struct.unpack_from('<H',clean,bank+index*8)[0]
        if name_id:widths.setdefault(name_id,None)
for name_id in new_names:widths[name_id]=None
for name_id in widths:
    pointer=m.word(others+name_id*4);widths[name_id]=m.call(WIDTH,pointer)
    check(widths[name_id]<=LIMIT,f'name {name_id} fits {LIMIT} tiles')
    if name_id not in new_names:
        check(text(rom,pointer)==text(parent,struct.unpack_from('<I',parent,others-0x08000000+name_id*4)[0]),f'original name {name_id} unchanged')
for lesson in registry['lessons']:
    shown=compact.get(lesson['id'],lesson['name'])
    pointer=m.word(others+lesson['nameId']*4)
    if lesson['id'] in compact:
        entry=next(n for n in revision['names'] if n['lesson']==lesson['id'])
        check(text(rom,pointer).hex()==entry.get('after',text(parent,pointer).hex()),f"{lesson['id']} shows {shown}")
    else:
        check(text(rom,pointer)==text(parent,pointer),f"{lesson['id']} keeps its approved name")
items=revision['itemTable']-0x08000000
by_name={i['name']:i['romItemId'] for i in registry['items']}
for item in design['items']:
    record=items+by_name[item['name']]*32
    check(rom[record+16]==item['weaponAttack'] and rom[record+18]==item['magicPowerBonus'],f"{item['name']} Weapon Attack {item['weaponAttack']}")
    check(item['weaponAttack']>=item.get('previousWeaponAttack',item['weaponAttack']),f"{item['name']} not weakened")
    check(rom[record:record+16]==parent[record:record+16] and rom[record+17:record+32]==parent[record+17:record+32],f"{item['name']} other fields unchanged")
check(rom[items:items+376*32]==parent[items:items+376*32],'original item records unchanged')
changed=[i for i,(a,b) in enumerate(zip(parent,rom)) if a!=b]
declared={n['offset']+k for n in revision['names'] if 'before' in n for k in range(len(n['before'])//2)}|{a['offset'] for a in revision['attacks']}
check(set(changed)<=declared and len(rom)==len(parent),'only declared name and attack bytes differ')
out=Path(meta['path']).parent/('native-revision-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=revision['baseSha1'],checks=len(checks),widthLimit=LIMIT,
    maxWidth=max(widths.values()),names=len(widths),changedBytes=len(changed))
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),maxWidth=report['maxWidth'],report=str(out/'report.json'))))
