"""Native secret-candidate and pub access using declared eligibility inputs.

Reuse the accepted exact-ROM fixture. No campaign/field results or candidate
are supplied. Fixed queue inputs bind a carried item to a repeatable mission;
native selectors, RNG and character construction produce every candidate.
"""
import ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);rom=ROM.read_bytes();LAB=ROM.parent
ledger=json.loads((ROOT/'build/reports/secret-recruit-sources.json').read_text())
assert ledger['candidateSha1']==meta['romSha1']==hashlib.sha1(rom).hexdigest()
FIX=LAB/'fixture-two-geomancers';proof=json.loads((FIX/'prepare-cache.json').read_text())
assert proof['inputs']['romSha1']==meta['romSha1']
for name,value in proof['outputs'].items():assert hashlib.sha1((FIX/name).read_bytes()).hexdigest()==value
base=(FIX/'battle-ready.ram').read_bytes();iw=(FIX/'battle-ready.iwram').read_bytes()
acceptance_only='--acceptance-only' in sys.argv
OUT=LAB/('secret-recruit-acceptance' if acceptance_only else 'secret-recruit-access');OUT.mkdir(exist_ok=True)
tree=ast.parse((ROOT/'scripts/test-battle-inventory.py').read_text())
ROM=rom
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM helper>','exec'))
m=ARM(iw)
counts=collections.Counter();cases=[];failures=[];case=None
CANDIDATE=0x02002fc4;CACHE=0x020021c8;NODES=0x020025c8
flag_reads=[]
m.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:flag_reads.append(u.reg_read(UC_ARM_REG_R0)),begin=0x080c9540,end=0x080c9540)

def check(label,value):
 counts[label]+=1
 assert value,(case,label)

def flag(r,index,value=True):
 p=0x1f70+index//8;b=1<<(index&7);r[p]=(r[p]|b) if value else r[p]&~b

def initial(mission,item=0,done=False):
 r=bytearray(base);r[0x1e79]=2;r[0x1f70:0x2030]=bytes(0xc0)
 r[0x21c8:0x28cc]=bytes(0x704)
 # Native accepted linked-list record shape, explicitly a fixture input.
 struct.pack_into('<H',r,0x21c8,mission);r[0x21cc]=item
 struct.pack_into('<III',r,0x25c8,CACHE,0,0);struct.pack_into('<I',r,0x28c8,NODES)
 if done:flag(r,mission+0x2ff)
 return r

def candidate(r,mission,seed):
 m.put(0x02000000,r);m.put(0x03000000,iw);m.w32(0x030034b0,seed);flag_reads.clear()
 result=m.call(0x080d241c,mission,CANDIDATE)
 return result,m.get(CANDIDATE,264),list(flag_reads),m.get(0x02000000,0x40000)

def is_named(row,unit):
 if row['nameIndex'] is not None:
  return unit[4]!=0 and struct.unpack_from('<I',unit)[0]==struct.unpack_from('<I',rom,0x5516d0+row['nameIndex']*4)[0]
 return unit[4]==row['type']

