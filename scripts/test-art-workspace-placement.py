"""Exact captured allocation sequence; no saved actor playback or video model."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
p=ROOT/'build/art/live-palette/battle/20260918T115150.012859Z'
ram=(p/'candidate-failed.ram').read_bytes();iw=(p/'candidate-failed.iwram').read_bytes()
assert sha(ram)=='a4b1101cf8e567f3dc71da44ddeb0770cad3dfb1e10a2858d585426244498997'
assert sha(iw)=='f6c416d7cc681c088a4acd546ccf7bd97b8d2b5d684e626067e945ce1300b677'
meta=json.loads((ROOT/'build/art/live-palette/all-classes-workspace-current.json').read_text())
base=json.loads((ROOT/'build/art/live-palette/all-classes-current.json').read_text())
assert meta['workspaceLowAddress'] and base['romSha1']=='4b35081ba8d69f6ebf997607c119931e303a6106'
checks=[];rows=[]
def check(ok,name):assert ok,name;checks.append(name)
def shape(a):
    b=a.word(0x0200f434);end=b+8+4*struct.unpack('<H',a.read(b+6,2))[0];at=b+8;result=[]
    while at:
        h=struct.unpack('<6H',a.read(at,12));check(b+8<=at<end,'physical block inside heap')
        result.append((at,h[2],h[3]));n=b+4*h[1] if h[1] else 0
        check(not n or at<n<=end-12,'physical chain increasing');at=n
    free={address for address,marker,size in result if marker==0x7370};seen=set();prior=0
    index=struct.unpack('<H',a.read(b,2))[0]
    while index:
        address=b+4*index
        check(address in free and address not in seen,'free list covers only unique physical free blocks')
        h=struct.unpack('<6H',a.read(address,12))
        check(h[4]==prior,'free list previous link matches')
        seen.add(address);prior=index;index=h[5]
    check(seen==free,'free list completely covers physical free blocks')
    return result
for label,m in [('original',base),('low-address',meta)]:
    rom=Path(m['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==m['romSha1']
    a=ARM(rom,iw);a.put(0x02000000,ram);heap=a.word(0x0200f434);initial=shape(a)
    manager=a.word(0x0200f4b0)
    check(a.call(0x09307860)==1,label+' actual owned workspace preparation succeeds')
    pool=a.word(manager+0x438)
    check(pool==(0x020373e8 if label=='original' else 0x020159e4),label+' exact measured workspace placement')
    # The temporary 22148-byte AI block is released before the larger request.
    a.call(0x08007170,heap,0x02031d58)
    before_request=shape(a)
    result=a.call(0x08022840,39944)
    check(bool(result)==(label=='low-address'),label+' native large-request outcome')
    check(a.read(0x02000080,0x1e70-0x80)==ram[0x80:0x1e70],label+' canonical units preserved')
    check(a.read(0x0203c000,0x3000)==ram[0x3c000:0x3f000],label+' palette reservation untouched')
    if result:
        a.call(0x08007170,heap,result)
        check(shape(a)==before_request,'large native allocation frees and coalesces exactly')
    a.call(0x08007170,heap,pool)
    check(a.word(manager+0x438)==0,label+' workspace free detaches owner')
    rows.append(dict(case=label,romSha1=m['romSha1'],pool=pool,nativeRequestResult=result,finalShape=shape(a)))
rom=Path(meta['path']).read_bytes()
for case in ('valid','wrong-size','unaligned','extent','marker','physical-next','physical-previous','free-neighbor'):
    a=ARM(rom,iw);a.put(0x02000000,ram);heap=a.word(0x0200f434);words=0x998
    if case=='wrong-size':words+=1
    if case=='unaligned':heap+=1
    if case=='extent':a.put(heap+6,struct.pack('<H',0xffff))
    if case=='marker':a.put(heap+12,b'xx')
    if case=='physical-next':a.put(heap+10,struct.pack('<H',0xffff))
    if case=='physical-previous':a.put(heap+8,struct.pack('<H',1))
    if case=='free-neighbor':a.put(heap+16,struct.pack('<H',0xffff))
    before=a.read(0x02000000,0x40000);a.call(meta['symbols']['ffta_art_workspace_find'],heap,words,0x0200e000,0x0200e004)
    check(a.word(0x0200e004)==(0x020159d8 if case=='valid' else 0),case+' bounded selector result')
    after=a.read(0x02000000,0x40000)
    check(after[:0xe000]==before[:0xe000] and after[0xe008:]==before[0xe008:],case+' selector has no heap mutation')
out=ROOT/'build/art/workspace-placement'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',romSha1=meta['romSha1'],ramSha256=sha(ram),iwramSha256=sha(iw),checks=checks,rows=rows,scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=str(out/'report.json'),checks=len(checks),rows=rows)))
