"""Captured natural table transition: speculative matches versus real actors.

Installed ARMv4T entrypoints only; no saved-state playback or invented art.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
meta=json.loads((ROOT/'build/art/live-palette/all-classes-workspace-current.json').read_text())
rom=Path(meta['path']).read_bytes();assert meta['provisionalHistory'] and hashlib.sha1(rom).hexdigest()==meta['romSha1']
p=ROOT/'build/art/live-palette/battle/20260918T115844.020648Z'
ram=(p/'candidate-failed.ram').read_bytes();iw=(p/'candidate-failed.iwram').read_bytes()
assert sha(ram)=='99f4c7014e1360f52c27095860fef3c9fd2edae432d30a91d3b33daa0e23f005'
assert sha(iw)=='37660e100f84c75d99e9ccc7534d8d43819553deaf8a5d49e9cd5132d9dc6b36'
assert sha((p/'palette-target.json').read_bytes())=='908afd8582cfc1fe4e1a8e224bf61b1a2710507a12063fab25ce42b5807c4e29'
capture=json.loads((p/'palette-target.json').read_text());words=struct.unpack('<10I',bytes.fromhex(capture['ring']))
_,_,FIRST,LAST,DURATION,TASK,KIND,TABLE,B,V=words
assert (FIRST,LAST,DURATION,KIND)==(448,463,30,3)
base=meta['ramReservation'][0];CONF=base+meta['confirmedOffset'];COLORS=meta['symbols']['ffta_art_custom_colors']
S=meta['symbols'];checks=[];rows=[]
def check(ok,label):assert ok,label;checks.append(label)
def call(name,*args):
    if len(args)>4:a.put(STACK,struct.pack('<'+'I'*len(args[4:]),*args[4:]))
    return a.call(S[name],*args[:4])
for case in ('provisional-unrelated','confirmed-absent','all-confirmed','baseline','uniform','partial'):
    a=ARM(rom,iw);a.put(0x02000000,ram);a.put(CONF,bytes([255]*20))
    keys=a.read(V,20);active=[i for i,k in enumerate(keys) if k!=255]
    check(active==[1,2,4,5,6,7,8],case+' authenticated seven native-bank matches')
    original_colors=[a.read(B+i*252,244) for i in range(20)]
    if case=='confirmed-absent':call('ffta_art_provisional_confirm',V,CONF,1<<1)
    if case=='all-confirmed':call('ffta_art_provisional_confirm',V,CONF,sum(1<<i for i in active))
    # A zero visible mask must not revoke a previously authenticated actor.
    call('ffta_art_provisional_confirm',V,CONF,0)
    if case=='baseline':a.put(TABLE,a.read(B+252+212,32))
    if case=='uniform':a.put(TABLE,struct.pack('<16H',*([0x4210]*16)))
    last=LAST-1 if case=='partial' else LAST
    before=a.word(B+5688)
    call('ffta_art_provisional_reconcile',V,B,CONF,FIRST,last,TABLE)
    remaining=[i for i,k in enumerate(a.read(V,20)) if k!=255]
    expected=[] if case=='provisional-unrelated' else [1] if case=='confirmed-absent' else active
    check(remaining==expected,case+' exact surviving identities')
    check([a.read(B+i*252,244) for i in range(20)]==original_colors,case+' reconciliation never invents or edits colors')
    call('ffta_art_binding_start_mapped',B,FIRST,last,DURATION,TASK,KIND,TABLE,COLORS,V)
    refused=1 if case=='confirmed-absent' else 7 if case in ('all-confirmed','partial') else 0
    check(a.word(B+5688)==before+refused,case+' unchanged strict mapper reports exact unsupported count')
    if case in ('baseline','uniform'):
        for slot in active:
            wanted=a.read(COLORS+(keys[slot]>>4)*32,32) if case=='baseline' else struct.pack('<16H',*([0x4210]*16))
            check(a.read(B+slot*252+32,32)==wanted,case+' supported target retained before first appearance '+str(slot))
    if case=='confirmed-absent':
        check(a.read(CONF+1,1)==keys[1:2],'Absent confirmed actor retains identity after strict refusal')
        a.put(V+1,b'\xff');call('ffta_art_provisional_confirm',V,CONF,0)
        check(a.read(CONF+1,1)==b'\xff','Explicit native bank retirement revokes prior confirmation')
        a.put(V+1,keys[1:2]);call('ffta_art_provisional_confirm',V,CONF,0)
        check(a.read(CONF+1,1)==b'\xff','Reused same key cannot inherit a retired actor confirmation')
    if case=='provisional-unrelated':
        N,O,T,M,VISIBLE=0x02008000,0x02008200,0x02008600,0x02008700,0x02008800
        native=bytearray(iw[0x3a60:0x3c60]);native[12*32:13*32]=a.read(TABLE,32)
        objects=bytearray(struct.pack('<4H',0x200,0,0,0)*128)
        struct.pack_into('<4H',objects,0,64,0x8040,12<<12,0)
        a.put(N,native);a.put(O,objects);a.put(T,bytes([1]+[255]*127))
        a.put(M,struct.pack('<10H',0,1<<12,*([0]*8)));a.put(VISIBLE,bytes(640))
        prior=(a.read(V,40),a.read(B,5692),a.read(T,128),a.read(VISIBLE,640))
        result=call('ffta_art_variants_prepare',V,B,T,O,M,N,S['ffta_art_native_reference'],COLORS,VISIBLE)
        check(result==0 and prior==(a.read(V,40),a.read(B,5692),a.read(T,128),a.read(VISIBLE,640)),
            'Unrelated target cannot silently authenticate a later custom actor')
        a.put(N+12*32,a.read(S['ffta_art_native_reference']+32,32))
        result=call('ffta_art_variants_prepare',V,B,T,O,M,N,S['ffta_art_native_reference'],COLORS,VISIBLE)
        call('ffta_art_provisional_confirm',V,CONF,result)
        check(result==2 and a.read(CONF+1,1)==b'\x1c' and a.read(VISIBLE+32,32)==a.read(COLORS+32,32),
            'Actual later actor confirms only a fresh matching baseline and correct generated palette')
    rows.append(dict(case=case,survivingSlots=remaining,refusals=refused))
out=ROOT/'build/art/provisional-history'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,rows=rows,ramSha256=sha(ram),iwramSha256=sha(iw),scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=str(out/'report.json'),checks=len(checks),rows=rows)))
