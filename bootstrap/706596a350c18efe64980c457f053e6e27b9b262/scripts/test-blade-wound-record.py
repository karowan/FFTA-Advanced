"""Compile and execute the pending Wound record layer; no gameplay hook enabled.

Exhaustive serialized states, replacement/two-pulse schedules, byte alignment,
canonical/staging owner boundaries and actual native inventory migration.
"""
import ast,collections,hashlib,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());assert hashlib.sha1(base).hexdigest()==meta['romSha1']
old={p[2]:int(p[0],16) for line in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=line.split())==3}
OUT=P/'blade-wound-record'/meta['romSha1'];OUT.mkdir(parents=True,exist_ok=True)
bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.section .text\n'
for name in ('ffta_state_exposed',):
 bindings+=f'.align 2\n.global {name}\n.thumb_func\n{name}:\n push {{r3}}\n ldr r3,={old[name]|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
(OUT/'bindings.s').write_text(bindings)
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'wound.elf';binary=OUT/'wound.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x091d0000,-e,ffta_wound_record_replace',str(ROOT/'src/engine/blade-wound.c'),str(OUT/'bindings.s'),'-lgcc','-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
symbols={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert rom[0x11d0000:0x11d0000+len(code)]==b'\xff'*len(code);rom[0x11d0000:0x11d0000+len(code)]=code
# This is a callable-code fixture only, with no installed native hooks.
sha=hashlib.sha1(rom).hexdigest();ART=OUT/sha;ART.mkdir(exist_ok=True);(ART/'record-test.gba').write_bytes(rom)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
arm=ARM(rom,bytes(0x8000));counts=collections.Counter()
def check(kind,actual,wanted):
 counts[kind]+=1;assert actual==wanted,(kind,actual,wanted)
def call(name,*args):return arm.call(symbols[name],*args)
record=0x02010001
# Independently classify every on-disk value, including inactive garbage and
# invalid count3. Verify exactly two pulses, including a valid zero-size pulse.
for value in range(65536):
 arm.put(record-1,b'\xa5'+struct.pack('<H',value)+b'\x5a')
 count=value>>14;valid=count in (1,2);pulse=value&16383
 check('serialized_remaining',call('ffta_wound_record_remaining',record),count if valid else 0)
 check('first_tick',call('ffta_wound_record_tick',record),pulse if valid else 0)
 check('second_tick',call('ffta_wound_record_tick',record),pulse if count==2 else 0)
 check('third_tick_empty',call('ffta_wound_record_tick',record),0)
 check('retirement_and_byte_guards',arm.read(record-1,4),b'\xa5\0\0\x5a')
for reference,alignment in itertools.product(range(1,32768),(0,1)):
 pointer=record+alignment;arm.put(pointer,struct.pack('<H',0x7fff))
 check('replacement_admitted',call('ffta_wound_record_replace',pointer,reference),1)
 check('replacement_schedules_only_new_pulses',arm.read(pointer,2),struct.pack('<H',0x8000+reference//2))
for reference in (0,32768,65535,0x7fffffff,0xffffffff,0x80000000):
 arm.put(record,b'\x23\x41');check('invalid_reference_rejected',call('ffta_wound_record_replace',record,reference),0)
 check('invalid_preserves_old_schedule',arm.read(record,2),b'\x23\x41')
check('null_replacement',call('ffta_wound_record_replace',0,100),0)
check('null_tick',call('ffta_wound_record_tick',0),0)
check('null_remaining',call('ffta_wound_record_remaining',0),0)
# Use real migrated state blocks at both live and native staging locations.
for state in (0x02000000,0x02003cb0):
 arm.put(state,bytes(0x3ca8));check('native_migration',arm.call(old['ffta_migrate_inventory'],state),1)
 check('migration_reserve_zero',arm.read(state+0x1ebc,96),bytes(96))
 owners={0x80+i*264:i for i in range(24)}|{0x2fc4+i*264:24+i for i in range(12)}
 for offset in range(0x3ca8):
  check('exact_owner_boundaries',call('ffta_state_wound',state,state+offset),state+0x1ebc+2*owners[offset] if offset in owners else 0)
 for offset,index in owners.items():
  pointer=state+0x1ebc+2*index;call('ffta_wound_record_replace',pointer,2*index+1)
 before=arm.read(state,0x3ca8);check('existing_format_migration_noop',arm.call(old['ffta_migrate_inventory'],state),0)
 check('existing_format_preserves_records',arm.read(state,0x3ca8),before)
 for a,b in itertools.product(range(25),repeat=2):
  arm.put(state,before);call('ffta_state_wound_swap',state,a,b);expected=bytearray(before)
  if a<24 and b<24:expected[0x1ebc+2*a:0x1ebe+2*a],expected[0x1ebc+2*b:0x1ebe+2*b]=before[0x1ebc+2*b:0x1ebe+2*b],before[0x1ebc+2*a:0x1ebe+2*a]
  check('roster_swap_whole_state',arm.read(state,0x3ca8),bytes(expected))
 for offset,index in owners.items():
  arm.put(state,before);call('ffta_state_wound_clear',state,state+offset);expected=bytearray(before);expected[0x1ebc+2*index:0x1ebe+2*index]=bytes(2)
  check('owner_clear_whole_state',arm.read(state,0x3ca8),bytes(expected))
 for version in (0,2,255):
  arm.put(state,before);arm.put(state+0x1e78,bytes([version]));unchanged=arm.read(state,0x3ca8)
  check('foreign_format_no_owner',call('ffta_state_wound',state,state+0x80),0)
  call('ffta_state_wound_swap',state,0,1);call('ffta_state_wound_clear',state,state+0x80)
  check('foreign_format_no_writes',arm.read(state,0x3ca8),unchanged)
report=dict(passed=True,romSha1=sha,baseSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Record layer only. No action, owner-copy hook, turn-end HP application, UI or native save-load acceptance.')
(ART/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
