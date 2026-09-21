"""Native queue ABI differential and exact captured-frame append/metadata guards.
Use --chemist for the job's composed hook and exact fresh native fixture.
"""
import argparse,ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools/arm-python'),str(ROOT/'scripts')]
from unicorn import *
from unicorn.arm_const import *
from native_battle_wrappers import from_memory
parser=argparse.ArgumentParser();parser.add_argument('--chemist',action='store_true');parser.add_argument('--integrated',action='store_true');args=parser.parse_args()
P=ROOT/'build/expansion/probes';meta=json.loads((P/('integrated-jobs' if args.integrated else 'chemist' if args.chemist else 'samurai')/'current.json').read_text());path=pathlib.Path(meta['path']);rom=path.read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
S=meta['symbols'];S={**meta.get('upstream',{}).get('symbols',{}),**S}
fix=path.parent/'executor' if args.chemist or args.integrated else P/'samurai-state'/meta['baseSha1']
ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes();regs=struct.unpack_from('<17I',(fix/'execute-trap.state').read_bytes(),0x20)
UNIT,TARGET,STACK,RETURN=0x02000080,0x020033e4,0x03006800,0x08000100
exec(compile(ast.Module(body=[n for n in ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000')).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();native=bytearray(rom);native[0xa4adc:0xa4ae8]=clean[0xa4adc:0xa4ae8]
if not (args.chemist or args.integrated):
 image=bytearray(rom);struct.pack_into('<HHHHI',image,0xa4adc,0xb408,0x46c0,0x4b00,0x4718,S['ffta_reaction_queue_entry']|1);rom=bytes(image)
a,b=ARM(bytes(native),iw),ARM(rom,iw);checks=collections.Counter()
def check(k,a,b):checks[k]+=1;assert a==b,(k,a,b)
allregs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC]
stops=(0x080a4ae8,0x080a529c)
def stop(u,pc,size,data):u.emu_stop()
for m in (a,b):
 for pc in stops:m.u.hook_add(UC_HOOK_CODE,stop,begin=pc,end=pc)
for kind,nonempty,residue,nzcv in itertools.product(range(256),(0,1),(0,4),(0,0xf0000000)):
 results=[]
 for m in (a,b):
  m.put(0x0203ff48,bytes(4));m.put(0x02010000,struct.pack('<I',nonempty)+bytes(10)+bytes([kind,0]))
  m.u.reg_write(UC_ARM_REG_CPSR,nzcv|0x30)
  for i,r in enumerate(allregs[:13]):m.u.reg_write(r,0x12340000+i)
  m.u.reg_write(UC_ARM_REG_R4,0x02010000);m.u.reg_write(UC_ARM_REG_SP,STACK+residue);m.u.reg_write(UC_ARM_REG_LR,0x08001235)
  m.u.emu_start(0x080a4add,0,count=10000)
  results.append(tuple(m.u.reg_read(r) for r in allregs)+(m.u.reg_read(UC_ARM_REG_CPSR)&0xf0000000,))
 check('native_queue_dispatch_all_registers_NZCV_SP',*results)
# Capture authentic native frame/heap/snapshot at exhaustion. Read-only hook.
m=ARM(rom,iw);wrappers={0x02000000+u:0x02000000+w for u,w in from_memory(rom,ram,iw).items()};captures=[]
def capture(u,pc,size,data):
 if not captures:captures.append((u.reg_read(UC_ARM_REG_SP),m.read(0x02000000,0x40000),m.read(0x03000000,0x8000)))
m.u.hook_add(UC_HOOK_CODE,capture,begin=0x080a4adc,end=0x080a4adc)
m.put(0x02000000,ram);m.put(0x03000000,iw)
for unit,x in ((UNIT,4),(TARGET,5)):
 m.put(unit+5,bytes([2,1,2]));m.put(unit+0x35,b'\x02');m.put(unit+0x3a,bytes(2));m.put(unit+0xe8,bytes(8));m.put(unit+0x18,struct.pack('<4H',500,500,999,999));m.put(unit+0x2a,struct.pack('<5H',1,0,0,0,0));m.put(unit+0xf6,bytes([x,14]));m.put(wrappers[unit]+8,struct.pack('<H',x*32));m.put(wrappers[unit]+12,struct.pack('<H',14*32))
m.put(regs[13],struct.pack('<4I',0,0,0,255));m.put(0x030034b0,bytes(4));m.call(0x080a433c,regs[0],wrappers[UNIT],5,14,stack=regs[13]);check('captured_native_frame',len(captures),1)
frame,cram,ciw=captures[0]
def restore():
 m.put(0x02000000,cram);m.put(0x03000000,ciw);root=m.word(0x0203ff48);m.put(root+800,struct.pack('<I',3));return root
for residue,kind,value in itertools.product((0,4),(128,130,131,136,137),(0,362,65535)):
 root=restore();sp=STACK+residue;write=m.word(frame+0x70);m.put(sp,struct.pack('<3I',kind,value,0))
 # Fifth/seventh args: frame,acting,target,action,kind,payload.
 result=m.call(S['ffta_reaction_queue_append'],frame,TARGET,TARGET,432,stack=sp)
 check('explicit_append_accepted',result,1);request=m.read(write,16)
 check('original_primary_wrapper_preserved',struct.unpack_from('<I',request,4)[0],wrappers[UNIT]);check('self_reaction_actor',struct.unpack_from('<I',request)[0],wrappers[TARGET]);check('payload_roundtrip',(request[13]|request[15]<<8),value);check('next_zero_terminator',m.read(write+16,16),bytes(16))
 # Authenticate immutable metadata on the native previous request, with exact child scope.
 obj=m.word(frame+0x20);m.put(obj,struct.pack('<I',wrappers[TARGET]));m.put(obj+0x10,struct.pack('<H',432));m.put(frame+0x6c,struct.pack('<I',write+16))
 check('metadata_exact_request',m.call(S['ffta_reaction_request_metadata'],frame,obj,wrappers[UNIT],stack=sp),(kind<<8)|(value<<16))
 check('metadata_reject_wrong_original',m.call(S['ffta_reaction_request_metadata'],frame,obj,wrappers[TARGET],stack=sp),0)
 for offset in (4,-4):check('metadata_reject_neighbor_frame',m.call(S['ffta_reaction_request_metadata'],frame+offset,obj,wrappers[UNIT],stack=sp),0)
for mutation in ('query','wrongframe','unknownactor','noheader','queuefull','outputfull','dirtyslot','nativekind','badaction','bigpayload'):
 root=restore();f=frame;actor=TARGET;kind=136;action=251;value=362
 if mutation=='query':m.put(root+800,bytes(4))
 if mutation=='wrongframe':f=frame+4
 if mutation=='unknownactor':actor=0x02002000
 if mutation=='noheader':m.put(m.word(frame+0x68)-8,bytes(2))
 if mutation=='queuefull':m.put(frame+0x70,struct.pack('<I',m.word(frame+0x68)+240))
 if mutation=='outputfull':m.put(m.word(frame+0x20)+0x26bd,b'\x0d')
 if mutation=='dirtyslot':m.put(m.word(frame+0x70)+15,b'\x01')
 if mutation=='nativekind':kind=127
 if mutation=='badaction':action=445 if args.integrated else 438
 if mutation=='bigpayload':value=65536
 m.put(STACK,struct.pack('<2I',kind,value));before=m.read(0x02000000,0x40000)
 check('append_guard_'+mutation,m.call(S['ffta_reaction_queue_append'],f,actor,TARGET,action,stack=STACK),0);check('rejected_append_no_RAM_changes',m.read(0x02000000,0x40000),before)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),scope=__doc__)
(path.parent/'reaction-queue-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
