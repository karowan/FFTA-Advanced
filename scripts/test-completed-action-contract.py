"""Bounded native constructor, preservation and rebuild proof for action completion.

All existing land/water graphs and native jobs remain byte-identical through
their actual pointers. Each added sequence preserves the original command stream
and uses only the focus class's generated pixels. Native constructor execution
covers all four facings. Actual Fight playback is accepted in separate reports.
"""
import ast, datetime, hashlib, importlib.util, json, struct, sys
from pathlib import Path
from native_art import ROOT, TILES, OAM, sha, layout
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
text=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/action-completion/contracts'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];constructors=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
w=lambda r,p:struct.unpack_from('<I',r,p)[0]
h=lambda r,p:struct.unpack_from('<H',r,p)[0]
try:
    view_path=ROOT/'build/art/action-completion/current.json';view=json.loads(view_path.read_bytes())
    connected_path=Path(view['connectedManifest']);connected=json.loads(connected_path.read_bytes())
    component=connected['components']['actionCompletion'];source_path=Path(component['sourceManifest']);source_raw=source_path.read_bytes()
    check(sha(source_raw)==component['sourceManifestSha256'],'Exact parent manifest authenticated')
    parent=json.loads(source_raw);original=Path(parent['path']).read_bytes();rom=Path(view['path']).read_bytes()
    check(hashlib.sha1(original).hexdigest()==parent['romSha1']==component['baseRomSha1'],'Exact parent ROM authenticated')
    check(hashlib.sha1(rom).hexdigest()==view['romSha1']==component['romSha1']==connected['romSha1'],'Exact completed candidate authenticated')
    check([(r['job'],r['slot'],r['donorJob']) for r in component['entries']]==[(122,42,39),(122,43,39),(122,60,42),(122,61,42),(123,42,39),(123,43,39)],'Explicit six-entry completion scope')
    table=w(rom,0x2102c)-0x08000000
    check(table==w(original,0x2102c)-0x08000000,'Existing extended native table address retained')
    added={(e['resource'],e['slot']) for e in component['entries']}
    changed={e['resource'] for e in component['entries']}
    for resource in range(277):
        old=w(original,table+resource*4)-0x08000000;new=w(rom,table+resource*4)-0x08000000
        if resource not in changed:check(old==new,str(resource)+' original table entry unchanged')
        if 256<=resource<276:
            for slot in range(84):
                before=original[old+slot*12:old+(slot+1)*12];after=rom[new+slot*12:new+(slot+1)*12]
                if (resource,slot) in added:
                    check(before==bytes(12) and w(after,0)!=0,str((resource,slot))+' only an absent descriptor completed')
                else:check(before==after,str((resource,slot))+' existing complete descriptor and graph pointer unchanged')
    allowed=set(range(*component['used']))
    for resource in changed:allowed.update(range(table+resource*4,table+resource*4+4))
    check(len(original)==len(rom) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom))),
          'Every old graph byte, native job, code hook, palette and save consumer unchanged outside two table entries')
    for entry in component['entries']:
        resource,slot=entry['resource'],entry['slot'];label=str((resource,slot))
        descriptor=w(rom,table+resource*4)-0x08000000+slot*12
        donor=w(original,table+entry['donorResource']*4)-0x08000000+slot*12
        q,nq=w(original,donor)-0x08000000,w(rom,descriptor)-0x08000000
        count=w(original,q)
        check(q==entry['sourceSequence'] and nq==entry['sequence'] and w(rom,nq)==count,label+' native count and declared pointers')
        check(rom[descriptor+4:descriptor+12]==original[donor+4:donor+12],label+' exact native descriptor metadata')
        source_desc=w(original,table+resource*4)-0x08000000
        idle=w(original,source_desc+(slot%2)*12)-0x08000000+4
        generated=TILES+w(original,idle)
        for index in range(count):
            old_frame=original[q+4+20*index:q+24+20*index];new_frame=rom[nq+4+20*index:nq+24+20*index]
            check(new_frame[8:]==old_frame[8:],label+'/'+str(index)+' all native command duration event fields exact')
            if old_frame[9]!=1 or struct.unpack_from('<II',old_frame)==(0xffff,0xffffffff):
                check(new_frame==old_frame,label+'/'+str(index)+' control record unchanged');continue
            t,o=struct.unpack_from('<II',new_frame);objects,_=layout(rom,OAM+o)
            check(TILES+t==generated and rom[TILES+t:TILES+t+512]==original[generated:generated+512],label+'/'+str(index)+' actual class imagegen pixels retained')
            check(len(objects)==1 and objects[0]['width']==objects[0]['height']==32 and objects[0]['tile']==0,label+'/'+str(index)+' native sixteen-tile allocation bound')
    capture=ROOT/'build/art/class-fight/20260919T022121.606456Z'
    ram=(capture/'failed.ram').read_bytes();iw=(capture/'failed.iwram').read_bytes()
    check(sha(ram)=='b9a68e508c50acb9074e75241abd89846be7dea2c6a40c8c3ccb8e8af84182c4' and sha(iw)=='7097aa69cca72d9d495e3506ae71a563b7b684431809d0ba5e2bc654b253cf4b','Detached native context authenticated')
    for job,mode in ((122,84),(122,120),(123,84)):
        for facing in range(4):
            unit,wrapper,body=0x020005a8,0x020229d8,0x02020e28;resource=256+2*(job-116)
            machine=ARM(rom,iw);machine.put(0x02000000,ram)
            machine.put(unit+5,bytes((job,5,job)));machine.put(wrapper+0x34,struct.pack('<H',resource));machine.put(wrapper+0x44,struct.pack('<I',body))
            before=machine.read(unit,264);machine.call(0x080975dc,wrapper,mode,facing,0)
            slot=(mode//4)*2+(1 if facing in (1,2) else 0)
            descriptor=w(rom,table+resource*4)-0x08000000+slot*12;sequence=w(rom,descriptor)
            check(machine.word(wrapper+0x44)==body,str((job,mode,facing))+' native constructor keeps valid body')
            check(machine.read(body+6,4)==struct.pack('<HH',resource,mode+facing) and machine.word(body+0x34)==sequence+4,
                  str((job,mode,facing))+' native constructor selects completed generated sequence')
            check(machine.read(unit,264)==before,str((job,mode,facing))+' native constructor leaves unit equipment and progression intact')
            constructors.append(dict(job=job,mode=mode,facing=facing,resource=resource,sequence=sequence))
    protected=[source_path,connected_path,view_path,ROOT/'build/art/pipeline/delivery/current.json',ROOT/'build/art/connected/current.json']
    snapshots={p:p.read_bytes() for p in protected}
    spec=importlib.util.spec_from_file_location('completion_rebuild',ROOT/'scripts/complete-generated-actions.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rebuilt=module.build(source_path)
    check(rebuilt['romSha1']==view['romSha1'] and Path(rebuilt['path']).read_bytes()==rom,'Exact deterministic completion-stage rebuild')
    check(all(p.read_bytes()==raw for p,raw in snapshots.items()),'Historical parent, candidate provenance and installed indexes unchanged')
    report=dict(status='passed',romSha1=view['romSha1'],parentRomSha1=parent['romSha1'],checks=checks,constructors=constructors,
        candidateManifestSha256=sha(connected_path.read_bytes()),scope=__doc__,
        reuse='Existing e1a87ecd land/water graphs and hardware palette interpretation remain exact; six formerly absent land entries are additions. This does not supply new current compositor, water attack, secondary-action, capacity or campaign runtime evidence.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,constructors=constructors),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
