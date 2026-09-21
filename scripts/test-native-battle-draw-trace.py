"""Trace one original draw scheduler call from authenticated retained battle RAM.

An isolated native-code diagnostic, not a timing or full battle acceptance test.
Only CpuSet/CpuFastSet BIOS operations are modeled; unknown calls fail closed.
"""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0, str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_INTR
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=3000000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
source=ROOT/'build/art/live-palette/battle/20260918T054254.715222Z'
meta=json.loads((ROOT/'build/art/live-palette/4cf2dcb9f5e96bfc9928770eb929e36dcd2e5690/manifest.json').read_text())
expected={
 'ram':'b866b0e2a65bd48e4d805a52eb452609bfde5f586ecc19adec9ec8cd1008b003',
 'iwram':'45d61181cd95764255d38f798e7f0a9fefef9520f960c61076425b26ed40d11e',
 'vram':'63ae3d0a460496651cd32f97f1a149dc8ad0e1d400181efcd0d289428cd333da',
 'palette':'b7a46ec3c89a4914147ed96dc7aae9c9ff5d1ff7f5611b06b2ccb46f4c0fb160',
 'oam':'dc06c84aa4bff1ce4fc99de9d51ebe95d04906c22c456fc3aec67d4229891e6f'}
out=ROOT/'build/art/native-battle-draw'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];calls=[];bios=[];a=None
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 data={k:(source/('parent-ready.'+k)).read_bytes() for k in expected}
 for k,v in data.items():check(sha(v)==expected[k],k+' authenticated')
 rom=Path(meta['source']).read_bytes();check(hashlib.sha1(rom).hexdigest()==meta['baseRomSha1'],'Parent ROM authenticated')
 a=ARM(rom,data['iwram']);a.put(0x02000000,data['ram'])
 for addr,size,k in [(0x04000000,0x1000,None),(0x05000000,0x1000,'palette'),(0x06000000,0x20000,'vram'),(0x07000000,0x1000,'oam')]:
  a.u.mem_map(addr,size)
  if k:a.put(addr,data[k])
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
 def trace(u,pc,size,user):
  values=[u.reg_read(r) for r in regs]
  # Keep all scheduler/renderer calls: layout can be in a nested descriptor.
  calls.append(dict(pc=hex(pc),lr=hex(u.reg_read(UC_ARM_REG_LR)),args=[hex(v) for v in values],stack=a.read(u.reg_read(UC_ARM_REG_SP),40).hex()))
 for pc in (0x080014c8,0x08001cf0,0x08001f34,0x08142248,0x0814224c,0x08142250,0x08142254):
  a.u.hook_add(UC_HOOK_CODE,trace,begin=pc,end=pc)
 def interrupt(u,number,user):
  pc=u.reg_read(UC_ARM_REG_PC);op=struct.unpack('<H',a.read(pc-2,2))[0]
  check(number==2 and op>>8==0xdf,'Known Thumb SWI encoding')
  call=op&255;src,dst,control=[u.reg_read(r) for r in regs[:3]]
  assert call in (0x0b,0x0c),f'Unsupported BIOS call {call:x} at {pc:x}'
  width=4 if call==0x0c or control&(1<<26) else 2
  count=control&0x1fffff
  if call==0x0c:assert count%8==0,'CpuFastSet alignment'
  payload=a.read(src,width)*count if control&(1<<24) else a.read(src,count*width)
  a.put(dst,payload);bios.append(dict(call=call,source=hex(src),destination=hex(dst),bytes=len(payload)))
 a.u.hook_add(UC_HOOK_INTR,interrupt)
 a.call(0x08000460)
 check(any('0x9dc21a4' in r['args'] for r in calls),'Actual Dark Knight portrait layout reached original renderer')
 for k,addr,length in [('iwram',0x03000000,0x8000),('ram',0x02000000,0x40000)]:
  (out/('after.'+k)).write_bytes(a.read(addr,length))
 report=dict(status='passed',checks=checks,calls=calls,bios=bios,romSha1=meta['baseRomSha1'],inputs=expected,
  scope='One isolated original 08000460 draw call from retained parent battle RAM with modeled CpuSet. Call-site/ownership evidence only; no hardware timing or candidate acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),calls=len(calls),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,calls=calls,bios=bios,pc=hex(a.u.reg_read(UC_ARM_REG_PC)) if a else None),indent=2)+'\n');print(out);raise
