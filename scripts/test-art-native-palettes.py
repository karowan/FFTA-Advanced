"""Native shared-palette stage, exact graph invariants and native getters.

Builds an isolated candidate from the completed action candidate. This does not
accept live palette effects, capacity, response timing or final artwork.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_palette_transport import build
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
RETURN,STACK=0x08000100,0x03007000
source=ROOT/'build/art/connected/5a14e6c7b69f9f9984a6965faf5740d3b318e41a/manifest.json'
out=ROOT/'build/art/native-palettes/tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    parent=json.loads(source.read_text());original=Path(parent['path']).read_bytes()
    connected=build(source);part=connected['components']['nativePaletteTransport'];rom=Path(connected['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==connected['romSha1'],'Native palette ROM authenticated')
    code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000').replace(
        'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
    tree=ast.parse(code);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native getters>','exec'))
    a=ARM(rom,bytes(0x8000));word=lambda b,p:struct.unpack_from('<I',b,p)[0]
    for p in part['palettes']:
        job=p['job']
        check(a.call(0x080c8570,job,job,6)==p['selector'] and a.call(0x080c8570,job,job,7)==p['opposingSelector'],'Native party and opposing palette selectors '+str(job))
        check(p['indexMap'][0]==0 and all(1<=x<=15 for x in p['indexMap'][1:]),'Opaque pixels cannot become transparent '+str(job))
    for resource in part['resources']:
        n=resource['resource'];desc=resource['descriptors'];old=resource['sourceDescriptors']
        for stream in resource['streams']:
            slot=stream['slot'];mode=(slot//2)*4+(1 if slot%2 else 0)
            selected=a.call(0x08021004,n,mode)-0x08000000
            check(selected==desc+12*slot,'Actual native descriptor getter '+str((n,slot)))
            check(rom[selected+4:selected+12]==original[old+slot*12+4:old+slot*12+12],'Native descriptor metadata unchanged')
            q=stream['sequence'];prior=stream['sourceSequence'];count=stream['count']
            check(word(rom,q)==word(original,prior)==count,'Native sequence count unchanged')
            for frame in range(count):
                p=q+4+frame*20;before=prior+4+frame*20
                # Only draw commands may change their tile pointer. OAM,
                # control commands, arguments, durations and event bytes agree.
                start=4 if rom[p+9]==1 else 0
                check(rom[p+start:p+20]==original[before+start:before+20],'Exact native action/control command '+str((n,slot,frame)))
    live=parent['components']['livePalette']
    for patch in live['changes']:
        p=patch['offset'];n=patch['bytes']
        if p in part['restoredNativeHooks']:check(rom[p:p+n]==bytes.fromhex(patch['before']),'Original native graphics consumer restored '+hex(p))
    check(len(part['resources'])==20 and set(r['job'] for r in part['resources'])==set(range(116,126)),'Every added class land and water resource retained')
    check(word(rom,live['symbols']['ffta_art_custom_mask']-0x08000000)==0,'Native palette path has no custom ownership demand')
    manifest=ROOT/'build/art/connected'/connected['romSha1']/'manifest.json'
    (ROOT/'build/art/native-palettes/current.json').write_bytes(manifest.read_bytes())
    report=dict(status='passed',romSha1=connected['romSha1'],checks=checks,manifest=str(manifest),scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),romSha1=connected['romSha1'],report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');raise
