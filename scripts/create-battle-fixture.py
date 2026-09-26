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
expected_heap_end=int(sys.argv[sys.argv.index('--heap-end')+1],0) if '--heap-end' in sys.argv else 0x0203f800
if '--out' in sys.argv:OUT=(ROOT/sys.argv[sys.argv.index('--out')+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
source_rom=ROOT/'build/expansion/probes/ability-core.gba'
if '--rom' in sys.argv:source_rom=(ROOT/sys.argv[sys.argv.index('--rom')+1]).resolve()
profile_path=(ROOT/sys.argv[sys.argv.index('--party-profile')+1]).resolve() if '--party-profile' in sys.argv else None
profile=json.loads(profile_path.read_text(encoding='utf-8')) if profile_path else None
ROM=OUT/'frozen.gba';ROM.write_bytes(source_rom.read_bytes())
e=h['Emulator'](ROM)
def tap(key,wait=180):e.run(8,key);e.run(wait)
def capture(label):
 ram=e.memory()
 # 0x0203FF44/48 are the execution-scope and snapshot chain heads: battle
 # setup may open and close a scope (equipped reactions/supports), leaving 0.
 scopes=ram[0x3ff44:0x3ff4c]
 assert all(scopes[i:i+4] in (guard[:4],bytes(4)) for i in (0,4)),('Scope pointer left set',label,scopes.hex())
 assert ram[0x3ff4c:0x40000]==guard[8:],('Reserved view/AP-root guard changed',label)
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(ram)
 (OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 if label.startswith(('deployment-','battle-')):
  entry=hp['heap'](ram);assert entry['end']==expected_heap_end
  snapshots.append({'label':label,**entry})
try:
 e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,180),(256,60),(256,60),(256,180)]:tap(key,wait)
 # Full renderer hooks slightly shift the native pub transition boundary.
 # Keep the same buttons/count, but release long enough for the next dialogue
 # before sending another confirmation (old180-frame inputs lost one page).
 for _ in range(3):tap(256,240)
 for _ in range(20):tap(256,240)
 for _ in range(4):tap(1,240)
 if '--confirm-pub-exit' in sys.argv:
  # Explicit alternate route for the retained cold-entry screenshot showing
  # the modal "No missions on the board" dialogue. B cannot dismiss this page.
  # Keep the original route unchanged unless this declared option is selected.
  tap(256,300)
  for _ in range(4):tap(1,300)
 capture('accepted-world')
 if profile:
  # Declared clan inputs BEFORE native battle wrappers/sprites/turn order exist.
  # Never write battle results, fields, native allocation headers or save bytes.
  assert profile['schema']==1
  registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
  original=e.memory();assignments=[];sidecar=[]
  for entry in profile['units']:
   slot=entry['slot'];source=entry.get('copyFrom',slot)
   assert 1<=slot<6 and 1<=source<6   # slot 1 is Montblanc, the only Moogle
   address=0x80+264*slot;source_address=0x80+264*source
   unit=bytearray(original[source_address:source_address+264])
   unit[:5]=original[address:address+5] # Preserve destination slot identity/existence.
   job=entry['job'];race=unit[6]
   unit[5]=unit[7]=unit[0x35]=job;unit[8]=0;unit[0x36:0x38]=bytes(2)
   unit[0x3a:0x3c]=bytes(2);unit[0x40:0xd0]=bytes(0x90)
   struct.pack_into('<4H',unit,0x18,entry['hp'],entry['hp'],entry['mp'],entry['mp'])
   # Optional declared loadout: secondary command (selection +36 and resolved
   # job +8, as the native commit stores them) and five equipment slots.
   secondary=entry.get('secondary',0);unit[8]=unit[0x36]=secondary
   if 'equipment' in entry:struct.pack_into('<5H',unit,0x2a,*(list(entry['equipment'])+[0]*5)[:5])
   # Optional declared original-game lessons by racial ability index.
   for index in entry.get('abilityIndices',[]):
    assert 0<index<0x90;unit[0x40+index]=255
   for lesson_id in entry.get('lessons',[]):
    lesson=next(l for l in registry['lessons'] if l['id']==lesson_id)
    owner=next(o for o in lesson['owners'] if o['race']==race and o['jobId'] in (job,secondary))
    index=owner['abilityIndex']
    if index<0x90:unit[0x40+index]=255
    else:
     # Human lessons 144..177 live in the clan AP sidecar, 34 bytes per roster slot.
     assert race==1 and 144<=index<178
     sidecar.append((0x1b40+34*slot+index-144,255))
   # Optional equipped reaction/support/combo lessons (+0x3A/+0x3B/+0x3C hold racial indices).
   for field,offset in (('reaction',0x3a),('support',0x3b),('combo',0x3c)):
    if field in entry:
     lesson=next(l for l in registry['lessons'] if l['id']==entry[field])
     owner=next(o for o in lesson['owners'] if o['race']==race and o['jobId'] in (job,secondary))
     assert 0<owner['abilityIndex']<256;unit[offset]=owner['abilityIndex']
   assignments.append((address,unit))
  assert len({p for p,_ in assignments})==len(assignments)
  for address,unit in assignments:e.set_memory(address,bytes(unit))
  for address,value in sidecar:e.set_memory(address,bytes((value,)))
  capture('party-profile')
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
         'fixture':'Ordinary early-town SRAM, native pub acceptance and world travel; '+('declared pre-battle party profile, no battle results injected' if profile else 'no gameplay RAM or ROM edits'),
         'partyProfile':dict(path=str(profile_path),sha1=hashlib.sha1(profile_path.read_bytes()).hexdigest(),data=profile) if profile else None,
         'battle':'Herb Picking, Giza Plains','manager':manager,'actors':count,'partyUnitPointers':party,
         'confirmPubExit':'--confirm-pub-exit' in sys.argv,
         'otherUnitPointers':[p for p in pointers if p not in party],'heapSnapshots':snapshots,
         'guard':'0203FF44..02040000 unchanged from title through first battle turn',
         'readyState':str(OUT/'battle-ready.state'),'matchingROM':str(ROM)}
 (OUT/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='heapSnapshots'},indent=2))
 (OUT/'route.json').write_text(json.dumps({'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'tile':tile,'target':target,'path':path},indent=2))
finally:e.close()
