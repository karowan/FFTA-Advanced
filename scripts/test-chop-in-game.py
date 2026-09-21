"""Native movement, Chop menu/preview/cancel/commit on a disposable battle.

Fixture gives Marche a legal two-handed Recruit Axe and mastered Chop AP.
Turn order, monster actions, movement, targeting and HP commits use game input.
"""
import ctypes as C,hashlib,json,pathlib,runpy,shutil,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/'build/expansion/probes/battle-fixture'
OUT=ROOT/'build/expansion/probes/chop-in-game';OUT.mkdir(exist_ok=True)
ROM=OUT/'frozen.gba';ROM.write_bytes((FIX/'frozen.gba').read_bytes())
control=bytearray(ROM.read_bytes());clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
control[0x1300e2:0x1300f2]=clean[0x1300e2:0x1300f2]
CONTROL=OUT/'native-P-control.gba';CONTROL.write_bytes(control)
shutil.copy2(FIX/'battle-ready.state',OUT/'initial.state')
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
a=runpy.run_path(str(ROOT/'scripts/test-battle-inventory.py'))
hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
samples=[];guard=bytes([0xd7])*0xbc;invariants=None;outcomes=[]
def u16(r,p):return struct.unpack_from('<H',r,p)[0]
def u32(r,p):return struct.unpack_from('<I',r,p)[0]
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def capture(e,label):
 r=e.memory();e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'))
 (OUT/(label+'.ram')).write_bytes(r);(OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 assert r[0x3ff44:0x40000]==guard,(label,'Reserved guard changed')
 assert hp['heap'](r)['end']==0x0203f800
 if invariants is not None:
  for offset,data in invariants:assert r[offset:offset+len(data)]==data,(label,'Persistent fixture changed',hex(offset))
 samples.append({'label':label,'targetHP':u16(r,0x33fc),'actorHP':u16(r,0x98),
                 'actorMP':u16(r,0x9c),'actorEXP':r[0x8a],'coordinates':list(r[0x176:0x178]),
                 'heap':hp['heap'](r)})
 return r
e=h['Emulator'](ROM)
try:
 e.load(OUT/'initial.state');e.run(1)
 e.set_memory(0xaa,struct.pack('<H',453));e.set_memory(0xae,b'\x00\x00');e.set_memory(0x1b5c,b'\x8a')
 # Native enemy growth rolls can vary with battle creation timing. Set its
 # HP pool explicitly, retaining generated defenses for the nativeP oracle.
 e.set_memory(0x33fc,struct.pack('<HH',250,250))
 before=capture(e,'initial')
 invariants=[(0x1940,before[0x1940:0x1e70]),(0x1e80,before[0x1e80:0x1e98]),(0xaa,before[0xaa:0xb4])]
 # Jona, Colette, Leonard and Joshua wait through the native turn system.
 for index in range(4):
  for key in [32,32,256]:tap(e,key)
  tap(e,256,4500 if index==3 else 900)
 ready=capture(e,'marche-turn')
 context=u32(ready,0xf438)-0x02000000
 assert u32(ready,context+0x18)==0x02000080,'Native turn did not reach Marche'
 assert ready[0x33e4+0xf6:0x33e4+0xf8]==bytes([5,14]),'Fixed target route changed'
 assert ready[0x1b5c]==0x8a
 # Native Move from2,13 to4,14. Unit coordinates remain uncommitted here.
 for key in [256,128,128,32]:tap(e,key)
 tap(e,256,600);moved=capture(e,'moved')
 assert moved[0x176:0x178]==bytes([2,13]),'Move preview fixture no longer exercises stale unit coordinates'
 # Action > Battle Tech > Chop, adjacent enemy Ocyth.
 for key in [256,32,256,32]:tap(e,key)
 capture(e,'chop-menu')
 for key in [256,128]:tap(e,key)
 capture(e,'target-selected')
 tap(e,256);preview=capture(e,'preview')
 assert u16(preview,0x33fc)==u16(ready,0x33fc),'Preview applied target damage'
 assert u16(preview,0x9c)==u16(ready,0x9c),'Preview charged MP'
 tap(e,1);cancelled=capture(e,'cancelled')
 assert u16(cancelled,0x33fc)==250 and cancelled[0x176:0x178]==bytes([2,13])
 assert hp['heap'](cancelled)['freePayload']>=hp['heap'](preview)['freePayload'],'Cancel leaked preview heap'
 tap(e,256);again=capture(e,'repreview')
 assert hp['heap'](again)['freePayload']==hp['heap'](preview)['freePayload'],'Reopening grew preview allocations'
 tap(e,256);confirmation=capture(e,'confirmation')
 assert u16(confirmation,0x33fc)==250 and confirmation[0x8a]==0
 # Bounded native RNG seeds must produce both outcomes. The control changes
 # only the final multiplier; no accuracy flags or hit rolls are overridden.
 seen=set();successful=None
 for seed in range(16):
  pair=[]
  for kind,path in [('native-P',CONTROL),('chop',ROM)]:
   e.close();e=h['Emulator'](path);e.load(OUT/'confirmation.state')
   C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
   tap(e,256,1200);result=capture(e,f'{kind}-seed-{seed}-executed')
   damage=250-u16(result,0x33fc);pair.append((damage,result[0x8a]))
   assert result[0x176:0x178]==bytes([4,14]),'Native move did not commit'
   assert result[0x34da:0x34dc]==bytes([5,14]),'Chop unexpectedly knocked the target back'
   assert result[0x98:0xa0]==confirmation[0x98:0xa0],'Chop changed caster HP/MP'
   if kind=='chop':
    assert bool(result[0x8a])==bool(damage),'Experience must follow actual success'
    # Move and Act consume both slots; confirm the native facing prompt.
    tap(e,256,900);next_turn=capture(e,f'seed-{seed}-next-turn')
    context=u32(next_turn,0xf438)-0x02000000
    assert u32(next_turn,context+0x18)==0x02000188,'Turn did not advance to Montblanc'
    if damage:successful=(OUT/f'seed-{seed}-next-turn.state',next_turn)
  assert pair[1][0]==pair[0][0]*11//10,('Chop coefficient versus nativeP',seed,pair)
  assert pair[0][1]==pair[1][1],('Chop changed native experience',seed,pair)
  outcomes.append(dict(seed=seed,nativeP=pair[0][0],damage=pair[1][0],experience=pair[1][1]))
  seen.add(pair[1][0]>0)
  if seen=={False,True}:break
 assert seen=={False,True},'Bounded seed set did not exercise hit and miss'
 e.load(successful[0]);e.run(1);executed=successful[1]
 # Native Save Now, with the successful hit and committed movement retained.
 for key in [1,8,16,256,256]:tap(e,key)
 capture(e,'before-suspend');old=e.memory(0);tap(e,256,300);saved=e.memory(0)
 assert saved!=old,'Native suspend did not write SRAM'
 (OUT/'suspended.sav').write_bytes(saved)
finally:e.close()

e=h['Emulator'](ROM)
try:
 e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
 for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
 resumed=capture(e,'cold-resumed')
 assert resumed[0x33fc:0x3404]==executed[0x33fc:0x3404] and resumed[0x8a]==executed[0x8a],'Cold suspend lost Chop outcome'
 assert resumed[0x176:0x178]==bytes([4,14]) and resumed[0x34da:0x34dc]==bytes([5,14])
 tap(e,32);tap(e,256);capture(e,'resumed-action-menu');tap(e,1);capture(e,'resumed-action-cancel')
finally:e.close()
report={'passedGameplayChecks':True,'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),'samples':samples,'outcomes':outcomes,'controlSha1':hashlib.sha1(control).hexdigest(),
        'fixture':'Native battle and inputs; legal Recruit Axe/no shield, mastered Chop; target HP250; bounded native RNG seeds0..15 at commit',
        'checks':['Real Move followed by valid adjacent targeting despite stale unit coordinates','Preview cancel and reopen without damage/MP charge',
                  'Native miss: zero damage and EXP','Native hit: floor11/10 of independent nativeP, nativeEXP, no knockback,0MP','Facing confirmation advances turn',
                  'Native suspend and cold Resume Battle preserve outcome, AP, inventory and gear','Resumed Action menu remains interactive'],
        'pending':['Full weapon-effect/critical/reaction/law/AI integration coverage'],
        'scope':'Chop gameplay lifecycle only; remaining custom abilities and complete balance are not accepted by this test'}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
