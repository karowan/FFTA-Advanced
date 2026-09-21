"""Compare Guarding Draw with the actual original Protect dispatcher."""
import ast,collections,hashlib,itertools,json,pathlib,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
P=ROOT/'build/expansion/probes';meta=json.loads((P/'samurai/current.json').read_text());OUT=pathlib.Path(meta['path']).parent
rom=pathlib.Path(meta['path']).read_bytes();base=(OUT/'input.gba').read_bytes();symbols=meta['symbols'];assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
fix=P/'samurai-state'/meta['baseSha1'];ram=(fix/'execute-trap.ram').read_bytes();iw=(fix/'execute-trap.iwram').read_bytes()
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000;CTX=0x0200f3f0
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
native,expanded=ARM(base,iw),ARM(rom,iw);checks=0
for status,packed,residue in itertools.product(range(-1,44),(0,1,5,13,255),(0,4)):
 for m in (native,expanded):
  m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(UNIT+0xe8,struct.pack('<Q',0 if status<0 else 1<<status));m.put(0x02001e98,bytes([packed])*36)
  context=bytearray(0x34);struct.pack_into('<IIIHH',context,0,0x02000398,UNIT,UNIT,9,0);struct.pack_into('<I',context,0x30,0x08553e70+78*4);m.put(CTX,context)
 native.call(0x0813388c,stack=STACK+residue)
 expanded.call(symbols['ffta_samurai_after_attempt'],UNIT,352,1,stack=STACK+residue)
 a=native.read(UNIT,264);b=expanded.read(UNIT,264);checks+=1
 assert a==b,('Native Protect differs',status,packed,residue,[(hex(i),x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y])
 checks+=1;assert expanded.read(0x02001e98,36)==bytes([packed])*36,'Protect touched custom state'
report=dict(passed=True,romSha1=meta['romSha1'],checks=checks,scope='Actual native Protect action9/stage78/effect82 dispatcher versus Guarding self-grant, all44 status bits, packed custom states and SP0/4; complete unit bytes')
(OUT/'protect-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
