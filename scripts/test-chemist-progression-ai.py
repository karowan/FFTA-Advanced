"""Native AI rows and placement with exact candidate code and owned memory."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
preparation=(ROOT/'scripts/test-chemist-progression-effects.py').read_text().split('\ntry:\n')[0]
exec(compile(preparation,'<shared authenticated ARM setup>','exec'))
out=Path(meta['path']).parent/'ai';out.mkdir(exist_ok=True)
checks=collections.Counter();samples=[];case=None
admissions=[]
def admission(machine,pc,size,data):
 c=machine.reg_read(UC_ARM_REG_R0)
 admissions.append(dict(case=case,context=m.read(c,0x34).hex()))
m.u.hook_add(UC_HOOK_CODE,admission,begin=meta['symbols']['ffta_cp_eligibility'],end=meta['symbols']['ffta_cp_eligibility'])
def alloc(n):
 p=m.call(0x08022840,n,stack=STACK);assert p
 m.put(p,bytes(n));return p
def formation():
 reset()
 for u,w in wrappers.items():
  x,y=(0,14) if u==UNIT else (1,13) if u==TARGET else (2,13) if u==OTHER else (0,0)
  m.put(u+0xf6,bytes((x,y)));m.put(w+8,struct.pack('<3H',x*32+16,32,y*32+16))
 m.put(UNIT+5,bytes((127,5,127)));m.put(UNIT+0x35,b'\x7f')
 m.put(UNIT+0x29,b'\x80');m.put(TARGET+0x29,b'\x80');m.put(OTHER+0x29,b'\x00')
 m.put(UNIT+0x40,bytes(0x90));m.put(UNIT+0x40+119,b'\xff')
 for u in (UNIT,TARGET,OTHER):hp(u,100,500)
 m.put(0x0200f4ec,struct.pack('<I',wrappers[UNIT]))
try:
 case='visible trap movement admission';formation();grid=alloc(16*16*7)
 call('ffta_geo_tile',grid,0,13,wrappers[UNIT]);native_tile=m.read(grid+13*16*7,7)
 check('native-hazard-control-is-walkable',bool(native_tile[0]&128),True)
 m.put(record(OTHER)+23,bytes((16,0,0xD0)))
 check('AI-sees-hostile-trap',call('ffta_cp_trap_at',UNIT,0,13)>0,True)
 call('ffta_geo_tile',grid,0,13,wrappers[UNIT])
 check('AI-avoids-visible-hostile-trap',m.read(grid+13*16*7,1)[0]&128,0)
 m.put(UNIT+0x29,b'\0');m.put(OTHER+0x29,b'\x80')
 call('ffta_geo_tile',grid,0,13,wrappers[UNIT])
 check('player-can-choose-hostile-trap',m.read(grid+13*16*7,7),native_tile)
 for action,target,expected_sign in ((446,TARGET,-1),(447,TARGET,-1),(448,TARGET,-1),(449,TARGET,-1),
       (451,TARGET,-1),(452,TARGET,-1),(453,OTHER,1),(454,OTHER,1),(455,OTHER,1),
       (456,UNIT,-1),(457,TARGET,-1),(458,TARGET,-1),(459,OTHER,1)):
  case=('native row',action);formation();row=alloc(20)
  m.put(STACK,bytes(8));m.call(meta['symbols']['ffta_ai_choice_row'],row,wrappers[UNIT],wrappers[target],action,stack=STACK)
  value=struct.unpack('<h',m.read(row+12,2))[0];count=int.from_bytes(m.read(row+10,2),'little')
  samples.append(dict(action=action,value=value,count=count,row=m.read(row,20).hex()))
  check('native-AI-admits-command',count>0,True)
  check('native-AI-correct-benefit-sign',value*expected_sign>0,True)
 case='Tripwire native placement';formation()
 group,others,move,buffer,centers,node=[alloc(n) for n in (0x290c,0x290c,256,1024,1024,0x21c)]
 for p,u in ((group,UNIT),(others,OTHER)):
  m.put(p,struct.pack('<I',wrappers[u]));m.put(p+0x2908,b'\x01\0');m.put(STACK,bytes(8))
  m.call(0x080c2618,p+4,wrappers[UNIT],wrappers[u],456,stack=STACK)
  m.put(p+804,struct.pack('<H',int(bool(int.from_bytes(m.read(p+14,2),'little')))))
 m.put(STACK,struct.pack('<5I',others,group+4,1,move,0))
 callback=m.call(0x080c01d0,node,wrappers[UNIT],wrappers[UNIT],group,stack=STACK)
 m.put(node+0x200,struct.pack('<I',centers));m.put(node+0x204,struct.pack('<I',buffer))
 movement=bytearray(b'\x80'*256)
 for x,y in ((0,14),(0,13),(0,12),(1,14),(1,12),(2,13),(2,12)):movement[y*16+x]=2
 m.put(move,movement)
 saved_ram=m.read(0x02000000,0x40000);saved_iw=m.read(0x03000000,0x8000)
 samples.append(dict(admission=m.call(0x080bdf9c,node,stack=STACK),usable=call('ffta_myk_usable',UNIT,456,128),value=call('ffta_cp_ai_value',0,UNIT,UNIT,456),node=m.read(node,0x24).hex(),cursor=m.read(node+0x1b8,2).hex()))
 m.put(0x02000000,saved_ram);m.put(0x03000000,saved_iw)
 for tick in range(257):
  if not m.call(callback,node,0,stack=STACK):break
 else:raise AssertionError('unbounded AI placement')
 success=m.read(node+0x1b1,1)[0];xy=list(m.read(node+0x1ac,4))
 samples.append(dict(case=case,callback=hex(callback),success=success,coordinates=xy,ticks=tick))
 check('native-AI-publishes-trap',success,1)
 check('native-AI-trap-center-empty',call('ffta_cp_empty_tile',UNIT,*xy[2:]),1)
 check('native-AI-movement-origin-legal',tuple(xy[:2]) in ((0,14),(0,13),(0,12),(1,14),(1,12),(2,13),(2,12)),True)
 case='Springboard native target search';formation()
 m.put(UNIT+0x40,bytes(144));m.put(UNIT+0x40+121,b'\xff')
 group,others,move,node=[alloc(n) for n in (0x290c,0x290c,256,0x21c)]
 for p,u in ((group,TARGET),(others,OTHER)):
  m.put(p,struct.pack('<I',wrappers[u]));m.put(p+0x2908,b'\x01\0');m.put(STACK,bytes(8))
  m.call(0x080c2618,p+4,wrappers[UNIT],wrappers[u],458,stack=STACK)
  m.put(p+804,struct.pack('<H',int(bool(int.from_bytes(m.read(p+14,2),'little')))))
 m.put(STACK,struct.pack('<5I',others,group+4,1,move,0))
 callback=m.call(0x080c01d0,node,wrappers[UNIT],wrappers[TARGET],group,stack=STACK)
 m.put(move,movement)
 for tick in range(257):
  if not m.call(callback,node,0,stack=STACK):break
 else:raise AssertionError('unbounded Springboard search')
 samples.append(dict(case=case,node=m.read(node+0x1ac,6).hex(),ticks=tick))
 check('AI-selects-threatened-ally',m.read(node+0x1b1,1),b'\x01')
 check('AI-targets-actual-ally-tile',m.read(node+0x1ae,2),bytes((1,13)))
 result=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),samples=samples)
except BaseException as error:
 result=dict(passed=False,romSha1=meta['romSha1'],checks=dict(checks),case=case,error=repr(error),samples=samples,admissions=admissions[-20:]);raise
finally:(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
