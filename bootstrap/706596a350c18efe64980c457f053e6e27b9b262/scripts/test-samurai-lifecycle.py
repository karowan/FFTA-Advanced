"""Native Dispel/equipment transactions, packed-state ownership and ABI."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent;rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols']
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=P/'samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(base,iw),ARM(rom,iw);counts=collections.Counter()
def check(kind,a,b):
 counts[kind]+=1
 assert a==b,(kind,[(hex(i),x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:15] if isinstance(a,(bytes,bytearray)) else (a,b))
def reset(m):m.put(0x02000000,ram);m.put(0x03000000,iw)
CTX=0x0200f3f0;ACTOR=0x02000398
table=struct.unpack_from('<I',base,0xccd84)[0]-0x08000000;dispels=[]
for action in range(347):
 for slot,stage in enumerate(base[table+action*28+12:table+action*28+15]):
  if base[0x553e70+stage*4+1]==53:dispels.append((action,slot,stage))
check('native_dispel_actions',[x[0] for x in dispels],[10,107,154,244,327])
admitted=0
for (action,slot,stage),status,query,residue,packed in itertools.product(dispels,range(-1,44),(0,0x10),(0,4),(0,1,4,13,255)):
 for m in (native,expanded):
  reset(m);m.put(0x02001e98,bytes([packed])*36);m.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status))
  context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,ACTOR,UNIT,UNIT,action,0)
  struct.pack_into('<H',context,0x26,query);context[0x28]=slot;struct.pack_into('<I',context,0x30,0x08553e70+stage*4);m.put(CTX,context)
 allowed=native.call(0x08133a58,UNIT,53);results=[m.call(0x0813388c,stack=STACK+residue) for m in (native,expanded)]
 want=bytearray(native.read(0x02000000,0x40000))
 if allowed and not query:
  want[0x1e98]&=~14
  if status<0:admitted+=1
 check('native_dispel_return',results[1],results[0]);check('native_dispel_status_masks_and_query',expanded.read(0x02000000,0x40000),want)
check('centered_only_admission',admitted,10*len(dispels))

# Native whole transactions, both entry points and SP residues. Compare every
# EWRAM byte with the base operation, permitting only the selected status byte.
for fn,items,slot,item,packed,residue in itertools.product((0x080caf78,0x080cb0d8),((376,377,0,0,0),(0,376,303,0,0)),range(5),(0,376,377,303,389),(0,1,4,13,255),(0,4)):
 for m in (native,expanded):
  reset(m);m.put(0x02001e98,bytes([packed])*36);m.put(UNIT+5,bytes([116,1,116]));m.put(UNIT+0x2a,struct.pack('<5H',*items))
 # Read the actual ordered-primary contract in the candidate, independently
 # of Centered's wrapper. The original transaction supplies the after state.
 before=expanded.call(symbols['ffta_primary_weapon'],UNIT)
 native.call(fn,UNIT,item,slot,stack=STACK+residue);expanded.call(fn,UNIT,item,slot,stack=STACK+residue)
 want=bytearray(native.read(0x02000000,0x40000));after=expanded.call(symbols['ffta_primary_weapon'],UNIT)
 if before!=after:want[0x1e98]&=~14
 check('native_equipment_full_memory',expanded.read(0x02000000,0x40000),want)
 counts['changed_primary' if before!=after else 'preserved_primary']+=1

# A raw copied unit is foreign; an explicit evaluated owner is private. Neither
# callback may clear the canonical owner by matching identity bytes.
main_symbols={p[2]:int(p[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(p:=l.split())==3}
for owned,residue in itertools.product((False,True),(0,4)):
 reset(expanded);expanded.put(0x02001e98,b'\xff'*36);copy=0x03007400
 if owned:check('evaluated_init',expanded.call(main_symbols['ffta_evaluated_init'],copy,UNIT),1)
 else:expanded.put(copy,expanded.read(UNIT,264)+bytes(12))
 context=bytearray(0x34);struct.pack_into('<I',context,8,copy);expanded.put(CTX,context);before=expanded.read(0x02000000,0x40000)
 expanded.call(symbols['ffta_centered_dispel_entry'],CTX,stack=STACK+residue)
 check('dispel_copy_source_isolation',expanded.read(0x02000000,0x40000),before)
 check('dispel_copy_owned_byte',expanded.read(copy+272,1),bytes([0xf1 if owned else 0]))
 if owned:expanded.call(main_symbols['ffta_evaluated_close'],copy)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(counts),total=sum(counts.values()),scope='Full native Dispel dispatcher and both equipment setters, whole EWRAM oracle, query/ownership/ABI; not yet gameplay UI acceptance')
(OUT/'lifecycle-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
