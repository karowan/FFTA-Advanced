"""Native actor mode/phase consumption of the partial Samurai support-pose map.

The retained RAM is an authenticated allocator context only. This invokes real
native actor construction/setters, not live battle actions or a display proof.
"""
import ast,copy,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,TILES,OAM,sha,layout
from live_action_plan import LiveActionPlan
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
code=(ROOT/'scripts/test-equipment-legality.py').read_text(encoding='utf-8')
code=code.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(code)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/refinement/samurai-support-v1/current.json').read_text(encoding='utf-8'))
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
out=ROOT/'build/art/refinement/samurai-support-native'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];modes=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    parent=json.loads((Path(meta['source']).parent/'manifest.json').read_text(encoding='utf-8'))
    original=Path(meta['source']).read_bytes();assert hashlib.sha1(original).hexdigest()==parent['romSha1']==meta['baseRomSha1']
    plan_path=ROOT/'src/art/imagegen/samurai-support-v1-plan.json';plan_spec=json.loads(plan_path.read_text(encoding='utf-8'))
    colors=rom[meta['symbols']['ffta_art_custom_colors']-0x08000000:meta['symbols']['ffta_art_custom_colors']-0x08000000+32]
    plan=LiveActionPlan(plan_path,116,original,parent['resources'],colors)
    expected={(r['resource'],r['slot'],r['index']):r for r in meta['actionPlans'][0]['assignments']}
    check(set(plan.bindings)==set(expected),'Reconstructed exact original-pose assignment coverage')
    native=json.loads((ROOT/'build/art/native-reference/actor-004/native.json').read_text(encoding='utf-8'))
    native_expected={key:[] for key in [p['nativePose'] for p in plan_spec['resources'][0]['poses']]}
    for slot in native['slots']:
        for frame,item in enumerate(slot['frames']):
            if item['pose'] in native_expected:native_expected[item['pose']].append((256,slot['slot'],frame))
    check(set(expected)=={k for keys in native_expected.values() for k in keys},'Every native occurrence replaced; no positional cycling substitute')
    candidates=[]
    for p in (ROOT/'build/art/class-resources/width-tests').glob('*/report.json'):
        proof=json.loads(p.read_text(encoding='utf-8'))
        if proof.get('status')=='passed':candidates.append((p,proof))
    proof_path,proof=sorted(candidates)[-1];stem=Path(proof['capture'])/'private-slot2-wheel'
    ram=stem.with_suffix('.ram').read_bytes();iw=stem.with_suffix('.iwram').read_bytes()
    check(sha(ram)==proof['sources']['private']['ramSha256'] and sha(iw)==proof['sources']['private']['iwramSha256'],'Retained allocator context authenticated')
    a=ARM(rom,iw);a.put(0x02000000,ram)
    for address,size in ((0x04000000,0x10000),(0x05000000,0x1000),(0x06000000,0x20000),(0x07000000,0x1000),(0x10000000,0x2000)):a.u.mem_map(address,size)
    widget=0x10000000;a.put(STACK,struct.pack('<6I',0,256,0,1,1,0));a.call(0x08029864,widget,2,2,7)
    a.u.reg_write(UC_ARM_REG_R5,widget);a.u.reg_write(UC_ARM_REG_SP,STACK-0x34);a.u.emu_start(0x080299a7,0x08029a0a,count=50000)
    check(a.u.reg_read(UC_ARM_REG_PC)==0x08029a0a,'Actual native widget actor constructed')
    rows={r['slot']:r for r in meta['assignments'] if r['resource']==256}
    seen=set()
    for slot in sorted({s for r,s,f in expected}):
        row=rows[slot]
        for direction in ((1,2) if slot%2 else (0,3)):
            mode=(slot//2)*4+direction;modes.append(mode);a.call(0x08029cd8,widget,mode,0);actor=a.word(widget+0x7c)
            check(struct.unpack('<HH',a.read(actor+6,4))==(256,mode),'Native identity/mode '+str(mode))
            check(a.word(actor+0x34)==0x08000000+row['sequence']+4,'Native descriptor resolves action sequence '+str(mode))
            for frame,new in enumerate(row['frames']):
                key=(256,slot,frame)
                if key not in expected:continue
                a.call(0x08021e28,actor,frame);entry=a.word(actor+0x38)
                check(entry==0x08000000+row['sequence']+4+frame*20,'Native phase setter resolves exact frame '+str((mode,frame)))
                tile,oam=struct.unpack('<II',a.read(entry,8));objects,_=layout(rom,OAM+oam)
                check(len(objects)==1 and objects[0]['width']==objects[0]['height']==32 and objects[0]['tile']==0,'Bounded action layout '+str((mode,frame)))
                pose,ref=plan.frame(*key)
                check(sha(rom[TILES+tile:TILES+tile+512])==new['tileSha256']==sha(__import__('native_art').pack_tiles(pose,16)),'Native frame points to exact generated support pixels '+str((mode,frame)))
                seen.add(ref['nativePose'])
    check(len(seen)==10,'Native consumers resolve all eight support and both neutral poses')
    plan.report()
    invalid=[]
    v=copy.deepcopy(plan_spec);v['coverage']='complete';invalid.append(('false-full-art',v))
    v=copy.deepcopy(plan_spec);v['job']=118;invalid.append(('wrong-job',v))
    v=copy.deepcopy(plan_spec);v['assets']['support']['sourceSha256']='0'*64;invalid.append(('wrong-source',v))
    v=copy.deepcopy(plan_spec);v['resources'][0]['poses'][2]['nativeTileSha256']='0'*64;invalid.append(('wrong-native-pose',v))
    v=copy.deepcopy(plan_spec);v['resources'][0]['poses'][2]['frame']=99;invalid.append(('outside-generated-sheet',v))
    v=copy.deepcopy(plan_spec);v['resources'][0]['poses'].append(v['resources'][0]['poses'][0]);invalid.append(('duplicate-pose',v))
    v=copy.deepcopy(plan_spec);v['resources'][0]['poses'][2]['nativePose']='ffffff-ffffff';invalid.append(('unused-pose',v))
    for name,bad in invalid:
        p=out/(name+'.json');p.write_text(json.dumps(bad),encoding='utf-8')
        try:LiveActionPlan(p,116,original,parent['resources'],colors)
        except AssertionError:check(True,'Reject '+name)
        else:raise AssertionError('Accepted '+name)
    try:LiveActionPlan(plan_path,116,original,parent['resources'],bytes(32))
    except AssertionError:check(True,'Reject cross-sheet palette mismatch')
    else:raise AssertionError('Accepted wrong palette')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,modes=modes,originalPoseKeys=sorted(seen),mappedFrames=len(expected),mappedSlots=len({s for r,s,f in expected}),allocatorContext=str(proof_path),allocatorContextSha256=sha(proof_path.read_bytes()),scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],error=str(error),checks=checks,modes=modes),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
