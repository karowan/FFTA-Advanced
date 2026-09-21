"""Trace native palette cycles from authenticated existing battle states.

No route replay, gameplay fixture creation, player data or ROM mutation. The
isolated native callback and short idle trace are diagnostic component evidence.
"""
import ast, ctypes as C, datetime, hashlib, json, runpy, struct, sys
from pathlib import Path
from native_art import ROOT, sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
tree=ast.parse((ROOT/'scripts/test-equipment-legality.py').read_text().replace('count=50000','count=500000'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native ARM>','exec'))
source=ROOT/'build/art/live-palette/battle/20260918T054254.715222Z'
meta=json.loads((ROOT/'build/art/live-palette/4cf2dcb9f5e96bfc9928770eb929e36dcd2e5690/manifest.json').read_text())
assert sha((source/'failed.json').read_bytes())=='fb46373f7ca0114a01a3c2285d0c221e214bc0837fff1592f3d796d0222cdabd'
expected={
 'parent':('e826d7ae117806a11bce91c956167a35b2c007f51ff8c0a3e4e00b80bc3d01cd','45d61181cd95764255d38f798e7f0a9fefef9520f960c61076425b26ed40d11e'),
 'candidate':('76783d518fd8b675d5759ce35c1b1717ce4e805c4e433e691cbf06d01c050491','f0a1ed1525c1036e578c557d49591bb93e931f830347cb09a5c692667ce389e5')}
out=ROOT/'build/art/native-battle-cycle'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
checks=[];records={};callbacks=[];e=None
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 for case,path,digest in [('parent',meta['source'],meta['baseRomSha1']),('candidate',meta['path'],meta['romSha1'])]:
  rom=Path(path).read_bytes();check(hashlib.sha1(rom).hexdigest()==digest,case+' ROM authenticated')
  state=source/(case+'-ready.state');iw=(source/(case+'-ready.iwram')).read_bytes()
  check(sha(state.read_bytes())==expected[case][0] and sha(iw)==expected[case][1],case+' retained state/IWRAM authenticated')
  if case=='parent':
   for offset,first,last in [(0x3c7c,162,168),(0x3cb4,169,175)]:
    task=0x03000000+offset;a=ARM(rom,iw)
    check(struct.unpack_from('<H',iw,offset+4)[0]==2 and struct.unpack_from('<2H',iw,offset+6)==(first,last),'Actual retained native cycle record '+hex(task))
    initial=a.read(0x03003860,1024);ring=struct.unpack_from('<7H',initial,first*2)
    rotations={struct.pack('<7H',*(ring[n:]+ring[:n])).hex() for n in range(7)}
    phases=[]
    for tick in range(64):
     a.call(0x08146865,task);actual=a.read(0x03003860,1024)
     check(actual[:first*2]==initial[:first*2] and actual[(last+1)*2:]==initial[(last+1)*2:],'Native cycle changes only its declared color range '+str((first,tick)))
     value=actual[first*2:(last+1)*2].hex();check(value in rotations,'Native cycle is an exact seven-color rotation '+str((first,tick)));phases.append(value)
    check(set(phases)==rotations,'All seven native phases observed '+str(first))
    callbacks.append(dict(task=task,first=first,last=last,initial=initial[first*2:(last+1)*2].hex(),phases=phases))
  e=E(Path(path));e.load(state);records[case]=[]
  schedule=[('ready',0)]+[('idle',0)]*256+[('move-open-press',256)]*8+[('move-open',0)]*256+[('cancel-press',1)]*8+[('cancel',0)]*128
  for tick,(phase,key) in enumerate(schedule):
   if tick:e.run(1,key)
   live=C.string_at(*e.maps[0x03000000]);palette=C.string_at(*e.maps[0x05000000])
   row=dict(tick=tick,phase=phase,key=key,head=struct.unpack_from('<I',live,0x3c64)[0],busy=live[0x5668],
            shadow=live[0x3860:0x3c60].hex(),palette=palette.hex(),
            cycles=[live[o:o+44].hex() for o in (0x3c7c,0x3cb4)],
            skippedDMA=struct.unpack_from('<H',live,0xe10)[0],queue=struct.unpack_from('<I',live,0x2bcc)[0])
   records[case].append(row)
   if tick in (0,1,8,256,257,264,265,272,280,520,521,528,529,656):(out/(case+'-'+str(tick)+'.iwram')).write_bytes(live)
  e.close();e=None
 summary={case:dict(heads=sorted({r['head'] for r in rows}),
          phaseHeads={phase:sorted({r['head'] for r in rows if r['phase']==phase}) for phase in ('idle','move-open-press','move-open','cancel-press','cancel')},
          cyclePhases={str(first):len({r['shadow'][first*4:(first+7)*4] for r in rows}) for first in (162,169,418)}) for case,rows in records.items()}
 report=dict(status='passed',checks=checks,romSha1=meta['romSha1'],source=str(source),stateHashes=expected,callbacks=callbacks,observations=records,summary=summary,
             scope='Original cycle callback contract plus idle/open-Move/cancel observations from each authenticated existing battle state. Eight-frame A/B inputs, no actual movement or fixture mutation. Does not accept phase normalization, frame pacing, palette overlay or complete battle integration.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),summary=summary,report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,observations=records,callbacks=callbacks),indent=2)+'\n');print(str(out));raise
finally:
 if e:e.close()