try:
 for row in ([] if acceptance_only else ledger['rows']):
  routes=[(x['record'],0) for x in row['missions']]
  routes += [(60,item['id']) for item in row['carriedItems']]
  for mission,item in routes:
   case=(row['name'],mission,item);r=initial(mission,item);witness=None;misses=[];results=[]
   for seed in range(16):
    result,unit,reads,after=candidate(r,mission,seed)
    if result and is_named(row,unit):
     if witness is None:witness=(seed,unit)
     results.append(seed)
    else:misses.append(seed)
   check('native-source-produces-intended-recruit',witness is not None)
   if row['chance']<100:check('original-random-offer-can-fail',bool(misses))
   seed,unit=witness
   # A generated, unaccepted offer must remain available. The game produces
   # the second candidate from its actual post-generation saved state.
   _,_,_,after=candidate(r,mission,seed)
   result,again,reads,_=candidate(after,mission,seed)
   check('unaccepted-offer-retries',result and is_named(row,again))
   for slot in (6,23):
    occupied=bytearray(r);p=0x80+slot*264;occupied[p:p+264]=unit
    # Native duplicate identity must survive an ordinary same-race job change.
    job={1:2,2:13,3:22,4:28,5:41}.get(unit[6])
    if job is not None:occupied[p+7]=job;occupied[p+0x35]=job
    result,unused,_,_=candidate(occupied,mission,seed)
    check('existing-unique-blocks-duplicate',result==0 and not any(unused))
   if row['acceptedFlag'] is not None:
    dead=bytearray(r);flag(dead,row['acceptedFlag'])
    result,unused,reads,_=candidate(dead,mission,seed)
    check('native-prior-acceptance-blocks-offer',result==0 and not any(unused) and row['acceptedFlag'] in reads)
    history=bytearray(r);flag(history,row['historyFlag'])
    result,again,reads,_=candidate(history,mission,seed)
    check('native-history-exception-preserved',bool(result and is_named(row,again))==(mission==row['retryException']))
   if mission==111:
    accepted=bytearray(r);accepted[0x1e79]=3
    result,unused,_,_=candidate(accepted,mission,seed)
    check('added-Quin-retry-preserves-accepted-history',result==0 and not any(unused))
   cases.append(dict(name=row['name'],mission=mission,item=item,successSeeds=results,missSeeds=misses,
    candidateSha1=hashlib.sha1(unit).hexdigest(),type=unit[4],race=unit[6],job=unit[7]))
 if acceptance_only:
  for row in (x for x in ledger['rows'] if x['acceptedFlag'] is not None):
   mission=row['missions'][0]['record'];case=('native-acceptance',row['name'],mission)
   r=initial(mission);result,unit,_,after=candidate(r,mission,0)
   check('native-special-candidate',result and is_named(row,unit))
   dest=0x020006b0
   # Execute the real Yes path from its memcpy through native flag receipt.
   # Context pointers are declared; neither copied unit nor receipt is supplied.
   m.put(0x02000000,after);m.w32(0x02002c78,dest);m.w32(0x02031000,0x02000000)
   for reg,value in ((UC_ARM_REG_R0,dest),(UC_ARM_REG_R1,CANDIDATE),(UC_ARM_REG_R2,264),
     (UC_ARM_REG_R4,0x2c78),(UC_ARM_REG_R5,0x02031000),(UC_ARM_REG_SP,0x03007000)):
    m.u.reg_write(reg,value)
   m.u.emu_start(0x080807d1,0x0808083a,count=100000)
   check('native-acceptance-block-returns',m.u.reg_read(UC_ARM_REG_PC)==0x0808083a and m.u.reg_read(UC_ARM_REG_SP)==0x03007000)
   check('native-acceptance-copies-real-candidate',m.get(dest,264)==unit)
   accepted=bytearray(m.get(0x02000000,0x40000));p=0x1f70+row['acceptedFlag']//8;bit=1<<(row['acceptedFlag']&7)
   check('native-acceptance-writes-history',bool(accepted[p]&bit))
   for absent in (False,True):
    state=bytearray(accepted)
    if absent:state[dest-0x02000000:dest-0x02000000+264]=bytes(264)
    for route in row['missions']:
     result,unused,_,_=candidate(state,route['record'],0)
     check('accepted-special-never-reoffers-even-absent',not result and not any(unused))
   cases.append(dict(name=row['name'],acceptedFlag=row['acceptedFlag'],candidateType=unit[4],
    routes=[x['record'] for x in row['missions']]))
except BaseException as error:
 failures.append(dict(case=case,error=repr(error)))
 (OUT/'failure.ram').write_bytes(m.get(0x02000000,0x40000))
report=dict(passed=not failures,romSha1=meta['romSha1'],counts=dict(counts),cases=cases,failures=failures,
 inputs=dict(fixture=proof['outputs'],seeds=list(range(16)),itemMission=60),
 limits=['Candidate access with declared queue/prerequisite inputs; not pub/campaign or full recruitment UI playback.',
 'Original repeatable named-recruit absence behavior is preserved; only the newly added Quin route has the extra saved history guard.'])
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
assert not failures,failures
