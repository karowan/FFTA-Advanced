"""Replay the retained missing-Chant decision; read-only native observers."""
import ctypes as C,json,runpy,struct
from ai_review_fixture import *
from unicorn import UC_HOOK_CODE
case=OUT/'bard-ai-turns-20260917T003003.939630Z/394-useful-3'
assert meta['romSha1']=='d559572aa6bb20bb44139644d6c91d0898fe38ac'
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
discovery=[]
for seed in range(32):
 e=E(case.parent/'playback.gba')
 try:
  e.load(case/'AI-turn-start.state')
  C.memmove(e.maps[0x03000000][0]+0x34b0,struct.pack('<I',seed),4)
  for setup_frames in range(1200):
   ram=e.memory()
   if int.from_bytes(ram[0x156ec:0x156ee],'little')==1 and ram[0x101fc:0x10200]==ram[0xf4ec:0xf4f0]:break
   e.run(1)
  else:raise AssertionError('no native candidate phase')
  base=int.from_bytes(ram[0x101f8:0x101fc],'little')-0x02000000
  assert 0<=base<0x3a97c,hex(base)
  n=int.from_bytes(ram[base+0x58:base+0x5a],'little');assert n<=40
  actions=list(struct.unpack('<'+str(n)+'H',ram[base+8:base+8+2*n]))
  discovery.append(dict(seed=seed,frames=setup_frames,base=hex(base),actions=actions))
  iw=C.string_at(*e.maps[0x03000000])
 finally:e.close()
 if 394 in actions:break
print(json.dumps(dict(discovery=discovery),indent=2),flush=True)
m.put(0x02000000,ram);m.put(0x03000000,iw)
base=m.word(0x020101f8)
actor=m.word(m.word(0x020101fc));count=int.from_bytes(m.read(base+0x58,2),'little')
actor_info=dict(unit=hex(actor),job=m.read(actor+5,3).hex(),mp=int.from_bytes(m.read(actor+0x1c,2),'little'),
 learned=m.read(actor+0x40+104,1).hex(),available=list(struct.unpack('<'+str(min(count,40))+'H',m.read(base+8,min(count,40)*2))),
 usableChant=m.call(0x08133e18,actor,394,128,stack=0x03007800))
n=m.call(0x08134094,0x0202f000,actor,stack=0x03007800)
actor_info['nativeLearnedActions']=list(struct.unpack('<'+str(n)+'H',m.read(0x0202f000,n*2)))
actor_info['observedGroups']=[]
for u in (0x02000080,0x020033e4,actor):
 m.put(0x03007800,bytes(8));m.put(0x0202f000,bytes(20))
 m.call(0x080c2618,0x0202f000,m.word(0x020101fc),wrappers[u],394,stack=0x03007800)
 actor_info['observedGroups'].append(dict(unit=hex(u),row=list(struct.unpack('<10h',m.read(0x0202f000,20)))))
groups=[]
for offset in (0x5c,0x2968):
 group=base+offset;count=int.from_bytes(m.read(group+0x2908,2),'little');entries=[]
 for i in range(min(count,13)):
  p=group+i*808;w=m.word(p);u=m.word(w);n=int.from_bytes(m.read(p+804,2),'little')
  entries.append(dict(unit=hex(u),faction=m.read(u+0x29,1)[0],rows=[list(struct.unpack('<10h',m.read(p+4+k*20,20))) for k in range(min(n,40))]))
 groups.append(dict(offset=hex(offset),entries=entries))
events=[];nodes=[]
def observe(u,pc,size,data):
 args=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
 if pc==0x080c01d0:
  p=m.word(u.reg_read(UC_ARM_REG_SP)+4);events.append(dict(event='candidate',row=list(struct.unpack('<10h',m.read(p,20)))))
 elif pc in (0x080bef28,0x080beac8):
  p=args[0];a=m.word(m.word(p));t=m.word(m.word(p+4))
  events.append(dict(event='search',action=int.from_bytes(m.read(p+8,2),'little'),node=hex(p),
   actor=hex(a),target=hex(t),actorXY=list(m.read(a+0xf6,2)),targetXY=list(m.read(t+0xf6,2)),
   kind=m.read(p+0x28,1)[0],stage=int.from_bytes(m.read(p+0x1b8,2),'little'),
   movement=list(m.read(m.word(p+0x214),256)),origins=m.read(m.word(p+0x200),24).hex(),
   counts=list(struct.unpack('<4h',m.read(p+0x208,8)))))
 elif pc in (0x080c359c,0x080c478c):
  p=m.word(u.reg_read(UC_ARM_REG_SP)+12)
  if 0x02000000<=p<=0x0203ffec:events.append(dict(event='willingness' if pc==0x080c359c else 'native-filter-exit',row=list(struct.unpack('<10h',m.read(p,20))),weight=u.reg_read(UC_ARM_REG_R7)))
 elif pc==0x080c281a:
  p=u.reg_read(UC_ARM_REG_R6);events.append(dict(event='created-row',row=list(struct.unpack('<10h',m.read(p,20))),filter=m.word(u.reg_read(UC_ARM_REG_SP)+20)))
for pc in (0x080c01d0,0x080bef28,0x080beac8,0x080c359c,0x080c478c,0x080c281a):m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
for tick in range(500):
 phase=int.from_bytes(m.read(0x020156ec,2),'little')
 if phase==8:break
 m.call(0x080c045c,0x020101f8,stack=0x03007800)
 p=0x02015488;nodes.append(dict(tick=tick,phase=phase,action=int.from_bytes(m.read(p+8,2),'little'),score=m.word(p+0x1c),success=m.read(p+0x1b1,1)[0]))
else:raise AssertionError('bounded planner timeout')
report=dict(diagnostic=True,discovery=discovery,romSha1=meta['romSha1'],sourceState=str(case/'AI-turn-start.state'),actor=actor_info,groups=groups,nodes=nodes,events=events,selected=m.read(0x02015488,44).hex())
(OUT/'bard-ai-trace.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
