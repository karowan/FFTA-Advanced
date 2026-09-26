"""Static and native-harness checks for the memory-fixes stage.

Against the memory-fixes candidate and its palette-removal parent:
- every ROM difference is compiled code inside the reservation or a declared
  patch; each replaced entry is a Thumb BX trampoline to its declared target;
- reaction masks: native 133ADC gives the clean result for reactions 1..15
  under each of the 44 single status bits (the audit found 109 differences);
- old-layout builders 7A094/8D0C4 return the same list as their already
  hooked siblings 799C0/8CBDC for every tab (valid, unique item IDs 1..460),
  where the parent returned fake records;
- no expansion action carries the native learnable flag (CCD50 selector 0x16),
  so Blue Magic's direct unit+0x40+index lesson write stays unreachable, and the
  native learnable set is unchanged;
- executor/result stack: compiled frames are bounded, and with no bank frame
  and low SP the fallbacks run without a stack snapshot (ffta_snapshot_begin
  is never given a stack frame); with high SP the stack snapshot is used.
- ffta_job_load clears the JST1 marker from loaded state.
- the EXP formula's job gate sends jobs 116..125 down the ordinary path, and
  the Chemist's single-ally recipes use the single-target shape.
- the menu recolor replacement writes only inside the layer's map buffers (the
  unit menu's 0xFF "previous row" request, which corrupted unit records,
  writes nothing); the job wheel clears 12 glyph columns; the Chemist payment
  gate never refuses (a refusal softlocks the executor).
"""
import datetime, hashlib, json, random, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
meta=json.loads(Path(json.loads((ROOT/'build/expansion/memory-fixes/current.json').read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=meta['memoryFixes']
parent=Path(json.loads(Path(fix['parent']).read_text())['path']).read_bytes()
assert hashlib.sha1(parent).hexdigest()==fix['baseSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
integrated=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())['symbols']
built=fix['symbols'];u32=lambda b,p:struct.unpack_from('<I',b,p)[0]
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

# 1. Declared bytes and trampolines.
allowed=set(range(*fix['used']))
check(fix['reservation']==[0x1fd0000,0x1fe0000] and fix['reservation'][0]<=fix['used'][0]<fix['used'][1]<=fix['reservation'][1],'code inside the reservation')
check(parent[fix['used'][1]:fix['reservation'][1]]==b'\xff'*(fix['reservation'][1]-fix['used'][1]),'rest of the reservation still erased')
for p in fix['patches']:
    n=len(bytes.fromhex(p['after']))
    check(rom[p['offset']:p['offset']+n].hex()==p['after'] and parent[p['offset']:p['offset']+n].hex()==p['before'],'patch '+hex(p['offset']))
    allowed|=set(range(p['offset'],p['offset']+n))
check(len(rom)==len(parent) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(parent,rom))),'only declared bytes differ')
def jump(at):
    """Target of push{r3}; ldr r3,lit; mov ip,r3; pop{r3}; bx ip at ROM offset at."""
    h=struct.unpack_from('<5H',rom,at)
    assert h[0]==0xb408 and h[1]&0xff00==0x4b00 and h[2:]==(0x469c,0xbc08,0x4760),hex(at)
    return u32(rom,((at+2+4)&~3)+4*(h[1]&0xff))
targets={'ffta_samurai_execute':built['ffta_samurai_execute'],'stack_result':built['ffta_result_fallback'],
         'ffta_job_load':built['ffta_job_load'],'ffta_chemist_payment_gate':built['ffta_chemist_payment_gate']}
for name,target in targets.items():
    check(jump((integrated[name]&~1)-0x08000000)==target|1,name+' -> compiled replacement')
for at,sibling in ((0x7a094,0x799c0),(0x8d0c4,0x8cbdc)):
    check(jump(at)==u32(rom,sibling+4),'old-layout builder %X -> sibling C builder'%at)
check(jump(0x8b890)==built['ffta_bg_recolor']|1 and clean[0x8b890:0x8b8a0]==parent[0x8b890:0x8b8a0],'native recolor 8B890 -> bounded replacement')
check(jump(0x12e5b4)==built['ffta_exp_job_gate']|1 and clean[0x12e5b4:0x12e5c4]==parent[0x12e5b4:0x12e5c4],'EXP formula 12E5B4 -> expansion-job gate')
actions=u32(rom,0xccd84)-0x08000000
check(all(rom[actions+28*a+9:actions+28*a+11]==bytes((1,0)) for a in (383,384,385,386,388,389,390,391,392))
      and rom[actions+28*387+9:actions+28*387+11]==bytes((5,2)),'Chemist recipes single-target except the Healing Mist cross')
check(u32(rom,0x857ec)==0x01000180 and u32(clean,0x857ec)==0x01000160,'job wheel label clear covers 12 glyph columns')
check(u32(rom,0x1339ec)==0x08527d5c==u32(clean,0x1339ec) and rom[0x527d5c:0x527d5c+192]==clean[0x527d5c:0x527d5c+192],'native reaction mask table')

# Native harness (unicorn).
def machine(image):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    for a,s in ((0x02000000,0x40000),(0x03000000,0x8000),(0x04000000,0x1000),(0x08000000,0x2000000)):u.mem_map(a,s)
    u.mem_write(0x08000000,image[:0x2000000]);return u
def call(u,address,*args,sp=0x03007000,count=5000000):
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
    stack=list(args[4:]);sp-=4*len(stack)
    for i,v in enumerate(stack):u.mem_write(sp+4*i,struct.pack('<I',v))
    for r,v in zip(regs,args):u.reg_write(r,v)
    u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x08000101)
    u.emu_start(address|1,0x08000100,count=count);return u.reg_read(UC_ARM_REG_R0)
