"""Actual native Fight preview/cancel/commit, turn advance and suspend cold load.

All gameplay writes are confined to disposable AP/preference fixture bytes;
original gear, abilities, stats and inventory are preserved. No user saves.
"""
import ctypes as C, hashlib, json, pathlib, runpy, shutil, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/'build/expansion/probes/battle-fixture'
if '--reuse-fixture' not in sys.argv:runpy.run_path(str(ROOT/'scripts/create-battle-fixture.py'))
OUT=ROOT/'build/expansion/probes/battle-lifecycle';OUT.mkdir(exist_ok=True)
ROM=OUT/'frozen.gba';shutil.copy2(FIX/'frozen.gba',ROM);shutil.copy2(FIX/'battle-ready.state',OUT/'initial.state')
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
guard=bytes([0xD9])*0xbc;samples=[]
def u16(ram,offset):return struct.unpack_from('<H',ram,offset)[0]
def u32(ram,offset):return struct.unpack_from('<I',ram,offset)[0]
def gear(ram):return [ram[0x80+264*i+0x2a:0x80+264*i+0x34] for i in range(24)]
def hp_values(ram):return [u16(ram,0x80+264*i+0x18) for i in range(24)]
def machine(e):
 m=a['ARM'](C.string_at(*e.maps[0x03000000]));m.put(0x08000000,ROM.read_bytes());m.put(0x02000000,e.memory());return m
def tap(e,key,wait=120):e.run(8,key);e.run(wait)
def photo(e,label):e.screenshot(OUT/(label+'.png'))
def check(e,label):
 ram=e.memory();assert ram[0x1b40:0x1e70]==ap,('AP changed',label)
 assert ram[0x1e80:0x1e98]==preferences,('Preference changed',label)
 assert ram[0x1940:0x1b40]==inventory,('Inventory changed',label)
 assert gear(ram)==original_gear,('Equipment changed',label)
 assert ram[0x3ff44:0x40000]==guard,('Reserved region overflow',label)
 heap=hp['heap'](ram);assert heap['end']==0x0203f800
 m=machine(e);manager=m.r32(0x0200f4b0);count=m.call(0x08099cdc,manager,0x02008000)
 pointers=[m.r32(m.r32(0x02008000+4*i)) for i in range(count)]
 party=[p for p in pointers if 0x02000080<=p<0x02001940 and (p-0x02000080)%264==0]
 assert count==12 and len(party)==6,(label,count,party)
 counts={1:178,2:111,3:124,4:118,5:116}
 for pointer in party:
  off=pointer-0x02000000
  assert ram[off+0x34]==counts[ram[off+6]],('Published AP count',label,hex(pointer),ram[off+0x34])
 samples.append({'label':label,'actors':count,'party':len(party),'heap':heap,
                 'hp':hp_values(ram),'jonaExperience':ram[0x398+0xa],
                 'snapshotRoot':u32(ram,0x3ff34),'manager':manager,
                 'partyPublishedCounts':[ram[p-0x02000000+0x34] for p in party]})
 photo(e,label);e.save(OUT/(label+'.state'))
 (OUT/(label+'.ram')).write_bytes(ram)
 return ram

e=h['Emulator'](ROM)
try:
 e.load(OUT/'initial.state');e.run(1);m=machine(e)
 costs=[m.get(m.call(0x080cd480,1,index),8)[7] for index in range(144,178)]
 assert min(costs)>1
 ap=bytes(1+(slot*17+i)%(costs[i]-1) for slot in range(24) for i in range(34))
 assert len(set(ap[i*34:(i+1)*34] for i in range(24)))==24
 assert all(0<value<costs[i%34] and not value&0x80 for i,value in enumerate(ap))
 preferences=bytes(i%3 for i in range(24))
 e.set_memory(0x1b40,ap);e.set_memory(0x1e80,preferences);e.set_memory(0x3ff44,guard)
 inventory=e.memory()[0x1940:0x1b40];original_gear=gear(e.memory())
 before=check(e,'initial');health=hp_values(before)
 # Native Action > Fight, select the adjacent Montblanc, inspect prediction.
 for key in [32,256,256,128,256]:tap(e,key)
 check(e,'fight-preview');assert hp_values(e.memory())==health
 for _ in range(3):tap(e,1)
 check(e,'preview-cancelled');assert hp_values(e.memory())==health
 # Re-enter, inspect the same target, then confirm native Do it.
 for key in [256,256,128,256,256]:tap(e,key)
 check(e,'fight-confirmation');assert hp_values(e.memory())==health
 tap(e,256,1200);executed=check(e,'fight-executed')
 assert u16(executed,0x1a0)==health[1]-18,('Expected native18 damage',hp_values(executed))
 assert executed[0x398+0xa]==before[0x398+0xa]+12,'Native Fight experience not awarded'
 assert hp_values(executed)==[health[0],health[1]-18,*health[2:]],'Unexpected other damage'
 # Finish Jona's turn. The next native actor is Colette in this fixed seed.
 for key in [32,32,256,256]:tap(e,key,600)
 check(e,'next-turn')
 # B exits an uncommitted unit menu; Start opens System. Up wraps to Save Now.
 for key in [1,8,16,256,256]:tap(e,key,180)
 photo(e,'suspend-confirmation');check(e,'before-suspend')
 original_sram=e.memory(0)
 tap(e,256,300);photo(e,'suspend-complete')
 saved=e.memory(0);assert saved!=original_sram,'Native suspend did not update SRAM'
 (OUT/'suspended.sav').write_bytes(saved)
finally:e.close()

# Real cold boot: never restore an emulator state for this persistence check.
e=h['Emulator'](ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 # Saved Game -> Resume Battle -> slot -> warning -> confirmation. Native
 # destructive-load confirmation defaults to No; Left chooses Yes locally.
 for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
 resumed=check(e,'cold-resumed')
 assert hp_values(resumed)==hp_values(executed),'Cold suspend load lost battle HP'
 assert resumed[0x398+0xa]==executed[0x398+0xa],'Cold suspend load lost experience'
 # Prove the restored turn remains interactive, rather than accepting a
 # plausible RAM image alone: Colette opens her ordinary native Action menu.
 tap(e,32);tap(e,256);check(e,'resumed-action-menu')
 tap(e,1);check(e,'resumed-action-cancel')
finally:e.close()
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),
        'fixture':'Native Herb Picking battle; patterned sub-mastery Human-sidecar AP and valid preferences; existing gear unchanged',
        'costs':costs,'minimumSampledFreeHeap':min(s['heap']['freePayload'] for s in samples),
        'damage':18,'experience':12,'samples':samples,
        'checks':['Twelve live actors, six canonical party pointers','Fight preview and cancel preserve AP/preferences and HP',
                  'Confirmed native Fight deals18 damage and awards12EXP','Wait advances to next turn',
                  'Native Save Now, emulator destruction, cold Resume Battle preserve AP/preferences, HP and EXP',
                  'Resumed ordinary Action menu opens and cancels','Inventory, gear and3FF44 reserved guard unchanged'],
        'scope':'Existing native combat only; no new ability effects, full mission completion or worst-case AI coverage'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))

