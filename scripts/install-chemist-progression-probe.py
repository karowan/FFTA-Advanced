"""Install the compiled ABI into an isolated test ROM, never a release.

No runtime acceptance is implied. This probe deliberately lives under build
and is not referenced by any player launcher or release channel.
"""
import hashlib, json, struct
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('memory_builder',ROOT/'scripts/build-memory-fixes.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

def main():
 cp=ROOT/'build/expansion/chemist-progressions/code/manifest.json';m=json.loads(cp.read_text())
 parent=json.loads(Path(m['parent']).read_text());original=Path(parent['path']).read_bytes()
 assert hashlib.sha1(original).hexdigest()==m['romSha1']
 code=Path(m['binary']).read_bytes();assert hashlib.sha256(code).hexdigest()==m['binarySha256']
 start=0x1a50000;assert original[start:start+len(code)]==b'\xff'*len(code)
 rom=bytearray(original);rom[start:start+len(code)]=code;patches=[]
 def put(at,data,label):
  before=bytes(rom[at:at+len(data)]);rom[at:at+len(data)]=data
  patches.append(dict(offset=at,before=before.hex(),after=data.hex(),label=label))
 sy=m['installedSymbols'];entries=m['installedEntries']
 addresses=sorted({a&~1 for values in entries.values() for a in values}|{a&~1 for a in sy.values() if 0x08000000<=a<0x0a000000})
 # Unchanged forwarding functions continue to call their patched callee.
 forward={'ffta_integrated_reaction_wrapper','ffta_integrated_result_storage','ffta_myk_law_hit'}
 # Renderer allocation/layout and pump/free behavior are unchanged. Only the
 # board collector needs new trap inputs; preserve small original tail-call
 # entries rather than overwriting their following function with a trampoline.
 forward.update({'ffta_geo_renderer_retire','ffta_geo_allocate','ffta_geo_renderer_free',
                 'ffta_geo_reset_owners','ffta_geo_renderer_stream','ffta_geo_renderer_pump'})
 seen={}
 assert original[0x92784:0x92794].hex()=='f0b557464e464546e0b4a4b00904090c'
 put(0x92784,helper.trampoline(0x92784,m['symbols']['ffta_cp_battle_tick_entry']['address']),'native battle controller observer')
 # Only these three comparisons are expansion upper bounds. Other #125
 # comparisons select Mystic Knight's specific weapon/animation privileges
 # and must never be changed by a numeric search across the binary.
 for name,register in (('ffta_secondary_job_entry',1),('ffta_party_command_label_entry',2),('ffta_exp_job_gate',0)):
  a=sy[name]&~1;end=next(x for x in addresses if x>a)
  expected=0x2800|(register<<8)|125
  sites=[at for at in range(a-0x08000000,end-0x08000000,2) if struct.unpack_from('<H',original,at)[0]==expected]
  assert len(sites)==1,(name,sites)
  put(sites[0],struct.pack('<H',expected+2),name+' expansion upper bound')
 # Older modules call both original function bodies and their own import
 # veneers. Patching only the newest symbol silently leaves callers on the
 # old record stride. Redirect every authenticated entry of each replacement.
 for n,old_entry in ((n,a) for n in m['exports'] for a in entries.get(n,[sy.get(n,0)])):
  if n not in sy or n in forward:continue
  old=old_entry&~1;at=old-0x08000000;target=m['symbols'][n]['address'];end=next((a for a in addresses if a>old),old+16)
  if old in seen:assert seen[old]==target,('alias collision',n,seen[old],target);continue
  seen[old]=target
  if n=='ffta_integrated_action_limit':
   b=code[target-0x09a50000:target-0x09a50000+6]
   assert m['symbols'][n]['bytes']==6 and b[-2:]==bytes.fromhex('7047')
   put(at,b,n);continue
  jump=helper.trampoline(at,target)
  if len(jump)>end-old:
   assert end-old==8 and original[at:at+4]==bytes.fromhex('004b1847'),(n,hex(old),end-old)
   put(at+4,struct.pack('<I',target|1),n+' existing trampoline target')
  else:put(at,jump,n)
 # Four independent snapshot constructors share the enlarged copy allocation.
 for at,old,new in ((0x9e8b4,0x1140,0x1180),(0x9f7e8,0x1140,0x1180),
                    (0x9f848,0x1140,0x1180),(0x9f8dc,0x1140,0x1180)):
  assert struct.unpack_from('<I',original,at)[0]==old,(hex(at),original[at:at+4].hex())
  put(at,struct.pack('<I',new),'copy allocation size')
 # Constructor literals are in the existing assembly, which owns the manager
 # header rather than any C function entry. Only authenticated symbols inside
 # that assembly may be inspected; never search-and-replace all ROM words.
 for at in (0x71118,0x711f8):
  assert struct.unpack_from('<I',original,at)[0]==0x9980
  put(at,struct.pack('<I',0x9990),'party copy tail and full item list allocation')
 assert struct.unpack_from('<I',original,0x71228)[0]==0x7280
 put(0x71228,struct.pack('<I',0x7290),'party item list starts after complete copy tail')
 a=sy['ffta_selection_allocate']&~1;end=sy['ffta_library_copy_entry']&~1
 literals=[at for at in range((a-0x08000000+3)&~3,end-0x08000000,4) if struct.unpack_from('<I',original,at)[0]==0x3840]
 assert len(literals)==1,literals
 put(literals[0],struct.pack('<I',0x3850),'selection owner allocation')
 for name in ('ffta_workspace_parent_capacity','ffta_workspace_native_manager'):
  if name not in sy:continue
  a=sy[name]&~1;end=next(x for x in addresses if x>a)
  for at in range((a-0x08000000+3)&~3,end-0x08000000,4):
   val=struct.unpack_from('<I',original,at)[0]
   if val in (0x440,0x4c0):put(at,struct.pack('<I',val+16),name+' allocation')
 allowed=set(range(start,start+len(code)))|{i for p in patches for i in range(p['offset'],p['offset']+len(bytes.fromhex(p['after'])))}
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
 digest=hashlib.sha1(rom).hexdigest();out=ROOT/'build/expansion/chemist-progressions/probes'/digest;out.mkdir(parents=True,exist_ok=True)
 path=out/'INCOMPLETE_TEST_ONLY.gba';path.write_bytes(rom)
 result=dict(status='INCOMPLETE TEST PROBE - not a playable or release build',path=str(path),romSha1=digest,
  parent=m['parent'],codeManifest=str(cp),codeManifestSha256=hashlib.sha256(cp.read_bytes()).hexdigest(),patches=patches,
  symbols={n:v['address'] for n,v in m['symbols'].items()},unmodifiedForwarders=sorted(forward))
 manifest=out/'manifest.json';manifest.write_text(json.dumps(result,indent=2)+'\n')
 (out.parent/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
 print(json.dumps(dict(status='test probe installed',romSha1=digest,patches=len(patches),manifest=str(manifest))))

if __name__=='__main__':main()
