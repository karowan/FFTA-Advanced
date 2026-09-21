"""Complete native A433C regressions, including payment-bypass incoming edges."""
import argparse,ast,collections,ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-sha',default='69a844aee6a536f29e2b00959acce62de1658e27');p.add_argument('--capture',action='store_true');p.add_argument('--fell',action='store_true');p.add_argument('--current',action='store_true');args=p.parse_args();OUT=ROOT/'build/expansion/probes/exposed-effects'/args.base_sha
sha=lambda b:hashlib.sha1(b).hexdigest()
if args.fell:
 from fell_test_context import load_context
 report=load_context(args.current);OUT=pathlib.Path(report['path']).parent
 base=(OUT/'base.gba').read_bytes();rom=pathlib.Path(report['path']).read_bytes();args.base_sha=report['baseSha1']
 fixture=OUT/'fixture/battle-ready.state';packed=bytes(36)
 assert sha((fixture.parent/'frozen.gba').read_bytes())==sha(rom)
else:
 report=json.loads((OUT/'report.json').read_text());base=(OUT/'frozen.gba').read_bytes();rom=(OUT/'isolated.gba').read_bytes()
 fixture=ROOT/'build/expansion/probes/exposed-storage/current'/args.base_sha/'battle/battle-ready.state';packed=b'\x0a'*36
assert sha(base)==args.base_sha and sha(rom)==report['romSha1']
if args.capture:
 image=bytearray(rom if args.fell else base);image[0xa433c:0xa433e]=bytes.fromhex('fee7');path=OUT/'executor-capture.gba';path.write_bytes(image);E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator'];e=E(path)
 try:
  e.load(fixture);e.run(1);e.set_memory(0x33fc,struct.pack('<HH',250,250));e.set_memory(0x1e98,packed)
  for key in [256,128,128,128,256,256,256,128,256,256,256]:e.run(8,key);e.run(180)
  e.save(OUT/'executor-capture.state');(OUT/'executor-capture.ram').write_bytes(e.memory());(OUT/'executor-capture.iwram').write_bytes(C.string_at(*e.maps[0x03000000]));regs=struct.unpack_from('<17I',(OUT/'executor-capture.state').read_bytes(),0x20);assert regs[15]==0x080a433e,[hex(x) for x in regs];print('Captured native A433C entry')
 finally:e.close()
 sys.exit(0)
if not (OUT/'executor-capture.state').exists():
 subprocess.run([sys.executable,__file__,'--base-sha',args.base_sha,'--capture',*(['--fell'] if args.fell else []),*(['--current'] if args.current else [])],check=True)
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import *
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
ram=(OUT/'executor-capture.ram').read_bytes();iw=(OUT/'executor-capture.iwram').read_bytes();regs=struct.unpack_from('<17I',(OUT/'executor-capture.state').read_bytes(),0x20)
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
a,b=ARM(base,iw),ARM(rom,iw);checks=0;recipient_checks=0
for action in list(range(347))+[357,358,423,424,425,426,427,428,429,430]:
 outputs=[]
 for m in (a,b):
  m.put(0x02000000,ram);m.put(0x03000000,iw);m.put(regs[13],struct.pack('<I',action));m.put(0x02001e98,packed)
  def recipient(u,pc,size,_):
   global recipient_checks
   if pc==0x080a3072:
    context=m.read(0x0200f3f0,12);formula,selected=struct.unpack_from('<II',context,4);assert formula==selected,('Selected recipient divergence',action,hex(formula),hex(selected));recipient_checks+=1
  hook=m.u.hook_add(UC_HOOK_CODE,recipient,begin=0x080a3072,end=0x080a3072)
  try:m.call(0x080a433c,*regs[:4],stack=regs[13])
  finally:m.u.hook_del(hook)
  outputs.append(m.read(0x02000000,0x40000))
 assert outputs[0]==outputs[1],('Full native executor regression',action,[(hex(i),x,y) for i,(x,y) in enumerate(zip(*outputs)) if x!=y][:15]);checks+=1
result=dict(passed=True,baseSha1=args.base_sha,romSha1=report['romSha1'],checks=checks,recipientChecks=recipient_checks,initialPackedByte=packed[0],scope='All347 originals and10 allocated custom IDs (including inert423) execute complete native A433C with inactive Exposed; no skipped fixtures. Includes native Fight/payment bypass. Explicit recipient equality checked at successful native magnitude boundary. New431 behavior is tested separately.')
(OUT/'executor-report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
