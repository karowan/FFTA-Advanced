"""Packed Centered ownership/state primitive; no action hooks installed here."""
import ast,hashlib,itertools,json,pathlib,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';base=(P/'combat.gba').read_bytes();meta=json.loads((P/'combat.json').read_text());sha=lambda b:hashlib.sha1(b).hexdigest()
engine=(ROOT/'build/expansion/engine.bin').read_bytes();assert sha(base)==meta['romSha1'] and sha(engine)==meta['engineSha1'];assert base[0x1100000:0x1100000+len(engine)]==engine
text=(ROOT/'build/expansion/engine.symbols').read_text();old={p[2]:int(p[0],16) for l in text.splitlines() if len(p:=l.split())==3}
OUT=P/'samurai-state'/sha(base);OUT.mkdir(parents=True,exist_ok=True);(OUT/'frozen.gba').write_bytes(base);(OUT/'engine.symbols').write_text(text)
(OUT/'owner.s').write_text('.syntax unified\n.cpu arm7tdmi\n.thumb\n.global ffta_owned_exposed\n.thumb_func\nffta_owned_exposed:\n ldr r3,='+str(old['ffta_owned_exposed']|1)+'\n bx r3\n.ltorg\n')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=OUT/'state.elf';binary=OUT/'state.bin'
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-I',str(ROOT/'build/expansion'),'-Wl,-Ttext=0x091e0000,-e,ffta_centered_active',str(ROOT/'src/engine/samurai-state.c'),str(ROOT/'src/engine/samurai-state.s'),str(OUT/'owner.s'),'-o',str(elf)],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True);symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=l.split())==3}
rom=bytearray(base);code=binary.read_bytes();assert rom[0x11e0000:0x11e0000+len(code)]==b'\xff'*len(code);rom[0x11e0000:0x11e0000+len(code)]=code;(OUT/'isolated.gba').write_bytes(rom)
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
fix=P/'grace/0e5f3193d77afe7a64b254cc0bdab0377cc02836/fixture';ram=(fix/'battle-ready.ram').read_bytes();iw=(fix/'battle-ready.iwram').read_bytes();m=ARM(rom,iw);checks=0
units=[0x02000080+264*i for i in range(24)]+[0x02002fc4+264*i for i in range(12)]
def reset(unit,value):
 m.put(0x02000000,ram);m.put(0x03000000,iw);idx=units.index(unit);m.put(0x02001e98+idx,bytes([value]));return 0x02001e98+idx
def call(name,*args,residue=0):return m.call(symbols[name],*args,stack=STACK+residue)
def check(ok,msg):
 global checks
 checks+=1;assert ok,msg
for unit,value,residue in itertools.product(units,range(256),(0,4)):
 slot=reset(unit,value);before=m.read(0x02000000,0x40000);v=(value>>1)&7;active=v in (1,2,5,6)
 check(call('ffta_centered_active',unit,residue=residue)==active,('active',value));check(m.read(0x02000000,0x40000)==before,'Query mutation')
 call('ffta_centered_clear',unit,residue=residue);expected=bytearray(before);expected[slot-0x02000000]=value&~14;check(m.read(0x02000000,0x40000)==expected,'Masked clear')
 reset(unit,value);call('ffta_centered_turn_end',unit,residue=residue)
 nv=0 if v in (3,7) else v&3 if v&4 else max(0,v-1);expected[slot-0x02000000]=(value&~14)|(nv<<1);check(m.read(0x02000000,0x40000)==expected,('T2 turn',value,nv))
for value,own,residue in itertools.product(range(256),(0,1),(0,4)):
 slot=reset(UNIT,value);call('ffta_centered_grant',UNIT,own,residue=residue);check(m.read(slot,1)[0]==(value&~14)|(12 if own else 4),'Grant/refresh')
 for expected in ([4,2,0] if own else [2,0]):
  call('ffta_centered_turn_end',UNIT,residue=residue);check(m.read(slot,1)[0]==(value&~14)|expected,'Exact two subsequent turns')
consuming={348,349,350,352,353,354,355}
for action,v,residue in itertools.product(range(432),range(8),(0,4)):
 slot=reset(UNIT,0xf1|(v<<1));active=v in (1,2,5,6)
 check(call('ffta_centered_factor',UNIT,action,residue=residue)==(5 if action in consuming and (active or v==7) else 4),'Explicit factor domain')
 paid=call('ffta_centered_paid',UNIT,action,residue=residue);check(paid==int(action in consuming and active),'Paid eligibility')
 check(m.read(slot,1)[0]==(0xff if paid else 0xf1|(v<<1)),'Paid masks')
 if paid:check(call('ffta_centered_active',UNIT,residue=residue)==0,'Consumed snapshot is not beneficial')
 call('ffta_centered_retire',UNIT,residue=residue);check(m.read(slot,1)[0]==(0xf1 if paid or v==7 else 0xf1|(v<<1)),'Bounded snapshot retirement')
for value,event,residue in itertools.product(range(256),range(10),(0,4)):
 slot=reset(UNIT,value);call('ffta_centered_event',UNIT,event,residue=residue)
 check(m.read(slot,1)[0]==(value&~14 if event in (2,3,4,5,7,8) else value),'Typed lifecycle event')
for unit,value,residue in itertools.product((UNIT,units[-1]),range(256),(0,4)):
 slot=reset(unit,value);scope=0x03007400;before=m.read(0x02000000,0x40000)
 check(m.call(old['ffta_evaluated_init'],scope,unit,stack=STACK+residue)==1,'Evaluated init')
 check(m.read(scope+272,1)[0]==value,'Whole-byte evaluator copy')
 call('ffta_centered_grant',scope,1,residue=residue);check(m.read(scope+272,1)[0]==(value&~14)|12,'Evaluated independent grant')
 call('ffta_centered_paid',scope,349,residue=residue);check(m.read(scope+272,1)[0]==(value&~14)|14,'Evaluated independent consumption')
 check(m.read(0x02000000,0x40000)==before,'Evaluated query leaked into live state/AP')
 m.call(old['ffta_evaluated_close'],scope,stack=STACK+residue);call('ffta_centered_grant',scope,1,residue=residue)
 check(m.read(scope+272,1)==b'\0','Retired evaluator regained state')
report=dict(passed=True,baseSha1=sha(base),romSha1=sha(rom),checks=checks,scope='Packed canonical36 owner primitives, all256 bytes, SP0/4, explicit432 action domain, no production hooks enabled')
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
