"""Compile a coherent private Fell/Exposed candidate from production sources."""
import hashlib,json,pathlib,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes';sha=lambda x:hashlib.sha1(x).hexdigest()
base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());engine=(ROOT/'build/expansion/engine.bin').read_bytes()
assert sha(base)==meta['romSha1'] and sha(engine)==meta['engineSha1']
assert base[0x1100000:0x1100000+len(engine)]==engine
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
OUT=P/'fell-private'/sha(base);OUT.mkdir(parents=True,exist_ok=True)
names=['ffta_owned_exposed','ffta_dark_weapon_valid','ffta_physical_rider_reference','ffta_finisher_numerator','ffta_projectile_los','ffta_arc_geometry']
stubs='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
for name in names:
 stubs+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,={old[name]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(stubs)
sources=[ROOT/'src/engine'/name for name in ['combat.c','combat-hooks.s','combat-geometry.c','combat-geometry.s','exposed-effects.c','exposed-effects.s','status-display.c','status-display.s','samurai-state.c']]
subprocess.run([str(pathlib.Path(__import__('sys').executable)),str(ROOT/'scripts/generate-status-glyphs.py')],check=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'fell.elf';binary=OUT/'fell.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091b0000,-e,ffta_exposed_paid_entry',*map(str,sources),str(OUT/'bindings.s'),'-lgcc','-o',str(elf)],cwd=ROOT,check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert rom[0x11b0000:0x11b0000+len(code)]==b'\xff'*len(code);rom[0x11b0000:0x11b0000+len(code)]=code
changes=[]
for start,end,name in [(0x1300e2,0x1300f2,'ffta_physical_final_entry'),(0xa0014,0xa0020,'ffta_combat_geometry_entry'),(0x130654,0x130660,'ffta_weapon_drain_entry'),(0x130688,0x130694,'ffta_weapon_effect_entry')]:
 jump=(start+5)&~3;assert struct.unpack_from('<I',rom,jump+4)[0]==old[name]|1
 rom[start:end]=b'\xc0\x46'*((end-start)//2);struct.pack_into('<H',rom,start,0xb408);struct.pack_into('<HHI',rom,jump,0x4b00,0x4718,symbols[name]|1);changes.append(dict(offset=start,bytes=end-start,name=name))
for offset,name in [(0x3a8604+8*4,'ffta_physical_eligibility_entry'),(0x3a86f8+30*4,'ffta_physical_magnitude_entry')]:
 assert struct.unpack_from('<I',rom,offset)[0]==old[name]|1;struct.pack_into('<I',rom,offset,symbols[name]|1)
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
lesson=next(l for l in registry['lessons'] if l['id']=='GLD-AX-A4');assert lesson['globalAbilityId']==431
table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000;offset=table+431*28;assert not any(rom[offset:offset+28])
record=bytearray(clean[0x55187c+112*28:0x55187c+113*28]);struct.pack_into('<H',record,0,lesson['nameId']);record[4]=16;record[7]=2;record[12:16]=bytes([63,1,1,1]);struct.pack_into('<H',record,22,0);rom[offset:offset+28]=record
(OUT/'input.gba').write_bytes(rom);(OUT/'symbols.json').write_text(json.dumps(symbols))
js="import fs from'node:fs';import{patchExposedEffects}from'./scripts/patch-exposed-effects.mjs';import{patchStatusDisplay}from'./scripts/patch-status-display.mjs';const p=process.argv[1],b=fs.readFileSync(p+'/input.gba'),s=JSON.parse(fs.readFileSync(p+'/symbols.json'));const h=[...patchExposedEffects(b,s,{application:true,incoming:true}),...patchStatusDisplay(b,s)];fs.writeFileSync(p+'/patched.gba',b);fs.writeFileSync(p+'/hooks.json',JSON.stringify(h));"
subprocess.run(['node','--input-type=module','-e',js,str(OUT)],cwd=ROOT,check=True)
rom=(OUT/'patched.gba').read_bytes();LAB=OUT/sha(rom);LAB.mkdir(exist_ok=True)
(LAB/'fell.gba').write_bytes(rom);(LAB/'base.gba').write_bytes(base)
report=dict(status='Private Fell/Exposed candidate: full acceptance pending',baseSha1=sha(base),romSha1=sha(rom),path=str(LAB/'fell.gba'),symbols=symbols,changes=changes+json.loads((OUT/'hooks.json').read_text()))
(LAB/'manifest.json').write_text(json.dumps(report,indent=2));(P/'fell-private/current.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('symbols','changes')},indent=2))
