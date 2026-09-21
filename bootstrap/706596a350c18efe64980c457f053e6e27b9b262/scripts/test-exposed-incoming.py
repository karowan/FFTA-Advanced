"""Native final-stage/Fight/Combo Exposed comparisons on a frozen private ROM."""
import argparse,ast,collections,hashlib,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-sha',default='69a844aee6a536f29e2b00959acce62de1658e27');p.add_argument('--fell',action='store_true');p.add_argument('--current',action='store_true');args=p.parse_args()
OUT=ROOT/'build/expansion/probes/exposed-effects'/args.base_sha
sha=lambda b:hashlib.sha1(b).hexdigest()
if args.fell:
 from fell_test_context import load_context
 report=load_context(args.current);OUT=pathlib.Path(report['path']).parent
 base=(OUT/'base.gba').read_bytes();image=pathlib.Path(report['path']).read_bytes();args.base_sha=report['baseSha1'];symbols=report['symbols'];fix=OUT/'fixture'
 assert sha((fix/'frozen.gba').read_bytes())==sha(image)
else:
 report=json.loads((OUT/'report.json').read_text());assert report['incomingHooks']
 base=(OUT/'frozen.gba').read_bytes();image=(OUT/'isolated.gba').read_bytes();symbols=json.loads((OUT/'symbols.json').read_text())
 fix=ROOT/'build/expansion/probes/exposed-storage/current'/args.base_sha/'battle'
