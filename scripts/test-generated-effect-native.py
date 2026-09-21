"""Action-scoped effect selector ABI, native resource loader and reproduction."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_effect_art import reference
from ffta_maps import lz77
from generated_effect_transport import build,TABLE,HOOK
out=ROOT/'build/art/generated-effect/native-tests'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    m=build();rom=Path(m['path']).read_bytes();base=Path(m['source']).read_bytes();pixels=lz77(rom,m['payload']+4).data
    check(sha(pixels)==m['pixelsSha256'],'Authenticated generated pixels')
    sys.path.insert(0,str(ROOT/'tools/arm-python'))
    from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
    from unicorn.arm_const import *
    UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
    tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native effect ARM>','exec'))
    iw=(Path(m['releaseSource']).parent/'fixture/battle-ready.iwram').read_bytes();a=ARM(rom,iw)
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,
        UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12)
    for stack in (0x03007000,0x03006ffc):
        for action in [*range(461),65535]:
            values=[0x66000000+i for i in range(13)];values[4]=0x02021000
            for reg,value in zip(regs,values):a.u.reg_write(reg,value)
            a.put(values[4]+16,struct.pack('<H',action));a.put(stack-16,b'\xa5'*40)
            a.u.reg_write(UC_ARM_REG_SP,stack);a.u.reg_write(UC_ARM_REG_LR,0x08000101)
            a.u.emu_start(0x08000000+HOOK+1,0x08000000+HOOK+8,count=100)
            check(a.u.reg_read(UC_ARM_REG_PC)==0x08000000+HOOK+8,f'{stack:x}/{action} exact native continuation')
            check(a.u.reg_read(UC_ARM_REG_R1)==0x08000000+(m['table'] if action==425 else TABLE),f'{stack:x}/{action} only Tomahawk owns generated resources')
            check(all(a.u.reg_read(reg)==value for reg,value in zip(regs[2:],values[2:])),f'{stack:x}/{action} untouched live registers')
            check(a.u.reg_read(UC_ARM_REG_SP)==stack and a.read(stack,8)==struct.pack('<2I',values[3],values[10])
                and a.read(stack-16,16)==b'\xa5'*16 and a.read(stack+8,16)==b'\xa5'*16,f'{stack:x}/{action} exact stolen stack stores/canaries')
    # The BIOS decompression call is a peripheral boundary; emulate its
    # documented LZ operation, then run both original native loader phases.
    def bios(u,address,size,data):
        source=u.reg_read(UC_ARM_REG_R0)-0x08000000;dest=u.reg_read(UC_ARM_REG_R1)
        a.put(dest,lz77(rom,source).data);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    a.u.hook_add(UC_HOOK_CODE,bios,begin=0x08141890,end=0x08141890)
    for name,table,expected,slack in (('original',TABLE,reference(base)['pixels'],1),('generated',m['table'],pixels,0)):
        state,scratch,dest=0x02020000,0x02025000,0x02027020
        data=bytearray(40);struct.pack_into('<I',data,0,0x08000000+table);data[7]=1
        struct.pack_into('<2I',data,32,scratch,dest);a.put(state,data);a.put(dest-32,b'\xa5'*(len(expected)+65))
        check(a.call(0x080d758c,state)==1,name+' native resource decode stage')
        check(a.call(0x080d7674,state)==1,name+' native resource unpack completion')
        check(a.read(dest,len(expected))==expected,name+' exact native output')
        check(a.read(dest-32,32)==b'\xa5'*32 and a.read(dest+len(expected)+slack,32)==b'\xa5'*32,name+' bounded native staging writes')
    check(rom[TABLE:TABLE+48]==base[TABLE:TABLE+48],'Original effect table exact')
    check(Path(build()['path']).read_bytes()==rom,'Exact generated effect rebuild')
    report=dict(status='passed',romSha1=m['romSha1'],checks=checks,scope='All461 action IDs plusFFFF at two stack residues through installed selector/continuation, live registers/stolen stores/canaries, original and generated native load/unpack with emulated BIOS LZ peripheral, original resources unchanged and exact rebuild. Actual impact playback separate.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print('Artifacts: '+str(out));raise
