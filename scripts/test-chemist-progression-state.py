"""Execute the actual ARM schema-3 codec and footer on deterministic records.

This proves exact serialization/migration, not installed flash hooks or battle
effects. Keep both the compiled ROM and the complete report in ignored build.
"""
import ast, collections, hashlib, json, random, struct, subprocess, sys, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/chemist-progressions/state-tests';OUT.mkdir(parents=True,exist_ok=True)
base=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
assert hashlib.sha1(base).hexdigest()=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
# Storage admission is outside this codec test. The canonical record/reset and
# native CRC are real compiled code; the test-only stub admits our owned bank.
(OUT/'bindings.s').write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n.global ffta_storage_format\n.thumb_func\nffta_storage_format:\n movs r0,#1\n bx lr\n')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'state.elf';binary=OUT/'state.bin'
command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-DFFTA_CHEMIST_PROGRESSION=1',
 '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib',
 '-Wl,-Ttext=0x09a50000,-e,ffta_job_reset',str(ROOT/'src/engine/job-state.c'),
 str(ROOT/'src/engine/chemist-progression-codec.c'),str(OUT/'bindings.s'),'-lgcc','-o',str(elf)]
result=subprocess.run(command,capture_output=True,text=True)
(OUT/'compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
rom=bytearray(base)+bytearray(b'\xff'*(0x2000000-len(base)))
code=binary.read_bytes();rom[0x1a50000:0x1a50000+len(code)]=code
(OUT/'test.gba').write_bytes(rom)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
m=ARM(rom,bytes(0x8000));counts=collections.Counter()
def check(kind,actual,expected):
 counts[kind]+=1
 assert actual==expected,(kind,actual,expected)
def call(name,*args):return m.call(symbols[name],*args)
BANK,BUFFER,RECORD,PACKED=0x0203f400,0x02010001,0x02011000,0x02011101
widths=[3,6,1,8,3,6,6,7,4,0,6,5,8,8,8,8,8,8,8,8,8,7,8,8,8,8,8]
rng=random.Random(20260927)
for n in range(258):
 row=bytes((1<<w)-1 if n==1 else rng.randrange(1<<w) if n>1 else 0 for w in widths)
 m.put(RECORD,row);check('pack-valid',call('ffta_cp_record_pack',PACKED,RECORD),1)
 # Independently assembled integer oracle catches ordering/width mistakes.
 value=0;shift=0
 for b,w in zip(row,widths):value|=b<<shift;shift+=w
 check('packed-oracle',m.read(PACKED,22),value.to_bytes(22,'little'))
 m.put(RECORD,b'\xff'*27);check('unpack-valid',call('ffta_cp_record_unpack',RECORD,PACKED),1)
 check('roundtrip-all-fields',m.read(RECORD,27),row)
for i,w in enumerate(widths):
 if w==8:continue
 row=bytearray(27);row[i]=1<<w;m.put(RECORD,row)
 check('invalid-field-rejected',call('ffta_cp_record_pack',PACKED,RECORD),0)
for pad in (64,128,192):
 m.put(PACKED,bytes(21)+bytes((pad,)))
 check('noncanonical-padding-rejected',call('ffta_cp_record_unpack',RECORD,PACKED),0)
m.put(BANK-4,b'\xd7'*1000);call('ffta_job_reset')
check('left-guard',m.read(BANK-4,4),b'\xd7'*4)
check('right-guard',m.read(BANK+988,8),b'\xd7'*8)
payload=bytes(rng.randrange(1<<w) for n in range(36) for w in widths)
m.put(BANK+16,payload)
check('footer-encode',call('ffta_job_footer_encode',BUFFER,73),1)
encoded=m.read(BUFFER,824);oracle=bytearray(encoded);oracle[16:20]=bytes(4)
check('native-crc',struct.unpack_from('<I',encoded,16)[0],zlib.crc32(oracle))
call('ffta_job_reset');check('decode-current',call('ffta_job_footer_decode',BUFFER,73),1)
check('footer-roundtrip',m.read(BANK+16,972),payload)
for byte in range(824):
 bad=bytearray(encoded);bad[byte]^=128;m.put(BUFFER,bad);before=m.read(BANK,988)
 check('corrupt-footer-rejected',call('ffta_job_footer_decode',BUFFER,73),0)
 check('failed-decode-atomic',m.read(BANK,988),before)
 check('input-preserved',m.read(BUFFER,824),bytes(bad))
for version,width in ((1,16),(2,22)):
 legacy=bytearray(32+36*width);legacy[:8]=f'FFTAJS0{version}'.encode();legacy[8:11]=bytes((version,width,36))
 struct.pack_into('<I',legacy,12,73);struct.pack_into('<I',legacy,20,36*width)
 legacy[32:]=bytes(rng.randrange(1<<widths[i]) for n in range(36) for i in range(width))
 struct.pack_into('<I',legacy,16,zlib.crc32(legacy));m.put(BUFFER,legacy)
 check('legacy-migration',call('ffta_job_footer_decode',BUFFER,73),1)
 expected=bytearray(972)
 for n in range(36):
  for i in range(width):
   if version!=1 or i not in (3,15):expected[n*27+i]=legacy[32+n*width+i]
 check('legacy-preserves-old-clears-new',m.read(BANK+16,972),bytes(expected))
 check('migrated-record-reserializes',call('ffta_job_footer_encode',BUFFER,74),1)
# Exact source tokens are transported through roster reorder; an absent owner
# clears only its fuse, never another caster's trap or smoke.
row=bytearray(27);row[1]=row[5]=row[24]=7;row[2]=1;row[23]=0xef
m.put(RECORD,row);call('ffta_job_record_reindex',RECORD,7,12);row[1]=row[5]=row[24]=12
check('reindex-fuse-owner',m.read(RECORD,27),bytes(row))
call('ffta_job_record_reindex',RECORD,12,0);row[1]=row[2]=row[5]=row[24]=0;row[23]&=63
check('remove-owner-clears-only-owned-fuse',m.read(RECORD,27),bytes(row))
report=dict(passed=True,romSha1=hashlib.sha1(rom).hexdigest(),checks=dict(counts),total=sum(counts.values()),
 scope='ARM codec/footer migration only; installed flash and all copy consumers require later integration acceptance',compileCommand=command)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
