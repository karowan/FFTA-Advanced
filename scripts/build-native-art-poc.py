"""Build an isolated Samurai icon POC from hand-drawn indexed pixel rows."""
import json,struct,subprocess
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,pack_tiles,tile_image,palette

def build():
 meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
 original=Path(meta['path']).read_bytes()
 import hashlib
 assert hashlib.sha1(original).hexdigest()=='1b070824a8dad4995434eee3ab40fa08187a6120'
 out=ROOT/'build/art/poc';out.mkdir(parents=True,exist_ok=True)
 ref=json.loads((ROOT/'build/art/native-reference/ui/report.json').read_text())
 donor=next(r for r in ref['records'] if r['job']==6)
 spec=json.loads((ROOT/'src/art/samurai-icon.json').read_text())
 image=tile_image(bytes.fromhex(donor['tilesHex']),palette(original,donor['paletteOffset'])[1],32)
 assert spec['schema']==2 and spec['width']==32 and spec['height']==16
 assert len(spec['rows'])==16 and all(len(row)==32 for row in spec['rows'])
 image.putdata([int(v,16) for row in spec['rows'] for v in row])
 assert sha(image.tobytes())==spec['pixelSha256']
 raw=pack_tiles(image,8);(out/'samurai-icon.bin').write_bytes(raw)
 image.save(out/'samurai-icon.png',bits=4)
 entry=struct.unpack_from('<I',original,0xcb9e4)[0]
 assert original[0xcb9e0:0xcb9e4]==bytes.fromhex('004b1847')
 address=0x09f00000
 assembly=f'''.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.global art_entry
.thumb_func
art_entry:
    lsls r2,r1,#24
    lsrs r2,r2,#24
    cmp r2,#116
    bne original
    push {{r4,lr}}
    ldr r2,=icon
    movs r3,#64
copy:
    ldmia r2!,{{r4}}
    stmia r0!,{{r4}}
    subs r3,#1
    bne copy
    movs r0,#0
    pop {{r4}}
    pop {{r1}}
    bx r1
original:
    ldr r3,={entry}
    bx r3
.ltorg
.align 2
icon:
.incbin "samurai-icon.bin"
'''
 (out/'poc.s').write_text(assembly)
 tool=ROOT/'tools/arm-gnu/bin'
 subprocess.run([str(tool/'arm-none-eabi-as.exe'),'-mcpu=arm7tdmi','-mthumb','poc.s','-o','poc.o'],cwd=out,check=True)
 subprocess.run([str(tool/'arm-none-eabi-ld.exe'),'-Ttext',hex(address),'-e','art_entry','poc.o','-o','poc.elf'],cwd=out,check=True)
 subprocess.run([str(tool/'arm-none-eabi-objcopy.exe'),'-O','binary','poc.elf','poc.bin'],cwd=out,check=True)
 blob=(out/'poc.bin').read_bytes();offset=address-0x08000000
 assert set(original[offset:offset+len(blob)])=={255}
 rom=bytearray(original);rom[offset:offset+len(blob)]=blob
 rom[0xcb9e0:0xcb9e8]=bytes.fromhex('004b1847')+struct.pack('<I',address|1)
 path=out/'native-art-poc.gba';path.write_bytes(rom)
 manifest=dict(romSha1=hashlib.sha1(rom).hexdigest(),baseRomSha1=meta['romSha1'],path=str(path),
               source=str(Path(meta['path'])),authoredSpecSha256=sha((ROOT/'src/art/samurai-icon.json').read_bytes()),
               iconSha256=sha(raw),changes=[dict(offset=0xcb9e0,bytes=8),dict(offset=offset,bytes=len(blob))],
               scope='Private one-icon POC. No installed player build or save touched.')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2));return manifest
if __name__=='__main__':build()
