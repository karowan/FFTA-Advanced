"""Native AI review inputs; reuse a capture only across verified help-only edits.

This loads current executable bytes. It never re-labels an old capture as new,
and records both hashes. A code/data change requires a current-ROM capture.
"""
import ast, hashlib, json, pathlib, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
RETURN,STACK=0x08000100,0x03006800
sha=lambda b:hashlib.sha1(b).hexdigest()
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();assert sha(rom)==meta['romSha1']
FIX=OUT/'fixture-two-geomancers'
if not FIX.exists():
 patch=meta['help']['completion']
 FIX=OUT.parent/patch['inputSha1']/'fixture-two-geomancers'
 before=(FIX/'frozen.gba').read_bytes();assert sha(before)==patch['inputSha1']
 expected=bytearray(before)
 for allocation in patch['allocations']:
  p,n=allocation['offset'],allocation['bytes']
  assert before[p:p+n]==b'\xff'*n and sha(rom[p:p+n])==allocation['sha1']
  expected[p:p+n]=rom[p:p+n]
 expected[0x36d6c4:0x36d6c8]=rom[0x36d6c4:0x36d6c8]
 content=json.loads((ROOT/'build/expansion/probes/content-data.json').read_text())
 p=content['addresses']['helpBanks']-0x08000000+84
 expected[p:p+2]=rom[p:p+2]
 registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
 word=lambda p:struct.unpack_from('<I',rom,p)[0]
 for lesson in patch['lessons']:
  entry=next(l for l in registry['lessons'] if l['id']==lesson['id'])
  for owner in entry['owners']:
   p=word(word(0x257e8)-0x08000000+owner['race']*4)-0x08000000+owner['abilityIndex']*8+2
   expected[p:p+2]=rom[p:p+2]
 assert bytes(expected)==rom,'Capture reuse requires identical code, combat data and layout'
proof=json.loads((FIX/'prepare-cache.json').read_text())
for name,value in proof['outputs'].items():assert sha((FIX/name).read_bytes())==value,name
assert proof['inputs']['romSha1']==sha((FIX/'frozen.gba').read_bytes())
ram=(FIX/'battle-ready.ram').read_bytes();iw=(FIX/'battle-ready.iwram').read_bytes()
capture=dict(path=str(FIX),romSha1=proof['inputs']['romSha1'],currentRomSha1=meta['romSha1'],
 equivalence='exact' if FIX.parent==OUT else 'full byte reconstruction: help only',files=proof['outputs'])
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
m=ARM(rom,iw);S=meta['symbols']
wrappers={u+0x02000000:w+0x02000000 for u,w in from_memory(rom,ram,iw).items()}
A,T=0x02000080,0x020033e4
def call(name,*args):return m.call(S[name],*args,stack=STACK)
def state(u):return call('ffta_job_state',u)
def reset():
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8));m.put(0x0203f728,bytes(4))
 call('ffta_job_reset');m.put(m.word(0x0200f438)+4,b'\0')
 for u,j,r in ((A,123,5),(T,2,1)):
  m.put(u+5,bytes((j,r,j)));m.put(u+0x35,bytes((j,)))
  m.put(u+0x18,struct.pack('<4H',200,300,50,100));m.put(u+0x20,struct.pack('<4H',70,40,80,40))
  m.put(u+0x28,bytes(2));m.put(u+0x2a,bytes(10));m.put(u+0x3a,bytes(2));m.put(u+0xe8,bytes(8))
  m.put(u+0x0c,bytes((1,))*9);m.put(state(u),bytes(22))
 m.put(0x030034b0,bytes(4))
def protected():
 return b''.join(m.read(u,264)+m.read(state(u),22) for u in (A,T))+m.read(0x030034b0,4)+m.read(0x02001940,512)
