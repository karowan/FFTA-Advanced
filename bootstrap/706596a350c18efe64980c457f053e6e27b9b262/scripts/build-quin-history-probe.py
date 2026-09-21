"""Private acceptance ROM; shared production integration is owned by Build Engine.

No save is modified. Runtime startup/load calls to ffta_quin_prepare must be
installed by the production integrator; this probe exposes its address so native
fixtures can initialize at the equivalent pre-mission boundary.
"""
import hashlib,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/probes/quin-history';OUT.mkdir(parents=True,exist_ok=True)
source=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/expansion/probes/mission-lab/frozen.gba'
rom=bytearray(source.read_bytes());prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
files=['quin-history.c','quin-history.s']
for name in files:(OUT/name).write_bytes((ROOT/'src/engine'/name).read_bytes())
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x09f00000','-Wl,-e,ffta_quin_candidate_entry',*[str(OUT/s) for s in files],'-o',str(OUT/'hooks.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'hooks.elf'),str(OUT/'hooks.bin')],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'hooks.elf')],text=True).splitlines() if len(p:=l.split())==3}
binary=(OUT/'hooks.bin').read_bytes();assert set(rom[0x1f00000:0x1f00000+len(binary)])<={255},'private code space occupied'
rom[0x1f00000:0x1f00000+len(binary)]=binary
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
sites=[(0xd241c,8,'ffta_quin_candidate_entry'),(0x807d4,8,'ffta_quin_accept_entry'),(0x62004,12,'ffta_quin_swap_entry')]
for address,size,name in sites:
 assert rom[address:address+size]==clean[address:address+size],('preimage',hex(address))
 if address%4:struct.pack_into('<HHHI',rom,address,0x4b01,0x4718,0x46c0,symbols[name]|1)
 else:
  struct.pack_into('<HHI',rom,address,0x4b00,0x4718,symbols[name]|1)
  for p in range(address+8,address+size,2):struct.pack_into('<H',rom,p,0x46c0)
(OUT/'quin-history.gba').write_bytes(rom)
meta={'source':str(source),'sourceSha1':hashlib.sha1(source.read_bytes()).hexdigest(),'romSha1':hashlib.sha1(rom).hexdigest(),'symbols':symbols,'hooks':sites,'startupIntegration':'pending parent production integration'}
(OUT/'quin-history.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'romSha1':meta['romSha1'],'bytes':len(binary)}))
