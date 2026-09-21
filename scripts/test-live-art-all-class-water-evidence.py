"""Authenticate and reconcile ten retained land/water palette consumer proofs.

Read-only evidence verification. No emulator, new fixture or game playback.
"""
import argparse,datetime,hashlib,json,struct,sys
from pathlib import Path
from native_art import ROOT,sha,layout,TILES,OAM
from actor_render_evidence import actors
from live_palette_evidence import observe
index_path=ROOT/'notes/native-art-all-class-water-evidence.json'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path,help='Reconcile unchanged resources and raw-capture interpretation; never claim new runtime.')
args=parser.parse_args()
index=json.loads(index_path.read_text())
meta=json.loads((ROOT/'build/art/live-palette'/index['romSha1']/'manifest.json').read_text())
assert hashlib.sha1(Path(meta['path']).read_bytes()).hexdigest()==index['romSha1']
class_raw=Path(meta['classManifest']).read_bytes();assert sha(class_raw)==meta['classManifestSha256']
classes={j['job']:j for j in json.loads(class_raw)['classResources']['jobs']}
assert [r['job'] for r in index['records']]==list(range(116,126))
checks=[];records=[]
out=ROOT/'build/art/all-class-water-evidence'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
original_excepthook=sys.excepthook
def failed(kind,error,traceback):
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,records=records),indent=2)+'\n',encoding='utf-8')
 print('Artifacts: '+str(out))
 original_excepthook(kind,error,traceback)
