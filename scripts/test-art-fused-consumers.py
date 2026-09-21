"""Compare complete same-input fused composition with the prior native bridge.

Retained raw battle data only; no serialized actor execution. Exercise native
highlight filtering and split history acquisition through the actual compositor.
DMA is synchronous: this is a consumer contract, not live timing or targeting UI.
"""
import argparse, ast, datetime, hashlib, itertools, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
ids=['a42c04e18e3584a8447564aef4d06ac8f10ed93e','e1a87ecde67f265f666d3ab9d7e50ba401370633']
metas=[json.loads((ROOT/'build/art/connected'/ident/'live-palette-view.json').read_text()) for ident in ids]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path)
args=parser.parse_args()
if args.candidate_manifest:
    metas[1]=json.loads(args.candidate_manifest.read_text(encoding='utf-8'))
    ids[1]=metas[1]['romSha1']
roms=[Path(m['path']).read_bytes() for m in metas]
assert [hashlib.sha1(r).hexdigest() for r in roms]==ids
for field in ('ramReservation','transientStateBytes','bindingOffset','variantOffset','tagOffset','historySlots','nativeHighlightOffset','refusalOffset'):
    assert metas[0][field]==metas[1][field],field
assert not metas[0].get('fusedCompose') and metas[1]['fusedCompose']
base,limit=metas[1]['ramReservation']
capture=ROOT/'build/art/live-palette/battle/20260919T013433.783581Z'
pins={'iwram':'98dfbdef073919f3531ce01463d3431818be6f7f0bb7f62495f0216446c35067',
      'oam':'2c8b0c55b6ac049a5fea101338f17f5bbe4db50405771bbfe50ffbf289c96894',
      'palette':'9eef77bd38e886e58803d5247717fbd0608790401dc16579ae708b1ca73a37d9',
      'ram':'133af7f1fd42414e7161e69c0aed1fae9cca65fa29ab67c2b898f336b1ff36f2',
      'vram':'08d9e233efc68e4eac8969eaeb86801f2fe63dc16d4e90407902b1d0b3a5077f'}
saved={name:(capture/('candidate-ready.'+name)).read_bytes() for name in pins}
assert all(sha(saved[k])==v for k,v in pins.items())
out=ROOT/'build/art/fused-consumers'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[];case=None

def check(ok,label):
    assert ok,(case,label)
    checks.append(str(case)+'/'+label)

def dma(u,pc,size,a):
    src,dst,flags=struct.unpack('<3I',a.read(0x040000b0,12));count=(flags&65535)*4
    assert flags>>16==0x8400 and 0x03000000<=src<=0x03008000-count and 0x07000000<=dst<=0x07000400-count
    a.put(dst,a.read(src,count));a.put(0x040000b8,struct.pack('<I',flags&0x7fffffff))

def machine(rom,highlight,mode,skipped):
    a=ARM(rom,saved['iwram']);a.put(0x02000000,saved['ram'])
    for address,size in ((0x04000000,0x1000),(0x05000000,0x1000),(0x06000000,0x18000),(0x07000000,0x1000)):a.u.mem_map(address,size)
    for name,address in [('vram',0x06000000),('palette',0x05000000),('oam',0x07000000)]:a.put(address,saved[name])
    a.put(0x04000006,struct.pack('<H',180))
    for pc in (0x08001322,0x08001396,0x080013e2,0x08001430):a.u.hook_add(UC_HOOK_CODE,dma,user_data=a,begin=pc,end=pc)
    mask=a.word(base+2572)
    for bank in range(16):
        if mask&(1<<bank):a.put(0x05000200+bank*32,a.read(base+2060+bank*32,32))
    a.put(base+2572,bytes(4));a.put(base+metas[1]['nativeHighlightOffset'],struct.pack('<I',highlight))
    a.put(0x03000e10,struct.pack('<H',skipped))
    if not skipped:a.put(0x05000000,a.read(0x03003860,1024))
    bank=a.read(0x03000028,1)[0]^1;main=a.word(0x03000020+bank*4)
    owned=[]
    for index in range(main):
        entry=base+4+bank*1024+index*8;src=0x03000030+bank*1024+index*8
        if a.read(entry+6,1)[0]<10 and a.read(entry,6)==a.read(src,6):owned.append((entry,src))
    check(len(owned)>1,'retained native source has multiple authenticated custom pieces')
    if mode=='split':
        # Two current pieces of the same class must demand different banks;
        # merely moving a unique class to bank9 would test acquisition only.
        a.put(owned[1][0]+6,a.read(owned[0][0]+6,1))
    changed=owned[:1] if mode=='split' else owned if mode=='all-bank9' else []
    for entry,src in changed:
        c=struct.unpack('<H',a.read(src+4,2))[0]
        value=struct.pack('<H',(c&4095)|0x9000);a.put(src+4,value);a.put(entry+4,value)
    return a

