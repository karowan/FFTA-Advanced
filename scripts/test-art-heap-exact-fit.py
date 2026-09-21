"""Native allocator diagnostic on authenticated pre-failure heap; no game inputs."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source);exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
p=ROOT/'build/art/live-palette/battle/20260918T110743.414156Z'
ram=(p/'candidate-turn-input-10.ram').read_bytes();iw=(p/'candidate-failed.iwram').read_bytes()
assert sha(ram)=='bc8afbd44d58dde893161d04ea7f8a9e30aca4124ec3624792637ad5f53076b6'
assert sha(iw)=='7eac92358110d38a9c52e2ba231eee276af44df0d7e0758d2712fead8afc8ef3'
meta=json.loads((ROOT/'build/art/live-palette/all-classes-current.json').read_text());rom=Path(meta['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==meta['romSha1']=='4b35081ba8d69f6ebf997607c119931e303a6106'
assert struct.unpack_from('<I',ram,0xf434)[0]==0x020159d0
assert ram[0x31d50:0x31d54]==bytes.fromhex('7073a115')
out=ROOT/'build/art/heap-exact-fit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
rows=[]
for address,size in [(0x08007138,22148),(0x08006ec0,5537),(0x08007138,22144),(0x08007138,22136)]:
    a=ARM(rom,iw);a.put(0x02000000,ram);result=None;error=None
    try:result=a.call(address,0x020159d0,size)
    except Exception as e:error=str(e)
    after=a.read(0x02000000,0x40000)
    rows.append(dict(address=address,size=size,result=result,error=error,
        firstFree=after[0x159d8:0x159e4].hex(),selected=after[0x31d4c:0x31d58].hex(),
        firstFreeNext=0x020159d0+4*struct.unpack_from('<H',after,0x159e2)[0],
        otherFree=after[0x230fc:0x23108].hex(),lastFree=after[0x39a48:0x39a54].hex()))
report=dict(status='observed',romSha1=meta['romSha1'],ramSha256=sha(ram),iwramSha256=sha(iw),rows=rows,scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=str(out/'report.json'),rows=rows),indent=2))