sys.excepthook=failed
def check(ok,label):assert ok,label;checks.append(label)
candidate=None;candidate_rom=None;resource_proofs=[]
if args.candidate_manifest:
 candidate=json.loads(args.candidate_manifest.read_text(encoding='utf-8'))
 candidate_rom=Path(candidate['path']).read_bytes()
 original=Path(meta['path']).read_bytes()
 check(hashlib.sha1(candidate_rom).hexdigest()==candidate['romSha1'],'Candidate ROM authenticated')
 for field in ('classManifestSha256','baseRomSha1','generatedSourceSha256','paletteSha256',
               'historySlots','ramReservation','bindingOffset','variantOffset','tagOffset',
               'visibleColorsOffset','refusalOffset','bindingCounterOffset'):
  check(candidate[field]==meta[field],'Unchanged retained resource/palette interpretation '+field)
 # The native table may relocate when a held-weapon resource is appended.
 # Follow both actual table pointers; do not assume equal pointer addresses.
 tables=[struct.unpack_from('<I',r,0x2102c)[0]-0x08000000 for r in (original,candidate_rom)]
 sizes=[struct.unpack_from('<I',r,0x21060)[0]-0x08000000 for r in (original,candidate_rom)]
 jobs=[struct.unpack_from('<I',r,0xc8598)[0]-0x08000000 for r in (original,candidate_rom)]
 check(original[0x210e4:0x21378]==candidate_rom[0x210e4:0x21378],'Native frame command dispatcher/update remains byte-exact')
 for job,entry in classes.items():
  old_record,new_record=[r[t+job*52:t+(job+1)*52] for r,t in zip((original,candidate_rom),jobs)]
  check(len(old_record)==52 and old_record==new_record and new_record[4]==entry['race'] and list(struct.unpack_from('<2H',new_record,7))==entry['resources'],str(job)+' actual native job/race/land/water routing exact')
 resources=json.loads(class_raw)['classResources']['resources']
 check(len(resources)==20,'Complete ten-class land/water resource inventory')
 for resource in resources:
  ident=resource['id'];slots=resource['slots'];seen=set();frames=0;slot_counts={}
  allocations=[struct.unpack_from('<H',r,t+ident*2)[0] for r,t in zip((original,candidate_rom),sizes)]
  check(allocations==[resource['size']]*2,str(ident)+' actual native allocation table preserves verified bound')
  pointers=[struct.unpack_from('<I',r,t+ident*4)[0]-0x08000000 for r,t in zip((original,candidate_rom),tables)]
  descriptors=[r[p:p+slots*12] for r,p in zip((original,candidate_rom),pointers)]
  check(all(len(d)==slots*12 for d in descriptors),str(ident)+' complete descriptor spans')
  for slot in range(slots):
   pointer,new_pointer=[struct.unpack_from('<I',d,slot*12)[0] for d in descriptors]
   check(bool(pointer)==bool(new_pointer) and descriptors[0][slot*12+4:slot*12+12]==descriptors[1][slot*12+4:slot*12+12],str((ident,slot))+' null selection and complete descriptor metadata exact')
   if not pointer:continue
   q,nq=pointer-0x08000000,new_pointer-0x08000000
   count=struct.unpack_from('<I',original,q)[0]
   check(0<count<=256 and candidate_rom[nq:nq+4]==original[q:q+4],str((ident,slot))+' same bounded native sequence count')
   slot_counts[slot]=count
   if (pointer,new_pointer) in seen:continue
   seen.add((pointer,new_pointer))
   for frame_index in range(count):
    t,o=struct.unpack_from('<II',original,q+4+frame_index*20)
    nt,no=struct.unpack_from('<II',candidate_rom,nq+4+frame_index*20)
    check(original[q+12+frame_index*20:q+24+frame_index*20]==candidate_rom[nq+12+frame_index*20:nq+24+frame_index*20],str((ident,slot,frame_index))+' complete command timing and frame metadata exact')
    objects,raw=layout(original,OAM+o);new_objects,new_raw=layout(candidate_rom,OAM+no)
    check(raw==new_raw and objects==new_objects,str((ident,slot,frame_index))+' complete native object layout exact')
    tiles=max(v['tile']+v['width']*v['height']//64 for v in objects)
    check(0<tiles<=resource['size'] and original[TILES+t:TILES+t+tiles*32]==candidate_rom[TILES+nt:TILES+nt+tiles*32],str((ident,slot,frame_index))+' complete displayed tile payload and allocation bound exact')
    frames+=1
  resource_proofs.append(dict(resource=ident,job=resource['job'],lifetime=resource['lifetime'],slots=slots,slotFrameCounts=slot_counts,sequences=len(seen),frames=frames))
for record in index['records']:
 job=record['job'];root=ROOT/record['directory'];race=classes[job]['race']
 for name,digest in record['sha256'].items():check(sha((root/name).read_bytes())==digest,str(job)+' authenticated '+name)
 report=json.loads((root/'report.json').read_text());fixture=json.loads((root/'generated/fixture.json').read_text())
 check(report['status']=='passed' and report['romSha1']==fixture['sourceRomSha1']==index['romSha1'],str(job)+' passed exact candidate and original-map fixture')
 check(report['outcomes']['baseline']==report['outcomes']['generated'],str(job)+' exact retained native gameplay outcome')
 rom=(root/'generated/natural-water.gba').read_bytes()
 check(hashlib.sha1(rom).hexdigest()==fixture['fixtureRomSha1'],str(job)+' authenticated actually executed ROM')
 slot={1:2,2:3,3:4,4:5,5:5}[race];unit=0x80+264*slot
 for phase,resource in zip(('water','land-return'),reversed(classes[job]['resources'])):
  raw={ext:(root/f'generated-{phase}.{ext}').read_bytes() for ext in ('ram','vram','palette','oam')}
  row=report['observations']['generated'][phase]
  check(raw['ram'][unit+4:unit+8]==bytes([1,job,race,job]),str(job)+'/'+phase+' canonical job/race identity')
  check(sha(raw['vram'])==row['vram'] and sha(raw['ram'][0x80:0x1e70])==row['owned'],str(job)+'/'+phase+' raw capture matches report')
  expected=next(a for a in row['actors'] if a['resource']==resource)
  actual=actors(rom,raw['ram'],raw['vram'],{expected['address']})
  check(len(actual)==1 and actual[0]['resource']==resource and actual[0]['declaredSequence'] and bool(actual[0]['displayedFrames']),str(job)+'/'+phase+' exact actual resource and displayed native frame')
  palette=observe(meta,rom,raw['ram'],raw['palette'],raw['oam'],lambda ok,label:check(ok,str(job)+'/'+phase+' '+label),set(range(10)))
  check(job-116 in palette['owners'],str(job)+'/'+phase+' focus class visibly owns exact generated palette')
  if candidate:
   mode=actual[0]['mode'];slot=(mode//4)*2+(1 if mode%4 in (1,2) else 0)
   graph=next(g for g in resource_proofs if g['resource']==resource)
   check(slot in graph['slotFrameCounts'],str(job)+'/'+phase+' captured native mode covered by complete equivalent candidate graph')
   current_palette=observe(candidate,candidate_rom,raw['ram'],raw['palette'],raw['oam'],lambda ok,label:check(ok,str(job)+'/'+phase+' candidate interpretation '+label),set(range(10)))
   check(current_palette==palette,str(job)+'/'+phase+' candidate artwork and palette layout interpret retained hardware identically')
 records.append(dict(job=job,race=race,resources=classes[job]['resources'],source=record['directory'],movementSampleFrames=record['movementSampleFrames']))
result=dict(status='passed',romSha1=index['romSha1'],checks=checks,records=records,indexSha256=sha(index_path.read_bytes()),scope='Authenticated retained raw water and land-return consumers for all ten correct-race jobs. Focus body and generated hardware palette independently verified from ROM/RAM/VRAM/OAM. Reuses declared native map92 route checks and their sampling limits. No new runtime, natural campaign/recruitment, timing, other actions or final-art acceptance.')
if candidate:
 result.update(candidateRomSha1=candidate['romSha1'],candidateManifestSha256=sha(args.candidate_manifest.read_bytes()),resourceProofs=resource_proofs,newRuntime=False)
 result['scope']+=' Candidate reuse reconciliation additionally proves all20 descriptor/sequence/layout/tile graphs equivalent through actual relocated pointers and covers the20 retained body modes. Candidate palette assets/layout interpret retained hardware identically. Old actor pointers are never resumed or rewritten. Executed ROM remains romSha1, not candidateRomSha1. Changed compositor, highlight field, heap and effect lifetimes require their own acceptance; this does not replay those lifetimes.'
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
