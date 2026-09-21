"""Compare original and rebuilt menu figures through the real ARM decoder.

No consumer or BIOS function is mocked. This does not establish displayed UI,
per-job palette choice, new artwork or production acceptance.
"""
import datetime, hashlib, json, struct, sys
from native_art import ROOT, palette, tile_image, pack_tiles, sha
from native_miniatures import CONTAINER, decode, encode
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

ROM=0x08000000; SOURCE=0x02010000; DEST=0x02020020
RETURN=0x08000100; STACK=0x03007000; CAPACITY=640*55
rom=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(rom).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
images=[decode(rom,CONTAINER,i) for i in range(54)]
rebuilt=encode(images+[images[4]])
assert len(rebuilt)<DEST-SOURCE-32
out=ROOT/'build/art/miniature-decoder'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True,exist_ok=False)
machine=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
for address,size in [(0x02000000,0x40000),(0x03000000,0x8000),(ROM,0x2000000)]: machine.mem_map(address,size)
machine.mem_write(ROM,rom);machine.mem_write(SOURCE,rebuilt)
checks=[];scenarios=[]

def check(value,label):
    assert value,label
    checks.append(label)

def call(base,index,count,expected,stack_offset=0):
    label=f'{base:x}/index{index}/count{count}/stack{stack_offset}'
    machine.mem_write(DEST-32,b'\xa5'*(CAPACITY+64))
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[base,DEST,index,count]): machine.reg_write(reg,value)
    saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
    for i,reg in enumerate(saved):machine.reg_write(reg,0x55000000+i)
    machine.reg_write(UC_ARM_REG_SP,STACK+stack_offset);machine.reg_write(UC_ARM_REG_LR,RETURN|1)
    machine.emu_start(0x08005319,RETURN,count=1500000)
    check(machine.reg_read(UC_ARM_REG_PC)==RETURN,label+' native return')
    check(machine.reg_read(UC_ARM_REG_SP)==STACK+stack_offset and all(machine.reg_read(r)==0x55000000+i for i,r in enumerate(saved)),label+' native ABI')
    check(machine.reg_read(UC_ARM_REG_R0)==(1 if not expected else 0),label+' return status')
    observed=bytes(machine.mem_read(DEST,len(expected)))
    check(observed==expected,label+' exact decoded bytes')
    check(bytes(machine.mem_read(DEST-32,32))==b'\xa5'*32,label+' leading canary')
    check(bytes(machine.mem_read(DEST+len(expected),CAPACITY+32-len(expected)))==b'\xa5'*(CAPACITY+32-len(expected)),label+' complete trailing capacity unchanged')
    scenarios.append(dict(base=hex(base),index=index,count=count,stackOffset=stack_offset,bytes=len(expected),sha256=sha(observed)))

try:
    _,rgb=palette(rom,0x419d80)
    for index,raw in enumerate(images):
        image=tile_image(raw,rgb,32)
        check(image.size==(32,40) and pack_tiles(image,20)==raw,f'image{index} 32x40 lossless pixel layout')
        for offset in (0,4):
            call(ROM+CONTAINER,index,1,raw,offset)
            call(SOURCE,index,1,raw,offset)
    call(SOURCE,54,1,images[4])
    # Real count semantics: zero or count beyond the container means all;
    # the decoder clamps that selection to the entries after start index.
    for base,items in [(ROM+CONTAINER,images),(SOURCE,images+[images[4]])]:
        for start,count in [(0,0),(1,0),(52,10),(0,65535),(53,1)]:
            number=len(items) if count==0 or count>len(items) else count
            call(base,start,count,b''.join(items[start:start+number]))
        for index in (len(items),65535):call(base,index,1,b'')
    # Byte corruption must be visible to this oracle: a changed literal must
    # alter exactly the corresponding decoded pixel byte, not its neighbors.
    changed=bytearray(rebuilt)
    first=int.from_bytes(changed[8:12],'big')+1
    changed[first]^=1
    machine.mem_write(SOURCE,bytes(changed))
    call(SOURCE,0,1,bytes([images[0][0]^1])+images[0][1:])
    check(bytes(machine.mem_read(DEST,640))!=images[0],'corruption control rejects unchanged-pixel claim')
    report=dict(status='passed',sourceRomSha1=hashlib.sha1(rom).hexdigest(),rebuiltSha256=sha(rebuilt),checks=checks,scenarios=scenarios,
                coverage='Native USA05318/051c4 decoder, all54 original images, rebuilt55-entry container with unchanged appended image4, both stack alignments, range/count/invalid-index semantics, output canaries and one positive corruption control. No UI display, palette routing, generated art or production acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),scenarios=len(scenarios),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),sourceRomSha1=hashlib.sha1(rom).hexdigest(),checks=checks,scenarios=scenarios),indent=2)+'\n')
    raise
