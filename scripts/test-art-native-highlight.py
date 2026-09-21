"""Exact native target-copy provenance, retirement and original pulse behavior."""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x080b70f6,0x03007800
code=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=1000000')
code=code.replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(code)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
meta=json.loads((ROOT/'build/art/connected/current.json').read_text());live=meta['components']['livePalette']
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
oldmeta=json.loads((ROOT/'build/art/connected/4a7d55ce09cd4a40965a0bb97de2701d276789c5/manifest.json').read_text())
old=Path(oldmeta['path']).read_bytes();assert hashlib.sha1(old).hexdigest()==oldmeta['romSha1']
source=ROOT/'build/art/connected/casting/20260918T203709.455123Z'
iw=(source/'371-active-ready.iwram').read_bytes();ram=(source/'371-active-ready.ram').read_bytes()
BASE,LIMIT=live['ramReservation'];H=BASE+live['nativeHighlightOffset'];V=BASE+live['variantOffset'];B=BASE+live['bindingOffset']
PAL=0x03003b80;SRC=0x03003c40;TEMP=0x02028000
out=ROOT/'build/art/connected/highlight-native'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];case='setup'
def check(ok,label):
    assert ok,(case,label)
    checks.append(case+'/'+label)
def machine(data):
    a=ARM(data,iw);a.put(0x02000000,ram);a.put(H,bytes(4));return a
def copy(a,dst=PAL,src=SRC,size=32,residue=0):return a.call(a.word(0x0836d4bc),dst,src,size,stack=STACK+residue)
def native(a):return a.read(0x03000000,0x7000)
def outside(a):return a.read(0x02000000,BASE-0x02000000)+a.read(LIMIT,0x02040000-LIMIT)
try:
    check(rom[0xb70de:0xb70f6]==old[0xb70de:0xb70f6] and rom[0xb4ff8:0xb50ee]==old[0xb4ff8:0xb50ee],'Original target setup and pulse instructions unchanged')
    for residue in (0,4):
        case='native-target-stack'+str(residue);a,n=machine(rom),machine(old)
        check(a.read(SRC,32)==rom[0x419f40:0x419f60],'Actual ready shared highlight palette exact ROM table')
        for slot in range(10):
            a.put(V+slot,bytes([slot*16+9]));a.put(V+20+slot,b'\x13')
            a.put(B+slot*252+248,struct.pack('<I',9));a.put(B+slot*252+244,struct.pack('<I',TEMP))
        a.put(BASE+2596,struct.pack('<I',1023))
        before=a.read(B+live['bindingCounterOffset'],12);refusals=a.read(BASE+live['refusalOffset'],16)
        check(copy(a,residue=residue)==copy(n,residue=residue)==RETURN|1,'Original callback return register exact')
        check(a.word(H)==1,'Only authenticated native target load establishes native ownership')
        check(native(a)==native(n) and outside(a)==outside(n),'Full native palette and unrelated game memory unchanged')
        check(a.word(BASE+2596)==0,'Prior displayed bank9 slot requests retired')
        check(a.read(V,10)==b'\xff'*10 and a.read(V+20,10)==bytes(10),'All prior bank9 class variants retired')
        check(all(a.word(B+s*252+248)==255 and a.word(B+s*252+244)==0 for s in range(10)),'Retired bindings cannot retain stale tasks')
        check(a.read(B+live['bindingCounterOffset'],12)==before and a.read(BASE+live['refusalOffset'],16)==refusals,'Known native takeover is not a refusal')
        # Original game pulses colors2..15 with per-channel direction flags.
        # Compare all IWRAM and nonreserved game RAM on every original call.
        for m in (a,n):m.put(TEMP,bytes(128))
        for phase in range(64):
            a.call(0x080b4ff8,TEMP,9);n.call(0x080b4ff8,TEMP,9)
            check(native(a)==native(n) and outside(a)==outside(n),'Original native pulse exact phase '+str(phase))
        copy(a,PAL,0x08419d60,32)
        check(a.word(H)==0,'Normal bank reuse revokes native highlight ownership')
    # Near-misses cannot establish native ownership, even with table bytes.
    for caller,dst,src,size,corrupt in ((0x08000100,PAL,SRC,32,False),(0x080b70f6,PAL,TEMP,32,False),
            (0x080b70f6,PAL,SRC,30,False),(0x080b70f6,PAL+2,SRC,32,False),(0x080b70f6,PAL,SRC,32,True)):
        case='reject-'+str((caller,dst,src,size,corrupt));RETURN=caller;a,n=machine(rom),machine(old)
        for m in (a,n):
            m.put(TEMP,rom[0x419f40:0x419f60])
            if corrupt:m.put(SRC+4,b'\x00\x00')
        check(copy(a,dst,src,size)==copy(n,dst,src,size),'Rejected provenance preserves original return')
        check(a.word(H)==0 and native(a)==native(n) and outside(a)==outside(n),'Rejected provenance preserves copy without native ownership')
    result=dict(status='passed',romSha1=meta['romSha1'],checks=checks,sourceSha256={p.name:sha(p.read_bytes()) for p in (source/'371-active-ready.ram',source/'371-active-ready.iwram')},
        scope='Actual installed copy hook on ARMv4T; exact caller/address/size/table provenance, both stack alignments, all ten bank9 variants retired, original64-step native highlight pulse, normal reuse revocation, five rejected provenance controls. Not live display, all target modes or final artwork acceptance.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=meta['romSha1'],case=case,error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
