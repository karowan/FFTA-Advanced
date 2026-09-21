"""Private, guarded integration of two Dark Knight sword arts; no shared outputs."""
import hashlib,json,pathlib,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'build/expansion/probes'
OUT=P/'dark-sword';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha1(b).hexdigest()
rom=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text())
assert sha(rom)==meta['romSha1']
engine=(ROOT/'build/expansion/engine.bin').read_bytes();assert sha(engine)==meta['engineSha1']
symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();frozen=OUT/meta['romSha1'];frozen.mkdir(exist_ok=True)
(frozen/'input.gba').write_bytes(rom);(frozen/'engine.symbols').write_bytes((ROOT/'build/expansion/engine.symbols').read_bytes())
def replace_once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
c=(ROOT/'src/engine/combat.c').read_text()
c=replace_once(c,'static const PhysicalDefinition physical_definitions[]={','extern unsigned ffta_dark_weapon_valid(unsigned,unsigned);\nstatic const PhysicalDefinition physical_definitions[]={\n    {FFTA_DRK_A2,95,100},{FFTA_DRK_A3,75,100},')
c=replace_once(c,'((ItemValue)0x080ca7a5u)(weapon,3)==31','ffta_dark_weapon_valid(action,weapon)')
c=replace_once(c,'((ItemValue)0x080ca7a5u)(weapon,3)!=31','!ffta_dark_weapon_valid(action,weapon)')
(frozen/'combat.c').write_text(c)
asm=(ROOT/'src/engine/combat-hooks.s').read_text()
for label in ('8f','9f'):
 old='    ldr r'+('0' if label=='8f' else '2')+',=FFTA_GLD_AX_A3'
 reg='r0' if label=='8f' else 'r2';value='r1' if label=='8f' else 'r0'
 new=''.join(f'    ldr {reg},=FFTA_DRK_A{n}\n    cmp {value},{reg}\n    beq {label}\n' for n in (2,3))+old
 asm=replace_once(asm,old,new)
(frozen/'combat-hooks.s').write_text(asm)
geometry=(ROOT/'src/engine/combat-geometry.c').read_text()
geometry=replace_once(geometry,'(uint16_t)action!=FFTA_GLD_AX_A3) return result;','(uint16_t)action!=FFTA_GLD_AX_A3 &&\n        (uint16_t)action!=FFTA_DRK_A2 && (uint16_t)action!=FFTA_DRK_A3) return result;')
geometry=replace_once(geometry,'return difference<=2;','return difference<=(((uint16_t)action==FFTA_DRK_A2 || (uint16_t)action==FFTA_DRK_A3)?3:2);')
(frozen/'combat-geometry.c').write_text(geometry)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=frozen/'dark-sword.elf';binary=frozen/'dark-sword.bin'
sources=[frozen/'combat.c',frozen/'combat-hooks.s',frozen/'combat-geometry.c',ROOT/'src/engine/combat-geometry.s',ROOT/'src/engine/dark-sword.c',ROOT/'src/engine/dark-sword-hooks.s']
externs=['ffta_physical_rider_reference','ffta_finisher_numerator','ffta_projectile_los','ffta_arc_geometry']
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
for n in externs:
 bindings+=f'.align 2\n.global {n}\n.thumb_func\n{n}:\n push {{r3}}\n ldr r3,={symbols[n]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(frozen/'bindings.s').write_text(bindings);sources.append(frozen/'bindings.s')
args=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091c0000,--entry=ffta_dark_sword_apply_entry']
subprocess.run(args+list(map(str,sources))+['-lgcc','-o',str(elf)],check=True,cwd=ROOT)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
new={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
code=binary.read_bytes();r=bytearray(rom);assert r[0x11c0000:0x11c0000+len(code)]==b'\xff'*len(code)
r[0x11c0000:0x11c0000+len(code)]=code;changes=[]
def entry(offset,end,name,installed=False):
 if not installed:assert r[offset:end]==clean[offset:end],hex(offset)
 original=bytes(r[offset:end]);r[offset:end]=b'\xc0\x46'*((end-offset)//2)
 struct.pack_into('<H',r,offset,0xb408);jump=(offset+5)&~3;assert jump+8<=end
 struct.pack_into('<HHI',r,jump,0x4b00,0x4718,new[name]|1)
 changes.append(dict(offset=offset,end=end,name=name,original=original.hex()))
for offset,end,name in [(0x1300e2,0x1300f2,'ffta_physical_final_entry'),(0xa0014,0xa0020,'ffta_combat_geometry_entry'),(0x130654,0x130660,'ffta_weapon_drain_entry'),(0x130688,0x130694,'ffta_weapon_effect_entry')]:entry(offset,end,name,True)
entry(0x12f8a4,0x12f8b0,'ffta_dark_sword_element_entry');entry(0xa315a,0xa3166,'ffta_dark_sword_apply_entry')
entry(0x13467a,0x134686,'ffta_dark_sword_law_weapon_entry')
for offset,name in [(0x3a8604+8*4,'ffta_physical_eligibility_entry'),(0x3a86f8+30*4,'ffta_physical_magnitude_entry')]:struct.pack_into('<I',r,offset,new[name]|1)
registry=json.loads((ROOT/'build/expansion/registry.json').read_text());table=struct.unpack_from('<I',r,0xccd84)[0]-0x08000000
for action,mp in [(357,6),(358,4)]:
 lesson=next(x for x in registry['lessons'] if x['globalAbilityId']==action and x['type']=='Action')
 row=bytearray(clean[0x55187c+147*28:0x55187c+148*28]);struct.pack_into('<H',row,0,lesson['nameId'])
 row[2]=0;row[4]=mp;row[5]=1;row[6]=2;row[7]=3;row[12:16]=bytes([63,1,1,1]);struct.pack_into('<H',row,22,0)
 assert not any(r[table+action*28:table+(action+1)*28]);r[table+action*28:table+(action+1)*28]=row
artifact=frozen/sha(r);artifact.mkdir(exist_ok=True)
(artifact/'dark-sword.gba').write_bytes(r);(artifact/'input.gba').write_bytes(rom)
for name in ('engine.symbols','combat.c','combat-hooks.s','combat-geometry.c','bindings.s','dark-sword.elf','dark-sword.bin'):
 (artifact/name).write_bytes((frozen/name).read_bytes())
result=dict(baseSha1=sha(rom),romSha1=sha(r),path=str(artifact/'dark-sword.gba'),symbols=new,changes=changes,actions=[357,358])
(OUT/'current.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='symbols'},indent=2))
