"""Bounded shop-only update on the accepted AI-speed candidate. No save writes.

Compile only the Buy constructor; redirect its existing entry and preserve all
other gameplay code. Retain the original entry in the symbol map so native
callers and tests both traverse the installed hook. Explicit Thumb BX veneers
call the exact parent's inventory helpers on ARM7TDMI.
"""
import datetime, hashlib, json, struct, subprocess
from pathlib import Path
from shop_progression import ROOT, PARENT, PARENT_SHA1, catalog

START, END = 0x1ffc000, 0x1ffe000
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p, text): p.write_bytes(text.encode('utf-8'))

def main():
    meta=json.loads(PARENT.read_text()); original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']==PARENT_SHA1
    assert original[START:END]==b'\xff'*(END-START), 'Shop reservation occupied'
    rows=catalog(); out=ROOT/'build/expansion/shop-progression'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    write(out/'registry.h','#define FFTA_MAX_ITEM 470u\n')
    write(out/'stock.h','#include <stdint.h>\nstatic const struct {uint16_t item,flag;uint8_t towns;} ffta_stock[]={\n'+
          ',\n'.join('{%d,%d,%d}'%(r['id'],r['flag'],r['towns']) for r in rows)+'\n};\n')
    sy=meta['symbols']; helpers=('ffta_owned','ffta_equipped')
    write(out/'imports.s','.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'+''.join(
        f'.align 2\n.global {n}\n.thumb_func\n{n}:\n ldr r3,={sy[n]|1:#x}\n bx r3\n.ltorg\n' for n in helpers))
    write(out/'link.ld','SECTIONS { . = 0x09ffc000; .text : { *(.text*) *(.rodata*) } '+
          '.unexpected : { *(.data*) *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment*) *(.ARM.attributes*) } '+
          'ASSERT(SIZEOF(.text)<=0x2000,"Shop reservation overflow") ASSERT(SIZEOF(.unexpected)==0,"No new persistent state") }\n')
    prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-'); elf=out/'shop.elf'; binary=out/'shop.bin'
    command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin',
             '-nostdlib','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',
             '-I',str(out),'-I',str(ROOT/'src/engine'),'-Wl,--gc-sections','-Wl,-e,ffta_shop_buy_list',
             '-Wl,-T,'+str(out/'link.ld'),str(ROOT/'src/engine/inventory-menus.c'),str(out/'imports.s'),'-o',str(elf)]
    run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    write(out/'compile.log',run.stdout+run.stderr);run.check_returncode()
    subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
    built={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
    code=binary.read_bytes(); assert len(code)<=END-START
    rom=bytearray(original); patches=[]
    def patch(at,raw,label):
        patches.append(dict(offset=at,before=original[at:at+len(raw)].hex(),after=raw.hex(),label=label))
        rom[at:at+len(raw)]=raw
    patch(START,code,'Buy constructor and constant stock table')
    at=sy['ffta_shop_buy_list']-0x08000000;assert at%4==0
    assert original[at:at+4].hex()=='f0b5de46', 'Unexpected parent shop entry'
    # Preserve r3 (town identity), unlike the ordinary three-argument veneer.
    # A Thumb BX ip precedes the literal; use an aligned 16-byte trampoline.
    patch(at,struct.pack('<6HI',0xb408,0x4b02,0x469c,0xbc08,0x4760,0x46c0,built['ffta_shop_buy_list']|1),'shop entry')
    items=struct.unpack_from('<I',original,0x79aec)[0]-0x08000000
    for r in rows:
        pos=items+r['id']*32
        assert original[pos+16]==r['attack'],r['name']
        assert struct.unpack_from('<HH',original,pos+4)==(r['oldPrice'],r['oldPrice']//2),r['name']
        if r['price']!=r['oldPrice']:patch(pos+4,struct.pack('<HH',r['price'],r['price']//2),r['name']+' buy/sell')
    allowed={p['offset']+i for p in patches for i in range(len(bytes.fromhex(p['after'])))}
    assert len(rom)==len(original) and all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    path=out/'FFTA_Reviewed_All_Classes.gba';path.write_bytes(rom)
    meta.update(path=str(path),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['shopProgression']=dict(parent=str(PARENT),baseSha1=PARENT_SHA1,reservation=[START,END],used=[START,START+len(code)],
        patches=patches,prices=rows,compileCommand=command,symbols=built,
        sources={p:sha((ROOT/p).read_bytes()) for p in ('scripts/shop_progression.py','scripts/build-shop-progression.py','src/engine/inventory-menus.c',
                'notes/equipment-acquisition.json','notes/chemist-progression-equipment.json')},
        helpers={n:dict(address=sy[n],first32Sha256=sha(original[sy[n]-0x08000000:sy[n]-0x08000000+32])) for n in helpers})
    manifest=out/'manifest.json';write(manifest,json.dumps(meta,indent=2)+'\n')
    write(out.parent/'current.json',json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(romSha1=meta['romSha1'],manifest=str(manifest),codeBytes=len(code),priceChanges=sum(r['price']!=r['oldPrice'] for r in rows))))

if __name__=='__main__':main()
