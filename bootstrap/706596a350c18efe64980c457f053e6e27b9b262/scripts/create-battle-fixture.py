"""Create a disposable native Ivalice battle fixture without campaign playthrough."""
import pathlib,runpy,struct,ctypes as C,json,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
guard=bytes([0xD7])*0xbc
snapshots=[]
OUT=ROOT/'build/expansion/probes/battle-fixture'
if '--out' in sys.argv:OUT=(ROOT/sys.argv[sys.argv.index('--out')+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
source_rom=ROOT/'build/expansion/probes/ability-core.gba'
if '--rom' in sys.argv:source_rom=(ROOT/sys.argv[sys.argv.index('--rom')+1]).resolve()
ROM=OUT/'frozen.gba';ROM.write_bytes(source_rom.read_bytes())
e=h['Emulator'](ROM)
def tap(key,wait=180):e.run(8,key);e.run(wait)
def capture(label):
 ram=e.memory()
 assert ram[0x3ff44:0x40000]==guard,('Reserved view/AP-root guard changed',label)
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(ram)
 (OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 if label.startswith(('deployment-','battle-')):
  entry=hp['heap'](ram);assert entry['end']==0x0203f800
  snapshots.append({'label':label,**entry})
try:
 e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(key,wait)
 for _ in range(3):tap(256)
 for _ in range(20):tap(256)
 for _ in range(4):tap(1)
 capture('accepted-world')
 # Native placement lookup and coordinates are evaluated against this live
 # world state. Movement itself uses ordinary game input, never RAM writes.
 m=a['ARM'](C.string_at(*e.maps[0x03000000]));m.put(0x08000000,ROM.read_bytes());m.put(0x02000000,e.memory())
 tile=m.call(0x08036330,8);assert tile==20
 target=(m.call(0x08035a20,tile-1)+6,m.call(0x08035a44,tile-1)+4)
 path=[]
 for _ in range(600):
  x,y=struct.unpack_from('<HH',e.memory(),0x2c16)
  if abs(x-target[0])<=2 and abs(y-target[1])<=2:break
  key=(128 if x<target[0] else 64) if abs(x-target[0])>2 else (32 if y<target[1] else 16)
  e.run(1,key);path.append([x,y,key])
 else:raise AssertionError(('World cursor never reached Giza',target,x,y))
 e.run(30);capture('giza-cursor');tap(256,1200);capture('mission-menu')
 for i in range(7):tap(256,600);capture('deployment-'+str(i))
 # Marche and Montblanc are already placed. Add all four generic members
 # through unit selection, deployment square and facing confirmation.
 for _ in range(3):tap(256)
 capture('deployment-three')
 for i in range(3):
  for key in [128,256,256,256]:tap(key)
  capture('deployment-'+str(i+4)+'-units')
 tap(8,600);capture('deployment-confirm')
 tap(256,600);capture('battle-intro')
 tap(256,600)
 # Frame-count assumptions drift when engine work changes native timing.
 # Observe the real menu before publishing a ready-to-input fixture.
 ready_wait_frames=observe['wait_for_menu'](e)
 capture('battle-ready')
 m=a['ARM'](C.string_at(*e.maps[0x03000000]));m.put(0x08000000,ROM.read_bytes());m.put(0x02000000,e.memory())
 manager=m.r32(0x0200f4b0)
 count=m.call(0x08099cdc,manager,0x02008000)
 pointers=[m.r32(m.r32(0x02008000+4*i)) for i in range(count)]
 party=[p for p in pointers if 0x02000080<=p<0x02001940 and (p-0x02000080)%264==0]
 assert count==12 and len(party)==6,(count,party)
 report={'passed':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),
         'readyWaitFrames':ready_wait_frames,
         'readyObservation':'Native Wait and Status labels, bright strokes plus dark outlines; no input while waiting',
         'readyAnchorSha256':hashlib.sha256((ROOT/'scripts/fixtures/native-turn-menu.json').read_bytes()).hexdigest(),
         'fixture':'Ordinary early-town SRAM, native pub acceptance and world travel; no gameplay RAM or ROM edits',
         'battle':'Herb Picking, Giza Plains','manager':manager,'actors':count,'partyUnitPointers':party,
         'otherUnitPointers':[p for p in pointers if p not in party],'heapSnapshots':snapshots,
         'guard':'0203FF44..02040000 unchanged from title through first battle turn',
         'readyState':str(OUT/'battle-ready.state'),'matchingROM':str(ROM)}
 (OUT/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='heapSnapshots'},indent=2))
 (OUT/'route.json').write_text(json.dumps({'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'tile':tile,'target':target,'path':path},indent=2))
finally:e.close()
