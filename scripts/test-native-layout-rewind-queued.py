"""Reproduce retained native rewind/queued upload from its matching ready state."""
import ctypes as C,datetime,hashlib,json,runpy,struct
from pathlib import Path
from native_art import ROOT,TILES,sha
from actor_render_evidence import actors
from native_body_display import layout_reset_display
source=ROOT/'build/art/live-palette/battle/20260918T065737.392257Z'
assert sha((source/'failed.json').read_bytes())=='4ae57e412418cf284f679d86eb884dd76480068d73a68d27001a6d857bf90936'
assert sha((source/'candidate-ready.state').read_bytes())=='43270a7f2985e94387afe45bce707035fff67f4998ca41ad366fd0016e5e6d70'
meta=json.loads((ROOT/'build/art/live-palette/21052ed615a6463251cba9b98952b4cc07ba4546/manifest.json').read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
out=ROOT/'build/art/layout-rewind-queued'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];samples={};e=None
def check(ok,label):
 assert ok,label
 checks.append(label)
def hardware(ram,raw):
 result=bytearray(raw);base=meta['ramReservation'][0]-0x02000000;keys=ram[base+meta['variantOffset']:base+meta['variantOffset']+10]
 active=struct.unpack_from('<I',ram,base+2572)[0]
 for i,slot in enumerate(ram[base+2608:base+2736]):
  attr2=struct.unpack_from('<H',result,i*8+4)[0]
  if slot<10 and keys[slot]<160 and active&(1<<(attr2>>12)):
   struct.pack_into('<H',result,i*8+4,(attr2&4095)|((keys[slot]&15)<<12))
 return bytes(result)
try:
 e=E(Path(meta['path']));e.load(source/'candidate-ready.state')
 for key in (256,128,128,128):e.run(8,key);e.run(180)
 e.run(8,256)
 for tick in range(22):
  e.run(1)
  if tick in (20,21):
   ram=e.memory();vram=C.string_at(*e.maps[0x06000000]);oam=C.string_at(*e.maps[0x07000000]);iw=C.string_at(*e.maps[0x03000000])
   samples[tick]=dict(ram=ram,vram=vram,oam=oam,iwram=iw)
   for name,data in samples[tick].items():(out/('frame-'+str(tick)+'.'+name)).write_bytes(data)
 e.close();e=None
 old,new=samples[20],samples[21];a=next(v for v in actors(rom,old['ram'],old['vram']) if v['address']==0x20a2c)
 a['tileOffset']=struct.unpack_from('<I',old['ram'],a['address']+0x20)[0]
 check(new['ram']==(source/'candidate-failed.ram').read_bytes() and new['vram']==(source/'candidate-failed.vram').read_bytes(),'Exact original failing RAM and VRAM reproduced without deployment replay')
 check(a['declaredSequence'] and a['displayedFrames']==[0] and a['index']==2 and bool(a['flags']&0x20000),'Original directly observed frame with queued upload before constructor rewind')
 previous_command=a['first']+20*(a['index']-1)
 check(struct.unpack_from('<I',rom,previous_command-0x08000000)[0]==a['tileOffset'],'Captured native tile offset identifies previous decoded command, not next sequence pointer')
 p=0x10000+a['tile']*32;size=a['allocation']*32;before=hardware(old['ram'],old['oam']);after=hardware(new['ram'],new['oam'])
 anchor=dict(direct=True,actor=a,identity=(a['resource'],a['tile'],a['allocation']),block=old['vram'][p:p+size],hardware=[x for i in range(128) if (x:=struct.unpack_from('<3H',before,i*8))[0]&0x300!=0x200 and x[2]&1023==a['tile']])
 result=layout_reset_display(rom,new['ram'],new['vram'],after,a['address'],anchor,1)
 check(result is not None and not result['configured'],'Exact captured queued source accepted through constructor rewind')
 check(new['vram'][p:p+size]==rom[TILES+a['tileOffset']:TILES+a['tileOffset']+size],'Complete allocation equals actual prior queued upload')
 for age in (0,5):check(layout_reset_display(rom,new['ram'],new['vram'],after,a['address'],anchor,age) is None,'Reject age '+str(age))
 for changes,label in [(dict(flags=a['flags']&~0x120000),'no pending transfer'),(dict(tileOffset=a['tileOffset']+32),'different captured source'),(dict(index=3),'different native command index')]:
  check(layout_reset_display(rom,new['ram'],new['vram'],after,a['address'],dict(anchor,actor=dict(a,**changes)),1) is None,'Reject '+label)
 changed=bytearray(new['vram']);changed[p]^=1
 check(layout_reset_display(rom,new['ram'],changed,after,a['address'],anchor,1) is None,'Reject one changed output pixel')
 changed=bytearray(new['ram']);struct.pack_into('<I',changed,a['address'],0x67)
 check(layout_reset_display(rom,changed,new['vram'],after,a['address'],anchor,1) is None,'Reject non-constructor transition with a different command')
 check(layout_reset_display(rom,new['ram'],new['vram'],after,a['address'],dict(anchor,direct=False),1) is None,'Reject inferred anchor')
 report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],source=str(source),actor=a,samples={str(k):{field:sha(raw) for field,raw in sample.items()} for k,sample in samples.items()},scope='Matching existing ready-state replay to exactly reproduce native constructor rewind and pending upload. Authenticated captured source, complete allocation/geometry and refusal controls. No complete battle/timing or final-art acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n');print(out);raise
finally:
 if e:e.close()
