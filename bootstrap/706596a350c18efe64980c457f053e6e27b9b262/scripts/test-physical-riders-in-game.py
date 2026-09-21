"""Fresh isolated player-selected Shatter/Armor lifecycle; no user saves."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'build/expansion/probes/battle-fixture'
FIX=pathlib.Path(sys.argv[sys.argv.index('--fixture')+1]).resolve() if '--fixture' in sys.argv else DEFAULT
rom=(FIX/'frozen.gba').read_bytes();sha=hashlib.sha1(rom).hexdigest()
FAMILY=ROOT/'build/expansion/probes/physical-riders-in-game';LAB=FAMILY/sha;LAB.mkdir(parents=True,exist_ok=True)
ROM=LAB/'frozen.gba';ROM.write_bytes(rom)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));hp=runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
guard=bytes([0xd7])*0xbc;samples=[];outcomes=[];checks=0
TARGET=0x33e4
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def word(r,p):return struct.unpack_from('<I',r,p)[0]
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def check(ok,detail):
 global checks
 checks+=1
 assert ok,detail
def capture(e,label):
 r=e.memory();e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'))
 (OUT/(label+'.ram')).write_bytes(r);(OUT/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 check(r[0x3ff44:]==guard,(label,'guard'));check(hp['heap'](r)['end']==0x0203f800,(label,'heap'))
 samples.append(dict(action=action,protect=protect,label=label,HP=half(r,TARGET+0x18),MP=half(r,actor+0x1c),Protect=r[TARGET+0xeb]&2,timer=r[TARGET+0xde]))
 return r
for action,actor,item,mp,ap in [(427,0x80,456,6,0x1b5f),(428,0x398,457,8,0x398+0x40+105)]:
 if '--action' in sys.argv and action!=int(sys.argv[sys.argv.index('--action')+1]):continue
 for protect in (False,True):
  OUT=LAB/f'{action}-protect-{int(protect)}';OUT.mkdir(exist_ok=True)
  e=h['Emulator'](ROM)
  try:
   e.load(FIX/'battle-ready.state');e.run(1)
   if action==428:
    for offset in (5,7,0x35):e.set_memory(actor+offset,b'\x10')
   e.set_memory(actor+0x2a,struct.pack('<5H',item,0,0,0,0));e.set_memory(ap,bytes([0x9e if action==427 else 0x94]))
   if action==427:
    for turn in range(4):
     for key in [32,32,256]:tap(e,key)
     tap(e,256,4500 if turn==3 else 900)
   ready=e.memory();context=word(ready,0xf438)-0x02000000
   check(word(ready,context+0x18)==0x02000000+actor,('wrong actor',action,hex(word(ready,context+0x18))))
   e.set_memory(actor+0x1c,struct.pack('<HH',50,50));e.set_memory(TARGET+0x18,struct.pack('<HH',250,250))
   e.set_memory(TARGET+0xeb,bytes([(ready[TARGET+0xeb]&~2)|(2 if protect else 0)]));e.set_memory(TARGET+0xde,bytes([13 if protect else 0]))
   ready=capture(e,'ready');target_stats=ready[TARGET+0x1c:TARGET+0x2a];actor_xy=ready[actor+0xf6:actor+0xf8]
   stable=[(0x1940,ready[0x1940:0x1e70]),(0x1e80,ready[0x1e80:0x1e98]),(actor+0x2a,ready[actor+0x2a:actor+0x34])]
   # Both use actual native Move to4,14, then a separately selected technique.
   for key in ([256,128,128,32] if action==427 else [256,128,128,128]):tap(e,key)
   tap(e,256,600);capture(e,'moved')
   for key in [256,32,256,32]:tap(e,key)
   capture(e,'ability-menu')
   for key in [256,128]:tap(e,key)
   capture(e,'target-selected');tap(e,256);preview=capture(e,'preview')
   check(half(preview,0xf3fc)==action,('wrong preview action',action,half(preview,0xf3fc)))
   for r in (preview,):
    check(half(r,TARGET+0x18)==250 and half(r,actor+0x1c)==50,('query HP/MP',action))
    check(r[TARGET+0xeb]&2==(2 if protect else 0) and r[TARGET+0xde]==(13 if protect else 0),('query Protect',action))
   tap(e,1);cancel=capture(e,'cancelled')
   check(cancel[TARGET:TARGET+264]==ready[TARGET:TARGET+264],('cancel target mutation',action))
   check(half(cancel,actor+0x1c)==50 and cancel[actor+0xf6:actor+0xf8]==actor_xy,('cancel MP/move',action))
   check(hp['heap'](cancel)['freePayload']>=hp['heap'](preview)['freePayload'],'cancel heap leak')
   tap(e,256);again=capture(e,'repreview');check(hp['heap'](again)['freePayload']==hp['heap'](preview)['freePayload'],'repreview heap')
   tap(e,256);capture(e,'confirmation');seen=set();successful=None
   for seed in range(16):
    e.load(OUT/'confirmation.state');C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
    tap(e,256,1200);result=capture(e,f'seed-{seed}-executed');hit=half(result,TARGET+0x18)<250
    check(half(result,actor+0x1c)==50-mp,(action,seed,'MP cost',half(result,actor+0x1c)))
    expected_protect=2 if protect and not(action==427 and hit) else 0
    check(result[TARGET+0xeb]&2==expected_protect,(action,seed,'Protect timing',hit))
    check(result[TARGET+0xde]==(13 if expected_protect else 0),(action,seed,'Protect timer'))
    check(result[TARGET+0x1c:TARGET+0x2a]==target_stats,(action,seed,'stored target stats'))
    check(result[TARGET+0xf6:TARGET+0xf8]==bytes([5,14]),'knockback')
    check(result[actor+0xf6:actor+0xf8]==bytes([4,14]),'Move commit')
    for off,data in stable:check(result[off:off+len(data)]==data,(action,seed,'AP/inventory/gear'))
    tap(e,256,900);next_turn=capture(e,f'seed-{seed}-next-turn')
    check(word(next_turn,word(next_turn,0xf438)-0x02000000+0x18)!=0x02000000+actor,'Turn did not advance')
    outcomes.append(dict(action=action,protect=protect,seed=seed,hit=hit,damage=250-half(result,TARGET+0x18),MP=half(result,actor+0x1c)))
    seen.add(hit)
    if hit:successful=OUT/f'seed-{seed}-next-turn.state'
    if len(seen)==2:break
   check(seen=={False,True},('No actual hit/miss pair',action,protect))
   e.load(successful);expected=capture(e,'successful-next-turn')
   for key in [1,8,16,256,256]:tap(e,key)
   old=e.memory(0);tap(e,256,300);saved=e.memory(0);check(saved!=old,'Suspend did not save');(OUT/'suspended.sav').write_bytes(saved)
  finally:e.close()
  e=h['Emulator'](ROM)
  try:
   e.set_memory(0,saved,0);e.run(3600);e.set_memory(0x3ff44,guard)
   for key,wait in [(8,600),(256,600),(256,600),(256,600),(256,600),(64,60),(256,1800)]:tap(e,key,wait)
   resumed=capture(e,'cold-resumed')
   for unit,offset,size in [(actor,0x1c,2),(actor,0xf6,2),(TARGET,0x18,2),(TARGET,0xde,1),(TARGET,0xeb,1),(TARGET,0x1c,14)]:
    check(resumed[unit+offset:unit+offset+size]==expected[unit+offset:unit+offset+size],('Cold outcome mismatch',action,protect,hex(unit+offset)))
   for off,data in stable:check(resumed[off:off+len(data)]==data,('Cold AP/inventory/gear',action))
   tap(e,32);tap(e,256);capture(e,'resumed-action-menu');tap(e,1);capture(e,'resumed-action-cancel')
  finally:e.close()
report=dict(passed=True,romSha1=sha,checks=checks,outcomes=outcomes,samples=samples,fixture='Fresh private native battle; legal primary axe/job/AP, test HP/MP/Protect fixtures, native movement/menus/accuracy/application/suspend and cold reload')
report_name='report-'+sys.argv[sys.argv.index('--action')+1]+'.json' if '--action' in sys.argv else 'report.json'
(LAB/report_name).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
