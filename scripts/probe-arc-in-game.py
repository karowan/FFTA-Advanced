"""Isolated directional UI discovery; cross-ROM state is diagnostic only."""
import ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/'build/expansion/probes/tomahawk-in-game/5b90d5fb623457405d96948e33df623b342da14c'
OUT=ROOT/'build/expansion/probes/arc-ui-lab';OUT.mkdir(exist_ok=True)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
geometry=(ROOT/'src/engine/combat-geometry.c').read_text()
geometry=geometry.replace('extern unsigned ffta_projectile_los', 'extern unsigned ffta_arc_geometry(unsigned,unsigned,unsigned,unsigned);\nextern unsigned ffta_projectile_los')
geometry=geometry.replace('    unsigned result=ffta_original_combat_geometry', '''    if((uint16_t)action==FFTA_SLD_AX_A3 || (uint16_t)action==FFTA_GLD_AX_A2)
        return ffta_arc_geometry((uint8_t)actor_x,(uint8_t)actor_y,(uint8_t)target_x,(uint8_t)target_y);
    unsigned result=ffta_original_combat_geometry''')
(OUT/'geometry.c').write_text(geometry)
sources=[ROOT/'src/engine/combat-area.c',ROOT/'src/engine/combat-area.s',OUT/'geometry.c',ROOT/'src/engine/combat-geometry.s',ROOT/'src/engine/projectile-los.c']
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091f0000','-Wl,-e,ffta_area_list',*[str(s) for s in sources],'-lgcc','-o',str(OUT/'arc.elf')],check=True,capture_output=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'arc.elf'),str(OUT/'arc.bin')],check=True,capture_output=True)
txt=subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'arc.elf')],text=True)
symbols={l.split()[2]:int(l.split()[0],16) for l in txt.splitlines() if len(l.split())==3}
rom=bytearray((FIX/'frozen.gba').read_bytes());code=(OUT/'arc.bin').read_bytes()
assert rom[0x11f0000:0x11f0000+len(code)]==b'\xff'*len(code)
rom[0x11f0000:0x11f0000+len(code)]=code
for p,name in [(0xb4a1c,'ffta_area_list_entry'),(0xa0014,'ffta_combat_geometry_entry'),(0x96a40,'ffta_arc_launch_entry')]:
 struct.pack_into('<HHHHI',rom,p,0xb408,0x46c0,0x4b00,0x4718,symbols[name]|1)
for p,name in [(0xb6fb6,'ffta_arc_confirm_entry'),(0xa3aba,'ffta_arc_commit_entry')]:
 struct.pack_into('<HHHI',rom,p,0xb408,0x4b00,0x4718,symbols[name]|1)
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();row=bytearray(clean[0x55187c+103*28:0x55187c+104*28])
struct.pack_into('<H',row,0,886);row[4]=4;row[5]=1;row[7]=2;row[9]=0;row[12:16]=bytes((63,1,1,1))
struct.pack_into('<HH',row,20,110,0);table=struct.unpack_from('<I',rom,0xccd84)[0]-0x08000000
rom[table+426*28:table+427*28]=row
struct.pack_into('<H',row,0,891);row[4]=8
rom[table+429*28:table+430*28]=row;ROM=OUT/'frozen.gba';ROM.write_bytes(rom)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))
def tap(e,k,wait=180):e.run(8,k);e.run(wait)
def capture(e,label):
 e.screenshot(OUT/(label+'.png'));e.save(OUT/(label+'.state'));(OUT/(label+'.ram')).write_bytes(e.memory())
 print(label,flush=True)
e=h['Emulator'](ROM)
try:
 e.load(FIX/'marche-turn.state');e.run(1)
 e.set_memory(0xaa,struct.pack('<H',455));e.set_memory(0x1b5d,b'\0');e.set_memory(0x1b5e,b'\x94')
 for key in [256,128,128,32]:tap(e,key)
 tap(e,256,600);capture(e,'moved')
 for key in [256,32,256,32]:tap(e,key)
 capture(e,'overpower-menu');tap(e,256);capture(e,'targeting')
 for i,key in enumerate([128,32,64,16]):tap(e,key);capture(e,f'facing-{i}')
 tap(e,128);capture(e,'east');tap(e,256);capture(e,'preview');tap(e,256);capture(e,'confirmation');tap(e,256,1800);capture(e,'executed')
finally:e.close()
e=h['Emulator'](ROM)
try:
 e.load(FIX/'initial.state');e.run(1)
 # Legal Bangaa Gladiator with Reaping Arc. Reposition Leonard in this
 # disposable diagnostic by native unit and battlefield-wrapper coordinates.
 for offset in (5,7,0x35):e.set_memory(0x398+offset,b'\x10')
 e.set_memory(0x398+0x2a,struct.pack('<5H',458,0,0,0,0));e.set_memory(0x398+0x40+106,b'\x99')
 e.set_memory(0x4a0+0xf6,bytes((2,15)));e.set_memory(0x22904+8,struct.pack('<H',2*32+16))
 r=e.memory();grid=struct.unpack_from('<I',r,0x7f14)[0]-0x02000000
 e.set_memory(0x22904+10,struct.pack('<H',r[grid+2*(15*16+2)]*16))
 for target in (0x80,0x188,0x4a0):e.set_memory(target+0x18,struct.pack('<HH',999,999))
 capture(e,'reaping-initial')
 tap(e,32);tap(e,256);tap(e,32);tap(e,256);tap(e,32);capture(e,'reaping-menu')
 tap(e,256);tap(e,128);capture(e,'reaping-targets')
 tap(e,256);capture(e,'reaping-preview');tap(e,256);capture(e,'reaping-confirmation');tap(e,256,2400);capture(e,'reaping-executed')
finally:e.close()
(OUT/'diagnostic.json').write_text(json.dumps({'romSha1':hashlib.sha1(rom).hexdigest(),'scope':'Isolated426 directional UI donor; native eligibility/magnitude; not production acceptance'},indent=2))
