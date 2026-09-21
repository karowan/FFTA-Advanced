"""Private opposing-side palette build and exact native reference contract.

Preserves default build bytes, proves all ten native job palette selectors,
both baseline scales and each corrupted color negative. Runtime capacity is a
separate declared step. No installed selector or player save changes.
"""
import argparse,ast,datetime,hashlib,importlib.util,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--existing',type=Path);args=parser.parse_args()
RETURN,STACK=0x08000100,0x03007000
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
parent_path=ROOT/'build/art/connected/5a14e6c7b69f9f9984a6965faf5740d3b318e41a/manifest.json'
parent=json.loads(parent_path.read_text());live=parent['components']['livePalette']
assert hashlib.sha1(Path(parent['path']).read_bytes()).hexdigest()==parent['romSha1']
out=ROOT/'build/art/opposing-palettes'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
protected={parent_path,ROOT/'build/art/connected/current.json',ROOT/'build/art/live-palette/status-current.json'}
for part in parent['components'].values():
    if 'path' in part:
        p=Path(part['path']).parent/'manifest.json'
        if p.exists():protected.add(p)
protected_bytes={p:p.read_bytes() for p in protected}
checks=[];phase='build'
def check(ok,label):
    assert ok,phase+'/'+label
    checks.append(phase+'/'+label)
try:
    if args.existing:
        connected=json.loads(args.existing.read_text());built=connected['components']['livePalette']
        check(built['opposingPalettes'] and 'actionCompletion' in connected['components'],'Reuse complete opposing-palette candidate')
    else:
        builder=module('opposing_palette_builder','build-live-art-palette.py')
        builder.PARENT=Path(live['source']).parent/'manifest.json'
        options=dict(history_slots=20,all_classes=True,workspace_low_address=True,provisional_history=True,fast_rotation=True,
                     owned_menu_buffer=True,shared_battle_menu_heap=True,compact_us_keyboard=True,compact_battle_status=True,publish_current=False,
                     fast_bank_scan=True,fast_oam_plan=True,arm_oam_scan=True,scoped_frame=True,
                     native_oam_prefix=True,native_owner_producer=True,fused_compose=True)
        baseline=builder.build(**options)
        check(baseline['romSha1']==live['romSha1'],'Default palette module remains byte-exact')
        built=builder.build(**options,opposing_palettes=True)
        for field in ('ramReservation','transientStateBytes','artInputs','partyHeapRoot'):
            check(built[field]==live[field],'Unchanged '+field)
        connected=module('opposing_connected','build-connected-art.py').build(Path(built['path']).parent/'manifest.json',publish_current=False,fixture_source=parent['fixtureSource'])
        connected=module('opposing_action_completion','complete-generated-actions.py').build(ROOT/'build/art/connected'/connected['romSha1']/'manifest.json',publish_current=False)
    image=Path(connected['path']).read_bytes();symbols=built['symbols']
    check(hashlib.sha1(image).hexdigest()==connected['romSha1'],'Authenticate exact contract candidate')
    phase='native-contract'
    source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000')
    source=source.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
    tree=ast.parse(source)
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM contract>','exec'))
    a=ARM(image,bytes(0x8000))
    V,B,T,O,BANKS,NATIVE,VISIBLE=0x02010000,0x02010100,0x02012000,0x02012100,0x02012600,0x02012800,0x02012a00
    REF=symbols['ffta_art_native_reference'];CUSTOM=symbols['ffta_art_custom_colors']
    def call(name,*values):
        a.put(STACK,struct.pack('<'+'I'*len(values[4:]),*values[4:]))
        return a.call(symbols[name],*values[:4])
    def scale(raw,n):
        return struct.pack('<16H',*[sum((((v>>s)&31)*n//32)<<s for s in (0,5,10)) for v in struct.unpack('<16H',raw)])
    def reset(owner,raw):
        a.put(V,bytes([255])*20+bytes(20));a.put(B,bytes(20*284+12))
        a.put(T,bytes([owner])+bytes([255])*127);a.put(O,bytes(1024))
        banks=[0]*10;banks[owner]=1;a.put(BANKS,struct.pack('<10H',*banks))
        a.put(NATIVE,raw+bytes(480));a.put(VISIBLE,b'\xa5'*640)
    def prepare():return call('ffta_art_variants_prepare',V,B,T,O,BANKS,NATIVE,REF,CUSTOM,VISIBLE)
    for owner in range(10):
        job=116+owner
        for prop,name in ((6,'ffta_art_native_reference'),(7,'ffta_art_native_opposing_reference')):
            index=a.call(0x080c8570,job,job,prop)
            raw=image[0x419d60+32*index:0x419d80+32*index]
            check(a.read(symbols[name]+owner*32,32)==raw,'Exact native property'+str(prop)+' source '+str(job))
            for factor in (32,19):
                native=scale(raw,factor);reset(owner,native)
                check(prepare()==1<<owner,'Accept complete side/scale '+str((job,prop,factor)))
                check(a.read(V+owner,1)==bytes((owner*16,)) and a.read(V+20+owner,1)==bytes((factor,)),'Class/bank/scale identity retained')
                custom=a.read(CUSTOM+owner*32,32)
                check(a.read(VISIBLE+owner*32,32)==scale(custom,factor),'Exact class colors published')
                # Each single-color corruption must remain an atomic refusal.
                for color in range(16):
                    bad=bytearray(native);bad[color*2]^=1;reset(owner,bad)
                    before=(a.read(V,40),a.read(B,20*284+12),a.read(T,128),a.read(VISIBLE,640))
                    check(prepare()==0,'Reject altered side/scale color '+str((job,prop,factor,color)))
                    check(before==(a.read(V,40),a.read(B,20*284+12),a.read(T,128),a.read(VISIBLE,640)),'Refusal preserves all state/tags/colors')
    manifest=ROOT/'build/art/connected'/connected['romSha1']/'manifest.json'
    (out.parent/'current.json').write_bytes(manifest.read_bytes())
    (out/'report.json').write_text(json.dumps(dict(status='passed',romSha1=connected['romSha1'],checks=checks,
        manifest=str(manifest),scope=__doc__,parent=str(parent_path)),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),romSha1=connected['romSha1'],report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',phase=phase,error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8')
    raise
finally:
    for p,raw in protected_bytes.items():p.write_bytes(raw)
