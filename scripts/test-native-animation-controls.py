"""Native animation control entries retain the preceding actual graphics upload.

Authenticate the retained Samurai frame53 failure, execute the original native
dispatcher on detached RAM, and reject pixel/source/command near matches.
No game route, player save, ROM build or art generation.
"""
import ast,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_body_display import pending_from_anchor
from native_art import ROOT,sha,TILES,OAM
from actor_render_evidence import actors
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
text=(ROOT/'scripts/test-equipment-legality.py').read_text().replace('self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)','self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
exec(compile(ast.Module(body=[n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
source=ROOT/'build/art/samurai-fight/20260918T221953.470284Z'
pins={'failed.json':'c7680e6fd19a624615bf63f3ddcd07c8ae594229f24d65c5a65b2fa1c196031a',
 'failed.ram':'247e688a3babcf037f59902ee93c6ec7c121c1d3f9625b22704ecef3a06a82ba',
 'failed.vram':'4a25a4fec1acc1b01bd2b702caa5e189bbdb04211e8bde2989de5ffef544c772',
 'failed.iwram':'531c229bb87b18fdf556ba3f9d1dc7009a8c0764bfe672796f012b430ee8eed6'}
out=ROOT/'build/art/native-animation-controls'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];records=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 samples={k:(source/k).read_bytes() for k in pins}
 for name,digest in pins.items():check(sha(samples[name])==digest,'Retained source authenticated '+name)
 prior=json.loads(samples['failed.json']);meta=json.loads((ROOT/'build/art/refinement/samurai-support-v1/current.json').read_text())
 rom=__import__('pathlib').Path(meta['path']).read_bytes();clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
 check(hashlib.sha1(rom).hexdigest()==prior['romSha1']=='5fe7c35d4b4a89e71f3cdc059e5bff75e747ee33','Exact failing candidate')
 check(rom[0x210e4:0x21378]==clean[0x210e4:0x21378],'Entire native dispatch/update code unchanged')
 ram=samples['failed.ram'];vram=samples['failed.vram'];body=133676;address=0x02000000+body
 observed=actors(rom,ram,vram,{body})[0];first=observed['first'];frame=first-0x08000000+40
 check(rom[frame+9]==8 and observed['index']==3,'Failure occurs immediately after native event command8')
 check(observed['exactUpload'] and observed['displayedFrames']==[1] and observed['controlHold']==dict(graphicsEntry=1,throughEntry=2,commands=[8]),'Exact actor source/VRAM retains graphics entry1 through event entry2')
 check(observed['tileOffset']==struct.unpack_from('<I',rom,first-0x08000000+20)[0],'Recorded source identifies preceding actual upload')
 check(observed['tileOffset']!=struct.unpack_from('<I',rom,frame)[0],'Event tile field differs and was not installed')
 # Native opcode0 and opcodes2..8 leave source/layout untouched. Each reads the real
 # command record with only its opcode varied in a private detached ROM clone.
 for opcode in (0,*range(2,9)):
  image=bytearray(rom);image[frame+9]=opcode;m=ARM(image,samples['failed.iwram']);m.put(0x02000000,ram)
  m.put(address+0x38,struct.pack('<I',first+40));m.put(address+0x1e,b'\0')
  before=m.read(address,72);writes=[]
  hook=m.u.hook_add(UC_HOOK_MEM_WRITE,lambda u,kind,p,n,value,data:writes.append((p,n)))
  m.call(0x080210e4,address,0);m.u.hook_del(hook);after=m.read(address,72)
  check(after[0x20:0x28]==before[0x20:0x28] and after[0x2c:0x30]==before[0x2c:0x30],'Native opcode retains upload source/size/layout '+str(opcode))
  check(all(address<=p and p+n<=address+72 or STACK-64<=p and p+n<=STACK for p,n in writes),'Only native actor fields and call stack written '+str(opcode))
  if opcode==8:check(after[0x1e]==0x82,'Original native event code emitted, no tile upload')
  if opcode==0:check(after==before,'Native opcode0 preserves complete actor record')
  records.append(dict(opcode=opcode,writes=writes,actorBefore=before.hex(),actorAfter=after.hex()))
 # Full native timer/index update reproduces the fields at the failing frame.
 m=ARM(rom,samples['failed.iwram']);m.put(0x02000000,ram)
 m.put(address+0xa,struct.pack('<2H',1,2));m.put(address+0x38,struct.pack('<I',first+40));m.put(address+0x1e,b'\0')
 m.call(0x08021290,address,0)
 check(m.read(address,72)==ram[body:body+72],'Native full update reproduces complete retained frame53 actor')
 for offset,value,label in ((0x20,observed['tileOffset']+32,'different recorded source'),(0x38,first,'inconsistent command cursor')):
  altered=bytearray(ram);struct.pack_into('<I',altered,body+offset,value)
  row=actors(rom,altered,vram,{body})[0]
  check(not row['displayedFrames'],'Reject '+label)
 altered=bytearray(vram);altered[0x10000+observed['tile']*32]^=1
 check(not actors(rom,ram,altered,{body})[0]['displayedFrames'],'Reject one changed uploaded pixel')
 # A real graphics opcode with these bytes must not inherit the old image.
 altered=bytearray(rom);altered[frame+9]=1
 check(not actors(altered,ram,vram,{body})[0]['displayedFrames'],'Reject changed event to graphics opcode')
 # Actual native trail streams contain opcode0 between graphics entries.
 # Pin the failed action evidence; establish a direct frame57 proof before
 # allowing the existing bounded pending-upload rule for frames58..61.
 held_index_path=ROOT/'notes/native-held-control-evidence.json'
 held_index=json.loads(held_index_path.read_text());held_source=ROOT/held_index['source']
 held_data={name:(held_source/name).read_bytes() for name in held_index['sha256']}
 for name,digest in held_index['sha256'].items():check(sha(held_data[name])==digest,'Held retained input '+name)
 held_prior=json.loads(held_data['failed.json'])
 connected=json.loads((ROOT/'build/art/connected'/held_index['romSha1']/'manifest.json').read_text())
 check(held_prior['romSha1']==connected['romSha1']==held_index['romSha1'],'Exact failed held candidate identity')
 held_records=[]
 for case,path,digest in [('baseline',connected['components']['weapon']['source'],connected['components']['weapon']['baseRomSha1']),
                          ('generated',connected['path'],connected['romSha1'])]:
  image=Path(path).read_bytes();check(hashlib.sha1(image).hexdigest()==digest,'Actual held '+case+' ROM')
  check(image[0x210e4:0x21378]==clean[0x210e4:0x21378],'Held native dispatcher/update unchanged '+case)
  raw=held_data[case+'-attack-57.ram'];video=held_data[case+'-attack-57.vram'];p=135432
  a,=actors(image,raw,video,{p});q=a['first']-0x08000000
  check(a['index']==3 and image[q+49]==0 and a['controlHold']==dict(graphicsEntry=1,throughEntry=2,commands=[0]),'Actual trail opcode0 retains nearest executed graphics '+case)
  check(a['displayedFrames']==[1] and a['exactUpload'],'Exact retained trail pixels '+case)
  table=struct.unpack_from('<I',image,0x2102c)[0]-0x08000000
  desc=struct.unpack_from('<I',image,table+4*a['resource'])[0]-0x08000000
  desc+=(a['mode']&~3)*6+(12 if a['mode']&3 in (1,2) else 0)+4
  check(struct.unpack_from('<I',image,desc)[0]+4==a['first'],'Actual secondary-channel descriptor '+case)
  # Replay original full timer/command update to reproduce the entire capture.
  # Reverse only the captured preceding cursor/timer/queued bit from frame56.
  previous=held_prior['observations'][case]['attack-56']['heldWeapons']
  old=next(x for x in previous if x['address']==p)
  m=ARM(image,samples['failed.iwram']);m.put(0x02000000,raw);addr=0x02000000+p
  m.put(addr,struct.pack('<I',old['flags']));m.put(addr+10,struct.pack('<2H',old['timer'],old['index']))
  m.put(addr+0x38,struct.pack('<I',old['current']));m.call(0x08021290,addr,0)
  check(m.read(addr,72)==raw[p:p+72],'Native complete update reproduces actual trail frame57 '+case)
  start=0x10000+a['tile']*32;block=video[start:start+a['allocation']*32]
  anchor=dict(direct=True,identity=(a['resource'],a['tile'],a['allocation']),block=block,first=a['first'],index=a['index'])
  for offset,value,label in [(0x20,a['tileOffset']+32,'source'),(0x38,a['first'],'cursor')]:
   damaged=bytearray(raw);struct.pack_into('<I',damaged,p+offset,value)
   check(not actors(image,damaged,video,{p})[0]['displayedFrames'],'Reject held '+case+' altered '+label)
  damaged=bytearray(video);damaged[start]^=1
  check(not actors(image,raw,damaged,{p})[0]['displayedFrames'],'Reject held '+case+' changed pixel')
  # Unknown commands are not included merely because native dispatch ignores
  # them. A new opcode requires its own documented consumer evidence.
  damaged=bytearray(image);damaged[q+49]=9
  check(not actors(damaged,raw,video,{p})[0]['displayedFrames'],'Reject unsupported held opcode '+case)
  if case=='baseline':
   for tick in range(58,62):
    next_raw=held_data[f'baseline-attack-{tick}.ram'];next_video=held_data[f'baseline-attack-{tick}.vram']
    nxt,=actors(image,next_raw,next_video,{p});next_block=next_video[start:start+len(block)]
    check(bool(pending_from_anchor(nxt,next_block,anchor,tick-57)),'Original pending trail retains complete direct allocation '+str(tick))
    check(not pending_from_anchor(nxt,next_block,anchor,17),'Reject expired trail anchor '+str(tick))
    altered=dict(nxt,flags=nxt['flags']&~0x120000)
    check(not pending_from_anchor(altered,next_block,anchor,tick-57),'Reject trail hold without pending native flag '+str(tick))
    damaged=bytearray(next_block);damaged[-1]^=1
    check(not pending_from_anchor(nxt,damaged,anchor,tick-57),'Reject changed allocation tail '+str(tick))
  held_records.append(dict(case=case,romSha1=digest,actor=a))
 report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],source=str(source),inputHashes=pins,observed=observed,records=records,
             heldRecords=held_records,heldIndexSha256=sha(held_index_path.read_bytes()),scope=__doc__+' Also proves actual original/generated secondary trail opcode0 and bounded pending holds from retained failure. No new battle playback.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n');print('Artifacts: '+str(out));raise