try:
    for highlight,mode,skipped,residue in itertools.product((0,1),('retained','split','all-bank9'),(0,1),(0,4)):
        case=(highlight,mode,skipped,residue);machines=[];calls=[]
        for rom,meta in zip(roms,metas):
            a=machine(rom,highlight,mode,skipped);seen=[]
            targets={meta['symbols'][name]:name for name in ('ffta_art_owners_compose_native','ffta_art_palette_live_apply_prefix')}
            if meta.get('fusedCompose'):
                targets.update({meta['symbols'][name]:name for name in ('ffta_art_owners_compose_fused','ffta_art_palette_live_apply_fused')})
            def record(u,pc,size,data):
                if pc in targets:seen.append(targets[pc])
            a.u.hook_add(UC_HOOK_CODE,record)
            a.call(0x080012bc,stack=STACK+residue);machines.append(a);calls.append(seen)
        old,new=machines
        for address,size,label in ((0x07000000,1024,'complete OAM'),(0x05000000,1024,'complete palette'),(0x06000000,0x18000,'complete VRAM'),(0x03000000,0x6d68,'native IWRAM below scratch'),(base,metas[1]['transientStateBytes'],'complete live state')):
            check(old.read(address,size)==new.read(address,size),label+' equals prior full classification')
        check(old.read(0x02000000,base-0x02000000)+old.read(limit,0x02040000-limit)==new.read(0x02000000,base-0x02000000)+new.read(limit,0x02040000-limit),'unrelated EWRAM unchanged')
        expected='ffta_art_owners_compose_native' if highlight else 'ffta_art_owners_compose_fused'
        check(expected in calls[1] and ('ffta_art_owners_compose_fused' not in calls[1] if highlight else 'ffta_art_owners_compose_native' not in calls[1]),'actual conditional ownership route')
        if highlight and mode=='all-bank9':check('ffta_art_palette_live_apply_prefix' not in calls[1] and new.word(base+2572)==0,'all highlighted owners retire before palette overlay')
        else:check(('ffta_art_palette_live_apply_prefix' if highlight else 'ffta_art_palette_live_apply_fused') in calls[1],'actual matching palette consumer route')
        keys=new.read(base+metas[1]['variantOffset'],20)
        requested=new.word(base+2596)
        demanded=[keys[i] for i in range(20) if requested&(1<<i)]
        if mode=='split' and not highlight:
            check(any(a//16==b//16 and a%16!=b%16 for a in demanded for b in demanded),'actual simultaneous split history requests retained')
        records.append(dict(highlight=highlight,mode=mode,skippedDMA=skipped,stackResidue=residue,calls=calls,requestedHistoryKeys=demanded,paletteSha256=sha(new.read(0x05000000,1024))))
    report=dict(status='passed',checks=checks,romSha1=ids[1],controlRomSha1=ids[0],inputHashes=pins,records=records,scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n');print(out);raise
