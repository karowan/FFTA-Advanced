"""Actual native paging, Samurai job change, menu reopen and cold saved-game load.

The disposable fixture masters Marche's lessons to expose all13Human jobs.
It does not claim gameplay AP progression or custom combat-effect completion.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
OUT=ROOT/'build/expansion/probes/job-wheel-in-game';OUT.mkdir(exist_ok=True)
ROM=OUT/'frozen.gba';ROM.write_bytes((OUT.parent/'job-ui.gba').read_bytes())
guard=bytes([0xd7])*0xbc;checks=[];captures=[]
def tap(e,key,wait=180):e.run(8,key);e.run(wait)
def cold(seed):
 e=h['Emulator'](ROM);e.set_memory(0,seed,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(e,key,wait)
 return e
def wheel(e):
 ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
 count=struct.unpack_from('<I',ram,p+0x1270)[0]
 assert 0<count<=12,count
 ids=[x&127 for x in ram[p+0x1278:p+0x1278+count]]
 assert len(set(ids))==count and all(ids)
 return p,ids
def capture(e,name):
 ram=e.memory();assert ram[0x3ff44:0x40000]==guard,('guard',name)
 assert [x&127 for x in ram[0xc0:0x14e]]==[100]*142,('inlineAP',name)
 assert [x&127 for x in ram[0x1b40:0x1b62]]==[100]*34,('extraAP',name)
 e.screenshot(OUT/(name+'.png'));captures.append(name)
e=cold((ROOT/'build/test-lab/early-town.sav').read_bytes())
try:
 e.set_memory(0xc0,bytes([100])*142);e.set_memory(0x1b40,bytes([100])*34)
 for key in [8,256,256,32,32]:tap(e,key)
 tap(e,256,600)
 _,first=wheel(e);assert first==list(range(2,9)),first;capture(e,'01-human-page1')
 tap(e,2048,600);_,second=wheel(e);assert second==[9,10,11,12,116,117],second;capture(e,'02-human-page2')
 for i,key in enumerate([1024,2048,1024,2048]):
  tap(e,key,600);assert wheel(e)[1]==(first if i%2==0 else second)
 capture(e,'03-repeat-paging');checks.append('All13Human jobs through7+6nativewheel pages with repeatedL/R')
 # From second-page index0, two left rotations select Samurai116.
 for key in [64,64]:tap(e,key)
 p,_=wheel(e);ram=e.memory();selected=ram[p+0x1287+28*ram[p+0x1275]]
 assert selected==116,selected
 tap(e,256,300);tap(e,1,300)
 assert e.memory()[0x87]==2,'Cancel must not change job';capture(e,'04-cancel-confirm')
 tap(e,256,300);tap(e,64);tap(e,256,1000)
 ram=e.memory();assert ram[0x87]==116 and ram[0xb5]==116,(ram[0x87],ram[0xb5])
 capture(e,'05-samurai-changed');checks.append('Native confirmation/cancel and C8C24job change toSamurai116')
 for key in [1,1,1]:tap(e,key,240)
 for key in [8,256,256,32,32]:tap(e,key)
 tap(e,256,600);p,ids=wheel(e);ram=e.memory()
 assert ids==second and ram[p+0x1287+28*ram[p+0x1275]]==116
 capture(e,'06-reopen-current-page');checks.append('Reopening selects currentSamurai on its correct page')
 for key in [1,1,1]:tap(e,key,240)
 for key,wait in [(8,180),(16,180),(256,180),(256,60),(256,60),(64,20),(256,300)]:tap(e,key,wait)
 saved=e.memory(0);assert saved!=(ROOT/'build/test-lab/early-town.sav').read_bytes()
 (OUT/'test-save.sav').write_bytes(saved)
finally:e.close()
e=cold(saved)
try:
 assert e.memory()[0x87]==116 and e.memory()[0xb5]==116
 capture(e,'07-cold-load');checks.append('Native save and fresh emulator load preserve job/command/AP; reservedguard intact')
finally:e.close()
report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'checks':checks,'captures':captures,
 'scope':'Native rendered Humanwheel, syntheticmastery fixture, Samurai jobchange, no customcombat claim'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
