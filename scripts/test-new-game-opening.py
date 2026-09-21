"""Fresh cartridge startup, real name keyboard and Snowball scene, fixed input."""
import ast,collections,hashlib,json,pathlib,runpy,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<native heap decoder>','exec'))
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
production=pathlib.Path(meta['path']);assert hashlib.sha1(production.read_bytes()).hexdigest()==meta['romSha1']
OUT=production.parent/'new-game-opening';OUT.mkdir(exist_ok=True)
clean=ROOT/'roms/clean/FFTA_US_clean.gba';clean_hash=hashlib.sha1(clean.read_bytes()).hexdigest()
assert clean_hash=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
checks=collections.Counter();failures=[];runs={};frames={}
def check(k,v,detail=None):
 checks[k]+=1
 if not v:failures.append(dict(check=k,detail=detail))
steps=list(range(0,71,5))
def crop(frame,box):
 raw,w,h,pitch,pixel=frame;x0,y0,x1,y1=box;stride=4 if pixel==1 else 2
 return b''.join(raw[y*pitch+x0*stride:y*pitch+x1*stride] for y in range(y0,y1))
def snapshot(e,folder,label):
 ram=e.memory();h=heap(ram);e.screenshot(folder/(label+'.png'));e.save(folder/(label+'.state'))
 (folder/(label+'.ram')).write_bytes(ram)
 return dict(label=label,heap=h,ramSha1=hashlib.sha1(ram).hexdigest(),frameSha1=hashlib.sha1(e.frame[0]).hexdigest())
def keyboard(e):return [b for b in heap(e.memory())['allocationBlocks'] if b['marker']=='la' and b['payloadBytes']==50688]
def fresh(e):
 e.set_memory(0,b'\xff'*len(e.memory(0)),0)
 e.run(3600);e.run(8,8);e.run(180);e.run(8,256);e.run(1800)
# Reproduce the established original-game reference sequence. Its final frame
# contains the teacher's Snowball instructions; acceptance compares that exact
# dialogue and scene, not the expansion's potentially different frame timing.
e=E(clean);folder=OUT/'clean';folder.mkdir(exist_ok=True);samples=[];reference={}
try:
 fresh(e)
 for step in range(71):
  if step:e.run(8,8 if step==31 else 64 if step==32 else 256);e.run(120)
  if step in steps:samples.append(snapshot(e,folder,str(step)));reference[step]=e.frame
 check('reference-keyboard-allocated',any(b['marker']=='la' and b['payloadBytes']==50688 for b in samples[5]['heap']['allocationBlocks']))
finally:e.close()
runs['clean']=dict(romSha1=clean_hash,samples=samples)
# Fixed, bounded state-observed input script: dialogue A until the real keyboard
# allocation exists, then Start/Up/A to confirm. Never keep typing A into a
# keyboard because a historical frame count assumed the scene had already ended.
trace=[];e=E(production);folder=OUT/'candidate';folder.mkdir(exist_ok=True);samples=[]
try:
 fresh(e)
 for step in range(97):
  if keyboard(e):break
  assert step<96,'Name keyboard never allocated within declared dialogue bound'
  e.run(8,256);e.run(360);trace.append(dict(phase='before-name',key=256,wait=360))
 e.run(180);samples.append(snapshot(e,folder,'keyboard'))
 check('keyboard-has-real-native-allocation',len(keyboard(e))==1)
 check('name-screen-positive-headroom',samples[-1]['heap']['freePayload']>0,samples[-1]['heap']['freePayload'])
 check('alphabet-matches-native-rendering',crop(e.frame,(17,33,176,126))==crop(reference[25],(17,33,176,126)))
 check('default-name-matches-native',crop(e.frame,(92,140,125,149))==crop(reference[25],(92,140,125,149)))
 for key,wait in ((8,360),(64,120),(256,360)):
  e.run(8,key);e.run(wait);trace.append(dict(phase='confirm-name',key=key,wait=wait))
 check('name-confirmed-keyboard-released',not keyboard(e))
 samples.append(snapshot(e,folder,'confirmed'))
 expected=crop(reference[70],(40,106,169,148))
 for step in range(97):
  if crop(e.frame,(40,106,169,148))==expected:break
  assert step<96,'Native Snowball instructions never reached within declared dialogue bound'
  e.run(8,256);e.run(360);trace.append(dict(phase='after-name',key=256,wait=360))
 samples.append(snapshot(e,folder,'snowball'))
 check('native-Snowball-instructions-rendered',crop(e.frame,(40,106,169,148))==expected)
 check('native-Snowball-scene-background',crop(e.frame,(0,0,80,32))==crop(reference[70],(0,0,80,32)))
 check('no-name-keyboard-left-live',not keyboard(e))
 for sample in samples:check('native-production-heap-end',sample['heap']['end']==0x0203f000,sample['label'])
finally:e.close()
runs['candidate']=dict(romSha1=meta['romSha1'],samples=samples)
check('reference-phases-nonvacuous',len({hashlib.sha1(reference[step][0]).hexdigest() for step in (0,25,35,50,70)})>=4)
report=dict(passed=not failures,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()),failures=failures,runs=runs,
 inputs=dict(initial=[[3600,0],[8,8],[180,0],[8,256],[1800,0]],baselineDialogueSteps=70,baselineWaitFrames=120,baselineOverrides={'31':8,'32':64},candidateDialogueBound=96,candidateWaitFrames=360,keyFrames=8,erasedSRAM=True,trace=trace,
 alphabetCrop=[17,33,176,126],defaultNameCrop=[92,140,125,149],snowballDialogueCrop=[40,106,169,148],snowballBackgroundCrop=[0,0,80,32]))
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='runs'},indent=2))
assert not failures,failures
