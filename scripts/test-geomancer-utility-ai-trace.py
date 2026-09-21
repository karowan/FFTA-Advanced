"""Bounded native AI replay of the retained Geomancer utility decision failure.
Read-only instruction observers expose candidate/search admission. This is
explicitly diagnostic, not new whole-turn acceptance or an injected decision.
"""
import pathlib,json,struct,ctypes as C,runpy
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py';ns={'__file__':str(source),'__name__':'mystic_ai_trace'}
exec(compile(source.read_text(encoding='utf-8').split('# Native casts cover')[0],str(source),'exec'),ns)
m,meta,OUT=(ns[k] for k in ('m','meta','OUT'))
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R7,UC_ARM_REG_SP
rom=pathlib.Path(meta['path'])
# Exact retained scenario, not newest-file guessing.
root=rom.parent
paths=[root/'geomancer-utility-turns-20260916T142850.090084Z/377-available-3/AI-turn-start.state']
assert paths[0].is_file(),paths[0]
assert len(paths)==1,paths
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(paths[0].parent.parent/'playback.gba')
try:
 e.load(paths[0])
 # The first active-unit frame still holds the previous unit's completed node.
 # Advance the actual native setup before replaying its candidate phase.
 for setup_frames in range(1200):
  ram=e.memory()
  if int.from_bytes(ram[0x156ec:0x156ee],'little')==3 and int.from_bytes(ram[0x101fc:0x10200],'little')==int.from_bytes(ram[0xf4ec:0xf4f0],'little'):break
  e.run(1)
 else:raise AssertionError('No native Geomancer candidate phase')
 iw=C.string_at(*e.maps[0x03000000])
finally:e.close()
m.put(0x02000000,ram);m.put(0x03000000,iw)
# Replay the already initialized candidate phase. Do not reset the planner or
# borrow the previous unit's node buffer as a movement map.
assert int.from_bytes(ram[0x156ec:0x156ee],'little')==3

groups=[]
for offset in (0x5c,0x2968):
 group=0x02010210+offset;count=int.from_bytes(m.read(group+0x2908,2),'little');entries=[]
 for i in range(min(count,13)):
  p=group+i*808;w=m.word(p);u=m.word(w);n=int.from_bytes(m.read(p+804,2),'little')
  entries.append(dict(unit=hex(u),faction=m.read(u+0x29,1)[0],rows=[list(struct.unpack('<10H',m.read(p+4+k*20,20))) for k in range(min(n,40))]))
 groups.append(dict(offset=hex(offset),count=count,entries=entries))
count=int.from_bytes(m.read(0x02010210+0x58,2),'little')
available=list(struct.unpack('<'+str(min(count,40))+'H',m.read(0x02010218,min(count,40)*2)))
events=[];phases=[];nodes=[]
def observe(u,pc,size,data):
 args=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
 if pc==0x080c01d0:
  row=m.word(u.reg_read(UC_ARM_REG_SP)+4);events.append(dict(event='candidate',args=args,row=m.read(row,20).hex()))
 elif pc in (0x080bf244,0x080bf26c,0x080bf338,0x080bf350,0x080bf394):
  node=u.reg_read(UC_ARM_REG_R7);events.append(dict(event='geometry',pc=hex(pc),args=args,nodeAction=int.from_bytes(m.read(node+8,2),'little'),actorRow=m.read(args[3],20).hex() if pc==0x080bf338 and 0x02000000<=args[3]<0x0203fff0 else None))
 elif pc==0x080bdecc:events.append(dict(event='score',args=args))
 elif pc==0x080bdf8a:events.append(dict(event='native-score-result',value=args[0]))
 elif pc in (0x080bef28,0x080beac8):events.append(dict(event='search',pc=hex(pc),action=int.from_bytes(m.read(args[0]+8,2),'little')))
for pc in (0x080c01d0,0x080bdecc,0x080bdf8a,0x080bef28,0x080beac8,0x080bf244,0x080bf26c,0x080bf338,0x080bf350,0x080bf394):m.u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
for tick in range(500):
 phase=int.from_bytes(m.read(0x020156ec,2),'little');phases.append(phase)
 if phase==8:break
 m.call(0x080c045c,0x020101f8,stack=0x03007800)
 n=0x02015488;nodes.append(dict(tick=tick,phase=phase,action=int.from_bytes(m.read(n+8,2),'little'),score=m.word(n+0x1c),count=m.word(n+0x20),success=m.read(n+0x1b1,1)[0],cursor=m.read(n+0x1b8,2).hex()))
else:raise AssertionError(('bounded AI replay timeout',phases[-20:]))
assert any(x['event']=='candidate' for x in events),events
report=dict(diagnostic=True,romSha1=meta['romSha1'],sourceState=str(paths[0]),nativeSetupFrames=setup_frames,available=available,groups=groups,phases=phases,nodes=nodes,events=events,selected=m.read(0x02015488,44).hex())
(OUT/'geomancer-utility-ai-trace.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
