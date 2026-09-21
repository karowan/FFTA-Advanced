"""Actual native overkill/empty-pool/undead drain results from accepted UI frames."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
meta,LAB,_,_=runpy.run_path(str(ROOT/'scripts/dark-sword-test-input.py'))['load_input']('--current' in sys.argv)
ROM=pathlib.Path(meta['path']);assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1'];h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
checks=0;outcomes=[];T=0x33e4
def half(r,p):return struct.unpack_from('<H',r,p)[0]
def check(a,b,case):
 global checks
 checks+=1;assert a==b,(case,a,b)
for job,actor in ((119,0x398),(117,0x80)):
 for action,cost in ((357,6),(358,4)):
  state=LAB/f'game-{job}-{action}/confirmation.state';assert state.exists(),'Run fresh dark-sword-in-game first'
  for hp,mp,undead,actor_hp in ((3,49,0,20),(250,0,0,20),(250,3,0,20),(250,49,1,1),(250,49,1,20)):
   name=f'{job}-{action}-hp{hp}-mp{mp}-undead{undead}-actor{actor_hp}';e=h['Emulator'](ROM)
   try:
    for seed in range(16):
     e.load(state);e.set_memory(actor+0x18,struct.pack('<H',actor_hp));e.set_memory(T+0x18,struct.pack('<HHHH',hp,250,mp,49))
     r=e.memory();e.set_memory(T+0xe8,bytes([(r[T+0xe8]&~4)|undead*4]));C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
     e.run(8,256);e.run(1500);r=e.memory();removed=max(0,hp-half(r,T+0x18))
     if not removed:continue
     if action==357:
      amount=min(removed//2,20);wanted_hp=max(0,actor_hp-amount) if undead else min(100,actor_hp+amount);wanted_mp=20-cost;target_mp=mp
     else:
      amount=min(removed//5,16,mp);wanted_hp=actor_hp;wanted_mp=max(0,20-cost-amount) if undead else min(50,20-cost+amount);target_mp=mp-amount
     check(half(r,actor+0x18),wanted_hp,(name,'actorHP'));check(half(r,actor+0x1c),wanted_mp,(name,'actorMP'));check(half(r,T+0x1c),target_mp,(name,'targetMP'))
     check(r[0x3ff44:],b'\xd7'*0xbc,(name,'guard'))
     e.screenshot(LAB/(name+'.png'));e.save(LAB/(name+'.state'));outcomes.append(dict(case=name,seed=seed,removed=removed,actorHP=wanted_hp,actorMP=wanted_mp,targetMP=target_mp));break
    else:raise AssertionError(('No successful native hit',name))
   finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,outcomes=outcomes);(LAB/'resource-edges-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
