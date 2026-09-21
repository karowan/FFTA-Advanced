"""Native status icon preservation and exact reserved Inoculated OBJ writes."""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
P=ROOT/'build/expansion/probes';meta=_load_job_candidate(P/'chemist/current.json');OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=OUT/'executor';ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw)
for machine in (m,n):machine.u.mem_map(0x06000000,0x20000)
counts=collections.Counter();SPRITE=0x02026000;STATE=0x0203f418

def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def reset(a):a.put(0x02000000,ram);a.put(0x03000000,iw);a.put(STATE,b'\0')
for status,key,residue in itertools.product(range(44),range(28),(0,4)):
 for a in (m,n):reset(a);a.put(UNIT+0xe8,struct.pack('<Q',1<<status))
 x=m.call(0x0809da0c,UNIT,key,stack=STACK+residue);y=n.call(0x0809da0c,UNIT,key,stack=STACK+residue)
 check('all-native-status-icons',x,y)
for active,key,residue in itertools.product((0,2,6),range(31),(0,4)):
 reset(m);m.put(STATE,bytes([active]));check('Inoculated-own-key',m.call(0x0809da0c,UNIT,30,stack=STACK+residue),30 if active else 0)
 if key>=28:
  if key<30:check("peer-keys-not-native-aliases",m.call(0x0809da0c,UNIT,key,stack=STACK+residue),0)
  continue
 reset(n);check('new-state-keeps-old-icons',m.call(0x0809da0c,UNIT,key,stack=STACK+residue),n.call(0x0809da0c,UNIT,key,stack=STACK+residue))
for icon,residue in itertools.product(range(28),(0,4)):
 for a in (m,n):reset(a);a.put(0x06010000,b'\xd7'*0x8000);a.put(SPRITE,b'\xdb'*64)
 x=m.call(meta['symbols']['ffta_chemist_status_visual'],SPRITE,icon,stack=STACK+residue)
 y=n.call(meta['upstream']['symbols']['ffta_wound_status_visual'],SPRITE,icon,stack=STACK+residue)
 check('old-glyph-return',x,y);check('old-glyph-VRAM',m.read(0x06010000,0x8000),n.read(0x06010000,0x8000));check('old-sprite-shape',m.read(SPRITE,64),n.read(SPRITE,64))
for residue in (0,4):
 reset(m);m.put(0x06010000,b'\xd7'*0x8000);m.put(SPRITE,b'\xdb'*64)
 check('reserved-tile-ID',m.call(meta['symbols']['ffta_chemist_status_visual'],SPRITE,30,stack=STACK+residue),0x1ea)
 check('VRAM-left-guard',m.read(0x06010000,0x3d40),b'\xd7'*0x3d40);check('VRAM-right-guard',m.read(0x06013d80,0x4280),b'\xd7'*0x4280)
 check('nonempty-glyph',m.read(0x06013d40,64)!=b'\xd7'*64,True)
check('central-pool-reservation',rom[0x97098:0x9709c],bytes.fromhex('f8235b00'))
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()));(OUT/'display-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
