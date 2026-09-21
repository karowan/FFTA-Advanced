"""Isolated saved Exposed byte ownership, native copy/clear and SRAM lifecycle."""
import ast,ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
OUT=ROOT/'build/expansion/probes/exposed-storage';OUT.mkdir(exist_ok=True)
CURRENT='--current' in sys.argv
sha=lambda b:hashlib.sha1(b).hexdigest();word=lambda b,p:struct.unpack_from('<I',b,p)[0]
base=(ROOT/'build/expansion/probes/combat.gba').read_bytes();manifest=json.loads((ROOT/'build/expansion/probes/combat.json').read_text());assert sha(base)==manifest['romSha1']
engine=(ROOT/'build/expansion/engine.bin').read_bytes();assert sha(engine)==manifest['engineSha1'];assert base[0x1100000:0x1100000+len(engine)]==engine
old={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
if CURRENT:OUT=OUT/'current'/sha(base);OUT.mkdir(parents=True,exist_ok=True)
(OUT/'base.gba').write_bytes(base);(OUT/'base.json').write_text(json.dumps(manifest,indent=2))
if CURRENT:
 symbols=old;image=bytearray(base);binary=engine
else:
 prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
 sources=['persistent.c','unit-copies.c','battle-state.c','blade-wound.c','evaluated-units.c','runtime.c']
 subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091d0000','-Wl,-e,ffta_state_exposed',*[str(ROOT/'src/engine'/s) for s in sources],'-lgcc','-o',str(OUT/'isolated.elf')],check=True)
 subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'isolated.elf'),str(OUT/'isolated.bin')],check=True)
 symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'isolated.elf')],text=True).splitlines() if len(p:=l.split())==3}
 image=bytearray(base);binary=(OUT/'isolated.bin').read_bytes();image[0x11d0000:0x11d0000+len(binary)]=binary
 for name,address in symbols.items():
  if name in ('ffta_on_unit_copy','ffta_on_unit_clear','ffta_swap_extra','ffta_clear_extra','ffta_clear_copy_extra'):
   p=old[name]-0x08000000
   if p%4:struct.pack_into('<HHHI',image,p,0x46c0,0x4b00,0x4718,address|1)
   else:struct.pack_into('<HHI',image,p,0x4b00,0x4718,address|1)
ROM=OUT/'isolated.gba';ROM.write_bytes(image)
h=runpy.run_path(str(ROOT/'scripts/emulator-test.py'));e=h['Emulator'](ROM)
try:e.run(60);iwram=C.string_at(*e.maps[0x03000000])
finally:e.close()
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
a=ARM(bytes(image),iwram);checks={}
def check(label,got,want):assert got==want,(label,got,want);checks[label]=checks.get(label,0)+1
def call(name,*args,**kwargs):return a.call(symbols[name],*args,**kwargs)
def init(state=0x02000000):a.put(state,bytes(0x4000));a.put(state+0x1e70,b'FFTAEXP1\x01')
def addr(unit):return call('ffta_owned_exposed',unit)
units=[UNIT+i*264 for i in range(24)]+[0x02002fc4+i*264 for i in range(12)]
init();check('native enemy domain base',word(base,0xc83b8),0x02002fc4)
# Native allocator consumes exactly twelve slots, without identity guessing.
for i in range(12):check('native enemy allocator',a.call(0x080c83a4),units[24+i]);a.put(units[24+i]+4,b'\x01')
check('native enemy domain exhausted',a.call(0x080c83a4),0)
for state in (0x02000000,0x02003cb0,0x02008000):
 init(state)
 for i,live in enumerate(units):
  p=live-0x02000000+state
  check('relative canonical domain',call('ffta_state_exposed',state,p),state+0x1e98+i)
  for delta in (-1,1,4,263):check('reject inexact',call('ffta_state_exposed',state,p+delta),0)
 check('reject mixed staging live',call('ffta_state_exposed',state,0x02018000),0)
for version in (0,2):
 init();a.put(0x02001e78,bytes([version]))
 check('invalid format rejected',call('ffta_state_exposed',0x02000000,UNIT),0)
init();a.put(0x02001e98,b'\x01'*36);before=a.read(0x02000000,0x3ca8)
check('format1 no remigration',call('ffta_migrate_inventory',0x02000000),0)
check('format1 state retained',a.read(0x02000000,0x3ca8),before)
# Exact native-copy dispatch and explicit registered tails.
init();heap=0x02018000;a.call(0x080070c8,heap,0x27000)
def alloc(size):p=a.call(0x08007138,heap,size);assert p;return p
snapshot=alloc(0x1014);manager=alloc(0x400);selection=alloc(0x3828);party=alloc(0x7268)
call('ffta_snapshot_register',snapshot);call('ffta_manager_register',manager);call('ffta_selection_register',selection)
a.put(0x0200f4b0,struct.pack('<I',manager));a.put(0x0200f454,struct.pack('<I',selection));a.put(0x03002818,struct.pack('<I',party));call('ffta_party_copy_register')
copies=[snapshot+4+i*264 for i in range(13)]+[manager+0x40,manager+0x148,selection+0xa4c,party+0x1be4]
allunits=units+copies+[0x02006000];owned={p:addr(p) for p in allunits};entry=word(image,0x36d4bc);clear=word(image,0x36d4b8)
for residue in (0,4):
 for source in allunits:
  for target in allunits:
   for p in allunits:
    if owned[p]:a.put(owned[p],bytes([(p>>2)&1]))
   to,fr=owned[target],owned[source];want=a.read(fr,1) if fr else b'\0'
   before=a.read(0x02001e98,36)
   a.call(entry,target,source,264,stack=STACK+residue)
   if to:check('native copy state',a.read(to,1),want)
   for i,p in enumerate(units):
    if p!=target:check('other canonical isolation',a.read(0x02001e98+i,1),before[i:i+1])
 for p in units+copies:
  a.put(addr(p),b'\x01');a.call(clear,p,263,stack=STACK+residue);check('partial clear preserves',a.read(addr(p),1),b'\x01')
  a.call(clear,p,264,stack=STACK+residue);check('whole clear resets',a.read(addr(p),1),b'\0')
a.put(0x02001e98,b'\x01'*36);a.call(clear,0x02002fc4,12*264);check('bulk enemy clear',a.read(0x02001e98,36),b'\x01'*24+b'\0'*12)
# Deliberately unsupported evaluator copies: Shatter's stack prediction and
# native law1343C8's plain264-byte allocation have no registered Extra tail.
# Copying native bytes must neither alias their source state nor invent ownership.
for temporary in (0x03006000,alloc(264)):
 a.put(addr(UNIT),b'\x01');a.call(entry,temporary,UNIT,264)
 check('unowned ephemeral rejected',addr(temporary),0)
 check('unowned ephemeral source retained',a.read(addr(UNIT),1),b'\x01')
# Explicit slot swap tracks physical roster ordering; padding has no effect on AP.
a.put(0x02001e98,bytes(range(36)));call('ffta_swap_extra',0x02000000,2,3);expected=bytearray(range(36));expected[2],expected[3]=3,2;check('sort state',a.read(0x02001e98,36),bytes(expected))
report={'passed':True,'currentBuild':CURRENT,'baseSha1':sha(base),'romSha1':sha(image),'binarySha1':sha(binary),'checks':checks,'total':sum(checks.values())}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
