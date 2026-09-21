"""Compare native saved-arrival predicate on identical captured states.

Actual pre-final save/close RAM is reused. Separate negative controls alter
only one declared gate. This is predicate/scene-queue evidence, not UI entry.
"""
import ast,datetime,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
sha=lambda b:hashlib.sha1(b).hexdigest()
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text());ROM=pathlib.Path(meta['path'])
image=ROM.read_bytes();assert sha(image)==meta['romSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert sha(clean)=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
folder=ROM.parent/'territory-scenes-20260917T121346.541215Z'
raw=(folder/'report.json').read_bytes();assert sha(raw)=='c444a0e888346c056fd473bdcc9cc4f22fa3b242'
producer=json.loads(raw);cap=next(c for c in producer['captures'] if c['label']=='after-native-save-close')
ram=(folder/'after-native-save-close.ram').read_bytes();assert sha(ram)==cap['files']['after-native-save-close.ram']
fixture=ROM.parent/'fixture';cache=json.loads((fixture/'prepare-cache.json').read_text());iw=(fixture/'battle-ready.iwram').read_bytes()
assert sha(iw)==cache['outputs']['battle-ready.iwram'] and cache['inputs']['romSha1']==meta['romSha1']
RETURN,STACK=0x08000100,0x03006800
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
OUT=ROM.parent/('final-condition-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));OUT.mkdir()
cases=[];checks=[];failure=None
def check(ok,label):
    assert ok,label
    checks.append(label)
def flag(m,i):return bool(m.read(0x02001f70+i//8,1)[0]&(1<<(i&7)))
try:
    for name,edit in [('actual-saved-arrival',None),('no-save',(75,False)),('already-cleared',(54,True)),('already-entered',(572,True))]:
        results=[]
        for label,rom in [('candidate',image),('clean',clean)]:
            m=ARM(rom,iw);m.put(0x02000000,ram);m.put(0x02002194,bytes(10))
            if edit:
                i,value=edit;a=0x02001f70+i//8;b=m.read(a,1)[0]
                m.put(a,bytes((b|(1<<(i&7)) if value else b&~(1<<(i&7)),)))
            trace=[]
            def observe(u,address,size,user):
                if address==0x080c9540:
                    i=u.reg_read(UC_ARM_REG_R0);trace.append(dict(flag=i,value=flag(m,i)))
                else:
                    ctx=u.reg_read(UC_ARM_REG_R5)
                    off=struct.unpack('<h',m.read(ctx+2,2))[0];op=m.word(ctx+4)+off
                    trace.append(dict(op=hex(op),bytes=m.read(op,6).hex()))
            h1=m.u.hook_add(UC_HOOK_CODE,observe,begin=0x080c9540,end=0x080c9540)
            h2=m.u.hook_add(UC_HOOK_CODE,observe,begin=0x0800a15a,end=0x0800a15a)
            location=m.call(0x08036350,m.read(0x02001f69,1)[0])
            result=m.call(0x0800a5d4,0);count=m.read(0x0200219c,1)[0]
            scenes=list(struct.unpack('<'+'H'*count,m.read(0x02002194,count*2))) if count else []
            row=dict(case=name,rom=label,result=result,scenes=scenes,location=location,stage=list(m.read(0x02002190,2)),
                     flags={str(i):flag(m,i) for i in (54,75,572)},trace=trace)
            cases.append(row);results.append(row);print(json.dumps(row),flush=True)
        check({k:v for k,v in results[0].items() if k!='rom'}=={k:v for k,v in results[1].items() if k!='rom'},'Candidate matches original arrival predicate:'+name)
        check((93 in results[0]['scenes'])==(edit is None),'Original final scene gate:'+name)
except BaseException as error:
    import traceback;traceback.print_exc();failure=repr(error)
report=dict(passed=failure is None,scope=__doc__,romSha1=meta['romSha1'],sourceSha1=sha(pathlib.Path(__file__).read_bytes()),
    producer=dict(report=str(folder/'report.json'),sha1=sha(raw),capture=cap),checks=checks,cases=cases,failure=failure)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),failure=failure,report=str(OUT/'report.json'))))
assert failure is None,failure
