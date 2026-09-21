"""Explicit frame map import, default preservation and incomplete-plan controls."""
import argparse,ast,copy,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,TILES,OAM,sha,layout
from generated_action_transport import build
from generated_animation_plan import AnimationPlan
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
out=ROOT/'build/art/animation-plan-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--plan',type=Path,default=ROOT/'src/art/imagegen/samurai-walk-transport.json')
parser.add_argument('--current',type=Path,default=ROOT/'build/art/generated-actions/mapped-walk-current.json')
args=parser.parse_args()
checks=[];meta={}
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    assembled=json.loads((ROOT/'build/art/assembled/current.json').read_text());prior=assembled['components']['actions']
    basepath=Path(prior['source']).parent/'manifest.json';base=Path(prior['source']).read_bytes()
    legacy=build(basepath,publish_current=False)
    check(legacy['romSha1']==prior['romSha1'] and Path(legacy['path']).read_bytes()==Path(prior['path']).read_bytes(),'Default action import byte-exact unchanged')
    planpath=args.plan
    requested=json.loads(planpath.read_text())
    assignments={e['slot']:e['frames'] for e in requested['sequences']}
    check(requested['jobs']==[116] and set(assignments)=={0,1,2,3} and all(e['job']==116 and e['lifetime']=='land' for e in requested['sequences']),'Declared Samurai four-slot test scope')
    meta=build(basepath,publish_current=False,animation_plan=planpath)
    rom=Path(meta['path']).read_bytes();old=Path(prior['path']).read_bytes()
    check(meta['animationPlan']['mappedSequences']==4 and meta['animationPlan']['requiredSequences']>4,'Partial coverage explicitly reported')
    check(meta['animationPlan']['productionAccepted'] is False,'Coverage does not accept production art')
    def pose(blob,q,f):
        t,o=struct.unpack_from('<II',blob,q+4+20*f);objects,raw=layout(blob,OAM+o)
        return blob[TILES+t:TILES+t+sum(v['width']*v['height']//64 for v in objects)*32],raw
    for res in meta['resources']:
        before=next(r for r in prior['resources'] if r['id']==res['id'])
        for slot in range(res['slots']):
            n=rom[res['descriptors']+12*slot:res['descriptors']+12*slot+12];o=old[before['descriptors']+12*slot:before['descriptors']+12*slot+12]
            nq,oq=struct.unpack_from('<I',n)[0],struct.unpack_from('<I',o)[0]
            check(n[4:]==o[4:] and bool(nq)==bool(oq),f'{res["id"]}/{slot} metadata and null contract')
            if not nq:continue
            nq-=0x08000000;oq-=0x08000000;count=struct.unpack_from('<I',rom,nq)[0]
            check(count==struct.unpack_from('<I',old,oq)[0],f'{res["id"]}/{slot} native entry count')
            mapped=res['id']==256 and slot in (0,1,2,3)
            for f in range(count):
                check(rom[nq+12+20*f:nq+24+20*f]==old[oq+12+20*f:oq+24+20*f],f'{res["id"]}/{slot}/{f} native timing commands and params')
                if not mapped:check(pose(rom,nq,f)==pose(old,oq,f),f'{res["id"]}/{slot}/{f} unassigned pixels and OAM exact')
    a=ARM(rom,(Path(assembled['source']).parent/'fixture/battle-ready.iwram').read_bytes())
    actor=next(r for r in meta['resources'] if r['id']==256)
    for mode in range(8):
        slot=(mode//4)*2+((mode&3) in (1,2));q=a.word(a.call(0x08021004,256,mode))-0x08000000
        seq=next(s for s in actor['sequences'] if s['slot']==slot)
        check(q==seq['target'],f'Native mode{mode} resolves explicit sequence')
        check(len({f['sha256'] for f in seq['frames']})>=3,f'Mode{mode} has distinct mapped phases')
        for f,frame in enumerate(seq['frames']):
            check(frame['explicitFrame']==assignments[slot][f],f'Mode{mode}/{f} exact declared source cell')
    classes=json.loads((Path(json.loads(basepath.read_text())['source']).parent/'manifest.json').read_text())
    spec=json.loads(planpath.read_text())
    invalid=[]
    v=copy.deepcopy(spec);v['coverage']='complete';invalid.append(('false-complete',v))
    v=copy.deepcopy(spec);v['sequences'].append(v['sequences'][0]);invalid.append(('duplicate-slot',v))
    v=copy.deepcopy(spec);v['sequences'][0]['slot']=999;invalid.append(('unknown-slot',v))
    v=copy.deepcopy(spec);v['sequences'][0]['frames'].pop();invalid.append(('missing-frame',v))
    v=copy.deepcopy(spec);v['sequences'][0]['frames'][0]['frame']=8;invalid.append(('outside-cell',v))
    v=copy.deepcopy(spec);v['sequences'][0]['frames'][0]['asset']='absent';invalid.append(('unknown-asset',v))
    v=copy.deepcopy(spec);v['assets']['walk']['sourceSha256']='0'*64;invalid.append(('wrong-source',v))
    for name,bad in invalid:
        p=out/(name+'.json');p.write_text(json.dumps(bad))
        try:AnimationPlan(p,base,classes['classResources']['resources'],out/'invalid')
        except AssertionError:check(True,'Reject '+name)
        else:raise AssertionError('Accepted '+name)
    rebuilt=build(basepath,publish_current=False,animation_plan=planpath)
    check(rebuilt['romSha1']==meta['romSha1'] and Path(rebuilt['path']).read_bytes()==rom,'Exact PNG-to-explicit-animation rebuild')
    alternate=ROOT/'src/art/imagegen/samurai-walk-transport.json'
    if planpath.resolve()!=alternate.resolve():
        other=AnimationPlan(alternate,base,classes['classResources']['resources'],ROOT/'build/art/generated-actions/conversions')
        other.frame({'asset':'walk','frame':0},base,0x419d80)
        oldfolder=next(iter(other.cache.values()))[0]
        newconversion=next(c for c in meta['animationPlan']['conversions'] if c['asset']=='walk')
        check(oldfolder!=Path(newconversion['manifest']).parent,'Same-name artwork revisions have independent conversion folders')
        check(sha(Path(newconversion['manifest']).read_bytes())==newconversion['manifestSha256'],'Converting older revision preserves new evidence')
    current=args.current
    selected=dict(meta,releaseSource=assembled['source'],comparisonSource=prior['path'],comparisonRomSha1=prior['romSha1'])
    current.write_text(json.dumps(selected,indent=2)+'\n')
    report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,manifest=str(current),scope='Explicit front/back Samurai walking cells; actual native mode getters; preservation of every unassigned decoded pose/OAM and metadata; default byte-exact rebuild; input/coverage rejection controls. No actual walking or visual acceptance in this native check.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta.get('romSha1'),error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
