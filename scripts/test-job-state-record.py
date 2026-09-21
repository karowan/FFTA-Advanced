"""Native ARM tests of owned canonical records and checked save footer.

Callable module only. Does not claim installed save hooks or copy integration.
"""
import ast,collections,hashlib,json,pathlib,struct,subprocess,sys,zlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'combat.json').read_text())
base=(P/'combat.gba').read_bytes();assert hashlib.sha1(base).hexdigest()==meta['romSha1']
old={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
OUT=P/'job-state-record'/meta['romSha1'];OUT.mkdir(parents=True,exist_ok=True)
(OUT/'bindings.s').write_text(f'''.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_storage_format
.thumb_func
ffta_storage_format:
 ldr r3,={old['ffta_storage_format']|1}
 bx r3
.ltorg
''')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'record.elf';binary=OUT/'record.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11',
 '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
 '-Wl,-Ttext=0x091d0000,-e,ffta_job_reset',str(ROOT/'src/engine/job-state.c'),
 str(OUT/'bindings.s'),'-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert rom[0x11d0000:0x11d0000+len(code)]==b'\xff'*len(code)
rom[0x11d0000:0x11d0000+len(code)]=code;(OUT/'record.gba').write_bytes(rom)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,bytes(0x8000));counts=collections.Counter()
def check(kind,actual,wanted):counts[kind]+=1;assert actual==wanted,(kind,actual,wanted)
def call(n,*a):return m.call(symbols[n],*a)
BANK=0x0203f400;BUFFER=0x02010001
m.put(0x02001e70,b'FFTAEXP1\x01');m.put(BANK-4,b'\xD7'*820)
check('foreign-uninitialized',call('ffta_job_state',UNIT),0)
call('ffta_job_reset');check('reset-payload',m.read(BANK+16,792),bytes(792))
check('left-guard',m.read(BANK-4,4),b'\xD7'*4);check('right-guard',m.read(BANK+808,8),b'\xD7'*8)
units=[UNIT+i*264 for i in range(24)]+[0x02002fc4+i*264 for i in range(12)]
for i,u in enumerate(units):
 check('canonical-state',call('ffta_job_state',u),BANK+16+i*22)
 check('canonical-origin',call('ffta_job_origin',u),i+1)
 check('native-preference',call('ffta_job_potion',u),0x02001e80+i if i<24 else 0)
 for delta in (-1,1,4,263):
  if u+delta not in units:
   check('interior-foreign',call('ffta_job_state',u+delta),0)
   check('foreign-origin',call('ffta_job_origin',u+delta),0)
payload=bytes((i*73+17)&255 for i in range(792));m.put(BANK+16,payload)
for generation in (0,1,0xffffffff):
 for align in (0,1):
  out=BUFFER+align;call('ffta_job_footer_encode',out,generation);encoded=m.read(out,824)
  check('footer-payload',encoded[32:],payload)
  oracle=bytearray(encoded);oracle[16:20]=bytes(4)
  check('independent-crc32',struct.unpack_from('<I',encoded,16)[0],zlib.crc32(oracle))
  call('ffta_job_reset');check('decode-valid',call('ffta_job_footer_decode',out,generation),1)
  check('decoded-bank',m.read(BANK+16,792),payload)
  for byte in range(824):
   altered=bytearray(encoded);altered[byte]^=0x80;m.put(out,altered)
   before=m.read(BANK,808);check('corruption-rejected',call('ffta_job_footer_decode',out,generation),0)
   check('failure-no-publication',m.read(BANK,808),before)
   check('decoder-restores-input',m.read(out,824),bytes(altered))
  m.put(out,encoded);check('generation-binding',call('ffta_job_footer_decode',out,generation^1),0)
# Schema1 migration: preserve assigned bytes only, initialize all newly
# assigned fields, check every legacy byte for corruption before publication.
legacy_payload=bytes((i*29+3)&255 for i in range(576))
legacy=bytearray(608);legacy[:8]=b'FFTAJS01';legacy[8:11]=bytes((1,16,36))
struct.pack_into('<II',legacy,20,576,0);struct.pack_into('<I',legacy,12,91)
legacy[32:]=legacy_payload;struct.pack_into('<I',legacy,16,zlib.crc32(legacy))
expected=bytearray(792)
for i in range(36):
 for j in range(15):
  if j!=3:expected[i*22+j]=legacy_payload[i*16+j]
m.put(BUFFER,legacy);check('legacy-valid',call('ffta_job_footer_decode',BUFFER,91),1)
check('legacy-assigned-state-and-empty-new-fields',m.read(BANK+16,792),bytes(expected))
for i in range(608):
 bad=bytearray(legacy);bad[i]^=1;m.put(BUFFER,bad);before=m.read(BANK,808)
 check('legacy-corruption-rejected',call('ffta_job_footer_decode',BUFFER,91),0)
 check('legacy-failure-no-publication',m.read(BANK,808),before)
report=dict(passed=True,romSha1=hashlib.sha1(rom).hexdigest(),total=sum(counts.values()),checks=dict(counts),
 scope='Callable native record/serialization tests; installed lifecycle, save hooks and copy ownership pending')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
