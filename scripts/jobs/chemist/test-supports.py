"""Installed Long Throw and Pharmacology native consumers; fixed independent oracles."""
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
fix=pathlib.Path(meta['path']).parent/'executor';iw=(fix/'execute-trap.iwram').read_bytes();ram=(fix/'execute-trap.ram').read_bytes()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
m,n=ARM(rom,iw),ARM(base,iw);counts=collections.Counter();registry=json.loads((ROOT/'build/expansion/registry.json').read_text());GRID=0x02026000;COPY=0x02027000

def check(k,a,b):counts[k]+=1;assert a==b,(k,a,b)
def support(race,kind):return next(o['abilityIndex'] for l in registry['lessons'] if l['id']==kind for o in l['owners'] if o['race']==race)
def setup(machine,race=3,job=20,kind=None,pointer=UNIT,delta=0,distance=1):
 machine.put(0x02000000,ram);machine.put(0x03000000,iw);unit=bytearray(machine.read(UNIT,264));unit[5]=unit[7]=job;unit[6]=race;unit[0x2a:0x34]=bytes(10);unit[0x3a:0x3c]=bytes((0,support(race,kind) if kind else 0));unit[0xe8:0xf0]=bytes(8);unit[0xf6:0xf8]=bytes((6,6));machine.put(pointer,unit)
 grid=bytearray(bytes((16,0))*256);grid[2*(6*16+6+distance)]=16+delta;machine.put(GRID,grid)
 info=bytearray(16);struct.pack_into('<I',info,4,GRID);info[8]=info[13]=info[15]=16;machine.put(0x02007f10,info)
def invoke(machine,action,distance=1,residue=0,pointer=UNIT):
 stack=STACK+residue;machine.put(stack,struct.pack('<4I',6,action,362,0));before=machine.read(pointer,264);grid=machine.read(GRID,512)
 result=machine.call(0x080a0014,pointer,6,6,6+distance,stack=stack)
 check('geometry-unit-read-only',machine.read(pointer,264),before);check('geometry-map-read-only',machine.read(GRID,512),grid);return result
for action,residue in itertools.product(range(347),(0,4)):
 for machine in (m,n):setup(machine)
 check('original-geometry',invoke(m,action,residue=residue),invoke(n,action,residue=residue))
for race,job in ((3,20),(5,38)):
 for action,residue,pointer in itertools.product(range(432),(0,4),(UNIT,COPY)):
  setup(m,race,job,'CHM-S2',pointer);native=m.call(0x080ccd50,action,4);radius=native&63
  eligible=251<=action<=264 or 383<=action<=392 and action!=387
  expected=(native&~63)|(max(4,radius) if radius<4 else min(5,radius+1) if radius<=5 else radius) if eligible else native
  check('LongThrow-explicit-domain',m.call(meta['symbols']['ffta_chemist_range'],pointer,action,stack=STACK+residue),expected)
for race,job,action,distance,delta,residue in itertools.product((3,5),(20,),[251,383,387,392],range(1,7),(-3,-2,0,2,3),(0,4)):
 for machine in (m,n):setup(machine,race,38 if race==5 else job,'CHM-S2',delta=delta,distance=distance)
 value=invoke(m,action,distance,residue)
 # Original native geometry uses height -3..+2. Chemist adds projectile LOS;
 # flat-height distance edges independently establish the actual range hook.
 if delta==0:check('installed-range-boundary',value,int(distance<= (4 if action==251 else 3 if action==387 else 5)))
 else:
  setup(m,race,38 if race==5 else job,None,delta=delta,distance=1)
  reference=invoke(m,action,1,residue)
  if distance==1:check('height-restrictions-preserved',value,reference)
# Native magnitude callbacks, not test-injected results. Actor's support only.
CTX=0x0200f3f0;TARGET=0x020033e4
for action,amount,selector in ((251,25,35),(252,50,35),(253,150,35),(254,80,34),(383,25,35),(388,80,34)):
 for race,boost,recipient_boost,missing,residue in itertools.product((3,5),(False,True),(False,True),(0,1,24,25,26,37,38,79,80,81,300),(0,4)):
  setup(m,race,20 if race==3 else 38,'CHM-S1' if boost else None)
  target=bytearray(m.read(TARGET,264));target[6]=race;target[0xe8:0xf0]=bytes(8);target[0x3b]=support(race,'CHM-S1') if recipient_boost else 0;struct.pack_into('<4H',target,0x18,300-missing,300,300-missing,300);m.put(TARGET,target)
  m.put(CTX,struct.pack('<IIIHH',UNIT,TARGET,TARGET,action,362));before=m.read(TARGET,264)
  entry=struct.unpack('<I',m.read(0x083a86f8+selector*4,4))[0]
  value=m.call(entry,CTX,stack=STACK+residue);wanted=amount*(3 if boost else 2)//2
  # Native item HP callback intentionally leaves cap to the native HP writer.
  if action in (383,388) or action==254 and boost:wanted=min(wanted,missing)
  check('Pharmacology-user-only-native-magnitude',value,wanted);check('magnitude-read-only',m.read(TARGET,264),before)
report=dict(passed=True,romSha1=meta['romSha1'],total=sum(counts.values()),checks=dict(counts));(OUT/'support-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