def returns(u,address,value):
    def hook(uc,a,size,data):
        uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=address&~1,end=address&~1)

# 2. Reaction masks.
uc,ux,up=machine(clean),machine(rom),machine(parent);changed=0
for reaction in range(1,16):
    for bit in range(44):
        bits=bytearray(8);bits[bit//8]|=1<<(bit%8)
        for u in (uc,ux,up):u.mem_write(0x02001000,bytes(bits))
        a=call(uc,0x08133adc,0x02001000,reaction);b=call(ux,0x08133adc,0x02001000,reaction)
        changed+=a!=call(up,0x08133adc,0x02001000,reaction)
        assert a==b,('reaction mask',reaction,bit,a,b)
check(changed>0,f'parent differed in {changed} reaction/status cases')
checks.append('reaction masks 15x44 equal clean')

# 3. Old-layout list builders.
random.seed(3);counts={i:random.randint(1,99) for i in range(1,461)}
def item_list(image,entry,tab):
    u=machine(image);state=bytearray(0x40000);state[0x1e70:0x1e79]=b'FFTAEXP1\x01'
    for i,c in counts.items():state[0x1940+i]=c
    state[0x80+4]=1;state[0x80+6]=1;u.mem_write(0x02000000,bytes(state))
    u.mem_write(0x03002818,struct.pack('<I',0x02010000));u.mem_write(0x02010000+0x1d0c,struct.pack('<I',0x02000080))
    returns(u,0x080cb48c,1)
    n=call(u,entry,tab,0x02020000);assert 0<=n<=460,n
    d=bytes(u.mem_read(0x02020000,0x230+20*n))
    return [u32(d,0x230+20*i+4) for i in range(n)]
for entry,sibling in ((0x0807a094,0x080799c0),(0x0808d0c4,0x0808cbdc)):
    for tab in range(5):
        ids=item_list(rom,entry,tab)
        check(ids and all(1<=i<=460 for i in ids) and len(set(ids))==len(ids) and ids==item_list(rom,sibling,tab),
              '%X tab %d: %d valid items, same as %X'%(entry,tab,len(ids),sibling))
    fake=lambda ids:any(not 1<=i<=460 for i in ids) or len(set(ids))!=len(ids)
    check(any(fake(item_list(parent,entry,tab)) or item_list(parent,entry,tab)!=item_list(rom,entry,tab) for tab in range(5)),
          'parent %X built a different (old-layout) list'%entry)

# 4. No expansion action is learnable (Blue Magic writes unit+0x40+index directly).
table=u32(rom,0xccd84)-0x08000000;end=347
while rom[table+28*end:table+28*end+28]!=b'\xff'*28:end+=1
learnable=lambda u,a:call(u,0x080ccd50,a,0x16)
check(end>=432 and not [a for a in range(347,end) if learnable(ux,a)],f'no learnable action among 347..{end-1}')
check([a for a in range(1,347) if learnable(ux,a)]==[a for a in range(1,347) if learnable(uc,a)],'native learnable actions unchanged')

# 5. Stack frames and fallback guards.
frames=fix['frames']
check(frames['samurai-execute:ffta_samurai_execute']+frames['samurai-execute:run']<=256,'executor lent path frame <= 256 bytes')
check(frames['result-fallback:ffta_result_fallback']<=64,'result fallback guard frame <= 64 bytes')
def fallback(entry,original,sp,args):
    """Run a fallback with no battle bank; report every ffta_snapshot_begin frame."""
    u=machine(rom);begun=[]
    def begin(uc,a,size,data):
        begun.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,begin,begin=integrated['ffta_snapshot_begin']&~1,end=integrated['ffta_snapshot_begin']&~1)
    returns(u,original,7)
    low=[sp]
    def track(uc,a,size,data):low[0]=min(low[0],uc.reg_read(UC_ARM_REG_SP))
    u.hook_add(UC_HOOK_CODE,track,begin=0x09fd0000,end=0x09fe0000)
    check(call(u,entry,*args,sp=sp)==7,'fallback result passes through')
    return begun,low[0]
