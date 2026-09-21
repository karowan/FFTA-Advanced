"""Actual Fight/Combo completion for every new job's permitted weapon family.
Requires the matching successful full combo in-game fixture report. Uses only
private RAM/savestates; original user games and saves are never opened.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'build/expansion/probes/combos-in-game-tests.json').read_text())
assert report['passed'] and len(report['owners'])==10
if '--frozen' not in sys.argv:assert report['romSha1']==json.loads((ROOT/'build/expansion/probes/combat.json').read_text())['romSha1'], 'Stale combo report'
source=ROOT/'build/expansion/probes/combos-in-game'/report['romSha1']
rom=(source/'frozen.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==report['romSha1']
OUT=ROOT/'build/expansion/probes/combo-weapon-visuals'/report['romSha1'];OUT.mkdir(parents=True,exist_ok=True);ROM=OUT/'frozen.gba';ROM.write_bytes(rom)
Emulator=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
TYPES={'SAM-C1':[9],'DRK-C1':[1,5,6],'VIK-C1':[31],'GEO-C1':[11,12],'CHM-C1':[7,12],'BRD-C1':[7,16],'DNC-C1':[7,8],'MYK-C1':[3,8]}
KEYS={1:32,2:128,3:16,4:128,5:64}
profiles=json.loads((ROOT/'build/expansion/probes/job-data.json').read_text())['profiles']
for job in profiles:
 allowed=[t for t in range(1,32) if (t<20 or t==31) and job['permissionMask']&(1<<(t-1))]
 assert sorted(TYPES[job['group']+'-C1'])==allowed, ('Incomplete approved weapon coverage',job['id'],allowed)
table=struct.unpack_from('<I',rom,0x79aec)[0]-0x08000000
items={t:next(i for i in range(1,461) if rom[table+i*32+8]==t) for t in set(sum(TYPES.values(),[]))}
checks=0;rows=[]
def check(condition,detail):
 global checks
 assert condition,detail
 checks+=1

def tap(e,key):e.run(8,key);e.run(180)
for owner in report['owners']:
 unit=int(owner['unit'],16);target=int(owner['target'],16);race=owner['race'];name=owner['id']+'-race'+str(race);src=source/name
 for category in TYPES[owner['id']]:
  for command in ('Fight','Combo'):
   if command=='Combo' and owner['id']=='BRD-C1' and category==7:continue
   case=OUT/(name+'-type'+str(category)+'-'+command);case.mkdir(exist_ok=True)
   e=Emulator(ROM)
   try:
    e.load(src/'turn-ready.state');e.set_memory(unit+0x2a,struct.pack('<5H',items[category],0,0,0,0));e.set_memory(unit+0xd6,struct.pack('<H',3));e.set_memory(target+0x18,struct.pack('<HH',999,999));ready=e.memory();gear=ready[unit+0x2a:unit+0x34]
    tap(e,32);tap(e,256)
    if command=='Combo':tap(e,16)
    tap(e,256);tap(e,KEYS[race]);e.screenshot(case/'selected.png')
    # Deterministic native RNG; record hit/miss outcomes without replacing RNG.
    C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',0),4)
    for _ in range(3):tap(e,256)
    e.run(1800);expected=Image.open(src/'turn-ready.png').convert('RGB').crop((530,345,650,375));points=[i for i,p in enumerate(expected.get_flattened_data()) if min(p)>=230];assert len(points)>50
    for elapsed in range(0,6300,300):
     e.screenshot(case/'completed.png')
     pixels=list(Image.open(case/'completed.png').convert('RGB').crop((530,345,650,375)).get_flattened_data())
     if all(min(pixels[i])>=230 for i in points):break
     e.run(300)
    else:
     e.save(case/'animation-stalled.state');(case/'animation-stalled.ram').write_bytes(e.memory())
     raise AssertionError(('weapon animation did not return control',name,category,command))
    after=e.memory();check(after[unit+0x2a:unit+0x34]==gear,(name,category,command,'equipment'));check(after[unit:unit+4]==ready[unit:unit+4],(name,'identity'));check(struct.unpack_from('<H',after,unit+0xd6)[0]==(0 if command=='Combo' else 3),(name,category,command,'JP'));check(struct.unpack_from('<H',after,target+0x18)[0]>0,(name,'target survives'))
    e.save(case/'completed.state');rows.append({'job':name,'category':category,'item':items[category],'command':command,'returnedControl':True,'targetHP':struct.unpack_from('<H',after,target+0x18)[0]});print(name,category,command,'finished',flush=True)
   finally:e.close()
assert len(rows)==39, ('Incomplete weapon-family coverage',len(rows))
for job,category in {(r['job'],r['category']) for r in rows}:
 assert any(r['job']==job and r['category']==category and r['targetHP']<999 for r in rows), ('No successful hit for weapon family',job,category)
result={'passed':True,'romSha1':report['romSha1'],'checks':checks,'cases':rows,'scope':'Actual native Fight and Combo UI through animation completion for every permitted weapon family on all10 new jobs; Bard knife Fight only because its Combo requires instruments. Disposable legal equipment/mastery fixtures, no user saves.'}
(OUT/'results.json').write_text(json.dumps(result,indent=2));(ROOT/'build/expansion/probes/combo-weapon-visuals-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
