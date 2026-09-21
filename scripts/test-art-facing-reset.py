"""Original constructor facing flags and exact retained Combo reset evidence."""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha
from native_oam_evidence import shapes_at_composition
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
source=(ROOT/'scripts/test-samurai-fight.py').read_text()
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='initial_action_reset'],type_ignores=[]),'<actual action observer>','exec'))
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
half=lambda r,p:struct.unpack_from('<H',r,p)[0]
folder=ROOT/'build/art/class-combo/20260919T043717.419638Z'
pins={'failed.json':'dc0298f4083632bf45b6d284192108a7c3518df9eb6d759a27a46c5c236dcde0',
 'failed.ram':'95eac04877f83721077f68388a5bdcfb2042cb2df98d4184eaae7b8cdfbbcd81',
 'failed.iwram':'f10d9224332ea4c5b2eb6e1d755dea8dacceea3e02fef357da4701b4d07c6a4c',
 'failed.oam':'069952a1ba6fd27cffe931eb5d5dd7ec08fbecc265bbfb1555b47f9cd1b742e1',
 'failed.vram':'8847457835780303e13da81e58178fb713af43543bf39380d029e32d80821a2c'}
out=ROOT/'build/art/facing-reset'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
def strict(ok,label):assert ok,label
try:
 for name,pin in pins.items():check(sha((folder/name).read_bytes())==pin,'Pinned '+name)
 meta=json.loads((ROOT/'build/art/connected/5a14e6c7b69f9f9984a6965faf5740d3b318e41a/live-palette-view.json').read_text());rom=Path(meta['path']).read_bytes()
 check(hashlib.sha1(rom).hexdigest()==meta['romSha1'],'Current candidate ROM authenticated')
 clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
 check(rom[0x21618:0x216f8]==clean[0x21618:0x216f8],'Entire original constructor body and literals unchanged')
 ram=(folder/'failed.ram').read_bytes();iw=(folder/'failed.iwram').read_bytes();vram=(folder/'failed.vram').read_bytes();hardware=(folder/'failed.oam').read_bytes()
 retained=json.loads((folder/'failed.json').read_text());last=retained['observations']['attack-325'];old=last['actor'];body=old['address']
 p=0x10000+old['tile']*32;block=vram[p:p+old['allocation']*32]
 check(sha(block)==last['blockSha256'],'Complete failed VRAM allocation matches last direct uploaded frame')
 before_oam=bytes.fromhex(retained['compositionEvents'][-2]['memory']['oam'])
 objects=[struct.unpack_from('<3H',before_oam,i*8) for i in range(128)]
 anchor=dict(frame=last['frame'],direct=True,actor=old,identity=(old['resource'],old['tile'],old['allocation']),block=block,
             hardware=[o for o in objects if o[0]&0x300!=0x200 and o[2]&1023==old['tile']])
 clock=last['frame']+1
 event=retained['compositionEvents'][-1]
 check(event['videoFrame']==retained['compositionEvents'][-2]['videoFrame']+1,'Consecutive actual native frames around reset')
 producer=shapes_at_composition(meta,rom,event,hardware,check)
 check(bool(anchor['hardware']) and initial_action_reset(ram,vram,hardware,body,producer) is not None,'Actual observer accepts facing1 reset with native added afterimage')
 check(initial_action_reset(ram,vram,hardware,body) is None,'Extra copy cannot bypass actual native producer proof')
 # Restore only the recorded pre-reset actor fields on the retained RAM clone.
 # Unrecorded bytes retain their captured values; this is a controlled native
 # constructor proof, not a claim to reconstruct the preceding entire frame.
 before=bytearray(ram)
 for offset,value in ((0,old['flags']),(0x20,old['tileOffset']),(0x28,old['oam']),(0x2c,old['oam']),(0x34,old['first']),(0x38,old['current'])):struct.pack_into('<I',before,body+offset,value)
 for offset,value in ((0xa,old['timer']),(0xc,old['index'])):struct.pack_into('<H',before,body+offset,value)
 a=ARM(rom,iw)
 for stack in (STACK,STACK+4):
  for facing in range(4):
   mode=(old['mode']&~3)|facing;a.put(0x02000000,before);a.put(stack,struct.pack('<3I',old['resource'],mode,0))
   result=a.call(0x08021618,word(before,body+0x40),0x02000000+body,0,old['allocation'],stack=stack)
   actual=a.read(0x02000000+body,72)
   check(result==0x02000000+body,'Actual constructor reuses actor '+str((stack,facing)))
   check(word(actual,0)==(0x45 if facing<2 else 0x65),'Original facing-specific flags '+str((stack,facing)))
   check(half(actual,0xa)==half(actual,0xc)==0 and word(actual,0x20)==0xffffffff and word(actual,0x2c)==0 and word(actual,0x34)==word(actual,0x38),'Original reset fields '+str((stack,facing)))
   if facing==old['mode']&3:check(actual==ram[body:body+72],'Entire original constructor result equals captured72-byte failed actor')
   records.append(dict(stack=stack,facing=facing,flags=word(actual,0),first=word(actual,0x34)))
 for offset,value in ((0,0x46),(0,0x65),(0xa,1),(0xc,1),(0x20,0),(0x28,0),(0x2c,old['oam'])):
  changed=bytearray(ram);struct.pack_into('<H' if offset in (0xa,0xc) else '<I',changed,body+offset,value)
  check(initial_action_reset(changed,vram,hardware,body,producer) is None,'Reject altered reset field '+str((offset,value)))
 changed=bytearray(vram);changed[p]^=1
 check(initial_action_reset(ram,changed,hardware,body,producer) is None,'Reject changed retained VRAM')
 changed=bytearray(hardware);changed[4*8]^=1
 try:shapes_at_composition(meta,rom,event,changed,strict)
 except AssertionError:check(True,'Reject changed added hardware copy at actual boundary')
 else:raise AssertionError('Changed hardware accepted')
 clock=last['frame']+5
 check(initial_action_reset(ram,vram,hardware,body,producer) is None,'Reject expired direct anchor')
 report=dict(status='passed',romSha1=meta['romSha1'],checks=checks,pins=pins,source=str(folder),records=records,
  scope='Exact captured-facing1 reset and unchanged complete VRAM. Actual original21618 on a retained RAM clone with recorded prior actor fields reproduces captured72-byte actor; all four facings and both stack residues establish45/65 flags. Consecutive recorded native composition boundaries prove the added afterimage geometry and prior-copy retention. Negative reset/pixel/age/changed-hardware cases rejected. Does not reconstruct prior whole-game state or replace live Combo replay.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');raise
