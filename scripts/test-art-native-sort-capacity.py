"""Prove the original draw-sort's 13-pointer boundary on retained actor records.

This is an isolated native-routine diagnosis, not encounter reachability or
capacity acceptance. The 14-actor branch stops immediately after collection;
the 13-actor control truncates only the last linked-list edge on a private clone.
No production ROM, player save or original evidence is modified.
"""
import datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha

sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_CPU_ARM_TI925T, UC_ARM_REG_R0, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

index_path=ROOT/'notes/native-art-sort-inputs.json'
index=json.loads(index_path.read_text())
raw={key:(ROOT/item['path']).read_bytes() for key,item in index['inputs'].items()}
assert all(sha(raw[key])==item['sha256'] for key,item in index['inputs'].items())
rom,ram,iwram=raw['rom'],raw['ram'],raw['iwram']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(clean).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
out=ROOT/'build/art/native-sort-capacity'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True);(out/'input-index.json').write_bytes(index_path.read_bytes())
checks=[];cases=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def word(data,p):return struct.unpack_from('<I',data,p-0x02000000)[0]

try:
    for start,end in [(0x98c20,0x98ce8),(0x9abe8,0x9ac30),(0xc7b74,0xc7b78),(0xc7cc0,0xc7cec),(0x14224c,0x142250)]:
        check(rom[start:end]==clean[start:end],'Exact original native code '+hex(start))
    manager=word(ram,0x0200f4b0);head=word(ram,word(ram,manager+16)+4)
    nodes=[];wrappers=[];units=[]
    while head:
        check(0x02000000<=head<0x0203fff4 and head not in nodes,'Unique bounded list node '+str(len(nodes)))
        nodes.append(head);wrapper=word(ram,head);unit=word(ram,wrapper)
        check(0x02000000<=wrapper<0x0203ff70 and 0x02000000<=unit<0x0203fef8,'Bounded native wrapper/unit '+str(len(nodes)))
        wrappers.append(wrapper);units.append(unit);head=word(ram,head+8)
    check(len(nodes)==14 and len(set(units))==14,'Fourteen distinct actual retained actors')
    check(units[-1]==0x02003a14 and ram[0x3a18]==20,'Fourteenth actor is the original judge')
    # Same original routine at both legal stack residues, on both byte-identical
    # native implementations. Stop before the malformed count enters sorting.
    for source,image in [('candidate',rom),('clean',clean)]:
        for count in (13,14):
            for residue in (0,4):
                m=Uc(UC_ARCH_ARM,UC_MODE_THUMB);m.ctl_set_cpu_model(UC_CPU_ARM_TI925T)
                for address,size in [(0,0x4000),(0x02000000,0x40000),(0x03000000,0x8000),(0x08000000,0x2000000)]:m.mem_map(address,size)
                for address,data in [(0x02000000,ram),(0x03000000,iwram),(0x08000000,image)]:m.mem_write(address,data)
                if count==13:m.mem_write(nodes[12]+8,bytes(4))
                before=bytes(m.mem_read(0x02000000,0x40000))
                stack=0x03007000+residue;frame=stack-28-0x44;counter=frame+0x34
                writes=[]
                def on_write(machine,access,address,size,value,unused):
                    if address<=counter<address+size:writes.append(dict(pc=machine.reg_read(UC_ARM_REG_PC),address=address,size=size,value=value))
                m.hook_add(UC_HOOK_MEM_WRITE,on_write)
                for reg,value in [(UC_ARM_REG_R0,manager),(UC_ARM_REG_SP,stack),(UC_ARM_REG_LR,0x08000101)]:m.reg_write(reg,value)
                m.emu_start(0x08098c21,0x08098c44,count=20000)
                check(m.reg_read(UC_ARM_REG_PC)==0x08098c44,'Collector returns '+str((source,count,residue)))
                actual=struct.unpack('<I',m.mem_read(counter,4))[0]
                expected=count if count==13 else wrappers[-1]+1
                check(actual==expected,'Exact collected counter '+str((source,count,residue)))
                collected=list(struct.unpack('<13I',m.mem_read(frame,52)))
                check(collected==wrappers[:13],'All thirteen in-bounds pointers retained '+str((source,count,residue)))
                check(bytes(m.mem_read(0x02000000,0x40000))==before,'Collection does not write EWRAM '+str((source,count,residue)))
                if count==14:
                    check(writes[-2:]==[dict(pc=0x0809ac22,address=counter,size=4,value=wrappers[-1]),dict(pc=0x0809ac28,address=counter,size=4,value=wrappers[-1]+1)],'Fourteenth pointer overwrites count, then increments it '+str((source,residue)))
                else:
                    m.emu_start(0x08098c45,0x08000100,count=20000)
                    check(m.reg_read(UC_ARM_REG_PC)==0x08000100 and m.reg_read(UC_ARM_REG_SP)==stack,'Thirteen-actor native sort returns with restored stack '+str((source,residue)))
                    after=bytes(m.mem_read(0x02000000,0x40000));allowed={u-0x02000000+offset for u in units[:13] for offset in (0xe7,0x104)}
                    check(all(a==b or p in allowed for p,(a,b) in enumerate(zip(before,after))),'Only native draw order and dirty flags change '+str((source,residue)))
                    ordered=sorted(units[:13],key=lambda u:after[u-0x02000000+0x104])
                    positions=[tuple(before[u-0x02000000+0xf6:u-0x02000000+0xf8]) for u in ordered]
                    check(positions==sorted(positions,reverse=True) and sorted(after[u-0x02000000+0x104] for u in units[:13])==list(range(13)),'Complete native descending position order '+str((source,residue)))
                cases.append(dict(source=source,count=count,stackResidue=residue,counter=actual,counterWrites=writes))
    report=dict(status='passed',checks=checks,cases=cases,romSha1=hashlib.sha1(rom).hexdigest(),inputIndexSha256=sha(index_path.read_bytes()),scope=__doc__)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,cases=cases,error=str(error)),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
