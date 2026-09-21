"""Pinned Combo hidden frame, exact native producer and refusal controls."""
import ast,datetime,hashlib,itertools,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_oam_evidence import reconstruct,hidden_body
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
out=ROOT/'build/art/native-only-oam'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
folder=ROOT/'build/art/class-combo/20260919T042521.380450Z'
pins={'failed.json':'f701266bb814eb1d5de6ae93bacc49b2d2020424902d3b3c8eb033a791684aed',
 'failed.ram':'d67c4314acb8ddc1a11774e1e8b320da0fed97b55fd6a7cadbbb4e78aeb89063',
 'failed.iwram':'753b55ef12abf446c1ccb835e2949eb429f6078c86890307a7af088c112cf13e',
 'failed.oam':'e0a743dd56ef01c8cfacceb80d1b1df310890f565d27e28c3bc16b8392457e31'}
checks=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
def strict(ok,label):assert ok,label
def dma(u,pc,size,a):
 src,dst,flags=struct.unpack('<3I',a.read(0x040000b0,12));count=(flags&65535)*4
 assert flags>>16==0x8400 and 0x03000000<=src<=0x03008000-count and 0x07000000<=dst<=0x07000400-count
 a.put(dst,a.read(src,count));a.put(0x040000b8,struct.pack('<I',flags&0x7fffffff))
try:
 for name,pin in pins.items():check(sha((folder/name).read_bytes())==pin,'Pinned '+name)
 meta=json.loads((ROOT/'build/art/connected/5a14e6c7b69f9f9984a6965faf5740d3b318e41a/live-palette-view.json').read_text())
 rom=Path(meta['path']).read_bytes();check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Exact current ROM')
 ram=(folder/'failed.ram').read_bytes();iw=(folder/'failed.iwram').read_bytes();oam=(folder/'failed.oam').read_bytes()
 failed=json.loads((folder/'failed.json').read_text());actor=failed['observations']['attack-110']['actor']
 tile,allocation=actor['tile'],actor['allocation'];body=actor['address']
 check(struct.unpack_from('<H',ram,body+0x12)[0]==tile and struct.unpack_from('<H',ram,body+0x16)[0]==allocation,'Actual failed body retains authenticated tile allocation')
 proof=hidden_body(meta,rom,ram,iw,oam,tile,allocation,check)
 native=bytearray(rom);native[0x12bc:0x12c4]=bytes.fromhex('f0b557464e464546')
 a=ARM(native,iw);a.put(0x02000000,ram)
 a.u.mem_map(0x04000000,0x1000);a.u.mem_map(0x07000000,0x1000)
 for pc in (0x08001322,0x08001396,0x080013e2,0x08001430):a.u.hook_add(UC_HOOK_CODE,dma,user_data=a,begin=pc,end=pc)
 for stack in (STACK,STACK+4):
  a.put(0x03000000,iw);a.put(0x07000000,b'\xa5'*1024);a.call(0x080012bc,stack=stack)
  check(a.read(0x07000000,1024)==oam,'Actual original producer exactly reproduces failed frame '+hex(stack))
 matrix=0
 for bank,other,front,ui,main,tail in itertools.product((0,1),(0,1),(0,1,48),(0,1,32),(0,1,79,80,81,127,128),(0,1,16)):
  a.put(0x03000000,iw);a.put(0x03000028,bytes([bank^1]));a.put(0x03002f58,bytes([other^1]))
  for p,v in ((0x2c50+4*bank,front),(0x2f60+4*other,ui),(0x20+4*bank,main),(0x3168+4*other,tail)):a.put(0x03000000+p,struct.pack('<I',v))
  a.put(0x03003270+bank*32,b'\x01'*32);a.put(0x030032b0+bank*256,struct.pack('<128H',*(0x5a00+i for i in range(128))))
  expected,_=reconstruct(rom,a.read(0x03000000,0x8000));a.call(0x080012bc)
  check(a.read(0x07000000,1024)==expected,'Original DMA/clipping/affine matrix '+str((bank,other,front,ui,main,tail)));matrix+=1
 base=meta['ramReservation'][0]-0x02000000
 controls=[('hardware mismatch','oam',0,b'\xff'),('invalid native bank','iw',0x28,b'\x02'),
  ('active custom overlay','ram',base+2572,b'\x01'),('custom emission','ram',base+meta['emittedOffset'],b'\x01'),
  ('wrong early return phase','ram',base+meta['composePhaseOffset'],b'\x04'),
  ('palette refusal','ram',base+meta['refusalOffset'],b'\x01'),('wrong tile mapping','iw',0x940,b'\x00')]
 rejected=[]
 for name,space,p,value in controls:
  data=dict(ram=bytearray(ram),iw=bytearray(iw),oam=bytearray(oam));data[space][p:p+len(value)]=value
  try:hidden_body(meta,rom,data['ram'],data['iw'],data['oam'],tile,allocation,strict)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Negative control accepted: '+name)
  check(True,'Reject '+name)
 try:hidden_body(meta,rom,ram,iw,oam,96,16,strict)
 except AssertionError:rejected.append('body tile overlap');check(True,'Reject actual native object overlapping body allocation')
 else:raise AssertionError('Body overlap accepted')
 report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,pins=pins,source=str(folder),proof=proof,matrix=matrix,rejected=rejected,
  scope='Pinned failed Combo frame is native-only OAM, not a rendered generated-body palette mismatch. Actual original producer reproduces all1024 hardware bytes at both stack residues; independent reconstruction matches native DMA/clipping/affine matrix. Negative controls reject overlay/emission/phase/refusal/mapping/OAM/tile-overlap mismatches. No new live action or full Combo acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');raise