FLOOR=0x03006d68;ARGS=(0,0,0,0,0,0,0,0,0,0)
for entry,original,need in ((integrated['stack_result']&~1,integrated['run_result'],820+2944),
                           ((integrated['ffta_samurai_execute']&~1),integrated['ffta_original_samurai_execute'],820+3328)):
    begun,low=fallback(entry,original,FLOOR+need-8,ARGS)
    check(not any(begun) and low>FLOOR+need-400,'%s: low SP runs without a stack snapshot'%hex(entry))
    begun,low=fallback(entry,original,0x03007e00,ARGS)
    check([b for b in begun if b] and all(0x03006000<b<0x03007e00 for b in begun if b),'%s: ample SP keeps the stack snapshot'%hex(entry))

# 6. Menu recolor bounds (native layer records at 030009E0, 76 bytes each).
def recolor(pointer):
    u=machine(rom);layer=bytearray(76);struct.pack_into('<II',layer,0x18,0x0203d4d4,0x0203d5dc);layer[0x28:0x2a]=bytes((12,9))
    u.mem_write(0x030009e0+4*76,bytes(layer));u.mem_write(0x0203d400,bytes(0x400));u.mem_write(0x02040000-0x400,bytes(0x400))
    u.mem_write(0x02000000,bytes(0x800))
    call(u,0x0808b890,4,pointer,10,0xc000)
    return bytes(u.mem_read(0x0203d400,0x400)),bytes(u.mem_read(0x02000000,0x800))
inside,low=recolor(0x0203d5dc+2*12*4+2)
row=0x0203d5dc+2*12*4+2-0x0203d400
check(all(struct.unpack_from('<H',inside,row+2*i)[0]==0xc000 and struct.unpack_from('<H',inside,row+24+2*i)[0]==0xc000 for i in range(10)),
      'recolor inside the layer buffers writes both rows')
inside,low=recolor(0x020405de)   # row 512 of the unit menu: the reported corruption
check(inside==bytes(0x400) and low==bytes(0x800),'out-of-range recolor (0xFF previous row) writes nothing')

# 7. Chemist payment gate never refuses (a refusal leaves the executor without a turn end).
u=machine(rom);state=bytearray(0x3ca8)
for i in range(362,376):state[0x1940+i]=5
u.mem_write(0x02000000,bytes(state))
returns(u,integrated['ffta_job_origin'],1);returns(u,integrated['ffta_job_peers'],0)
check(call(u,integrated['ffta_chemist_payment_gate'],0x02000080,383,0,0x03006000)==1 and bytes(u.mem_read(0x02001940+362,1))==b'',
      'Potion on a non-party tile continues without consuming a Potion')

# 8. JST1 marker cleared by ffta_job_load.
u=machine(rom);state=bytearray(0x3ca8);state[0x10]=0;state[0x1f04:0x1f08]=b'JST1'
u.mem_write(0x02003cb0,bytes(state));returns(u,integrated['ffta_job_original_migrate'],0);returns(u,integrated['ffta_job_reset'],0)
call(u,integrated['ffta_job_load'],0x02003cb0)
check(bytes(u.mem_read(0x02003cb0+0x1f04,4))==bytes(4),'loaded state no longer carries JST1')

out=Path(meta['path']).parent/('memory-fixes-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=fix['baseSha1'],checks=checks,parentReactionDifferences=changed,
            actionTableEnd=end,frames=frames)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),report=str(out/'report.json'))))
