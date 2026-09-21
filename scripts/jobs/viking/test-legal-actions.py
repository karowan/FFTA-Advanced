"""Native cross-job Reaving enumeration, MP/Silence restrictions and law groups.

This verifies legal action generation, not tactical understanding of Provoke.
"""
import pathlib as _candidate_path, sys as _candidate_sys
_candidate_sys.path.insert(0,str(_candidate_path.Path(__file__).resolve().parents[2]))
from job_test_candidate import load_candidate as _load_job_candidate
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=_load_job_candidate(ROOT/'build/expansion/probes/viking/current.json');ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();S=meta['symbols'];fix=ROM.parent/'executor'
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,TARGET,EQUIPMENT,RETURN,STACK=0x02000080,0x020033e4,0x02002000,0x08000100,0x03007000
node=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,iw);checks=collections.Counter();observations=[]
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b,globals().get('case'))
def reset(job=118,mp=50,silence=False):
 m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(0x0203ff44,bytes(8));m.call(S['ffta_job_reset'])
 m.put(UNIT+5,bytes([job,2,job,118]));m.put(UNIT+0x35,bytes([job,118 if job!=118 else 0,0]));m.put(UNIT+0x3a,bytes(3));m.put(UNIT+0x40,bytes(142));m.put(UNIT+0x40+91,b'\xff'*14)
 m.put(UNIT+0x2a,struct.pack('<5H',399,0,0,0,0));m.put(UNIT+0x18,struct.pack('<4H',200,200,mp,200));m.put(UNIT+0xe8,struct.pack('<Q',1<<27 if silence else 0))
 m.put(TARGET+0x18,struct.pack('<4H',500,500,50,50));m.put(TARGET+0xe8,bytes(8))
costs={365:6,366:0,367:6,368:8,369:12,370:10,371:20,372:18,373:6}
magic={365,369,371,372}
for job,mp,silence in itertools.product((13,14,15,16,17,18,19,118),(0,5,6,7,8,9,10,11,12,17,18,19,20,50),(False,True)):
 case=(job,mp,silence);reset(job,mp,silence);before=m.read(UNIT,264)+m.read(0x0203f400,808);rng=m.read(0x030034b0,4)
 output=0x02024000;m.put(output,b'\xd7'*256);count=m.call(0x08133f70,output,UNIT,255)
 check('bounded-native-list',count<=128,True);actions=list(struct.unpack('<'+str(count)+'H',m.read(output,count*2)))
 eligible={a for a,c in costs.items() if mp>=c and not (silence and a in magic)}
 check('cross-job-known-Reaving-actions',set(actions)&set(costs),eligible)
 for action in costs:
  check('native-usable-matches-enumeration',bool(m.call(0x08133e18,UNIT,action,255)),action in eligible)
 check('enumeration-no-live-state-writes',m.read(UNIT,264)+m.read(0x0203f400,808),before)
 check('enumeration-no-RNG',m.read(0x030034b0,4),rng)
 observations.append(dict(job=job,mp=mp,silence=silence,actions=actions))
# Native element and weapon laws must see the actual expanded record. This
# intentionally does not claim custom harmful-status application transport.
LAW=0x02024000
for action,kind,value,residue in itertools.product(costs,(2,10),range(1,33),(0,4)):
 case=('law',action,kind,value,residue);reset();m.put(LAW,bytes([0,0,0,0,kind,value])+bytes(10));m.put(STACK+residue,struct.pack('<4I',0,0,0,LAW))
 before=m.read(UNIT,264)+m.read(TARGET,264)+m.read(0x0203f400,808);rng=m.read(0x030034b0,4)
 result=m.call(0x081343c8,UNIT,TARGET,action,0,stack=STACK+residue)
 elemental=6 if action in (365,369,371) else 4 if action==372 else 0
 expected=int((kind==2 and value==elemental) or (kind==10 and value==31 and action in (367,370)))
 check('native-element-weapon-law',result,expected)
 check('law-no-live-state-writes',m.read(UNIT,264)+m.read(TARGET,264)+m.read(0x0203f400,808),before)
 check('law-no-RNG',m.read(0x030034b0,4),rng)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),observations=observations,scope=__doc__)
(ROM.parent/'legal-actions.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='observations'},indent=2))