assert sha(base)==args.base_sha and sha(image)==report['romSha1']
ram=(fix/'battle-ready.ram').read_bytes();iw=(fix/'battle-ready.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
TARGET,CTX=0x020033e4,0x0200f3f0
state=0x02001e98+24+(TARGET-0x02002fc4)//264
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(base,iw),ARM(image,iw)
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
signed=lambda x:x-(1<<32) if x>>31 else x
actions=word(base,0xccd84)-0x08000000
checks=collections.Counter();samples=[]
# Native classification catalog is deliberately materialized independently:
# raw physical support class, HP effect kind and actual damage callbacks. It
# includes physical GoblinPunch/Subdue; excludes recovery/self-cost callbacks.
eligible=set()
for action in range(347):
 r=actions+28*action;physical=action==0 or bool(word(base,r+16)&0x40000)
 for stage in base[r+12:r+15]:
  d=base[0x553e70+4*stage:0x553e74+4*stage]
  hp=base[0x3a87b0+12*d[1]+4]==1
  if hp and ((physical and d[3] in (12,24,30,31,39,43,44)) or (action,d[3]) in ((148,36),(211,38))):eligible.add((action,stage))
for action in list(range(347))+([] if args.fell else [357,358,424,425,426,427,428,429,430,431]):
 r=actions+28*action
 for slot,stage in enumerate(base[r+12:r+15]):
  if not stage:continue
  for stack in (STACK,STACK+4):
   for packed in (0,0x0a,1,0x0b):
    outcomes=[]
    for m in (native,expanded):
     m.put(0x02000000,ram);m.put(state,bytes([packed]))
     context=bytearray(0x34)
     struct.pack_into('<IIIHH',context,0,UNIT,TARGET,TARGET,action,265)
     struct.pack_into('<hhh',context,0x20,37,-13,0)
     context[0x26]=0x10;context[0x28]=slot
     struct.pack_into('<II',context,0x2c,0x08000000+r+12,0x08553e70+4*stage)
     m.put(CTX,context)
     value=signed(m.call(0x08131b20,stack=stack))
     outcomes.append((value,m.read(0x02000000,0x40000)))
    value=outcomes[0][0]
    want=min(999,value*6//5) if packed&1 and value>0 and (action,stage) in eligible else value
    assert outcomes[1][0]==want,('stage',action,stage,packed,value,outcomes[1][0],want)
    assert outcomes[1][1]==outcomes[0][1],('query writes/RNG',action,stage,packed)
    checks['native_stage_value_and_memory']+=2
    if packed&1 and want!=value and len(samples)<30:samples.append({'action':action,'stage':stage,'native':value,'exposed':want})
# Full native Fight preview bypasses the stage dispatcher. Other actions must
# receive exactly one stage modifier, never a second outer wrapper multiplier.
for action in (0,1,11,23,90,112,113,115,125,148,211,223,266)+(() if args.fell else (424,430)):
 for packed in (0,0x0a,1,0x0b):
  for mode in (0,2):
   for stack in (STACK,STACK+4):
    outcomes=[]
    for m in (native,expanded):
     m.put(0x02000000,ram);m.put(state,bytes([packed]));m.put(stack,struct.pack('<II',0,mode))
     outcomes.append((signed(m.call(0x08130200,UNIT,TARGET,action,265,stack=stack)),m.read(0x02000000,0x40000)))
    value=outcomes[0][0]
    # These listed originals select a single qualifying HP-damage stage;
    # Cure/Fire and custom coefficients deliberately do not scale here.
    qualifies=action in (0,90,112,113,115,125,148,211,223,266)
    want=min(999,value*6//5) if packed&1 and value>0 and qualifies else value
    assert outcomes[1][0]==want,('full preview',action,packed,mode,value,outcomes[1][0],want)
    assert outcomes[1][1]==outcomes[0][1],('preview mutation/RNG',action,packed,mode)
    checks['preview_once_and_memory']+=2
for strength in (0,1,5,25,100):
 for packed in (0,0x0a,1,0x0b):
  for stack in (STACK,STACK+4):
   outcomes=[]
   for m in (native,expanded):
    m.put(0x02000000,ram);m.put(state,bytes([packed]))
    outcomes.append((signed(m.call(0x08130454,UNIT,TARGET,strength,stack=stack)),m.read(0x02000000,0x40000)))
   value=outcomes[0][0];want=min(999,value*6//5) if packed&1 and value>0 else value
   assert outcomes[1][0]==want and outcomes[1][1]==outcomes[0][1],('combo',strength,packed,outcomes[0][0],outcomes[1][0],want)
   checks['combo_final_and_memory']+=2
# Explicit selected recipient and independently owned evaluator copies. No
# identity/name fallback: the canonical source can change after scoped copy.
symbol_path=ROOT/'build/expansion/accepted'/args.base_sha/'engine.symbols' if args.fell else OUT/'engine.symbols'
if args.current:symbol_path=ROOT/'build/expansion/engine.symbols'
oldsymbols={p[2]:int(p[0],16) for line in symbol_path.read_text().splitlines() if len(p:=line.split())==3}
for stack in (STACK,STACK+4):
 for packed in range(256):
  expanded.put(0x02000000,ram);expanded.put(state,bytes([packed]));expanded.put(0x02001e98,bytes([packed^1]))
  for damage in (-999,-1,0,1,37,999):
   before=expanded.read(0x02000000,0x40000)
   assert expanded.call(symbols['ffta_exposed_incoming_numerator'],damage&0xffffffff,TARGET,stack=stack)==(6 if damage>0 and packed&1 else 5)
   assert expanded.read(0x02000000,0x40000)==before
   checks['packed_sign_explicit_recipient']+=2
 for packed in (0x0a,0x0b,0xfe,0xff):
  expanded.put(0x02000000,ram);expanded.put(state,bytes([packed]));scope=0x03007400;foreign=0x03007600
  assert expanded.call(oldsymbols['ffta_evaluated_init'],scope,TARGET,stack=stack)==1
  expanded.put(state,bytes([packed^1]));expanded.put(foreign,expanded.read(TARGET,264)+bytes(12))
  assert expanded.call(symbols['ffta_exposed_incoming_numerator'],37,scope,stack=stack)==(6 if packed&1 else 5)
  assert expanded.call(symbols['ffta_exposed_incoming_numerator'],37,foreign,stack=stack)==5
  expanded.call(oldsymbols['ffta_evaluated_close'],scope,stack=stack)
  assert expanded.call(symbols['ffta_exposed_incoming_numerator'],37,scope,stack=stack)==5
  checks['owned_copy_independence_retirement']+=4
result={'passed':True,'baseSha1':args.base_sha,'romSha1':sha(image),'checks':sum(checks.values()),'groups':dict(checks),'samples':samples,'scope':'Native original stage/Fight/Combo final modifier, explicit recipient and scoped copies. Custom factor composition and actual431 are tested separately.'}
(OUT/'incoming-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
